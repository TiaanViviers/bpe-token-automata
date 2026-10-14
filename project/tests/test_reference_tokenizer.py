"""Tests for the independent reference tokenizer."""

from pathlib import Path

import pytest

from bpe_token_automata.dictionary import ImproperDictionaryError, parse_dictionary_path
from bpe_token_automata.dictionary.model import Dictionary, MergeRule
from bpe_token_automata.reference_tokenizer import _find_best_merge, tokenize_reference
from bpe_token_automata.tokens import TokenSequence, detokenize, format_token_sequence

DATA = Path(__file__).resolve().parents[1] / "data" / "dictionaries"


def test_empty_dictionary_returns_base_tokenization() -> None:
    dictionary = Dictionary(())
    result = tokenize_reference(dictionary, b"abc")
    assert result.tokens == (b"a", b"b", b"c")


def test_empty_input_returns_empty_sequence() -> None:
    dictionary = Dictionary(())
    result = tokenize_reference(dictionary, b"")
    assert result.tokens == ()


def test_paper_example1_tokenization() -> None:
    parsed = parse_dictionary_path(DATA / "example1.merges")
    assert parsed.dictionary is not None
    result = tokenize_reference(parsed.dictionary, b"abcbcab")
    assert format_token_sequence(result) == "abc⫽bc⫽ab"


def test_example1_derivation_steps() -> None:
    """Paper Example 1 steps (preserved by the proper reordering of D)."""
    parsed = parse_dictionary_path(DATA / "example1.merges")
    assert parsed.dictionary is not None

    tokens = list(TokenSequence.from_bytes(b"abcbcab").tokens)
    expected = [
        (b"a", b"b", b"c", b"b", b"c", b"a", b"b"),
        (b"ab", b"c", b"b", b"c", b"a", b"b"),
        (b"ab", b"c", b"b", b"c", b"ab"),
        (b"ab", b"c", b"bc", b"ab"),
        (b"abc", b"bc", b"ab"),
    ]

    for current, nxt in zip(expected[:-1], expected[1:], strict=True):
        assert tuple(tokens) == current
        merge = _find_best_merge(tokens, parsed.dictionary)
        assert merge is not None
        position, rule = merge
        tokens[position : position + 2] = [rule.merged]
        assert tuple(tokens) == nxt

    assert _find_best_merge(tokens, parsed.dictionary) is None


def test_self_merge_applies_leftmost_once_per_step() -> None:
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    result = tokenize_reference(dictionary, b"aaa")
    assert result.tokens == (b"aa", b"a")


def test_detokenize_after_tokenize_is_identity() -> None:
    parsed = parse_dictionary_path(DATA / "example1.merges")
    assert parsed.dictionary is not None
    text = b"abcbcab"
    tokenized = tokenize_reference(parsed.dictionary, text)
    assert detokenize(tokenized) == text


def test_improper_dictionary_is_rejected() -> None:
    parsed = parse_dictionary_path(DATA / "improper_example3.merges")
    assert parsed.dictionary is not None
    with pytest.raises(ImproperDictionaryError):
        tokenize_reference(parsed.dictionary, b"abababab")
