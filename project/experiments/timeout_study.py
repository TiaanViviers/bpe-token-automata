"""Section 5.6 larger-dictionary construction timeout study.

Measures baseline and compact construction on GPT-2 and SmolLM 2 prefixes.
Does not belong in ``make check``. Peak memory is RSS (``ru_maxrss``), not
tracemalloc. Timeouts and OOM are recorded results.

Linux ``ru_maxrss`` is kilobytes; this script converts to bytes. ``RLIMIT_AS``
caps virtual address space, which is not the same as RSS.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import signal
import subprocess
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal, TextIO, cast

from bpe_token_automata.automaton import (
    CompactOptions,
    DelayedInputDFA,
    TokenDFA,
    apply_compact_merge,
    apply_merge,
    byte_alphabet,
    lift_to_delayed,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import parse_dictionary_path
from bpe_token_automata.dictionary.model import Dictionary
from bpe_token_automata.dictionary.validator import validate_proper

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "results"
CACHE = ROOT / "experiments" / ".cache" / "timeout"
DATA = ROOT / "data" / "dictionaries"

CHECKPOINT_PREFIXES: frozenset[int] = frozenset(
    {
        0,
        1,
        2,
        5,
        10,
        25,
        50,
        100,
        250,
        500,
        1000,
        2500,
        5000,
        10_000,
        25_000,
        50_000,
    }
)
TIMEOUT_SHORT_S = 60.0
TIMEOUT_LONG_S = 600.0
MEMORY_LIMIT_BYTES = 8 * 1024**3
ConstructionName = Literal["baseline", "compact"]
StopStatus = Literal[
    "completed",
    "timeout_600s",
    "memory",
    "unsupported",
    "error",
]

STUDY_RUNS: tuple[tuple[str, ConstructionName], ...] = (
    ("gpt2", "baseline"),
    ("gpt2", "compact"),
    ("smollm2", "baseline"),
    ("smollm2", "compact"),
)


def rss_bytes() -> int:
    """Peak resident set of this process, in bytes."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    if sys.platform == "darwin":
        return int(usage.ru_maxrss)
    return int(usage.ru_maxrss) * 1024


def apply_address_space_limit(memory_limit_bytes: int) -> str:
    """Best-effort ``RLIMIT_AS``. Returns how the cap was applied."""
    if not hasattr(resource, "RLIMIT_AS"):
        return "unsupported"
    try:
        resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))
    except (ValueError, OSError) as exc:
        return f"failed:{type(exc).__name__}"
    return "rlimit_as"


def host_metadata() -> dict[str, object]:
    mem_kb: int | None = None
    meminfo = Path("/proc/meminfo")
    if meminfo.is_file():
        for line in meminfo.read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                mem_kb = int(line.split()[1])
                break
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "cpu_count": os.cpu_count(),
        "host_memory_bytes": None if mem_kb is None else mem_kb * 1024,
        "ru_maxrss_unit": "bytes_on_darwin_else_kilobytes",
    }


def _counts(
    construction: ConstructionName, automaton: TokenDFA | DelayedInputDFA
) -> dict[str, int]:
    if construction == "baseline":
        dfa = cast(TokenDFA, automaton)
        return {
            "n_states": dfa.n_states,
            "n_final": dfa.n_final,
            "n_tokens": dfa.n_tokens,
            "n_transitions": dfa.n_transitions,
            "n_defaults": 0,
            "n_sink_states": 0,
        }
    compact = cast(DelayedInputDFA, automaton)
    return {
        "n_states": compact.n_states_excluding_sink,
        "n_final": compact.n_final,
        "n_tokens": compact.n_tokens,
        "n_transitions": compact.n_transitions,
        "n_defaults": compact.n_defaults,
        "n_sink_states": 1,
    }


def _write_record(handle: TextIO, record: Mapping[str, object]) -> None:
    handle.write(json.dumps(record, sort_keys=True) + "\n")
    handle.flush()
    os.fsync(handle.fileno())


def should_checkpoint(n_rules: int) -> bool:
    return n_rules in CHECKPOINT_PREFIXES


