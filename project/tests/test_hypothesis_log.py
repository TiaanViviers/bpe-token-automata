"""Spec §6.4 failure-log fields."""

import json
from pathlib import Path

import pytest

from bpe_token_automata.dictionary.model import Dictionary, MergeRule
from hypothesis_log import (
    HYPOTHESIS_SEED,
    example_note,
    record_example,
)


def test_failure_log_records_seed_dictionary_input_and_counterexample(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import hypothesis_log as log

    monkeypatch.setattr(log, "FAILURE_DIR", tmp_path)
    monkeypatch.setattr(log, "LATEST_PATH", tmp_path / "latest.json")
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    payload = record_example(dictionary, frozenset({b"a"}), b"aa")
    assert payload["seed"] == HYPOTHESIS_SEED
    path = log.write_failure_log(error="assertion failed")
    assert path is not None
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["seed"] == 0
    assert record["dictionary"] == [{"index": 0, "left": "61", "right": "61"}]
    assert record["input"] == "6161"
    counterexample = record["smallest_known_counterexample"]
    assert counterexample["input"] == "6161"
    assert counterexample["seed"] == 0
    assert counterexample["dictionary"] == record["dictionary"]
    assert "61" in example_note(payload)
    assert f"seed={HYPOTHESIS_SEED}" in example_note(payload)
