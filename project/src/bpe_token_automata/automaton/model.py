"""Token DFA model (Berglund, Martens and van der Merwe [5], Definition 1)."""

from __future__ import annotations

from dataclasses import dataclass, field

from bpe_token_automata.automaton.errors import TokenDFAError
from bpe_token_automata.tokens import Token, TokenSequence

Transition = tuple[int, Token, int]


def make_token_dfa(
    *,
    states: frozenset[int],
    alphabet: frozenset[Token],
    initial: int,
    accepting: frozenset[int],
    delta: dict[tuple[int, Token], int],
) -> TokenDFA:
    """Build a token DFA from a mutable transition map."""
    transitions = tuple(
        sorted((src, token, dst) for (src, token), dst in delta.items())
    )
    return TokenDFA(
        states=states,
        alphabet=alphabet,
        initial=initial,
        accepting=accepting,
        transitions=transitions,
    )


@dataclass(frozen=True, slots=True)
class TokenDFA:
    """A token DFA with a partial transition function."""

    states: frozenset[int]
    alphabet: frozenset[Token]
    initial: int
    accepting: frozenset[int]
    transitions: tuple[Transition, ...]
    _lookup: dict[tuple[int, Token], int] = field(
        init=False, repr=False, compare=False, hash=False
    )

    def __post_init__(self) -> None:
        lookup = {(src, token): dst for src, token, dst in self.transitions}
        if len(lookup) != len(self.transitions):
            raise TokenDFAError("duplicate transition")
        object.__setattr__(self, "_lookup", lookup)

        if self.initial not in self.states:
            raise TokenDFAError("initial state is not in the state set")
        if not self.accepting <= self.states:
            raise TokenDFAError("accepting state is not in the state set")
        for src, _token, dst in self.transitions:
            if src not in self.states or dst not in self.states:
                raise TokenDFAError("transition refers to an unknown state")

    @property
    def delta(self) -> dict[tuple[int, Token], int]:
        return dict(self._lookup)

    @property
    def n_states(self) -> int:
        return len(self.states)

    @property
    def n_final(self) -> int:
        return len(self.accepting)

    @property
    def n_tokens(self) -> int:
        return len(self.alphabet)

    @property
    def n_transitions(self) -> int:
        return len(self.transitions)

    def step(self, state: int, token: Token) -> int | None:
        """Return δ(state, token), or None if the transition is missing."""
        return self._lookup.get((state, token))

    def accepts(self, tokens: TokenSequence) -> bool:
        """True iff there is an accepting run on the token sequence."""
        state = self.initial
        for token in tokens:
            nxt = self.step(state, token)
            if nxt is None:
                return False
            state = nxt
        return state in self.accepting
