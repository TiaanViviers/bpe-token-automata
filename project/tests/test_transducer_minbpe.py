"""Differential tests against minbpe BasicTokenizer (spec §5.4)."""

from itertools import product
from pathlib import Path

from bpe_token_automata.automaton import universal_token_dfa
from bpe_token_automata.dictionary import Dictionary, MergeRule, parse_dictionary_path
from bpe_token_automata.transducer import compile_tokenizer, tokenize
from minbpe_adapter import LoadedBasicTokenizer

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dictionaries"
MAX_LENGTH = 6


def _agree(dictionary: Dictionary, alphabet: frozenset[bytes], text: bytes) -> None:
    machine = compile_tokenizer(dictionary, universal_token_dfa(alphabet))
    minbpe = LoadedBasicTokenizer(dictionary)
    assert tokenize(machine, text) == minbpe.token_sequence(text)


def test_example2_matches_minbpe_on_token_sequences() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    alphabet = frozenset({b"a", b"b"})
    for length in range(MAX_LENGTH + 1):
        for symbols in product(b"ab", repeat=length):
            _agree(parsed.dictionary, alphabet, bytes(symbols))


def test_empty_and_self_merge_match_minbpe() -> None:
    alphabet = frozenset({b"a", b"b"})
    _agree(Dictionary(()), alphabet, b"aba")
    self_merge = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    for text in (b"", b"a", b"aa", b"aaa", b"ab"):
        _agree(self_merge, alphabet, text)
