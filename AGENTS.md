# AGENTS.md

Repository-wide operating contract for the **BPE Token Automata** CS345 project.

This file is the entry point for humans and coding agents. Detailed policies live under `agent/`. Prefer links over duplicated instructions.

## Navigation cheat sheet

| Need | Go here |
|---|---|
| This contract | `AGENTS.md` (this file) |
| Agent workspace map | [`agent/README.md`](agent/README.md) |
| CS345 project specification (Markdown, default) | [`agent/specs/cs345-project-specification.md`](agent/specs/cs345-project-specification.md) → [`research/markdown/cs345-project-specification/index.md`](research/markdown/cs345-project-specification/index.md) |
| CS345 project specification (PDF, verify only) | `research/sources/cs345-project-specification.pdf` |
| CI / quality gates | [`agent/specs/ci-and-quality-gates.md`](agent/specs/ci-and-quality-gates.md) |
| Git rules | [`agent/rules/git-and-branches.md`](agent/rules/git-and-branches.md) |
| Research / citation rules | [`agent/rules/research-sources.md`](agent/rules/research-sources.md) |
| Testing / correctness rules | [`agent/rules/testing-and-correctness.md`](agent/rules/testing-and-correctness.md) |
| Feature workflow | [`agent/workflows/feature-development.md`](agent/workflows/feature-development.md) |
| GitLab publication workflow | [`agent/workflows/gitlab-publication.md`](agent/workflows/gitlab-publication.md) |
| Ticket / handoff templates | [`agent/templates/`](agent/templates/) |
| Example ticket / handoff | [`agent/tickets/TICKET-000-example-infrastructure.md`](agent/tickets/TICKET-000-example-infrastructure.md) |
| Agent skills | [`.agents/skills/`](.agents/skills/) |
| Git write skill | [`.agents/skills/git-ops/SKILL.md`](.agents/skills/git-ops/SKILL.md) |
| Submission-safe code | `project/` |

## Project overview

The project studies byte pair encoding tokenization using formal-language and automata-theoretic methods.

Required work eventually includes dictionary parsing and validation, an independent reference tokenizer, baseline and compact token automata, a string-to-tokenization transducer, rigorous testing, reproducible experiments, and approved extensions.

Formal correctness, reproducibility, independent verification, and human understanding are primary requirements. Passing a few examples is not sufficient.

## Repository structure

Private collaborative GitHub monorepository:

```text
bpe-token-automata/
├── AGENTS.md          # this contract
├── project/           # only GitLab-exportable subtree
├── agent/             # private agent workspace
├── .agents/           # private Agent Skills (Codex/Cursor discovery)
├── research/          # papers, conversions, notes
├── scripts/           # monorepo export tooling
├── .cursor/           # Cursor rule adapters
└── .github/           # GitHub CI and collaboration
```

| Path | Role |
|---|---|
| `project/` | Submission-safe installable project root after export |
| `agent/` | Rules, workflows, tickets, handoffs, specs, plans, reviews, prompts |
| `.agents/` | Private reusable Agent Skills (`SKILL.md`); not for GitLab |
| `research/` | Research sources and derived material |
| `scripts/` | Monorepo submission build/verify tooling |
| `.cursor/` | Thin Cursor adapters into `AGENTS.md` and `agent/` |
| `.github/` | Actions and pull-request templates |

There is intentionally no root `README.md` yet. Public project documentation lives in `project/README.md`. Agent navigation uses this file and `agent/README.md`.

## Submission boundary

Only `project/` may enter the university GitLab repository:

```bash
git subtree split --prefix=project
```

Private material must never appear in the export, including:

```text
AGENTS.md
agent/
.agents/
skills-lock.json  # Agent Skills installer lockfile
research/
.cursor/
.github/
scripts/          # monorepo root scripts; not submission-safe project scripts
```

A future `project/scripts/` directory may legitimately export as root `scripts/`. Monorepo export tooling under the repository-root `scripts/` must never be copied into `project/`.

Before any GitLab publication:

```bash
./scripts/configure_gitlab_remote.sh  # once per local clone
./scripts/build_submission.sh
./scripts/verify_submission.sh
```

Never bypass verification. Do not push to GitLab unless a human with required access explicitly instructs it.

For the controlled GitHub Actions release procedure and one-time credential
setup, follow [`agent/workflows/gitlab-publication.md`](agent/workflows/gitlab-publication.md).

## Canonical authority order

When sources disagree, use this order only:

1. official CS345 project specification ([pointer](agent/specs/cs345-project-specification.md); PDF authoritative, Markdown for ordinary reading);
2. original cited research-paper PDFs;
3. published errata or authoritative author clarifications;
4. explicit human-approved project decisions;
5. approved engineering specifications and architecture records;
6. verified Markdown paper conversions;
7. tests and implementation;
8. temporary plans, tickets, handoffs, reviews, and agent-generated notes.

Clarifications:

* existing code is not automatically correct;
* tests and implementation provide evidence but cannot override formal sources above them;
* temporary agent material has the lowest authority;
* conflicts must be surfaced rather than silently reconciled.

Do not reproduce or redefine this list elsewhere. Other documents must link here.

## Research principle

Use Markdown conversions for search and initial reading. Verify fidelity-sensitive material against the original PDF before encoding implementation decisions. Formal documentation must cite the original publication, not the conversion file.

