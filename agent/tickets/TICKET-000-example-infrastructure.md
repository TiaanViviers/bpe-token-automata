# TICKET-000: Example — agent infrastructure navigation

> **EXAMPLE ONLY.** This ticket documents the shape of a filled ticket. It is not active work. Do not implement from it. Copy [`../templates/ticket.md`](../templates/ticket.md) for real tickets.

## Status

```text
done
```

## Owner

- Human owner: (example)
- Supporting partner: (example)
- Agent use: documentation / navigation setup

## Goal

Provide a concrete example of a completed ticket so humans and agents can match the expected structure for future work.

## Background

The private agent workspace needs discoverable rules, workflows, and a pointer to the official CS345 project specification. This example records that kind of bounded documentation task.

## Authoritative sources

List the exact sources that govern this task.

- Project specification: [`../specs/cs345-project-specification.md`](../specs/cs345-project-specification.md) → `research/markdown/cs345-project-specification.md` (PDF verify-only)
- Paper and section: N/A for this example
- Approved decision: keep Markdown as the default agent reading format
- Existing implementation/documentation: [`../../AGENTS.md`](../../AGENTS.md), [`../README.md`](../README.md)

## Scope

The ticket includes:

- pointer document under `agent/specs/`
- navigation cheat sheets
- Cursor rule glob updates for ordinary implementation paths

## Non-goals

The ticket explicitly excludes:

- implementing tokenizer or automata algorithms
- converting research papers
- creating production skills

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] The branch and repository state are suitable.

## Proposed design

- Keep a single pointer file for the course specification.
- Agents read Markdown by default; open the PDF only for fidelity checks.
- Cursor adapters remain thin and link to canonical `agent/` docs.

## Files likely to change

```text
AGENTS.md
agent/README.md
agent/specs/cs345-project-specification.md
.cursor/rules/*.mdc
research/README.md
```

This list is guidance, not permission for unrelated changes.

## Acceptance criteria

- [x] Spec pointer exists and paths resolve.
- [x] `AGENTS.md` and `agent/README.md` include short navigation cheat sheets.
- [x] Feature and testing Cursor rules attach under normal `project/src` work paths.
- [x] Example ticket and handoff exist for format reference.

## Required test evidence

### Unit tests

- N/A (documentation / process)

### Regression tests

- N/A

### Differential or exhaustive tests

- N/A

### Property or equivalence tests

- N/A

### Negative and special cases

- N/A

## Documentation changes

- [x] Public API or README
- [ ] Architecture or algorithm documentation
- [ ] Decision record
- [ ] Testing documentation
- [ ] Experiment documentation
- [ ] Known limitations

State specific expected updates:

- Update agent navigation docs and research README with spec paths.

## Validation commands

```bash
# Path and link sanity (illustrative for this example)
test -f research/markdown/cs345-project-specification.md
test -f agent/specs/cs345-project-specification.md
```

Additional commands:

```bash
# No project/ code changes in this example.
```

## Risks

- Formal interpretation: N/A
- Correctness: N/A
- Performance: N/A
- Compatibility: Cursor glob behaviour may still miss some tasks; description matching remains a backup
- Scope: avoid turning examples into living task trackers
- Reproducibility: PDF remains local/gitignored

## Open questions

- None for this example.

Do not begin implementation while a blocking question remains unresolved.

## Definition of done

- [x] Approved scope implemented.
- [x] Acceptance criteria satisfied.
- [x] Required tests added and passing.
- [x] Relevant documentation updated.
- [ ] `make check` passes.
- [x] No private material entered `project/`.
- [x] Handoff produced.
- [ ] Human review completed.
- [x] Both partners can explain the implementation.
