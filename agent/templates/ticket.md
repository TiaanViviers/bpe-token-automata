# TICKET-XXX: <Concise title>

## Status

```text
backlog | ready | active | review | blocked | done
```

## Owner

- Human owner:
- Supporting partner:
- Agent use:

## Goal

State the concrete outcome in one or two paragraphs.

## Background

Explain why the work is needed and how it fits into the project.

## Authoritative sources

List the exact sources that govern this task.

- Project specification:
- Paper and section:
- Approved decision:
- Existing implementation/documentation:

## Scope

The ticket includes:

-

## Non-goals

The ticket explicitly excludes:

-

## Preconditions

Before implementation:

- [ ] Relevant formal definitions are understood.
- [ ] Major ambiguity has been resolved or recorded.
- [ ] Required interfaces or dependencies exist.
- [ ] `26455900-CS345/` is on `main` and its working state is understood.
- [ ] Pre-existing changes have been identified and can be preserved.

## Proposed design

Describe the data model, public interfaces, invariants, algorithmic steps, error behaviour, deterministic behaviour, and representation decisions.

For formal work, distinguish paper semantics from implementation representation.

## Files likely to change

Paths below are relative to the workspace root:

```text
26455900-CS345/src/...
26455900-CS345/tests/...
26455900-CS345/docs/...
```

This list is guidance, not permission for unrelated changes.

## Acceptance criteria

- [ ]

Criteria must be observable and testable.

## Required test evidence

### Unit tests

-

### Regression tests

-

### Differential or exhaustive tests

-

### Property or equivalence tests

-

### Negative and special cases

-

## Documentation changes

- [ ] Public API or README
- [ ] Architecture or algorithm documentation
- [ ] Decision record
- [ ] Testing documentation
- [ ] Experiment documentation
- [ ] Known limitations

State specific expected updates:

-

## Validation commands

```bash
cd 26455900-CS345
make check
```

Additional commands:

```bash
# Add exact feature-specific commands.
```

## Risks

- Formal interpretation:
- Correctness:
- Performance:
- Compatibility:
- Scope:
- Reproducibility:

## Open questions

-

Do not begin implementation while a blocking question remains unresolved.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] Relevant documentation updated.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Handoff produced where appropriate.
- [ ] Human review completed.
- [ ] Both partners can explain the implementation.

