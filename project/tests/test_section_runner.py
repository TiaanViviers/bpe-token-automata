from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "section.py"
GPT2 = ROOT / "data" / "dictionaries" / "gpt2.merges"


def _write_example(directory: Path) -> Path:
    path = directory / "live.merges"
    path.write_text("# text: aba\n# pattern: a\na a\nb a\n", encoding="utf-8")
    return path


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_reference_tokenizer_prints_example2_tokens(tmp_path: Path) -> None:
    path = _write_example(tmp_path)
    result = _run("reference_tokenizer", str(path))

    assert result.returncode == 0
    assert "proper: yes" in result.stdout
    assert "T^D(aba): a⫽ba" in result.stdout


def test_make_token_dfa_prints_serialisation(tmp_path: Path) -> None:
    path = _write_example(tmp_path)
    result = subprocess.run(
        ["make", "token_dfa", str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "states: 2" in result.stdout
    assert "serialisation:" in result.stdout
    assert "0 --aa--> 0" in result.stdout


def test_transducer_agrees_with_reference(tmp_path: Path) -> None:
    path = _write_example(tmp_path)
    result = _run("5.4", str(path))

    assert result.returncode == 0
    assert "transducer: a⫽ba" in result.stdout
    assert "reference: a⫽ba" in result.stdout
    assert "token_sequence_agreement: yes" in result.stdout


def test_examples_show_the_first_merge_triple(tmp_path: Path) -> None:
    path = _write_example(tmp_path)
    result = _run("examples", str(path))

    assert result.returncode == 0
    assert "triples: (0, 0, 0)" in result.stdout
    assert "T^D(aba) after this rule: a⫽ba" in result.stdout


def test_partial_order_compares_disjoint_extensions(tmp_path: Path) -> None:
    path = tmp_path / "partial.merges"
    path.write_text("# text: abcd\na b\nc d\n", encoding="utf-8")
    result = _run("partial_order", str(path))

    assert result.returncode == 0
    assert "disjoint_class: yes" in result.stdout
    assert "extensions: 2" in result.stdout
    assert "extensions_agree: yes" in result.stdout
    assert "0: a ⫽ b, c ⫽ d" in result.stdout
    assert "1: c ⫽ d, a ⫽ b" in result.stdout


def test_pattern_match_reports_the_inner_byte(tmp_path: Path) -> None:
    path = _write_example(tmp_path)
    result = _run("8.11", str(path))

    assert result.returncode == 0
    assert "token_matches: [0,1)" in result.stdout
    assert "byte_matches: [0,1), [2,3)" in result.stdout


def test_large_dictionary_is_not_built() -> None:
    result = _run("5.2", str(GPT2))

    assert result.returncode != 0
    assert "too large to build live" in result.stderr
    assert "serialisation:" not in result.stdout


def test_timeout_study_without_a_file_prints_recorded_stops() -> None:
    result = _run("5.6")

    assert result.returncode == 0
    assert "stop_status=timeout_600s" in result.stdout
    assert "not rerun" in result.stdout
