---
name: doubt-driven-development
description: >
  Subject correctness-sensitive claims to adversarial fresh-context challenge
  before they stand. Use for formal algorithm interpretations, automata
  equivalence, transducer behaviour, Unicode representation, experimental
  methodology, oracle independence, and similar high-stakes claims. Trigger
  phrases include "doubt this", "adversarial review", and "challenge this
  claim". Do not manufacture doubt for trivial edits; do not rewrite code
  automatically.
---

# Doubt-Driven Development

A confident answer is not a correct one. For correctness-sensitive claims in
this project, materialize an adversarial challenge — preferably with fresh
context — before the claim stands.

This is not a substitute for `code-review-and-quality`. Review judges a finished
diff. Doubt challenges an in-flight claim while course-correction is still cheap.

## Suitable claims

Examples:

* formal algorithm interpretations;
* transition inheritance;
* self-merge handling;
* automata equivalence;
* transducer determinisation;
* Unicode representation;
* experimental methodology;
* timeout and memory reporting;
* independence of test oracles.

**When not to use:** renames, formatting, obvious one-line edits, or when the
human explicitly wants speed over verification.

## Process

Use this structure:

```text
Claim
Evidence
Assumptions
Adversarial doubt
Counterexample search
Reconciliation
Status
```

### Claim

State the claim in two or three lines and why it matters.

### Evidence

List the actual evidence: paper sections/pages, tests, derivations, experiments.
Follow `@agent/rules/research-sources.md` and the canonical source-authority
order in `@AGENTS.md`. Prefer primary sources.

### Assumptions

List unstated assumptions explicitly.

### Adversarial doubt

Challenge the claim. Prefer a fresh-context reviewer (separate subagent/session)
biased to **disprove**, not approve.

Pass the artifact and the contract/evidence only — do not pass your conclusion
as a leading prompt.

Look for:

* unstated assumptions;
* minimal counterexamples;
* paper/spec mismatches;
* correlated oracles;
* edge cases (empty dictionaries, self-merges, partial transitions, Unicode);
* ways the claim could be true in tests yet false formally.

### Counterexample search

Seek the smallest concrete counterexample or distinguishing case. Do not stop at
vague worry.

### Reconciliation

Classify each finding:

* contract/claim mis-stated;
* valid and actionable;
* valid trade-off (document it);
* noise given missing context.

### Status

Finish with exactly one of:

```text
supported
supported with limitations
requires evidence
contradicted
unresolved
```

## Stop conditions

* If a central correctness claim remains **unresolved**, **contradicted**, or
  **requires evidence**, stop implementation until a human decides.
* Bound the doubt loop (suggest at most three serious cycles) and escalate
  rather than grinding.
* Do not manufacture doubt for trivial choices.
* Do not rewrite code automatically; report findings.

## Cross-model / external tools

If offering an external second opinion (another model/CLI):

* ask the human first;
* never invoke network/CLI tools without explicit authorisation;
* prefer writing the prompt to a workspace file under `agent/` rather than
  shell-interpolating untrusted artifact text;
* announce when cross-model review was skipped.

## Constraints

* Follow `@agent/rules/git-and-branches.md`.
* Do not place private doubt notes under `project/`.
* Honesty beats false certification of understanding or correctness.
