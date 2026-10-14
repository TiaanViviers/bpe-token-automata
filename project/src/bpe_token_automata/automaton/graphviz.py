"""Optional Graphviz DOT output for token DFAs."""

from __future__ import annotations

from bpe_token_automata.automaton.model import TokenDFA
from bpe_token_automata.automaton.serialize import format_token_label


def to_dot(dfa: TokenDFA) -> str:
    """Return a Graphviz DOT representation of a token DFA."""
    lines = [
        "digraph TokenDFA {",
        "  rankdir=LR;",
        "  node [shape=circle];",
        '  init [shape=point, label=""];',
        f"  init -> {dfa.initial};",
    ]
    for state in sorted(dfa.states):
        shape = "doublecircle" if state in dfa.accepting else "circle"
        lines.append(f"  {state} [shape={shape}];")

    grouped: dict[tuple[int, int], list[str]] = {}
    for src, token in sorted(dfa.delta, key=lambda item: (item[0], item[1])):
        dst = dfa.delta[(src, token)]
        grouped.setdefault((src, dst), []).append(format_token_label(token))

    for (src, dst), labels in sorted(grouped.items()):
        joined = ",".join(labels)
        escaped = joined.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'  {src} -> {dst} [label="{escaped}"];')

    lines.append("}")
    return "\n".join(lines) + "\n"
