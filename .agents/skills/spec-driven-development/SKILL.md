---
name: spec-driven-development
description: >
  Create or refine engineering specifications under agent/specs/ before coding.
  Use when starting a feature or significant change, when requirements are
  unclear, or when university requirements must be distinguished from local
  design decisions. Trigger phrases include "write a spec", "specify this",
  and "spec-driven". Stop after the specification. Do not automatically plan,
  ticket, or implement.
---

# Spec-Driven Development

Write a structured engineering specification before implementation. The spec is
a shared design artefact for this research/software-engineering project — not a
product marketing brief and not a substitute for the official CS345 project
specification.

## When to use

* Starting a medium or large feature
* Requirements are ambiguous or incomplete
* The change touches multiple modules or formal constructions
* An architectural or representation decision needs to be recorded

**When not to use:** trivial fixes, typo corrections, or changes whose
requirements are already unambiguous in an approved ticket.

## Authority and sources

Follow the canonical source-authority order in `@AGENTS.md`.

Also follow `@agent/rules/research-sources.md`.

Before drafting:

1. Inspect `@agent/specs/cs345-project-specification.md` and the linked Markdown
   course specification.
2. Locate relevant research papers via `research/` (Markdown for navigation;
   PDF for fidelity-sensitive details).
3. Distinguish:

   * university / course requirements;
   * claims from cited papers;
   * local engineering design decisions;
   * unresolved formal questions.

Do not invent requirements. Surface assumptions explicitly before filling them in.

## Output location

Write or refine specs under:

```text
agent/specs/
```

Use a descriptive kebab-case name, for example:

```text
agent/specs/dictionary-validation.md
agent/specs/baseline-token-automaton.md
```

Do **not** create a generic root-level `SPEC.md`.

Do **not** place specs under `project/` unless promoting human-reviewed
submission-safe documentation later (out of scope for this skill).

## Spec content

Tailor terminology to this project. Cover at least:

1. **Goal** — what is being specified and why
2. **Background** — course requirement vs research context
3. **Scope** and **Non-goals**
4. **Authoritative sources** — course spec clauses; paper sections/pages;
   approved decisions
5. **Interfaces** — types, modules, serialisation, CLI or API surfaces
6. **Invariants** — formal and representation invariants
7. **Error and edge behaviour**
8. **Testing and acceptance criteria** — independent evidence expectations;
   see `@agent/rules/testing-and-correctness.md`
9. **Risks**
10. **Open questions** — especially unresolved formal questions
11. **Validation commands** — ordinarily `cd project && make check`

Surface assumptions before writing body content:

```text
ASSUMPTIONS I'M MAKING:
1. ...
→ Correct me now or I'll proceed with these.
```

## Stop condition

This skill stops after producing or refining the requested specification and
listing open questions.

Do **not** automatically proceed into:

* `planning-and-task-breakdown`;
* ticket generation;
* implementation.

If the human next asks for planning or tickets, that is a separate invocation.

## Living specs

Update the spec when approved decisions change. Specs belong in version control
under `agent/specs/`. Committing remains a separately authorised Git action —
see `@agent/rules/git-and-branches.md`.
