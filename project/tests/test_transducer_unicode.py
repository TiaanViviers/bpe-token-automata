"""Unicode/emoji transducer agreement with the reference tokenizer."""

from itertools import product
from pathlib import Path

from bpe_token_automata.automaton import construct_token_dfa, universal_token_dfa
from bpe_token_automata.dictionary import parse_dictionary_path
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.transducer import compile_tokenizer, tokenize

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dictionaries"
EACUTE_NFC = b"\xc3\xa9"
GRINNING_FACE = b"\xf0\x9f\x98\x80"
MAX_LENGTH = 3


def _agree(path: Path, alphabet: frozenset[bytes], samples: tuple[bytes, ...]) -> None:
    parsed = parse_dictionary_path(path)
    assert parsed.dictionary is not None
    base = universal_token_dfa(alphabet)
    dfa = construct_token_dfa(parsed.dictionary, base).final
    machine = compile_tokenizer(parsed.dictionary, base)
    for text in samples:
        output = tokenize(machine, text)
        assert output == tokenize_reference(parsed.dictionary, text)
        assert output.detokenize() == text
        assert dfa.accepts(output)


def test_eacute_nfc_transducer() -> None:
    alphabet = frozenset({b"\xc3", b"\xa9"})
    _agree(
        DATA / "original_eacute.merges",
        alphabet,
        (b"", b"\xc3", b"\xa9", EACUTE_NFC),
    )


def test_grinning_face_transducer() -> None:
    alphabet = frozenset({b"\xf0", b"\x9f", b"\x98", b"\x80"})
    samples = [GRINNING_FACE, b""]
    symbols = tuple(sorted(alphabet))
    for length in range(MAX_LENGTH + 1):
        for parts in product(symbols, repeat=length):
            samples.append(b"".join(parts))
    _agree(DATA / "original_emoji.merges", alphabet, tuple(samples))
