# TICKET-008: Transducer model and Observation 3

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Add frozen transducer types and implement Observation 3 of [5] (PDF p. 10). Lock the empty-dictionary identity machine and Fig. 8(a) for \(D=[a⫽a]\).

## Background

First half of §5.4. Engineering spec: [`../specs/string-to-tokenization-transducer.md`](../specs/string-to-tokenization-transducer.md).

## Authoritative sources

- Project specification: §5.4, §4.3
- Paper and section: [5] Definition 6, Observation 3, Fig. 8(a) (PDF pp. 10–11)
- Approved decision: D23, D25, D26, D29
- Existing implementation: `TokenDFA`, `construct_token_dfa`

## Scope

The ticket includes:

- `Transducer` / errors
- `from_token_dfa`
- deterministic serialisation and optional Graphviz
- tests: empty dictionary; Fig. 8(a)

## Non-goals

The ticket explicitly excludes:

- Béal–Carton determinisation (TICKET-009)
- `tokenize` / minbpe / experiments

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

Spell each DFA token \(u=\alpha_1\cdots\alpha_k\) left to right. Intermediate ids start after `max(states)` in sorted DFA-transition order. \(F(q)=\varepsilon\) on DFA accepting states.

Do not import `tokenize_reference`.

## Files likely to change

```text
26455900-CS345/src/bpe_token_automata/transducer/
26455900-CS345/src/bpe_token_automata/__init__.py
26455900-CS345/tests/test_transducer_observation.py
```

## Acceptance criteria

- [ ] Empty dictionary: one transition \(q_0 \xrightarrow{\alpha|\alpha} q_0\) per base symbol; subsequential
- [ ] Fig. 8(a) matches the PDF (nondeterministic \(a\) from \(q_0\); \(s_1\) not accepting)
- [ ] Spelling states are not accepting
- [ ] Deterministic serialisation

## Required test evidence

### Unit tests

- Observation 3 on \(A_0\) and \(A_1\) of Example 2’s first merge

### Regression tests

- None yet

### Differential or exhaustive tests

- None (TICKET-010)

### Property or equivalence tests

- None

### Negative and special cases

- Empty token in a DFA alphabet must not occur; length-1 tokens emit immediately

## Documentation changes

- [ ] Public API or README
- [x] Architecture or algorithm documentation (private spec already)
- [ ] Decision record (TICKET-012)

## Validation commands

```bash
cd 26455900-CS345
uv run pytest tests/test_transducer_observation.py
make check
```

## Risks

- Formal interpretation: Fig. 8(a) vs our integer ids
- Correctness: shared prefixes of tokens create genuine nondeterminism
- Performance: none
- Compatibility: none
- Scope: do not start determinisation
- Reproducibility: sorted transition order

## Open questions

None.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
