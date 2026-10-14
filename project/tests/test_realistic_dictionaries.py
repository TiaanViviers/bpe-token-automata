"""Parse, validate, and smoke-construct committed realistic dictionaries."""

from pathlib import Path

import pytest

from bpe_token_automata.automaton import (
    construct_compact_token_dfa,
    construct_token_dfa,
    universal_token_dfa,
)
from bpe_token_automata.automaton.construction import byte_alphabet
from bpe_token_automata.dictionary import Dictionary, parse_dictionary_path
from bpe_token_automata.dictionary.validator import validate_proper

DATA = Path(__file__).resolve().parents[1] / "data" / "dictionaries"

REALISTIC = (
    ("gpt2.merges", 50_000),
    ("smollm2.merges", 48_900),
)


@pytest.mark.parametrize(("filename", "n_rules"), REALISTIC)
def test_committed_realistic_dictionary_parses_and_is_proper(
    filename: str, n_rules: int
) -> None:
    result = parse_dictionary_path(DATA / filename)
    assert result.ok
    assert result.dictionary is not None
    assert len(result.dictionary) == n_rules
    assert validate_proper(result.dictionary).ok


@pytest.mark.parametrize("n_rules", [0, 1, 2])
@pytest.mark.parametrize("filename", ["gpt2.merges", "smollm2.merges"])
def test_byte_alphabet_construction_smoke(filename: str, n_rules: int) -> None:
    parsed = parse_dictionary_path(DATA / filename)
    assert parsed.dictionary is not None
    prefix = Dictionary(parsed.dictionary.rules[:n_rules])
    base = universal_token_dfa(byte_alphabet())
    baseline = construct_token_dfa(prefix, base)
    compact = construct_compact_token_dfa(prefix, base)
    assert baseline.final.n_states >= 1
    assert compact.final.n_states_excluding_sink >= 1
    if n_rules == 0:
        assert baseline.final.n_states == 1
        assert baseline.final.n_transitions == 256
