"""Thin tokenization time/memory comparison (course spec §5.4, not §5.6)."""

from __future__ import annotations

import json
import platform
import statistics
import sys
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path

from bpe_token_automata.automaton import universal_token_dfa
from bpe_token_automata.dictionary import Dictionary, MergeRule, parse_dictionary_path
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.transducer import compile_tokenizer, tokenize

ROOT = Path(__file__).resolve().parents[1]
RESULTS = Path(__file__).resolve().parent / "results"
DATA = ROOT / "data" / "dictionaries"
REPEATS = 7


def _peak_bytes(fn: Callable[[], object]) -> tuple[object, int]:
    tracemalloc.start()
    try:
        result = fn()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, peak


def _median_seconds(fn: Callable[[], object], repeats: int = REPEATS) -> float:
    samples: list[float] = []
    fn()  # warmup
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def _measure(
    name: str,
    dictionary: Dictionary,
    alphabet: frozenset[bytes],
    text: bytes,
) -> dict[str, object]:
    base = universal_token_dfa(alphabet)
    compile_time = _median_seconds(lambda: compile_tokenizer(dictionary, base))
    machine, compile_peak = _peak_bytes(lambda: compile_tokenizer(dictionary, base))

    def run_transducer() -> object:
        return tokenize(machine, text)

    def run_reference() -> object:
        return tokenize_reference(dictionary, text)

    transduced = run_transducer()
    referenced = run_reference()
    agree = transduced == referenced
    return {
        "case": name,
        "n_bytes": len(text),
        "n_rules": len(dictionary),
        "n_transducer_states": len(machine.states),
        "compile_seconds_median": compile_time,
        "compile_peak_bytes": compile_peak,
        "tokenize_seconds_median": _median_seconds(run_transducer),
        "tokenize_peak_bytes": _peak_bytes(run_transducer)[1],
        "reference_seconds_median": _median_seconds(run_reference),
        "reference_peak_bytes": _peak_bytes(run_reference)[1],
        "token_sequence_agreement": agree,
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    example2 = parse_dictionary_path(DATA / "example2.merges").dictionary
    unary = parse_dictionary_path(DATA / "unary_self_merge.merges").dictionary
    assert example2 is not None
    assert unary is not None
    self_merge = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    rows = [
        _measure("example2_ababab", example2, frozenset({b"a", b"b"}), b"ab" * 32),
        _measure("self_merge_a_n", self_merge, frozenset({b"a", b"b"}), b"a" * 256),
        _measure("unary_chain_a_n", unary, frozenset({b"a"}), b"a" * 128),
        _measure("empty_dict_ab", Dictionary(()), frozenset({b"a", b"b"}), b"ab" * 64),
    ]
    payload = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "repeats": REPEATS,
        "notes": (
            "Compile time is separated from tokenize time. "
            "Peak memory is tracemalloc in this process, not RSS. "
            "No pre-tokenization. Dictionaries are tiny; this is not §5.6."
        ),
        "rows": rows,
    }
    out = RESULTS / "transducer_tokenize.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
