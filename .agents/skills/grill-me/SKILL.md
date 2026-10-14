---
name: grill-me
description: >
  User-facing entry point for an adaptive grilling session that stress-tests a
  plan, design, formal interpretation, or decision. Use when the user explicitly
  asks to be grilled, interviewed, or stress-tested about their thinking.
  Trigger phrases include "grill me", "stress-test this", and "interview me
  about this plan". Do not use to implement code, write tickets, or modify
  files. Prefers the grilling skill for the interview procedure.
---

# Grill Me

User-invoked entry point for a grilling session. Do not start this skill unless
the human explicitly asked for grilling, interviewing, or stress-testing of
their thinking.

## Procedure

1. Confirm the topic to explore (plan, design, formal interpretation, ticket
   scope, experiment method, or similar).
2. Follow the interview procedure in `@.agents/skills/grilling/SKILL.md`.
3. Ask **one question at a time**. Wait for the answer before continuing.
4. Prefer probing decisions, assumptions, trade-offs, examples, and
   counterexamples over quiz-style trivia.
5. If a fact can be answered by inspecting this repository, inspect it. Do not
   ask the human for repository facts you can look up.
6. Do **not** implement code, create tickets, edit files, stage changes, commit,
   or push.
7. Do **not** treat answers as automatically approved project decisions. Record
   unresolved decisions as unresolved.

Respect `@AGENTS.md` and `@agent/rules/git-and-branches.md`.

## Closing summary

When the topic is sufficiently explored or the human ends the session, finish
with:

* areas understood well;
* weak or uncertain areas;
* unresolved decisions;
* readiness assessment;
* recommended next learning or design step.

The readiness assessment must not falsely certify understanding. If evidence of
understanding is thin, say so.
