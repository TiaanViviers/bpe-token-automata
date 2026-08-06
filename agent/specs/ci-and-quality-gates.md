# CI and Quality Gates

Private engineering specification for Phase 1 GitHub Actions quality gates.

Workflow source: [`.github/workflows/checks.yml`](../../.github/workflows/checks.yml).

The GitHub main branch is protected by a ruleset requiring pull requests and the three CI quality gates.

This document does not replace repository settings. Configuring the `main`
ruleset / required status checks is a separate human operations step.

## Purpose

GitHub Actions on this repository exists to:

* protect `main` from unreviewed or broken integration;
* detect cheap regressions before merge;
* validate reproducibility from the locked `project/` environment;
* validate that the standalone `project/` subtree export installs and checks
  independently.

It does **not** prove that a marker’s machine is identical to CI. The ordinary
checks workflow does not publish to GitLab; controlled publication is isolated
in the manual [`Publish project to GitLab`](../../.github/workflows/publish-gitlab.yml)
workflow and documented in the
[`GitLab publication workflow`](../workflows/gitlab-publication.md).

## Current required PR jobs

Exact job identifiers (stable names for the future `main` ruleset):

```text
branch-name
quality
submission-export
```

Do not rename these casually. Do not reuse these IDs in another workflow.

## Trigger behaviour

The `Checks` workflow runs on:

* pull requests targeting `main`;
* pushes to `main`;
* manual `workflow_dispatch` runs.

It does **not** use `pull_request_target`.

Concurrency cancels outdated runs for the same workflow and ref.

## What each job proves

### `branch-name`

Enforces the collaborative branch-naming convention on pull-request source
branches:

```text
^(feature|fix|test|docs|experiment|research|ci|chore)/[a-z0-9]+(-[a-z0-9]+)*$
```

(Bash ERE form of the project convention; equivalent to the PCRE non-capturing
variant with `(?:…)`.)

On pushes to `main` (and other non-PR events), the job passes without applying
the feature-branch regex.

### `quality`

Checks out the monorepo, installs Python 3.12 via `uv` from `project/uv.lock`
(`uv sync --frozen`), and runs:

```bash
make check
```

That currently covers format verification, Ruff lint, mypy, and pytest from
`project/`.

### `submission-export`

Validates the **exact checked-out commit** as a standalone exported project:

1. full-history checkout (`fetch-depth: 0` for `git subtree split`);
2. build local `submission` via `./scripts/build_submission.sh`;
3. verify via `./scripts/verify_submission.sh`;
4. extract with `git archive` into a clean temporary directory;
5. run `uv sync --frozen` and `make check` from that export root;
6. upload `bpe-token-automata-submission.tar.gz` as artifact
   `validated-submission` (short retention; not a release).

Dirty-tree handling: the subtree is built **before** dependency install in this
job so the default clean-tree safety of the export script remains intact.

Pull-request checkout: Actions tests GitHub’s merge commit of the PR into
`main`. The export job uses that same commit — it does not fetch or export an
unrelated `main` tip.

## What does not run in ordinary PR CI

Ordinary PR / `main` CI stays lightweight. It does **not** run:

* full-scale experiments;
* one-minute or ten-minute timeout studies;
* large dictionary builds;
* expensive exhaustive verification campaigns;
* final benchmark campaigns;
* GitLab publication.

## Future tiers

Mentioned for planning only — **not** implemented in Phase 1:

```text
manual full-verification workflow
GitLab clean-environment CI
long experiment runners
```

## Manual GitLab publication

GitLab publication is deliberately not a required PR check and never runs on a
push or pull request. The separate manual workflow accepts only GitHub `main`,
repeats the export verification and standalone project checks, and pushes only
the generated publication commit using a dedicated GitLab SSH credential. The
publication commit has exactly the verified subtree tree, retains subtree
history as a parent, and descends from the fetched GitLab tip so the update is
a normal fast-forward to protected `main`.

The publication job is not evidence that ordinary CI passed for a different
commit: it validates the exact `main` commit selected for the manual run.

## Limitations

* GitHub Actions does not prove a human marker’s machine matches CI.
* Passing CI does not replace partner review or formal source fidelity.
* The uploaded submission artifact is a CI convenience only; it is not an
  official release and must not be pushed to GitLab outside the controlled
  publication process.
* Action major-version upgrades and ruleset wiring remain follow-up work.
