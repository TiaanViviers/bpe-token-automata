# TICKET-013: Delayed-input DFA and O1 compact merge

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Implement `DelayedInputDFA`, lift a baseline `TokenDFA` by adding an unused sink, and apply [4] Algorithm \(2^X\) (O1 only: default transitions plus sink edges). Provide `expand_defaults` (Observation 1, sink dropped) and deterministic serialisation. Show language agreement with the Section 5.2 baseline.

## Background

Section 5.5 compact construction. Engineering spec: [`../specs/compact-delayed-input-automaton.md`](../specs/compact-delayed-input-automaton.md). O2/O3 are TICKET-014; flags may exist but must be off (or unimplemented paths unused) for this ticket’s constructor behaviour.

## Authoritative sources

- Project specification: §5.5, §4.3, §6.4–6.5
- Paper and section: [4] Def. 2, \(\delta^\nu\), Observation 1 (PDF p. 3); Algorithm 2 with blue/red lines removed (PDF p. 5); Lemma 1
- Approved decision: [`../plans/section-5-5-compact-d2fa.md`](../plans/section-5-5-compact-d2fa.md) D33–D42
- Existing implementation: `construct_token_dfa`, `TokenDFA`

## Scope

The ticket includes:

- Frozen `DelayedInputDFA` with partial \(\delta\), partial \(\nu\), `sink`, `step` via \(\delta^\nu\), `accepts`
- `lift_to_delayed`, `apply_compact_merge` with O2/O3 disabled, `construct_compact_token_dfa`
- `expand_defaults` → `TokenDFA` without sink
- `serialize_delayed_input_dfa`
- Tests: \(\delta^\nu\) units; empty/improper dictionaries; Example 2 / unary language vs baseline; Lemma 1 state-count after expand; Fig. 2 A1 structural facts (`a⫽b`)

## Non-goals

The ticket explicitly excludes:

- O2/O3 logic (TICKET-014)
- Product-automaton helper beyond expand+accepts
- Comparison experiment
- Graphviz, CLI, O4
- `docs/` updates (TICKET-014)

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

See engineering spec. `step` returns `None` for \(\bot\) and for \(q_s\). Triple finding: explicit \(u\), extended \(v\). Fresh state: \(\nu=\mathrm{s}_2\), sink on \(v\) (and \(uv\) iff \(u=v\)), then redirect \(\delta(s_1,u)\). Do not import `tokenize_reference`.

## Files likely to change

```text
26455900-CS345/src/bpe_token_automata/automaton/compact.py
26455900-CS345/src/bpe_token_automata/automaton/__init__.py
26455900-CS345/src/bpe_token_automata/__init__.py
26455900-CS345/tests/test_compact_construction.py
```

## Acceptance criteria

- [ ] Lifted unused sink is non-accepting and has no outgoing edges
- [ ] `step` follows \(\delta^\nu\); explicit edges win
- [ ] O1-only compact agrees with baseline `accepts` on Example 2 and unary
- [ ] `expand_defaults(compact).n_states == baseline.n_states` (O1-only)
- [ ] Improper dictionaries raise `ImproperDictionaryError`
- [ ] Empty dictionary language equals the lifted base / baseline

## Required test evidence

### Unit tests

- explicit vs default vs sink
- acyclic \(\nu\)
- \(u=v\) sink on \(uv\) from fresh; \(u\neq v\) no sink on \(uv\) from O1

### Differential or exhaustive tests

- Example 2 and unary: compact vs `construct_token_dfa` on token sequences derived from strings of length \(\le 6\) (or the existing unary bound)

### Negative and special cases

- improper dictionary
- empty dictionary

## Documentation changes

- [ ] None in the assessable repo (TICKET-014)

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Formal interpretation: \(S\) must use \(\delta^\nu\) on \(v\)
- Correctness: Lemma 1 isomorphism is after dropping sink
- Scope: do not implement O2/O3 here beyond flag plumbing

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Both partners can explain the implementation.
