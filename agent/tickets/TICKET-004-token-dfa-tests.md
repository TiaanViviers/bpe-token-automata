# TICKET-004: Token DFA paper examples and correctness tests

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Lock Algorithm 2 against paper Example 2 / Fig. 3, a unary self-merge chain, spec §6.1 unit cases, and bounded differential checks using the independent 5.1 reference tokenizer.

## Background

Expected automata come from the PDF figures and hand application of Algorithm 2, not from `apply_merge`. The reference tokenizer must not be imported by automaton production code.

## Authoritative sources

- Project specification: §6.1, §6.2 (DFA acceptance clause), §6.3
- Paper and section: [5] Example 2, Figs. 3–4; Algorithm 2 \(u=v\) vs \(u\neq v\)
- Approved decision: D15, D22; unary chain is project-constructed (`[a⫽a, aa⫽a]`) because [5] has no unary figure
- Existing implementation/documentation: `tokenize_reference`

## Scope

The ticket includes:

- Example 2 fixtures and transition assertions for \(A_0,A_1,A_2\)
- Unary dictionary `[a⫽a, aa⫽a]` over \(\{a\}\)
- §6.1 cases listed in the engineering spec
- Exhaustive: all \(w\in\{a,b\}^{\le 6}\) on Example 2’s \(D\); canonical sequence accepted; \(T_\emptyset(w)\) rejected when it differs
- User-supplied non-universal string DFA smoke test

## Non-goals

The ticket explicitly excludes:

- 5.3 report write-up
- Original Unicode/emoji examples
- Transducer comparison
- Compact-automaton equivalence

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

Hand-code Fig. 3 as sets of `(src, token, dst)` triples. Compare to `construct_token_dfa` results. Differential tests import `tokenize_reference` only from test files.

## Files likely to change

```text
26455900-CS345/tests/test_token_dfa_construction.py
26455900-CS345/tests/test_token_dfa_examples.py
26455900-CS345/tests/test_token_dfa_exhaustive.py
26455900-CS345/data/dictionaries/
26455900-CS345/data/automata/
```

## Acceptance criteria

- [ ] Example 2 \(A_1\) and \(A_2\) match Fig. 3
- [ ] Self-merge does not copy \(uv\) onto the fresh state
- [ ] Distinct merge copies \(uv\) onto the fresh state
- [ ] Improper dictionary raises
- [ ] Bounded oracle agreement on \(\{a,b\}^{\le 6}\)

## Required test evidence

### Unit tests

- §6.1 list in the engineering spec

### Regression tests

- Paper Example 2 steps

### Differential or exhaustive tests

- All strings length ≤ 6 over `{a,b}` vs `tokenize_reference`

### Property or equivalence tests

- Deferred (full §6.4 later)

### Negative and special cases

- Improper dictionary; no-op rule

## Documentation changes

- [ ] None required beyond constructor docs

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Formal interpretation: Fig. 3 vs Example 2 prose
- Correctness: missing non-canonical rejection
- Reproducibility: bound \(n=6\) must be stated

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Both partners can explain Example 2 from Fig. 3.
