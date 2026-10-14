# Git and Repository Rules

## Purpose

This document defines the simple Git workflow for the assessable project and protects the boundary around private AI support material.

## Only Git repository

The only real Git repository is:

```text
~/Projects/automata_345/26455900-CS345/
```

Start from the workspace root when private context is useful, but use an explicit repository target:

```bash
git -C 26455900-CS345 status
git -C 26455900-CS345 branch --show-current
git -C 26455900-CS345 log --oneline -5
```

Alternatively, `cd 26455900-CS345` before running Git commands.

Never run Git commands from `~/Projects/automata_345`, initialise a repository there, or treat stale root-level metadata as authoritative.

## Branch model

`main` is the normal and only working branch.

Do not create feature branches, ticket branches, submission branches, publication branches, pull requests, or merge requests unless the human explicitly requests an exception. Do not resurrect the former development-repository/subtree-publication model.

Before editing, confirm the actual repository is on `main`. If it is not, report the state rather than switching silently.

## Normal workflow

When the request authorises the corresponding Git writes, work directly in the repository:

```bash
cd 26455900-CS345
git status
git add <files>
git commit -m "<message>"
git push origin main
```

Use `git pull --ff-only origin main` only when updating from the remote is required and authorised. Do not create merge commits as a side effect of pulling.

The configured university GitLab remote is `origin`. Special publication remotes and push refspecs are obsolete.

## Agent permissions

Agents may inspect status, logs, tracked files, remotes, and diffs without separate approval.

A human request to stage, commit, pull, or push authorises only the Git operations reasonably needed for that request. Otherwise, leave changes unstaged and uncommitted.

Separate explicit direction is required for destructive or repository-administration operations, including:

- force-pushing or rewriting shared history;
- resetting or discarding changes;
- changing remotes or credentials;
- changing repository settings;
- deleting branches or tags.

Never force-push `main`. Never place credentials in files, remote URLs, command arguments, issues, handoffs, or chat.

## Commit policy

Commits should be coherent, explainable, and limited to the requested scope. Prefer descriptive messages such as:

```text
feat(dictionary): validate merge dependencies
test(dfa): add self-merge regression cases
fix(serialization): sort transitions deterministically
docs(research): record Unicode symbol policy
```

Avoid vague messages such as `update`, `fix stuff`, `agent changes`, or `final`.

Before committing:

- run relevant checks;
- inspect `git status` and `git diff`;
- stage explicit paths, not unrelated changes;
- confirm no credentials, private workspace material, caches, or generated junk entered the repository;
- ensure the commit can be understood without chat history.

## Private workspace boundary

These workspace-root paths remain outside GitLab:

```text
AGENTS.md
agent/
research/
scripts/
skills-lock.json
.agents/
.codex/
```

The assessable repository may contain its own project-owned paths with similar generic names only when they are legitimate project content. Do not bulk-copy workspace directories into it.

There is no export verifier now because there is no export. Boundary safety comes from making all project edits directly under `26455900-CS345/`, reviewing `git status` and `git diff --cached`, and staging explicit files.

## Pre-existing changes

Never assume the working tree is disposable. When unrelated changes exist:

- identify and preserve them;
- avoid editing or staging them;
- report them in the handoff;
- ask for direction only if they block the requested work.

Do not use blanket cleanup commands to make the tree appear clean.

## Conflicts and remote divergence

When a conflict occurs, identify the intent on both sides, consult the relevant source or approved decision, preserve semantics, rerun tests, and document non-obvious resolutions.

Do not choose silently between conflicting formal interpretations. Do not use force or history rewriting to bypass divergence. Report the state and obtain direction when a safe fast-forward workflow is not possible.

## Before push

Immediately before an authorised push:

1. confirm the current directory/repository is `26455900-CS345/`;
2. confirm the branch is `main`;
3. inspect the final commit and status;
4. confirm relevant validation passed;
5. push with `git push origin main`;
6. report the pushed commit and any remaining local changes.

No publication, synchronisation, or second-repository verification step is required.

