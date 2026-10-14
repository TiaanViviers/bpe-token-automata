# TICKET-012: Transducer performance measurements and documentation

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Measure tokenization time and peak memory for the transducer vs at least the 5.1 reference (and minbpe if TICKET-011 succeeded) on small fixtures. Record results and document §5.4 decisions.

## Background

Course §5.4 performance paragraph and §7.1/7.3 questions 5–6. Not the §5.6 large-dictionary timeout study.

## Authoritative sources

- Project specification: §5.4, §7.1–7.3
- Paper and section: [5] Corollary 14 and the caveat on compiled state space / pretokenization (PDF p. 12)
- Approved decision: D9, D32
- Existing implementation: `tokenize`, `tokenize_reference`

## Scope

The ticket includes:

- `experiments/` script and committed CSV/JSON
- ordinary and pathological strings (`a^n`, nested self-merges)
- `docs/design-decisions.md` §5.4; README status; short `docs/transducer.md` Fig. 8 walkthrough

## Non-goals

§5.6 prefixes, one-/ten-minute timeouts, compact-automaton measurements.

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

`time.perf_counter` + `tracemalloc` on identical inputs. Repeat short runs; report median. Separate compile time from tokenize time. Interpret: linear run after compile; compiled machine can still be large; no pre-tokenization.

## Files likely to change

```text
26455900-CS345/experiments/
26455900-CS345/docs/design-decisions.md
26455900-CS345/docs/transducer.md
26455900-CS345/README.md
```

## Acceptance criteria

- [ ] Raw JSON/CSV committed
- [ ] Transducer and reference measured
- [ ] Caveats written (state space, pre-tokenization)
- [ ] README lists §5.4 as implemented

## Required test evidence

### Unit tests

- Experiment script is runnable; not a substitute for §6.2 tests

## Documentation changes

- [x] Public API or README
- [x] Architecture or algorithm documentation
- [x] Decision record
- [x] Experiment documentation
- [x] Known limitations

## Validation commands

```bash
cd 26455900-CS345
uv run python experiments/transducer_tokenize.py
make check
```

## Risks

- Performance: noisy single-machine timings; report method and hardware
- Reproducibility: record Python version and repetition policy
- Scope: keep dictionaries tiny

## Open questions

None.

## Definition of done

- [ ] Measurements committed.
- [ ] Docs updated.
- [ ] `make check` passes.
