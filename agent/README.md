# Agent Development Workspace

The `agent/` directory contains private collaborative material used to plan, guide, review, and document AI-assisted development of the BPE Token Automata project.

It is not part of the university GitLab submission.

Only content under `project/` is eligible for export through the repository’s `git subtree split` workflow.

## Navigation cheat sheet

| Need | Go here |
|---|---|
| Repository contract | [`../AGENTS.md`](../AGENTS.md) |
| CS345 project specification | [`specs/cs345-project-specification.md`](specs/cs345-project-specification.md) |
| CI / quality gates | [`specs/ci-and-quality-gates.md`](specs/ci-and-quality-gates.md) |
| Research catalogue | [`../research/index.yaml`](../research/index.yaml) · [`../research/README.md`](../research/README.md) |
| Rules | [`rules/`](rules/) |
| Feature workflow | [`workflows/feature-development.md`](workflows/feature-development.md) |
| Templates | [`templates/ticket.md`](templates/ticket.md), [`templates/handoff.md`](templates/handoff.md) |
| Example filled docs | [`tickets/TICKET-000-example-infrastructure.md`](tickets/TICKET-000-example-infrastructure.md) |
| Working tickets / handoffs | [`tickets/`](tickets/), [`handoffs/`](handoffs/) |
| Long-lived specs | [`specs/`](specs/) |
| Agent skills | [`../.agents/skills/<name>/SKILL.md`](../.agents/skills/) |

Read this full map when placing a new document. For ordinary tasks, start from the cheat sheet and the linked rule or workflow.

## Purpose

This directory exists to give human contributors and coding agents a shared development context.

It supports:

* structured planning before implementation;
* reusable development rules and workflows;
* implementation tickets;
* research-sensitive design work;
* task handoffs between humans and agents;
* reviews and quality checks;
* reusable prompts;
* long-lived engineering specifications.

Reusable Agent Skills live outside this directory at [`.agents/skills/`](../.agents/skills/).

Material here may be incomplete, exploratory, or internal. It must not be treated as automatically authoritative.

## Authority

The root-level [`AGENTS.md`](../AGENTS.md) defines the repository-wide operating contract.

The canonical source-authority order is defined in the root [`AGENTS.md`](../AGENTS.md).
Do not reproduce or redefine it here.

Agent-generated documents must not silently override formal sources or approved decisions.

## Directory map

```text
agent/
├── README.md
├── specs/
├── rules/
├── workflows/
├── templates/
├── tickets/
├── handoffs/
├── plans/
├── reviews/
└── prompts/
```

Agent Skills are not stored under `agent/`. They live at repository-root
[`.agents/skills/`](../.agents/skills/).

Some directories may remain empty until the corresponding workflow is introduced.

## `specs/`

Contains long-lived engineering specifications and pointer documents for external authoritative sources.

Current entries:

* [`cs345-project-specification.md`](specs/cs345-project-specification.md) — pointer to the official course specification (Markdown default; PDF verify-only)
* [`ci-and-quality-gates.md`](specs/ci-and-quality-gates.md) — Phase 1 GitHub Actions jobs (`branch-name`, `quality`, `submission-export`)

Examples of specifications that may be added later:

* engineering interpretation of the project specification;
* system architecture;
* domain model;
* testing strategy;
* experiment framework;
* documentation strategy;
* extension evaluation.

Specifications describe what the system should do and how major components fit together.

They should be:

* human-reviewed;
* version controlled;
* explicit about uncertainty;
* updated when approved architecture changes;
* referenced by tickets and implementation plans.

Do not create speculative specifications merely to fill the directory.

When a formal testing strategy is created, it should live under `agent/specs/`.

## `rules/`

Contains stable development constraints that apply repeatedly.

Current rules:

* [`git-and-branches.md`](rules/git-and-branches.md)
* [`research-sources.md`](rules/research-sources.md)
* [`testing-and-correctness.md`](rules/testing-and-correctness.md)

Rules describe constraints such as:

* what agents may do;
* how Git operations are controlled;
* how research sources are interpreted;
* what correctness evidence is expected;
* what material may enter `project/`.

Rules should remain narrower than the root `AGENTS.md`.

They must not duplicate large sections of repository-wide instructions unnecessarily.

## `workflows/`

Contains repeatable project-specific procedures.

Current workflow:

* [`feature-development.md`](workflows/feature-development.md)

Future workflows may include bug fixing, paper analysis, architecture decisions, experiment development, pull-request review, and GitLab release preparation.

A workflow describes how to perform a recurring class of task from beginning to end.

Rules define constraints.

Workflows define procedures.

## `templates/`

Contains standard document structures.

Current templates:

* [`ticket.md`](templates/ticket.md)
* [`handoff.md`](templates/handoff.md)

Templates should be copied into the appropriate working directory and completed for a specific task.

Do not edit the canonical template to record task-specific information.

Future templates may include architecture decision records, research notes, experiment plans, review reports, and bug reports.

## `tickets/`

Contains bounded units of approved or proposed work in a flat directory:

```text
agent/tickets/
```

Ticket state is recorded in the ticket document `Status` field, not by moving files between lifecycle directories.

A ticket should define:

* goal;
* background;
* authoritative sources;
* scope;
* non-goals;
* proposed design;
* acceptance criteria;
* required tests;
* documentation changes;
* risks;
* open questions;
* definition of done.

Theory-sensitive implementation should not begin from a vague request when a formal ticket is required.

Ticket identifiers should be stable.

Example:

```text
TICKET-004-dictionary-parser.md
```

Moving a ticket to `done` status requires human review.

## `handoffs/`

