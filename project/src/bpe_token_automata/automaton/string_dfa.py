"""YAML loader for user-supplied string DFAs."""

from __future__ import annotations

from typing import Any

import yaml

from bpe_token_automata.automaton.construction import from_string_dfa
from bpe_token_automata.automaton.errors import TokenDFAError
from bpe_token_automata.automaton.model import TokenDFA
from bpe_token_automata.dictionary.encoding import decode_token_literal
from bpe_token_automata.tokens import Token


def parse_string_dfa_yaml(text: str) -> TokenDFA:
    """Parse a string DFA YAML fixture into a token DFA over length-1 tokens."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise TokenDFAError(f"invalid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise TokenDFAError("string DFA YAML must be a mapping")

    raw_states = data.get("states")
    if not isinstance(raw_states, list) or not raw_states:
        raise TokenDFAError("string DFA YAML requires a non-empty list 'states'")

    state_ids = {label: index for index, label in enumerate(raw_states)}
    if len(state_ids) != len(raw_states):
        raise TokenDFAError("duplicate state name in string DFA YAML")

    initial_label = data.get("initial")
    if initial_label not in state_ids:
        raise TokenDFAError("initial state is missing from 'states'")

    raw_accepting = data.get("accepting")
    if not isinstance(raw_accepting, list):
        raise TokenDFAError("string DFA YAML requires a list field 'accepting'")
    accepting: set[int] = set()
    for label in raw_accepting:
        if label not in state_ids:
            raise TokenDFAError(f"accepting state {label!r} is not in 'states'")
        accepting.add(state_ids[label])

    raw_transitions = data.get("transitions")
    if not isinstance(raw_transitions, list):
        raise TokenDFAError("string DFA YAML requires a list field 'transitions'")

    delta: dict[tuple[int, Token], int] = {}
    alphabet: set[Token] = set()
    for entry in raw_transitions:
        src, token, dst = _parse_transition(entry, state_ids)
        key = (src, token)
        if key in delta and delta[key] != dst:
            raise TokenDFAError(f"nondeterministic transition on {token!r}")
        delta[key] = dst
        alphabet.add(token)

    declared = data.get("alphabet")
    if declared is not None:
        if not isinstance(declared, list):
            raise TokenDFAError("optional 'alphabet' must be a list of symbols")
        for item in declared:
            token = _decode_symbol(item)
            alphabet.add(token)

    if not alphabet:
        raise TokenDFAError("string DFA has an empty alphabet")

    return from_string_dfa(
        states=frozenset(state_ids.values()),
        alphabet=frozenset(alphabet),
        initial=state_ids[initial_label],
        accepting=frozenset(accepting),
        delta=delta,
    )


def _parse_transition(
    entry: Any,
    state_ids: dict[Any, int],
) -> tuple[int, Token, int]:
    if not isinstance(entry, dict):
        raise TokenDFAError("each transition must be a mapping")
    if "from" not in entry or "to" not in entry or "symbol" not in entry:
        raise TokenDFAError("transition requires 'from', 'symbol', and 'to'")
    if entry["from"] not in state_ids or entry["to"] not in state_ids:
        raise TokenDFAError("transition refers to an unknown state")
    token = _decode_symbol(entry["symbol"])
    return state_ids[entry["from"]], token, state_ids[entry["to"]]


def _decode_symbol(literal: Any) -> Token:
    if not isinstance(literal, str):
        raise TokenDFAError("transition symbols must be strings")
    token, issue = decode_token_literal(literal)
    if issue is not None or token is None:
        message = issue.message if issue is not None else "invalid symbol"
        raise TokenDFAError(message)
    if len(token) != 1:
        raise TokenDFAError("string-DFA symbols must be length-1 tokens")
    return token
