# TICKET-022: Token-sequence agreement and tokenize throughput (Q5–Q6)

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Write match-rate and bytes-per-second artefacts for §7.3 questions 5 and 6. Compare the subsequential tokenizer with the independent reference (and minbpe where the adapter applies) on bounded sets and on ordinary plus pathological input lengths, with a 60 s per-row cap.

## Background

Section 6 already proves exact agreement, but §7.1 wants a match-rate file. D57 deferred huge \(n\) and throughput to Q6. D60–D64. Depends on TICKET-020. Leave `transducer_tokenize.py` unchanged as the §5.4 toy.

## Authoritative sources

- Project specification: §7.1 throughput and output agreement; §7.3 Q5–Q6; §5.4 performance; §6.2–6.3, §6.6
- Paper and section: [5] Corollary 14 (linear after compile)
- Approved decision: D60, D61, D62, D63, D64, D67
- Existing implementation: `compile_tokenizer`, `tokenize`, `tokenize_reference`, `tests/minbpe_adapter.py`

## Scope

The ticket includes:

- `experiments/tokenize_eval.py` writing `output_agreement.json`/`.csv` and `tokenize_throughput.json`/`.csv`
- Q5: Example 2 all `{a,b}^{\le 8}` vs reference; unary \(a^{\le 8}\) vs reference; Example 2 `{a,b}^{\le 6}` vs minbpe
- Q6: lengths 256, 1024, 4096, 16384, 65536; ordinary `(ab)^{n/2}` on Example 2 and empty dict; pathological \(a^n\) on unary and doubling; implementations transducer, reference, minbpe (skip minbpe if injection fails)
- Compile once per dictionary; warmup + 7 repeats; median; bytes/s = `n_bytes / median_seconds`; tracemalloc peak; 60 s row budget with `status=timeout_60s` and null medians
- Pytest: agreement on `{a,b}^{\le 2}`; throughput `n=8`, 1 repeat, no 60 s wait

## Non-goals

The ticket explicitly excludes:

- GPT-2/SmolLM transducer compile
- tiktoken / Hugging Face encode
- matplotlib
- Changing tokenizer algorithms
- Docs tables (TICKET-023)
- Expanding `transducer_tokenize.py`

## Preconditions

Before implementation:

- [x] TICKET-020 helper exists.
- [x] Section 6 oracles exist and stay independent of the transducer implementation.

## Proposed design

Enumerate strings with `itertools.product` as in the exhaustive tests. Compile one machine per dictionary. For Q6, a Unix `SIGALRM` / `ITIMER_REAL` deadline covers warmup plus repeats; on expiry record `timeout_60s` and do not invent a median. Peak tracemalloc is a separate pass after successful timing. Throughput unit field: `bytes_per_second_median`.

## Files likely to change

```text
26455900-CS345/experiments/tokenize_eval.py
26455900-CS345/experiments/results/output_agreement.json
26455900-CS345/experiments/results/output_agreement.csv
26455900-CS345/experiments/results/tokenize_throughput.json
26455900-CS345/experiments/results/tokenize_throughput.csv
26455900-CS345/tests/test_tokenize_eval.py
```

## Acceptance criteria

- [ ] Q5 JSON reports 511, 9, and 127 strings on the three sets; match_rate 1.0 or the run is a failing bug
- [ ] Q6 JSON states unit bytes/s; compile time is separate from tokenize time
- [ ] Timeouts use `timeout_60s` and omit medians
- [ ] pytest does not run the full length ladder
- [ ] minbpe comparison is token sequences, not detokenized text only

## Required test evidence

### Unit tests

- `{a,b}^{\le 2}` agreement row has match_rate 1.0
- Throughput on 8-byte Example 2 with 1 repeat has `status=ok` and a positive bytes/s

### Negative and special cases

- A synthetic already-expired deadline yields `timeout_60s` without a median

## Documentation changes

- Later TICKET-023

## Validation commands

```bash
cd 26455900-CS345
make check
uv run python experiments/tokenize_eval.py
```

## Risks

- Reference tokenizer on \(a^{65536}\) may timeout; that is a result
- `SIGALRM` is Unix-only; recorded host is Linux
- Mixing tracemalloc with §5.6 RSS would mislead Q2

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Full `tokenize_eval.py` run committed as JSON/CSV.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
