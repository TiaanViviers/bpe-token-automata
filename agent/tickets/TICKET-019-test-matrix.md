# TICKET-019: Section 6.7 test matrix

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Publish an assessable test matrix that names each §6 family, the fault class it targets, the bound or seed, the number of cases run, the outcome, and explicit limitations (especially large alphabets for §6.5).

## Background

Spec §6.7: the repository has automated tests and a command that runs them (`make test` already exists). The report must include a concise matrix. Screenshots are not evidence. D58 puts the matrix in `docs/testing.md` so the PDF report can copy it.

Depends on TICKET-017 and TICKET-018 so counts reflect the completed suite.

## Authoritative sources

- Project specification: §6.7, §9.1 testing methodology
- Approved decision: D58, D53–D57
- Existing implementation/documentation: `Makefile` `test` / `check`; coverage audit

## Scope

The ticket includes:

- A real `make test` (or `uv run pytest`) run after 017+018
- `docs/testing.md` with one row per family (6.1–6.6), plus the runner command
- Case counts from that run (pytest items and, where relevant, inner enumerations such as \(2^9-1=511\) Example 2 strings)
- README pointer
- Explicit §6.5 limitation: no product expansion on GPT-2 / SmolLM 256-byte / ~50k-token alphabets
- Do **not** list 5.6 timeout smokes as 6.6 rows (they may appear as a separate “harness smoke” note)

## Non-goals

The ticket explicitly excludes:

- PDF report chapter
- Screenshots
- Re-running the 10-minute timeout study
- Changing tests except to fix a count/doc mismatch discovered while writing the matrix

## Preconditions

Before implementation:

- [ ] TICKET-017 and TICKET-018 tests exist and pass
- [ ] `26455900-CS345/` working state is understood

## Proposed design

Table columns: family, fault class, artefacts (test modules), bound/seed, cases, outcome, limitations.

Inner enumeration sizes (Example 2 \(|\{a,b\}^{\le 8}|\), Hypothesis 40 examples, \(a^n\) four lengths) are stated even when they sit inside one pytest function.

## Files likely to change

```text
26455900-CS345/docs/testing.md
26455900-CS345/README.md
26455900-CS345/docs/design-decisions.md
```

## Acceptance criteria

- [ ] `docs/testing.md` exists and is copyable into the report
- [ ] README links to it
- [ ] Counts come from a command that was actually run
- [ ] Large-alphabet 6.5 limit is stated
- [ ] 5.6 study is not labelled as 6.6

## Required test evidence

### Unit tests

- None new

## Documentation changes

- [x] Testing documentation: `docs/testing.md`
- [x] Public API or README: pointer
- [ ] Known limitations: 6.5 large \(\Gamma\)

## Validation commands

```bash
cd 26455900-CS345
make check
```

Additional commands:

```bash
uv run pytest -q --collect-only
```

## Risks

- Reproducibility: case counts drift if tests are added later — date the matrix and the HEAD commit
- Scope: do not rewrite tests to inflate counts

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Both partners can walk the marker through the matrix.
