# TICKET-016: Timeout harness, results, and Section 5.6 docs

## Status

```text
review
```

Blocked on TICKET-015: cleared 2026-09-14 (human reviewed conversion).

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Run baseline and compact token-DFA construction on prefixes of the two committed realistic dictionaries under a 60 s cutoff, a 600 s timeout, and an 8 GiB RSS cap. Write raw JSON results that include successes and failures. Document the method so a clean checkout can reproduce the study without guessing limits or hiding timeouts.

## Background

Course §5.6 and §7.1–7.3 questions 1–4. The 5.5 script `experiments/compact_compare.py` is a toy comparison (`tracemalloc`, `{a,b}` alphabets) and must not be claimed as §5.6. Engineering spec: [`../specs/larger-dictionary-timeouts.md`](../specs/larger-dictionary-timeouts.md). Decisions D47–D52.

## Authoritative sources

- Project specification: §5.6 (PDF p. 5); §5.5 required comparison columns; §7.1–7.2
- Paper and section: [4] §7 motivates scale; do not copy paper tables as our results
- Approved decision: D47, D48, D49, D50, D51, D52
- Existing implementation: `apply_merge`, `apply_compact_merge`, `byte_alphabet`, `universal_token_dfa`; TICKET-015 files

## Scope

The ticket includes:

- `experiments/timeout_study.py`: parent launches one child per `(dictionary, construction)`
- Child: incremental construction from \(A_0\), JSONL checkpoints, 600 s wall-clock, 8 GiB cap
- Summary `experiments/results/timeout_study.json` (optional CSV generated from the same data)
- Host metadata: processor, RAM, OS, Python, important library versions
- README: how to run; §5.6 status; RSS vs tracemalloc; O4 not implemented
- `docs/design-decisions.md` §5.6
- A short-limit smoke so `make check` can exercise the protocol without a 10-minute wait

## Non-goals

The ticket explicitly excludes:

- Re-converting dictionaries (TICKET-015)
- Transducer compile/tokenize, minbpe
- O4, compact flag sweep, Graphviz, CLI
- Section 9 PDF plots
- Changing automaton algorithms
- Averaging timeouts into successful measurements
- Silently raising the 8 GiB cap
- 8.2 / 8.11

## Preconditions

Before implementation:

- [ ] TICKET-015 converted files are committed and `validate_proper`.
- [ ] Human has reviewed that `Ġ t` became `\x20 t` and both dictionaries are proper.
- [ ] Relevant formal definitions are understood.
- [ ] `26455900-CS345/` is on `main` and its working state is understood.
- [ ] Pre-existing changes have been identified and can be preserved.

## Proposed design

Parent process:

1. Record host metadata.
2. For each of `{gpt2, smollm2}` × `{baseline, compact}` start a child with a 600 s join timeout and memory cap.
3. On child timeout/OOM/crash, harvest the last JSONL checkpoint.
4. Build comparison rows: intersection of prefixes where both constructions have `status=ok`; plus `timeout_60s` / `timeout_600s` / `memory` / `completed` boundary rows per construction.
5. Write `experiments/results/timeout_study.json`.

Child process:

1. `resource.setrlimit(RLIMIT_AS, (8 GiB, 8 GiB))` where available (Linux).
2. Parse the committed dictionary; build \(A_0=\mathrm{universal\_token\_dfa}(\mathrm{byte\_alphabet}())\).
3. For compact, `lift_to_delayed` then `apply_compact_merge` with default `CompactOptions`.
4. After prefixes in `{0,1,2,5,10,25,50,100,250,500,1000,2500,5000,10000,25000,50000}` ∩ `[0, |D|]` and after **every** rule that finishes when elapsed just crossed 60 s or when stopping: append JSONL with counts, `elapsed_s`, `rss_bytes` (`resource.getrusage().ru_maxrss`, documenting KB vs bytes).
5. Continue past 60 s until 600 s, OOM, error, or \(n=|D|\).
6. Do not serialise or render Graphviz inside the timed region.

JSON must include:

