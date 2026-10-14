"""Thin baseline vs compact construction comparison (course spec §5.5, not §5.6)."""

from __future__ import annotations

import json
import platform
import statistics
import sys
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path

from bpe_token_automata.automaton import (
    construct_compact_token_dfa,
    construct_token_dfa,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import Dictionary, MergeRule, parse_dictionary_path
from bpe_token_automata.tokens import Token

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
    fn()
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def _measure_prefix(
    name: str,
    dictionary: Dictionary,
    alphabet: frozenset[Token],
    n_rules: int,
) -> dict[str, object]:
    prefix = Dictionary(dictionary.rules[:n_rules])
    base = universal_token_dfa(alphabet)

    def build_baseline() -> object:
        return construct_token_dfa(prefix, base)

    def build_compact() -> object:
        return construct_compact_token_dfa(prefix, base)

    baseline = construct_token_dfa(prefix, base)
    compact = construct_compact_token_dfa(prefix, base)
    return {
        "case": name,
        "n_rules": n_rules,
        "baseline_n_states": baseline.final.n_states,
        "baseline_n_transitions": baseline.final.n_transitions,
        "compact_n_states": compact.final.n_states_excluding_sink,
        "compact_n_sink_states": 1,
        "compact_n_transitions": compact.final.n_transitions,
        "compact_n_defaults": compact.final.n_defaults,
        "o2_state_avoidance": compact.options.o2_state_avoidance,
        "o3_clean_copy": compact.options.o3_clean_copy,
        "baseline_seconds_median": _median_seconds(build_baseline),
        "compact_seconds_median": _median_seconds(build_compact),
        "compact_peak_bytes": _peak_bytes(build_compact)[1],
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    example2 = parse_dictionary_path(DATA / "example2.merges").dictionary
    unary = parse_dictionary_path(DATA / "unary_self_merge.merges").dictionary
    assert example2 is not None
    assert unary is not None
    chain = Dictionary(
        (
            MergeRule(left=b"a", right=b"b", index=0),
            MergeRule(left=b"ab", right=b"b", index=1),
            MergeRule(left=b"abb", right=b"b", index=2),
        )
    )
    rows: list[dict[str, object]] = []
    for n_rules in range(len(example2) + 1):
        rows.append(
            _measure_prefix("example2", example2, frozenset({b"a", b"b"}), n_rules)
        )
    for n_rules in range(len(unary) + 1):
        rows.append(
            _measure_prefix("unary_self_merge", unary, frozenset({b"a"}), n_rules)
        )
    for n_rules in range(len(chain) + 1):
        rows.append(
            _measure_prefix(
                "paper_example1_chain", chain, frozenset({b"a", b"b"}), n_rules
            )
        )
    payload = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "repeats": REPEATS,
        "notes": (
            "Compact n_states excludes the distinguished sink (always 1). "
            "Peak memory is tracemalloc in this process, not RSS. "
            "O1 is always on; O2 and O3 are the public defaults. "
            "O4 is not implemented. "
            "Dictionaries are tiny; this is not §5.6."
        ),
        "rows": rows,
    }
    out = RESULTS / "compact_compare.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
