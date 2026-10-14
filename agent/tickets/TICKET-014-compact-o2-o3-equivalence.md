# TICKET-014: O2/O3, equivalence tests, comparison, docs

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Enable Algorithm 2’s O2 (state-avoidance) and O3 (clean-copy reuse) behind `CompactOptions`. Add product-style language equivalence, Hypothesis compact/baseline agreement, a thin prefix comparison experiment, and assessable documentation.

## Background

Depends on TICKET-013’s D²FA and O1 merge. Engineering spec: [`../specs/compact-delayed-input-automaton.md`](../specs/compact-delayed-input-automaton.md). Public defaults: O2 and O3 **on**.

## Authoritative sources

- Project specification: §5.5, §6.4–6.5, §7.1
- Paper and section: [4] Def. 3–4, Algorithm 2 lines 9–24, Lemma 2, Examples 1–2 (PDF pp. 4–5)
- Approved decision: D34, D38, D39
- Existing implementation: TICKET-013; `experiments/transducer_tokenize.py` as the experiment pattern

## Scope

The ticket includes:

- O2: \(S_2'\) = multiple-use wrt \(v\) or \(s_2=q_0\); leftover \(s_2\) get sink on \(v\) (and \(uv\) iff \(u=v\))
- O3: reuse least-id clean-copy (sink labels = O1’s \(\Lambda\), D38)
- `languages_agree` product BFS on small alphabets
- Hypothesis compact vs baseline `accepts`
- Flag-combination language agreement; O2/O3 may reduce `n_states`
- `experiments/compact_compare.py` + JSON on existing small dictionary prefixes
- README status and `docs/design-decisions.md` compact section

## Non-goals

The ticket explicitly excludes:

- O4 / §5.6
- Graphviz, CLI
- 5.3-style examples document
- Changing `TokenDFA`

## Preconditions

Before implementation:

- [x] TICKET-013 constructor exists and O1 vs baseline tests pass.
- [ ] Def. 3–4 PDF interpretation (D38, D39) is followed.

## Proposed design

Implement the coloured lines of Algorithm 2 only. `languages_agree(baseline, compact)` walks pairs of states; `step` None-ness and accepting bits must match for every token in \(\Gamma\). Experiment columns: baseline states, baseline explicit transitions, compact states (exclude sink), compact explicit transitions, default-transition count, construction time, peak memory.

## Files likely to change

```text
26455900-CS345/src/bpe_token_automata/automaton/compact.py
26455900-CS345/tests/test_compact_construction.py
26455900-CS345/tests/test_compact_equivalence.py
26455900-CS345/tests/test_transducer_properties.py
26455900-CS345/experiments/compact_compare.py
26455900-CS345/experiments/results/compact_compare.json
26455900-CS345/docs/design-decisions.md
26455900-CS345/README.md
```

## Acceptance criteria

- [ ] Default public constructor uses O2 and O3
- [ ] Example 1-style dictionary \([a⫽b, ab⫽b, abb⫽b]\) reuses a state with O3
- [ ] All four flag combinations agree on language for Example 2
- [ ] Product emptiness agrees on Example 2
- [ ] Hypothesis compact vs baseline `accepts`
- [ ] Experiment JSON has the required columns
- [ ] Design-decisions records flags, sink, \(\delta^\nu\) equivalence, O4 deferred

## Required test evidence

### Unit tests

- multiple-use / initial-state O2 skip
- clean-copy reuse (O3)

### Property or equivalence tests

- product BFS
- Hypothesis agreement
- exhaustive \(\{a,b\}^{\le 6}\) on Example 2

### Negative and special cases

- Unicode fixture compact vs baseline on a declared bound

## Documentation changes

- [ ] Public API or README
- [ ] Decision record in `docs/design-decisions.md`
- [ ] Experiment documentation (script docstring + JSON notes)
- [ ] Known limitations (O4 deferred; product on small \(\Gamma\) only)

## Validation commands

```bash
cd 26455900-CS345
make check
uv run python experiments/compact_compare.py
```

## Risks

- Formal interpretation: Def. 3 \(P_{q,u}\)
- Correctness: O3 \(\Lambda\) (D38)
- Performance: experiment is tiny prefixes only; do not claim §5.6

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
