# TICKET-003: Construction stats, serialisation, Graphviz

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

For every construction run, record after each rule the number of states, final states, tokens, transitions, and fresh states. Provide deterministic textual serialisation and optional Graphviz DOT output.

## Background

Spec §5.2 required outputs. Counts must reflect untrimmed Algorithm 2 automata (D14).

## Authoritative sources

- Project specification: §5.2 required outputs; §4.2 textual serialisation for tests
- Paper and section: [5] Remark 2 (useless states may exist); Lemma 7 (\(|Q'|=|Q|+|S_2|\))
- Approved decision: D14, D17, D20
- Existing implementation/documentation: TICKET-002 `ConstructionResult`

## Scope

The ticket includes:

- `ConstructionStep` fields populated by `construct_token_dfa`
- `serialize_token_dfa` — sorted state ids, sorted transitions, token labels printable ASCII or `\xHH`
- `to_dot` — Graphviz; accepting states doublecircle; initial indicated

## Non-goals

The ticket explicitly excludes:

- Rendering PNG/SVG in CI (DOT text only)
- CLI writers
- Trimming before counting

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

Serialisation is the test oracle format, not Graphviz. Token labels: ASCII graphic bytes except `\\` print as characters; otherwise `\xHH`.

## Files likely to change

```text
26455900-CS345/src/bpe_token_automata/automaton/serialize.py
26455900-CS345/src/bpe_token_automata/automaton/graphviz.py
26455900-CS345/tests/test_token_dfa_serialize.py
```

## Acceptance criteria

- [ ] After each rule, stats equal the constructed automaton’s sizes plus `n_fresh = |S_2|`
- [ ] Serialisation is deterministic (same DFA → identical string)
- [ ] `to_dot` is optional and does not affect counts

## Required test evidence

### Unit tests

- Serialisation order stable
- Example 2 stats: \(A_0\) 1 state; after first merge 2 states, 1 fresh; after second 3 states, 1 fresh

### Regression tests

-

### Differential or exhaustive tests

-

### Property or equivalence tests

-

### Negative and special cases

- Empty \(S\): `n_fresh == 0`, `n_tokens` may increase by one

## Documentation changes

- [x] Decision record D20

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Formal interpretation: counting alphabet symbols vs used transition labels
- Reproducibility: unsorted sets would make snapshots differ

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
