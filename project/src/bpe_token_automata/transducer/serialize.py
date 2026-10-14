"""Deterministic textual serialisation of transducers."""

from __future__ import annotations

from bpe_token_automata.tokens import (
    TokenSequence,
    format_token_label,
    format_token_sequence,
)
from bpe_token_automata.transducer.model import SubsequentialTransducer, Transducer

AnyTransducer = Transducer | SubsequentialTransducer


def _format_output(output: TokenSequence) -> str:
    if not output.tokens:
        return "ε"
    return format_token_sequence(output)


def serialize_transducer(transducer: AnyTransducer) -> str:
    """Return a deterministic text snapshot of a transducer."""
    states = ",".join(str(state) for state in sorted(transducer.states))
    accepting = ",".join(str(state) for state in sorted(transducer.accepting))
    alphabet = ",".join(
        format_token_label(symbol) for symbol in sorted(transducer.input_alphabet)
    )
    lines = [
        f"states: {states}",
        f"initial: {transducer.initial}",
        f"accepting: {accepting}",
        f"input_alphabet: {alphabet}",
        "final_outputs:",
    ]
    for state, output in transducer.final_output:
        lines.append(f"{state}: {_format_output(output)}")
    lines.append("transitions:")
    for src, symbol, output, dst in transducer.transitions:
        label = format_token_label(symbol)
        lines.append(f"{src} --{label}|{_format_output(output)}--> {dst}")
    return "\n".join(lines) + "\n"
