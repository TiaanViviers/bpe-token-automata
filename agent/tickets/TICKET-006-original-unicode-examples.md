# TICKET-006: Original examples and Unicode token identity

## Status

```text
review
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Add three original worked-example fixtures and tests that lock token identity as UTF-8 bytes, including non-ASCII `é` and emoji 😀.

## Background

Spec §5.3 requires at least three original examples (one non-ASCII, one emoji or other multi-byte Unicode). Spec §6.1 requires Unicode/emoji tests that token identity is not altered by normalisation.

## Authoritative sources

- Project specification: §5.3, §6.1
- Approved decision: D1 (bytes); [`../specs/token-dfa-canonical-examples.md`](../specs/token-dfa-canonical-examples.md)
- Existing implementation/documentation: `finite_ab.yaml`, `decode_token_literal`

## Scope

The ticket includes:

- `original_finite_ab.merges` with `finite_ab.yaml`
- `original_eacute.merges` (`\xc3 ⫽ \xa9`)
- `original_emoji.merges` (four-byte 😀 chain)
- Hand-expected traces/edges
- Bounded `tokenize_reference` agreement
- Parser: `\xHH` pair vs UTF-8 `é` literal
- NFC vs NFD distinctness

## Non-goals

The ticket explicitly excludes:

- Changing D1
- Using character literals as base-alphabet symbols
- Worked-example prose (TICKET-007)

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

Keep \(\Sigma\) as the relevant length-1 bytes. Merge files use `\xHH`. Tests construct expected triples by applying Algorithm 2 by hand on these tiny automata.

## Files likely to change

```text
26455900-CS345/data/dictionaries/original_finite_ab.merges
26455900-CS345/data/dictionaries/original_eacute.merges
26455900-CS345/data/dictionaries/original_emoji.merges
26455900-CS345/tests/test_token_dfa_unicode.py
26455900-CS345/tests/test_dictionary_parser.py
```

## Acceptance criteria

- [ ] Finite \(L=\{ab\}\) with `a⫽b`: only `ab` accepted after the merge
- [ ] `é` bytes: canonical token of `C3 A9` is the two-byte token
- [ ] 😀 bytes: canonical token of `F0 9F 98 80` is the four-byte token
- [ ] NFC `é` and NFD `é` are different byte strings and different tokenizations
- [ ] Parser distinguishes `\xc3 \xa9` from a single `é` token

## Required test evidence

### Unit tests

- Token identity / parser literal kinds

### Regression tests

- Hand-expected triples for each original dictionary

### Differential or exhaustive tests

- All strings up to a stated bound on each original \(\Sigma\) vs `tokenize_reference`

### Negative and special cases

- Base tokenization of the emoji rejected after the full merge chain
- NFD input not accepted as the NFC merged token

## Documentation changes

- [ ] Deferred to TICKET-007

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Formal interpretation: treating `é` as a length-1 symbol
- Correctness: emoji chain must be proper
- Reproducibility: bound must be stated

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
