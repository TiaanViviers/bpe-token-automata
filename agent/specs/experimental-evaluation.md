# Experimental evaluation (Section 7)

Engineering specification for the compulsory experimental evaluation: measurements, method, and the six minimum questions in course spec §7. This phase does not introduce a new automaton model and does not write the Section 9 PDF report.

## Goal

Produce machine-readable construction and tokenization measurements, with documented method and honest timeouts, so that course spec §7.3 questions 1–6 can be answered from files in the repository. Assessable documentation is a Markdown evidence note with tables generated from those files, not plots.

Questions 1, 2, and 4 are already answered by the committed Section 5.6 timeout study. This spec covers reuse of that study plus the missing artefacts for questions 3, 5, and 6.

## Background

- **Course requirement:** spec §7.1–7.3 (PDF pp. 7–8): construction time, peak memory, state count (sink separate), explicit vs default transitions, tokenization throughput with unit stated, exact token-sequence match rate, failure boundary (dictionary prefix **or** input size). Method: host metadata, construction separated from serialisation/Graphviz, identical prefixes when comparing, median of short repeats, do not average timeouts, raw CSV or JSON, generate report tables from those files. Six minimum questions.
- **Already implemented:** §5.4 thin tokenize timings (`experiments/transducer_tokenize.py`); §5.5 toy compact compare (`experiments/compact_compare.py`); §5.6 timeout study (`experiments/timeout_study.py` and committed JSON/CSV). Section 6 tests already show exact transducer/reference agreement on bounded sets.
- **Locked decisions already in force:** D1/D5 UTF-8 bytes; D2 SentencePiece \(T^D\); D9 no pre-tokenization; D14 no trim; D33–D35 compact O1 on, O2/O3 default on, O4 out; D44–D52 timeout-study method; D57 huge \(n\) and throughput belong to §7 Q6, not `make test`; D58 test matrix in `docs/testing.md`.

ASSUMPTIONS (locked with the human as D59–D68):

1. Do **not** rerun the 10-minute timeout study. Q1, Q2, Q4 tables are derived from committed `timeout_study.json` / `.csv`.
2. Q6 varies **input length** on small in-tree dictionaries. Do not compile GPT-2 / SmolLM transducers.
3. Throughput unit is **input bytes per second**.
4. Tokenize peak memory is **tracemalloc** (documented in-process equivalent). Construction scaling memory remains RSS from §5.6. Do not mix the two series.
5. No matplotlib and no committed PNG plots. Tables live in `docs/experiments.md`.
6. `make check` stays fast: pytest smokes only.

## Scope

- Shared experiment helper for host metadata, warmup/median timing, and tracemalloc.
- Rule-pattern study (Q3): per-rule `n_fresh` for baseline vs compact on paper/project fixtures and on GPT-2 / SmolLM prefixes of 250 rules; O2/O3 on vs off on the paper chain.
- Output-agreement artefact (Q5): exact token-sequence match rate on the same comparable sets as Section 6 (Example 2 `{a,b}^{\le 8}`, unary \(a^{\le 8}\), minbpe `{a,b}^{\le 6}`).
- Tokenize throughput study (Q6): bytes/s vs length on ordinary `(ab)^{n/2}` and pathological \(a^n\), transducer vs reference vs minbpe where the adapter applies, 60 s per-row cap.
- Assessable `docs/experiments.md` with one table per §7.3 question, README pointer, design-decisions §7 note.
- Pytest schema/smoke for the new runners. Long runs are explicit commands.

## Non-goals

- Matplotlib, committed PNG/PDF plots, or a plot dependency.
- Rerunning `experiments/timeout_study.py`.
- Expanding `transducer_tokenize.py` or `compact_compare.py` into the scaling study (cite them as §5.4/§5.5 toys).
- GPT-2 / SmolLM transducer compile or tiktoken / Hugging Face `encode()`.
- O4, compact flag sweep beyond the Q3 chain ablation, Graphviz in timings, library CLI.
- Changing Algorithm 2, the compact construction, or the tokenizer.
- Section 9 PDF report chapter (tables here are copied into the report later).
- Extensions 8.2 / 8.11.
- Averaging timeouts into successful medians.
- Treating tiny-dictionary RSS as a compact-vs-baseline memory comparison (use §5.6 RSS).

## Authoritative sources

| Source | What it governs |
|---|---|
| Course spec §7.1–7.3 (PDF pp. 7–8); §5.4 performance; §5.6 | Compulsory measurements, method, six questions |
| Course spec §6.2–6.3, §6.6 | Comparable agreement sets; pathological input families for Q6 |
| [5] Corollary 14 | Linear tokenize after compile; compiled state space may still be large |
| [4] Algorithm 2, O2/O3 | Compact state avoidance and clean-copy reuse (Q3) |
| D1, D9, D49, D57, D59–D68 | Bytes, no pre-tokenization, timeout-study repeats, Q6 deferred then specified |
| Existing `construct_token_dfa` / `construct_compact_token_dfa` / `compile_tokenizer` / `tokenize` / `tokenize_reference` | Constructions and tokenizers under test |

**Course vs tests.** Section 6 is correctness evidence. Section 7 requires **files** that report match rate, throughput, and failure boundaries. Do not replace JSON with “see pytest”.

