# Experimental evaluation (Section 7)

Course spec §7.1–7.3. Tables below are copied from the committed JSON/CSV files. Plots are not part of this phase. `make check` does not run the long studies.

**Hosts.** Construction scaling (Q1, Q2, Q4) used the committed Section 5.6 timeout study: Python 3.12.3, Linux 7.0.0-31-generic x86_64, 16 CPUs, 16 129 413 120 bytes RAM. Q3/Q5/Q6 used the same machine class (Python 3.12.3, same kernel string, 16 CPUs, 16 129 409 024 bytes RAM; PyYAML 6.0.3, Hypothesis 6.161.5). Do not mix §5.6 child-process RSS with tokenize `tracemalloc` peaks.

**Runners** (from the repository root):

```bash
uv run python -m experiments.rule_patterns
uv run python -m experiments.tokenize_eval
uv run python experiments/timeout_study.py   # already committed; do not rerun for this document
```

Toy §5.4/§5.5 scripts `experiments/transducer_tokenize.py` and `experiments/compact_compare.py` remain small-dictionary checks, not the scaling answer.

## Method

- Construction time for realistic prefixes is incremental wall-clock from \(A_0\) after parse (no Graphviz). One run per `(dictionary, construction)`; no median of timeouts.
- Short tokenize runs: compile once; one warmup; 7 timed repeats; median. Peak memory is `tracemalloc` in-process (documented equivalent of §7.1 peak memory). Throughput unit: **input bytes per second**.
- 60 s wall-clock cap per Q6 row (warmup + repeats). Timeouts are `timeout_60s` with omitted medians.
- Compact `n_states` excludes the distinguished sink.
- O4 is not implemented. No pre-tokenization. No tiktoken / Hugging Face `encode()`.

## Q1. Baseline state and transition growth

Source: [`experiments/results/timeout_study.csv`](../experiments/results/timeout_study.csv). Shared prefixes only (both constructions finished). Compact columns are listed for later Q2; Q1 is the baseline pair.

| Dictionary | Rules | Baseline states | Baseline explicit transitions | Baseline seconds | Baseline RSS (bytes) |
|---|---:|---:|---:|---:|---:|
| GPT-2 | 0 | 1 | 256 | 0.000308 | 37 818 368 |
| GPT-2 | 10 | 11 | 2 909 | 0.0137 | 37 818 368 |
| GPT-2 | 50 | 51 | 15 209 | 0.151 | 37 818 368 |
| GPT-2 | 100 | 101 | 34 271 | 0.655 | 43 606 016 |
| GPT-2 | 250 | 251 | 119 229 | 5.30 | 87 367 680 |
| GPT-2 | 500 | 501 | 354 881 | 31.1 | 221 048 832 |
| GPT-2 | 1000 | 1 001 | 1 184 546 | 227 | 528 482 304 |
| SmolLM 2 | 0 | 1 | 256 | 0.000371 | 38 080 512 |
| SmolLM 2 | 10 | 11 | 2 908 | 0.0170 | 38 080 512 |
| SmolLM 2 | 50 | 51 | 14 981 | 0.150 | 38 080 512 |
| SmolLM 2 | 100 | 101 | 33 562 | 0.600 | 43 991 040 |
| SmolLM 2 | 250 | 251 | 114 396 | 4.97 | 87 666 688 |
| SmolLM 2 | 500 | 501 | 343 629 | 29.8 | 173 342 720 |
| SmolLM 2 | 1000 | 1 001 | 1 159 037 | 219 | 521 613 312 |

Baseline states track \(n+1\) on these prefixes (one fresh state per rule plus \(A_0\)). Explicit transitions grow much faster than states because \(\lvert\Gamma\rvert\) grows with the dictionary over a 256-byte alphabet.

## Q2. Compact reduction of explicit transitions and memory

Same CSV. Compact `n_states` excludes the sink (`n_sink_states = 1`).

