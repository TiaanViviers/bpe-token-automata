# Agent Development Workspace

The `agent/` directory contains private local material used to plan, guide, review, and document AI-assisted development of the BPE Token Automata project.

It is outside the assessable Git repository. The only Git repository is the sibling directory `../26455900-CS345/`.

## Navigation

| Need | Go here |
|---|---|
| Workspace contract | [`../AGENTS.md`](../AGENTS.md) |
| Project specification | [`specs/cs345-project-specification.md`](specs/cs345-project-specification.md) |
| Quality gates | [`specs/ci-and-quality-gates.md`](specs/ci-and-quality-gates.md) |
| Git rules | [`rules/git-and-branches.md`](rules/git-and-branches.md) |
| Research rules | [`rules/research-sources.md`](rules/research-sources.md) |
| Testing rules | [`rules/testing-and-correctness.md`](rules/testing-and-correctness.md) |
| Development workflow | [`workflows/feature-development.md`](workflows/feature-development.md) |
| Templates | [`templates/ticket.md`](templates/ticket.md), [`templates/handoff.md`](templates/handoff.md) |
| Tickets and handoffs | [`tickets/`](tickets/), [`handoffs/`](handoffs/) |
| Research catalogue | [`../research/index.yaml`](../research/index.yaml) |
| Project-specific skills | [`../.agents/skills/`](../.agents/skills/) |
| Cursor rule adapters | [`../.cursor/rules/`](../.cursor/rules/) |
| Assessable repository | [`../26455900-CS345/`](../26455900-CS345/) |

## Boundary and working model

Start agent sessions from the workspace root:

```text
~/Projects/automata_345
```

This keeps private context discoverable. Read `AGENTS.md`, `agent/`, and `research/` there, but target all source changes, project documentation, tests, commands, and Git operations at:

```text
26455900-CS345/
```

Never copy `agent/`, `research/`, root `AGENTS.md`, root `scripts/`, `.agents/`, `.codex/`, or `skills-lock.json` into the assessable repository unless the human explicitly requests particular content to be promoted.

There is no export or synchronisation step. The project repository is already the submission repository.

## Directory map

```text
agent/
├── README.md
├── specs/       # long-lived engineering specifications and source pointers
├── rules/       # stable constraints
├── workflows/   # repeatable procedures
├── templates/   # ticket and handoff structures
├── tickets/     # bounded work items
├── handoffs/    # durable task-state summaries
├── plans/       # temporary planning
├── reviews/     # review records
└── prompts/     # reusable prompt material
```

Some directories may remain empty until needed. Do not create placeholder documents merely to fill them.

## Authority

The workspace [`AGENTS.md`](../AGENTS.md) defines the operating contract and canonical source-authority order. Agent-generated documents do not silently override formal sources or approved human decisions.

## Specifications

Specifications describe what the system should do and how major components fit together. They should be human-reviewed, explicit about uncertainty, updated when approved decisions change, and referenced by relevant tickets.

Current entries:

- [`cs345-project-specification.md`](specs/cs345-project-specification.md) — pointer to the official course specification.
- [`ci-and-quality-gates.md`](specs/ci-and-quality-gates.md) — current local validation contract.
- [`larger-dictionary-timeouts.md`](specs/larger-dictionary-timeouts.md) — Section **5.6** realistic dictionaries and construction timeouts.
- [`experimental-evaluation.md`](specs/experimental-evaluation.md) — Section **7** measurements, method, and questions 1–6.

## Plans and approved decisions

Plans record human-approved direction before or alongside implementation tickets.

Current entries:

