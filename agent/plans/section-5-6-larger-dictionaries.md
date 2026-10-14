# Section 5.6 — Larger-dictionary construction and controlled timeouts

Planning document for the compulsory realistic-dictionary timeout study.

## Metadata

| Field | Value |
|---|---|
| **Status** | `approved` — blocking decisions D44–D52 locked 2026-09-14 |
| **Spec section** | Course spec §5.6 (PDF p. 5); §7.1–7.3 questions 1–4 |
| **Primary sources** | Course spec; compact paper [4] §7 Table 1 as dictionary-family evidence only |
| **Engineering spec** | [`../specs/larger-dictionary-timeouts.md`](../specs/larger-dictionary-timeouts.md) |
| **PDF check** | Course spec PDF p. 5 (§5.6 wording verified 2026-09-14) |
| **Tickets** | TICKET-015 import/commit dictionaries; TICKET-016 timeout harness, results, docs |

## What Section 5.6 requires

Apply the existing baseline and compact constructors to prefixes of at least two realistic BPE dictionaries. Full construction is not compulsory. Record the largest prefix completed under a one-minute timeout, a ten-minute timeout, and a stated memory limit. Timeout, memory exhaustion, and unsupported input are results.

## Human locks (2026-09-14)

- Dictionaries: **GPT-2** and **SmolLM 2** (not Whisper, not Phi-4).
- Timeout harness: **baseline + compact construction only**. Transducer compile/tokenize is out of the 5.6 table.

## Decision register

| # | Decision | Blocking? | Status | Decision | Rationale |
|---|---|---|---|---|---|
| D44 | Sources | yes | `decided` | GPT-2 and SmolLM 2 HF `merges.txt`, pinned URL + revision + SHA-256 | Course [15] / [4] Table 1; two distinct lists |
| D45 | HF encoding | yes | `decided` | GPT-2 `bytes_to_unicode` inverse; stop if SmolLM 2 differs | `Ġ` is byte 32, not U+0120 |
| D46 | What to commit | yes | `decided` | Converted `.merges` + attribution; gitignore raw cache | Spec §4.2; offline `make check` |
| D47 | Alphabet | yes | `decided` | `universal_token_dfa(byte_alphabet())` | D1/D5; realistic BPE is byte-level |
| D48 | Limits | yes | `decided` | 60 s, 600 s, 8 GiB RSS in a child process | Course §5.6; RSS not tracemalloc |
| D49 | Run shape | yes | `decided` | One 10-minute incremental child per `(dict, construction)`; annotate 60 s cutoff; no repeats | Honest elapsed time; do not average timeouts |
| D50 | Compact flags | yes | `decided` | O1–O3 public defaults; no O4; no flag sweep | 5.5 already locked O4 out |
| D51 | Comparison rows | yes | `decided` | Shared prefixes only if both finished; plus per-construction boundaries | Course §7.2 identical prefixes |
| D52 | Tests vs study | yes | `decided` | `make check` offline; no 10-minute run in pytest | Quality gates must stay fast |

## Tickets

1. TICKET-015 — fetch/convert GPT-2 and SmolLM 2; commit `.merges`; importer tests
2. TICKET-016 — timeout subprocess harness; `timeout_study.json`; README and design-decisions

Human review after TICKET-015 / `make check` **before** the long TICKET-016 run.

## Non-goals

O4, Whisper, Phi-4, transducer throughput, tiktoken/`transformers` `encode()`, CLI, Graphviz of large automata, Section 9 plots, 8.2/8.11, extending `compact_compare.py` into this study.
