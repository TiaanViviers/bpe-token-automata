# Handoff: TICKET-015 realistic dictionaries

## Task

- Ticket: TICKET-015
- Repository: `26455900-CS345/`
- Branch: `main`
- Agent or contributor: Cursor Grok 4.6
- Date: 2026-09-14
- Scope: Convert and add GPT-2 and SmolLM 2 merge lists; converter tests; no timeout runner

## Status

```text
ready for review
```

Converted files parse, are proper, and smoke-construct prefixes 0–2 over the byte alphabet. `make check` equivalents passed. Not git-committed. TICKET-016 must wait for human review of the conversion (`Ġ` = space).

## Summary of work

Added a no-network GPT-2 `bytes_to_unicode` converter, an optional pinned Hugging Face fetch script, committed-format `gpt2.merges` (50 000 rules) and `smollm2.merges` (48 900 rules), and attribution. SmolLM 2 used the same mapping; conversion did not stop. `#` bytes are hex-escaped so they are not merge-list comments.

## Files changed

```text
26455900-CS345/experiments/hf_merges.py
26455900-CS345/experiments/fetch_dictionaries.py
26455900-CS345/experiments/__init__.py
26455900-CS345/data/dictionaries/gpt2.merges
26455900-CS345/data/dictionaries/smollm2.merges
26455900-CS345/data/dictionaries/REALISTIC.md
26455900-CS345/tests/test_hf_merges.py
26455900-CS345/tests/test_realistic_dictionaries.py
26455900-CS345/.gitignore
26455900-CS345/README.md
26455900-CS345/pyproject.toml
26455900-CS345/Makefile
agent/tickets/TICKET-015-realistic-dictionaries.md
agent/handoffs/TICKET-015/2026-09-14-implementation.md
```

Raw Hugging Face files live only under gitignored `experiments/.cache/`.

## Sources consulted

- Project specification: §5.6, §4.2 (Markdown; §5.6 PDF p. 5 from earlier session)
- Papers: [4] §7 Table 1 dictionary families; GPT-2 `bytes_to_unicode` / tiktoken `data_gym_to_mergeable_bpe_ranks`
- Approved decisions: D1, D4, D44–D46, D52
- Existing documentation: `format_token_label`, `parse_merge_list`

## Decisions made

- `format_merge_token` matches `format_token_label` plus hex-escaping `#` (0x23). `Ġt` therefore becomes `\x20\x74`, not `\x20t`.
- Skip only `#version` headers on HF input; later `# #` lines are real merges.
- Pins: GPT-2 rev `607a30d7…`, SHA-256 `1ce16647…` (same as tiktoken `vocab.bpe`); SmolLM 2 rev `effd688a…`, SHA-256 `0b54e8aa…`.
- mypy still runs on `src tests` only so pre-existing experiment scripts stay out of the typecheck.

## Assumptions and invariants

- Converted dictionaries remain proper (Definition 5) without dropping rules.
- Fetch is optional; tests are offline.

## Tests added or changed

### Added

- `tests/test_hf_merges.py`
- `tests/test_realistic_dictionaries.py`

### Modified

- None of the existing construction tests

### Important cases covered

- `Ġ t` → space + `t`; bijection; `#` not a comment; unmapped character; wrong arity; both files proper; prefixes 0–2 on `byte_alphabet()`

## Commands run

```bash
cd 26455900-CS345
.venv/bin/ruff format --check .
.venv/bin/ruff check .
.venv/bin/mypy src tests
.venv/bin/pytest
```

Network used only to download the two pinned `merges.txt` files.

## Validation results

| Check | Result |
|---|---|
| Formatting | passed |
| Linting | passed |
| Type checking | passed |
| Unit tests | passed (102) |
| Full `make check` | passed (same four commands via `.venv`; `uv run` not used because it tried to rebuild) |
| Additional verification | both dictionaries `validate_proper`; 50 000 / 48 900 rules |
| Private-boundary review | passed |

## Known limitations

- Timeout study is TICKET-016; not started.
- Converted files are ~800 KB each.

## Unresolved questions

- None blocking. Human should confirm `Ġ` = space on a few lines in `gpt2.merges` before TICKET-016.

## Risks for reviewer

- Spot-check `\x20 t` as the first GPT-2 rule.
- Confirm licences (MIT / Apache-2.0) are acceptable to commit the converted lists.
- Do not run the 10-minute study until this review.

## Pre-existing changes preserved

```text
None
```

## Recommended next step

Human review of conversion, then git commit of `26455900-CS345/` if authorised, then TICKET-016.

## Git status

```text
## main...origin/main
 M .gitignore README.md pyproject.toml
?? data/dictionaries/REALISTIC.md gpt2.merges smollm2.merges
?? experiments/__init__.py fetch_dictionaries.py hf_merges.py
?? tests/test_hf_merges.py test_realistic_dictionaries.py
```

No commit or push was requested or performed.
