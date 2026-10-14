"""Per-rule fresh-state patterns (course spec §7.3 question 3)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from bpe_token_automata.automaton import (
    CompactOptions,
    byte_alphabet,
    construct_compact_token_dfa,
    construct_token_dfa,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import Dictionary, MergeRule, parse_dictionary_path
from bpe_token_automata.tokens import Token
from experiments.host import host_metadata, write_csv, write_json

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "results"
DATA = ROOT / "data" / "dictionaries"
REALISTIC_PREFIX = 250
CSV_FIELDS = (
    "case",
    "o2_state_avoidance",
    "o3_clean_copy",
    "rule_index",
    "self_merge",
    "baseline_n_fresh",
    "baseline_n_states",
    "compact_n_fresh",
    "compact_n_states",
    "compact_n_defaults",
    "compact_reused",
)


def _require_dictionary(path: Path) -> Dictionary:
    parsed = parse_dictionary_path(path)
    if parsed.dictionary is None:
        raise ValueError(f"failed to parse {path}")
    return parsed.dictionary


def paper_chain() -> Dictionary:
    """Paper [5] chain ``a⫽b, ab⫽b, abb⫽b`` (compact_compare fixture)."""
    return Dictionary(
        (
            MergeRule(left=b"a", right=b"b", index=0),
            MergeRule(left=b"ab", right=b"b", index=1),
            MergeRule(left=b"abb", right=b"b", index=2),
        )
    )


def measure_case(
    name: str,
    dictionary: Dictionary,
    alphabet: frozenset[Token],
    options: CompactOptions | None = None,
) -> dict[str, Any]:
    """Per-rule baseline vs compact ``n_fresh`` for one dictionary and flag set."""
    opts = CompactOptions() if options is None else options
    base = universal_token_dfa(alphabet)
    baseline = construct_token_dfa(dictionary, base)
    compact = construct_compact_token_dfa(dictionary, base, opts)
    steps: list[dict[str, Any]] = []
    for rule, base_step, compact_step in zip(
        dictionary.rules, baseline.steps, compact.steps, strict=True
    ):
        reused = compact_step.n_fresh == 0
        steps.append(
            {
                "case": name,
                "o2_state_avoidance": opts.o2_state_avoidance,
                "o3_clean_copy": opts.o3_clean_copy,
                "rule_index": rule.index,
                "self_merge": rule.left == rule.right,
                "baseline_n_fresh": base_step.n_fresh,
                "baseline_n_states": base_step.n_states,
                "compact_n_fresh": compact_step.n_fresh,
                "compact_n_states": compact_step.n_states,
                "compact_n_defaults": compact_step.n_defaults,
                "compact_reused": reused,
            }
        )
    summary: dict[str, object]
    if steps:
        summary = {
            "n_rules": len(steps),
            "n_self_merge": sum(1 for row in steps if row["self_merge"]),
            "n_distinct": sum(1 for row in steps if not row["self_merge"]),
            "n_compact_reused": sum(1 for row in steps if row["compact_reused"]),
            "baseline_n_fresh_total": sum(
                int(row["baseline_n_fresh"]) for row in steps
            ),
            "compact_n_fresh_total": sum(int(row["compact_n_fresh"]) for row in steps),
            "baseline_n_states_final": steps[-1]["baseline_n_states"],
            "compact_n_states_final": steps[-1]["compact_n_states"],
        }
    else:
        compact_a0 = compact.automata[0]
        summary = {
            "n_rules": 0,
            "n_self_merge": 0,
            "n_distinct": 0,
            "n_compact_reused": 0,
            "baseline_n_fresh_total": 0,
            "compact_n_fresh_total": 0,
            "baseline_n_states_final": baseline.final.n_states,
            "compact_n_states_final": compact_a0.n_states_excluding_sink,
        }
    return {
        "case": name,
        "n_rules": len(dictionary),
        "o2_state_avoidance": opts.o2_state_avoidance,
        "o3_clean_copy": opts.o3_clean_copy,
        "baseline_n_states_a0": baseline.automata[0].n_states,
        "compact_n_states_a0": compact.automata[0].n_states_excluding_sink,
        "steps": steps,
        "summary": summary,
    }


def study_cases(*, include_realistic: bool) -> list[dict[str, Any]]:
    example2 = _require_dictionary(DATA / "example2.merges")
    unary = _require_dictionary(DATA / "unary_self_merge.merges")
    doubling = _require_dictionary(DATA / "doubling_self_merge.merges")
    chain = paper_chain()
    off = CompactOptions(o2_state_avoidance=False, o3_clean_copy=False)
    cases = [
        measure_case("example2", example2, frozenset({b"a", b"b"})),
        measure_case("unary_self_merge", unary, frozenset({b"a"})),
        measure_case("paper_example1_chain", chain, frozenset({b"a", b"b"})),
        measure_case(
            "paper_example1_chain_o2_o3_off",
            chain,
            frozenset({b"a", b"b"}),
            off,
        ),
        measure_case("doubling_self_merge", doubling, frozenset({b"a"})),
    ]
    if include_realistic:
        gpt2 = _require_dictionary(DATA / "gpt2.merges")
        smollm2 = _require_dictionary(DATA / "smollm2.merges")
        alphabet = byte_alphabet()
        cases.append(
            measure_case(
                "gpt2_prefix_250",
                Dictionary(gpt2.rules[:REALISTIC_PREFIX]),
                alphabet,
            )
        )
        cases.append(
            measure_case(
                "smollm2_prefix_250",
                Dictionary(smollm2.rules[:REALISTIC_PREFIX]),
                alphabet,
            )
        )
    return cases


def flatten_steps(cases: list[dict[str, Any]]) -> list[Mapping[str, object]]:
    rows: list[Mapping[str, object]] = []
    for case in cases:
        rows.extend(case["steps"])
    return rows


def build_payload(cases: list[dict[str, Any]]) -> dict[str, object]:
    return {
        "host": host_metadata(),
        "realistic_prefix": REALISTIC_PREFIX,
        "notes": (
            "compact_reused means compact n_fresh == 0 for that rule "
            "(O2 avoidance or O3 clean-copy). Compact n_states excludes the sink. "
            "GPT-2 / SmolLM rows are prefix 250 only. O4 is not implemented."
        ),
        "cases": cases,
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    cases = study_cases(include_realistic=True)
    payload = build_payload(cases)
    json_path = RESULTS / "rule_patterns.json"
    write_json(json_path, payload)
    write_csv(RESULTS / "rule_patterns.csv", flatten_steps(cases), CSV_FIELDS)
    print(json_path)


if __name__ == "__main__":
    main()
