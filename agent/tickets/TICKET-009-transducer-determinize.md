# TICKET-009: Béal–Carton subsequentialisation

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Determinise Observation 3 transducers with Béal–Carton [3, §2.2] (PDF pp. 233–234). Lock Fig. 8(b) behaviour, including \(F(q_1)=a\).

## Background

Nondeterministic Observation 3 is not the shipped tokenizer. Theorem 13 of [5] points at this algorithm.

## Authoritative sources

- Project specification: §5.4
- Paper and section: [3] §2.2; [5] Fig. 8(b), Example 9
- Approved decision: D24, D25, D30
- Existing implementation: TICKET-008 `from_token_dfa`

## Scope

The ticket includes:

- `SubsequentialTransducer` and `subsequentialise`
- pending-output / state-count caps
- tests: Fig. 8(b); empty dictionary remains equivalent; input-determinism

## Non-goals

The ticket explicitly excludes:

- Full §6.2 matrix (TICKET-010)
- minbpe, experiments

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

BFS of accessible pair-sets. On input \(a\), form \(R\), emit LCP \(v\), keep remainders. Accepting \(F\) is the unique delayed word of an accepting pair. Cap \(|w|\) at \(2n^2 M\).

## Files likely to change

```text
26455900-CS345/src/bpe_token_automata/transducer/determinize.py
26455900-CS345/src/bpe_token_automata/transducer/model.py
26455900-CS345/tests/test_transducer_determinize.py
```

## Acceptance criteria

- [ ] Result is input-deterministic
- [ ] After one `a`, no token is emitted and \(F=a\)
- [ ] `aa` emits `aa`; `ab` emits `a` then `b`
- [ ] Empty dictionary subsequentialise is the identity tokenizer
- [ ] Cap raises `TransducerError` rather than looping forever (tested with a tiny fake cap if needed)

## Required test evidence

### Unit tests

- Fig. 8(b) walk from the PDF, not from a search of Observation 3

### Negative and special cases

- Over-cap raises

## Documentation changes

None in the assessable repo (TICKET-012).

## Validation commands

```bash
cd 26455900-CS345
uv run pytest tests/test_transducer_determinize.py tests/test_transducer_observation.py
make check
```

## Risks

- Formal interpretation: multi-token outputs
- Correctness: LCP over token sequences, not raw bytes
- Performance: exponential subset construction
- Scope: do not weaken Fig. 8 tests

## Open questions

None.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
