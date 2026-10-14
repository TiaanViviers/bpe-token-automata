# TICKET-007: Worked-example documentation

## Status

```text
review
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Write the assessable Section 5.3 chapter as `26455900-CS345/docs/token-dfa-examples.md`: per-merge triples, fresh states, redirects, and bounded tokenization tables for the paper examples, the unary chain, and the three original examples.

## Background

Spec §5.3: the report shall not merely include final diagrams. The §9.1 PDF is later; this Markdown is the 5.3 content that both partners can explain.

## Authoritative sources

- Project specification: §5.3
- Paper and section: [5] Algorithm 2, Example 2, Figs. 3–4
- Approved decision: D1, D22
- Existing implementation/documentation: TICKET-005 traces, TICKET-006 fixtures

## Scope

The ticket includes:

- `docs/token-dfa-examples.md`
- README and `docs/design-decisions.md` pointers
- D1 restatement and NFC/NFD contrast
- DOT regeneration note (`to_dot`; no CI PNG)

## Non-goals

The ticket explicitly excludes:

- The full 10-page PDF report
- Transducer / compact / experiment chapters

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

Narrative follows Algorithm 2 line order for each merge. Cite [5] for Example 2 and state that the unary chain is a project fixture. Diagrams as mermaid or DOT code blocks.

## Files likely to change

```text
26455900-CS345/docs/token-dfa-examples.md
26455900-CS345/docs/design-decisions.md
26455900-CS345/README.md
```

## Acceptance criteria

- [ ] Example 2, unary chain, and three original examples are each explained at merge granularity
- [ ] Symbol model is stated (bytes, not code points or graphemes)
- [ ] D22 “non-ba” slip is mentioned
- [ ] README links the new doc

## Required test evidence

Documentation-only ticket; correctness evidence lives in TICKET-005/006. `make check` must still pass.

## Documentation changes

- [x] Public API or README
- [x] Architecture or algorithm documentation
- [ ] Decision record (pointer only)

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Scope: do not turn this into the full technical report
- Formal interpretation: tables must match tests / paper, not an uncited dump

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Relevant documentation updated.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Human review completed.
- [ ] Both partners can explain Example 2 from triples to tokenizations.
