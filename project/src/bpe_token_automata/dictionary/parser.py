"""Dictionary file parsing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from bpe_token_automata.dictionary.encoding import decode_token_literal
from bpe_token_automata.dictionary.errors import (
    DictionaryIssue,
    IssueKind,
    ParseResult,
)
from bpe_token_automata.dictionary.model import Dictionary, MergeRule
from bpe_token_automata.tokens import Token

_MERGE_OPERATOR = "⫽"


def _split_rule_line(line: str) -> tuple[str, str] | None:
    if _MERGE_OPERATOR in line:
        left, right = line.split(_MERGE_OPERATOR, maxsplit=1)
        return left.strip(), right.strip()
    parts = line.split()
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


def _parse_rule_pair(
    left_text: str,
    right_text: str,
    *,
    line_number: int | None,
    rule_index: int,
    seen: set[tuple[Token, Token]],
    issues: list[DictionaryIssue],
) -> MergeRule | None:
    left, left_issue = decode_token_literal(left_text)
    if left_issue is not None:
        issues.append(
            DictionaryIssue(
                kind=left_issue.kind,
                message=f"left token: {left_issue.message}",
                line_number=line_number,
                rule_index=rule_index,
            )
        )
        return None

    right, right_issue = decode_token_literal(right_text)
    if right_issue is not None:
        issues.append(
            DictionaryIssue(
                kind=right_issue.kind,
                message=f"right token: {right_issue.message}",
                line_number=line_number,
                rule_index=rule_index,
            )
        )
        return None

    assert left is not None and right is not None
    key = (left, right)
    if key in seen:
        issues.append(
            DictionaryIssue(
                kind=IssueKind.DUPLICATE_RULE,
                message=f"duplicate rule {left_text!r} ⫽ {right_text!r}",
                line_number=line_number,
                rule_index=rule_index,
            )
        )
        return None

    seen.add(key)
    return MergeRule(left=left, right=right, index=rule_index)


def parse_merge_list(text: str) -> ParseResult:
    """Parse a line-oriented merge list (priority = line order)."""
    issues: list[DictionaryIssue] = []
    rules: list[MergeRule] = []
    seen: set[tuple[Token, Token]] = set()

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", maxsplit=1)[0].strip()
        if not line:
            continue

        split = _split_rule_line(line)
        if split is None:
            issues.append(
                DictionaryIssue(
                    kind=IssueKind.MALFORMED_LINE,
                    message=f"expected two tokens, got {line!r}",
                    line_number=line_number,
                    rule_index=len(rules),
                )
            )
            continue

        left_text, right_text = split
        rule = _parse_rule_pair(
            left_text,
            right_text,
            line_number=line_number,
            rule_index=len(rules),
            seen=seen,
            issues=issues,
        )
        if rule is not None:
            rules.append(rule)

    if issues:
        return ParseResult(dictionary=None, issues=tuple(issues))

    return ParseResult(dictionary=Dictionary(tuple(rules)), issues=())


def _parse_yaml_rules(
    data: Any,
) -> tuple[list[tuple[str, str]] | None, DictionaryIssue | None]:
    if not isinstance(data, dict):
        return None, DictionaryIssue(
            kind=IssueKind.YAML_STRUCTURE,
            message="dictionary YAML must be a mapping",
        )

    rules_data = data.get("rules")
    if not isinstance(rules_data, list):
        return None, DictionaryIssue(
            kind=IssueKind.YAML_STRUCTURE,
            message="dictionary YAML requires a list field 'rules'",
        )

    parsed: list[tuple[str, str]] = []
    for entry in rules_data:
        if not isinstance(entry, dict) or "left" not in entry or "right" not in entry:
            return None, DictionaryIssue(
                kind=IssueKind.YAML_STRUCTURE,
                message="each rule must be a mapping with 'left' and 'right'",
            )
        left = entry["left"]
        right = entry["right"]
        if not isinstance(left, str) or not isinstance(right, str):
            return None, DictionaryIssue(
                kind=IssueKind.YAML_STRUCTURE,
                message="rule tokens must be strings",
            )
        parsed.append((left, right))

    return parsed, None


def parse_yaml_dictionary(text: str) -> ParseResult:
    """Parse a YAML dictionary fixture."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return ParseResult(
            dictionary=None,
            issues=(
                DictionaryIssue(
                    kind=IssueKind.YAML_STRUCTURE,
                    message=f"invalid YAML: {exc}",
                ),
            ),
        )

    if data is None:
        return ParseResult(dictionary=Dictionary(()), issues=())

    rule_pairs, structure_issue = _parse_yaml_rules(data)
    if structure_issue is not None:
        return ParseResult(dictionary=None, issues=(structure_issue,))

    assert rule_pairs is not None
    issues: list[DictionaryIssue] = []
    rules: list[MergeRule] = []
    seen: set[tuple[Token, Token]] = set()

    for rule_index, (left_text, right_text) in enumerate(rule_pairs):
        rule = _parse_rule_pair(
            left_text,
            right_text,
            line_number=None,
            rule_index=rule_index,
            seen=seen,
            issues=issues,
        )
        if rule is not None:
            rules.append(rule)

    if issues:
        return ParseResult(dictionary=None, issues=tuple(issues))

    return ParseResult(dictionary=Dictionary(tuple(rules)), issues=())


def parse_dictionary_path(path: Path) -> ParseResult:
    """Parse a dictionary file, inferring format from suffix."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return parse_yaml_dictionary(text)
    return parse_merge_list(text)
