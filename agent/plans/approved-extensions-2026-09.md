# Approved advanced extensions (CS345)

Human-approved project decision. Authority order: root [`AGENTS.md`](../../AGENTS.md) §4.

## Status

```text
approved
```

Lecturer approval confirmed by the group on **2026-09-11**.

## Group and module context

- **Module:** CS345 (two extensions required; minimum met by this selection)
- **Compulsory work:** Sections 5–7 remain unchanged and take priority over extension implementation
- **Submission identification:** when promoted to the assessable repository, name these extensions explicitly in `26455900-CS345/README.md` and the technical report (Section 9)

## Chosen extensions

| Spec § | Title | Citation anchor |
|---|---|---|
| **8.2** | Equivalence and canonicalisation of BPE dictionaries | Berglund & van der Merwe [6]; product constructions [5] |
| **8.11** | Pattern matching and constrained generation on canonical token sequences | Token DFA [5]; Aho–Corasick [2]; optional FST background [8] |

## Rationale

Both extensions reuse machinery the compulsory project already requires:

- proper dictionary model and reference tokenizer (Section 5.1);
- baseline token DFA construction (Section 5.2);
- tokenizer transducer (Section 5.4);
- exhaustive, differential, and product-automaton equivalence testing (Sections 6–6.5).

They apply existing components to new questions rather than introducing a new automaton model (contrast with 8.7 streaming, 8.8 dropout, 8.9 two-dimensional automata, or 8.3 symbolic alphabets).

## Scope bounds

Record these limits so implementation and the report stay defensible.

### 8.2 — Dictionary equivalence and canonicalisation

**In scope (minimum credible deliverable):**

- Precise definition of dictionary equivalence used by this project (same canonical tokenization function on a stated input class, with Unicode representation fixed by the core project decision).
- **Bounded equivalence checking** for small proper dictionaries using independent evidence:
  - reference tokenizer agreement on enumerated or randomly generated inputs (recorded seeds and bounds);
  - token-DFA semantic agreement where both automata can be built;
  - product-automaton / symmetric-difference style checks on bounded token sequences where practical (Section 6.5 machinery).
- Examples of equivalent vs non-equivalent dictionary pairs.
- Optional: sufficient **commutation / independence conditions** for rule reordering (even partial, with worked examples).

**Out of scope (do not claim without new proof):**

- General decidability or complexity results for arbitrary dictionaries (open in [6]).
- Canonicalisation of all BPE dictionaries into a unique global normal form unless restricted to a proved class.
- Equivalence under improper dictionaries except as explicit negative tests.

### 8.11 — Pattern matching on canonical token sequences

**In scope (minimum credible deliverable):**

- Compose the constructed **token DFA** with a token-alphabet pattern matcher (DFA or Aho–Corasick [2]).
- Compare **direct token-level matching** with **detokenize-then-match** baselines on the same patterns.
- Deliberate test cases where patterns **cross token boundaries** and the two approaches differ or where token-level processing is cleaner.
- Evidence that matched outputs remain canonical token sequences accepted by the token DFA where applicable.

**Out of scope unless explicitly re-approved:**

- Full tokenization-aware constrained generation via weighted/FST pipelines [8] beyond a small demonstrator.
- Pattern matching that silently changes tokenization semantics or accepts non-canonical segmentations.

## Dependencies and sequencing

Extensions are **blocked** until the listed compulsory milestones exist.

| Extension | Blocked until | Reuses from compulsory path |
|---|---|---|
| 8.2 | 5.1 reference tokenizer; 5.2 baseline token DFA; 6.5 equivalence hooks | Product/bounded checks, dictionary fixtures, seeds |
| 8.11 | 5.2 token DFA; canonical token-sequence types; trustworthy small examples | Token alphabet, acceptance, detokenization |

**Implementation order relative to extensions:**

1. Complete 5.1 → 5.2 → 5.4 core path.
2. Build Section 6.5 equivalence infrastructure (shared with 8.2).
3. Implement **8.2** bounded dictionary equivalence.
4. Implement **8.11** pattern matching and baseline comparison.

Do not delay compulsory milestones to prefabricate extension-only frameworks.

## Architectural foresight (compulsory core)

When implementing Sections 5–7, prefer seams that extensions can reuse without speculative abstraction:

- distinct **token-sequence** types (not only detokenized strings);
- reusable **automaton composition** and **bounded equivalence** utilities (needed for 6.5 anyway);
- dictionary and experiment fixtures that support **pairs of dictionaries** and **pattern suites**;
- honest reporting of bounds, seeds, timeouts, and limitations.

## Authoritative sources

- Project specification Section 8: [`../specs/cs345-project-specification.md`](../specs/cs345-project-specification.md)
- [6] Formalizing BPE tokenization — equivalence question, proper dictionaries
- [5] Constructing a BPE tokenization DFA — token DFA, product ideas
- [2] Aho & Corasick — multi-pattern matching (8.11)
- [8] Cognetta & Okazaki — optional background for constrained generation (8.11, if pursued)

Research catalogue: [`../../research/index.yaml`](../../research/index.yaml)

## Future tickets

Create bounded implementation tickets when compulsory prerequisites are satisfied:

- `agent/tickets/TICKET-802-dictionary-equivalence.md`
- `agent/tickets/TICKET-811-token-pattern-matching.md`

## Promotion to assessable repository

When extension work begins or at report time, promote a concise summary (not this private plan verbatim) to:

- `26455900-CS345/docs/` — extension scope and methods
- `26455900-CS345/README.md` — chosen extensions and how to run related tests/experiments

## Revision history

| Date | Change |
|---|---|
| 2026-09-11 | Initial record; lecturer approved 8.2 and 8.11 |
