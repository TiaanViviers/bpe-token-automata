"""Compile and run a subsequential string-to-tokenization transducer."""

from __future__ import annotations

from bpe_token_automata.automaton.construction import construct_token_dfa
from bpe_token_automata.automaton.model import TokenDFA
from bpe_token_automata.dictionary.model import Dictionary
from bpe_token_automata.tokens import TokenSequence
from bpe_token_automata.transducer.determinize import subsequentialise
from bpe_token_automata.transducer.errors import TokenizationError
from bpe_token_automata.transducer.model import SubsequentialTransducer
from bpe_token_automata.transducer.observation import from_token_dfa


def compile_tokenizer(
    dictionary: Dictionary,
    base: TokenDFA,
) -> SubsequentialTransducer:
    """Build the subsequential tokenizer for `dictionary` over `base`."""
    token_dfa = construct_token_dfa(dictionary, base).final
    return subsequentialise(from_token_dfa(token_dfa))


def tokenize(machine: SubsequentialTransducer, text: bytes) -> TokenSequence:
    """Map `text` to its canonical token sequence, or raise TokenizationError."""
    state = machine.initial
    emitted: list[bytes] = []
    for byte in text:
        stepped = machine.step(state, bytes((byte,)))
        if stepped is None:
            raise TokenizationError("no transducer transition for this input")
        output, state = stepped
        emitted.extend(output.tokens)
    final = machine.final_of(state)
    if final is None:
        raise TokenizationError("input ended in a non-accepting transducer state")
    emitted.extend(final.tokens)
    return TokenSequence(tuple(emitted))
