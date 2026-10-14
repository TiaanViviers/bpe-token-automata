# TICKET-000: Example — workspace navigation

> **EXAMPLE ONLY.** This demonstrates a filled ticket. It is not active work. Copy [`../templates/ticket.md`](../templates/ticket.md) for real tickets.

## Status

```text
done
```

## Owner

- Human owner: (example)
- Supporting partner: (example)
- Agent use: documentation and navigation

## Goal

Document the boundary between the private AI workspace and the assessable project so future agents use the correct sources, working directory, and Git repository.

## Background

The workspace provides private rules and research next to a standalone university GitLab checkout. Agents need both contexts without copying the private material into the project.

## Authoritative sources

- Project specification: [`../specs/cs345-project-specification.md`](../specs/cs345-project-specification.md)
- Paper and section: N/A
- Approved decision: `26455900-CS345/` is the only Git repository and `main` is the working branch
- Existing documentation: [`../../AGENTS.md`](../../AGENTS.md), [`../README.md`](../README.md)

## Scope

- document the workspace/repository boundary;
- make the specification and workflow easy to find;
- show project commands running from `26455900-CS345/`.

## Non-goals

- implement tokenizer or automata algorithms;
- copy private agent or research material into the project;
- create branches, publication commits, or synchronisation tooling.

## Preconditions

- [x] Required paths are known.
- [x] The repository state was inspected.
- [x] No project implementation change is required.

## Proposed design

Keep private navigation at the workspace root, point agents to authoritative sources, and use explicit `git -C 26455900-CS345` or `cd 26455900-CS345` commands.

## Files likely to change

```text
AGENTS.md
agent/README.md
agent/rules/...
agent/workflows/...
```

## Acceptance criteria

- [x] The only repository is named explicitly.
- [x] Private paths are named explicitly.
- [x] Direct `main` commands are shown.
- [x] No export/publication workflow is required.

## Required test evidence

Documentation-only: path checks and a repository status check are sufficient for this example.

## Documentation changes

- [x] Agent navigation
- [x] Git workflow
- [x] Repository boundary

## Validation commands

```bash
test -d 26455900-CS345/.git
git -C 26455900-CS345 status --short --branch
test -f agent/specs/cs345-project-specification.md
```

## Risks

- Scope: accidentally editing project implementation during a workflow-only task
- Compatibility: agents running Git from the workspace root
- Reproducibility: claiming private files are part of the project checkout

## Open questions

None for this example.

## Definition of done

- [x] Approved scope represented.
- [x] Paths and workflow are unambiguous.
- [x] Private material remains outside the project.
- [x] Example handoff exists.
- [ ] Human review completed.