For the course project specification, start at [`agent/specs/cs345-project-specification.md`](agent/specs/cs345-project-specification.md). Do not open the PDF unless verifying exact requirement wording.

Details: [`agent/rules/research-sources.md`](agent/rules/research-sources.md) and [`research/README.md`](research/README.md).

## Required initial inspection

Before meaningful work:

```bash
git status
git branch --show-current
git log --oneline -5
```

Also identify the ticket or request, read applicable rules and workflows, inspect recent handoffs, locate authoritative sources, bound the scope, and surface uncertainty before encoding assumptions.

## Scope and correctness

Implement only the approved task. Do not broaden scope, add speculative abstractions, or silently resolve formal ambiguity.

For theory-sensitive work, identify the exact definition or algorithm, preserve source terminology, state deviations explicitly, and do not use the implementation as its only correctness oracle.

Testing must provide independent evidence. Details: [`agent/rules/testing-and-correctness.md`](agent/rules/testing-and-correctness.md).

## Hard Git restrictions

Agents may inspect Git state and diffs freely.

Unless explicitly authorised, do not create or switch branches, stage, commit, amend, rebase, merge, push, force-push, delete branches, modify remotes, change repository settings, or publish to GitLab.

Authorisation for repository-legal Git write work is granted when the human
invokes [`.agents/skills/git-ops/SKILL.md`](.agents/skills/git-ops/SKILL.md)
or asks in chat to perform that Git work. Details and remaining hard stops:
[`agent/rules/git-and-branches.md`](agent/rules/git-and-branches.md).

Never commit directly to `main`. Preserve unrelated human changes.

Feature process: [`agent/workflows/feature-development.md`](agent/workflows/feature-development.md).

## Essential commands

Run from `project/` unless stated otherwise:

```bash
make install
make check
make test
make lint
make format-check
make typecheck
make format
```

For ordinary source changes, `make check` is the minimum expected validation before handoff.

## AI-assisted development

AI tools support research, planning, implementation, testing, review, documentation, and debugging. They must not replace human understanding.

Generated work must be reviewed, tested, adapted where necessary, explainable by both group members, and attributable per the project specification.

Never fabricate paper claims, benchmark results, citations, test outcomes, experiment success, implementation status, or human approval. When uncertain, state the uncertainty.

## Documentation boundary

* `agent/` — private process material (tickets, plans, handoffs, rules, reviews).
* `.agents/` — private Agent Skills procedures (and related installer metadata such as root `skills-lock.json`).
* `project/docs/` — submission-safe technical documentation.

Do not copy private agent or skills material into `project/`. Promote only human-reviewed, formally consistent documentation.

## Definition of done

A meaningful implementation task is complete only when:

* approved scope is implemented against the relevant formal definitions;
* important assumptions and invariants are documented;
* suitable independent tests exist and relevant checks pass;
* required documentation is updated;
* no unrelated changes or private material entered `project/`;
* both partners can explain the work;
* a clear handoff exists where the process requires one;
* human review and pull-request approval remain outstanding until performed.

Templates: [`agent/templates/ticket.md`](agent/templates/ticket.md), [`agent/templates/handoff.md`](agent/templates/handoff.md).

## Detailed references

| Kind | Location |
|---|---|
| Agent workspace map | [`agent/README.md`](agent/README.md) |
| CS345 project specification | [`agent/specs/cs345-project-specification.md`](agent/specs/cs345-project-specification.md) |
| CI / quality gates | [`agent/specs/ci-and-quality-gates.md`](agent/specs/ci-and-quality-gates.md) |
| Git rules | [`agent/rules/git-and-branches.md`](agent/rules/git-and-branches.md) |
| Research rules | [`agent/rules/research-sources.md`](agent/rules/research-sources.md) |
| Testing rules | [`agent/rules/testing-and-correctness.md`](agent/rules/testing-and-correctness.md) |
| Feature workflow | [`agent/workflows/feature-development.md`](agent/workflows/feature-development.md) |
| GitLab publication workflow | [`agent/workflows/gitlab-publication.md`](agent/workflows/gitlab-publication.md) |
| Ticket template | [`agent/templates/ticket.md`](agent/templates/ticket.md) |
| Handoff template | [`agent/templates/handoff.md`](agent/templates/handoff.md) |
| Example ticket | [`agent/tickets/TICKET-000-example-infrastructure.md`](agent/tickets/TICKET-000-example-infrastructure.md) |
| Agent skills | [`.agents/skills/`](.agents/skills/) |
| Git write skill | [`.agents/skills/git-ops/SKILL.md`](.agents/skills/git-ops/SKILL.md) |

Additional workflows and specifications may be added under `agent/`. Additional skills may be added under `.agents/skills/`. Do not assume nonexistent files are present.

## Prohibited actions

Do not:

* expose credentials, tokens, private keys, or `.env` contents;
* place private agent, skills, or research material under `project/`;
* push to GitLab without explicit approval;
* implement formal algorithms from memory or unverified summaries alone;
* silently resolve contradictions between sources;
* hide timeouts, memory failures, unsupported inputs, or failed experiments;
* fabricate successful validation or weaken correctness checks to pass CI;
* redistribute copyrighted research papers without checking rights;
* make the repository public, change licences, or alter branch-protection/CI security settings without agreement;
* perform destructive Git operations or expand beyond approved scope.

When instructions conflict, stop and identify the conflict clearly.
