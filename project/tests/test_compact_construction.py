"""Unit tests for the compact D²FA construction (spec §5.5, Algorithm 2^X)."""

from itertools import product
from pathlib import Path

import pytest

from bpe_token_automata.automaton import (
    CompactOptions,
    construct_compact_token_dfa,
    construct_token_dfa,
    expand_defaults,
    lift_to_delayed,
    serialize_delayed_input_dfa,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import (
    Dictionary,
    ImproperDictionaryError,
    MergeRule,
    parse_dictionary_path,
)
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.tokens import TokenSequence

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
O1_ONLY = CompactOptions(o2_state_avoidance=False, o3_clean_copy=False)


def _alphabet(*symbols: str) -> frozenset[bytes]:
    return frozenset(symbol.encode("ascii") for symbol in symbols)


def test_lift_adds_unused_nonaccepting_sink() -> None:
    base = universal_token_dfa(_alphabet("a", "b"))
    lifted = lift_to_delayed(base)
    assert lifted.sink not in lifted.accepting
    assert lifted.sink in lifted.states
    assert lifted.n_states_excluding_sink == base.n_states
    assert lifted.defaults == ()
    assert all(src != lifted.sink for src, _token, _dst in lifted.transitions)
    assert lifted.step(lifted.sink, b"a") is None
    assert lifted.accepts(TokenSequence((b"a", b"b")))
    assert serialize_delayed_input_dfa(lifted).startswith("states:")


def test_empty_dictionary_matches_baseline_language() -> None:
    base = universal_token_dfa(_alphabet("a", "b"))
    compact = construct_compact_token_dfa(Dictionary(()), base, O1_ONLY)
    baseline = construct_token_dfa(Dictionary(()), base)
    assert compact.final.n_defaults == 0
    assert compact.steps == ()
    assert compact.final.accepts(TokenSequence((b"a", b"b")))
    assert baseline.final.accepts(TokenSequence((b"a", b"b")))
    assert expand_defaults(compact.final).n_states == baseline.final.n_states


def test_improper_dictionary_is_rejected() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "improper_example3.merges")
    assert parsed.dictionary is not None
    base = universal_token_dfa(_alphabet("a", "b"))
    with pytest.raises(ImproperDictionaryError):
        construct_compact_token_dfa(parsed.dictionary, base, O1_ONLY)


def test_explicit_edge_wins_over_default() -> None:
    """Fig. 2 A1: after a⫽b, q1 defaults to q0 but b from q1 is a sink, not q0's b."""
    base = universal_token_dfa(_alphabet("a", "b"))
    dictionary = Dictionary((MergeRule(left=b"a", right=b"b", index=0),))
    result = construct_compact_token_dfa(dictionary, base, O1_ONLY)
    dfa = result.final
    fresh = dfa.step(0, b"a")
    assert result.steps[0].n_fresh == 1
    assert fresh is not None and fresh != 0
    assert dfa.defaults == ((fresh, 0),)
    assert dfa.step(0, b"b") == 0
    assert dfa.step(fresh, b"b") is None
    assert dfa.explicit_step(fresh, b"b") == dfa.sink
    assert dfa.step(fresh, b"a") == fresh
    assert dfa.accepts(TokenSequence((b"ab",)))
    assert not dfa.accepts(TokenSequence((b"a", b"b")))


def test_self_merge_fresh_state_sinks_on_v_and_uv() -> None:
    base = universal_token_dfa(_alphabet("a", "b"))
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    dfa = construct_compact_token_dfa(dictionary, base, O1_ONLY).final
    fresh = dfa.step(0, b"a")
    assert fresh is not None
    assert dfa.step(fresh, b"a") is None
    assert dfa.step(fresh, b"aa") is None
    assert dfa.explicit_step(fresh, b"a") == dfa.sink
    assert dfa.explicit_step(fresh, b"aa") == dfa.sink
    assert dfa.step(fresh, b"b") == 0


def test_o1_example2_matches_baseline_accepts() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "example2.merges")
    assert parsed.dictionary is not None
    alphabet = _alphabet("a", "b")
    base = universal_token_dfa(alphabet)
    compact = construct_compact_token_dfa(parsed.dictionary, base, O1_ONLY)
    baseline = construct_token_dfa(parsed.dictionary, base)
    assert expand_defaults(compact.final).n_states == baseline.final.n_states
    for length in range(7):
        for symbols in product(b"ab", repeat=length):
            text = bytes(symbols)
            canonical = tokenize_reference(parsed.dictionary, text)
            assert compact.final.accepts(canonical) == baseline.final.accepts(canonical)
            base_tokens = TokenSequence.from_bytes(text)
            assert compact.final.accepts(base_tokens) == baseline.final.accepts(
                base_tokens
            )


def test_o1_does_not_sink_an_existing_live_uv() -> None:
    """Regression: [a⫽a, aa⫽a, a⫽aa] reuses aaa; [4] Lemma 3 excludes this."""
    dictionary = Dictionary(
        (
            MergeRule(left=b"a", right=b"a", index=0),
            MergeRule(left=b"aa", right=b"a", index=1),
            MergeRule(left=b"a", right=b"aa", index=2),
        )
    )
    alphabet = _alphabet("a")
    base = universal_token_dfa(alphabet)
    compact = construct_compact_token_dfa(dictionary, base, O1_ONLY)
    baseline = construct_token_dfa(dictionary, base)
    sequence = TokenSequence((b"aa", b"aaa"))
    assert baseline.final.accepts(sequence)
    assert compact.final.accepts(sequence)
    assert expand_defaults(compact.final).n_states == baseline.final.n_states


def test_o1_unary_matches_baseline_accepts() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "unary_self_merge.merges")
    assert parsed.dictionary is not None
    alphabet = _alphabet("a")
    base = universal_token_dfa(alphabet)
    compact = construct_compact_token_dfa(parsed.dictionary, base, O1_ONLY)
    baseline = construct_token_dfa(parsed.dictionary, base)
    assert expand_defaults(compact.final).n_states == baseline.final.n_states
    for length in range(9):
        text = b"a" * length
        canonical = tokenize_reference(parsed.dictionary, text)
        assert compact.final.accepts(canonical)
        assert baseline.final.accepts(canonical)
        assert compact.final.accepts(canonical) == baseline.final.accepts(canonical)


def test_o1_plants_sink_on_new_uv_before_defaults_inherit_it() -> None:
    """Fig. 1 family: after a⫽a then aa⫽aa, the first fresh must reject aaaa."""
    dictionary = Dictionary(
        (
            MergeRule(left=b"a", right=b"a", index=0),
            MergeRule(left=b"aa", right=b"aa", index=1),
        )
    )
    base = universal_token_dfa(_alphabet("a"))
    compact = construct_compact_token_dfa(dictionary, base, O1_ONLY).final
    baseline = construct_token_dfa(dictionary, base).final
    fresh = compact.step(0, b"a")
    assert fresh is not None
    assert compact.step(fresh, b"aaaa") is None
    assert compact.explicit_step(fresh, b"aaaa") == compact.sink
    sequence = TokenSequence((b"aaaa",))
    assert compact.accepts(sequence) == baseline.accepts(sequence)
