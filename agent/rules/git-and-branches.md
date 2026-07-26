# Git and Branching Rules

## Purpose

This document defines the repository's Git workflow and the permissions expected of human contributors and coding agents.

The goals are:

- preserve a clear and reviewable history;
- protect `main`;
- prevent accidental loss of work;
- keep private material outside the GitLab submission;
- ensure every meaningful change is reviewed before integration.

## Repository model

The private GitHub repository is the primary collaborative repository.

The university GitLab repository receives a filtered history generated only from:

```text
project/
```

The GitLab export is created with:

```bash
git subtree split --prefix=project
```

No one should develop directly on the generated submission branch.

## Permanent branches

The repository uses one permanent development branch:

```text
main
```

There is no permanent `dev` branch.

All meaningful work should occur on short-lived branches and return to `main` through a pull request.

## Branch naming

Use one of the following prefixes:

```text
feature/<short-description>
fix/<short-description>
test/<short-description>
docs/<short-description>
experiment/<short-description>
chore/<short-description>
research/<short-description>
```

Examples:

```text
feature/dictionary-validator
fix/self-merge-transition-copy
test/exhaustive-small-dictionaries
docs/unicode-symbol-policy
experiment/baseline-prefix-scaling
research/transducer-determinisation
```

Use lowercase words separated by hyphens.

Do not include student names, agent names, or vague labels such as:

```text
feature/stuff
fix/changes
work/latest
```

## Starting work

Before creating or using a feature branch:

```bash
git status
git branch --show-current
git log --oneline -5
git fetch origin
```

A human should confirm that:

- the current work belongs on a new branch;
- the branch starts from the intended `main` commit;
- unrelated local changes have been handled safely.

Suggested human workflow:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/<short-description>
```

Agents must not create or switch branches without explicit permission.

## Commit policy

Commits should represent coherent, explainable changes.

Prefer commit messages such as:

```text
feat(dictionary): validate merge dependencies
test(dfa): add self-merge regression cases
fix(serialization): sort transitions deterministically
docs(research): record Unicode symbol decision
```

Avoid:

```text
update
fix stuff
agent changes
final
wip
```

Each commit should ideally:

- build successfully;
- preserve relevant tests;
- avoid unrelated formatting or refactors;
- contain no credentials or private local files;
- remain understandable without agent conversation context.

Do not combine implementation, unrelated cleanup, large generated documentation, and experiment outputs in one commit.

## Agent Git permissions

Agents may perform these operations without separate approval:

- inspect `git status`;
- inspect branches and logs;
- inspect staged and unstaged diffs;
- compare branches;
- suggest branch names;
- suggest commit boundaries and messages;
- run export scripts locally without pushing.

Agents require explicit approval before:

- creating or switching branches;
- staging files;
- committing;
- amending;
- rebasing;
- merging;
- pulling with merge behaviour;
- pushing;
- force-pushing;
- deleting branches;
- modifying remotes;
- publishing to GitLab.

Destructive operations such as `git reset --hard`, force-pushes, and history rewriting require explicit human direction and a clear explanation of the impact.

## Pull requests

Each meaningful branch should return through a GitHub pull request.

A pull request should include:

- the problem being solved;
- the approved scope;
- important design decisions;
- formal sources used, where relevant;
- tests added or changed;
- validation commands and outcomes;
- known limitations;
- follow-up work that was deliberately excluded.

Before merge:

```bash
cd project
make check
```

The submission export validation workflow must also pass.

The reviewing partner should understand the change well enough to explain it independently.

## Main branch protection

When repository settings permit, configure `main` so that:

- direct pushes are blocked;
- pull requests are required;
- required CI checks must pass;
- at least one approval is required;
- stale approvals are dismissed after material changes;
- force-pushes and deletion are disabled.

Do not change branch-protection settings without both partners agreeing.

## Submission branch

The local `submission` branch is generated, not authored.

Create it using:

```bash
./scripts/build_submission.sh
./scripts/verify_submission.sh
```

Rules:

- do not edit it directly;
- do not merge it back into `main`;
- do not treat it as an ordinary development branch;
- recreate it from the intended `main` commit;
- verify it before any GitLab push.

Only a human with authorised GitLab credentials may approve publication.

## Private material

These root-level paths must remain outside the GitLab export:

```text
AGENTS.md
agent/
research/
.cursor/
.github/
scripts/          # monorepo root scripts only
```

Clarification:

- repository-root `scripts/` contains private monorepo export tooling and must not be copied into `project/`;
- a future submission-safe `project/scripts/` directory may legitimately appear as root `scripts/` after export;
- verification rejects known private infrastructure paths and monorepo export script filenames.

Private material must not be copied into `project/` merely to make it easier for an agent to find.

The export verification script is defence in depth, not a substitute for careful review.

## Handling pre-existing changes

Never assume the working tree is disposable.

When unrelated modifications are present:

- identify them;
- avoid overwriting them;
- do not stage them accidentally;
- report them in the handoff;
- ask for direction if they block the task.

Do not use blanket cleanup commands to make the repository appear clean.

## Merge conflicts

When a conflict occurs:

- identify the competing intent on both sides;
- consult the relevant human-approved design or ticket;
- preserve semantics, not merely syntax;
- rerun relevant tests;
- document non-obvious resolutions.

An agent must not choose between conflicting formal interpretations silently.

## GitLab publication

GitLab publication is a controlled release operation.

Before publication:

1. ensure `main` is the intended source;
2. ensure the working tree is clean;
3. run `make check`;
4. build the submission subtree;
5. verify forbidden content is absent;
6. test the exported project independently;
7. inspect the exported file list;
8. obtain explicit human approval;
9. push using authorised credentials.

Never add GitLab credentials to the repository.
