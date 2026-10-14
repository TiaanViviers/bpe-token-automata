"""Smoke tests for the Section 5.6 timeout harness (not the 10-minute study)."""

from pathlib import Path

from experiments.timeout_study import (
    CHECKPOINT_PREFIXES,
    MEMORY_LIMIT_BYTES,
    TIMEOUT_LONG_S,
    TIMEOUT_SHORT_S,
    launch_child,
    load_checkpoints,
    run_child,
    summarise,
)

from bpe_token_automata.dictionary import parse_dictionary_path

DATA = Path(__file__).resolve().parents[1] / "data" / "dictionaries"


def test_checkpoint_prefixes_include_required_milestones() -> None:
    assert 0 in CHECKPOINT_PREFIXES
    assert 1 in CHECKPOINT_PREFIXES
    assert 50_000 in CHECKPOINT_PREFIXES
    assert TIMEOUT_SHORT_S == 60
    assert TIMEOUT_LONG_S == 600
    assert MEMORY_LIMIT_BYTES == 8 * 1024**3


def test_zero_long_timeout_records_a0_and_stops(tmp_path: Path) -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    jsonl = tmp_path / "child.jsonl"
    stop = run_child(
        dictionary=parsed.dictionary,
        dictionary_name="example2",
        construction="baseline",
        jsonl_path=jsonl,
        timeout_short_s=60.0,
        timeout_long_s=0.0,
        memory_limit_bytes=MEMORY_LIMIT_BYTES,
        apply_rlimit=False,
    )
    assert stop == "timeout_600s"
    rows = load_checkpoints(jsonl)
    assert rows
    assert rows[0]["n_rules"] == 0
    assert rows[0]["status"] == "ok"
    assert max(int(row["n_rules"]) for row in rows) == 0
    assert rows[0]["n_sink_states"] == 0
    assert rows[0]["n_defaults"] == 0
    assert rows[0]["n_transitions"] == 256


def test_example2_subprocess_completes_or_times_out(tmp_path: Path) -> None:
    jsonl = tmp_path / "sub.jsonl"
    result = launch_child(
        dictionary_path=DATA / "example2.merges",
        dictionary_name="example2",
        construction="compact",
        jsonl_path=jsonl,
        timeout_short_s=60.0,
        timeout_long_s=5.0,
        memory_limit_bytes=MEMORY_LIMIT_BYTES,
        apply_rlimit=False,
    )
    assert jsonl.is_file()
    assert result["checkpoints"]
    assert result["stop_status"] in {
        "completed",
        "timeout_600s",
        "memory",
        "error",
    }
    assert result["largest_prefix_ok"] is not None
    compact = result["checkpoints"][-1]
    assert compact["n_sink_states"] == 1
    assert "n_defaults" in compact


def test_summarise_shared_prefixes_only() -> None:
    runs = [
        {
            "dictionary": "demo",
            "construction": "baseline",
            "stop_status": "timeout_600s",
            "checkpoints": [
                {
                    "n_rules": 0,
                    "n_states": 1,
                    "n_transitions": 2,
                    "elapsed_s": 0.0,
                    "rss_bytes": 1,
                    "n_defaults": 0,
                },
                {
                    "n_rules": 1,
                    "n_states": 2,
                    "n_transitions": 4,
                    "elapsed_s": 0.1,
                    "rss_bytes": 2,
                    "n_defaults": 0,
                },
            ],
        },
        {
            "dictionary": "demo",
            "construction": "compact",
            "stop_status": "completed",
            "checkpoints": [
                {
                    "n_rules": 0,
                    "n_states": 1,
                    "n_transitions": 2,
                    "elapsed_s": 0.0,
                    "rss_bytes": 1,
                    "n_defaults": 0,
                },
                {
                    "n_rules": 1,
                    "n_states": 2,
                    "n_transitions": 3,
                    "elapsed_s": 0.05,
                    "rss_bytes": 2,
                    "n_defaults": 1,
                },
                {
                    "n_rules": 2,
                    "n_states": 2,
                    "n_transitions": 4,
                    "elapsed_s": 0.08,
                    "rss_bytes": 2,
                    "n_defaults": 1,
                },
            ],
        },
    ]
    payload = summarise(
        runs,
        timeout_short_s=60.0,
        timeout_long_s=600.0,
        memory_limit_bytes=MEMORY_LIMIT_BYTES,
        host={"python": "3.12"},
    )
    limits = payload["limits"]
    options = payload["compact_options"]
    shared_map = payload["shared_prefixes"]
    rows = payload["comparison_rows"]
    notes = payload["notes"]
    assert isinstance(limits, dict)
    assert isinstance(options, dict)
    assert isinstance(shared_map, dict)
    assert isinstance(rows, list)
    assert isinstance(notes, str)
    assert limits["timeout_s_short"] == 60.0
    assert limits["memory_measure"] == "ru_maxrss"
    assert options["o4_prefix_forest"] is False
    demo = shared_map["demo"]
    assert isinstance(demo, dict)
    assert demo["shared_prefixes"] == [0, 1]
    assert len(rows) == 2
    assert rows[1]["n_rules"] == 1
    assert rows[1]["compact_n_defaults"] == 1
    assert "timeout_600s" in notes
