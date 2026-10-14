# TICKET-015: Import and commit GPT-2 and SmolLM 2 dictionaries

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Download the pinned GPT-2 and SmolLM 2 Hugging Face merge lists, convert them from the GPT-2 `bytes_to_unicode` display encoding into this project’s byte-level `.merges` syntax, validate that both dictionaries are proper, and commit the converted files with attribution. After this ticket, `parse_dictionary_path` can load realistic dictionaries with no network.

## Background

Section 5.6 needs two realistic BPE dictionaries in the assessable repository. Hugging Face `merges.txt` is not safe to parse as UTF-8 token literals: `Ġ` means byte `0x20` (space), not U+0120. Engineering spec: [`../specs/larger-dictionary-timeouts.md`](../specs/larger-dictionary-timeouts.md). Decisions D44–D46, D52.

## Authoritative sources

- Project specification: §5.6, §4.2 (input dictionaries in the repo)
- Paper and section: [4] §7 Table 1 sources [11] GPT-2 and [6] SmolLM 2 (PDF p. 10); mapping from GPT-2 `encoder.py` / tiktoken `data_gym_to_mergeable_bpe_ranks`
- Approved decision: D1, D4, D44, D45, D46, D52
- Existing implementation: `parse_merge_list`, `format_token_label`, `validate_proper`

## Scope

The ticket includes:

- `experiments/hf_merges.py`: `bytes_to_unicode` and inverse; `decode_hf_token`; `convert_hf_merges` (no network)
- `experiments/fetch_dictionaries.py`: stdlib HTTP GET of pinned URLs into `experiments/.cache/huggingface/`; SHA-256 check; write converted files
- Committed `data/dictionaries/gpt2.merges` and `data/dictionaries/smollm2.merges`
- `data/dictionaries/REALISTIC.md`: URL, git revision, SHA-256 of the **raw** file, licence, conversion date, rule counts
- `.gitignore` entry for the raw cache only
- Tests for the converter and for parse/properness of the committed files
- Smoke: prefixes 0–2 over `byte_alphabet()` for both constructors

## Non-goals

The ticket explicitly excludes:

- Timeout harness / §5.6 runner (TICKET-016)
- Transducer, minbpe, Phi-4, Whisper
- Adding Hugging Face, tiktoken, or `requests` to `pyproject.toml`
- Changing `parse_merge_list` unless a genuine bug is found
- Network inside `make check`

## Preconditions

Before implementation:

- [x] Relevant formal definitions are understood.
- [x] Major ambiguity has been resolved or recorded (D44–D52).
- [x] Required interfaces or dependencies exist (`parse_merge_list`, `validate_proper`).
- [x] `26455900-CS345/` is on `main` and its working state is understood.
- [x] Pre-existing changes have been identified and can be preserved (clean tree at 5.5 HEAD).

## Proposed design

GPT-2 printable mapping (Radford et al. `encoder.py`): bytes in `!`–`~`, `¡`–`¬`, `®`–`ÿ` map to themselves as Unicode code points; remaining bytes map to `chr(256+n)` in order. Inverse is a 256-entry bijection. Space (`0x20`) maps to `Ġ`.

`convert_hf_merges`:

1. Skip empty lines and `#` comments (including `#version: 0.2`).
2. Split each remaining line on ASCII whitespace into exactly two fields.
3. Decode each field character-wise through the inverse map to `bytes`.
4. Emit `format_token_label(left) + " " + format_token_label(right)`.
5. On any unmapped character or wrong field count: raise; do not skip the line.

Fetch pins (fill exact revision and SHA-256 when first download succeeds; abort on later mismatch):

- GPT-2: `https://huggingface.co/openai-community/gpt2/resolve/<rev>/merges.txt`
- SmolLM 2: `https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B/resolve/<rev>/merges.txt`

If SmolLM 2 conversion hits an unmapped character, **stop**. Do not invent a second encoding. Record `unsupported` in attribution and do not commit a guessed file.

