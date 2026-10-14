# TICKET-017: Section 6.1–6.5 testing gap-fill

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Close the §6.1–6.5 holes identified in the coverage audit: useful vs useless language change, full §6.2 checks on exhaustive families, composition uniqueness at bound 8, Hypothesis seed plus uniqueness, and `expand_defaults` language agreement.

## Background

Most unit, differential, exhaustive, Hypothesis, and compact-equivalence tests already exist from TICKET-004 / 010 / 014. They are not a substitute for the missing bullets. Shared helpers (`assert_section_62`, compositions) must live outside a single test module so 6.3 and 6.6 can reuse them.

The 5.1 reference tokenizer remains the oracle. Automaton production code must not import it.

## Authoritative sources

- Project specification: §6.1–6.5
- Paper and section: [5] Algorithm 2; [6] useful/useless remark after Definition 5; [4] Observation 1 (`expand_defaults`)
- Approved decision: D53, D54, D55, D56
- Existing implementation/documentation: `assert_section_62` in `tests/test_transducer_tokenize.py`; `languages_agree`; `proper_with_useless_rule.yaml`

## Scope

The ticket includes:

- Move `assert_section_62` (and first-long-token split) to `tests/differential.py`
- Add `compositions(text) -> Iterable[TokenSequence]` (every split of `text` into non-empty byte pieces)
- Optionally `token_dfa_languages_agree` next to `languages_agree`
- Useful vs useless accepted-language tests
- Named multi-predecessor redirect test for Example 2’s `b`-edges
- Exhaustive Example 2 `{a,b}^{≤8}` and unary `{a}^{≤8}` using the full five §6.2 checks plus composition uniqueness
- Hypothesis: `seed=0`, `derandomize=True`, strings drawn from the generated alphabet, uniqueness via compositions
- `expand_defaults(compact)` language agreement with baseline on Example 2 and unary

## Non-goals

The ticket explicitly excludes:

- §6.6 pathological suite (TICKET-018)
- §6.7 test matrix (TICKET-019)
- Test-directory reshuffle
- Product expansion on GPT-2 / SmolLM
- Changing Algorithm 2 / compact / transducer production semantics
- Raising Hypothesis `max_examples` beyond 40

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

`compositions(w)` yields every `TokenSequence` whose tokens are non-empty contiguous pieces that concatenate to `w` (\(2^{n-1}\) sequences for \(|w|=n\), plus the empty sequence when \(w\) is empty).

For each enumerated `w`:

1. `assert_section_62(dictionary, alphabet, w)`
2. among `compositions(w)`, exactly one is accepted by the token DFA, and it equals \(T^D(w)\)

Useful rule: `D=[a⫽a]` over `{a,b}` — `A_0` accepts `(a,a)` and rejects `(aa)`; `A_1` the reverse.

Useless rule: `proper_with_useless_rule.yaml` last rule `ab⫽cd` — bounded accepted tokenizations of `{a,b,c,d}^{≤8}` agree with the three-rule prefix (via oracle sequences and DFA `accepts`).

`token_dfa_languages_agree(left, right)`: product BFS on the union alphabet, same shape as `languages_agree` but both sides are `TokenDFA.step`.

Hypothesis `@given(proper_dictionaries(), st.integers(min_value=0, max_value=6))` then build `text` by sampling the generated alphabet; drop the unused integer `seed` parameter.

## Files likely to change

```text
26455900-CS345/tests/differential.py
26455900-CS345/tests/test_transducer_tokenize.py
26455900-CS345/tests/test_token_dfa_exhaustive.py
26455900-CS345/tests/test_transducer_exhaustive.py
26455900-CS345/tests/test_transducer_properties.py
26455900-CS345/tests/test_token_dfa_construction.py
26455900-CS345/tests/test_token_dfa_examples.py
26455900-CS345/tests/test_compact_equivalence.py
26455900-CS345/src/bpe_token_automata/automaton/compact.py
26455900-CS345/src/bpe_token_automata/automaton/__init__.py
26455900-CS345/src/bpe_token_automata/__init__.py
```

## Acceptance criteria

- [ ] Exhaustive Example 2 and unary run all five §6.2 checks
- [ ] Uniqueness uses compositions of each `w`, not \(\Gamma^{\le 4}\)
- [ ] Example 2 bound is 8
- [ ] Useless rule does not change bounded accepted language; useful rule does
- [ ] Named multi-predecessor redirect assertion exists
- [ ] Hypothesis uses `seed=0` and `derandomize=True` and checks uniqueness
- [ ] `expand_defaults` language agrees with baseline on Example 2 and unary
- [ ] `make check` passes

## Required test evidence

### Unit tests

- Useful vs useless language
- Named Example 2 multi-predecessor redirect

### Regression tests

- None unless Hypothesis finds a shrink

### Differential or exhaustive tests

- `{a,b}^{≤8}` Example 2; unary `{a}^{≤8}`; full §6.2 + uniqueness

### Property or equivalence tests

- Hypothesis properties including uniqueness; expand-defaults product

### Negative and special cases

- Existing improper/malformed tests stay; do not duplicate

## Documentation changes

- [ ] Decision record: none in the assessable repo (D53–D56 live in `agent/plans/section-6-testing.md`)
- [ ] Testing documentation: deferred to TICKET-019

## Validation commands

```bash
cd 26455900-CS345
make check
```

Additional commands:

```bash
uv run pytest tests/test_token_dfa_exhaustive.py tests/test_transducer_exhaustive.py tests/test_transducer_properties.py tests/test_compact_equivalence.py tests/test_token_dfa_construction.py
```

## Risks

- Formal interpretation: “useful” as BPE-application vs DFA reachable language — lock accepted language / oracle sequences
- Correctness: compositions include splits that are not tokens in \(\Gamma\); `accepts` must reject those
- Performance: `{a,b}^{≤8}` plus \(2^{n-1}\) compositions is fine (\(\sum_n 2^n 2^{n-1}\) small)
- Reproducibility: Hypothesis seed 0
- Scope: do not start 6.6 here

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Both partners can explain compositions uniqueness and useful vs useless.
