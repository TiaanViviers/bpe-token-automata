# TICKET-021: Rule-pattern state growth (Section 7.3 Q3)

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Record, for each merge rule, whether the baseline and compact constructions allocate fresh states, and which compact flags are on. Answer §7.3 question 3 from a JSON/CSV file without changing automaton APIs.

## Background

`ConstructionStep.n_fresh` and `CompactStep.n_fresh` already exist. The timeout study stores prefix totals, not per-rule patterns. D65. Depends on TICKET-020.

## Authoritative sources

- Project specification: §7.3 question 3; §5.5 O2/O3
- Paper and section: [4] Algorithm 2 state-avoidance and clean-copy reuse; [5] Algorithm 2 fresh states
- Approved decision: D65, D67
- Existing implementation: `construct_token_dfa`, `construct_compact_token_dfa`, `CompactOptions`

## Scope

The ticket includes:

- `experiments/rule_patterns.py` writing `experiments/results/rule_patterns.json` and `.csv`
- Cases: Example 2, unary, paper `{a⫽b, ab⫽b, abb⫽b}` chain, doubling; O2/O3 on vs both off on the chain; GPT-2 and SmolLM **prefix 250** with public compact defaults
- Per-rule: `self_merge`, baseline/compact `n_fresh` and `n_states`, compact `n_defaults`, `compact_reused` (`n_fresh == 0`)
- Pytest smoke on Example 2 only (no prefix 250 in `make check`)

## Non-goals

The ticket explicitly excludes:

- Timeout-study rerun
- Language-equivalence claims from `n_fresh == 0`
- O4, Graphviz, CLI
- Q5/Q6
- Docs tables (TICKET-023)

## Preconditions

Before implementation:

- [x] TICKET-020 helper exists (same session).
- [x] `26455900-CS345/` is on `main` and its working state is understood.

## Proposed design

For each case, build baseline and compact from the same base DFA (`universal_token_dfa` on the case alphabet; `byte_alphabet()` for realistic prefixes). Zip baseline `steps` with compact `steps`. Prefix 250 is `Dictionary(rules[:250])`. Main() writes results; smoke calls a function with Example 2.

## Files likely to change

```text
26455900-CS345/experiments/rule_patterns.py
26455900-CS345/experiments/results/rule_patterns.json
26455900-CS345/experiments/results/rule_patterns.csv
26455900-CS345/tests/test_rule_patterns.py
```

## Acceptance criteria

- [ ] JSON includes host metadata and per-rule rows for the listed cases
- [ ] Example 2 first rule is a self-merge with `baseline_n_fresh >= 1`
- [ ] Chain with O2/O3 on shows compact state reuse relative to O2/O3 off or to baseline
- [ ] Prefix 250 is only in the full command, not pytest
- [ ] Compact `n_states` excludes the sink

## Required test evidence

### Unit tests

- Example 2: zero-rule case has no steps; one-rule row has required keys; `a ⫽ a` is `self_merge`

### Negative and special cases

- Do not construct GPT-2 in pytest

## Documentation changes

- Later TICKET-023

## Validation commands

```bash
cd 26455900-CS345
make check
uv run python experiments/rule_patterns.py
```

## Risks

- Prefix 250 baseline is ~5 s; acceptable for the extra command, not for pytest
- `n_fresh == 0` is a size fact, not a proof of O2 vs O3 without the chain ablation

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Full `rule_patterns.py` run committed as JSON/CSV.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
