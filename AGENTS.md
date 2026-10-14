# AGENTS.md

Workspace-wide operating contract for the **BPE Token Automata** CS345 project.

This file is the entry point for humans and coding agents. Detailed policies live under [`agent/`](agent/README.md).

## Workspace and repository boundary

The workspace root is `~/Projects/automata_345`. Agents should start there so they can use the private planning and research context.

```text
automata_345/
├── 26455900-CS345/   # assessable project; only real Git repository
├── agent/            # private AI workflow material
├── research/         # private research corpus
├── AGENTS.md         # this contract
└── skills-lock.json  # private skill metadata
```

`26455900-CS345/` is the Stellenbosch University GitLab checkout and the only directory that is version controlled. Development, project documentation, tests, and Git history live directly in it.

Everything alongside it is private local infrastructure. Never copy or commit these workspace-level paths into `26455900-CS345/` unless the human explicitly requests a specific promotion:

```text
AGENTS.md
agent/
research/
scripts/
skills-lock.json
.agents/
.codex/
```

Do not run Git commands from the workspace root, treat it as a Git repository, or initialise a repository there. Ignore any stale or incidental root-level Git metadata. Use one of these explicit forms:

```bash
git -C 26455900-CS345 status

# or
cd 26455900-CS345
git status
```

Do not use subtree exports, publication commits, synchronisation repositories, generated submission branches, special publication remotes, feature branches, pull requests, or merge requests unless the human explicitly reintroduces one for a particular task.

## Navigation

| Need | Go here |
|---|---|
| Agent workspace map | [`agent/README.md`](agent/README.md) |
| Project specification | [`agent/specs/cs345-project-specification.md`](agent/specs/cs345-project-specification.md) |
| Quality gates | [`agent/specs/ci-and-quality-gates.md`](agent/specs/ci-and-quality-gates.md) |
| Git rules | [`agent/rules/git-and-branches.md`](agent/rules/git-and-branches.md) |
| Research discipline | [`agent/rules/research-sources.md`](agent/rules/research-sources.md) |
| Testing and correctness | [`agent/rules/testing-and-correctness.md`](agent/rules/testing-and-correctness.md) |
| Development workflow | [`agent/workflows/feature-development.md`](agent/workflows/feature-development.md) |
| Ticket and handoff templates | [`agent/templates/`](agent/templates/) |
| Project-specific agent skills | [`.agents/skills/`](.agents/skills/) |
| Cursor adapters | [`.cursor/rules/`](.cursor/rules/) |
| Assessable project | [`26455900-CS345/`](26455900-CS345/) |

## Project overview

The project studies byte pair encoding tokenization using formal-language and automata-theoretic methods.

Required work eventually includes dictionary parsing and validation, an independent reference tokenizer, baseline and compact token automata, a string-to-tokenization transducer, rigorous testing, reproducible experiments, and approved extensions.

Formal correctness, reproducibility, independent verification, and human understanding are primary requirements. Passing a few examples is not sufficient.

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

Existing code and tests are evidence, not higher authority than formal sources. Surface conflicts instead of silently reconciling them. Other documents should link here rather than reproduce this list.

## Required initial inspection

Before meaningful work, start at the workspace root and inspect the actual repository explicitly:

```bash
git -C 26455900-CS345 status
git -C 26455900-CS345 branch --show-current
git -C 26455900-CS345 log --oneline -5
```

Also identify the request or ticket, read applicable rules and workflows, inspect recent relevant handoffs, locate authoritative sources, bound the scope, and report pre-existing changes that overlap the task.

## Working-directory discipline

Use the workspace root to read `AGENTS.md`, `agent/`, and `research/`. Execute project commands and make project changes inside `26455900-CS345/`:

```bash
cd 26455900-CS345
make install
make check
make test
make lint
make format-check
make typecheck
make format
```

For ordinary source changes, `make check` is the minimum expected validation before handoff.

## Git workflow

`main` is the normal working branch. Do not create or switch to feature, ticket, publication, or submission branches unless explicitly asked.

When the human authorises the relevant Git write operations, the normal sequence from `26455900-CS345/` is:

```bash
git status
git add <files>
git commit -m "<message>"
git push origin main
```

Git inspection is always allowed. Staging, committing, pulling, pushing, rewriting history, changing remotes, or changing repository settings requires an explicit request for that Git action. Never force-push, discard unrelated work, or expose credentials. See [`agent/rules/git-and-branches.md`](agent/rules/git-and-branches.md).

## Scope and correctness

Implement only the approved task. Do not broaden scope, add speculative abstractions, or silently resolve formal ambiguity.

For theory-sensitive work, identify the exact definition or algorithm, preserve source terminology, state deviations explicitly, and do not use the implementation as its only correctness oracle.

Use Markdown conversions for search and initial reading. Verify fidelity-sensitive details against original PDFs before encoding implementation decisions. Formal documentation must cite the original publication. See [`agent/rules/research-sources.md`](agent/rules/research-sources.md) and [`agent/rules/testing-and-correctness.md`](agent/rules/testing-and-correctness.md).

## Documentation boundary

- `agent/` contains private process material.
- `research/` contains private source material and notes.
- `26455900-CS345/docs/` contains assessable technical documentation.

When private reasoning needs to become project documentation, rewrite only the relevant, human-reviewed technical content under `26455900-CS345/`. Do not copy prompts, handoffs, private notes, or PDFs into the repository.

## Definition of done

A meaningful implementation task is complete only when:

- approved scope is implemented against the relevant formal definitions;
- important assumptions and invariants are documented;
- suitable independent tests exist and relevant checks pass;
- required documentation is updated;
- no unrelated changes or private workspace material entered `26455900-CS345/`;
- both partners can explain the work;
- a clear handoff exists where the process requires one;
- outstanding human review is reported honestly.

## Prohibited actions

Do not:

- expose credentials, tokens, private keys, or `.env` contents;
- treat any directory other than `26455900-CS345/` as the project Git repository;
- copy private workspace infrastructure into the assessable repository without explicit instruction;
- recreate the retired export/publication workflow;
- create branches, pull requests, or merge requests unless explicitly asked;
- implement formal algorithms from memory or unverified summaries alone;
- silently resolve contradictions between sources;
- hide timeouts, memory failures, unsupported inputs, or failed experiments;
- fabricate validation, benchmark, citation, approval, or implementation results;
- weaken correctness checks merely to pass;
- redistribute copyrighted research papers without checking rights;
- perform destructive Git operations or expand beyond approved scope.

When instructions conflict, stop and identify the conflict clearly.