Contains durable task-state summaries.

A handoff should record:

* what was requested;
* what was completed;
* files changed;
* sources consulted;
* decisions made;
* tests added;
* commands run;
* validation results;
* unresolved questions;
* known risks;
* recommended next step;
* final Git status.

Handoffs allow another agent or human to resume work without relying on chat history.

A handoff must not claim that unperformed validation succeeded.

Suggested organisation:

```text
handoffs/
└── TICKET-004/
    ├── 2026-08-01-codex-implementation.md
    └── 2026-08-02-human-review.md
```

## `plans/`

Contains temporary or intermediate planning documents that are broader than a ticket but not yet approved specifications.

Examples:

* milestone decomposition;
* proposed architecture alternatives;
* implementation sequencing;
* migration plans;
* refactoring proposals.

Plans are working material.

Once a plan becomes an approved long-lived decision, the relevant parts should be promoted into:

* `specs/`;
* a formal architecture decision;
* a ticket;
* or submission-safe documentation under `project/docs/`.

Do not treat an abandoned plan as current architecture.

## `reviews/`

Contains structured reviews of:

* code changes;
* implementation plans;
* research interpretations;
* experiment designs;
* architecture proposals;
* documentation;
* submission readiness.

Reviews should distinguish:

* blocking issues;
* correctness risks;
* design concerns;
* optional improvements;
* follow-up suggestions.

A review should reference the exact commit, branch, ticket, diff, or document being reviewed.

## `prompts/`

Contains reusable prompt material that does not qualify as a skill or formal workflow.

Examples:

* one-off agent handover prompts;
* review prompts;
* research investigation prompts;
* repository setup prompts;
* migration prompts.

Avoid storing raw chat transcripts without a clear future use.

Prompts should state:

* intended task;
* required context;
* constraints;
* expected output;
* prohibited actions.

Reusable procedural prompts should eventually be promoted into
[`.agents/skills/`](../.agents/skills/) or [`workflows/`](workflows/).

## Skills

Reusable agent skills for recurring procedures live at:

```text
.agents/skills/<skill-name>/SKILL.md
```

Example:

```text
.agents/skills/grill-me/SKILL.md
```

Clarifications:

* `.agents/skills/` is the canonical location for project Agent Skills;
* `.agents/` is private collaborative material and must not enter the GitLab
  export (see root [`AGENTS.md`](../AGENTS.md) and
  [`rules/git-and-branches.md`](rules/git-and-branches.md));
* root `skills-lock.json` pins installed skill content hashes and is likewise
  private;
* skills are reusable procedures, not stores of project facts;
* skills should not duplicate authoritative rules or specifications — they
  should point to those sources when necessary;
* this `agent/` directory no longer contains a `skills/` subtree.

## Document lifecycle

Use the following progression where appropriate:

```text
idea
  ↓
plan
  ↓
research or design work
  ↓
approved specification or ticket
  ↓
implementation
  ↓
handoff
  ↓
review
  ↓
merged code and formal documentation
```

Not every small task requires every stage.

Use process proportional to risk:

* small changes may need only a concise plan and validation;
* medium changes usually require a ticket and handoff;
* formal or architectural work should include research, design approval, testing strategy, and review.

## Creating new documents

Before adding a document, determine its correct category.

Ask:

* Is this a stable rule?
* Is this a repeatable workflow?
* Is this a long-lived specification?
* Is this a bounded task?
* Is this temporary planning?
* Is this a record of completed work?
* Is this a review?
* Is this a reusable skill (then place it under `.agents/skills/`, not here)?

Do not create multiple documents containing the same authority.

Prefer links to canonical files over copied instructions.

## Naming conventions

Use lowercase kebab-case for general Markdown files:

```text
domain-model.md
feature-development.md
```

Use stable uppercase identifiers for tickets where useful:

```text
TICKET-001-reference-tokenizer.md
```

Use ISO-style dates in handoffs and dated notes:

```text
2026-08-01-codex-implementation.md
```

Avoid vague names such as:

```text
notes.md
latest.md
new-plan.md
final-final.md
```

## Agent working expectations

Before using this directory, an agent should:

1. read the root [`AGENTS.md`](../AGENTS.md);
2. inspect Git status and current branch;
3. identify the relevant ticket or request;
4. read applicable rules and workflows;
5. inspect recent handoffs;
6. consult authoritative research sources where required;
7. produce a plan before non-trivial implementation;
8. remain within approved scope;
9. run relevant validation;
10. produce a handoff.

Agents must not commit, push, merge, rebase, switch branches, or modify remotes without explicit human approval.

## Submission safety

Nothing under `agent/` should enter the exported GitLab repository.

Do not copy private agent material into `project/`.

When internal reasoning needs to become part of the formal submission, rewrite it as human-reviewed technical documentation under an appropriate `project/` path.

The resulting document must:

* stand on its own;
* use formal terminology correctly;
* cite original sources;
* match the implementation;
* exclude private prompt or agent-process context.

## Current setup status

The private agent workspace currently provides:

* repository-wide guidance through `AGENTS.md`;
* navigation cheat sheets in `AGENTS.md` and this README;
* a pointer to the official CS345 project specification;
* detailed Git rules;
* research-source rules;
* testing and correctness rules;
* a feature-development workflow;
* ticket and handoff templates plus an example ticket/handoff pair;
* Cursor rule adapters under `.cursor/rules/`;
* tailored Agent Skills under `.agents/skills/`.

Research indexing and paper-conversion documentation will be completed after the initial Marker conversion process is stable.

A root human-facing README remains a non-blocking future decision while the repository is private.
