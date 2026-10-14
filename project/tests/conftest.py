"""Pytest hooks for Section 6 Hypothesis failure logs."""

from __future__ import annotations

import pytest

from hypothesis_log import write_failure_log


def pytest_exception_interact(
    node: pytest.Item,
    call: pytest.CallInfo[object],
    report: pytest.TestReport,
) -> None:
    if not report.failed:
        return
    if "test_random_proper_dictionary_agrees_with_oracle" not in node.nodeid:
        return
    write_failure_log(error=str(report.longrepr)[:8000])
