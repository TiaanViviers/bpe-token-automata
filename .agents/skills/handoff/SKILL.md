---
name: handoff
description: >
  Compact the current conversation into a durable handoff document under
  agent/handoffs/ so another human or agent can continue. Use when ending a
  session, switching contributors, or the user asks for a handoff. Trigger
  phrases include "write a handoff", "hand this off", and "session summary for
  the next agent". Inspect real Git status and diffs. Do not commit or push.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

# Handoff

Write a durable handoff summarising work so a fresh agent or human can continue
without relying on chat history.

## Template and location

Use `@agent/templates/handoff.md` as the structure.

Default output location:

```text
agent/handoffs/
```

If a ticket identifier exists, prefer:

```text
agent/handoffs/<ticket-id>/<date>-<short-description>.md
```

Example:

```text
agent/handoffs/TICKET-004/2026-07-26-codex-implementation.md
```

Otherwise use a clear dated filename directly under `agent/handoffs/`:

```text
agent/handoffs/2026-07-26-<short-description>.md
```

Do **not** write handoffs to `/tmp` or another transient directory.

Do **not** place handoffs under `project/`.

## Required inspection

Before writing, inspect actual state:

```bash
git status
git branch --show-current
git log --oneline -5
git diff
git diff --cached
```

Record only work genuinely completed. Do not list planned work as done.

## Required content

Complete every section of the template, including:

* task, ticket, branch, scope, and status;
* files changed and their roles;
* sources consulted (Markdown vs PDF where relevant);
* decisions made, with temporary vs approved distinguished;
* tests added or changed;
* commands actually run;
* validation results distinguishing **pass**, **fail**, **blocked**, and
  **not run**;
* pre-existing unrelated changes preserved;
* unresolved questions and risks;
* exactly one concrete recommended next step;
* final Git status summary.

If the user passed arguments, treat them as the focus of the next session and
tailor the handoff accordingly.

Optionally include a short "suggested skills" section naming skills the next
session may need. Reference existing artefacts by path instead of duplicating
them.

Redact secrets, API keys, passwords, and unnecessary personal data.

## Prohibited actions

* Do not stage, commit, amend, push, or open a pull request.
* Do not switch or create branches.
* Do not claim unperformed validation succeeded.

Follow `@AGENTS.md` and `@agent/rules/git-and-branches.md`.
