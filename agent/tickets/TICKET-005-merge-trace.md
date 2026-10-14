# TICKET-005: MergeTrace and byte-safe token labels

## Status

```text
review
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Expose Algorithm 2’s triples, fresh-state map, inherited copies, and redirected `u`-edges as `MergeTrace`, and make token-sequence formatting byte-safe so incomplete UTF-8 tokens can be displayed.

## Background

Section 5.3 requires explaining each merge. `apply_merge` currently discards triples and returns only `|S2|`. `format_token_sequence` UTF-8-decodes each token and will raise on `\xf0`.

## Authoritative sources

- Project specification: §5.3
- Paper and section: [5] Algorithm 2 (PDF p. 4), Example 2, Figs. 3–4
- Approved decision: [`../specs/token-dfa-canonical-examples.md`](../specs/token-dfa-canonical-examples.md); D1; D22
- Existing implementation/documentation: `apply_merge`, `ConstructionResult`

## Scope

The ticket includes:

- `format_token_label` in `tokens.py`; `format_token_sequence` joins labels
- `MergeTrace`; `apply_merge` → `(TokenDFA, MergeTrace)`
- `ConstructionResult.traces`
- Tests: Example 2 paper triples; unary hand-applied triples; incomplete UTF-8 formatting

## Non-goals

The ticket explicitly excludes:

- Original Unicode/emoji fixtures (TICKET-006)
- Worked-example Markdown (TICKET-007)
- CLI, trimming, PNG rendering

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

See the engineering spec. Record `inherited` before line 19. Sort states and tokens so traces are deterministic.

## Files likely to change

```text
26455900-CS345/src/bpe_token_automata/tokens.py
26455900-CS345/src/bpe_token_automata/automaton/serialize.py
26455900-CS345/src/bpe_token_automata/automaton/construction.py
26455900-CS345/src/bpe_token_automata/automaton/__init__.py
26455900-CS345/src/bpe_token_automata/__init__.py
26455900-CS345/tests/test_tokens.py
26455900-CS345/tests/test_token_dfa_examples.py
```

## Acceptance criteria

- [ ] Example 2 traces match the paper’s \(S\) and fresh-state story
- [ ] Unary traces match hand-applied Algorithm 2
- [ ] `format_token_sequence` formats `\xf0` as `\xf0`
- [ ] Empty \(S\) yields `n_fresh == 0` and empty triples
- [ ] `n_fresh` still equals `|S2|`

## Required test evidence

### Unit tests

- Byte-safe formatting of incomplete UTF-8 and printable ASCII round-trip display

### Regression tests

- Example 2 Fig. 3 edges remain
- Example 2 triples from paper text
- Unary chain triples and omitted `uv` on the first self-merge

### Differential or exhaustive tests

- Covered by existing length-≤6 Example 2 oracle test

### Negative and special cases

- Empty \(S\)

## Documentation changes

- [ ] Deferred to TICKET-007 except public exports

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Formal interpretation: `inherited` vs post-redirect edges
- Correctness: expected triples must not be copied from `apply_merge`
- Scope: do not add original Unicode fixtures here

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
