"""Tests for dictionary parsing."""

from pathlib import Path

from bpe_token_automata.dictionary import (
    parse_dictionary_path,
    parse_merge_list,
    parse_yaml_dictionary,
)

DATA = Path(__file__).resolve().parents[1] / "data" / "dictionaries"


def test_parse_example1_merge_list_preserves_order() -> None:
    result = parse_dictionary_path(DATA / "example1.merges")
    assert result.ok
    assert result.dictionary is not None
    assert [rule.merged for rule in result.dictionary.rules] == [
        b"ab",
        b"bc",
        b"abc",
        b"abc",
    ]


def test_parse_yaml_fixture() -> None:
    text = (DATA / "proper_with_useless_rule.yaml").read_text(encoding="utf-8")
    result = parse_yaml_dictionary(text)
    assert result.ok
    assert result.dictionary is not None
    assert len(result.dictionary) == 4


def test_reject_malformed_line() -> None:
    result = parse_merge_list("a\nonlyone")
    assert not result.ok
    assert result.issues[0].kind.value == "malformed_line"


def test_reject_duplicate_rule() -> None:
    result = parse_merge_list("a b\na b")
    assert not result.ok
    assert result.issues[0].kind.value == "duplicate_rule"


def test_reject_empty_token() -> None:
    result = parse_merge_list("a⫽")
    assert not result.ok
    assert result.issues[0].kind.value == "empty_token"


def test_byte_escape_decoding() -> None:
    result = parse_merge_list(r"\x61 \x62")
    assert result.ok
    assert result.dictionary is not None
    assert result.dictionary.rules[0].left == b"a"
    assert result.dictionary.rules[0].right == b"b"


def test_reject_unsupported_escape() -> None:
    result = parse_merge_list(r"\u0061 b")
    assert not result.ok
    assert result.issues[0].kind.value == "unsupported_encoding"


def test_utf8_character_literal_is_one_token() -> None:
    character = parse_merge_list("é a")
    assert character.ok
    assert character.dictionary is not None
    assert character.dictionary.rules[0].left == b"\xc3\xa9"
    assert len(character.dictionary.rules[0].left) == 2

    escaped = parse_merge_list(r"\xc3 \xa9")
    assert escaped.ok
    assert escaped.dictionary is not None
    assert escaped.dictionary.rules[0].left == b"\xc3"
    assert escaped.dictionary.rules[0].right == b"\xa9"
