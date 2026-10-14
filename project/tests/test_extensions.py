"""Tests for the approved §8.2 and §8.11 extensions."""

from itertools import product

import pytest

from bpe_token_automata import (
    Dictionary,
    ImproperDictionaryError,
    MergeRule,
    TokenPatternMatcher,
    TokenSequence,
    compare_dictionaries_bounded,
    match_bytes,
)
from bpe_token_automata.automaton import construct_token_dfa, universal_token_dfa
from bpe_token_automata.automaton.model import make_token_dfa


def _dictionary(*rules: tuple[bytes, bytes]) -> Dictionary:
    return Dictionary(
        tuple(
            MergeRule(left=left, right=right, index=index)
            for index, (left, right) in enumerate(rules)
        )
    )


def _bounded_inputs() -> tuple[bytes, ...]:
    return tuple(
        b"".join(symbols)
        for length in range(5)
        for symbols in product((b"a", b"b", b"c", b"d"), repeat=length)
    )


def test_bounded_equivalence_finds_commuting_rule_reordering() -> None:
    first = _dictionary((b"a", b"b"), (b"c", b"d"))
    second = _dictionary((b"c", b"d"), (b"a", b"b"))

    result = compare_dictionaries_bounded(
        first, second, _bounded_inputs(), check_token_dfa=True
    )

    assert result.equivalent
    assert result.reference_agrees
    assert result.dfa_agrees
    assert result.counterexample is None


def test_bounded_equivalence_reports_first_counterexample() -> None:
    first = _dictionary((b"a", b"b"))
    second = Dictionary(())

    result = compare_dictionaries_bounded(first, second, (b"", b"a", b"ab"))

    assert not result.equivalent
    assert result.counterexample == b"ab"
    assert result.left_tokens == TokenSequence((b"ab",))
    assert result.right_tokens == TokenSequence((b"a", b"b"))


def test_bounded_equivalence_rejects_improper_dictionary() -> None:
    improper = _dictionary((b"ab", b"c"))
    with pytest.raises(ImproperDictionaryError):
        compare_dictionaries_bounded(improper, Dictionary(()), (b"abc",))


def test_bounded_equivalence_rejects_improper_dictionary_even_with_empty_inputs() -> (
    None
):
    improper = _dictionary((b"ab", b"c"))
    with pytest.raises(ImproperDictionaryError):
        compare_dictionaries_bounded(improper, Dictionary(()), ())


def test_bounded_equivalence_reports_dfa_witness_for_transition_disagreement() -> None:
    left = _dictionary((b"a", b"b"), (b"b", b"a"))
    right = _dictionary((b"b", b"a"), (b"a", b"b"))

    sample = compare_dictionaries_bounded(left, right, (b"a",), check_token_dfa=True)
    left_dfa = construct_token_dfa(
        left, universal_token_dfa(frozenset({b"a", b"b"}))
    ).final
    right_dfa = construct_token_dfa(
        right, universal_token_dfa(frozenset({b"a", b"b"}))
    ).final

    assert sample.reference_agrees
    assert sample.dfa_agrees is False
    assert sample.counterexample is None
    assert isinstance(sample.dfa_witness, TokenSequence)
    assert sample.dfa_witness == TokenSequence((b"a", b"ba"))
    assert left_dfa.accepts(sample.dfa_witness) != right_dfa.accepts(sample.dfa_witness)

    aba_result = compare_dictionaries_bounded(
        left, right, (b"aba",), check_token_dfa=True
    )
    assert not aba_result.reference_agrees
    assert aba_result.counterexample == b"aba"
    assert aba_result.left_tokens == TokenSequence((b"ab", b"a"))
    assert aba_result.right_tokens == TokenSequence((b"a", b"ba"))


def test_bounded_equivalence_on_empty_input_is_no_evidence() -> None:
    first = _dictionary((b"a", b"b"))
    second = _dictionary((b"a", b"b"))

    result = compare_dictionaries_bounded(first, second, ())
    assert result.reference_agrees is None
    assert not result.equivalent
    assert result.counterexample is None

    dfa_result = compare_dictionaries_bounded(first, second, (), check_token_dfa=True)
    assert dfa_result.reference_agrees is None
    assert dfa_result.dfa_agrees
    assert dfa_result.equivalent


def test_token_matcher_matches_complete_tokens_and_overlaps() -> None:
    sequence = TokenSequence((b"a", b"b", b"c"))
    matcher = TokenPatternMatcher(
        (TokenSequence((b"a", b"b")), TokenSequence((b"b", b"c")))
    )

    matches = matcher.find(sequence)
    assert [(match.pattern_index, match.start, match.end) for match in matches] == [
        (0, 0, 2),
        (1, 1, 3),
    ]


def test_token_matcher_orders_same_end_matches_like_byte_baseline() -> None:
    sequence = TokenSequence((b"b", b"a"))
    patterns = (TokenSequence((b"a",)), TokenSequence((b"b", b"a")))

    token_matches = TokenPatternMatcher(patterns).find(sequence)
    byte_matches = match_bytes(b"ba", (b"a", b"ba"))

    assert token_matches == byte_matches


def test_token_matching_differs_from_detokenize_then_match_at_boundary() -> None:
    sequence = TokenSequence((b"ab", b"cd"))
    matcher = TokenPatternMatcher((TokenSequence((b"b", b"c")),))

    assert matcher.find(sequence) == ()
    byte_match = match_bytes(b"abcd", (b"bc",))[0]
    assert byte_match.start == 1
    assert byte_match.end == 3

    dfa = construct_token_dfa(
        _dictionary((b"a", b"b"), (b"c", b"d")),
        universal_token_dfa(frozenset({b"a", b"b", b"c", b"d"})),
    ).final
    assert dfa.accepts(sequence)
    assert matcher.find_canonical(sequence, dfa) == ()


def test_token_matcher_uses_failure_links_for_overlapping_patterns() -> None:
    sequence = TokenSequence((b"a", b"b", b"c", b"a", b"b", b"c"))
    matcher = TokenPatternMatcher(
        (
            TokenSequence((b"a", b"b")),
            TokenSequence((b"b", b"c")),
            TokenSequence((b"a", b"b", b"c")),
            TokenSequence((b"c", b"a")),
        )
    )

    matches = matcher.find(sequence)
    assert [(match.pattern_index, match.start, match.end) for match in matches] == [
        (0, 0, 2),
        (1, 1, 3),
        (2, 0, 3),
        (3, 2, 4),
        (0, 3, 5),
        (1, 4, 6),
        (2, 3, 6),
    ]


def test_find_canonical_rejects_noncanonical_match_span() -> None:
    matcher = TokenPatternMatcher((TokenSequence((b"ab",)),))
    sequence = TokenSequence((b"ab", b"cd"))
    dfa = make_token_dfa(
        states=frozenset({0, 1, 2}),
        alphabet=frozenset({b"ab", b"cd"}),
        initial=0,
        accepting=frozenset({2}),
        delta={(0, b"ab"): 1, (1, b"cd"): 2},
    )

    assert dfa.accepts(sequence)
    assert not dfa.accepts(TokenSequence((b"ab",)))
    with pytest.raises(ValueError, match="not accepted"):
        matcher.find_canonical(sequence, dfa)


def test_empty_patterns_are_rejected() -> None:
    with pytest.raises(ValueError):
        TokenPatternMatcher((TokenSequence(()),))
    with pytest.raises(ValueError):
        match_bytes(b"abc", (b"",))
