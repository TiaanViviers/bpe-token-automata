# Handoff: Example — agent infrastructure navigation

> **EXAMPLE ONLY.** Shows the shape of a filled handoff. Copy [`../../templates/handoff.md`](../../templates/handoff.md) for real handoffs.

## Task

- Ticket: [`../../tickets/TICKET-000-example-infrastructure.md`](../../tickets/TICKET-000-example-infrastructure.md)
- Branch: (example — often `chore/agent-infrastructure`)
- Agent or contributor: example
- Date: 2026-07-26
- Scope: navigation docs, CS345 spec pointer, Cursor glob widening, wording fix, example ticket/handoff

## Status

```text
complete
```

Explain the current state in a few sentences.

This example handoff records a documentation-only change set that makes the official project specification discoverable and improves agent navigation. No `project/` source code was modified.

## Summary of work

Describe what was actually changed.

- Confirmed Markdown and PDF copies of the CS345 specification under `research/`.
- Added `agent/specs/cs345-project-specification.md` as the agent entry pointer.
- Added navigation cheat sheets to `AGENTS.md` and `agent/README.md`.
- Widened Cursor rule globs for feature and testing work.
- Fixed feature-workflow wording to set ticket `Status` to `done` instead of “moving” the file.
- Added this example ticket/handoff pair.

## Files changed

```text
AGENTS.md
agent/README.md
agent/specs/cs345-project-specification.md
agent/rules/research-sources.md
agent/workflows/feature-development.md
research/README.md
.cursor/rules/feature-development.mdc
.cursor/rules/git-workflow.mdc
.cursor/rules/testing-correctness.mdc
.cursor/rules/repository-context.mdc
agent/tickets/TICKET-000-example-infrastructure.md
agent/handoffs/TICKET-000/2026-07-26-example-handoff.md
```

For each important file, briefly state its role.

- Spec pointer: single place agents should open first for the course brief.
- Cheat sheets: reduce mandatory reading of the full agent map.
- Cursor globs: attach process/testing rules during ordinary implementation.

## Sources consulted

- Project specification: Markdown at `research/markdown/cs345-project-specification.md`; PDF at `research/sources/cs345-project-specification.pdf` (renamed from `SPEC.pdf` for a stable id)
- Papers and sections: N/A
- Approved decisions: Markdown-first reading; PDF verify-only
- Existing documentation: prior agent infrastructure draft

State whether converted Markdown and/or original PDFs were checked.

Markdown was read for discoverability. PDF presence was verified on disk; full PDF ingest was intentionally avoided.

## Decisions made

Record decisions that affect:

- semantics;
- interfaces;
- representations;
- error handling;
- tests;
- performance;
- documentation.

- Stable id `cs345-project-specification` for both Markdown and PDF filenames.
- Pointer lives under `agent/specs/`; body stays under `research/`.
- Example ticket remains `Status: done` and clearly labelled EXAMPLE ONLY.

Distinguish temporary implementation choices from approved architectural decisions.

## Assumptions and invariants

- `*.pdf` remains gitignored; collaborators keep the PDF locally under `research/sources/`.
- Agents must not treat this example ticket as active work.

## Tests added or changed

### Added

- None (process/docs)

### Modified

- None

### Important cases covered

- Path presence checks listed under validation

## Commands run

```bash
test -f research/markdown/cs345-project-specification.md
test -f research/sources/cs345-project-specification.pdf
test -f agent/specs/cs345-project-specification.md
```

Add all meaningful validation commands actually executed.

## Validation results

| Check | Result |
|---|---|
| Formatting | N/A |
| Linting | N/A |
| Type checking | N/A |
| Unit tests | N/A |
| Full `make check` | not run (docs-only example) |
| Submission export | not run |
| Additional verification | spec Markdown + PDF + pointer paths present |

Do not report a check as passing unless it was run successfully.

## Known limitations

- Marker conversion of the specification is `converted-unverified`.
- Skills discovery adapters are still future work.

## Unresolved questions

- None blocking for this example.

Mark whether each question is blocking or non-blocking.

## Risks for reviewer

Call attention to areas needing careful review:

- formal interpretation;
- edge cases;
- test independence;
- performance;
- documentation;
- compatibility;
- submission boundary.

- Confirm PDF rename/`SPEC.pdf` local copies are updated for both partners.
- Confirm example docs are not mistaken for live tickets.

## Pre-existing changes preserved

List unrelated modifications that existed before the task and were not changed.

```text
.github/pull_request_template.md (modified earlier)
scripts/verify_submission.sh (modified earlier)
```

## Recommended next step

State one concrete next action.

Human review of the navigation/docs change set, then commit on an agreed `chore/` branch when authorised.

## Git status

Paste or summarise the final status.

```text
# illustrative — run git status at handoff time
```

No commit or push should be performed unless explicitly authorised.
