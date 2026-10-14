"""Compact delayed-input token DFA (Algorithm 2 of Berglund et al. [4])."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from bpe_token_automata.automaton.errors import TokenDFAError
from bpe_token_automata.automaton.model import TokenDFA, Transition, make_token_dfa
from bpe_token_automata.dictionary.errors import ImproperDictionaryError
from bpe_token_automata.dictionary.model import Dictionary, MergeRule
from bpe_token_automata.dictionary.validator import validate_proper
from bpe_token_automata.tokens import Token, TokenSequence, format_token_label

StateTriple = tuple[int, int, int]


def _delta_nu(
    lookup: dict[tuple[int, Token], int],
    defaults: dict[int, int],
    sink: int,
    state: int,
    token: Token,
) -> int | None:
    """Extended transition δ^ν. May return the sink. None means ⊥."""
    seen: set[int] = set()
    current = state
    while True:
        if current == sink:
            return sink
        if current in seen:
            raise TokenDFAError("cyclic default transition")
        explicit = lookup.get((current, token))
        if explicit is not None:
            return explicit
        nxt = defaults.get(current)
        if nxt is None:
            return None
        seen.add(current)
        current = nxt


def _has_default_cycle(defaults: dict[int, int]) -> bool:
    visiting: set[int] = set()
    done: set[int] = set()

    def visit(node: int) -> bool:
        if node in done:
            return False
        if node in visiting:
            return True
        visiting.add(node)
        nxt = defaults.get(node)
        if nxt is not None and visit(nxt):
            return True
        visiting.remove(node)
        done.add(node)
        return False

    return any(visit(node) for node in defaults)


@dataclass(frozen=True, slots=True)
class CompactOptions:
    """Optimisation flags for Algorithm 2. O1 is always enabled."""

    o2_state_avoidance: bool = True
    o3_clean_copy: bool = True


@dataclass(frozen=True, slots=True)
class DelayedInputDFA:
    """A D²FA with partial δ, partial acyclic ν, and distinguished sink (Def. 2)."""

    states: frozenset[int]
    alphabet: frozenset[Token]
    initial: int
    accepting: frozenset[int]
    transitions: tuple[Transition, ...]
    defaults: tuple[tuple[int, int], ...]
    sink: int
    _lookup: dict[tuple[int, Token], int] = field(
        init=False, repr=False, compare=False, hash=False
    )
    _defaults: dict[int, int] = field(init=False, repr=False, compare=False, hash=False)

    def __post_init__(self) -> None:
        lookup = {(src, token): dst for src, token, dst in self.transitions}
        if len(lookup) != len(self.transitions):
            raise TokenDFAError("duplicate transition")
        default_map = dict(self.defaults)
        if len(default_map) != len(self.defaults):
            raise TokenDFAError("duplicate default transition")
        object.__setattr__(self, "_lookup", lookup)
        object.__setattr__(self, "_defaults", default_map)

        if self.sink not in self.states:
            raise TokenDFAError("sink is not in the state set")
        if self.sink in self.accepting:
            raise TokenDFAError("sink must not be accepting")
        if self.initial not in self.states or self.initial == self.sink:
            raise TokenDFAError("initial state is not a non-sink state")
        if not self.accepting <= self.states:
            raise TokenDFAError("accepting state is not in the state set")
        if self.sink in default_map:
            raise TokenDFAError("sink must not have a default transition")
        for src, token, dst in self.transitions:
            if src not in self.states or dst not in self.states:
                raise TokenDFAError("transition refers to an unknown state")
            if src == self.sink:
                raise TokenDFAError("sink must not have outgoing transitions")
            if token not in self.alphabet:
                raise TokenDFAError("transition token is not in the alphabet")
        for src, dst in self.defaults:
            if src not in self.states or dst not in self.states:
                raise TokenDFAError("default refers to an unknown state")
            if src == self.sink or dst == self.sink:
                raise TokenDFAError("default must not involve the sink")
        if _has_default_cycle(default_map):
            raise TokenDFAError("cyclic default transition")

    @property
    def n_states_excluding_sink(self) -> int:
        return len(self.states) - 1

    @property
    def n_final(self) -> int:
        return len(self.accepting)

    @property
    def n_tokens(self) -> int:
        return len(self.alphabet)

    @property
    def n_transitions(self) -> int:
        return len(self.transitions)

    @property
    def n_defaults(self) -> int:
        return len(self.defaults)

    def explicit_step(self, state: int, token: Token) -> int | None:
        """Return δ(state, token), or None if missing (may be the sink)."""
        return self._lookup.get((state, token))

    def step(self, state: int, token: Token) -> int | None:
        """Return δ^ν(state, token), or None if missing or the sink."""
        result = _delta_nu(self._lookup, self._defaults, self.sink, state, token)
        if result is None or result == self.sink:
            return None
        return result

    def accepts(self, tokens: TokenSequence) -> bool:
        """True iff there is an accepting run on the token sequence via δ^ν."""
        state = self.initial
        for token in tokens:
            nxt = self.step(state, token)
            if nxt is None:
                return False
            state = nxt
        return state in self.accepting


def _make_delayed(
    *,
    states: frozenset[int],
    alphabet: frozenset[Token],
    initial: int,
    accepting: frozenset[int],
    delta: dict[tuple[int, Token], int],
    defaults: dict[int, int],
    sink: int,
) -> DelayedInputDFA:
    transitions = tuple(
        sorted((src, token, dst) for (src, token), dst in delta.items())
    )
    default_pairs = tuple(sorted(defaults.items()))
    return DelayedInputDFA(
        states=states,
        alphabet=alphabet,
        initial=initial,
        accepting=accepting,
        transitions=transitions,
        defaults=default_pairs,
        sink=sink,
    )


def lift_to_delayed(base: TokenDFA) -> DelayedInputDFA:
    """Copy a token DFA and add a distinguished unused sink (Algorithm 2 input)."""
    sink = (max(base.states) + 1) if base.states else 0
    return _make_delayed(
        states=base.states | {sink},
        alphabet=base.alphabet,
        initial=base.initial,
        accepting=base.accepting,
        delta=dict(base.delta),
        defaults={},
        sink=sink,
    )


def _live_states(states: set[int], sink: int) -> list[int]:
    return sorted(state for state in states if state != sink)


def _incoming_labels(
    delta: dict[tuple[int, Token], int],
    family: set[int],
) -> set[Token]:
    return {token for (_src, token), dst in delta.items() if dst in family}


def _default_family(
    live: set[int],
    defaults: dict[int, int],
    delta: dict[tuple[int, Token], int],
    origin: int,
    token: Token,
) -> set[int]:
    """P_{origin, token} (Definition 3)."""
    family = {origin}
    changed = True
    while changed:
        changed = False
        for state in live:
            if state in family:
                continue
            if defaults.get(state) in family and (state, token) not in delta:
                family.add(state)
                changed = True
    return family


def _is_multiple_use(
    live: set[int],
    defaults: dict[int, int],
    delta: dict[tuple[int, Token], int],
    state: int,
    token: Token,
) -> bool:
    family = _default_family(live, defaults, delta, state, token)
    return len(_incoming_labels(delta, family)) > 1


def _sink_labels(u: Token, v: Token, uv: Token) -> frozenset[Token]:
    """O1 sink labels (Algorithm 2 lines 16–18 / Fig. 2), not Def. 4's u≠v branch."""
    labels = {v}
    if u == v:
        labels.add(uv)
    return frozenset(labels)


