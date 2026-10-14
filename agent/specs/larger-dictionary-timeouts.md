# Larger-dictionary construction and controlled timeouts (Section 5.6)

Engineering specification for applying the existing baseline and compact token-DFA constructors to prefixes of realistic BPE dictionaries under fixed time and memory limits.

## Goal

Take prefixes of two openly published BPE merge lists, construct the Section 5.2 baseline token DFA and the Section 5.5 compact delayed-input automaton from the universal byte-alphabet DFA, and report construction size, time, and peak RSS until a one-minute cutoff, a ten-minute cutoff, or an 8 GiB RSS limit is reached. A timeout, memory exhaustion, or unsupported input is a recorded result.

This phase does not introduce a new automaton model. It is the compulsory scaling study for course §5.6 and §7.1–7.3 questions 1–4.

## Background

- **Course requirement:** spec §5.6 (PDF p. 5): prefixes of at least two realistic dictionaries; GPT-2-style / Whisper-style / Phi-style / other open merge lists [15]; full construction not compulsory; one-minute and ten-minute timeouts plus a stated memory limit; timeout / OOM / unsupported must appear in tables and must not be replaced by an unverified estimate. Spec §5.5 required comparison columns on dictionary prefixes. Spec §7.1–7.2 experimental method. Spec §7.3 questions 1–4 (growth, compact reduction, which rules add states, failure boundary). Spec §4.2: repository contains input dictionaries; clean checkout executable from the README.
- **Research context (not a correctness oracle):** Berglund, Jonsson, Martens, and van der Merwe [4] §7 used GPT-2/GPT-3, SmolLM 2, Whisper, and Phi-4 at full size and reported that a naive Phi-4 DFA can have on the order of \(10^5\) states and \(\sim 10^{10}\) transitions. This project does **not** claim to reproduce those full-dictionary tables (O4 is unimplemented; timeouts are allowed).
- **Locked project decisions already in force:** D1/D5 UTF-8 bytes and fixed \(\Sigma=\{0,\ldots,255\}\); D2 SentencePiece \(T^D\); D3 merge-list + YAML parsers; D4 `\xHH` literals; D9 no pre-tokenization; D14 no trim; D33–D35 compact O1 on, O2/O3 default on, O4 out of scope.

ASSUMPTIONS (locked 2026-09-14 with the human):

1. The two dictionaries are **GPT-2** and **SmolLM 2**, not Whisper and not Phi-4.
2. The timeout harness measures **baseline and compact construction only**. Transducer compile/tokenize is out of the 5.6 table (Section 7.3 questions 5–6 remain a later item).
3. Fetch/convert is a one-shot experiment helper. Converted `.merges` files are committed. `make check` stays offline and does not download.
4. Hugging Face / tiktoken are **not** runtime dependencies of `bpe_token_automata`.
5. If SmolLM 2 `merges.txt` is not the GPT-2 `bytes_to_unicode` display encoding, stop and record unsupported rather than invent a second mapping.
6. Memory is **8 GiB RSS**, measured in a child process, not `tracemalloc`.
7. One 10-minute child per `(dictionary, construction)` records the last finished prefix at 60 s and at stop.
8. Existing `experiments/compact_compare.py` remains the 5.5 toy comparison and is not extended into this study.

## Scope

- One-shot fetch of pinned Hugging Face `merges.txt` files into a gitignored cache.
- Conversion from GPT-2 `bytes_to_unicode` display encoding into this project’s merge-list syntax (`format_token_label`).
- Committed converted dictionaries plus attribution (URL, revision, SHA-256, licence).
- Subprocess timeout study: incremental merges from \(A_0=\mathrm{universal\_token\_dfa}(\mathrm{byte\_alphabet}())\).
- JSONL checkpoints and a summary `experiments/results/timeout_study.json`.
- README and `docs/design-decisions.md` for §5.6 method, limits, and honest failure reporting.
- Tests for conversion, parse, properness, and a 0–2-rule construction smoke over the byte alphabet.

## Non-goals