def run_child(
    *,
    dictionary: Dictionary,
    dictionary_name: str,
    construction: ConstructionName,
    jsonl_path: Path,
    timeout_short_s: float,
    timeout_long_s: float,
    memory_limit_bytes: int,
    apply_rlimit: bool,
) -> StopStatus:
    """Incrementally merge from A0. JSONL records are always ``status=ok``."""
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    if apply_rlimit:
        apply_address_space_limit(memory_limit_bytes)

    start = time.monotonic()
    current: TokenDFA | DelayedInputDFA
    if construction == "compact":
        current = lift_to_delayed(universal_token_dfa(byte_alphabet()))
    else:
        current = universal_token_dfa(byte_alphabet())

    marked_short = False
    stop: StopStatus = "completed"
    with jsonl_path.open("w", encoding="utf-8") as handle:

        def emit(n_rules: int) -> None:
            elapsed = time.monotonic() - start
            record: dict[str, object] = {
                "dictionary": dictionary_name,
                "construction": construction,
                "n_rules": n_rules,
                "elapsed_s": elapsed,
                "rss_bytes": rss_bytes(),
                "status": "ok",
                **_counts(construction, current),
            }
            _write_record(handle, record)

        emit(0)
        last_emitted = 0
        for index, rule in enumerate(dictionary.rules, start=1):
            elapsed = time.monotonic() - start
            if elapsed >= timeout_long_s:
                stop = "timeout_600s"
                break
            if rss_bytes() >= memory_limit_bytes:
                stop = "memory"
                break
            try:
                if construction == "compact":
                    current, _fresh = apply_compact_merge(
                        cast(DelayedInputDFA, current), rule
                    )
                    del _fresh
                else:
                    current, trace = apply_merge(cast(TokenDFA, current), rule)
                    del trace
            except MemoryError:
                stop = "memory"
                break
            elapsed = time.monotonic() - start
            crossed_short = elapsed >= timeout_short_s and not marked_short
            if should_checkpoint(index) or crossed_short:
                emit(index)
                last_emitted = index
            if crossed_short:
                marked_short = True
            if elapsed >= timeout_long_s:
                stop = "timeout_600s"
                if last_emitted != index:
                    emit(index)
                    last_emitted = index
                break
            if rss_bytes() >= memory_limit_bytes:
                stop = "memory"
                if last_emitted != index:
                    emit(index)
                    last_emitted = index
                break
        else:
            stop = "completed"
            last = len(dictionary.rules)
            if last_emitted != last:
                emit(last)

    return stop


def load_checkpoints(jsonl_path: Path) -> list[dict[str, Any]]:
    if not jsonl_path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _boundary(
    checkpoints: list[dict[str, Any]],
    *,
    timeout_short_s: float,
    stop: StopStatus,
) -> dict[str, object]:
    if not checkpoints:
        return {
            "largest_prefix_ok": None,
            "prefix_at_60s": None,
            "stop_status": stop,
        }
    largest = checkpoints[-1]
    at_short = None
    for row in checkpoints:
        if float(row["elapsed_s"]) <= timeout_short_s:
            at_short = row
    return {
        "largest_prefix_ok": largest["n_rules"],
        "largest_elapsed_s": largest["elapsed_s"],
        "largest_rss_bytes": largest["rss_bytes"],
        "prefix_at_60s": None if at_short is None else at_short["n_rules"],
        "elapsed_at_60s": None if at_short is None else at_short["elapsed_s"],
        "stop_status": stop,
    }