| Dictionary | Rules | Compact states | Compact explicit transitions | Compact defaults | Compact seconds | Compact RSS (bytes) | Transition ratio (baseline / compact) |
|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-2 | 100 | 33 | 514 | 32 | 0.0313 | 38 002 688 | 67 |
| GPT-2 | 250 | 93 | 1 050 | 92 | 0.0814 | 38 002 688 | 114 |
| GPT-2 | 500 | 195 | 2 181 | 194 | 0.247 | 38 002 688 | 163 |
| GPT-2 | 1000 | 385 | 4 877 | 384 | 1.19 | 38 002 688 | 243 |
| SmolLM 2 | 100 | 40 | 565 | 39 | 0.0309 | 37 634 048 | 59 |
| SmolLM 2 | 250 | 93 | 1 188 | 92 | 0.0920 | 37 634 048 | 96 |
| SmolLM 2 | 500 | 199 | 2 440 | 198 | 0.301 | 37 634 048 | 141 |
| SmolLM 2 | 1000 | 404 | 5 482 | 403 | 1.35 | 37 634 048 | 211 |

At 1000 GPT-2 rules the compact RSS is still the process floor (~36 MiB) while baseline RSS is ~504 MiB. Do not cite [`compact_compare.json`](../experiments/results/compact_compare.json) as the scaling answer: on two-rule `{a,b}` dictionaries Python overhead dominates and compact can look slower.

## Q3. Which rule patterns add states vs allow reuse

Source: [`experiments/results/rule_patterns.json`](../experiments/results/rule_patterns.json). `compact_reused` means compact `n_fresh == 0` for that rule (O2 state-avoidance or O3 clean-copy). That is a size fact, not a language claim.

| Case | O2/O3 | Rules | Self-merge | Distinct | Compact reused | Baseline fresh total | Compact fresh total | Baseline states | Compact states |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Example 2 `[a⫽a, b⫽a]` | on | 2 | 1 | 1 | 0 | 2 | 2 | 3 | 3 |
| Unary `[a⫽a, aa⫽a]` | on | 2 | 1 | 1 | 0 | 2 | 2 | 3 | 3 |
| Doubling self-merge chain | on | 4 | 4 | 0 | 0 | 4 | 4 | 5 | 5 |
| Paper chain `[a⫽b, ab⫽b, abb⫽b]` | on | 3 | 0 | 3 | 2 | 3 | 1 | 4 | 2 |
| Same chain | off | 3 | 0 | 3 | 0 | 3 | 3 | 4 | 4 |
| GPT-2 prefix 250 | on | 250 | 6 | 244 | 158 | 250 | 92 | 251 | 93 |
| SmolLM 2 prefix 250 | on | 250 | 6 | 244 | 158 | 250 | 92 | 251 | 93 |

Self-merges on these fixtures always allocated a compact fresh state. The paper chain reuses two states only with O2/O3 enabled. On the 250-rule realistic prefixes, 158/250 compact merges allocated no fresh state; baseline still added one state per rule.

Prefix 250 is not a claim about the rest of GPT-2 / SmolLM 2.

## Q4. Timeout and memory failure boundary

Source: [`experiments/results/timeout_study.json`](../experiments/results/timeout_study.json). Limits: 60 s annotation, 600 s kill, 8 GiB RSS. The 8 GiB cap was **not** hit. `prefix_at_60s` is the last geometric checkpoint with elapsed ≤ 60 s, not a 60 s kill.

| Dictionary | Construction | Prefix at 60 s | Largest prefix ok | Stop | Peak RSS (bytes) |
|---|---|---:|---:|---|---:|
| GPT-2 | baseline | 500 | 1 396 | `timeout_600s` | 975 724 544 |
| GPT-2 | compact | 5 000 | 14 280 | `timeout_600s` | 99 360 768 |
| SmolLM 2 | baseline | 500 | 1 405 | `timeout_600s` | 969 629 696 |
| SmolLM 2 | compact | 5 000 | 13 439 | `timeout_600s` | 97 685 504 |

Neither dictionary completed. Timeouts are results, not estimates of a finishing prefix.

## Q5. Transducer vs reference (exact token sequences)

Source: [`experiments/results/output_agreement.json`](../experiments/results/output_agreement.json). Broader evidence: [`docs/testing.md`](testing.md).

