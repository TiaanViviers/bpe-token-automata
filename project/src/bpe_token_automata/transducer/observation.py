"""Observation 3 of Berglund, Martens and van der Merwe [5] (PDF p. 10)."""

from __future__ import annotations

from bpe_token_automata.automaton.model import TokenDFA
from bpe_token_automata.tokens import Token, TokenSequence
from bpe_token_automata.transducer.errors import TransducerError
from bpe_token_automata.transducer.model import (
    Transducer,
    TransducerTransition,
    make_transducer,
)


def _spell(token: Token) -> tuple[Token, ...]:
    if not token:
        raise TransducerError("cannot spell an empty token")
    return tuple(bytes((byte,)) for byte in token)


def from_token_dfa(dfa: TokenDFA) -> Transducer:
    """Replace each token-edge by a byte spelling that emits the token at the end."""
    states = set(dfa.states)
    next_id = (max(states) + 1) if states else 0
    transitions: list[TransducerTransition] = []
    input_alphabet: set[Token] = set()

    for src, token, dst in dfa.transitions:
        symbols = _spell(token)
        input_alphabet.update(symbols)
        if len(symbols) == 1:
            transitions.append((src, symbols[0], TokenSequence((token,)), dst))
            continue
        prev = src
        for symbol in symbols[:-1]:
            spelling = next_id
            next_id += 1
            states.add(spelling)
            transitions.append((prev, symbol, TokenSequence(()), spelling))
            prev = spelling
        transitions.append((prev, symbols[-1], TokenSequence((token,)), dst))

    final_output = {state: TokenSequence(()) for state in dfa.accepting}
    return make_transducer(
        states=frozenset(states),
        input_alphabet=frozenset(input_alphabet),
        output_alphabet=dfa.alphabet,
        initial=dfa.initial,
        final_output=final_output,
        transitions=transitions,
    )
