"""Bounded semantic comparison of proper BPE dictionaries."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass

from bpe_token_automata.automaton import (
    TokenDFA,
    construct_token_dfa,
    token_dfa_languages_agree,
    universal_token_dfa,
)
from bpe_token_automata.dictionary.errors import ImproperDictionaryError
from bpe_token_automata.dictionary.model import Dictionary
from bpe_token_automata.dictionary.validator import validate_proper
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.tokens import TokenSequence


@dataclass(frozen=True, slots=True)
class DictionaryEquivalenceResult:
    """Evidence collected for one bounded dictionary comparison."""

    equivalent: bool
    checked_inputs: tuple[bytes, ...]
    reference_agrees: bool | None
    dfa_agrees: bool | None
    counterexample: bytes | None
    left_tokens: TokenSequence | None
    right_tokens: TokenSequence | None
    dfa_witness: TokenSequence | None = None


def _comparison_alphabet(
    left: Dictionary, right: Dictionary, inputs: tuple[bytes, ...]
) -> frozenset[bytes]:
    values = set().union(*(set(text) for text in inputs))
    for dictionary in (left, right):
        for rule in dictionary.rules:
            values.update(rule.left)
            values.update(rule.right)
    if not values:
        values.add(0)
    return frozenset(bytes((value,)) for value in values)


def _dfa_witness(left_dfa: TokenDFA, right_dfa: TokenDFA) -> TokenSequence | None:
    """Return a shortest token-sequence accepted by exactly one DFA."""
    alphabet = tuple(sorted(left_dfa.alphabet | right_dfa.alphabet))
    start = (left_dfa.initial, right_dfa.initial)
    queue: deque[tuple[tuple[int | None, int | None], tuple[bytes, ...]]] = deque(
        [(start, ())]
    )
    seen: set[tuple[int | None, int | None]] = {start}

    def accepts(dfa: TokenDFA, state: int | None) -> bool:
        return state is not None and state in dfa.accepting

    def step(dfa: TokenDFA, state: int | None, token: bytes) -> int | None:
        if state is None:
            return None
        return dfa.step(state, token)

    while queue:
        (left_state, right_state), prefix = queue.popleft()
        if accepts(left_dfa, left_state) != accepts(right_dfa, right_state):
            return TokenSequence(prefix)
        for token in alphabet:
            next_pair = (
                step(left_dfa, left_state, token),
                step(right_dfa, right_state, token),
            )
            if next_pair == (None, None) or next_pair in seen:
                continue
            seen.add(next_pair)
            queue.append((next_pair, prefix + (token,)))
    return None


def compare_dictionaries_bounded(
    left: Dictionary,
    right: Dictionary,
    inputs: Iterable[bytes],
    *,
    check_token_dfa: bool = False,
) -> DictionaryEquivalenceResult:
    """Compare two dictionaries on a deterministic, explicitly bounded input set.

    The reference comparison is the primary result. When ``check_token_dfa``
    is enabled, both dictionaries are also compiled over the finite alphabet
    observed in the supplied inputs and rules, and their token languages are
    compared by product exploration. This is bounded evidence, not a general
    equivalence decision procedure.
    """
    for dictionary in (left, right):
        validation = validate_proper(dictionary)
        if not validation.ok:
            raise ImproperDictionaryError(validation.issues)

    checked_inputs = tuple(dict.fromkeys(inputs))
    first_counterexample: bytes | None = None
    left_tokens: TokenSequence | None = None
    right_tokens: TokenSequence | None = None

    for text in checked_inputs:
        candidate_left = tokenize_reference(left, text)
        candidate_right = tokenize_reference(right, text)
        if candidate_left != candidate_right:
            first_counterexample = text
            left_tokens = candidate_left
            right_tokens = candidate_right
            break

    reference_agrees: bool | None
    if checked_inputs:
        reference_agrees = first_counterexample is None
    else:
        reference_agrees = None

    dfa_agrees: bool | None = None
    dfa_witness: TokenSequence | None = None
    if check_token_dfa:
        alphabet = _comparison_alphabet(left, right, checked_inputs)
        left_dfa = construct_token_dfa(left, universal_token_dfa(alphabet)).final
        right_dfa = construct_token_dfa(right, universal_token_dfa(alphabet)).final
        dfa_agrees = token_dfa_languages_agree(left_dfa, right_dfa)
        if dfa_agrees is False:
            dfa_witness = _dfa_witness(left_dfa, right_dfa)

    equivalent = (
        bool(checked_inputs)
        and reference_agrees is not False
        and dfa_agrees is not False
    ) or (not checked_inputs and dfa_agrees is True)

    return DictionaryEquivalenceResult(
        equivalent=equivalent,
        checked_inputs=checked_inputs,
        reference_agrees=reference_agrees,
        dfa_agrees=dfa_agrees,
        counterexample=first_counterexample,
        left_tokens=left_tokens,
        right_tokens=right_tokens,
        dfa_witness=dfa_witness,
    )