| Set | Comparators | Strings | Exact sequence matches | Match rate |
|---|---|---:|---:|---:|
| Example 2, `{a,b}^{≤8}` | transducer vs \(T^D\) | 511 | 511 | 1.0 |
| Unary \(a^{≤8}\) | transducer vs \(T^D\) | 9 | 9 | 1.0 |
| Example 2, `{a,b}^{≤6}` | transducer vs minbpe | 127 | 127 | 1.0 |

## Q6. Tokenization throughput vs input length

Source: [`experiments/results/tokenize_throughput.csv`](../experiments/results/tokenize_throughput.csv). Unit: **bytes/s**. Compile time is excluded from tokenize time. Peak column is `tracemalloc`, not RSS.

Ordinary: `(ab)^{n/2}` on Example 2 and on the empty dictionary. Pathological: \(a^n\) on unary `[a⫽a, aa⫽a]` and on the doubling chain. Lengths \(n \in \{256, 1024, 4096, 16384, 65536\}\).

### Ordinary, Example 2

| \(n\) bytes | Transducer bytes/s | Reference bytes/s | minbpe bytes/s |
|---:|---:|---:|---:|
| 256 | 3.92e6 | 2.17e5 | 3.57e6 |
| 1 024 | 4.22e6 | 5.24e4 | 3.26e6 |
| 4 096 | 4.18e6 | 1.18e4 | 3.83e6 |
| 16 384 | 4.35e6 | `timeout_60s` | 3.67e6 |
| 65 536 | 4.34e6 | `timeout_60s` | 3.82e6 |

### Ordinary, empty dictionary

| \(n\) bytes | Transducer bytes/s | Reference bytes/s | minbpe bytes/s |
|---:|---:|---:|---:|
| 256 | 4.01e6 | 8.11e6 | 5.80e6 |
| 1 024 | 4.43e6 | 1.01e7 | 6.60e6 |
| 4 096 | 4.50e6 | 1.07e7 | 6.70e6 |
| 16 384 | 4.49e6 | 1.07e7 | 6.61e6 |
| 65 536 | 4.40e6 | 8.91e6 | 6.59e6 |

### Pathological \(a^n\), unary

| \(n\) bytes | Transducer bytes/s | Reference bytes/s | minbpe bytes/s |
|---:|---:|---:|---:|
| 256 | 4.09e6 | 8.88e5 | 3.76e6 |
| 1 024 | 4.43e6 | 2.67e5 | 3.83e6 |
| 4 096 | 4.60e6 | 6.11e4 | 3.96e6 |
| 16 384 | 4.66e6 | 1.42e4 | 3.85e6 |
| 65 536 | 4.60e6 | `timeout_60s` | 3.82e6 |

### Pathological \(a^n\), doubling chain

| \(n\) bytes | Transducer bytes/s | Reference bytes/s | minbpe bytes/s |
|---:|---:|---:|---:|
| 256 | 4.06e6 | 3.90e5 | 2.82e6 |
| 1 024 | 4.47e6 | 1.04e5 | 2.92e6 |
| 4 096 | 4.53e6 | 2.40e4 | 2.73e6 |
| 16 384 | 4.49e6 | 5.65e3 | 2.83e6 |
| 65 536 | 4.64e6 | `timeout_60s` | 2.86e6 |

Input-size failure boundary for the **reference** tokenizer under the 60 s row cap: Example 2 ordinary at 16 384 bytes; unary and doubling \(a^n\) at 65 536 bytes. The transducer and minbpe adapter finished every stated length. Transducer bytes/s is roughly flat in \(n\) after compile (Corollary 14 of [5]: linear in the input once the machine exists). The reference successive-merge tokenizer slows as \(n\) grows and as merge chains apply, which is expected: it is the correctness oracle, not the throughput implementation.

## Limitations

- No matplotlib / committed plots; the PDF report may plot these files later.
- §5.6 was not rerun for this document.
- Q3 realistic rows stop at prefix 250.
- Q6 does not compile GPT-2 / SmolLM transducers.
- Tokenize peak memory is `tracemalloc`; construction peak memory is RSS.
- Compact toy timings on two-rule dictionaries are not a performance ranking.
- `SIGALRM` row caps are Unix-only; the recorded host is Linux.
