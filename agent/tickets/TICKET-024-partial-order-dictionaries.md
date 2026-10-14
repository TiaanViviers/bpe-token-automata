# TICKET-024: §8.6 byte-disjoint partial orders

## Status

```text
ready
```

## Owner

- Human owner: Lenz (implementation), Tiaan (review after the code lands)
- Supporting partner:
- Agent use: do not implement this ticket in the planning session

## Goal

Implement specification §8.6 for one restricted class: byte-disjoint base
rules under an explicit precedence relation. Every linear extension is checked
with the existing §8.2 comparison. A general DAG semantics is out of scope.

The build contract is
[`agent/plans/section-8-6-partial-order.md`](../plans/section-8-6-partial-order.md).
That document is authoritative for API shape, tests, and rejection criteria.
This ticket only records status and the gate.

## Background

§8.2 compares two total orders. §8.6 asks whether every linear extension of a
partial order agrees. The specification treats a general DAG as a change of
BPE semantics and names a restricted class as the concrete extension.

## Authoritative sources

- Project specification: §8.6
- Paper and section: Berglund & van der Merwe, EPTCS 388, 2023, Definition 5
  (`validate_proper`); Berglund, Martens & van der Merwe, TCS 1083, 2026,
  Algorithm 2 (`construct_token_dfa`)
- Approved decision: restricted byte-disjoint class, agreed 2026-10-05
- Existing implementation/documentation:
  `26455900-CS345/src/bpe_token_automata/dictionary_equivalence.py`,
  `26455900-CS345/docs/extensions.md`

## Scope

The ticket includes:

- `partial_order.py` with `OrderedRules`, `LinearExtensionResult`,
  `is_byte_disjoint_base`, `linear_extensions`, and `check_linear_extensions`
- tests in `tests/test_partial_order.py` as listed in the plan
- README, `docs/extensions.md`, and `docs/testing.md` updates
- package exports

## Non-goals

The ticket explicitly excludes:

- general dependency DAGs, multi-byte component rules inside the safe class,
  a new `apply_merge`, fused Algorithm 2 steps, and any change to the §8.2
  product unless a bug actually blocks the new caller

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [ ] `26455900-CS345/` is on `main` and its working state is understood.
- [ ] Pre-existing changes have been identified and can be preserved.

## Proposed design

See the plan. Flags `disjoint_class` and `extensions_agree` are independent.
Precedence pairs are `(earlier, later)`. Emitted dictionaries are re-indexed
from 0. The extension cap is 24. Improper extensions are reported, not turned
into a fake byte counterexample.

## Files likely to change

```text
26455900-CS345/src/bpe_token_automata/partial_order.py
26455900-CS345/src/bpe_token_automata/__init__.py
26455900-CS345/tests/test_partial_order.py
26455900-CS345/docs/extensions.md
26455900-CS345/docs/testing.md
26455900-CS345/README.md
```

## Acceptance criteria

- [ ] Byte-disjoint rules `a⫽b`, `c⫽d` have two extensions, both tokenize
      `abcd` as `(ab, cd)`, and the token DFAs agree.
- [ ] `a⫽b`, `b⫽a` is outside the class and disagrees on `aba` with tokens
      `(ab, a)` versus `(a, ba)`, and `dfa_witness` is accepted by exactly one DFA.
- [ ] Precedence `(0, 1)` on three disjoint rules yields exactly
      `(0,1,2), (0,2,1), (2,0,1)`.
- [ ] A cycle and a 5-rule antichain raise `ValueError`.
- [ ] `ab⫽c` with `d⫽e` yields `extensions_agree is None` and an improper
      extension, with no byte counterexample.
- [ ] Docs state the class, the cap, the bounds, and the citations, and do
      not claim a general DAG result.
- [ ] `docs/testing.md` count and runtime come from the `make check` run that
      validates the commit.

## Required test evidence

### Unit tests

Lexicographic extensions, precedence filtering, re-indexing, cycle, cap,
byte-disjoint classification.

### Regression tests

`aba` token sequences `(ab, a)` and `(a, ba)`. Improper `ab⫽c` extension.

### Differential or exhaustive tests

`{a,b,c,d}` strings of length at most 4 for the two-rule disjoint pair, plus
`check_token_dfa=True` language agreement via `compare_dictionaries_bounded`.

### Property or equivalence tests

Not required beyond the product check above. Do not add a Hypothesis grammar
for partial orders in this ticket.

### Negative and special cases

Empty inputs raise. One-rule poset is vacuous and must not be described as
commutation evidence. Overlapping rules stay outside `disjoint_class`.

## Documentation changes

- [x] Public API or README
- [x] Architecture or algorithm documentation
- [ ] Decision record
- [x] Testing documentation
- [ ] Experiment documentation
- [x] Known limitations

State specific expected updates:

`docs/extensions.md` §8.6, README status line, `docs/testing.md` matrix row
and a freshly recorded pytest count.

## Validation commands

```bash
cd 26455900-CS345
uv run pytest tests/test_partial_order.py
make check
```

## Risks

- Formal interpretation: calling a general DAG solved, or calling one linear
  extension “commutation”.
- Correctness: reusing `MergeRule.index` from the caller; treating improper
  extensions as tokenization mismatches; a witness both DFAs accept.
- Performance: uncapped `n!` DFA builds.
- Compatibility: behaviour change inside `compare_dictionaries_bounded`.
- Scope: a new merge algorithm.
- Reproducibility: copied pytest timings.

## Open questions

None. The class, cap, and API flags in the plan are decided.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] Relevant documentation updated.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Handoff produced where appropriate.
- [ ] Human review completed.
- [ ] Both partners can explain the implementation.
