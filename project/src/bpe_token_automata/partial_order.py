"""Bounded evidence for the restricted partial-order extension in section 8.6."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from bpe_token_automata.automaton import construct_token_dfa, universal_token_dfa
from bpe_token_automata.dictionary.model import Dictionary, MergeRule
from bpe_token_automata.dictionary.validator import validate_proper
from bpe_token_automata.dictionary_equivalence import compare_dictionaries_bounded
from bpe_token_automata.tokens import TokenSequence

MAX_LINEAR_EXTENSIONS = 24


@dataclass(frozen=True, slots=True)
class OrderedRules:
    """Rules identified by position, plus precedence constraints."""

    rules: tuple[MergeRule, ...]
    precedes: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True, slots=True)
class LinearExtensionResult:
    """Evidence for one partial order. The flags are independent on purpose."""

    disjoint_class: bool
    extensions: tuple[Dictionary, ...]
    extensions_agree: bool | None
    improper_extension: Dictionary | None
    compared_inputs: tuple[bytes, ...]
    counterexample_input: bytes | None
    left_extension: int | None
    right_extension: int | None
    left_tokens: TokenSequence | None
    right_tokens: TokenSequence | None
    dfa_agrees: bool | None
    dfa_witness: TokenSequence | None
    state_counts: tuple[int, ...] | None


def is_byte_disjoint_base(rules: Sequence[MergeRule]) -> bool:
    """Return whether nonempty rules form the restricted disjoint class."""
    if not rules:
        return False
    used: set[int] = set()
    for rule in rules:
        if len(rule.left) != 1 or len(rule.right) != 1:
            return False
        components = set(rule.left) | set(rule.right)
        if used & components:
            return False
        used.update(components)
    return True


def _precedence(order: OrderedRules) -> tuple[dict[int, set[int]], dict[int, int]]:
    n_rules = len(order.rules)
    successors: dict[int, set[int]] = {position: set() for position in range(n_rules)}
    indegree = {position: 0 for position in range(n_rules)}
    for earlier, later in order.precedes:
        if not 0 <= earlier < n_rules or not 0 <= later < n_rules:
            raise ValueError("precedence endpoint is outside the rule positions")
        if earlier == later:
            raise ValueError("precedence relation contains a self-loop")
        if later not in successors[earlier]:
            successors[earlier].add(later)
            indegree[later] += 1
    return successors, indegree


def _check_acyclic(successors: dict[int, set[int]], indegree: dict[int, int]) -> None:
    ready = sorted(position for position, degree in indegree.items() if degree == 0)
    remaining = dict(indegree)
    visited = 0
    while ready:
        position = ready.pop(0)
        visited += 1
        for successor in sorted(successors[position]):
            remaining[successor] -= 1
            if remaining[successor] == 0:
                ready.append(successor)
                ready.sort()
    if visited != len(indegree):
        raise ValueError("precedence relation contains a cycle")


def linear_extensions(order: OrderedRules) -> tuple[Dictionary, ...]:
    """Enumerate lexicographic linear extensions, re-indexed as dictionaries."""
    successors, indegree = _precedence(order)
    _check_acyclic(successors, indegree)

    extensions: list[tuple[int, ...]] = []
    n_rules = len(order.rules)

    def search(chosen: tuple[int, ...], remaining: dict[int, int]) -> None:
        if len(extensions) > MAX_LINEAR_EXTENSIONS:
            return
        if len(chosen) == n_rules:
            extensions.append(chosen)
            if len(extensions) > MAX_LINEAR_EXTENSIONS:
                raise ValueError(
                    f"number of linear extensions exceeds cap {MAX_LINEAR_EXTENSIONS}"
                )
            return
        for position in range(n_rules):
            if position in chosen or remaining[position] != 0:
                continue
            next_remaining = dict(remaining)
            for successor in successors[position]:
                next_remaining[successor] -= 1
            search(chosen + (position,), next_remaining)

    search((), indegree)
    return tuple(
        Dictionary(
            tuple(
                MergeRule(
                    left=order.rules[position].left,
                    right=order.rules[position].right,
                    index=index,
                )
                for index, position in enumerate(positions)
            )
        )
        for positions in extensions
    )


def _state_counts(extensions: tuple[Dictionary, ...]) -> tuple[int, ...]:
    values = {
        byte
        for dictionary in extensions
        for rule in dictionary.rules
        for component in (rule.left, rule.right)
        for byte in component
    }
    alphabet = frozenset(bytes((byte,)) for byte in values)
    return tuple(
        construct_token_dfa(dictionary, universal_token_dfa(alphabet)).final.n_states
        for dictionary in extensions
    )


def check_linear_extensions(
    order: OrderedRules,
    inputs: Iterable[bytes],
) -> LinearExtensionResult:
    """Enumerate and compare the bounded linear extensions of ``order``."""
    disjoint_class = is_byte_disjoint_base(order.rules)
    extensions = linear_extensions(order)

    for extension in extensions:
        if not validate_proper(extension).ok:
            return LinearExtensionResult(
                disjoint_class=disjoint_class,
                extensions=extensions,
                extensions_agree=None,
                improper_extension=extension,
                compared_inputs=(),
                counterexample_input=None,
                left_extension=None,
                right_extension=None,
                left_tokens=None,
                right_tokens=None,
                dfa_agrees=None,
                dfa_witness=None,
                state_counts=None,
            )

    checked = tuple(dict.fromkeys(inputs))
    if not checked:
        raise ValueError("linear-extension comparison requires at least one input")

    for index, extension in enumerate(extensions[1:], start=1):
        comparison = compare_dictionaries_bounded(
            extensions[0], extension, checked, check_token_dfa=True
        )
        if comparison.reference_agrees is not True or comparison.dfa_agrees is not True:
            return LinearExtensionResult(
                disjoint_class=disjoint_class,
                extensions=extensions,
                extensions_agree=False,
                improper_extension=None,
                compared_inputs=checked,
                counterexample_input=comparison.counterexample,
                left_extension=0,
                right_extension=index,
                left_tokens=comparison.left_tokens,
                right_tokens=comparison.right_tokens,
                dfa_agrees=comparison.dfa_agrees,
                dfa_witness=comparison.dfa_witness,
                state_counts=_state_counts(extensions),
            )

    return LinearExtensionResult(
        disjoint_class=disjoint_class,
        extensions=extensions,
        extensions_agree=True,
        improper_extension=None,
        compared_inputs=checked,
        counterexample_input=None,
        left_extension=None,
        right_extension=None,
        left_tokens=None,
        right_tokens=None,
        dfa_agrees=True,
        dfa_witness=None,
        state_counts=_state_counts(extensions),
    )


__all__ = [
    "MAX_LINEAR_EXTENSIONS",
    "LinearExtensionResult",
    "OrderedRules",
    "check_linear_extensions",
    "is_byte_disjoint_base",
    "linear_extensions",
]
