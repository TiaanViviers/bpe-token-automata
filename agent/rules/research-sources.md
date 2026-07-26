# Research Source Rules

## Purpose

This document defines how research papers, converted Markdown, notes, and external sources must be used.

The project depends on recent formal literature. Conversion errors, notation loss, and incorrect paraphrases can directly produce incorrect implementations.

## Authority

The canonical source-authority order is defined in the root [`AGENTS.md`](../../AGENTS.md).
Do not reproduce or redefine it here.

Do not silently reconcile contradictions between sources.

## Preferred reading workflow

For an ordinary research question:

1. locate the paper through the research directory and notes;
2. search and read the Markdown conversion;
3. identify the relevant section, theorem, definition, or algorithm;
4. inspect the original PDF for fidelity-sensitive content;
5. record the interpretation and remaining uncertainty;
6. cite the original paper in formal documentation.

Markdown is the preferred navigation and search format.

The PDF remains authoritative.

## When PDF verification is mandatory

Consult the original PDF for:

- definitions whose exact quantifiers matter;
- equations;
- formal notation;
- subscripts and superscripts;
- pseudocode;
- transition diagrams;
- automata figures;
- tables;
- proofs;
- page references;
- multi-column layouts;
- ambiguous conversion output;
- symbols that may have been replaced or normalised;
- any detail used to justify an implementation invariant.

Do not implement a formal algorithm solely from converted Markdown when the PDF contains notation, diagrams, or pseudocode relevant to the task.

## Research directory

Current structure:

```text
research/
├── sources/
├── markdown/
├── notes/
└── README.md
```

### Project specification

The official CS345/CS711 project specification uses the same dual-format pattern:

- pointer: [`../specs/cs345-project-specification.md`](../specs/cs345-project-specification.md)
- Markdown (default): `research/markdown/cs345-project-specification.md`
- PDF (verify only): `research/sources/cs345-project-specification.pdf`

Do not open the PDF for routine reading.

### `sources/`

Contains original papers and other source material.

Original files remain authoritative and should not be edited.

### `markdown/`

Contains machine-generated derivatives for search and reading.

Conversions should preserve:

- source identity;
- page markers where possible;
- heading structure;
- equations and algorithms as faithfully as possible;
- figure and table references.

### `notes/`

Contains human-reviewed interpretation and verification notes.

A note must clearly distinguish:

- source claim;
- project interpretation;
- implementation implication;
- unresolved question.

## Research index

A formal research index may be designed after Marker conversion is stable.

Until then, locate papers through `research/README.md`, directory layout, and human-maintained notes.

When an index is introduced, each paper should have a stable identifier and metadata similar to:

```yaml
papers:
  - id: constructing-bpe-token-dfa-2026
    title: Constructing a BPE Tokenization DFA
    authors:
      - Martin Berglund
      - Willeke Martens
      - Brink van der Merwe
    year: 2026
    role: core
    citation_key: berglund2026constructing
    pdf: sources/constructing-bpe-token-dfa-2026.pdf
    markdown: markdown/constructing-bpe-token-dfa-2026/
    notes: notes/constructing-bpe-token-dfa-2026.md
    conversion_status: converted-unverified
```

Do not invent missing metadata. Mark it as unknown until verified.

Do not create the index file until the conversion workflow is approved.

## Conversion status

Use a small controlled vocabulary:

```text
unconverted
converted-unverified
partially-verified
verified-for-use
conversion-defective
```

A paper need not be verified line by line.

Instead, verify the sections used for implementation or formal claims.

Record known defects such as:

- broken equations;
- lost token symbols;
- merged columns;
- missing figure labels;
- incorrect Unicode characters;
- malformed pseudocode indentation.

## Citation rules

Formal documentation and the report must cite the original source.

Do not cite:

- the Markdown conversion as though it were the publication;
- an agent summary in place of a paper;
- a generated explanation without a supporting source.

Internal notes may link to Markdown paths for convenience, but should also identify the original paper and relevant page or section.

Never fabricate:

- page numbers;
- theorem numbers;
- quotations;
- author claims;
- publication details.

## Quotation and paraphrase

Prefer accurate paraphrase.

When exact language is necessary:

- verify it against the PDF;
- quote only the required passage;
- preserve notation;
- record the page.

Clearly label interpretation as interpretation.

## Research notes

A useful research note contains:

```text
Question
Sources consulted
Relevant sections
Source-derived findings
Interpretation
Implementation implications
Examples or counterexamples
Uncertainty
Decisions required
```

Do not present unresolved interpretation as an approved design decision.

## Adding new papers

Before adding a source:

- confirm its relevance;
- record bibliographic metadata;
- record where it was obtained;
- check licence and redistribution constraints;
- classify it as core or supplementary;
- convert it reproducibly where practical;
- update any research index once that mechanism exists.

Do not commit copyrighted PDFs to a future public repository without checking redistribution rights.

## Using external web material

Research papers and official documentation are preferred over blogs and summaries for technical claims.

External explanations may help understanding, but they do not override the project specification or cited formal literature.

Record important external sources so another person can reproduce the reasoning.

## Agent obligations

An agent working on a research-sensitive task must report:

- papers consulted;
- sections or pages used;
- whether Markdown or PDF was read;
- conversion defects encountered;
- interpretation made;
- unresolved ambiguity;
- consequences for implementation or testing.

When a formal point remains uncertain, stop and surface it rather than selecting the most convenient interpretation.