- O4 (prefix-forest sink predicates).
- Whisper, Phi-4, or any third realistic dictionary.
- Transducer compile, tokenize throughput, or minbpe on realistic prefixes.
- Changing `TokenDFA`, `DelayedInputDFA`, or Algorithm 2.
- CLI or Graphviz of large automata.
- Committing raw Hugging Face `merges.txt`.
- Network access during `make check`.
- Section 9 report plots (raw results only).
- Extensions 8.2 / 8.11.
- Using tiktoken / Hugging Face `encode()` as a 5.6 oracle (regex pre-tokenization would measure a different function).
- Reproducing [4] Table 2–3 full-dictionary counts.
- Raising the memory cap silently when a machine has less RAM.

## Authoritative sources

| Source | What it governs |
|---|---|
| Course spec §5.6 (PDF p. 5); §7.1–7.3 Q1–4; §4.2 | Compulsory experiment, reporting, repository contents |
| Course spec §5.5 required comparison | Columns: baseline states/explicit transitions; compact states/explicit transitions/defaults; construction time; peak memory |
| [15] tiktoken; [4] §7 Table 1 sources [6], [11] | Acceptable dictionary families; GPT-2 and SmolLM 2 URLs |
| GPT-2 `bytes_to_unicode` (Radford et al. `encoder.py`; tiktoken `data_gym_to_mergeable_bpe_ranks`) | Display-encoding inverse |
| D1, D5, D44–D52 | Byte alphabet, sources, limits, run shape |
| Existing `construct_token_dfa` / `construct_compact_token_dfa` | Constructions under test |

**Course vs paper.** The course requires prefixes and timeouts. Paper [4] reports full dictionaries with O1–O4. Source claim: compact construction reduces explicit transitions on real dictionaries. Project decision: measure our O1–O3 implementation until the stated limits. Implementation consequence: do not fill tables with [4] numbers.

## Interfaces

No change to the public automaton API. New experiment-only surfaces:

```text
experiments/hf_merges.py          # mapping + convert; no network
experiments/fetch_dictionaries.py # optional regenerate; network
experiments/timeout_study.py      # 5.6 runner; offline once files exist

data/dictionaries/gpt2.merges
data/dictionaries/smollm2.merges
data/dictionaries/REALISTIC.md    # attribution

experiments/.cache/huggingface/   # gitignored raw downloads
experiments/results/timeout_study.json
experiments/results/timeout_study.jsonl  # optional per-run checkpoints copied or summarised
```

Fetch helper (not imported by `src/`):

```text
gpt2_bytes_to_unicode() -> dict[int, str]
gpt2_unicode_to_byte() -> dict[str, int]
decode_hf_token(literal: str) -> bytes
convert_hf_merges(text: str) -> str    # our .merges body
```

Timeout child protocol:

```text
apply_merge / apply_compact_merge incrementally from A0
after each checkpoint prefix, append one JSONL record:
  dictionary, construction, n_rules, elapsed_s,
  n_states, n_final, n_tokens, n_transitions,
  n_defaults (compact only; 0 for baseline),
  n_sink_states (1 compact / 0 baseline),
  rss_bytes, status="ok"
on 60s wall: record largest n_rules with status still ok (do not stop)
on 600s or RLIMIT_AS: stop; last ok record is the failure-boundary prefix
status in {ok, timeout_60s, timeout_600s, memory, unsupported, error}
```

`timeout_60s` is a **cutoff annotation** on the last prefix finished at or before 60 s, not a child-kill at 60 s. The child continues until 600 s, OOM, completion, or error.

Reuse:

- `parse_dictionary_path` / `parse_merge_list`
- `validate_proper`
- `construct_token_dfa` / `apply_merge`
- `construct_compact_token_dfa` / `apply_compact_merge` / `CompactOptions` defaults
- `byte_alphabet` / `universal_token_dfa`
- `format_token_label`

## Invariants