def _is_clean_copy(
    state: int,
    parent: int,
    live: set[int],
    accepting: set[int],
    defaults: dict[int, int],
    delta: dict[tuple[int, Token], int],
    alphabet: set[Token],
    sink: int,
    lam: frozenset[Token],
) -> bool:
    if defaults.get(state) != parent:
        return False
    if (state in accepting) != (parent in accepting):
        return False
    for token in alphabet:
        dest = delta.get((state, token))
        if token in lam:
            if dest != sink:
                return False
        elif dest is not None:
            return False
    return state in live


def apply_compact_merge(
    dfa: DelayedInputDFA,
    rule: MergeRule,
    options: CompactOptions | None = None,
) -> tuple[DelayedInputDFA, int]:
    """Apply [4] Algorithm 2. Returns (A', number of newly created states)."""
    opts = options if options is not None else CompactOptions()
    u = rule.left
    v = rule.right
    uv = rule.merged
    sink = dfa.sink

    delta = dict(dfa._lookup)
    defaults = dict(dfa._defaults)
    states = set(dfa.states)
    accepting = set(dfa.accepting)
    alphabet = set(dfa.alphabet)
    live = set(_live_states(states, sink))

    for state in _live_states(states, sink):
        if delta.get((state, u)) != sink:
            continue
        # Line 3 plants a sink on uv before S adds live uv-edges (Fig. 1).
        # Do not overwrite an already-live δ^ν(q, uv): [4] Lemma 3 assumes
        # unique useful concatenations; we allow proper useless uv reuse.
        existing_uv = _delta_nu(delta, defaults, sink, state, uv)
        if existing_uv is None or existing_uv == sink:
            delta[(state, uv)] = sink

    triples: list[StateTriple] = []
    for s1 in _live_states(states, sink):
        s2 = delta.get((s1, u))
        if s2 is None or s2 == sink:
            continue
        s3 = _delta_nu(delta, defaults, sink, s2, v)
        if s3 is None or s3 == sink:
            continue
        triples.append((s1, s2, s3))

    for s1, _s2, s3 in triples:
        existing = delta.get((s1, uv))
        if existing is not None and existing != s3:
            raise TokenDFAError(
                f"conflicting transition on {uv!r} from state {s1}: {existing} vs {s3}"
            )
        delta[(s1, uv)] = s3

    alphabet.add(uv)

    s2_set = {s2 for _s1, s2, _s3 in triples}
    if opts.o2_state_avoidance:
        s2_prime = {
            s2
            for s2 in s2_set
            if s2 == dfa.initial or _is_multiple_use(live, defaults, delta, s2, v)
        }
    else:
        s2_prime = set(s2_set)

    lam = _sink_labels(u, v, uv)
    next_id = (max(states) + 1) if states else 0
    fresh: dict[int, int] = {}
    n_fresh = 0
    for s2 in sorted(s2_prime):
        reused: int | None = None
        if opts.o3_clean_copy:
            copies = [
                state
                for state in _live_states(states, sink)
                if _is_clean_copy(
                    state, s2, live, accepting, defaults, delta, alphabet, sink, lam
                )
            ]
            if copies:
                reused = min(copies)
        if reused is not None:
            fresh[s2] = reused
            continue
        fresh_id = next_id
        next_id += 1
        fresh[s2] = fresh_id
        states.add(fresh_id)
        live.add(fresh_id)
        n_fresh += 1
        if s2 in accepting:
            accepting.add(fresh_id)
        defaults[fresh_id] = s2
        delta[(fresh_id, v)] = sink
        if u == v:
            delta[(fresh_id, uv)] = sink

    for s2 in s2_set - s2_prime:
        delta[(s2, v)] = sink
        if u == v:
            delta[(s2, uv)] = sink

    for s1, s2, _s3 in triples:
        if s2 in s2_prime:
            delta[(s1, u)] = fresh[s2]

    result = _make_delayed(
        states=frozenset(states),
        alphabet=frozenset(alphabet),
        initial=dfa.initial,
        accepting=frozenset(accepting),
        delta=delta,
        defaults=defaults,
        sink=sink,
    )
    return result, n_fresh


