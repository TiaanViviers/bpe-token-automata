# TICKET-001: Dictionary model and reference tokenizer (Section 5.1)

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Implement Section 5.1: typed BPE dictionary model, parser (merge list + YAML), proper-dictionary validator, and independent reference tokenizer using SentencePiece semantics `T^D` over UTF-8 bytes.

This delivers the correctness oracle for baseline DFA (5.2), transducer (5.4), differential tests (6.2), and extension 8.2.

## Background

First compulsory implementation milestone. Scaffolding exists; no tokenizer or dictionary code yet. Design decisions D1–D7 are locked in [`../plans/section-5-1-dictionary-and-reference-tokenizer.md`](../plans/section-5-1-dictionary-and-reference-tokenizer.md).

## Authoritative sources

- Project specification: §5.1, §4.3, §6.1 (improper), §6.2 (oracle)
- Paper and section: Berglund & van der Merwe [6] Definitions 1, 3, 5; Example 1; Example 3 (improper)
- Approved decision: [`../plans/section-5-1-dictionary-and-reference-tokenizer.md`](../plans/section-5-1-dictionary-and-reference-tokenizer.md) (D1–D7)
- Approved decision: [`../plans/approved-extensions-2026-09.md`](../plans/approved-extensions-2026-09.md) (TokenSequence first-class)
- Existing implementation/documentation: package stub only

## Scope

The ticket includes:

- `Token`, `TokenSequence`, detokenize, base tokenization `T_∅`
- `MergeRule`, `Dictionary` immutable model
- Merge-list and YAML dictionary parsers with structured errors
- Proper-dictionary validation (Def. 5)
- Reference tokenizer `T^D` (Def. 3); reject improper dictionaries
- Unit tests and fixtures including paper Example 1
- Promote design summary to `26455900-CS345/docs/design-decisions.md`

## Non-goals

The ticket explicitly excludes:

- Token DFA construction (5.2)
- Transducer (5.4)
- minbpe integration
- Useful-rule API (deferred D8)
- CLI (deferred D11)
- Performance optimisation

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

See locked decisions in planning doc. Summary:

- Alphabet: bytes 0–255; tokens are `bytes`
- Semantics: SentencePiece highest-priority then leftmost merge each step
- Formats: `.merges` text (one `left right` per line) and `.yaml` fixture format
- Errors: `ParseResult` / `ValidationResult` with indexed issues; `ImproperDictionaryError` at tokenize

## Files likely to change

```text
26455900-CS345/src/bpe_token_automata/tokens.py
26455900-CS345/src/bpe_token_automata/reference_tokenizer.py
26455900-CS345/src/bpe_token_automata/dictionary/__init__.py
26455900-CS345/src/bpe_token_automata/dictionary/model.py
26455900-CS345/src/bpe_token_automata/dictionary/errors.py
26455900-CS345/src/bpe_token_automata/dictionary/encoding.py
26455900-CS345/src/bpe_token_automata/dictionary/parser.py
26455900-CS345/src/bpe_token_automata/dictionary/validator.py
26455900-CS345/tests/test_tokens.py
26455900-CS345/tests/test_dictionary_parser.py
26455900-CS345/tests/test_dictionary_validator.py
26455900-CS345/tests/test_reference_tokenizer.py
26455900-CS345/data/dictionaries/example1.merges
26455900-CS345/data/dictionaries/improper_example3.merges
26455900-CS345/docs/design-decisions.md
26455900-CS345/README.md
```

## Acceptance criteria

- [x] Parse merge-list and YAML dictionaries; preserve rule order
- [x] Reject duplicates, malformed lines, empty tokens with structured errors
- [x] `validate_proper` implements Def. 5; rejects Example 3 improper dict
- [x] `tokenize_reference` implements Def. 3; matches paper Example 1 on `abcbcab`
- [x] Empty dictionary returns base tokenization
- [x] `detokenize(tokenize(w)) == w` on fixture strings
- [x] Tokenizer rejects improper dictionary explicitly
- [x] `make check` passes

## Required test evidence

### Unit tests

- Token encoding/decoding, TokenSequence, detokenize
- Parser valid/invalid fixtures
- Validator proper/improper/useless-but-proper

### Regression tests

- Paper Example 1 tokenization steps

### Differential or exhaustive tests

- Deferred to 6.2 (oracle used later)

### Property or equivalence tests

- Deferred

### Negative and special cases

- Improper dict tokenize raises
- Duplicate rule in merge file

## Documentation changes

- [x] Architecture or algorithm documentation — `docs/design-decisions.md`
- [ ] Public API or README — brief pointer to docs
- [x] Decision record — promoted from agent plan
- [ ] Testing documentation — deferred

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Formal interpretation: byte encoding of paper character examples
- Correctness: leftmost+highest-priority loop must match Def. 3 exactly
- Scope: avoid importing future DFA code into reference tokenizer

## Open questions

- D8 useful-rule helper timing — deferred
- D12 full doc promotion — partial via design-decisions.md

## Definition of done

- [ ] Approved scope implemented.
- [x] Acceptance criteria satisfied.
- [x] Required tests added and passing.
- [x] Relevant documentation updated.
- [x] `make check` passes.
- [x] No private workspace material entered `26455900-CS345/`.
- [ ] Handoff produced where appropriate.
- [ ] Human review completed.
- [ ] Both partners can explain the implementation.