- `limits`: `timeout_s_short=60`, `timeout_s_long=600`, `memory_limit_bytes=8*1024**3`, `memory_measure="ru_maxrss"`
- `compact_options`: O2/O3 true; note O1 always on, O4 absent
- `rows` / `boundaries` with `status` in `{ok, timeout_60s, timeout_600s, memory, unsupported, error, completed}`
- No invented counts for failed prefixes

`timeout_60s` is an annotation of the last `ok` prefix with `elapsed_s <= 60`, not a separate process.

Keep `experiments/compact_compare.py` unchanged aside from README wording that it is still not §5.6.

## Files likely to change

```text
26455900-CS345/experiments/timeout_study.py
26455900-CS345/experiments/results/timeout_study.json
26455900-CS345/tests/test_timeout_study.py
26455900-CS345/README.md
26455900-CS345/docs/design-decisions.md
```

This list is guidance, not permission for unrelated changes.

## Acceptance criteria

- [ ] Four child runs are defined (2 dictionaries × 2 constructions)
- [ ] 60 s and 600 s cutoffs and 8 GiB are stated in the JSON
- [ ] Peak memory is RSS (`ru_maxrss`), documented, not tracemalloc
- [ ] Timeout/OOM/error rows exist when they occur; never omitted; never estimated
- [ ] Shared-prefix comparison uses only prefixes both finished
- [ ] Compact `n_states` excludes the sink; `n_defaults` reported; baseline has no defaults
- [ ] README documents the extra command and that `make check` does not run it
- [ ] Design-decisions records D47–D52 at project-doc level (alphabet, limits, RSS, O4 out)
- [ ] Smoke test uses a tiny dictionary and a sub-second limit
- [ ] `make check` still passes in well under the 10-minute study time

## Required test evidence

### Unit tests

- Checkpoint prefix list
- JSON schema/keys on a fixture or dry-run
- Status vocabulary includes failure values

### Regression tests

- README / design-decisions mention §5.6 as the timeout study (manual in review)

### Differential or exhaustive tests

- Not required for the harness (constructions already have §6 tests)

### Property or equivalence tests

- Not required here; do not run `languages_agree` on 256-symbol realistic prefixes in pytest

### Negative and special cases

- Child timeout path: fake 0.5 s limit on `example2.merges` still writes a summary with `timeout_*` or `completed`
- Kill leaves the last checkpoint, not an empty file

## Documentation changes

- [ ] Public API or README
- [ ] Architecture or algorithm documentation (method only; no new algorithm)
- [ ] Decision record in `docs/design-decisions.md`
- [ ] Testing documentation (study is not in `make check`)
- [ ] Experiment documentation
- [ ] Known limitations (O4, 8 GiB, RSS vs `RLIMIT_AS`, no transducer)

State specific expected updates:

- README status line: 5.1–5.6 constructions/experiments as applicable
- Experiment command `uv run python experiments/timeout_study.py`
- Design-decisions: §5.6 paragraph; pointer that 5.4/5.5 toy JSONs remain not this study

## Validation commands

```bash
cd 26455900-CS345
make check
uv run python experiments/timeout_study.py
```

The second command is the 5.6 study. It may take up to about \(4 \times 10\) minutes plus overhead. Partial JSON after a single killed child is still a valid artefact if statuses are honest.

## Risks

- Formal interpretation: none new; do not treat [4] full-dict tables as our outcome
- Correctness: an 8 GiB `RLIMIT_AS` may fire before RSS reports 8 GiB; document
- Performance: baseline may die at tiny \(n\); that answers §7.3 Q4
- Compatibility: do not slow `make check`
- Scope: no transducer sneak-in
- Reproducibility: record host; one machine; no median of timeouts

## Open questions

None blocking after TICKET-015 review.

Do not begin implementation while a blocking question remains unresolved.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] Relevant documentation updated.
- [ ] `make check` passes.
- [ ] Timeout study JSON committed with honest failures if they occurred.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Handoff produced where appropriate.
- [ ] Human review completed.
- [ ] Both partners can explain limits, prefixes, and why a timeout is a result.
