"""Successive-merge token-DFA construction (Algorithm 2 of [5])."""

from __future__ import annotations

from dataclasses import dataclass

from bpe_token_automata.automaton.errors import TokenDFAError
from bpe_token_automata.automaton.model import TokenDFA, Transition, make_token_dfa
from bpe_token_automata.dictionary.errors import ImproperDictionaryError
from bpe_token_automata.dictionary.model import Dictionary, MergeRule
from bpe_token_automata.dictionary.validator import validate_proper
from bpe_token_automata.tokens import Token

StateTriple = tuple[int, int, int]
FreshMap = tuple[tuple[int, int], ...]
Redirect = tuple[int, Token, int, int]


@dataclass(frozen=True, slots=True)
class MergeTrace:
    """Algorithm 2 bookkeeping for one merge, recorded for Section 5.3."""

    rule: MergeRule
    before: TokenDFA
    after: TokenDFA
    triples: tuple[StateTriple, ...]
    s2_to_fresh: FreshMap
    added_uv: tuple[Transition, ...]
    inherited: tuple[Transition, ...]
    omitted_labels: frozenset[Token]
    redirected: tuple[Redirect, ...]

    @property
    def n_fresh(self) -> int:
        return len(self.s2_to_fresh)


def byte_alphabet() -> frozenset[Token]:
    """Base alphabet of all single-byte tokens (D5)."""
    return frozenset(bytes((value,)) for value in range(256))


def universal_token_dfa(alphabet: frozenset[Token]) -> TokenDFA:
    """One-state token DFA accepting every tokenization over `alphabet`."""
    if not alphabet:
        raise TokenDFAError("universal DFA requires a non-empty alphabet")
    for token in alphabet:
        if len(token) != 1:
            raise TokenDFAError("base alphabet tokens must have length 1")

    delta = {(0, token): 0 for token in alphabet}
    return make_token_dfa(
        states=frozenset({0}),
        alphabet=alphabet,
        initial=0,
        accepting=frozenset({0}),
        delta=delta,
    )


def from_string_dfa(
    *,
    states: frozenset[int],
    alphabet: frozenset[Token],
    initial: int,
    accepting: frozenset[int],
    delta: dict[tuple[int, Token], int],
) -> TokenDFA:
    """Lift a string DFA to a token DFA (each symbol becomes a length-1 token)."""
    for token in alphabet:
        if len(token) != 1:
            raise TokenDFAError("string-DFA symbols must be length-1 tokens")
    for (_src, token), _dst in delta.items():
        if token not in alphabet:
            raise TokenDFAError(f"transition token {token!r} is not in the alphabet")
    return make_token_dfa(
        states=states,
        alphabet=alphabet,
        initial=initial,
        accepting=accepting,
        delta=delta,
    )


def apply_merge(dfa: TokenDFA, rule: MergeRule) -> tuple[TokenDFA, MergeTrace]:
    """Apply Algorithm 2 of [5] with rule u ⫽ v. Returns (A', merge trace)."""
    u = rule.left
    v = rule.right
    uv = rule.merged

    # Lines 2–3: triples where δ(s1, u) = s2 and δ(s2, v) = s3.
    triples: list[StateTriple] = []
    for s1 in sorted(dfa.states):
        s2 = dfa.step(s1, u)
        if s2 is None:
            continue
        s3 = dfa.step(s2, v)
        if s3 is None:
            continue
        triples.append((s1, s2, s3))

    s2_set = {s2 for _s1, s2, _s3 in triples}

    delta = dict(dfa.delta)
    states = set(dfa.states)
    accepting = set(dfa.accepting)
    alphabet = set(dfa.alphabet)

    # Lines 4–6: add δ(s1, uv) = s3.
    added_uv: list[Transition] = []
    for s1, _s2, s3 in triples:
        existing = delta.get((s1, uv))
        if existing is not None and existing != s3:
            raise TokenDFAError(
                f"conflicting transition on {uv!r} from state {s1}: {existing} vs {s3}"
            )
        delta[(s1, uv)] = s3
        added_uv.append((s1, uv, s3))

    # Line 7: add uv to Γ even when S is empty.
    alphabet.add(uv)

    # Lines 8–11: one fresh state per distinct s2, inheriting accepting status.
    next_id = (max(states) + 1) if states else 0
    fresh: dict[int, int] = {}
    for s2 in sorted(s2_set):
        fresh_id = next_id
        next_id += 1
        fresh[s2] = fresh_id
        states.add(fresh_id)
        if s2 in accepting:
            accepting.add(fresh_id)

    # Lines 12–18: copy outgoing transitions except v, and except uv when u = v.
    omitted_labels = frozenset({v, uv} if u == v else {v})
    inherited: list[Transition] = []
    for s2 in sorted(s2_set):
        fresh_id = fresh[s2]
        for token in sorted(alphabet):
            if token in omitted_labels:
                continue
            target = delta.get((s2, token))
            if target is not None:
                delta[(fresh_id, token)] = target
                inherited.append((fresh_id, token, target))

    # Lines 19–21: redirect every current u-edge into S2, including fresh states.
    redirected: list[Redirect] = []
    for state in sorted(states):
        target = delta.get((state, u))
        if target in s2_set:
            new_target = fresh[target]
            delta[(state, u)] = new_target
            redirected.append((state, u, target, new_target))

    result = make_token_dfa(
        states=frozenset(states),
        alphabet=frozenset(alphabet),
        initial=dfa.initial,
        accepting=frozenset(accepting),
        delta=delta,
    )
    trace = MergeTrace(
        rule=rule,
        before=dfa,
        after=result,
        triples=tuple(triples),
        s2_to_fresh=tuple((s2, fresh[s2]) for s2 in sorted(s2_set)),
        added_uv=tuple(added_uv),
        inherited=tuple(inherited),
        omitted_labels=omitted_labels,
        redirected=tuple(redirected),
    )
    return result, trace


@dataclass(frozen=True, slots=True)
class ConstructionStep:
    """Sizes of A_i after merging rule i (0-based)."""

    rule_index: int
    n_states: int
    n_final: int
    n_tokens: int
    n_transitions: int
    n_fresh: int


@dataclass(frozen=True, slots=True)
class ConstructionResult:
    """A_n together with the intermediate automata, traces, and per-rule counts."""

    final: TokenDFA
    automata: tuple[TokenDFA, ...]
    steps: tuple[ConstructionStep, ...]
    traces: tuple[MergeTrace, ...]


def construct_token_dfa(
    dictionary: Dictionary,
    base: TokenDFA,
) -> ConstructionResult:
    """Build A_0, …, A_n by applying each dictionary rule in priority order."""
    validation = validate_proper(dictionary)
    if not validation.ok:
        raise ImproperDictionaryError(validation.issues)

    automata = [base]
    steps: list[ConstructionStep] = []
    traces: list[MergeTrace] = []
    current = base
    for rule in dictionary.rules:
        current, trace = apply_merge(current, rule)
        automata.append(current)
        traces.append(trace)
        steps.append(
            ConstructionStep(
                rule_index=rule.index,
                n_states=current.n_states,
                n_final=current.n_final,
                n_tokens=current.n_tokens,
                n_transitions=current.n_transitions,
                n_fresh=trace.n_fresh,
            )
        )

    return ConstructionResult(
        final=current,
        automata=tuple(automata),
        steps=tuple(steps),
        traces=tuple(traces),
    )
