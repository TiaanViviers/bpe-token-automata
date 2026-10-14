"""Bounded differential tests: token DFA vs independent reference tokenizer."""

from itertools import product
from pathlib import Path

from bpe_token_automata.automaton import construct_token_dfa, universal_token_dfa
from bpe_token_automata.dictionary import parse_dictionary_path
from bpe_token_automata.transducer import compile_tokenizer
from differential import assert_section_62, assert_unique_tokenization

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dictionaries"
MAX_LENGTH = 8


def test_example2_dfa_agrees_with_reference_tokenizer() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    dictionary = parsed.dictionary
    alphabet = frozenset({b"a", b"b"})
    base = universal_token_dfa(alphabet)
    dfa = construct_token_dfa(dictionary, base).final
    machine = compile_tokenizer(dictionary, base)

    for length in range(MAX_LENGTH + 1):
        for symbols in product(b"ab", repeat=length):
            text = bytes(symbols)
            canonical = assert_section_62(
                dictionary, alphabet, text, dfa=dfa, machine=machine
            )
            assert_unique_tokenization(dfa, dictionary, text, canonical)
