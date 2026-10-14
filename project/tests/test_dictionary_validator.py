"""Tests for proper-dictionary validation."""

from pathlib import Path

from bpe_token_automata.dictionary import (
    is_proper,
    parse_dictionary_path,
    parse_merge_list,
    validate_proper,
)

DATA = Path(__file__).resolve().parents[1] / "data" / "dictionaries"


def test_example1_is_proper() -> None:
    result = parse_dictionary_path(DATA / "example1.merges")
    assert result.dictionary is not None
    assert is_proper(result.dictionary)


def test_example3_is_improper() -> None:
    result = parse_dictionary_path(DATA / "improper_example3.merges")
    assert result.dictionary is not None
    validation = validate_proper(result.dictionary)
    assert not validation.ok
    assert validation.issues[0].kind.value == "improper_rule"


def test_improper_right_component() -> None:
    result = parse_merge_list("a b\na bc")
    assert result.dictionary is not None
    validation = validate_proper(result.dictionary)
    assert not validation.ok
    assert validation.issues[0].kind.value == "improper_rule"
    assert validation.issues[0].rule_index == 1


def test_proper_with_useless_rule_still_validates() -> None:
    result = parse_dictionary_path(DATA / "proper_with_useless_rule.yaml")
    assert result.dictionary is not None
    assert is_proper(result.dictionary)