- [`plans/approved-extensions-2026-09.md`](plans/approved-extensions-2026-09.md) — lecturer-approved CS345 extensions **8.2** and **8.11** (2026-09-11).
- [`plans/section-5-1-dictionary-and-reference-tokenizer.md`](plans/section-5-1-dictionary-and-reference-tokenizer.md) — Section **5.1** requirements, component plan, and design decision register (approved 2026-09-11).
- [`plans/section-5-6-larger-dictionaries.md`](plans/section-5-6-larger-dictionaries.md) — Section **5.6** decision register D44–D52 (approved 2026-09-14).
- [`plans/section-6-testing-audit.md`](plans/section-6-testing-audit.md) — Section **6** test-coverage audit vs HEAD `dcedef2` (2026-09-14; not an implementation plan).
- [`plans/section-6-testing.md`](plans/section-6-testing.md) — Section **6** decision register D53–D58 (approved 2026-09-14).
- [`plans/section-7-experiments.md`](plans/section-7-experiments.md) — Section **7** decision register D59–D68 (approved 2026-09-19).

## Rules and workflows

Rules define recurring constraints. Workflows define repeatable procedures.

Current rules:

- [`git-and-branches.md`](rules/git-and-branches.md)
- [`research-sources.md`](rules/research-sources.md)
- [`testing-and-correctness.md`](rules/testing-and-correctness.md)

Current workflow:

- [`feature-development.md`](workflows/feature-development.md)

The former filtered GitLab publication workflow was retired. Do not recreate or cite it.

## Tickets

Tickets live in a flat `agent/tickets/` directory, with lifecycle state recorded in each document's `Status` field.

A ticket should define the goal, sources, scope, non-goals, design, acceptance criteria, tests, documentation, risks, questions, and definition of done. Theory-sensitive implementation should not begin from a vague request when a formal ticket is needed.

Ticket identifiers should be stable, for example:

```text
TICKET-004-dictionary-parser.md
```

## Handoffs

Handoffs record what was requested and completed, files changed, sources consulted, decisions, tests, commands and outcomes, unresolved questions, risks, the recommended next step, and the final Git status of `26455900-CS345/`.

Suggested organisation:

```text
handoffs/
└── TICKET-004/
    ├── 2026-09-07-codex-implementation.md
    └── 2026-09-08-human-review.md
```

Do not claim unperformed validation succeeded.

## Plans, reviews, and prompts

Plans are temporary proposals, not current architecture unless approved and promoted.

Reviews should distinguish blocking issues, correctness risks, design concerns, optional improvements, and follow-up suggestions. Reference the exact repository commit, ticket, diff, or document being reviewed.

Prompts should state their task, context, constraints, expected output, and prohibited actions. Avoid raw chat transcripts without a durable use.

## Document lifecycle

Use process proportional to risk:

```text
idea → plan/research → approved specification or ticket → implementation
     → handoff → review → project code/documentation
```

Small changes may require only a concise plan and validation. Formal or architectural work should include source verification, explicit design, independent testing, and review.

## Agent working expectations

Before non-trivial work:

1. read [`../AGENTS.md`](../AGENTS.md);
2. inspect `26455900-CS345/` Git status, branch, and recent log;
3. identify the request or ticket;
4. read applicable rules and workflows;
5. inspect relevant handoffs;
6. consult authoritative sources where required;
7. keep the scope bounded;
8. run relevant commands from `26455900-CS345/`;
9. review the project diff;
10. produce a handoff when appropriate.

The normal branch is `main`. Branches, pull requests, merge requests, and publication branches are not part of the default process.

## Private-to-project promotion

When internal reasoning should become assessable documentation, rewrite only the relevant technical content under an appropriate path such as `26455900-CS345/docs/`. The result must stand alone, use formal terminology correctly, cite original sources, match the implementation, and exclude private prompt or process context.

Root `skills-lock.json` and any workspace-level agent configuration remain private support metadata.

## Skills and editor adapters

Reusable project-specific skills live under `.agents/skills/`. Their procedures
must use the same workspace boundary as this document: private outputs remain at
the workspace root, while code inspection and project commands explicitly target
`26455900-CS345/`.

Cursor rules under `.cursor/rules/` are thin adapters into `AGENTS.md`, agent
rules, workflows, and skills. Keep their path globs aligned with the standalone
repository. Do not duplicate the retired publication workflow in an adapter.
