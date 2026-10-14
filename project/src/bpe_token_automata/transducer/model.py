"""Transducer models ([5] Definition 6; Béal–Carton output words on edges)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from bpe_token_automata.tokens import Token, TokenSequence
from bpe_token_automata.transducer.errors import TransducerError

TransducerTransition = tuple[int, Token, TokenSequence, int]
FinalOutput = tuple[int, TokenSequence]


def _final_lookup(
    final_output: tuple[FinalOutput, ...],
) -> dict[int, TokenSequence]:
    lookup = dict(final_output)
    if len(lookup) != len(final_output):
        raise TransducerError("duplicate final-output entry")
    return lookup


@dataclass(frozen=True, slots=True)
class Transducer:
    """A real-time transducer; the input automaton need not be deterministic."""

    states: frozenset[int]
    input_alphabet: frozenset[Token]
    output_alphabet: frozenset[Token]
    initial: int
    final_output: tuple[FinalOutput, ...]
    transitions: tuple[TransducerTransition, ...]
    _successors: dict[tuple[int, Token], tuple[tuple[TokenSequence, int], ...]] = field(
        init=False, repr=False, compare=False, hash=False
    )
    _final: dict[int, TokenSequence] = field(
        init=False, repr=False, compare=False, hash=False
    )

    def __post_init__(self) -> None:
        final = _final_lookup(self.final_output)
        object.__setattr__(self, "_final", final)

        if self.initial not in self.states:
            raise TransducerError("initial state is not in the state set")
        if not frozenset(final) <= self.states:
            raise TransducerError("final-output state is not in the state set")
        for symbol in self.input_alphabet:
            if len(symbol) != 1:
                raise TransducerError("input symbols must be length-1 tokens")

        grouped: dict[tuple[int, Token], list[tuple[TokenSequence, int]]] = defaultdict(
            list
        )
        for src, symbol, output, dst in self.transitions:
            if src not in self.states or dst not in self.states:
                raise TransducerError("transition refers to an unknown state")
            if symbol not in self.input_alphabet:
                raise TransducerError("transition input is not in the input alphabet")
            grouped[(src, symbol)].append((output, dst))
        object.__setattr__(
            self,
            "_successors",
            {key: tuple(values) for key, values in grouped.items()},
        )

    @property
    def accepting(self) -> frozenset[int]:
        return frozenset(self._final)

    def successors(
        self, state: int, symbol: Token
    ) -> tuple[tuple[TokenSequence, int], ...]:
        """Return every (output, destination) pair on this input."""
        return self._successors.get((state, symbol), ())

    def final_of(self, state: int) -> TokenSequence | None:
        """Return F(state), or None if the state is not accepting."""
        return self._final.get(state)

    def is_subsequential(self) -> bool:
        """True iff each (state, input) has at most one successor."""
        return all(len(options) <= 1 for options in self._successors.values())


@dataclass(frozen=True, slots=True)
class SubsequentialTransducer:
    """Input-deterministic transducer with a partial final-output function."""

    states: frozenset[int]
    input_alphabet: frozenset[Token]
    output_alphabet: frozenset[Token]
    initial: int
    final_output: tuple[FinalOutput, ...]
    transitions: tuple[TransducerTransition, ...]
    _delta: dict[tuple[int, Token], tuple[TokenSequence, int]] = field(
        init=False, repr=False, compare=False, hash=False
    )
    _final: dict[int, TokenSequence] = field(
        init=False, repr=False, compare=False, hash=False
    )

    def __post_init__(self) -> None:
        final = _final_lookup(self.final_output)
        object.__setattr__(self, "_final", final)

        if self.initial not in self.states:
            raise TransducerError("initial state is not in the state set")
        if not frozenset(final) <= self.states:
            raise TransducerError("final-output state is not in the state set")
        for symbol in self.input_alphabet:
            if len(symbol) != 1:
                raise TransducerError("input symbols must be length-1 tokens")

        delta: dict[tuple[int, Token], tuple[TokenSequence, int]] = {}
        for src, symbol, output, dst in self.transitions:
            if src not in self.states or dst not in self.states:
                raise TransducerError("transition refers to an unknown state")
            if symbol not in self.input_alphabet:
                raise TransducerError("transition input is not in the input alphabet")
            key = (src, symbol)
            if key in delta:
                raise TransducerError("input-nondeterministic subsequential transducer")
            delta[key] = (output, dst)
        object.__setattr__(self, "_delta", delta)

    @property
    def accepting(self) -> frozenset[int]:
        return frozenset(self._final)

    def step(self, state: int, symbol: Token) -> tuple[TokenSequence, int] | None:
        """Return (output, destination), or None if the transition is missing."""
        return self._delta.get((state, symbol))

    def final_of(self, state: int) -> TokenSequence | None:
        """Return F(state), or None if the state is not accepting."""
        return self._final.get(state)


def make_transducer(
    *,
    states: frozenset[int],
    input_alphabet: frozenset[Token],
    output_alphabet: frozenset[Token],
    initial: int,
    final_output: dict[int, TokenSequence],
    transitions: list[TransducerTransition],
) -> Transducer:
    """Build a transducer from mutable maps."""
    return Transducer(
        states=states,
        input_alphabet=input_alphabet,
        output_alphabet=output_alphabet,
        initial=initial,
        final_output=tuple(sorted(final_output.items(), key=lambda item: item[0])),
        transitions=tuple(
            sorted(
                transitions,
                key=lambda item: (item[0], item[1], item[3], item[2].tokens),
            )
        ),
    )


def make_subsequential(
    *,
    states: frozenset[int],
    input_alphabet: frozenset[Token],
    output_alphabet: frozenset[Token],
    initial: int,
    final_output: dict[int, TokenSequence],
    transitions: list[TransducerTransition],
) -> SubsequentialTransducer:
    """Build an input-deterministic transducer from mutable maps."""
    return SubsequentialTransducer(
        states=states,
        input_alphabet=input_alphabet,
        output_alphabet=output_alphabet,
        initial=initial,
        final_output=tuple(sorted(final_output.items(), key=lambda item: item[0])),
        transitions=tuple(
            sorted(
                transitions,
                key=lambda item: (item[0], item[1], item[3], item[2].tokens),
            )
        ),
    )
