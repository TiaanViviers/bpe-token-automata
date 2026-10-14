"""compile_tokenizer / tokenize vs the independent reference oracle."""

from itertools import product
from pathlib import Path

import pytest

from bpe_token_automata.automaton import (
    parse_string_dfa_yaml,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import (
    Dictionary,
    ImproperDictionaryError,
    MergeRule,
    parse_dictionary_path,
)
from bpe_token_automata.tokens import TokenSequence
from bpe_token_automata.transducer import (
    TokenizationError,
    compile_tokenizer,
    tokenize,
)
from differential import assert_section_62

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def _alphabet(*symbols: str) -> frozenset[bytes]:
    return frozenset(symbol.encode("ascii") for symbol in symbols)


def test_empty_input_on_universal_language() -> None:
    dictionary = Dictionary(())
    machine = compile_tokenizer(dictionary, universal_token_dfa(_alphabet("a")))
    assert tokenize(machine, b"") == TokenSequence(())


def test_self_merge_matches_reference() -> None:
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    alphabet = _alphabet("a", "b")
    for text in (b"", b"a", b"aa", b"aaa", b"ab", b"ba", b"b"):
        assert_section_62(dictionary, alphabet, text)


def test_improper_dictionary_is_rejected() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "improper_example3.merges")
    assert parsed.dictionary is not None
    with pytest.raises(ImproperDictionaryError):
        compile_tokenizer(parsed.dictionary, universal_token_dfa(_alphabet("a", "b")))


def test_unknown_byte_is_rejected() -> None:
    dictionary = Dictionary(())
    machine = compile_tokenizer(dictionary, universal_token_dfa(_alphabet("a")))
    with pytest.raises(TokenizationError):
        tokenize(machine, b"b")


def test_user_supplied_language_rejects_prefixes() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "original_finite_ab.merges")
    assert parsed.dictionary is not None
    base = parse_string_dfa_yaml(
        (DATA / "automata" / "finite_ab.yaml").read_text(encoding="utf-8")
    )
    machine = compile_tokenizer(parsed.dictionary, base)
    assert tokenize(machine, b"ab") == TokenSequence((b"ab",))
    with pytest.raises(TokenizationError):
        tokenize(machine, b"")
    with pytest.raises(TokenizationError):
        tokenize(machine, b"a")
    with pytest.raises(TokenizationError):
        tokenize(machine, b"b")


def test_example2_sample_strings() -> None:
    parsed = parse_dictionary_path(DATA / "dictionaries" / "example2.merges")
    assert parsed.dictionary is not None
    alphabet = _alphabet("a", "b")
    for symbols in product(b"ab", repeat=3):
        assert_section_62(parsed.dictionary, alphabet, bytes(symbols))
