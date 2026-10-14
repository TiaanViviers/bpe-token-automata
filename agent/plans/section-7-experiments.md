# Section 7 — Experimental evaluation

Planning document for the compulsory experimental overlay on Sections 5.4–5.6.

## Metadata

| Field | Value |
|---|---|
| **Status** | `approved` — blocking decisions D59–D68 locked 2026-09-19 |
| **Spec section** | Course spec §7.1–7.3 (PDF pp. 7–8); §5.4 performance; §5.6 timeouts; §9.1 experimental method (tables only, not the PDF) |
| **Primary sources** | Course spec; [`../specs/experimental-evaluation.md`](../specs/experimental-evaluation.md) |
| **PDF check** | Course spec PDF pp. 7–8 verified 2026-09-19 (Markdown §7.1 table is garbled; PDF layout used) |
| **Tickets** | TICKET-020 helper; TICKET-021 Q3; TICKET-022 Q5+Q6; TICKET-023 docs |

## What Section 7 requires

Measure constructions and tokenizers with a stated method, keep raw JSON/CSV in the repository, and answer six questions. This is not a new tokenizer. Plots are deferred to the PDF report. Confirmed 2026-09-19: tables in `docs/experiments.md` only.

Q1, Q2, Q4 already have committed timeout-study files. Remaining work is Q3, Q5 as a match-rate file, Q6 throughput vs length, shared host/timing helpers, and the evidence document.

## Human locks (2026-09-19)

- Reuse committed `timeout_study.json`; do not rerun the 10-minute study.
- No matplotlib; no committed PNG plots.
- `make check` stays fast.
- Leave `transducer_tokenize.py` and `compact_compare.py` as §5.4/§5.5 toys.

## Decision register

| # | Decision | Blocking? | Status | Decision | Rationale |
|---|---|---|---|---|---|
| D59 | Reuse 5.6 | yes | `decided` | Do not rerun `timeout_study.py`. Q1/Q2/Q4 from committed JSON/CSV. If a later host differs, record both; do not mix RSS series | Study already answers growth, compact reduction, failure boundary |
| D60 | Q6 domain | yes | `decided` | Input length on Example 2, unary, doubling, empty dict. No GPT-2/SmolLM transducer compile | Spec Q6 is length, not dictionary size; 5.6 already excluded the transducer from large prefixes |
| D61 | Throughput unit | yes | `decided` | Input bytes per second = `n_bytes / median_seconds` | D1 is a byte alphabet; do not report characters/s |
| D62 | Tokenize method | yes | `decided` | Compile once. Warmup once, 7 repeats, median. Peak memory = tracemalloc. Optional process RSS must not be compared with §5.6 child RSS | Spec allows a documented language-specific equivalent; tiny-dict RSS is interpreter noise |
| D63 | Q6 lengths and timeout | yes | `decided` | \(n \in \{256, 1024, 4096, 16384, 65536\}\). Ordinary: `(ab)^{n/2}` on Example 2 (empty dict as a no-merge control). Pathological: \(a^n\) on unary and doubling. 60 s row cap; `timeout_60s` is the input-size boundary; do not average timeouts | D57 deferred huge \(n\) here; spec §7.1 failure boundary includes input size |
| D64 | Q5 artefact | yes | `decided` | Match rate on Example 2 `{a,b}^{\le 8}` (511), unary \(a^{\le 8}\) (9), minbpe `{a,b}^{\le 6}` (127). Columns `n_strings`, `n_exact_sequence_match`, `match_rate`. Expect 1.0 | Spec wants a match-rate file; tests remain the broader evidence |
| D65 | Q3 artefact | yes | `decided` | Per-rule `n_fresh` / `n_states`; `u=v` vs `u\neq v`; compact flags. Cases: Example 2, unary, paper chain, doubling; O2/O3 on vs off on the chain; GPT-2 and SmolLM prefix **250**. `compact_n_fresh == 0` counts as reuse/avoidance | Steps already exist on `ConstructionStep` / `CompactStep`; no API change |
| D66 | Docs location | yes | `decided` | Assessable `docs/experiments.md`; README pointer; no PDF chapter in this phase | Counterpart of D58 / `docs/testing.md` |
| D67 | pytest vs study | yes | `decided` | `make check` smokes only (tiny dict, tiny \(n\), 1 repeat). Full Q3/Q6 are extra commands | Same split as D52 |
| D68 | Non-goals | yes | `decided` | No matplotlib, no new runtime dep, no library CLI, no Graphviz timings, no O4, no tiktoken encode, no 8.2/8.11, no 5.6 rerun, no Algorithm 2 rewrite | Keep scope to evaluation artefacts |

## Tickets

1. TICKET-020 — `experiments/host.py` and smoke
2. TICKET-021 — `rule_patterns.py` (depends on 020)
3. TICKET-022 — `tokenize_eval.py` Q5+Q6 (depends on 020)
4. TICKET-023 — `docs/experiments.md`, README, design-decisions (depends on 021+022 result files)

Human review of Q3 classification and Q6 timeouts after the full experiment commands, before treating numbers as report-ready.

## Non-goals

New algorithms, CLI, plot generation, rerunning §5.6, expanding the toy 5.4/5.5 scripts into this study, product equivalence on realistic dictionaries, the PDF report, extensions 8.2/8.11.
