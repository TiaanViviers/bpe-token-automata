"""Unit tests for Algorithm 2 construction (spec §6.1)."""

from itertools import product
from pathlib import Path

import pytest

from bpe_token_automata.automaton import (
    construct_token_dfa,
    parse_string_dfa_yaml,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import (
    Dictionary,
    ImproperDictionaryError,
    MergeRule,
    parse_dictionary_path,
    parse_merge_list,
)
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.tokens import TokenSequence

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def _alphabet(*symbols: str) -> frozenset[bytes]:
    return frozenset(symbol.encode("ascii") for symbol in symbols)


def test_empty_dictionary_leaves_base_unchanged() -> None:
    base = universal_token_dfa(_alphabet("a", "b"))
    result = construct_token_dfa(Dictionary(()), base)
    assert result.final == base
    assert result.automata == (base,)
    assert result.steps == ()
    assert result.traces == ()


def test_improper_dictionary_is_rejected() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "improper_example3.merges")
    assert parsed.dictionary is not None
    base = universal_token_dfa(_alphabet("a", "b"))
    with pytest.raises(ImproperDictionaryError):
        construct_token_dfa(parsed.dictionary, base)


def test_noop_rule_does_not_change_language() -> None:
    """No run reads a then a, so S is empty; language stays {b}* tokenizations."""
    base = universal_token_dfa(_alphabet("b"))
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    result = construct_token_dfa(dictionary, base)
    assert result.steps[0].n_fresh == 0
    assert result.traces[0].triples == ()
    assert result.traces[0].n_fresh == 0
    assert result.traces[0].redirected == ()
    assert b"aa" in result.final.alphabet
    assert result.final.accepts(TokenSequence((b"b", b"b")))
    assert not result.final.accepts(TokenSequence((b"a",)))
    assert not result.final.accepts(TokenSequence((b"aa",)))


def test_self_merge_does_not_copy_uv_onto_fresh_state() -> None:
    base = universal_token_dfa(_alphabet("a", "b"))
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    result = construct_token_dfa(dictionary, base)
    a1 = result.final
    fresh = 1
    assert a1.step(0, b"a") == fresh
    assert a1.step(fresh, b"aa") is None
    assert a1.step(fresh, b"a") is None
    assert a1.step(fresh, b"b") == 0
    assert a1.step(0, b"aa") == 0


def test_distinct_merge_copies_uv_onto_fresh_state() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "example2.merges")
    assert parsed.dictionary is not None
    result = construct_token_dfa(
        parsed.dictionary, universal_token_dfa(_alphabet("a", "b"))
    )
    a2 = result.final
    assert a2.step(2, b"ba") == 1
    assert a2.step(2, b"a") is None


def test_fresh_state_inherits_accepting_status() -> None:
    base = parse_string_dfa_yaml(
        """
states: [0, 1, 2]
initial: 0
accepting: [1, 2]
transitions:
  - from: 0
    symbol: a
    to: 1
  - from: 1
    symbol: a
    to: 2
"""
    )
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    a1 = construct_token_dfa(dictionary, base).final
    # s2 = 1 is accepting, so fresh(1) is accepting.
    fresh = a1.step(0, b"a")
    assert fresh is not None
    assert fresh in a1.accepting
    assert fresh != 1


def test_fresh_state_from_non_accepting_s2_is_not_accepting() -> None:
    base = parse_string_dfa_yaml(
        """
states: [0, 1, 2]
initial: 0
accepting: [2]
transitions:
  - from: 0
    symbol: a
    to: 1
  - from: 1
    symbol: a
    to: 2
"""
    )
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    a1 = construct_token_dfa(dictionary, base).final
    fresh = a1.step(0, b"a")
    assert fresh is not None
    assert fresh not in a1.accepting


def test_user_supplied_finite_language_dfa() -> None:
    base = parse_string_dfa_yaml(
        (DATA / "automata" / "finite_ab.yaml").read_text(encoding="utf-8")
    )
    parsed = parse_merge_list("a b")
    assert parsed.dictionary is not None
    result = construct_token_dfa(parsed.dictionary, base)
    final = result.final
    assert final.accepts(TokenSequence((b"ab",)))
    assert not final.accepts(TokenSequence((b"a", b"b")))
    assert not final.accepts(TokenSequence.from_bytes(b"a"))


def test_useful_rule_changes_accepted_language() -> None:
    base = universal_token_dfa(_alphabet("a", "b"))
    empty = construct_token_dfa(Dictionary(()), base).final
    useful = construct_token_dfa(
        Dictionary((MergeRule(left=b"a", right=b"a", index=0),)),
        base,
    ).final
    pair = TokenSequence((b"a", b"a"))
    merged = TokenSequence((b"aa",))
    assert empty.accepts(pair)
    assert not empty.accepts(merged)
    assert useful.accepts(merged)
    assert not useful.accepts(pair)


def test_useless_but_proper_rule_constructs() -> None:
    parsed = parse_dictionary_path(
        DATA / "dictionaries" / "proper_with_useless_rule.yaml"
    )
    assert parsed.dictionary is not None
    result = construct_token_dfa(
        parsed.dictionary,
        universal_token_dfa(_alphabet("a", "b", "c", "d")),
    )
    assert result.final.n_states >= 1
    assert len(result.steps) == 4


def test_useless_rule_does_not_change_bounded_language() -> None:
    """Last rule ab⫽cd is proper but unused; {a,b,c,d}^{<=6} tokenizations match."""
    parsed = parse_dictionary_path(
        DATA / "dictionaries" / "proper_with_useless_rule.yaml"
    )
    assert parsed.dictionary is not None
    full = parsed.dictionary
    prefix = Dictionary(full.rules[:-1])
    alphabet = _alphabet("a", "b", "c", "d")
    base = universal_token_dfa(alphabet)
    before = construct_token_dfa(prefix, base).final
    after = construct_token_dfa(full, base).final
    max_length = 6
    for length in range(max_length + 1):
        for symbols in product(b"abcd", repeat=length):
            text = bytes(symbols)
            canonical = tokenize_reference(full, text)
            assert tokenize_reference(prefix, text) == canonical
            assert before.accepts(canonical) is after.accepts(canonical)
            assert after.accepts(canonical)
