"""Deterministic textual serialisation of token DFAs."""

from __future__ import annotations

from bpe_token_automata.automaton.model import TokenDFA
from bpe_token_automata.tokens import format_token_label

__all__ = ["format_token_label", "serialize_token_dfa"]


def serialize_token_dfa(dfa: TokenDFA) -> str:
    """Return a deterministic text snapshot of a token DFA."""
    states = ",".join(str(state) for state in sorted(dfa.states))
    accepting = ",".join(str(state) for state in sorted(dfa.accepting))
    alphabet = ",".join(format_token_label(token) for token in sorted(dfa.alphabet))
    lines = [
        f"states: {states}",
        f"initial: {dfa.initial}",
        f"accepting: {accepting}",
        f"alphabet: {alphabet}",
        "transitions:",
    ]
    for src, token in sorted(dfa.delta, key=lambda item: (item[0], item[1])):
        dst = dfa.delta[(src, token)]
        lines.append(f"{src} --{format_token_label(token)}--> {dst}")
    return "\n".join(lines) + "\n"
