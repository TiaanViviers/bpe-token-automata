"""Béal–Carton finite-word determinisation ([3] §2.2, PDF pp. 233–234)."""

from __future__ import annotations

from collections import defaultdict

from bpe_token_automata.tokens import Token, TokenSequence
from bpe_token_automata.transducer.errors import TransducerError
from bpe_token_automata.transducer.model import (
    SubsequentialTransducer,
    Transducer,
    TransducerTransition,
    make_subsequential,
)

Pair = tuple[int, TokenSequence]
Subset = frozenset[Pair]


def longest_common_prefix(words: list[TokenSequence]) -> TokenSequence:
    """Longest common token-sequence prefix of `words` (non-empty)."""
    if not words:
        raise TransducerError("longest common prefix of an empty set")
    shortest = min(len(word) for word in words)
    index = 0
    while index < shortest and all(
        word.tokens[index] == words[0].tokens[index] for word in words
    ):
        index += 1
    return TokenSequence(words[0].tokens[:index])


def _remainder(word: TokenSequence, prefix: TokenSequence) -> TokenSequence:
    if word.tokens[: len(prefix)] != prefix.tokens:
        raise TransducerError("output word does not start with the emitted prefix")
    return TokenSequence(word.tokens[len(prefix) :])


def _max_output_length(transducer: Transducer) -> int:
    lengths = [len(output) for _, _, output, _ in transducer.transitions]
    return max(lengths, default=1)


def subsequentialise(
    transducer: Transducer,
    *,
    max_pending: int | None = None,
    max_states: int = 100_000,
) -> SubsequentialTransducer:
    """Construct an equivalent subsequential transducer (Béal–Carton §2.2)."""
    n_states = max(len(transducer.states), 1)
    bound = max_pending
    if bound is None:
        bound = 2 * n_states * n_states * max(_max_output_length(transducer), 1)

    outgoing: dict[tuple[int, Token], list[tuple[TokenSequence, int]]] = defaultdict(
        list
    )
    for src, symbol, output, dst in transducer.transitions:
        outgoing[(src, symbol)].append((output, dst))

    initial: Subset = frozenset({(transducer.initial, TokenSequence(()))})
    order: list[Subset] = [initial]
    ids: dict[Subset, int] = {initial: 0}
    transitions: list[TransducerTransition] = []
    input_symbols = tuple(sorted(transducer.input_alphabet))

    index = 0
    while index < len(order):
        current = order[index]
        src_id = ids[current]
        for symbol in input_symbols:
            collected: list[Pair] = []
            for state, delayed in current:
                for output, dest in outgoing.get((state, symbol), ()):
                    combined = TokenSequence(delayed.tokens + output.tokens)
                    if len(combined) > bound:
                        raise TransducerError(
                            "pending output exceeded the Béal–Carton length bound"
                        )
                    collected.append((dest, combined))
            if not collected:
                continue
            emitted = longest_common_prefix([word for _, word in collected])
            nxt: Subset = frozenset(
                (dest, _remainder(word, emitted)) for dest, word in collected
            )
            if nxt not in ids:
                if len(ids) >= max_states:
                    raise TransducerError(
                        "subsequential construction exceeded the state budget"
                    )
                ids[nxt] = len(order)
                order.append(nxt)
            transitions.append((src_id, symbol, emitted, ids[nxt]))
        index += 1

    final_output: dict[int, TokenSequence] = {}
    accepting = transducer.accepting
    for subset, subset_id in ids.items():
        delayed_accepting = [word for state, word in subset if state in accepting]
        if not delayed_accepting:
            continue
        unique = set(delayed_accepting)
        if len(unique) != 1:
            raise TransducerError(
                "accepting pairs in a determinised state have distinct delayed output"
            )
        final_output[subset_id] = delayed_accepting[0]

    return make_subsequential(
        states=frozenset(ids.values()),
        input_alphabet=transducer.input_alphabet,
        output_alphabet=transducer.output_alphabet,
        initial=0,
        final_output=final_output,
        transitions=transitions,
    )
