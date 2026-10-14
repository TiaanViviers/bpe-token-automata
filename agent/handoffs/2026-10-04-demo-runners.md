# Handoff: Demo runners for the professor walkthrough

## Task

- Ticket: none
- Repository: `26455900-CS345/`
- Branch: `main`
- Agent or contributor: review only; implementation is for the teammate
- Date: 2026-10-04
- Scope: Review whether the project can be demonstrated section by section from the Makefile, tests, and standalone scripts. Produce an implementation prompt. Do not change project code.

## Status

```text
complete
```

The review is complete. No project files were edited. The repository is still a library plus pytest plus batch experiment scripts. A live “run this component on this input” path does not exist yet.

## Summary of work

Inspected the Makefile, README, public package API, `data/`, `experiments/`, the Section 6 test matrix, and the “No CLI” notes in `docs/design-decisions.md`. Git on `main` was clean and up to date with `origin/main`.

## Files changed

```text
agent/handoffs/2026-10-04-demo-runners.md
```

Private handoff only. Nothing under `26455900-CS345/` was modified.

## Sources consulted

- Project specification: pointer only (`agent/specs/cs345-project-specification.md`). Section numbers below follow the project README and docs (5.1–5.6, 6, 7, 8.2, 8.11). The PDF was not re-checked; this task does not change formal semantics.
- Papers and sections: not re-read. Demo fixtures already cited in `docs/token-dfa-examples.md`.
- Approved decisions: `26455900-CS345/docs/design-decisions.md` records “No CLI” for the token DFA, transducer, and compact automaton. A demo script must be a presentation wrapper and that note must be updated, not silently contradicted.
- Existing documentation: `README.md`, `docs/testing.md`, `docs/experiments.md`, `docs/extensions.md`, `docs/token-dfa-examples.md`, `data/dictionaries/REALISTIC.md`.

## Decisions made

Temporary review conclusions, not approved architecture:

- `make test` is already short enough for a live test demo (recorded 136 passed in 1.70 s on 2026-10-04). The gap is human-readable execution, not the test suite.
- Do not run `experiments/timeout_study.py` or `experiments/tokenize_eval.py` live. Use committed JSON/CSV and the smoke tests.
- New commands should call existing public functions. They must not reimplement tokenization or construction.

## Assumptions and invariants

- Symbols stay UTF-8 bytes. Demo printing should use `format_token_label` / `format_token_sequence`.
- Improper dictionaries must still fail validation; the demo should show that failure for `improper_example3.merges`.
- Graphviz PNG/SVG stays optional. `to_dot` already returns DOT text.
- Full GPT-2 / SmolLM construction stays out of the live path.

## Tests added or changed

### Added

- None.

### Modified

- None.

### Important cases covered

- None. This was a read-only review.

## Commands run

```bash
git -C 26455900-CS345 status
git -C 26455900-CS345 branch --show-current
git -C 26455900-CS345 log --oneline -5
git -C 26455900-CS345 diff
git -C 26455900-CS345 diff --cached
```

## Validation results

| Check | Result |
|---|---|
| Formatting | not run |
| Linting | not run |
| Type checking | not run |
| Unit tests | not run |
| Full `make check` | not run |
| Additional verification | not applicable (read-only review) |
| Private-boundary review | passed (no project files written) |

## Known limitations

- Pytest has no section markers. A file can be run with `uv run pytest tests/<file>.py -q`, but that is not documented as a demo menu except for `tests/test_extensions.py`.
- Dictionary fixtures exist. Sample strings to tokenize do not; they are hardcoded inside tests and experiment scripts.
- Experiment `main()` functions rewrite result JSON. They are measurement jobs, not a walkthrough.

## Unresolved questions

- Whether the professor wants a diagram on screen (DOT only vs optional `dot -Tsvg`). Non-blocking. Default to printing DOT text.
- Whether a one-command scripted walkthrough is enough, or each section also needs flags for an arbitrary dictionary and string. Non-blocking. The prompt asks for both: a no-argument Example 2 walkthrough, plus flags.

## Risks for reviewer

- Adding a CLI contradicts the current “No CLI” sentences in `docs/design-decisions.md` unless those sentences are updated to say the constructions stay library calls and `scripts/demo.py` is presentation only.
- A demo must not claim GPT-2 automata were built, and must not hide the §5.6 timeout.
- Do not copy this handoff or `agent/` into `26455900-CS345/`.

## Pre-existing changes preserved

```text
None. Working tree clean on main, up to date with origin/main.
```

## Recommended next step

Give the teammate the pasteable prompt in the next section. Implement only that demo layer on `main` in `26455900-CS345/`. Do not commit unless a human asks.

## Pasteable implementation prompt

See the user-facing message from 2026-10-04. Implement a thin `scripts/demo.py` plus Makefile section targets and a README “Live demo” section. Call the existing public API. Add fast tests that the Example 2 walkthrough prints the reference and transducer token sequences and that they agree. Update `docs/design-decisions.md` so “No CLI” means “no CLI inside the constructions”; the demo script is allowed. Leave algorithms, experiment result files, and the 40-minute timeout study unchanged.

## Git status

```bash
git -C 26455900-CS345 status --short --branch
## main...origin/main
```

No commits or pushes were requested or performed. The handoff file is private workspace material and is not tracked by `26455900-CS345/`.
