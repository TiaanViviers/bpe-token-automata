"""Host metadata and timing helpers for Section 7 experiments."""

from __future__ import annotations

import csv
import importlib.metadata
import json
import os
import platform
import resource
import signal
import statistics
import sys
import time
import tracemalloc
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path


class DeadlineExceeded(TimeoutError):
    """Wall-clock deadline for one experiment row."""


def rss_bytes() -> int:
    """Peak resident set of this process, in bytes."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    if sys.platform == "darwin":
        return int(usage.ru_maxrss)
    return int(usage.ru_maxrss) * 1024


def host_memory_bytes(meminfo: Path | None = None) -> int | None:
    """Host RAM from ``/proc/meminfo``, or None if unavailable."""
    path = Path("/proc/meminfo") if meminfo is None else meminfo
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("MemTotal:"):
            return int(line.split()[1]) * 1024
    return None


def library_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name in ("pyyaml", "hypothesis"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def host_metadata() -> dict[str, object]:
    """Processor, RAM, OS, Python, and locked library versions."""
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "cpu_count": os.cpu_count(),
        "host_memory_bytes": host_memory_bytes(),
        "libraries": library_versions(),
    }


def median_seconds(
    fn: Callable[[], object],
    *,
    repeats: int = 7,
    warmup: bool = True,
) -> float:
    """Warm up once, then return the median of ``repeats`` wall-clock samples."""
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    if warmup:
        fn()
    samples: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def peak_tracemalloc[T](fn: Callable[[], T]) -> tuple[T, int]:
    """Run ``fn`` and return ``(result, peak_traced_bytes)``."""
    tracemalloc.start()
    try:
        result = fn()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, peak


def call_with_timeout[T](fn: Callable[[], T], timeout_s: float) -> T:
    """Run ``fn``; raise ``DeadlineExceeded`` if it exceeds ``timeout_s``.

    Uses ``SIGALRM`` / ``setitimer`` (Unix).
    """
    if timeout_s <= 0:
        raise DeadlineExceeded("no time remaining")
    if not hasattr(signal, "SIGALRM") or not hasattr(signal, "setitimer"):
        raise DeadlineExceeded("wall-clock timeouts require SIGALRM")

    def _handler(_signum: int, _frame: object) -> None:
        raise DeadlineExceeded("wall-clock timeout")

    previous = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, timeout_s)
    try:
        return fn()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous)


def write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _csv_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def write_csv(
    path: Path,
    rows: Sequence[Mapping[str, object]],
    fieldnames: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(fieldnames), extrasaction="ignore"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _csv_cell(row.get(key)) for key in fieldnames})
