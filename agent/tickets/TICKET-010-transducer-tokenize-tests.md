# TICKET-010: compile_tokenizer, tokenize, and independent tests

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Expose `compile_tokenizer` / `tokenize` and prove token-sequence agreement with `tokenize_reference` plus DFA acceptance (course §6.2–6.4).

## Background

This is the marked tokenizer. The 5.1 reference remains the oracle and must not be imported by transducer production code.

## Authoritative sources

- Project specification: §5.4, §6.2–6.4
- Paper and section: [5] Theorem 13, Corollary 14; [6] Definition 3
- Approved decision: D26, D27, D28
- Existing implementation: TICKET-008/009; `tokenize_reference`; exhaustive `{a,b}^{≤6}`

## Scope

The ticket includes:

- `compile_tokenizer(dictionary, base)` and `tokenize(machine, text)`
- §6.2 differential checks
- extend exhaustive Example 2 tests to the transducer
- Hypothesis proper-dictionary generator
- Unicode/emoji fixtures
- negatives: improper \(D\), byte outside \(\Sigma\), empty input, user-supplied \(L\)

## Non-goals

minbpe (TICKET-011), performance artefacts (TICKET-012), compact automaton.

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

`compile_tokenizer` = `construct_token_dfa` → Observation 3 → `subsequentialise`. Tests import the oracle only from test modules.

## Files likely to change

```text
26455900-CS345/src/bpe_token_automata/transducer/tokenize.py
26455900-CS345/src/bpe_token_automata/__init__.py
26455900-CS345/tests/test_transducer_tokenize.py
26455900-CS345/tests/test_transducer_exhaustive.py
26455900-CS345/tests/test_transducer_properties.py
26455900-CS345/tests/test_transducer_unicode.py
26455900-CS345/tests/test_token_dfa_exhaustive.py
```

## Acceptance criteria

- [ ] `tokenize` equals `tokenize_reference` on §6.2 checks
- [ ] detokenize equals \(w\); DFA accepts; altered non-canonical boundaries rejected
- [ ] exhaustive `{a,b}^{≤6}` on Example 2 includes the transducer
- [ ] Hypothesis properties pass with a recorded seed
- [ ] Unicode/emoji dictionaries agree
- [ ] Off-domain and improper inputs raise

## Required test evidence

### Differential or exhaustive tests

- Example 2, unary chain, finite `{ab}` language

### Property or equivalence tests

- detokenization, stability, DFA agreement

### Negative and special cases

- improper dictionary; unknown byte; empty string on universal vs non-universal base

## Documentation changes

Package `__init__` exports only.

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Correctness: correlated tests if Observation 3 search is used as oracle
- Scope: keep generators small
- Reproducibility: Hypothesis seed

## Open questions

None.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
