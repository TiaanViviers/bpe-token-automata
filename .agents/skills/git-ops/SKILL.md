---
name: git-ops
description: >
  Execute repository-legal Git operations for this project: inspect state,
  create or switch branches, stage, commit, amend, rebase, merge, pull, push,
  delete local branches, and open or update GitHub pull requests. Use when the
  skill is invoked explicitly, or whenever the user asks to commit, push, open
  a PR, create a branch, rebase, amend, merge, or otherwise perform Git write
  work. Follows @agent/rules/git-and-branches.md. Does not publish to GitLab
  or change repository settings. Do not ask again for permission after this
  skill applies.
---

# Git Ops

Execute Git and GitHub PR operations that are legal under this repository's
Git rules. Invoking this skill, or asking for Git write work in chat, is the
human's explicit authorisation for those operations.

## Authority

When this skill applies:

* Treat the user's request as approval for every **repository-legal** Git
  operation needed to complete it (branch, stage, commit, amend, rebase,
  merge, pull, push, open/update PR, delete local feature branches when
  appropriate).
* Do **not** re-ask for conversational sign-off ("should I commit?", "push
  now?", "open the PR?"). Execute, then report what you did.
* Request Cursor tool permissions (`git_write`, network/`all` as needed)
  immediately; do not pause for a second chat confirmation.
* Hard stops in [safety-rails.md](safety-rails.md) still require a clearer,
  separate human instruction (GitLab publish, force-push to `main`, rewriting
  shared history, credentials, settings changes).

Canonical policy: `@agent/rules/git-and-branches.md`.
CI expectations: `@agent/specs/ci-and-quality-gates.md`.
Do not invent a competing rulebook inside this skill.

## Mandatory bootstrap

Before any mutating Git command, complete this bootstrap every time:

1. Read `@agent/rules/git-and-branches.md`.
2. If push or PR is in scope, read `@agent/specs/ci-and-quality-gates.md`.
3. If opening or updating a PR, read `@.github/pull_request_template.md`.
4. Inspect live state:

```bash
git status
git branch --show-current
git log --oneline -5
git fetch origin
git diff
git diff --cached
```

5. Note unrelated local changes and never stage or discard them by accident.

## Intent dispatch

Map the user request to a mode and follow the linked workflow:

| Mode | Trigger examples | Workflow |
|---|---|---|
| `status` | "git status", "what's on this branch" | Bootstrap only; report |
| `branch` | "make a branch", "switch to …" | [pr-workflow.md](pr-workflow.md) § Branch |
| `commit` | "commit", "commit this" | [commit-workflow.md](commit-workflow.md) |
| `push` | "push", "push this branch" | [pr-workflow.md](pr-workflow.md) § Push |
| `pr` | "open a PR", "create a pull request" | [pr-workflow.md](pr-workflow.md) § Pull request |
| `ship` | "commit and open a PR", "ship this" | commit → push → PR |
| `integrate` | "rebase on main", "merge main in", "amend" | [commit-workflow.md](commit-workflow.md) § History | 

If the request is ambiguous between modes, choose the smallest mode that
satisfies the stated goal; prefer `ship` only when the user clearly wants the
full path to a PR.

## Repository invariants (quick reference)

Reload details from the bootstrap docs. Do not contradict them.

* Permanent branch: `main` only. Never commit directly on `main`.
* Short-lived branch names must match:

```text
^(feature|fix|test|docs|experiment|research|ci|chore)/[a-z0-9]+(-[a-z0-9]+)*$
```

* Prefer conventional commit subjects (`feat(scope): …`, `fix(…): …`, …).
* Before a PR that touches `project/`, run `cd project && make check`.
* Required PR CI jobs: `branch-name`, `quality`, `submission-export`.
* Private paths (`AGENTS.md`, `agent/`, `.agents/`, `research/`, `.cursor/`,
  `.github/`, root `scripts/`, `skills-lock.json`) must not be copied into
  `project/`.
* The `submission` branch is generated; do not develop on it or merge it into
  `main`.
* Never push to GitLab unless a human with access separately and explicitly
  orders that publication.

## Output after execution

Report briefly:

* branch name and whether it tracks a remote;
* commit hashes created or rewritten (if any);
* push result;
* PR URL (if any);
* validation commands run and outcomes;
* unrelated local changes left untouched;
* any hard-stop that blocked part of the request.

## Additional resources

* [commit-workflow.md](commit-workflow.md)
* [pr-workflow.md](pr-workflow.md)
* [safety-rails.md](safety-rails.md)
