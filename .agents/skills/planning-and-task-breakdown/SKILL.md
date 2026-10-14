---
name: planning-and-task-breakdown
description: >
  Create dependency-aware implementation tickets from an approved specification
  or design. Use when medium or large work needs bounded scope, non-goals,
  acceptance criteria, independent test requirements, risks, and documentation
  tasks before implementation. Trigger phrases include "break this into
  tickets", "task breakdown", and "plan the implementation". Do not use to
  implement the tickets.
---

# Planning and Task Breakdown

Decompose approved work into bounded, dependency-aware tickets. Planning is
read-only with respect to `26455900-CS345/` source: the outputs are tickets (and
optionally a short plan note), not implementation.

## When to use

* An approved specification, design, or concrete human-approved requirements
  exists
* Work is too large or vague to start safely
* Implementation order or parallelism is unclear

**When not to use:** single-file obvious edits, or when a single existing ticket
already defines the work.

## Inputs

Prefer, in order:

1. an approved engineering spec under `agent/specs/`;
2. an approved design / decision record;
3. sufficiently concrete human-approved requirements.

Follow the canonical source-authority order in `@AGENTS.md`.

Read `@agent/workflows/feature-development.md` for sequencing expectations.

## Template and output location

Use `@agent/templates/ticket.md`.

Write tickets under the flat directory:

```text
agent/tickets/
```

Filename convention:

```text
TICKET-XXX-<short-description>.md
```

Example:

```text
agent/tickets/TICKET-004-dictionary-parser.md
```

Do **not** assume GitHub Issues or another external issue tracker.

Do **not** write plans or tickets under `26455900-CS345/`.

Optional broader sequencing notes may go under `agent/plans/` if useful. Prefer
tickets as the actionable artefacts.

## Planning process

### 1. Read-only survey

* Read the approved spec/design and relevant code/tests
* Identify authoritative sources
* Map dependencies
* Note risks and blocking questions
* **Do not implement**

### 2. Dependency graph and tracer-bullet sequence

Order work so foundations come first and each step leaves a reviewable state.
Prefer a useful tracer-bullet / vertical-slice sequence over purely horizontal
layering when that yields earlier semantic evidence.

Avoid tiny bureaucratic tickets for trivial edits — fold small related edits
into a coherent ticket instead.

### 3. Write tickets

Each ticket should include, via the template:

* goal, background, authoritative sources;
* scope and non-goals;
* proposed design outline;
* acceptance criteria;
* independent test evidence requirements
  (`@agent/rules/testing-and-correctness.md`);
* documentation changes;
* validation commands (ordinarily `cd 26455900-CS345 && make check`);
* risks;
* blocking open questions;
* definition of done.

### 4. Checkpoints

After groups of related tickets, note a human review checkpoint before large
follow-on work.

## Stop condition

Stop after the plan/tickets are written and open questions are listed.

Do **not** implement the tickets in this skill.

Git commit/push remains separately authorised — `@agent/rules/git-and-branches.md`.