## Interfaces

No change to the public `bpe_token_automata` API. Experiment-only surfaces:

```text
experiments/host.py                 # host metadata, timing, tracemalloc, CSV/JSON write
experiments/rule_patterns.py        # Q3 runner
experiments/tokenize_eval.py        # Q5 + Q6 runner

experiments/results/rule_patterns.json
experiments/results/rule_patterns.csv
experiments/results/output_agreement.json
experiments/results/output_agreement.csv
experiments/results/tokenize_throughput.json
experiments/results/tokenize_throughput.csv

# reused, not regenerated in this phase:
experiments/results/timeout_study.json
experiments/results/timeout_study.csv

docs/experiments.md
```

Q3 row (one per applied rule):

```text
case, o2_state_avoidance, o3_clean_copy, rule_index, self_merge,
baseline_n_fresh, baseline_n_states,
compact_n_fresh, compact_n_states, compact_n_defaults,
compact_reused   # compact_n_fresh == 0
```

Q5 row:

```text
set, n_strings, n_exact_sequence_match, match_rate, comparators
```

Q6 row:

```text
case, dictionary, kind, n_bytes, implementation, status,
tokenize_seconds_median, bytes_per_second_median, tokenize_peak_bytes,
compile_seconds_median
```

`status` in `{ok, timeout_60s}`. Timeouts omit medians (JSON `null`); they are not filled with estimates.

Reuse:

- `parse_dictionary_path`, `Dictionary(rules[:n])`
- `construct_token_dfa` / `construct_compact_token_dfa` / `CompactOptions`
- `ConstructionStep.n_fresh`, `CompactStep.n_fresh`
- `compile_tokenizer` / `tokenize` / `tokenize_reference`
- `tests/minbpe_adapter.py` `LoadedBasicTokenizer` (experiment-only import from tests path)
- committed `timeout_study.json` for Q1/Q2/Q4 tables

## Invariants

- Tokens remain `bytes`. Throughput uses input **byte** length.
- Compact `n_states` excludes the distinguished sink.
- Construction time in §5.6 is incremental wall-clock from \(A_0\) after parse; tokenize time excludes compile and Graphviz (none).
- Shared §5.6 comparison rows exist only for prefixes both constructions finished.
- Tokenize Q6: compile once per dictionary; warmup one tokenize; 7 timed repeats; median of successful samples only when all repeats finish inside the 60 s row budget.
- Peak tokenize memory is tracemalloc in the measuring process, not RSS. Optional RSS may be recorded but must not be compared with §5.6 child RSS as if they were the same quantity.
- Q5 match rate is exact token-sequence equality. A rate other than 1.0 on the stated sets is a bug.
- Q3 `compact_reused` means `n_fresh == 0` for that compact merge (O2 avoidance or O3 clean-copy). It is not a language-equivalence claim.
- GPT-2 / SmolLM Q3 uses prefix 250 only. That is evidence about those prefixes, not all BPE dictionaries.
- Host metadata is recorded on every new JSON payload. If the host differs from the timeout-study host, both are stated; RSS series are not mixed.

## Error and edge behaviour

| Case | Behaviour |
|---|---|
| Q6 row exceeds 60 s wall-clock including warmup and repeats | Interrupt; `status=timeout_60s`; no median |
| Reference or transducer slower than 60 s on one call | Same timeout status |
| Empty input (\(n=0\)) | Allowed in Q5 enumerations; Q6 lengths start at 256 |
| Improper dictionary | Constructors already raise; these runners only load committed proper files |
| minbpe adapter cannot inject a token | Skip minbpe for that dictionary; record why; do not invent encodings |
| Timeout study file missing | Q1/Q2/Q4 docs cannot be written; do not estimate counts from [4] |
| `make check` | Must not run prefix-250 or length-65536 work |

## Testing and acceptance

Independent evidence already exists for constructions and tokenizers (Section 6). New tests check the **harness**, not a second oracle.

- `host_metadata()` contains python, platform, processor, cpu_count, host_memory_bytes, and library versions.
- Q3 smoke: Example 2 prefix 0 has no steps; after one rule, required keys exist; `self_merge` is true for `a ⫽ a`.
- Q5 smoke: `{a,b}^{\le 2}` match rate is 1.0 vs reference.
- Q6 smoke: `n=8`, 1 repeat, Example 2, finishes quickly and reports `bytes_per_second_median` with unit implied by the field name.
- JSON/CSV schema keys match the interfaces above.
- `make check` does not call the full prefix-250 or full length ladder.

## Risks

- Reference tokenizer on \(a^{65536}\) with doubling/unary may hit 60 s; that is a valid input-size failure boundary.
- Tiny-dictionary compact construction can look slower than baseline because of Python overhead; scaling answers come from §5.6, not `compact_compare.json`.
- `SIGALRM` is Unix-specific; this project’s recorded host is Linux.
- Q3 prefix 250 does not explain every later GPT-2 rule.

## Open questions

None blocking after D59–D68.

## Validation commands

```bash
cd 26455900-CS345
make check
uv run python experiments/rule_patterns.py
uv run python experiments/tokenize_eval.py
# do not run unless a human asks:
# uv run python experiments/timeout_study.py
```
