# Section 6 — Testing and verification

Planning document for the compulsory testing overlay on Sections 5.1–5.6.

## Metadata

| Field | Value |
|---|---|
| **Status** | `approved` — blocking decisions D53–D58 locked 2026-09-14 |
| **Spec section** | Course spec §6.1–6.7 (PDF pp. 5–6); §9.1 testing methodology |
| **Primary sources** | Course spec; [`../rules/testing-and-correctness.md`](../rules/testing-and-correctness.md) |
| **Coverage audit** | [`section-6-testing-audit.md`](section-6-testing-audit.md) |
| **PDF check** | Course spec Markdown conversion used for planning; §6 bullets match the 2026-09-14 audit |
| **Tickets** | TICKET-017 gap-fill 6.1–6.5; TICKET-018 pathological 6.6; TICKET-019 test matrix 6.7 |

## What Section 6 requires

Prove the Section 5 constructions with independent evidence families (unit/regression, differential vs \(T^D\), exhaustive bounded, property-based, automata equivalence, pathological), then put a concise matrix in the submission. This is not a new tokenizer or automaton.

Most of 6.1–6.5 already exists from TICKET-004 / 010 / 014. Remaining work is gap-fill, a 6.6 suite, and the 6.7 matrix.

## Human locks (2026-09-14)

- Keep pytest + Hypothesis + the minbpe adapter. No new testing framework.
- Do not split `tests/` into family directories.
- Do not treat the §5.6 timeout study as §6.6.

## Decision register

| # | Decision | Blocking? | Status | Decision | Rationale |
|---|---|---|---|---|---|
| D53 | Exhaustive bound | yes | `decided` | Example 2: all \(w\in\{a,b\}^{\le 8}\). Unary stays \(\le 8\) | Spec’s example length; \(2^8\) is cheap |
| D54 | Uniqueness method | yes | `decided` | For each \(w\), every composition into non-empty byte pieces (\(2^{n-1}\) splits); exactly one accepted, equal to \(T^D(w)\) | Closes the \(\Gamma^{\le 4}\) hole; matches “enumerate token sequences per underlying string” |
| D55 | Equivalence methods | yes | `decided` | Keep `languages_agree` (\(\delta^\nu\) product BFS). Add `expand_defaults` then TokenDFA–TokenDFA product on small alphabets. Never product-expand GPT-2 / SmolLM | Spec §6.5 two methods; large \(\Gamma\) is a stated limitation |
| D56 | Hypothesis | yes | `decided` | `@settings(seed=0, derandomize=True, deadline=None, max_examples=40)`; draw strings from the generated alphabet; uniqueness via compositions; pytest/Hypothesis shrink is the failure log; freeze a shrink as a regression if one appears | Spec §6.4 reproducibility; TICKET-010 seed never landed |
| D57 | Pathological sizes | yes | `decided` | `make test`: \(n\in\{8,16,32,64\}\) for \(a^n\); doubling chain of four rules; one unspaced length-64 `{a,b}` string. Huge \(n\) is §7 Q6 | Spec §6.6 without bloating `make check` |
| D58 | Matrix location | yes | `decided` | Assessable `docs/testing.md` from a real `make test` run; README pointer; PDF report copies it | Spec §6.7; screenshots are not evidence |

## Tickets

1. TICKET-017 — helpers, useful/useless language, exhaustive 6.2/6.3, Hypothesis, expand-defaults language
2. TICKET-018 — `tests/test_pathological.py` (depends on 017 helpers)
3. TICKET-019 — `docs/testing.md` matrix (depends on 017+018)

Human review after TICKET-017 / `make check` if the composition uniqueness helper looks wrong; otherwise 017 → 018 → 019 on `main`.

## Non-goals

New algorithms, CLI, test-directory reshuffle, using `apply_merge` as the expected-answer oracle, product equivalence on realistic dictionaries, 10-minute pytest, the PDF report chapter beyond `docs/testing.md`, extensions 8.2/8.11.
