# Handoff: <Task or ticket title>

## Task

- Ticket:
- Repository: `26455900-CS345/`
- Branch: `main` unless explicitly approved otherwise
- Agent or contributor:
- Date:
- Scope:

## Status

```text
complete | partially complete | blocked | ready for review
```

Explain the current state in a few sentences. Do not include planned work as though it were completed.

## Summary of work

Describe what was actually changed.

## Files changed

Use paths relative to the workspace root:

```text
26455900-CS345/path/to/file
agent/path/to/private-file
```

For each important file, briefly state its role and make the private/project boundary clear.

## Sources consulted

- Project specification:
- Papers and sections:
- Approved decisions:
- Existing documentation:

State whether converted Markdown and/or original PDFs were checked.

## Decisions made

Record decisions affecting semantics, interfaces, representations, error handling, tests, performance, or documentation. Distinguish temporary implementation choices from approved architecture.

## Assumptions and invariants

-

## Tests added or changed

### Added

-

### Modified

-

### Important cases covered

-

## Commands run

```bash
cd 26455900-CS345
make check
```

List only meaningful commands actually executed.

## Validation results

| Check | Result |
|---|---|
| Formatting | |
| Linting | |
| Type checking | |
| Unit tests | |
| Full `make check` | |
| Additional verification | |
| Private-boundary review | |

Use `passed`, `failed`, `timed out`, `not run`, or `not applicable`. Do not report success for an unrun check.

## Known limitations

-

## Unresolved questions

-

Mark each question as blocking or non-blocking.

## Risks for reviewer

Call attention to formal interpretation, edge cases, test independence, performance, documentation, compatibility, and accidental private-file inclusion.

## Pre-existing changes preserved

```text
None
```

## Recommended next step

State one concrete next action.

## Git status

Summarise the final state of the actual repository:

```bash
git -C 26455900-CS345 status --short --branch
```

State whether commits or pushes were requested and performed. Never imply that private workspace files are tracked by this repository.

