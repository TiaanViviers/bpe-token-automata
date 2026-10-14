"""Token and token-sequence types for byte-level BPE."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

Token = bytes
"""A BPE token: a byte sequence over the base alphabet."""


@dataclass(frozen=True, slots=True)
class TokenSequence:
    """An ordered canonical or intermediate tokenization."""

    tokens: tuple[Token, ...]

    def __iter__(self) -> Iterator[Token]:
        return iter(self.tokens)

    def __len__(self) -> int:
        return len(self.tokens)

    @classmethod
    def from_bytes(cls, data: bytes) -> TokenSequence:
        """Base tokenization T_empty(w): one token per byte."""
        return cls(tuple(bytes((byte,)) for byte in data))

    def detokenize(self) -> bytes:
        """Concatenate tokens (pi in Berglund & van der Merwe [6])."""
        return b"".join(self.tokens)


def detokenize(tokens: TokenSequence) -> bytes:
    """Return the string obtained by concatenating tokens."""
    return tokens.detokenize()


def format_token_label(token: Token) -> str:
    """Format a token: printable ASCII, otherwise \\xHH bytes."""
    if all(0x21 <= byte <= 0x7E and byte != ord("\\") for byte in token):
        return token.decode("ascii")
    return "".join(f"\\x{byte:02x}" for byte in token)


def format_token_sequence(sequence: TokenSequence, *, separator: str = "⫽") -> str:
    """Format tokens for tests and logging without requiring valid UTF-8."""
    return separator.join(format_token_label(token) for token in sequence.tokens)


def parse_token_sequence(text: str, *, separator: str = "⫽") -> TokenSequence:
    """Parse a separator-delimited token sequence from UTF-8 text."""
    if not text:
        return TokenSequence(())
    parts = text.split(separator)
    return TokenSequence(tuple(part.encode("utf-8") for part in parts))