@dataclass(frozen=True, slots=True)
class CompactStep:
    """Sizes of A_i after merging rule i (0-based). n_states excludes the sink."""

    rule_index: int
    n_states: int
    n_final: int
    n_tokens: int
    n_transitions: int
    n_defaults: int
    n_fresh: int


@dataclass(frozen=True, slots=True)
class CompactResult:
    """A_n together with intermediates, per-rule counts, and enabled options."""

    final: DelayedInputDFA
    automata: tuple[DelayedInputDFA, ...]
    steps: tuple[CompactStep, ...]
    options: CompactOptions


def construct_compact_token_dfa(
    dictionary: Dictionary,
    base: TokenDFA,
    options: CompactOptions | None = None,
) -> CompactResult:
    """Build a compact D²FA by applying each dictionary rule in priority order."""
    opts = options if options is not None else CompactOptions()
    validation = validate_proper(dictionary)
    if not validation.ok:
        raise ImproperDictionaryError(validation.issues)

    current = lift_to_delayed(base)
    automata = [current]
    steps: list[CompactStep] = []
    for rule in dictionary.rules:
        current, n_fresh = apply_compact_merge(current, rule, opts)
        automata.append(current)
        steps.append(
            CompactStep(
                rule_index=rule.index,
                n_states=current.n_states_excluding_sink,
                n_final=current.n_final,
                n_tokens=current.n_tokens,
                n_transitions=current.n_transitions,
                n_defaults=current.n_defaults,
                n_fresh=n_fresh,
            )
        )
    return CompactResult(
        final=current,
        automata=tuple(automata),
        steps=tuple(steps),
        options=opts,
    )


