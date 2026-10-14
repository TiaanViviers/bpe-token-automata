"""Tests for the restricted partial-order extension in section 8.6."""

from __future__ import annotations

from itertools import product

import pytest

from bpe_token_automata import (
    Dictionary,
    MergeRule,
    OrderedRules,
    TokenSequence,
    check_linear_extensions,
    construct_token_dfa,
    is_byte_disjoint_base,
    linear_extensions,
    tokenize_reference,
    universal_token_dfa,
)


def _rules(*pairs: tuple[bytes, bytes]) -> tuple[MergeRule, ...]:
    return tuple(
        MergeRule(left, right, index) for index, (left, right) in enumerate(pairs)
    )


def _bounded_inputs(alphabet: tuple[bytes, ...], length: int) -> tuple[bytes, ...]:
    """Return every string in the alphabet of length at most ``length``."""
    return tuple(
        b"".join(parts)
        for size in range(length + 1)
        for parts in product(alphabet, repeat=size)
    )


def test_disjoint_rules_commute_on_bounded_inputs() -> None:
    """The 341 strings in {a,b,c,d} of length at most 4 are checked."""
    rules = _rules((b"a", b"b"), (b"c", b"d"))
    result = check_linear_extensions(
        OrderedRules(rules), _bounded_inputs((b"a", b"b", b"c", b"d"), 4)
    )

    assert result.disjoint_class is True
    assert len(result.extensions) == 2
    assert result.extensions_agree is True
    for extension in result.extensions:
        assert tokenize_reference(extension, b"abcd") == TokenSequence((b"ab", b"cd"))
    assert result.dfa_agrees is True
    assert result.dfa_witness is None
    assert result.state_counts is not None and len(result.state_counts) == 2
    assert result.extensions[0].rules == _rules((b"a", b"b"), (b"c", b"d"))
    assert result.extensions[1].rules == _rules((b"c", b"d"), (b"a", b"b"))


def test_precedence_restricts_three_rule_extensions() -> None:
    rules = _rules((b"a", b"b"), (b"c", b"d"), (b"e", b"f"))
    order = OrderedRules(rules, precedes=((0, 1),))
    extensions = linear_extensions(order)

    assert [
        tuple(rule.left for rule in extension.rules) for extension in extensions
    ] == [(b"a", b"c", b"e"), (b"a", b"e", b"c"), (b"e", b"a", b"c")]
    result = check_linear_extensions(
        order, _bounded_inputs((b"a", b"b", b"c", b"d", b"e", b"f"), 2)
    )
    assert result.disjoint_class is True
    assert result.extensions_agree is True


def test_overlapping_orders_report_reference_and_dfa_counterexamples() -> None:
    result = check_linear_extensions(
        OrderedRules(_rules((b"a", b"b"), (b"b", b"a"))), (b"aba",)
    )

    assert result.disjoint_class is False
    assert len(result.extensions) == 2
    assert result.extensions_agree is False
    assert result.counterexample_input == b"aba"
    assert result.left_tokens == TokenSequence((b"ab", b"a"))
    assert result.right_tokens == TokenSequence((b"a", b"ba"))
    assert result.dfa_witness is not None
    alphabet = frozenset({b"a", b"b"})
    left = construct_token_dfa(
        result.extensions[0], universal_token_dfa(alphabet)
    ).final
    right = construct_token_dfa(
        result.extensions[1], universal_token_dfa(alphabet)
    ).final
    assert left.accepts(result.dfa_witness) != right.accepts(result.dfa_witness)


def test_improper_extension_is_dependency_evidence() -> None:
    result = check_linear_extensions(
        OrderedRules(_rules((b"ab", b"c"), (b"d", b"e"))), (b"abc",)
    )

    assert result.disjoint_class is False
    assert result.extensions_agree is None
    assert result.improper_extension == result.extensions[0]
    assert result.counterexample_input is None
    assert result.state_counts is None


def test_cycle_is_rejected() -> None:
    with pytest.raises(ValueError, match="cycle"):
        linear_extensions(
            OrderedRules(_rules((b"a", b"b"), (b"c", b"d")), ((0, 1), (1, 0)))
        )


def test_extension_cap_is_rejected_before_comparison() -> None:
    rules = _rules(
        (b"a", b"b"),
        (b"c", b"d"),
        (b"e", b"f"),
        (b"g", b"h"),
        (b"i", b"j"),
    )
    with pytest.raises(ValueError, match="24"):
        linear_extensions(OrderedRules(rules))


def test_single_extension_is_vacuously_agreeing_not_commutation() -> None:
    result = check_linear_extensions(OrderedRules(_rules((b"a", b"b"))), (b"ab",))

    assert result.disjoint_class is True
    assert len(result.extensions) == 1
    assert result.extensions_agree is True
    assert result.dfa_agrees is True


def test_empty_inputs_are_rejected_after_properness() -> None:
    with pytest.raises(ValueError, match="at least one input"):
        check_linear_extensions(OrderedRules(_rules((b"a", b"b"), (b"c", b"d"))), ())


def test_disjoint_class_rejects_empty_shared_and_multibyte_rules() -> None:
    assert is_byte_disjoint_base(()) is False
    assert is_byte_disjoint_base(_rules((b"a", b"b"), (b"b", b"a"))) is False
    assert is_byte_disjoint_base(_rules((b"ab", b"c"), (b"d", b"e"))) is False
    assert is_byte_disjoint_base(_rules((b"a", b"a"), (b"b", b"b"))) is True


def test_extensions_reindex_rules_in_extension_order() -> None:
    original = (
        MergeRule(b"a", b"b", 99),
        MergeRule(b"c", b"d", 42),
    )
    extensions = linear_extensions(OrderedRules(original, ((1, 0),)))
    assert extensions[0] == Dictionary(
        (MergeRule(b"c", b"d", 0), MergeRule(b"a", b"b", 1))
    )
