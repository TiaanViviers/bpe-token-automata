# Feature Development Workflow

## Purpose

This workflow applies to medium or large implementation changes.

Small documentation fixes and trivial configuration corrections may use a lighter process, provided scope and validation remain clear.

## 1. Confirm readiness

Before implementation, identify:

- the requested outcome;
- the approved ticket;
- relevant formal definitions;
- unresolved design decisions;
- expected test evidence;
- files likely to change.

Do not begin theory-sensitive implementation from a vague idea alone.

A feature is ready when:

- scope is bounded;
- non-goals are stated;
- required sources are identified;
- acceptance criteria are testable;
- major ambiguities have been resolved or explicitly deferred.

## 2. Inspect repository state

Run:

```bash
git status
git branch --show-current
git log --oneline -5
```

Read:

- root `AGENTS.md`;
- the approved ticket;
- recent relevant handoffs;
- applicable rules;
- relevant code and tests;
- relevant human-approved decisions.

Report pre-existing changes before editing.

## 3. Prepare the branch

A human approves branch creation or switching.

Suggested pattern:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/<short-description>
```

Use another approved prefix where appropriate.

Do not combine unrelated tickets on one branch.

## 4. Produce an implementation plan

The plan should cover:

- current understanding;
- files or modules involved;
- data structures and invariants;
- algorithmic steps;
- error behaviour;
- test strategy;
- documentation changes;
- risks;
- explicit non-goals.

For formal algorithms, identify the paper section or specification clause being implemented.

Obtain human approval before making substantial implementation changes.

## 5. Implement in narrow increments

Prefer a sequence such as:

1. domain types or interfaces;
2. deterministic fixtures;
3. focused unit tests;
4. minimal implementation;
5. special cases;
6. differential or property tests;
7. documentation;
8. cleanup.

Avoid large speculative rewrites.

Keep semantic decisions separate from representation optimisation where possible.

## 6. Validate continuously

During implementation, run focused checks.

Examples:

```bash
cd project
uv run pytest tests/path/to/relevant_test.py
uv run mypy src tests
uv run ruff check .
```

Before handoff:

```bash
make check
```

For changes affecting exportability, also run from the repository root:

```bash
./scripts/build_submission.sh
./scripts/verify_submission.sh
```

A feature-specific ticket may require additional exhaustive, equivalence, or benchmark commands.

## 7. Review the diff

Inspect:

```bash
git status
git diff
```

Check for:

- accidental scope expansion;
- unrelated formatting;
- private files under `project/`;
- generated artefacts that should not be committed;
- missing tests;
- missing documentation;
- nondeterministic output;
- silent fallback behaviour;
- duplicated implementation and oracle logic.

Do not stage or commit unless explicitly authorised.

## 8. Produce a handoff

Use the handoff template.

The handoff should include:

- task and scope;
- status;
- files changed;
- sources consulted;
- decisions made;
- tests added;
- commands run;
- outcomes;
- open questions;
- known risks;
- recommended next step.

Do not describe work as complete when review or required evidence remains outstanding.

## 9. Human review

The human reviewer should:

- compare the diff with the ticket;
- verify formal-source agreement;
- challenge assumptions;
- inspect test independence;
- run or inspect validation;
- confirm documentation;
- confirm both partners can explain the change.

Material changes after approval require renewed review.

## 10. Commit and pull request

After approval, create coherent commits.

Open a pull request using the repository template.

The pull request should link to:

- the ticket;
- relevant research note;
- architecture decision where applicable;
- handoff;
- tests and results.

CI must pass before merge (`branch-name`, `quality`, `submission-export`; see [`../specs/ci-and-quality-gates.md`](../specs/ci-and-quality-gates.md)).

## 11. Merge and close

After merge:

- delete the feature branch when safe;
- set the ticket `Status` field to `done` (tickets stay in the flat `agent/tickets/` directory);
- record any deferred follow-up work;
- ensure long-lived documentation reflects the merged behaviour;
- verify `main` remains healthy.

Do not merge unresolved formal ambiguity merely because CI passes.
