# TICKET-023: Section 7 experimental evidence document

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Publish an assessable experimental note that answers §7.3 questions 1–6 from repository files: method, host, tables, and limitations. Point the README at it. Record §7 method in `docs/design-decisions.md`.

## Background

D66. Counterpart of TICKET-019 / `docs/testing.md`. Q1/Q2/Q4 tables come from committed `timeout_study.csv` / `.json`. Q3/Q5/Q6 tables come from TICKET-021/022 result files. No plots. Depends on those result files existing.

## Authoritative sources

- Project specification: §7.1–7.3, §9.1 experimental method (tables, not the PDF body)
- Approved decision: D59, D66, D68
- Existing documentation: `docs/testing.md`, `docs/design-decisions.md`, README Experiments

## Scope

The ticket includes:

- `docs/experiments.md` with method, hosts, one table per question generated from JSON/CSV, limitations (RSS vs tracemalloc, O4 absent, prefix 250, no GPT-2 tokenize, no plots)
- README: Section 7 status, commands for `rule_patterns.py` and `tokenize_eval.py`, pointer to `docs/experiments.md`
- `docs/design-decisions.md` short §7 paragraph (D59–D68 at project-doc level)

## Non-goals

The ticket explicitly excludes:

- PDF report chapter, figures, matplotlib
- Rerunning `timeout_study.py`
- Extensions 8.2/8.11 identified in README (still later)
- Changing result numbers by hand

## Preconditions

Before implementation:

- [ ] `timeout_study.json` is present (already committed).
- [ ] `rule_patterns.py` and `tokenize_eval.py` have been run and JSON/CSV exist.

## Proposed design

Write tables by reading the result files (human/agent copies numbers from a real run, like TICKET-019). State both hosts if the Q3/Q6 host differs from the 5.6 host. Compact `n_states` excludes the sink. Point to `docs/testing.md` as the broader Q5 evidence.

## Files likely to change

```text
26455900-CS345/docs/experiments.md
26455900-CS345/README.md
26455900-CS345/docs/design-decisions.md
agent/plans/section-7-experiments.md
agent/README.md
```

## Acceptance criteria

- [ ] Six questions each have a table or an explicit pointer to the file that is the table
- [ ] Throughput unit is bytes/s
- [ ] Timeouts appear as results
- [ ] README commands match the runners
- [ ] No PNG assets

## Required test evidence

None beyond `make check` still passing (docs-only plus already-tested runners).

## Documentation changes

- [x] Public API or README
- [x] Decision record
- [x] Experiment documentation
- [x] Known limitations

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Copying a stale CSV into Markdown; tables must match the committed JSON
- Claiming compact is slower from the toy 5.5 script

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Tables match committed result files.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
