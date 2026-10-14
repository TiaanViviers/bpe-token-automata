"""Pathological and robustness tests (spec §6.6).

Malformed dictionaries and unsupported encodings are covered by
``test_dictionary_parser.py``; this module does not duplicate them.
Do not enumerate all compositions of strings longer than 8 bytes.
"""

from pathlib import Path

from bpe_token_automata.automaton import construct_token_dfa, universal_token_dfa
from bpe_token_automata.dictionary import Dictionary, MergeRule, parse_dictionary_path
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.tokens import TokenSequence
from bpe_token_automata.transducer import compile_tokenizer
from differential import assert_section_62, assert_unique_tokenization

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dictionaries"
REPEATED_LENGTHS = (8, 16, 32, 64)
SPACE = b" "
NFD_EACUTE = b"e\xcc\x81"
NFC_EACUTE = b"\xc3\xa9"
GRINNING_FACE = b"\xf0\x9f\x98\x80"
MIXED = SPACE + NFD_EACUTE + GRINNING_FACE
LONG_UNSPACED = b"ab" * 32  # length 64, no pre-tokenizer boundary


def _unary_alphabet() -> frozenset[bytes]:
    return frozenset({b"a"})


def test_repeated_a_n_increasing_lengths() -> None:
    parsed = parse_dictionary_path(DATA / "unary_self_merge.merges")
    assert parsed.dictionary is not None
    alphabet = _unary_alphabet()
    base = universal_token_dfa(alphabet)
    dfa = construct_token_dfa(parsed.dictionary, base).final
    machine = compile_tokenizer(parsed.dictionary, base)
    for length in REPEATED_LENGTHS:
        text = b"a" * length
        canonical = assert_section_62(
            parsed.dictionary, alphabet, text, dfa=dfa, machine=machine
        )
        if length <= 8:
            assert_unique_tokenization(dfa, parsed.dictionary, text, canonical)
        else:
            split = TokenSequence.from_bytes(text)
            if split != canonical:
                assert not dfa.accepts(split)


def test_doubling_self_merge_chain() -> None:
    parsed = parse_dictionary_path(DATA / "doubling_self_merge.merges")
    assert parsed.dictionary is not None
    alphabet = _unary_alphabet()
    base = universal_token_dfa(alphabet)
    dfa = construct_token_dfa(parsed.dictionary, base).final
    machine = compile_tokenizer(parsed.dictionary, base)
    for exponent in range(5):
        text = b"a" * (2**exponent)
        canonical = assert_section_62(
            parsed.dictionary, alphabet, text, dfa=dfa, machine=machine
        )
        if len(text) <= 8:
            assert_unique_tokenization(dfa, parsed.dictionary, text, canonical)
    for length in REPEATED_LENGTHS:
        text = b"a" * length
        assert_section_62(parsed.dictionary, alphabet, text, dfa=dfa, machine=machine)


def test_long_input_without_pretokenization_boundaries() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    alphabet = frozenset({b"a", b"b"})
    assert b" " not in LONG_UNSPACED
    assert len(LONG_UNSPACED) == 64
    base = universal_token_dfa(alphabet)
    dfa = construct_token_dfa(parsed.dictionary, base).final
    machine = compile_tokenizer(parsed.dictionary, base)
    canonical = assert_section_62(
        parsed.dictionary, alphabet, LONG_UNSPACED, dfa=dfa, machine=machine
    )
    split = TokenSequence.from_bytes(LONG_UNSPACED)
    assert split != canonical
    assert not dfa.accepts(split)


def test_initial_token_changes_after_append() -> None:
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    alphabet = frozenset({b"a", b"b"})
    short = tokenize_reference(dictionary, b"a")
    longer = tokenize_reference(dictionary, b"aa")
    assert short.tokens == (b"a",)
    assert longer.tokens == (b"aa",)
    assert short != longer
    assert_section_62(dictionary, alphabet, b"a")
    assert_section_62(dictionary, alphabet, b"aa")


def test_mixed_whitespace_combining_mark_and_emoji() -> None:
    alphabet = frozenset({bytes((byte,)) for byte in MIXED})
    dictionary = Dictionary(())
    assert MIXED != SPACE + NFC_EACUTE + GRINNING_FACE
    assert NFC_EACUTE not in MIXED
    canonical = assert_section_62(dictionary, alphabet, MIXED)
    assert canonical == TokenSequence.from_bytes(MIXED)
    nfc_variant = SPACE + NFC_EACUTE + GRINNING_FACE
    nfc_tokens = tokenize_reference(dictionary, nfc_variant)
    assert nfc_tokens != canonical
    assert nfc_tokens.detokenize() != MIXED