def summarise(
    runs: list[dict[str, Any]],
    *,
    timeout_short_s: float,
    timeout_long_s: float,
    memory_limit_bytes: int,
    host: Mapping[str, object],
) -> dict[str, object]:
    by_dict: dict[str, dict[str, list[int]]] = {}
    comparison_rows: list[dict[str, object]] = []
    for dictionary_name in sorted({str(run["dictionary"]) for run in runs}):
        grouped = {
            str(run["construction"]): run
            for run in runs
            if run["dictionary"] == dictionary_name
        }
        baseline = grouped.get("baseline")
        compact = grouped.get("compact")
        shared: list[int] = []
        if baseline is not None and compact is not None:
            base_ok = {int(row["n_rules"]): row for row in baseline["checkpoints"]}
            compact_ok = {int(row["n_rules"]): row for row in compact["checkpoints"]}
            shared = sorted(set(base_ok) & set(compact_ok))
            for n_rules in shared:
                left = base_ok[n_rules]
                right = compact_ok[n_rules]
                comparison_rows.append(
                    {
                        "dictionary": dictionary_name,
                        "n_rules": n_rules,
                        "baseline_n_states": left["n_states"],
                        "baseline_n_transitions": left["n_transitions"],
                        "baseline_seconds": left["elapsed_s"],
                        "baseline_rss_bytes": left["rss_bytes"],
                        "compact_n_states": right["n_states"],
                        "compact_n_transitions": right["n_transitions"],
                        "compact_n_defaults": right["n_defaults"],
                        "compact_seconds": right["elapsed_s"],
                        "compact_rss_bytes": right["rss_bytes"],
                    }
                )
        by_dict[dictionary_name] = {"shared_prefixes": shared}

    return {
        "limits": {
            "timeout_s_short": timeout_short_s,
            "timeout_s_long": timeout_long_s,
            "memory_limit_bytes": memory_limit_bytes,
            "memory_measure": "ru_maxrss",
            "memory_cap_mechanism": "RLIMIT_AS plus ru_maxrss poll",
        },
        "compact_options": {
            "o1_default_transitions": True,
            "o2_state_avoidance": CompactOptions().o2_state_avoidance,
            "o3_clean_copy": CompactOptions().o3_clean_copy,
            "o4_prefix_forest": False,
        },
        "host": dict(host),
        "notes": (
            "Construction time starts at A0 after the dictionary is parsed. "
            "JSONL checkpoints are status=ok only. timeout_60s is the last "
            "prefix with elapsed_s <= timeout_s_short; it is not a kill. "
            "timeout_600s / memory / error / completed are stop statuses. "
            "Comparison rows include only prefixes both constructions finished. "
            "Do not average timeouts into successful times. O4 is not implemented. "
            "RSS is ru_maxrss (KiB on Linux, converted to bytes)."
        ),
        "runs": runs,
        "shared_prefixes": by_dict,
        "comparison_rows": comparison_rows,
    }


def _parse_dictionary(path: Path) -> Dictionary | None:
    parsed = parse_dictionary_path(path)
    if not parsed.ok or parsed.dictionary is None:
        return None
    if not validate_proper(parsed.dictionary).ok:
        return None
    return parsed.dictionary


def _child_argv(
    *,
    dictionary_path: Path,
    dictionary_name: str,
    construction: ConstructionName,
    jsonl_path: Path,
    timeout_short_s: float,
    timeout_long_s: float,
    memory_limit_bytes: int,
    apply_rlimit: bool,
) -> list[str]:
    argv = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--child",
        "--dictionary-path",
        str(dictionary_path),
        "--dictionary-name",
        dictionary_name,
        "--construction",
        construction,
        "--jsonl",
        str(jsonl_path),
        "--timeout-short",
        str(timeout_short_s),
        "--timeout-long",
        str(timeout_long_s),
        "--memory-bytes",
        str(memory_limit_bytes),
    ]
    if not apply_rlimit:
        argv.append("--no-rlimit")
    return argv


def launch_child(
    *,
    dictionary_path: Path,
    dictionary_name: str,
    construction: ConstructionName,
    jsonl_path: Path,
    timeout_short_s: float,
    timeout_long_s: float,
    memory_limit_bytes: int,
    apply_rlimit: bool,
) -> dict[str, Any]:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    if jsonl_path.exists():
        jsonl_path.unlink()
    join_timeout = timeout_long_s + 30.0
    try:
        completed = subprocess.run(
            _child_argv(
                dictionary_path=dictionary_path,
                dictionary_name=dictionary_name,
                construction=construction,
                jsonl_path=jsonl_path,
                timeout_short_s=timeout_short_s,
                timeout_long_s=timeout_long_s,
                memory_limit_bytes=memory_limit_bytes,
                apply_rlimit=apply_rlimit,
            ),
            check=False,
            timeout=join_timeout,
            cwd=str(ROOT),
        )
        returncode = completed.returncode
        timed_out_join = False
    except subprocess.TimeoutExpired:
        returncode = None
        timed_out_join = True

    checkpoints = load_checkpoints(jsonl_path)
    stop: StopStatus
    if timed_out_join:
        stop = "timeout_600s"
    elif returncode == 0:
        # Child prints the stop status on stdout as a last JSON line via exit.
        stop = "completed"
        if checkpoints and float(checkpoints[-1]["elapsed_s"]) >= timeout_long_s:
            stop = "timeout_600s"
    elif returncode is not None and returncode < 0:
        sig = -returncode
        stop = "memory" if sig in {signal.SIGKILL, signal.SIGSEGV} else "error"
    elif returncode not in {0, None}:
        stop = "error"
    else:
        stop = "error"

    marker = jsonl_path.with_suffix(".status")
    if marker.is_file():
        reported = marker.read_text(encoding="utf-8").strip()
        if reported in {
            "completed",
            "timeout_600s",
            "memory",
            "unsupported",
            "error",
        }:
            stop = cast(StopStatus, reported)

    boundary = _boundary(checkpoints, timeout_short_s=timeout_short_s, stop=stop)
    return {
        "dictionary": dictionary_name,
        "construction": construction,
        "returncode": returncode,
        "timed_out_join": timed_out_join,
        "checkpoints": checkpoints,
        **boundary,
    }


