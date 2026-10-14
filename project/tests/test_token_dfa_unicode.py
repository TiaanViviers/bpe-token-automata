"""Original Unicode/emoji token-DFA examples and token-identity tests."""

from itertools import product
from pathlib import Path

import pytest

from bpe_token_automata.automaton import (
    TokenDFA,
    TokenDFAError,
    construct_token_dfa,
    parse_string_dfa_yaml,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import Dictionary, parse_dictionary_path
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.tokens import TokenSequence, format_token_sequence

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MAX_LENGTH = 4

EACUTE_NFC = b"\xc3\xa9"
EACUTE_NFD = b"e\xcc\x81"
GRINNING_FACE = b"\xf0\x9f\x98\x80"


def _assert_prefix_agreement(
    dictionary: Dictionary,
    alphabet: frozenset[bytes],
    automata: tuple[TokenDFA, ...],
    max_length: int,
) -> None:
    symbols = tuple(sorted(alphabet))
    for index, dfa in enumerate(automata):
        prefix = Dictionary(dictionary.rules[:index])
        for length in range(max_length + 1):
            for parts in product(symbols, repeat=length):
                text = b"".join(parts)
                canonical = tokenize_reference(prefix, text)
                assert dfa.accepts(canonical)
                base = TokenSequence.from_bytes(text)
                if base.tokens != canonical.tokens:
                    assert not dfa.accepts(base)


def test_nfc_and_nfd_eacute_are_different_byte_strings() -> None:
    assert EACUTE_NFC == b"\xc3\xa9"
    assert EACUTE_NFD == b"e\xcc\x81"
    assert EACUTE_NFC != EACUTE_NFD


def test_unicode_code_point_is_not_a_base_symbol() -> None:
    with pytest.raises(TokenDFAError, match="length 1"):
        universal_token_dfa(frozenset({EACUTE_NFC}))
    with pytest.raises(TokenDFAError, match="length 1"):
        universal_token_dfa(frozenset({GRINNING_FACE}))


def test_original_finite_ab_merge_trace() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "original_finite_ab.merges")
    assert parsed.dictionary is not None
    base = parse_string_dfa_yaml(
        (DATA / "automata" / "finite_ab.yaml").read_text(encoding="utf-8")
    )
    result = construct_token_dfa(parsed.dictionary, base)
    trace = result.traces[0]

    assert trace.triples == ((0, 1, 2),)
    assert trace.s2_to_fresh == ((1, 3),)
    assert trace.added_uv == ((0, b"ab", 2),)
    assert trace.omitted_labels == frozenset({b"b"})
    assert trace.inherited == ()
    assert trace.redirected == ((0, b"a", 1, 3),)

    final = result.final
    assert final.accepts(TokenSequence((b"ab",)))
    assert not final.accepts(TokenSequence((b"a", b"b")))
    assert 3 not in final.accepting

    before = tokenize_reference(Dictionary(()), b"ab")
    after = tokenize_reference(parsed.dictionary, b"ab")
    assert before.tokens == (b"a", b"b")
    assert after.tokens == (b"ab",)
    assert result.automata[0].accepts(before)
    assert not final.accepts(before)
    assert final.accepts(after)


def test_original_eacute_byte_merge() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "original_eacute.merges")
    assert parsed.dictionary is not None
    alphabet = frozenset({b"\xc3", b"\xa9"})
    result = construct_token_dfa(parsed.dictionary, universal_token_dfa(alphabet))
    trace = result.traces[0]

    assert trace.triples == ((0, 0, 0),)
    assert trace.s2_to_fresh == ((0, 1),)
    assert trace.added_uv == ((0, EACUTE_NFC, 0),)
    assert trace.omitted_labels == frozenset({b"\xa9"})
    assert trace.inherited == ((1, b"\xc3", 0), (1, EACUTE_NFC, 0))
    assert trace.redirected == (
        (0, b"\xc3", 0, 1),
        (1, b"\xc3", 0, 1),
    )

    canonical = tokenize_reference(parsed.dictionary, EACUTE_NFC)
    assert canonical.tokens == (EACUTE_NFC,)
    assert result.final.accepts(canonical)
    assert not result.final.accepts(TokenSequence.from_bytes(EACUTE_NFC))

    nfd = tokenize_reference(parsed.dictionary, EACUTE_NFD)
    assert nfd.tokens == (b"e", b"\xcc", b"\x81")
    assert format_token_sequence(nfd) == r"e⫽\xcc⫽\x81"
    assert canonical != nfd

    _assert_prefix_agreement(parsed.dictionary, alphabet, result.automata, MAX_LENGTH)


def test_original_emoji_byte_chain() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "original_emoji.merges")
    assert parsed.dictionary is not None
    alphabet = frozenset({b"\xf0", b"\x9f", b"\x98", b"\x80"})
    result = construct_token_dfa(parsed.dictionary, universal_token_dfa(alphabet))

    first, second, third = result.traces
    assert first.triples == ((0, 0, 0),)
    assert first.s2_to_fresh == ((0, 1),)
    assert first.added_uv == ((0, b"\xf0\x9f", 0),)
    assert first.omitted_labels == frozenset({b"\x9f"})

    assert second.triples == ((0, 0, 0), (1, 0, 0))
    assert second.s2_to_fresh == ((0, 2),)
    assert second.added_uv == ((0, b"\xf0\x9f\x98", 0), (1, b"\xf0\x9f\x98", 0))

    assert third.triples == ((0, 0, 0), (1, 0, 0), (2, 0, 0))
    assert third.s2_to_fresh == ((0, 3),)
    assert third.added_uv == (
        (0, GRINNING_FACE, 0),
        (1, GRINNING_FACE, 0),
        (2, GRINNING_FACE, 0),
    )

    canonical = tokenize_reference(parsed.dictionary, GRINNING_FACE)
    assert canonical.tokens == (GRINNING_FACE,)
    assert result.final.accepts(canonical)
    assert not result.final.accepts(TokenSequence.from_bytes(GRINNING_FACE))

    _assert_prefix_agreement(parsed.dictionary, alphabet, result.automata, 3)


def test_token_identity_is_byte_equality() -> None:
    merged = TokenSequence((EACUTE_NFC,))
    split = TokenSequence((b"\xc3", b"\xa9"))
    assert merged.tokens != split.tokens
    assert merged.detokenize() == split.detokenize() == EACUTE_NFC
