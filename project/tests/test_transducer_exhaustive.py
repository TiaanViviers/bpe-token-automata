"""Exhaustive bounded transducer checks (spec §6.3)."""

from itertools import product
from pathlib import Path

from bpe_token_automata.automaton import construct_token_dfa, universal_token_dfa
from bpe_token_automata.dictionary import parse_dictionary_path
from bpe_token_automata.transducer import compile_tokenizer
from differential import assert_section_62, assert_unique_tokenization

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dictionaries"
MAX_LENGTH = 8
UNARY_MAX_LENGTH = 8


def test_unary_self_merge_chain_exhaustive() -> None:
    parsed = parse_dictionary_path(DATA / "unary_self_merge.merges")
    assert parsed.dictionary is not None
    alphabet = frozenset({b"a"})
    base = universal_token_dfa(alphabet)
    dfa = construct_token_dfa(parsed.dictionary, base).final
    machine = compile_tokenizer(parsed.dictionary, base)
    for length in range(UNARY_MAX_LENGTH + 1):
        text = b"a" * length
        canonical = assert_section_62(
            parsed.dictionary, alphabet, text, dfa=dfa, machine=machine
        )
        assert_unique_tokenization(dfa, parsed.dictionary, text, canonical)


def test_example2_transducer_enumerates_token_uniqueness_bound() -> None:
    """Within {a,b}^{<=8}, the DFA accepts exactly one composition per string."""
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    alphabet = frozenset({b"a", b"b"})
    base = universal_token_dfa(alphabet)
    dfa = construct_token_dfa(parsed.dictionary, base).final
    machine = compile_tokenizer(parsed.dictionary, base)
    for length in range(MAX_LENGTH + 1):
        for symbols in product(b"ab", repeat=length):
            text = bytes(symbols)
            canonical = assert_section_62(
                parsed.dictionary, alphabet, text, dfa=dfa, machine=machine
            )
            assert_unique_tokenization(dfa, parsed.dictionary, text, canonical)
