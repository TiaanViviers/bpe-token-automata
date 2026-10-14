# TICKET-020: Experiment host and timing helper

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Add a small shared helper so Section 7 runners record the same host metadata and use the same warmup / median / tracemalloc policy. Do not build an experiment framework.

## Background

Course §7.2 requires processor, memory, OS, language version, and important library versions. Only `timeout_study.py` currently records a full host block. Tokenize peak memory is tracemalloc (D62). Engineering spec: [`../specs/experimental-evaluation.md`](../specs/experimental-evaluation.md). Decisions D62, D67.

## Authoritative sources

- Project specification: §7.1–7.2 (PDF pp. 7–8)
- Approved decision: D62, D67, D68
- Existing implementation: `experiments/timeout_study.py` `host_metadata` / `rss_bytes`; `experiments/transducer_tokenize.py` timing

## Scope

The ticket includes:

- `experiments/host.py`: host metadata (python, platform, processor, cpu_count, host_memory_bytes, pyyaml/hypothesis versions), `median_seconds`, `peak_tracemalloc`, optional `rss_bytes`, JSON/CSV writers
- A pytest smoke for required metadata keys and a trivial median
- Do **not** refactor `timeout_study.py` onto this helper in this ticket (reuse committed 5.6 files as-is)

## Non-goals

The ticket explicitly excludes:

- Q3/Q5/Q6 runners (TICKET-021/022)
- matplotlib
- Changing automaton or tokenizer code
- Rerunning the timeout study

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded (D59–D68).
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

Mirror the timeout-study host fields plus `importlib.metadata` versions. `median_seconds(fn, repeats=7, warmup=True)` runs `fn` once untimed then `repeats` timed samples. `peak_tracemalloc` is a separate pass so it does not bias the median. Keep the module under `experiments/` and import it from tests the same way as `timeout_study`.

## Files likely to change

```text
26455900-CS345/experiments/host.py
26455900-CS345/tests/test_experiment_host.py
```

This list is guidance, not permission for unrelated changes.

## Acceptance criteria

- [ ] `host_metadata()` includes python, platform, processor, cpu_count, host_memory_bytes, library versions
- [ ] Median of a constant-time callable is a float
- [ ] Tracemalloc peak is an int (bytes)
- [ ] `make check` stays fast

## Required test evidence

### Unit tests

- Required keys on `host_metadata()`
- `median_seconds` with `repeats=1`, `warmup=False` on a no-op

### Regression tests

- None

### Differential or exhaustive tests

- Not required

### Property or equivalence tests

- Not required

### Negative and special cases

- Missing `/proc/meminfo` must not crash (`host_memory_bytes` may be null)

## Documentation changes

- [ ] Public API or README (later TICKET-023)
- [ ] Experiment documentation (later TICKET-023)

State specific expected updates:

- None in this ticket beyond the helper module docstring

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Formal interpretation: none
- Correctness: none for constructions
- Performance: helper must stay cheap in pytest
- Compatibility: Unix RSS unit (KiB on Linux) if `rss_bytes` is exposed
- Scope: do not swallow timeout_study into this module
- Reproducibility: library versions come from the locked environment

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
