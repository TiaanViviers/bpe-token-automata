"""Smoke tests for Section 7 experiment host helpers."""

from pathlib import Path

import pytest
from experiments.host import (
    DeadlineExceeded,
    call_with_timeout,
    host_memory_bytes,
    host_metadata,
    median_seconds,
    peak_tracemalloc,
)


def test_host_metadata_has_required_keys() -> None:
    meta = host_metadata()
    for key in (
        "python",
        "platform",
        "processor",
        "cpu_count",
        "host_memory_bytes",
        "libraries",
    ):
        assert key in meta
    libraries = meta["libraries"]
    assert isinstance(libraries, dict)
    assert "pyyaml" in libraries
    assert "hypothesis" in libraries


def test_host_memory_bytes_missing_file_is_none(tmp_path: Path) -> None:
    assert host_memory_bytes(tmp_path / "no-such-meminfo") is None


def test_host_memory_bytes_reads_memtotal(tmp_path: Path) -> None:
    meminfo = tmp_path / "meminfo"
    meminfo.write_text("MemTotal:       2048 kB\n", encoding="utf-8")
    assert host_memory_bytes(meminfo) == 2048 * 1024


def test_median_seconds_noop() -> None:
    samples = median_seconds(lambda: None, repeats=1, warmup=False)
    assert isinstance(samples, float)
    assert samples >= 0.0


def test_peak_tracemalloc_is_int() -> None:
    result, peak = peak_tracemalloc(lambda: bytearray(64))
    assert result is not None
    assert isinstance(peak, int)
    assert peak >= 0


def test_call_with_timeout_expired() -> None:
    with pytest.raises(DeadlineExceeded):
        call_with_timeout(lambda: None, 0.0)
