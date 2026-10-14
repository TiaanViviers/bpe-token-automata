# Quality Gates

Private engineering specification for project validation.

## Current status

No CI configuration is currently tracked in `26455900-CS345/`. The present quality contract is local and is run from the assessable repository itself. GitLab CI may be added later if explicitly approved; it must operate directly on this repository and must not recreate export or publication jobs.

## Purpose

Quality gates provide repeatable evidence that:

- formatting is stable;
- static analysis passes;
- type checking passes;
- tests pass;
- the locked development environment remains usable;
- changes satisfy any additional ticket-specific correctness requirements.

Passing checks does not replace formal-source fidelity, independent testing, or human review.

## Standard commands

From the workspace root:

```bash
cd 26455900-CS345
make install
make check
```

`make check` is the minimum expected validation before handoff for ordinary source changes. It currently runs:

```text
format-check → lint → typecheck → test
```

The corresponding focused commands are:

```bash
make format-check
make lint
make typecheck
make test
```

`make format` modifies files and should be used deliberately.

## Environment and reproducibility

The project targets Python 3.12+ and uses `uv.lock`. Use the locked environment rather than silently changing dependency versions.

A clean-environment check should use:

```bash
uv sync --frozen
make check
```

If the current `make install` target uses non-frozen `uv sync`, do not claim that running it alone proves lockfile reproducibility.

## Change-specific evidence

The standard gate is necessary but may be insufficient. Tickets may also require:

- focused regression tests;
- bounded exhaustive checks with declared bounds;
- differential or property tests with recorded seeds;
- automata equivalence checks;
- deterministic serialization checks;
- benchmark smoke tests;
- documented timeout or memory limits.

Use [`../rules/testing-and-correctness.md`](../rules/testing-and-correctness.md) to select independent evidence.

## Handoff reporting

Record exact commands and outcomes. Distinguish:

- passed;
- failed;
- timed out;
- not run;
- not applicable.

Do not report `make check` as passed when only focused tests ran. Do not omit failures.

## Future CI

If GitLab CI is introduced, its ordinary pipeline should run on commits to this repository and reproduce the local quality gate from the repository root. It should not require branch-name checks, pull-request jobs, subtree splitting, submission archives, publication commits, special remotes, or repository synchronisation unless the human explicitly changes the workflow.

## Limitations

- Local success does not prove a marker's environment is identical.
- Tooling checks do not prove formal correctness.
- Expensive experiments and exhaustive campaigns remain separate unless a ticket requires them.
- Repository settings and server-side CI state are not documented here unless verified.

