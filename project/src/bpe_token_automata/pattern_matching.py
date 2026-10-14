"""Pattern matching over canonical BPE token sequences."""

from __future__ import annotations

from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass

from bpe_token_automata.automaton.model import TokenDFA
from bpe_token_automata.tokens import Token, TokenSequence


@dataclass(frozen=True, slots=True)
class PatternMatch:
    """One half-open match interval in token or byte coordinates."""

    pattern_index: int
    start: int
    end: int


class TokenPatternMatcher:
    """Aho-Corasick matcher whose alphabet consists of complete BPE tokens."""

    def __init__(self, patterns: Sequence[TokenSequence]) -> None:
        if any(len(pattern) == 0 for pattern in patterns):
            raise ValueError("patterns must be non-empty")
        self.patterns = tuple(patterns)
        children: list[dict[Token, int]] = [{}]
        failures = [0]
        outputs: list[list[int]] = [[]]

        for pattern_index, pattern in enumerate(self.patterns):
            state = 0
            for token in pattern:
                next_state = children[state].get(token)
                if next_state is None:
                    next_state = len(children)
                    children[state][token] = next_state
                    children.append({})
                    failures.append(0)
                    outputs.append([])
                state = next_state
            outputs[state].append(pattern_index)

        queue: deque[int] = deque(children[0].values())
        while queue:
            state = queue.popleft()
            for token, next_state in children[state].items():
                queue.append(next_state)
                fallback = failures[state]
                while fallback and token not in children[fallback]:
                    fallback = failures[fallback]
                failures[next_state] = children[fallback].get(token, 0)
                outputs[next_state].extend(outputs[failures[next_state]])

        self._children = tuple(children)
        self._failures = tuple(failures)
        self._outputs = tuple(tuple(values) for values in outputs)

    def find(self, sequence: TokenSequence) -> tuple[PatternMatch, ...]:
        """Return all matches, including overlaps, in scan order."""
        state = 0
        matches: list[PatternMatch] = []
        for end, token in enumerate(sequence, start=1):
            while state and token not in self._children[state]:
                state = self._failures[state]
            state = self._children[state].get(token, 0)
            for pattern_index in self._outputs[state]:
                start = end - len(self.patterns[pattern_index])
                matches.append(PatternMatch(pattern_index, start, end))
        return tuple(
            sorted(matches, key=lambda match: (match.end, match.pattern_index))
        )

    def find_canonical(
        self, sequence: TokenSequence, token_dfa: TokenDFA
    ) -> tuple[PatternMatch, ...]:
        """Find matches only when the complete sequence and each match span
        are canonical.

        The token DFA validates both the full sequence and each matched token
        span before Aho-Corasick reports the match, so pattern processing
        cannot silently operate on a non-canonical segmentation.
        """
        if not token_dfa.accepts(sequence):
            raise ValueError("sequence is not accepted by the token DFA")
        matches = self.find(sequence)
        for match in matches:
            span = TokenSequence(sequence.tokens[match.start : match.end])
            if not token_dfa.accepts(span):
                raise ValueError(
                    f"matched span {span!r} is not accepted by the token DFA"
                )
        return matches


def match_bytes(data: bytes, patterns: Sequence[bytes]) -> tuple[PatternMatch, ...]:
    """Match byte patterns after detokenization, preserving byte coordinates."""
    if any(not pattern for pattern in patterns):
        raise ValueError("patterns must be non-empty")
    matches: list[PatternMatch] = []
    for pattern_index, pattern in enumerate(patterns):
        start = data.find(pattern)
        while start >= 0:
            matches.append(PatternMatch(pattern_index, start, start + len(pattern)))
            start = data.find(pattern, start + 1)
    return tuple(sorted(matches, key=lambda match: (match.end, match.pattern_index)))
