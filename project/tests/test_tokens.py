"""Tests for token and token-sequence utilities."""

from bpe_token_automata.tokens import (
    TokenSequence,
    detokenize,
    format_token_label,
    format_token_sequence,
    parse_token_sequence,
)


def test_base_tokenization_splits_bytes() -> None:
    sequence = TokenSequence.from_bytes(b"abc")
    assert sequence.tokens == (b"a", b"b", b"c")


def test_detokenize_round_trip() -> None:
    data = b"abcbcab"
    sequence = TokenSequence.from_bytes(data)
    assert detokenize(sequence) == data


def test_format_and_parse_token_sequence() -> None:
    sequence = parse_token_sequence("abc⫽bc⫽ab")
    assert format_token_sequence(sequence) == "abc⫽bc⫽ab"
    assert detokenize(sequence) == b"abcbcab"


def test_format_token_label_uses_hex_for_non_ascii() -> None:
    assert format_token_label(b"a") == "a"
    assert format_token_label(b"\xf0") == r"\xf0"
    assert format_token_label(b"\xc3\xa9") == r"\xc3\xa9"


def test_format_token_sequence_allows_incomplete_utf8() -> None:
    sequence = TokenSequence((b"\xf0", b"\x9f"))
    assert format_token_sequence(sequence) == r"\xf0⫽\x9f"