Converted files must `validate_proper`. Do not drop or reorder rules to force properness.

Keep helpers under `experiments/` so `src/bpe_token_automata` stays independent. Tests may import `experiments.hf_merges`.

## Files likely to change

```text
26455900-CS345/experiments/hf_merges.py
26455900-CS345/experiments/fetch_dictionaries.py
26455900-CS345/experiments/.cache/huggingface/   # gitignored
26455900-CS345/.gitignore
26455900-CS345/data/dictionaries/gpt2.merges
26455900-CS345/data/dictionaries/smollm2.merges
26455900-CS345/data/dictionaries/REALISTIC.md
26455900-CS345/tests/test_hf_merges.py
26455900-CS345/tests/test_realistic_dictionaries.py
```

This list is guidance, not permission for unrelated changes.

## Acceptance criteria

- [x] Converter maps `Ġ t` → `\x20 t`, `h e` → `h e`, `Ġt he` → `\x20\x74 he` (via `format_merge_token`; mixed space+letter tokens are fully hex-escaped)
- [x] Inverse mapping covers all 256 bytes bijectively
- [x] `gpt2.merges` and `smollm2.merges` are committed and parse with no issues
- [x] Both dictionaries are proper; GPT-2 has 50 000 rules; SmolLM 2 rule count is recorded and matches the converted non-comment line count
- [x] Attribution file records URL, revision, raw SHA-256, licence, date
- [x] Raw HF files are not committed
- [x] `fetch_dictionaries.py` is optional; `make check` does not call it
- [x] Prefixes 0–2 over the byte alphabet construct for baseline and compact
- [x] No new third-party dependencies

## Required test evidence

### Unit tests

- Frozen HF snippets (no network): first GPT-2-style lines including `Ġ`
- Comment / version header skipped
- Unmapped character raises
- Wrong arity line raises
- `format_token_label` round-trip of decoded tokens through `parse_merge_list`

### Regression tests

- Committed files parse
- `validate_proper` on both
- Rule counts

### Differential or exhaustive tests

- Mapping is a bijection on `{0,…,255}`

### Property or equivalence tests

- Not required beyond bijection

### Negative and special cases

- SmolLM 2 mapping failure path (unit with a fake character) if the real file converts; if the real file fails, the ticket stops rather than weakening the test

## Documentation changes

- [ ] Public API or README (brief pointer that realistic files exist; full 5.6 runner is TICKET-016)
- [ ] Architecture or algorithm documentation
- [ ] Decision record — attribution file is enough here; design-decisions §5.6 in TICKET-016
- [ ] Testing documentation
- [ ] Experiment documentation
- [ ] Known limitations (display encoding; O4 unused)

State specific expected updates:

- `data/dictionaries/REALISTIC.md`
- Optional one-line README note under experiments, without claiming the timeout study is done

## Validation commands

```bash
cd 26455900-CS345
make check
```

Additional commands:

```bash
uv run python experiments/fetch_dictionaries.py
```

Network is required only for the optional fetch. After the converted files are committed, `make check` must pass offline.

## Risks

- Formal interpretation: treating HF `merges.txt` as UTF-8 would silently build the wrong dictionary
- Correctness: SmolLM 2 encoding may differ; stopping is required
- Performance: converting 50k lines is cheap; constructing even 2 rules over 256 symbols must stay inside pytest time
- Compatibility: do not change D4 parser rules for GPT-2 quirks
- Scope: do not start TICKET-016
- Reproducibility: pin revision and SHA-256; do not track `resolve/main` without a hash

## Open questions

None blocking. Exact Hugging Face revisions/hashes are captured on first successful fetch.

Do not begin implementation while a blocking question remains unresolved.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] Attribution committed.
- [ ] `make check` passes offline.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Handoff produced where appropriate.
- [ ] Human review completed before TICKET-016’s long run.
- [ ] Both partners can explain the conversion (`Ġ` = space).
