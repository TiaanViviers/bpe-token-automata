---
name: code-review-and-quality
description: >
  Conduct multi-axis code review for this repository before merge. Use when
  reviewing your own, another agent's, or a human's change; after bug fixes; or
  when assessing quality across ticket scope, formal correctness, tests,
  architecture, docs, and submission-boundary safety. Trigger phrases include
  "review this", "code review", and "before merge". Produce a review report;
  do not automatically rewrite the code.
---

# Code Review and Quality

Multi-dimensional review for the BPE Token Automata project. Produce a review
report. Suggest patches when helpful, but **do not implement fixes** unless the
human separately authorises that work.

## When to use

* Before merging a PR or integrating a change
* After feature implementation or a bug fix
* When evaluating agent-produced code
* When asked for a structured review

## Review dimensions

Evaluate every change across:

1. **Ticket and scope agreement** — matches the approved ticket/spec; no silent
   scope expansion
2. **Formal and semantic correctness** — agrees with cited course/paper sources;
   preserves terminology and invariants
3. **Test quality and independence** — suitable families; independent oracles;
   no correlated implementation/oracle logic
   (`@agent/rules/testing-and-correctness.md`)
4. **Architecture and representation** — fits existing design; representation
   choices do not quietly change semantics
5. **Readability and maintainability** — explainable by both students; no
   unnecessary abstraction
6. **Performance and scaling risk** — pathological inputs, timeouts, memory;
   honesty about limits
7. **Documentation and reproducibility** — docs, seeds, commands, limitations
8. **Submission-boundary safety** — no private `agent/`, `research/`, `.agents/`,
   or `.cursor/` material under `project/`

Follow the canonical source-authority order in `@AGENTS.md`. When semantics are
involved, consult the cited formal sources rather than trusting the diff alone.

## Process

### 1. Context

Identify the ticket, approved spec, expected behaviour, and branch/diff under
review.

```bash
git status
git branch --show-current
git log --oneline -5
git diff
git diff --cached
```

### 2. Tests first

Inspect tests as carefully as implementation:

* Do tests exist for the claimed behaviour?
* Are oracles independent of the production logic?
* Could the change pass tests while still violating the paper?
* Are edge cases (self-merges, improper dictionaries, Unicode, etc.) covered?

### 3. Implementation walk

For each important changed file, apply the eight dimensions above.

### 4. Classify findings

| Label | Meaning |
|---|---|
| **Blocking** | Must fix before merge |
| **Risk** | Correctness/reproducibility concern needing explicit decision |
| **Improvement** | Optional improvement |
| **Nit** | Style preference; may ignore |
| **FYI** | Context only |

Distinguish blocking issues from optional improvements. Lead with high-leverage
findings.

Call out explicitly:

* correlated oracle/test logic;
* undocumented assumptions;
* paper/spec mismatches that tests might miss;
* submission-boundary leaks.

### 5. Verification story

Record which checks were actually run vs not run. Prefer project commands:

```bash
cd project
make check
```

Do not claim checks passed unless they were run.

## Output

Write a review report (conversation and, if requested, under `agent/reviews/`).
Do not silently rewrite the tree.

Suggested shape:

```markdown
## Review: <title>

### Context
### Blocking findings
### Risks
### Improvements
### Tests and independence
### Formal sources consulted
### Verification
### Verdict
- Request changes | Approve with follow-ups | Approve
```

## Constraints

* Follow `@agent/rules/git-and-branches.md` — review does not commit or push.
* Do not weaken tests to obtain a green review.
* Both partners must be able to explain accepted changes.
