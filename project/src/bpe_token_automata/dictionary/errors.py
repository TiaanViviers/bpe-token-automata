"""Structured errors for dictionary parsing and validation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from bpe_token_automata.dictionary.model import Dictionary


class IssueKind(StrEnum):
    """Categories of dictionary problems."""

    MALFORMED_LINE = "malformed_line"
    EMPTY_TOKEN = "empty_token"
    DUPLICATE_RULE = "duplicate_rule"
    UNSUPPORTED_ENCODING = "unsupported_encoding"
    IMPROPER_RULE = "improper_rule"
    YAML_STRUCTURE = "yaml_structure"


@dataclass(frozen=True, slots=True)
class DictionaryIssue:
    """One parse or validation problem."""

    kind: IssueKind
    message: str
    line_number: int | None = None
    rule_index: int | None = None


@dataclass(frozen=True, slots=True)
class ParseResult:
    """Outcome of parsing a dictionary file."""

    dictionary: Dictionary | None
    issues: tuple[DictionaryIssue, ...]

    @property
    def ok(self) -> bool:
        return self.dictionary is not None and not self.issues


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Outcome of proper-dictionary validation."""

    issues: tuple[DictionaryIssue, ...]

    @property
    def ok(self) -> bool:
        return not self.issues


class DictionaryError(Exception):
    """Base class for dictionary failures."""


class ImproperDictionaryError(DictionaryError):
    """Raised when tokenization is requested on an improper dictionary."""

    def __init__(self, issues: tuple[DictionaryIssue, ...]) -> None:
        self.issues = issues
        summary = "; ".join(issue.message for issue in issues)
        super().__init__(summary)
