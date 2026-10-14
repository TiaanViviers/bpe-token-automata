"""Record Hypothesis counterexamples for spec §6.4 reproducibility.

On a property-test failure, write JSON with the dictionary, seed, input, and
the smallest known counterexample (the last example after shrinking).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bpe_token_automata.dictionary.model import Dictionary
from bpe_token_automata.tokens import Token

HYPOTHESIS_SEED = 0
FAILURE_DIR = Path(__file__).resolve().parent / "hypothesis_failures"
LATEST_PATH = FAILURE_DIR / "latest.json"

_current: dict[str, Any] | None = None


def _token_hex(token: Token) -> str:
    return token.hex()


def record_example(
    dictionary: Dictionary,
    alphabet: frozenset[bytes],
    text: bytes,
) -> dict[str, Any]:
    """Remember the current generated example (overwritten as Hypothesis shrinks)."""
    global _current
    rules = [
        {
            "index": rule.index,
            "left": _token_hex(rule.left),
            "right": _token_hex(rule.right),
        }
        for rule in dictionary.rules
    ]
    payload: dict[str, Any] = {
        "seed": HYPOTHESIS_SEED,
        "dictionary": rules,
        "alphabet": sorted(_token_hex(symbol) for symbol in alphabet),
        "input": _token_hex(text),
    }
    _current = payload
    return payload


def example_note(payload: dict[str, Any]) -> str:
    """One-line record for Hypothesis ``note()`` / the pytest log."""
    rules = payload["dictionary"]
    merges = ", ".join(f"{row['left']}⫽{row['right']}" for row in rules) or "(empty)"
    return f"seed={payload['seed']} dictionary=[{merges}] input={payload['input']}"


def write_failure_log(*, error: str = "") -> Path | None:
    """Write the current example as the smallest known counterexample."""
    if _current is None:
        return None
    FAILURE_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "seed": _current["seed"],
        "dictionary": _current["dictionary"],
        "alphabet": _current["alphabet"],
        "input": _current["input"],
        "smallest_known_counterexample": {
            "seed": _current["seed"],
            "dictionary": _current["dictionary"],
            "input": _current["input"],
        },
        "error": error,
    }
    LATEST_PATH.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return LATEST_PATH


def current_example() -> dict[str, Any] | None:
    return _current
