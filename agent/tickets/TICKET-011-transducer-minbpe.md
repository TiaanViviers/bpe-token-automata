# TICKET-011: minbpe BasicTokenizer comparison

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Compare the subsequential tokenizer with Karpathy minbpe `BasicTokenizer` on token sequences, where the merge list can be loaded without regex pre-tokenization.

## Background

Course §5.4: “where compatible”. D1/D9 already match byte-level BasicTokenizer (no GPT-2 regex).

## Authoritative sources

- Project specification: §5.4
- External: https://github.com/karpathy/minbpe (MIT)
- Approved decision: D31
- Existing implementation: `tokenize` vs `tokenize_reference`

## Scope

The ticket includes:

- attributed adapter that injects our ordered merges into BasicTokenizer tables
- token-sequence comparison (map ids back to bytes)
- README attribution

## Non-goals

GPT-2 regex tokenizer; training from a corpus and hoping merges match; weakening the 5.1 oracle tests if minbpe cannot load merges.

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

If minbpe cannot be imported as a package, vendor the MIT `BasicTokenizer.encode` loop with a license comment and inject `merges`/`vocab`. If even that cannot represent our dictionary, record a limitation and keep the reference-oracle tests as the correctness evidence.

## Files likely to change

```text
26455900-CS345/tests/test_transducer_minbpe.py
26455900-CS345/tests/minbpe_adapter.py
26455900-CS345/README.md
```

## Acceptance criteria

- [ ] On Example 2 / unary / empty dictionary, token sequences match when the adapter can load merges
- [ ] Comparison is on tokens, not only decoded text
- [ ] Source and license are identified

## Required test evidence

### Differential or exhaustive tests

- `{a,b}^{≤6}` Example 2 if the adapter works

## Documentation changes

- [x] Public API or README (attribution)

## Validation commands

```bash
cd 26455900-CS345
uv run pytest tests/test_transducer_minbpe.py
make check
```

## Risks

- Compatibility: HF-style global min-rank vs SentencePiece; for **proper** dictionaries they coincide ([6] Lemma 1)
- Scope: do not fake agreement

## Open questions

Whether minbpe exposes merge loading — resolve during implementation; do not block TICKET-010.

## Definition of done

- [ ] Adapter or documented limitation.
- [ ] Tests or explicit skip-with-reason only if loading is impossible.
- [ ] `make check` passes.
