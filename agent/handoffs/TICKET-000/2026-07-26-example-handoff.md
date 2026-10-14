# Handoff: Example — workspace navigation

> **EXAMPLE ONLY.** This shows a filled handoff. Copy [`../../templates/handoff.md`](../../templates/handoff.md) for real work.

## Task

- Ticket: [`../../tickets/TICKET-000-example-infrastructure.md`](../../tickets/TICKET-000-example-infrastructure.md)
- Repository: `26455900-CS345/`
- Branch: `main`
- Agent or contributor: example
- Date: 2026-09-07
- Scope: private workspace navigation and repository-boundary documentation

## Status

```text
ready for review
```

## Summary of work

Updated private agent guidance to distinguish the workspace root from the standalone assessable repository. The example assumes no project implementation was changed.

## Files changed

```text
AGENTS.md
agent/README.md
agent/rules/git-and-branches.md
agent/workflows/feature-development.md
agent/templates/ticket.md
agent/templates/handoff.md
```

All listed files are private workspace infrastructure and remain outside the university repository.

## Sources consulted

- Approved decision: `26455900-CS345/` is the only Git repository
- Existing documentation: prior agent workflow files
- Project specification and papers: not needed for this documentation example

## Decisions made

- Agents start from the workspace root for context.
- Project and Git commands explicitly target `26455900-CS345/`.
- Direct work on `main` is the default.
- Export, publication, feature-branch, PR, and MR procedures are retired.

## Assumptions and invariants

- Private workspace material is not copied into the repository.
- Git write operations still occur only when requested.

## Tests added or changed

None; documentation-only example.

## Commands run

```bash
test -d 26455900-CS345/.git
git -C 26455900-CS345 status --short --branch
```

## Validation results

| Check | Result |
|---|---|
| Full `make check` | not applicable |
| Path checks | passed (illustrative) |
| Private-boundary review | passed (illustrative) |

## Known limitations

This is an example, not evidence for a live task.

## Unresolved questions

None.

## Risks for reviewer

Confirm no wording suggests that workspace-level files are tracked by `26455900-CS345/`.

## Pre-existing changes preserved

```text
None (illustrative)
```

## Recommended next step

Human review of the documentation.

## Git status

```text
main; inspect live status at handoff time
```

No commit or push is implied by this example.

