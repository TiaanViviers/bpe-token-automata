"""Dictionary package public API."""

from bpe_token_automata.dictionary.errors import (
    DictionaryError,
    DictionaryIssue,
    ImproperDictionaryError,
    IssueKind,
    ParseResult,
    ValidationResult,
)
from bpe_token_automata.dictionary.model import Dictionary, MergeRule
from bpe_token_automata.dictionary.parser import (
    parse_dictionary_path,
    parse_merge_list,
    parse_yaml_dictionary,
)
from bpe_token_automata.dictionary.validator import is_proper, validate_proper

__all__ = [
    "Dictionary",
    "DictionaryError",
    "DictionaryIssue",
    "ImproperDictionaryError",
    "IssueKind",
    "MergeRule",
    "ParseResult",
    "ValidationResult",
    "is_proper",
    "parse_dictionary_path",
    "parse_merge_list",
    "parse_yaml_dictionary",
    "validate_proper",
]
