"""Smoke tests for Section 7.3 Q5–Q6 tokenize evaluation."""

from pathlib import Path

from experiments.tokenize_eval import (
    agreement_row,
    enumerate_strings,
    measure_timed,
    throughput_jobs,
)

from bpe_token_automata.automaton import universal_token_dfa
from bpe_token_automata.dictionary import parse_dictionary_path
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.transducer import compile_tokenizer, tokenize
from minbpe_adapter import LoadedBasicTokenizer

DATA = Path(__file__).resolve().parents[1] / "data" / "dictionaries"


def test_enumerate_ab_le2_has_seven_strings() -> None:
    texts = enumerate_strings(b"ab", 2)
    assert len(texts) == 7


def test_example2_agreement_ab_le2() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    dictionary = parsed.dictionary
    alphabet = frozenset({b"a", b"b"})
    machine = compile_tokenizer(dictionary, universal_token_dfa(alphabet))
    row = agreement_row(
        name="example2_ab_le2",
        texts=enumerate_strings(b"ab", 2),
        left=lambda text: tokenize(machine, text),
        right=lambda text: tokenize_reference(dictionary, text),
        comparators="transducer_vs_reference",
    )
    assert row["n_strings"] == 7
    assert row["n_exact_sequence_match"] == 7
    assert row["match_rate"] == 1.0

    minbpe = LoadedBasicTokenizer(dictionary)
    minbpe_row = agreement_row(
        name="example2_ab_le2_minbpe",
        texts=enumerate_strings(b"ab", 2),
        left=lambda text: tokenize(machine, text),
        right=minbpe.token_sequence,
        comparators="transducer_vs_minbpe",
    )
    assert minbpe_row["match_rate"] == 1.0


def test_throughput_smoke_n8_one_repeat() -> None:
    rows = throughput_jobs(lengths=(8,), repeats=1, timeout_s=5.0, warmup=False)
    example2 = [
        row
        for row in rows
        if row["dictionary"] == "example2" and row["implementation"] == "transducer"
    ]
    assert example2
    row = example2[0]
    assert row["status"] == "ok"
    assert row["n_bytes"] == 8
    bps = row["bytes_per_second_median"]
    assert isinstance(bps, float)
    assert bps > 0
    assert row["compile_seconds_median"] is not None


def test_expired_deadline_omits_median() -> None:
    row = measure_timed(lambda: None, n_bytes=8, repeats=1, timeout_s=0.0, warmup=False)
    assert row["status"] == "timeout_60s"
    assert row["tokenize_seconds_median"] is None
    assert row["bytes_per_second_median"] is None