- Tokens remain `bytes`. Converted files must round-trip through `parse_merge_list`.
- Converted dictionaries must be **proper** (Definition 5 of [6]); otherwise the constructors correctly raise and the study records `unsupported` or `error` — it must not strip rules to force properness.
- Base automaton is the **full byte alphabet**, one accepting state, 256 explicit self-loops.
- Compact public defaults: O1 on, O2 on, O3 on. Record these flags in the JSON. No flag sweep.
- Compact `n_states` excludes the distinguished sink; `n_sink_states = 1`. Baseline has no sink row.
- Construction time is **wall-clock in the child**, excluding fetch, parse of the full file before \(A_0\), and Graphviz (none). Parsing the committed file once per child is allowed and should be noted.
- Prefix \(n\) means the first \(n\) rules in dictionary order (`Dictionary.rules[:n]`), \(n=0\) being \(A_0\).
- Shared comparison rows exist only for prefixes where **both** constructions have an `ok` record. Failure-boundary rows are per construction.
- Timeouts and OOM are not averaged into successful times. There is no estimated “would have finished at \(n=\)…”.
- Repeat/median policy: **no repeats** for this study (D49 simplified). One incremental run per `(dictionary, construction)`.

## Error and edge behaviour

| Case | Behaviour |
|---|---|
| Network failure during optional fetch | Script exits non-zero; committed files unchanged |
| SHA-256 mismatch vs recorded pin | Abort; do not convert |
| Malformed HF line (not two tokens) | Conversion error; do not emit a partial dictionary |
| Character outside `bytes_to_unicode` inverse | Conversion error (SmolLM 2 mapping mismatch) |
| Converted dictionary improper | `validate_proper` fails; do not commit; record as blocking |
| Child exceeds 600 s | Kill; status `timeout_600s`; keep last `ok` checkpoint |
| Child exceeds 8 GiB address space / RSS policy | Kill; status `memory`; keep last `ok` checkpoint |
| Child crash / Python error | status `error` with exception type/message; no fabricated counts |
| Host has less than 8 GiB RAM | Still **state** the 8 GiB cap; if the OS OOM-kills earlier, record `memory` and the host RAM in metadata |
| Prefix larger than dictionary | Stop with status `ok` at \(\lvert D\rvert\) (completed) |

## Testing and acceptance

Independent evidence: frozen HF snippet → known byte pairs; `parse_merge_list` on committed files; `validate_proper`; constructors already tested in §§5.2/5.5. Do not use tiktoken `encode` to check conversion.

- Unit: `Ġ t` → `\x20 t`; `h e` → `h e`; `Ġt he` → `\x20t he`; `#version` / blank / `#` comments skipped; inverse mapping is 256-bijective.
- Committed `gpt2.merges` and `smollm2.merges` parse with **zero** issues.
- Both are proper; rule counts equal non-comment HF merge lines (GPT-2: 50 000; SmolLM 2: record the counted value, expected \(\approx 48\,900\) per [4] Table 1).
- Smoke: `construct_token_dfa` and `construct_compact_token_dfa` on prefixes 0, 1, 2 over `byte_alphabet()` finish quickly.
- Timeout runner: a unit/smoke that does **not** wait ten minutes — e.g. invoke the child protocol with a 0.5 s fake limit on a tiny dictionary, or parse JSON schema on a fixture. Full 5.6 run is a documented extra command.
- `make check` does not call `fetch_dictionaries.py` or the 10-minute study.

## Risks

- SmolLM 2 may not use GPT-2 `bytes_to_unicode`. Stopping is required (D45).
- Baseline on 256 symbols may hit 60 s at a very small prefix. That is a valid §5.6 result.
- `RLIMIT_AS` is not identical to RSS; document both the cap mechanism and `ru_maxrss` reporting.
- Incremental `apply_merge` time for prefix \(n\) is elapsed time from \(A_0\), which is what §7.1 asks; it is not a from-scratch rebuild of that prefix.
- Converted files are ~0.5–1 MB; acceptable for GitLab but must not be regenerated with unstable ordering.
- Host metadata must be recorded or the measurements cannot be interpreted.

## Open questions

None blocking. Remaining operational details (exact Hugging Face git revisions and SHA-256 pins) are **recorded at TICKET-015 fetch time**, not guessed here.

Optional later work, out of this spec: transducer throughput on prefixes that finish; Phi-4 as an extra dictionary; Section 9 plots generated from `timeout_study.json`.

## Validation commands

```bash
cd 26455900-CS345
make check
# TICKET-015 regenerate (optional; network):
uv run python experiments/fetch_dictionaries.py
# TICKET-016 (not part of make check):
uv run python experiments/timeout_study.py
```
