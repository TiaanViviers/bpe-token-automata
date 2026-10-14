"""Token-DFA public API."""

from bpe_token_automata.automaton.compact import (
    CompactOptions,
    CompactResult,
    CompactStep,
    DelayedInputDFA,
    apply_compact_merge,
    construct_compact_token_dfa,
    expand_defaults,
    languages_agree,
    lift_to_delayed,
    serialize_delayed_input_dfa,
    token_dfa_languages_agree,
)
from bpe_token_automata.automaton.construction import (
    ConstructionResult,
    ConstructionStep,
    MergeTrace,
    apply_merge,
    byte_alphabet,
    construct_token_dfa,
    from_string_dfa,
    universal_token_dfa,
)
from bpe_token_automata.automaton.errors import TokenDFAError
from bpe_token_automata.automaton.graphviz import to_dot
from bpe_token_automata.automaton.model import TokenDFA
from bpe_token_automata.automaton.serialize import (
    format_token_label,
    serialize_token_dfa,
)
from bpe_token_automata.automaton.string_dfa import parse_string_dfa_yaml

__all__ = [
    "CompactOptions",
    "CompactResult",
    "CompactStep",
    "ConstructionResult",
    "ConstructionStep",
    "DelayedInputDFA",
    "MergeTrace",
    "TokenDFA",
    "TokenDFAError",
    "apply_compact_merge",
    "apply_merge",
    "byte_alphabet",
    "construct_compact_token_dfa",
    "construct_token_dfa",
    "expand_defaults",
    "format_token_label",
    "from_string_dfa",
    "languages_agree",
    "lift_to_delayed",
    "token_dfa_languages_agree",
    "parse_string_dfa_yaml",
    "serialize_delayed_input_dfa",
    "serialize_token_dfa",
    "to_dot",
    "universal_token_dfa",
]
