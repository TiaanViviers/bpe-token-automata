# TICKET-002: Token DFA model and Algorithm 2 constructor

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Implement `TokenDFA`, universal and user-supplied base DFAs, `apply_merge` as Algorithm 2 of [5], and `construct_token_dfa` that applies every dictionary rule in order and rejects improper dictionaries.

## Background

Section 5.2 successive-merge construction. Engineering spec: [`../specs/baseline-token-automaton.md`](../specs/baseline-token-automaton.md).

## Authoritative sources

- Project specification: §5.2, §4.3
- Paper and section: [5] Algorithm 2 (PDF p. 4), Remarks 2–3, Theorem 4
- Approved decision: [`../plans/section-5-2-baseline-token-dfa.md`](../plans/section-5-2-baseline-token-dfa.md) D13–D22
- Existing implementation/documentation: 5.1 `Dictionary`, `MergeRule`, `validate_proper`, `TokenSequence`

## Scope

The ticket includes:

- Frozen `TokenDFA` with partial \(\delta\), `step`, `accepts`
- `universal_token_dfa(alphabet)`
- `from_string_dfa` / YAML parser for user-supplied bases
- `apply_merge` following Algorithm 2 line order, including \(u=v\) inheritance and line-19 redirect over fresh states
- `construct_token_dfa` returning all \(A_i\) and per-rule counts (counts may be filled in TICKET-003 if the result type lives here)
- `TokenDFAError` for malformed bases / conflicting \(uv\) transitions
- Reject improper dictionaries

## Non-goals

The ticket explicitly excludes:

- Graphviz
- Serialisation string format (TICKET-003)
- Exhaustive/paper tests beyond what is needed to compile (TICKET-004)
- Trimming, CLI, transducer

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded.
- [x] Required interfaces or dependencies exist.
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved.

## Proposed design

See engineering spec. `apply_merge` copies \(\delta\) into a mutable dict, then: collect \(S\) in state-id order; add \(uv\) edges; add \(uv\) to \(\Gamma\); allocate fresh ids for sorted \(S_2\); copy outgoing except excluded labels; redirect every \(\delta(q,u)\in S_2\).

Do not import `tokenize_reference`.

## Files likely to change

```text
26455900-CS345/src/bpe_token_automata/automaton/
26455900-CS345/src/bpe_token_automata/__init__.py
26455900-CS345/data/automata/
```

## Acceptance criteria

- [ ] Universal one-state DFA over a given \(\Sigma\)
- [ ] User-supplied string DFA via Python and YAML
- [ ] `apply_merge` matches Algorithm 2 including \(u=v\)
- [ ] `construct_token_dfa` rejects improper \(D\)
- [ ] Empty \(D\) leaves the base automaton unchanged
- [ ] No trim

## Required test evidence

Covered primarily by TICKET-004. This ticket may include smoke tests for constructors.

## Documentation changes

- [ ] Architecture in `docs/design-decisions.md` (TICKET-003/docs pass)

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Risks

- Formal interpretation: line 19 over fresh states; Example 2 “non-ba” prose
- Correctness: conflicting \(uv\) on non-CI inputs
- Performance: not a goal; tiny dictionaries only
- Scope: do not start the transducer

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] Relevant documentation updated.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Both partners can explain the implementation.
