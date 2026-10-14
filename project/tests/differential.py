"""Shared §6.2–6.3 checks: oracle differential and composition uniqueness."""

from __future__ import annotations

from collections.abc import Iterator

from bpe_token_automata.automaton import (
    TokenDFA,
    construct_token_dfa,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import Dictionary
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.tokens import TokenSequence
from bpe_token_automata.transducer import (
    SubsequentialTransducer,
    compile_tokenizer,
    tokenize,
)


def compositions(text: bytes) -> Iterator[TokenSequence]:
    """Yield every split of ``text`` into non-empty contiguous byte pieces.

    The empty string has one composition (the empty sequence). A string of
    length ``n >= 1`` has ``2 ** (n - 1)`` compositions.
    """
    if not text:
        yield TokenSequence(())
        return

    n = len(text)

    def rec(start: int, parts: list[bytes]) -> Iterator[TokenSequence]:
        if start == n:
            yield TokenSequence(tuple(parts))
            return
        for end in range(start + 1, n + 1):
            parts.append(text[start:end])
            yield from rec(end, parts)
            parts.pop()

    yield from rec(0, [])


def split_first_long_token(sequence: TokenSequence) -> TokenSequence | None:
    """Split the first token of length > 1 into a one-byte prefix and the rest."""
    tokens = list(sequence.tokens)
    for index, token in enumerate(tokens):
        if len(token) > 1:
            tokens[index : index + 1] = [token[:1], token[1:]]
            return TokenSequence(tuple(tokens))
    return None


def assert_section_62(
    dictionary: Dictionary,
    alphabet: frozenset[bytes],
    text: bytes,
    *,
    dfa: TokenDFA | None = None,
    machine: SubsequentialTransducer | None = None,
) -> TokenSequence:
    """Compare transducer output with ``T^D(w)`` on the five §6.2 checks."""
    if dfa is None or machine is None:
        base = universal_token_dfa(alphabet)
        if dfa is None:
            dfa = construct_token_dfa(dictionary, base).final
        if machine is None:
            machine = compile_tokenizer(dictionary, base)
    output = tokenize(machine, text)
    expected = tokenize_reference(dictionary, text)
    assert output == expected
    assert all(token in dfa.alphabet for token in output)
    assert output.detokenize() == text
    assert dfa.accepts(output)
    altered = split_first_long_token(output)
    if altered is not None and altered != output:
        assert not dfa.accepts(altered)
    return output


def assert_unique_tokenization(
    dfa: TokenDFA,
    dictionary: Dictionary,
    text: bytes,
    canonical: TokenSequence | None = None,
) -> None:
    """Exactly one composition of ``text`` is accepted, and it equals ``T^D``."""
    if canonical is None:
        canonical = tokenize_reference(dictionary, text)
    accepted = [sequence for sequence in compositions(text) if dfa.accepts(sequence)]
    assert accepted == [canonical]
