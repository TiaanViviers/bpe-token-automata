"""Semantic equivalence of compact D²FA vs baseline token DFA (spec §6.4–6.5)."""

from itertools import product
from pathlib import Path

import pytest

from bpe_token_automata.automaton import (
    CompactOptions,
    DelayedInputDFA,
    TokenDFAError,
    construct_compact_token_dfa,
    construct_token_dfa,
    expand_defaults,
    languages_agree,
    token_dfa_languages_agree,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import Dictionary, MergeRule, parse_dictionary_path
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.tokens import TokenSequence
from differential import assert_unique_tokenization

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MAX_LENGTH = 8
FLAG_COMBOS = (
    CompactOptions(o2_state_avoidance=False, o3_clean_copy=False),
    CompactOptions(o2_state_avoidance=True, o3_clean_copy=False),
    CompactOptions(o2_state_avoidance=False, o3_clean_copy=True),
    CompactOptions(o2_state_avoidance=True, o3_clean_copy=True),
)


def _alphabet(*symbols: str) -> frozenset[bytes]:
    return frozenset(symbol.encode("ascii") for symbol in symbols)


def _chain_ab() -> Dictionary:
    return Dictionary(
        (
            MergeRule(left=b"a", right=b"b", index=0),
            MergeRule(left=b"ab", right=b"b", index=1),
            MergeRule(left=b"abb", right=b"b", index=2),
        )
    )


def test_public_constructor_enables_o2_and_o3() -> None:
    base = universal_token_dfa(_alphabet("a", "b"))
    result = construct_compact_token_dfa(_chain_ab(), base)
    assert result.options.o2_state_avoidance
    assert result.options.o3_clean_copy


def test_o3_reuses_clean_copy_on_paper_example_1() -> None:
    """[4] Example 1 / Fig. 2: O3 reuses the first fresh state on later merges."""
    base = universal_token_dfa(_alphabet("a", "b"))
    on = construct_compact_token_dfa(_chain_ab(), base)
    off = construct_compact_token_dfa(
        _chain_ab(),
        base,
        CompactOptions(o2_state_avoidance=False, o3_clean_copy=False),
    )
    assert on.steps[0].n_fresh == 1
    assert on.steps[1].n_fresh == 0
    assert on.steps[2].n_fresh == 0
    assert on.final.n_states_excluding_sink == 2
    assert off.final.n_states_excluding_sink > on.final.n_states_excluding_sink
    assert languages_agree(construct_token_dfa(_chain_ab(), base).final, on.final)


def test_o2_skips_clone_when_state_is_single_use() -> None:
    """[4] Example 2: after a⫽b, q1 is only reached on a, so a⫽ab patches it."""
    dictionary = Dictionary(
        (
            MergeRule(left=b"a", right=b"b", index=0),
            MergeRule(left=b"a", right=b"ab", index=1),
        )
    )
    base = universal_token_dfa(_alphabet("a", "b"))
    with_o2 = construct_compact_token_dfa(
        dictionary, base, CompactOptions(o2_state_avoidance=True, o3_clean_copy=False)
    )
    without = construct_compact_token_dfa(
        dictionary, base, CompactOptions(o2_state_avoidance=False, o3_clean_copy=False)
    )
    assert with_o2.steps[1].n_fresh == 0
    assert without.steps[1].n_fresh == 1
    assert with_o2.final.n_states_excluding_sink < without.final.n_states_excluding_sink
    baseline = construct_token_dfa(dictionary, base).final
    assert languages_agree(baseline, with_o2.final)
    assert languages_agree(baseline, without.final)


def test_flag_combinations_agree_on_example2() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "example2.merges")
    assert parsed.dictionary is not None
    base = universal_token_dfa(_alphabet("a", "b"))
    baseline = construct_token_dfa(parsed.dictionary, base).final
    for options in FLAG_COMBOS:
        compact = construct_compact_token_dfa(parsed.dictionary, base, options)
        assert languages_agree(baseline, compact.final)


def test_product_and_exhaustive_example2() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "example2.merges")
    assert parsed.dictionary is not None
    alphabet = _alphabet("a", "b")
    base = universal_token_dfa(alphabet)
    baseline = construct_token_dfa(parsed.dictionary, base).final
    compact = construct_compact_token_dfa(parsed.dictionary, base).final
    expanded = expand_defaults(compact)
    assert languages_agree(baseline, compact)
    assert token_dfa_languages_agree(baseline, expanded)

    for length in range(MAX_LENGTH + 1):
        for symbols in product(b"ab", repeat=length):
            text = bytes(symbols)
            canonical = tokenize_reference(parsed.dictionary, text)
            assert compact.accepts(canonical) == baseline.accepts(canonical)
            assert expanded.accepts(canonical) == baseline.accepts(canonical)
            base_tokens = TokenSequence.from_bytes(text)
            assert compact.accepts(base_tokens) == baseline.accepts(base_tokens)
            assert_unique_tokenization(baseline, parsed.dictionary, text, canonical)
            assert_unique_tokenization(expanded, parsed.dictionary, text, canonical)


def test_expand_defaults_unary_agrees_with_baseline() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "unary_self_merge.merges")
    assert parsed.dictionary is not None
    alphabet = _alphabet("a")
    base = universal_token_dfa(alphabet)
    baseline = construct_token_dfa(parsed.dictionary, base).final
    compact = construct_compact_token_dfa(parsed.dictionary, base).final
    expanded = expand_defaults(compact)
    assert languages_agree(baseline, compact)
    assert token_dfa_languages_agree(baseline, expanded)
    for length in range(MAX_LENGTH + 1):
        text = b"a" * length
        canonical = tokenize_reference(parsed.dictionary, text)
        assert expanded.accepts(canonical)
        assert_unique_tokenization(expanded, parsed.dictionary, text, canonical)


def test_emoji_compact_agrees_with_baseline() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "original_emoji.merges")
    assert parsed.dictionary is not None
    alphabet = frozenset({bytes((byte,)) for byte in b"\xf0\x9f\x98\x80"})
    base = universal_token_dfa(alphabet)
    baseline = construct_token_dfa(parsed.dictionary, base).final
    compact = construct_compact_token_dfa(parsed.dictionary, base).final
    assert languages_agree(baseline, compact)
    symbols = tuple(sorted(alphabet))
    for length in range(5):
        for parts in product(symbols, repeat=length):
            text = b"".join(parts)
            canonical = tokenize_reference(parsed.dictionary, text)
            assert compact.accepts(canonical) == baseline.accepts(canonical)


def test_cyclic_defaults_are_rejected() -> None:
    with pytest.raises(TokenDFAError, match="cyclic"):
        DelayedInputDFA(
            states=frozenset({0, 1, 2}),
            alphabet=frozenset({b"a"}),
            initial=0,
            accepting=frozenset({0}),
            transitions=(),
            defaults=((0, 1), (1, 0)),
            sink=2,
        )
