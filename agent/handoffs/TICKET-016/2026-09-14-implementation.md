# Handoff: TICKET-016 timeout study

## Task

- Ticket: TICKET-016
- Repository: `26455900-CS345/`
- Branch: `main`
- Agent or contributor: Cursor Grok 4.6
- Date: 2026-09-14
- Scope: Section 5.6 construction timeout harness, results, docs. No transducer. No commit.

## Status

```text
ready for review
```

Harness, smoke tests, documentation, and a full 4×10-minute study completed. Timeouts are recorded as results (no construction finished the full dictionary). Not git-committed.

## Summary of work

Added `experiments/timeout_study.py`: sequential child processes, incremental `apply_merge` / `apply_compact_merge` from the universal byte DFA, JSONL checkpoints, 60 s annotation, 600 s stop, 8 GiB `RLIMIT_AS` plus RSS poll. Wrote `experiments/results/timeout_study.json` and `.csv`. README and `docs/design-decisions.md` describe the method.

Observed boundaries on this host (16-thread Linux, ~15 GiB RAM, Python 3.12.3):

| Dictionary | Construction | Prefix at ≤60 s | Largest prefix at 600 s | RSS |
|---|---|---|---|---|
| GPT-2 | baseline | 500 | 1396 | ~931 MiB |
| GPT-2 | compact | 5000 | 14280 | ~95 MiB |
| SmolLM 2 | baseline | 500 | 1405 | ~925 MiB |
| SmolLM 2 | compact | 5000 | 13439 | ~93 MiB |

All four stopped with `timeout_600s`. Shared comparison prefixes: 0–1000 for both dictionaries. Compact processed about 10× more rules at about 10× less RSS. Do not treat these as [4] full-dictionary tables (O4 off; prefixes only).

## Files changed

```text
26455900-CS345/experiments/timeout_study.py
26455900-CS345/experiments/results/timeout_study.json
26455900-CS345/experiments/results/timeout_study.csv
26455900-CS345/tests/test_timeout_study.py
26455900-CS345/README.md
26455900-CS345/docs/design-decisions.md
agent/tickets/TICKET-015-realistic-dictionaries.md
agent/tickets/TICKET-016-timeout-study.md
agent/handoffs/TICKET-016/2026-09-14-implementation.md
```

JSONL intermediates are gitignored under `experiments/.cache/timeout/`.

## Sources consulted

- Project specification: §5.6 PDF p. 5; §7.1–7.3 Q1–4
- Paper [4] §7 as motivation only
- Decisions D47–D52
- TICKET-015 converted dictionaries (human-reviewed)

## Decisions made

- Sequential children (avoid 4× memory).
- Default apply `RLIMIT_AS`; `--no-rlimit` for tests.
- Discard `MergeTrace` immediately so traces do not retain previous automata.
- `timeout_60s` = last checkpoint with `elapsed_s <= 60` (baseline GPT-2: 500 rules; a 635-rule row exists at 60.002 s and is kept in checkpoints).

## Tests added or changed

### Added

- `tests/test_timeout_study.py` — prefix list, zero long-timeout, subprocess smoke on `example2.merges`, summarise shared prefixes

## Commands run

```bash
cd 26455900-CS345
.venv/bin/ruff format --check .
.venv/bin/ruff check .
.venv/bin/mypy src tests
.venv/bin/pytest
PYTHONUNBUFFERED=1 .venv/bin/python experiments/timeout_study.py
```

## Validation results

| Check | Result |
|---|---|
| Formatting | passed |
| Linting | passed |
| Type checking | passed |
| Unit tests | passed (106) |
| Full `make check` | passed (same commands via `.venv`) |
| Additional verification | timeout study exit 0 in 2404 s; four `timeout_600s` results |
| Private-boundary review | passed |

## Known limitations

- O4 not implemented.
- Host RAM ~15 GiB; 8 GiB cap did not bind (RSS stayed under 1 GiB).
- `RLIMIT_AS` ≠ RSS; both are documented.
- Transducer throughput is still a later §7.3 item.

## Unresolved questions

- None blocking.

## Risks for reviewer

- Confirm JSON stop statuses are timeouts, not invented larger prefixes.
- Compact vs baseline comparison only through 1000 rules (shared checkpoints).

## Pre-existing changes preserved

TICKET-015 uncommitted dictionary files remain in the working tree.

## Recommended next step

Human review of `timeout_study.json`, then a git commit of TICKET-015+016 if authorised.

## Git status

Uncommitted on `main` (015 + 016 files). No commit or push requested or performed.
