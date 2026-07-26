# Testing and Correctness Rules

## Purpose

Testing in this project is evidence for formal and semantic correctness.

The objective is not to maximise test count. Different test families should expose different classes of faults.

Passing tests does not replace understanding of the implemented construction.

## Independent evidence

Avoid correlated validation.

Do not allow the same implementation logic to generate:

- the implementation;
- the reference oracle;
- expected fixtures;
- and the correctness conclusion.

Prefer independent paths:

```text
Direct reference tokenizer
Paper-derived worked examples
Automaton construction
Exhaustive bounded enumeration
Product-automaton equivalence
Property-based generation
```

Agreement between independent methods is stronger than duplicated logic.

## Required test families

Depending on the component, use a justified combination of:

- unit tests;
- regression tests;
- differential tests;
- exhaustive bounded tests;
- property-based tests;
- fuzz tests;
- negative tests;
- Unicode and emoji tests;
- automata equivalence tests;
- pathological robustness tests;
- benchmark smoke tests.

Not every ticket requires every family.

The ticket or test plan should state which fault classes matter.

## Unit tests

Unit tests should isolate specific semantics or representation invariants.

Examples include:

- dictionary rule ordering;
- malformed or improper dictionaries;
- missing transitions;
- accepting-state inheritance;
- state reachability;
- deterministic serialisation;
- default transition behaviour;
- token identity.

Avoid unit tests that reproduce the full implementation line by line.

## Regression tests

Every significant bug should produce a minimal permanent regression case.

A regression test should record:

- the smallest known triggering dictionary;
- the input or token sequence;
- expected behaviour;
- the original failure class;
- fixed seed where relevant.

Do not remove a regression test merely because a refactor makes it inconvenient.

## Differential testing

For each raw string `w`, compare the transducer output with the independent reference tokenizer.

Check:

- exact token-sequence equality;
- every output token is valid;
- detokenisation equals `w`;
- the canonical token sequence is accepted by the token DFA;
- altered non-canonical boundaries are rejected where applicable.

Equality of detokenised strings is necessary but insufficient.

## Exhaustive bounded testing

For small alphabets and dictionaries:

- enumerate every raw string up to a declared bound;
- compare the independent tokenizer and transducer;
- test DFA acceptance of canonical token sequences;
- where feasible, enumerate token sequences;
- verify uniqueness of accepted tokenisation for each underlying string.

Bounds must be stated explicitly.

Do not imply exhaustive verification beyond the tested bound.

## Property-based testing

Use Hypothesis or an equivalent generator for random small instances.

Generators should preserve intended preconditions.

For proper dictionaries, construct rules incrementally from tokens already available.

Useful properties include:

- `detokenize(tokenize(w)) == w`;
- canonical stability;
- DFA acceptance of canonical output;
- uniqueness within the tested bound;
- baseline and compact agreement;
- deterministic serialisation;
- reproducibility from a recorded seed.

When a generated failure is found, preserve the reduced counterexample as a regression fixture.

## Negative testing

Explicitly test invalid inputs and unsupported behaviour:

- malformed dictionaries;
- improper dictionaries;
- duplicate rules;
- unsupported encodings;
- invalid token sequences;
- missing required transitions;
- corrupt serialised automata.

The implementation must not silently reinterpret malformed input.

## Special semantic cases

Give dedicated coverage to:

- empty dictionaries;
- no-op merges;
- self-merges where `u = v`;
- distinct merges where `u ≠ v`;
- loops;
- multiple incoming transitions;
- final and non-final intermediate states;
- useful and useless rules;
- Unicode code points;
- emoji and multi-byte encodings;
- partial transition semantics;
- default transitions;
- sink or reject handling.

## Equivalence testing

Baseline and compact automata should be compared semantically.

Use complementary methods:

1. exhaustive bounded token-sequence comparison;
2. product-automaton symmetric-difference emptiness where practical.

Do not compare raw transition tables as evidence of semantic equivalence.

When default transitions are involved, evaluate the extended transition semantics correctly.

State any limits caused by:

- alphabet size;
- partial functions;
- expansion cost;
- timeout;
- memory.

## Pathological testing

Include structured stress cases such as:

- repeated-character strings;
- nested self-merge chains;
- long inputs without pre-tokenisation boundaries;
- inputs whose initial stable token changes after later input;
- mixed Unicode;
- combining marks;
- whitespace;
- emoji;
- malformed dictionaries.

Separate correctness tests from large performance experiments.

## Determinism and reproducibility

Randomised tests must record seeds.

Failure records should include:

- dictionary;
- seed;
- input;
- expected result;
- observed result;
- smallest known counterexample.

Serialised fixtures and generated summaries must use stable ordering.

## Timeouts and failures

Timeouts, memory exhaustion, unsupported inputs, and failed experiments are results.

Do not:

- omit them;
- replace them with estimates;
- average them into successful measurements;
- label them as success.

Tests should fail clearly when a required computation does not complete.

## Test organisation

Prospective recommended organisation (create directories only when they contain meaningful tests):

```text
project/tests/
├── unit/
├── regression/
├── exhaustive/
├── property/
├── equivalence/
└── fixtures/
```

This layout is not required to exist yet. Place new tests under `project/tests/` in a clear location and expand the tree when families are introduced.

Test names should describe the semantic behaviour being checked.

## Running tests

From `project/`:

```bash
make test
make check
```

Run focused tests during development, but run `make check` before handoff for ordinary source changes.

## Modifying tests

Do not weaken or delete a failing test to obtain a green build unless:

- the test is demonstrably incorrect;
- the corrected expectation is justified;
- the reason is documented;
- relevant formal sources are consulted where needed.

A change to expected formal behaviour requires human review.

## Test evidence in documentation

For major components, record:

- test family;
- fault class targeted;
- number of cases;
- bounds;
- seeds;
- outcome;
- limitations.

Screenshots are not a substitute for machine-readable logs.

## Completion standard

A correctness-sensitive task is not complete until:

- relevant invariants are identified;
- suitable independent tests exist;
- edge cases are covered;
- failures are reproducible;
- checks pass;
- limitations are reported honestly;
- both partners can explain why the evidence is convincing.