def _run_parent(args: argparse.Namespace) -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    host = host_metadata()
    runs: list[dict[str, Any]] = []
    for dictionary_name, construction in STUDY_RUNS:
        if args.only:
            wanted = f"{dictionary_name}:{construction}"
            if wanted != args.only:
                continue
        path = DATA / f"{dictionary_name}.merges"
        jsonl_path = CACHE / f"{dictionary_name}_{construction}.jsonl"
        print(f"starting {dictionary_name} {construction}", flush=True)
        runs.append(
            launch_child(
                dictionary_path=path,
                dictionary_name=dictionary_name,
                construction=construction,
                jsonl_path=jsonl_path,
                timeout_short_s=args.timeout_short,
                timeout_long_s=args.timeout_long,
                memory_limit_bytes=args.memory_bytes,
                apply_rlimit=not args.no_rlimit,
            )
        )
    payload = summarise(
        runs,
        timeout_short_s=args.timeout_short,
        timeout_long_s=args.timeout_long,
        memory_limit_bytes=args.memory_bytes,
        host=host,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    csv_path = output.with_suffix(".csv")
    rows = cast(list[dict[str, object]], payload["comparison_rows"])
    if rows:
        keys = list(rows[0].keys())
        lines = [",".join(keys)]
        for row in rows:
            lines.append(",".join(str(row[key]) for key in keys))
        csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(output)
    return 0


def _run_child(args: argparse.Namespace) -> int:
    status_path = Path(args.jsonl).with_suffix(".status")
    status_path.parent.mkdir(parents=True, exist_ok=True)
    dictionary = _parse_dictionary(Path(args.dictionary_path))
    if dictionary is None:
        status_path.write_text("unsupported\n", encoding="utf-8")
        return 2
    try:
        stop = run_child(
            dictionary=dictionary,
            dictionary_name=args.dictionary_name,
            construction=args.construction,
            jsonl_path=Path(args.jsonl),
            timeout_short_s=args.timeout_short,
            timeout_long_s=args.timeout_long,
            memory_limit_bytes=args.memory_bytes,
            apply_rlimit=not args.no_rlimit,
        )
    except MemoryError:
        stop = "memory"
    except Exception as exc:  # noqa: BLE001 — child must record unexpected errors
        Path(args.jsonl).parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text("error\n", encoding="utf-8")
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    status_path.write_text(stop + "\n", encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child", action="store_true")
    parser.add_argument("--dictionary-path", type=Path)
    parser.add_argument("--dictionary-name", default="")
    parser.add_argument(
        "--construction", choices=("baseline", "compact"), default="baseline"
    )
    parser.add_argument("--jsonl", type=Path)
    parser.add_argument("--timeout-short", type=float, default=TIMEOUT_SHORT_S)
    parser.add_argument("--timeout-long", type=float, default=TIMEOUT_LONG_S)
    parser.add_argument("--memory-bytes", type=int, default=MEMORY_LIMIT_BYTES)
    parser.add_argument("--no-rlimit", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=RESULTS / "timeout_study.json",
    )
    parser.add_argument("--only", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.child:
        if args.dictionary_path is None or args.jsonl is None:
            build_parser().error("--child requires --dictionary-path and --jsonl")
        return _run_child(args)
    return _run_parent(args)


if __name__ == "__main__":
    raise SystemExit(main())
