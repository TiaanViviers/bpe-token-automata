"""BPE dictionary model."""

from __future__ import annotations

from dataclasses import dataclass

from bpe_token_automata.tokens import Token


@dataclass(frozen=True, slots=True)
class MergeRule:
    """One merge rule u ⫽ v with dictionary priority equal to its index."""

    left: Token
    right: Token
    index: int

    @property
    def merged(self) -> Token:
        """Token uv obtained by merging u and v."""
        return self.left + self.right


@dataclass(frozen=True, slots=True)
class Dictionary:
    """Ordered BPE dictionary D = [u1 ⫽ v1, ..., un ⫽ vn]."""

    rules: tuple[MergeRule, ...]

    def __len__(self) -> int:
        return len(self.rules)
