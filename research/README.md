# Research materials

Locally managed research-paper sources, Marker Markdown conversions, notes, and a machine-readable catalogue.

This directory is private local infrastructure and is **not** part of the university GitLab repository at `../26455900-CS345/`.

```text
research/
├── README.md                 # this file
├── index.yaml                # machine-readable research catalogue
├── sources/                  # original PDFs (*.pdf gitignored)
├── markdown/                 # Marker conversions (one folder per work)
│   └── <stable-id>/
│       ├── index.md          # conversion entry point
│       ├── marker_meta.json  # optional Marker metadata
│       └── _page_*.jpeg      # extracted figures when present
└── notes/
    └── <stable-id>.md        # human verification / interpretation notes
```

Stable path names omit years. Catalogue `id` values include the year (for example `formalizing-bpe-tokenization-2023`).

## Quick start for agents and humans

1. Open [`index.yaml`](index.yaml) to find the work you need.
2. Read the Markdown entry listed under `markdown` for search and ordinary reading.
3. Open the PDF listed under `pdf` only for fidelity-sensitive material (definitions, equations, algorithms, diagrams, proofs, exact wording).
4. Record interpretation and verification progress in the matching `notes` file **and** update `conversion.status` / `conversion.known_issues` in the catalogue when status changes.


## Project specification

| Role | Path |
|---|---|
| Agent entry pointer | [`../agent/specs/cs345-project-specification.md`](../agent/specs/cs345-project-specification.md) |
| Markdown (default reading) | [`markdown/cs345-project-specification/index.md`](markdown/cs345-project-specification/index.md) |
| PDF (authoritative; verify only) | `sources/cs345-project-specification.pdf` |
| Catalogue entry | `id: cs345-project-specification-2026` in [`index.yaml`](index.yaml) |

Prefer the Markdown conversion for ordinary work. Open the PDF only when exact wording or conversion fidelity matters.

## What `index.yaml` is for

The catalogue is the directory of the research library. Without it, an agent must guess:

- which Markdown folder corresponds to which PDF;
- which works are compulsory (`role: core`) versus background/extension material;
- which citation key to use;
- whether a conversion has been checked;
- what topics each work covers;
- whether there are known conversion problems.

Each entry points at the real files on disk. Do not invent bibliographic metadata; mark unknowns explicitly and verify against the PDF or an authoritative publisher page.

### Roles

| Role | Meaning |
|---|---|
| `specification` | Course project specification |
| `core` | Compulsory for the main CS345 implementation path |
| `background` | Formal background cited by the core path |
| `extension` | Optional extension material from the specification |
| `supplementary` | Useful context, not a primary implementation source |

### Conversion statuses

Use only this vocabulary:

| Status | Meaning |
|---|---|
| `unconverted` | PDF present; no usable Markdown conversion yet |
| `converted-unverified` | Marker finished; important sections not yet checked against the PDF |
| `partially-verified` | Selected sections used by the project have been compared with the PDF |
| `verified-for-use` | All sections currently relied on by the project have been checked |
| `conversion-defective` | Serious conversion damage; Markdown is unsafe without repair or frequent PDF consultation |

You do not need to verify every word of every paper. Verify the portions that affect implementation or the report, then raise the status accordingly.

### Verification workflow

1. Pick a catalogue entry whose status is `converted-unverified` or `conversion-defective`.
2. Identify sections needed for the current task (definitions, algorithms, theorems, examples).
3. Compare those sections with the PDF; record page/section references in the notes file.
4. Append durable defects to `conversion.known_issues`.
5. Update `conversion.status` to `partially-verified`, `verified-for-use`, or keep/set `conversion-defective`.
6. Verify the edited catalogue fields, controlled vocabulary, referenced paths, and Markdown image links. No automated research-index verifier currently exists.

The verifier is intentionally lightweight: it checks catalogue structure, uniqueness, allowed statuses/roles, path existence, and Markdown image references. It does **not** prove that a conversion is semantically faithful.

## Current library snapshot

See [`index.yaml`](index.yaml) for the live list. At catalogue creation the core set is:

| Stable path | Role | Status |
|---|---|---|
| `formalizing-bpe-tokenization` | core | converted-unverified |
| `constructing-bpe-token-dfa` | core | converted-unverified |
| `constructing-compact-bpe-token-dfas` | core | converted-unverified |
| `determinization-of-transducers` | background | converted-unverified |
| `streaming-bpe-tokenization` | extension | conversion-defective |
| `incremental-bpe-tokenization` | extension | converted-unverified |
| `subword-tokenization-meets-formal-language-theory` | supplementary | converted-unverified |
| `cs345-project-specification` | specification | converted-unverified |

## Rules and authority

Research-source rules: [`../agent/rules/research-sources.md`](../agent/rules/research-sources.md).

Canonical authority order: root [`../AGENTS.md`](../AGENTS.md).

Formal documentation must cite the original publication (or the course PDF for the specification), not the Markdown conversion file.