def expand_defaults(dfa: DelayedInputDFA) -> TokenDFA:
    """Observation 1: materialise δ^ν and drop the sink and edges into it."""
    live = frozenset(state for state in dfa.states if state != dfa.sink)
    delta: dict[tuple[int, Token], int] = {}
    for state in live:
        for token in dfa.alphabet:
            dest = _delta_nu(dfa._lookup, dfa._defaults, dfa.sink, state, token)
            if dest is None or dest == dfa.sink:
                continue
            delta[(state, token)] = dest
    return make_token_dfa(
        states=live,
        alphabet=dfa.alphabet,
        initial=dfa.initial,
        accepting=dfa.accepting,
        delta=delta,
    )


def token_dfa_languages_agree(left: TokenDFA, right: TokenDFA) -> bool:
    """True iff two token DFAs agree on every reachable token step (small Γ)."""
    alphabet = left.alphabet | right.alphabet
    if (left.initial in left.accepting) != (right.initial in right.accepting):
        return False
    start = (left.initial, right.initial)
    seen = {start}
    queue: deque[tuple[int, int]] = deque([start])
    while queue:
        left_state, right_state = queue.popleft()
        for token in alphabet:
            next_left = left.step(left_state, token)
            next_right = right.step(right_state, token)
            if (next_left is None) != (next_right is None):
                return False
            if next_left is None or next_right is None:
                continue
            if (next_left in left.accepting) != (next_right in right.accepting):
                return False
            pair = (next_left, next_right)
            if pair not in seen:
                seen.add(pair)
                queue.append(pair)
    return True


def languages_agree(baseline: TokenDFA, compact: DelayedInputDFA) -> bool:
    """True iff the two automata agree on every reachable token step (small Γ)."""
    alphabet = baseline.alphabet | compact.alphabet
    if (baseline.initial in baseline.accepting) != (
        compact.initial in compact.accepting
    ):
        return False
    start = (baseline.initial, compact.initial)
    seen = {start}
    queue: deque[tuple[int, int]] = deque([start])
    while queue:
        left, right = queue.popleft()
        for token in alphabet:
            next_left = baseline.step(left, token)
            next_right = compact.step(right, token)
            if (next_left is None) != (next_right is None):
                return False
            if next_left is None or next_right is None:
                continue
            if (next_left in baseline.accepting) != (next_right in compact.accepting):
                return False
            pair = (next_left, next_right)
            if pair not in seen:
                seen.add(pair)
                queue.append(pair)
    return True


def serialize_delayed_input_dfa(dfa: DelayedInputDFA) -> str:
    """Return a deterministic text snapshot of a D²FA."""
    states = ",".join(str(state) for state in sorted(dfa.states))
    accepting = ",".join(str(state) for state in sorted(dfa.accepting))
    alphabet = ",".join(format_token_label(token) for token in sorted(dfa.alphabet))
    lines = [
        f"states: {states}",
        f"initial: {dfa.initial}",
        f"accepting: {accepting}",
        f"sink: {dfa.sink}",
        f"alphabet: {alphabet}",
        "defaults:",
    ]
    for src, dst in dfa.defaults:
        lines.append(f"{src} -> {dst}")
    lines.append("transitions:")
    for src, token, dst in dfa.transitions:
        lines.append(f"{src} --{format_token_label(token)}--> {dst}")
    return "\n".join(lines) + "\n"
