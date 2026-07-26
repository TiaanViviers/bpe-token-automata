---
name: grilling
description: >
  Grill the user relentlessly but constructively about a plan, decision, formal
  interpretation, or idea. Use when the user wants to stress-test their
  thinking, or when grill-me delegates here. Trigger phrases include "grill",
  "stress-test", and "interview me about". Do not implement, edit files, or
  commit. Ask one adaptive question at a time.
---

# Grilling

Adaptive interview procedure used by `grill-me` and available directly when the
human asks to be grilled.

## Goal

Reach a shared, honest understanding of the topic by walking decision branches
one at a time. Distinguish recognition ("I've heard that") from genuine
understanding (can explain, give examples, handle counterexamples).

## Rules

1. Ask **one question at a time**. Wait for feedback before continuing.
2. Later questions must respond to previous answers. Do not run a fixed quiz
   script.
3. Probe:

   * examples and concrete cases;
   * counterexamples;
   * assumptions;
   * edge cases;
   * trade-offs;
   * failure modes;
   * what would change the decision.

4. For each question, you may offer a brief recommended answer, then wait. Do
   not dump a complete solution that ends the need to think.
5. If a *fact* can be found by inspecting the repository (filesystem, Git state,
   specs, papers, code), look it up rather than asking. *Decisions* remain the
   human's — put each one to them and wait.
6. When answers are vague, become more direct and ask for a concrete example or
   counterexample. Remain constructive, not hostile.
7. Do not act on the plan (implement, rewrite files, create tickets, commit)
   until the human confirms shared understanding — and even then, only if they
   separately authorise that next action.
8. Stop when the agreed topic is sufficiently explored or the human ends the
   session.

## Repository constraints

* Follow `@AGENTS.md` and `@agent/rules/git-and-branches.md`.
* Do not modify files unless the human explicitly asks for a written artefact
  after the grill.
* Do not place private notes under `project/`.
* Follow the canonical source-authority order in `AGENTS.md` when formal claims
  arise; surface ambiguity rather than resolving it silently.

## Closing

If invoked via `grill-me`, use that skill's closing summary format. If invoked
directly, provide the same closing summary unless the human asks otherwise.
