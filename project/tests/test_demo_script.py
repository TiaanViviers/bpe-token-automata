from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "demo.py"


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_walkthrough_shows_reference_transducer_and_improper_dictionary() -> None:
    result = _run("walkthrough")

    assert result.returncode == 0
    assert "Reference tokenization T^D" in result.stdout
    assert "Transducer tokenization" in result.stdout
    assert "Agrees with reference: True" in result.stdout
    assert "improper_example3.merges is improper" in result.stdout


def test_large_dictionary_is_refused_before_construction() -> None:
    result = _run("dfa", "--dictionary", "data/dictionaries/gpt2.merges")

    assert result.returncode != 0
    assert "too large to build live" in result.stderr
    assert "Baseline token DFA" not in result.stdout
