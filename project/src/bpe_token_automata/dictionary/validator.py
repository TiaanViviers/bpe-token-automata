"""Proper-dictionary validation (Berglund & van der Merwe [6], Definition 5)."""

from __future__ import annotations

from bpe_token_automata.dictionary.errors import (
    DictionaryIssue,
    IssueKind,
    ValidationResult,
)
from bpe_token_automata.dictionary.model import Dictionary
from bpe_token_automata.tokens import Token


def validate_proper(dictionary: Dictionary) -> ValidationResult:
    """Return whether the dictionary is proper in the sense of Definition 5."""
    issues: list[DictionaryIssue] = []
    produced: set[Token] = set()

    for rule in dictionary.rules:
        for side, component in (("left", rule.left), ("right", rule.right)):
            if len(component) > 1 and component not in produced:
                issues.append(
                    DictionaryIssue(
                        kind=IssueKind.IMPROPER_RULE,
                        message=(
                            f"rule {rule.index} ({side}={component!r}) uses token "
                            "not produced by any higher-priority rule"
                        ),
                        rule_index=rule.index,
                    )
                )
        produced.add(rule.merged)

    return ValidationResult(issues=tuple(issues))


def is_proper(dictionary: Dictionary) -> bool:
    """Convenience wrapper around validate_proper."""
    return validate_proper(dictionary).ok
