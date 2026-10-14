# Development Workflow

## Purpose

This workflow applies to medium or large implementation changes. Small documentation or configuration fixes may use a lighter version while keeping scope and validation clear.

All project work occurs directly in `26455900-CS345/` on `main`. The workspace root supplies private context only.

## 1. Confirm readiness

Identify:

- the requested outcome and approved scope;
- the relevant ticket, if one exists;
- formal definitions and source sections;
- unresolved design decisions;
- expected test evidence;
- likely files.

Theory-sensitive work is ready only when its scope, non-goals, sources, testable acceptance criteria, and blocking ambiguities are clear.

## 2. Inspect context and repository state

From the workspace root, read `AGENTS.md`, applicable rules, the ticket, recent handoffs, relevant research, code, and tests.

Inspect the real repository explicitly:

```bash
git -C 26455900-CS345 status
git -C 26455900-CS345 branch --show-current
git -C 26455900-CS345 log --oneline -5
```

The branch should be `main`. Report overlapping pre-existing changes before editing. Do not create or switch branches unless explicitly asked.

## 3. Plan the change

For non-trivial work, cover:

- current understanding;
- modules involved;
- data structures and invariants;
- algorithmic steps;
- error behaviour;
- independent test strategy;
- documentation changes;
- risks and non-goals.

For formal algorithms, identify the governing paper section or specification clause. Surface unresolved ambiguity before encoding an assumption.

## 4. Implement narrowly

Make project changes only under `26455900-CS345/`. Prefer small, coherent increments such as:

1. domain types or interfaces;
2. deterministic fixtures;
3. focused tests;
4. minimal implementation;
5. special cases;
6. differential, property, or equivalence evidence;
7. technical documentation;
8. cleanup within scope.

Avoid speculative rewrites. Keep semantic decisions separate from representation optimisation where practical.

## 5. Validate continuously

Run focused checks from the project repository:

```bash
cd 26455900-CS345
uv run pytest tests/path/to/relevant_test.py
uv run mypy src tests
uv run ruff check .
```

Before handoff for ordinary source changes:

```bash
make check
```

A ticket may require additional exhaustive, equivalence, or benchmark commands. Report timeouts, unsupported cases, and failures honestly.

No subtree build, submission export, or cross-repository publication verification is required.

## 6. Review the project diff

From `26455900-CS345/`, inspect:

```bash
git status
git diff
```

Check for accidental scope expansion, unrelated formatting, private workspace files, generated artefacts, missing tests or documentation, nondeterministic output, silent fallback behaviour, and correlated implementation/oracle logic.

## 7. Produce a handoff

Use [`../templates/handoff.md`](../templates/handoff.md) when a durable handoff is appropriate. Record scope, files, sources, decisions, tests, commands, actual outcomes, questions, risks, pre-existing changes, and the repository's final Git status.

Do not call work complete when required evidence or review remains outstanding.

## 8. Human review

The reviewer should compare the diff with the request or ticket, verify formal-source agreement, challenge assumptions, inspect test independence, review validation, and confirm that the change is explainable.

Material changes after review require renewed review.

## 9. Commit and push when requested

Staging, committing, and pushing are not automatic consequences of implementation. When the human requests them, use coherent commits directly on `main`:

```bash
cd 26455900-CS345
git status
git add <files>
git commit -m "<message>"
git push origin main
```

Stage only intended project files. Do not create a branch, pull request, merge request, submission branch, or publication commit.

## 10. Close the task

After completion:

- update the ticket `Status` when applicable;
- record deliberately deferred work;
- keep long-lived project documentation consistent;
- confirm `main` and the working tree are in the reported state;
- leave private AI support material outside the repository.

Passing checks cannot resolve a formal ambiguity by itself.

