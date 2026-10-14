---
name: source-driven-development
description: >
  Ground implementation and design decisions in the official project
  specification, original research-paper PDFs, verified Markdown conversions,
  human-approved decisions, and official technical docs. Use when formal or
  library correctness matters, when citing algorithms/definitions, or when the
  user asks for source-backed work. Trigger phrases include "source-driven",
  "cite the paper", and "verify against the PDF". Stop before implementing when
  source interpretation remains blocking.
---

# Source-Driven Development

Every correctness-sensitive decision must be grounded in an authoritative
source the human can check. Training data and blog summaries are not enough for
formal constructions in this project.

This skill is **not** limited to framework documentation. Primary sources here
are formal papers and the course specification.

## When to use

* Implementing or designing against paper algorithms/definitions
* Choosing representations that must preserve formal semantics
* Using a library/tooling API where the official docs matter
* Reviewing whether code matches a cited source

**When not to use:** pure renames, formatting, or logic that does not depend on
an external formal or API source.

## Authority

Follow the canonical source-authority order in `@AGENTS.md`.

Follow `@agent/rules/research-sources.md` for the reading workflow.

Do not invent a competing hierarchy inside this skill.

## Process

### 1. Navigate with Markdown

Search and read verified/available Markdown conversions under `research/markdown/`
(and the course-spec pointer under `agent/specs/`) for navigation and initial
reading.

### 2. Verify fidelity-sensitive details against the PDF

For definitions, equations, pseudocode, diagrams, quantifiers, page references,
and anything used as an implementation invariant, consult the original PDF under
`research/sources/`.

Do not implement a formal algorithm solely from converted Markdown when the PDF
carries relevant notation or pseudocode.

### 3. Record what was consulted

Where available, record:

* paper or specification identity;
* section;
* page;
* definition, theorem, algorithm, or figure identifier.

Never fabricate citations, page numbers, theorem numbers, or quotations.

### 4. Separate layers of claim

Always distinguish:

| Layer | Meaning |
|---|---|
| Source claim | What the paper/spec says |
| Interpretation | How we read it |
| Project decision | What we choose for this repository |
| Implementation consequence | What code/tests must do |

Surface ambiguity instead of silently resolving it.

### 5. Prefer primary sources

Prefer:

1. official CS345 project specification;
2. original research-paper PDFs;
3. published errata / author clarifications;
4. human-approved project decisions;
5. approved engineering specs;
6. verified Markdown conversions;
7. official technical documentation for libraries/tools.

Do not treat Stack Overflow, random blogs, or model memory as primary authority.

### 6. Stop when blocked

If source interpretation remains blocking, **stop before implementation** and
report:

* sources consulted (Markdown and/or PDF);
* what is clear;
* what is ambiguous;
* decisions required from a human.

## Library / tooling docs

When the decision is about a dependency API rather than a paper:

* detect versions from dependency files under `26455900-CS345/`;
* fetch the official docs for that version;
* cite deep links;
* flag unverified patterns explicitly.

## Outputs

In conversation and in tickets/handoffs/notes:

* cite sources;
* label interpretations;
* list unresolved questions.

Do not place private research notes under `26455900-CS345/`.
