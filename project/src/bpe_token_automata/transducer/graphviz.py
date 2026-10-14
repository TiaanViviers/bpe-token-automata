"""Optional Graphviz DOT output for transducers."""

from __future__ import annotations

from bpe_token_automata.tokens import (
    TokenSequence,
    format_token_label,
    format_token_sequence,
)
from bpe_token_automata.transducer.serialize import AnyTransducer


def _format_output(output: TokenSequence) -> str:
    if not output.tokens:
        return "ε"
    return format_token_sequence(output)


def to_dot(transducer: AnyTransducer) -> str:
    """Return a Graphviz DOT representation of a transducer."""
    lines = [
        "digraph Transducer {",
        "  rankdir=LR;",
        "  node [shape=circle];",
        '  init [shape=point, label=""];',
        f"  init -> {transducer.initial};",
    ]
    finals = dict(transducer.final_output)
    for state in sorted(transducer.states):
        shape = "doublecircle" if state in finals else "circle"
        extra = ""
        if state in finals and finals[state].tokens:
            extra = f', xlabel="F={_format_output(finals[state])}"'
        lines.append(f"  {state} [shape={shape}{extra}];")

    for src, symbol, output, dst in transducer.transitions:
        label = f"{format_token_label(symbol)}|{_format_output(output)}"
        escaped = label.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'  {src} -> {dst} [label="{escaped}"];')

    lines.append("}")
    return "\n".join(lines) + "\n"
