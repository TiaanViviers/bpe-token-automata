# Section 6 testing audit

Coverage audit of course spec **§6 Testing and verification requirements** against the
tests currently on `26455900-CS345` `main`. This is **not** an implementation plan
and does not create tickets.

## Metadata

| Field | Value |
|---|---|
| **Status** | `audit` — input to a later Section 6 plan; not human-approved direction |
| **Date** | 2026-09-14 |
| **Repository HEAD** | `dcedef2` (`Implement the Section 5.6 larger-dictionary timeout study.`) |
| **Branch** | `main`, clean, up to date with `origin/main` |
| **Course spec** | §6.1–6.7 (PDF pp. 5–6); Markdown conversion `research/markdown/cs345-project-specification/index.md` |
| **Local rules** | [`../rules/testing-and-correctness.md`](../rules/testing-and-correctness.md) |
| **Out of repo** | This file lives under `agent/plans/`. Do not copy it into `26455900-CS345/`. |

## How to read this document

Section 6 is a **verification overlay**, not a new construction like 5.1–5.6. Most
of 6.1–6.5 was written while those constructions were implemented. The question
now is: which spec bullets are already evidenced, which are only partly evidenced,
and which still need tests or report artefacts.

Verdicts:

| Verdict | Meaning |
|---|---|
| **covered** | An existing test (or paper-example fixture) discharges the bullet. Optional polish only. |
| **partial** | Something related exists, but the spec’s stated check is missing or weaker than required. |
| **missing** | No adequate evidence. This is remaining implementation (or report) work. |
| **out of band** | Exists, but it is Section 5.6 / 7 experiment smoke, not a §6 family. |

Do not treat pytest function count as the deliverable. The spec wants independent
fault classes, stated bounds, and a report matrix.

## Existing test inventory (HEAD)

About 90 pytest functions across 21 modules (plus Hypothesis examples inside one
test). Collected from source; `uv run pytest --collect-only` was not available in
this environment because the project venv was not installed.

| Module | Role relative to §6 |
|---|---|
| `tests/test_dictionary_parser.py` | 6.1 improper / malformed; 6.6 unsupported encodings |
| `tests/test_dictionary_validator.py` | 6.1 improper; weak useful/useless |
| `tests/test_reference_tokenizer.py` | 5.1 oracle; 6.1 empty/self-merge/improper; 6.2/6.4 detokenize |
| `tests/test_tokens.py` | token identity / detokenize utilities |
| `tests/test_token_dfa_construction.py` | 6.1 unit cases |
| `tests/test_token_dfa_examples.py` | paper Example 2 + unary; 6.1 loops/fresh/self-merge via traces |
| `tests/test_token_dfa_exhaustive.py` | 6.2–6.3 DFA vs oracle vs transducer, bound 6 |
| `tests/test_token_dfa_unicode.py` | 6.1 Unicode/emoji identity |
| `tests/test_transducer_tokenize.py` | 6.2 helper `assert_section_62` on samples |
| `tests/test_transducer_exhaustive.py` | 6.3 unary + uniqueness (token-seq length ≤ 4) |
| `tests/test_transducer_properties.py` | 6.4 Hypothesis |
| `tests/test_transducer_unicode.py` | 6.2 on Unicode/emoji dictionaries |
| `tests/test_transducer_minbpe.py` | extra independent oracle (5.4); supports 6.2 |
| `tests/test_transducer_observation.py` | 5.4 construction, not a §6 family |
| `tests/test_transducer_determinize.py` | 5.4 construction / caps |
| `tests/test_compact_construction.py` | 6.1 compact specials; some 6.5 `expand_defaults` *counts* |
| `tests/test_compact_equivalence.py` | 6.5 product + bounded exhaustive |
| `tests/test_package_smoke.py` | import smoke |
| `tests/test_hf_merges.py` | 5.6 conversion (not §6) |
| `tests/test_realistic_dictionaries.py` | 5.6 parse/proper/smoke (not §6) |
| `tests/test_timeout_study.py` | 5.6 harness smoke (not 6.6) |

`make test` / `make check` already exist (`Makefile`). Pytest writes
machine-readable logs; `.hypothesis/` is gitignored.

---

## 6.1 Deterministic unit and regression tests

Fault class: Algorithm 2 local mistakes (wrong copy/omit, wrong redirect, silent
improper input, Unicode normalisation).

| Spec bullet | Verdict | Existing evidence | Remaining |
|---|---|---|---|
| Empty dictionary: token DFA coincides with base | **covered** | `test_empty_dictionary_leaves_base_unchanged`; compact twin `test_empty_dictionary_matches_baseline_language`; reference `test_empty_dictionary_returns_base_tokenization` | None required |
| No-op rule: no run reads \(u\) then \(v\) | **covered** | `test_noop_rule_does_not_change_language` (alphabet `{b}`, rule `a ≀ a`) | None required |
| Fresh-state: copied, omitted, accept inheritance | **covered** | construction tests + Example 2 / unary traces (`inherited`, `omitted_labels`, `s2_to_fresh`) | Optional: one named test that asserts copy vs omit in one place |
| Self-merge \(u=v\): LTR; invalid \(uv\) not inherited | **covered** | `test_self_merge_does_not_copy_uv_onto_fresh_state`; reference `test_self_merge_applies_leftmost_once_per_step`; compact `test_self_merge_fresh_state_sinks_on_v_and_uv`; unary fixture | None required |
| Distinct merge \(u\neq v\): non-\(v\) outgoing preserved | **covered** | Example 2 Fig. 3 edge set + `test_distinct_merge_copies_uv_onto_fresh_state` (checks `ba` on fresh, omits `a`) | The small unit test is narrower than the figure match; figure match is enough |
| Loops and multiple incoming: redirect every predecessor | **covered** | Example 2 second merge `redirected == ((0,b,0,2),(1,b,0,2),(2,b,0,2))`; unary `(0,aa,0,2),(2,aa,0,2)` | Optional named test for the report matrix; behaviour is already locked |
| Final and non-final intermediate states | **covered** | `test_fresh_state_inherits_accepting_status`; `test_fresh_state_from_non_accepting_s2_is_not_accepting` | None required |
| Improper dictionary: reject or diagnose | **covered** | parser/validator Example 3; DFA, compact, transducer, reference all raise `ImproperDictionaryError` | None required |
| Useful and useless rules: whether the rule changes reachable behaviour | **partial** | Validator: `test_proper_with_useless_rule_still_validates`. Constructor: `test_useless_but_proper_rule_constructs` only checks `n_states >= 1` and four steps. Fixture `proper_with_useless_rule.yaml` (`[b≀c, a≀b, c≀d, ab≀cd]`) | **Need:** compare accepted language (or bounded tokenizations) before vs after a *useless* rule (unchanged) and after a *useful* rule (changed). Spec wording is about behaviour, not merely “it constructs” |
| Unicode and emoji alphabets: token identity, no accidental byte/NFC change | **covered** | `test_nfc_and_nfd_eacute_are_different_byte_strings`; `test_token_identity_is_byte_equality`; original é / 😀 merge traces; transducer Unicode tests | Mixed combining+whitespace+emoji is 6.6, not this bullet |

**6.1 remaining implementation:** one useful-vs-useless language test (and
optionally a named multi-predecessor redirect test for the matrix).

---

## 6.2 Differential testing against an independent oracle

Fault class: transducer agrees with \(T^D\) on *token sequences*, not just on
concatenated bytes; DFA accepts only the canonical grouping.

For each test string \(w\) the spec requires all five:

1. output sequence identical to `tokenize_reference`;
2. every output token is in the dictionary-induced token alphabet;
3. concatenation equals \(w\);
4. token DFA accepts the output;
5. a non-canonical regrouping of the same \(w\) is rejected.

| Check | Sample path (`assert_section_62`) | Exhaustive Example 2 (`test_token_dfa_exhaustive`) | Unary exhaustive | Unicode transducer |
|---|---|---|---|---|
| (1) sequence equality | yes | yes | yes | yes |
| (2) tokens in alphabet | yes (`token in dfa.alphabet`) | no | no | no |
| (3) detokenize \(= w\) | yes | **no** | yes | yes |
| (4) DFA accepts canonical | yes | yes | yes | yes |
| (5) altered boundaries rejected | yes (split first long token) | only fully-split base if it differs | no | no |

`assert_section_62` is the right helper. It is only used on:

- self-merge sample strings;
- Example 2 strings of length 3 (not the exhaustive bound).

minbpe (`test_transducer_minbpe.py`) is a *third* oracle on sequences; it does
not run checks (2)–(5). That is extra 5.4 evidence, not a substitute for 6.2.

**6.2 remaining implementation:** run the full five-check helper on the exhaustive
Example 2 family (and unary), not only on samples. Extending `assert_section_62`
into `test_token_dfa_exhaustive.py` / `test_transducer_exhaustive.py` is enough;
do not invent a second oracle.

---

## 6.3 Exhaustive bounded testing

Fault class: fresh-state redirection and self-merges on *every* short string;
uniqueness of accepted tokenization.

| Requirement | Verdict | Evidence | Remaining |
|---|---|---|---|
| Enumerate every string up to a stated bound | **covered** with a **stated bound of 6**, not the spec’s example of 8 | `{a,b}^{≤6}` Example 2 in `test_token_dfa_exhaustive.py`; unary `a^{≤8}` | Spec’s “for example length eight” is an illustration. Either raise Example 2 to 8 *or* keep 6 and write the bound in the 6.7 matrix. \(2^8=256\) vs \(2^6=64\) is cheap |
| Compare reference, transducer, and DFA acceptance | **partial** | Exhaustive file compares all three on sequences + DFA accept; missing some 6.2 clauses (above) | Same as 6.2 remaining |
| Enumerate token sequences; exactly one accepted tokenization per string | **partial** | `test_example2_transducer_enumerates_token_uniqueness_bound`: enumerates token sequences of **length ≤ 4** over \(\Gamma\), then keeps those whose detokenization is in `{a,b}^{≤6}` | Strings whose canonical (or non-canonical) tokenization has **more than 4 tokens** are not in the uniqueness scan (e.g. `bbbbbb` under Example 2). Need a uniqueness check whose token-sequence bound covers the string bound, or enumerate partitions of each \(w\) |

**6.3 remaining implementation:** (a) decide bound 6 vs 8 and record it; (b) make
uniqueness cover the same string bound.

---

## 6.4 Property-based and fuzz testing

Fault class: bugs that only appear on dictionaries nobody hand-wrote; missing
reproducibility when Hypothesis finds a counterexample.

Existing: `tests/test_transducer_properties.py`

- Generator builds rules from tokens already present → proper dictionaries.
- Alphabet `{a,b,c}`, ≤ 3 rules, strings of length ≤ 6, `max_examples=40`.
- Checks: sequence vs oracle, \(\pi(T^D(w))=w\), DFA accept, stability
  (re-tokenize detokenized output), compact `accepts` agreement, `languages_agree`.

| Spec property | Verdict | Notes |
|---|---|---|
| Detokenization \(\pi(T^D(w))=w\) | **covered** | |
| Stability | **covered** | transducer and reference |
| DFA agreement | **covered** | |
| Uniqueness within the tested bound | **missing** | Not checked on generated dictionaries |
| Baseline/compact agreement | **covered** | `accepts` + `languages_agree` |
| Reproducibility: log dictionary, seed, input, smallest counterexample | **partial** | No `@settings(seed=…)` / `derandomize`. The `seed` argument is a string-generator integer, not Hypothesis’s PRNG seed. TICKET-010 asked for a recorded seed and did not land it. `.hypothesis/` is gitignored, so shrinks are local-only. No project-side failure log |

The generator can skip adding a rule (`continue` on duplicate / too-long merge),
so “`n_rules` drawn as 3” may yield fewer rules. That is acceptable for
properness; mention it in the matrix.

**6.4 remaining implementation:** uniqueness on generated instances (small bound);
explicit Hypothesis seed (or `derandomize=True` plus a documented seed); a
failure-recording convention (pytest traceback is the log; optionally persist
shrunk `(dictionary, text)` as a regression fixture when one appears).

---

## 6.5 Automata equivalence tests

Fault class: compact defaults / O2 / O3 change the language; comparing raw
transition tables would hide that.

Spec asks for **two complementary methods**:

1. Exhaustive comparison on bounded token sequences.
2. Where practical: expand compact default transitions, then a product-automaton
   symmetric-difference emptiness check. State limits (large alphabets, partial
   \(\delta\)) explicitly.

| Method | Verdict | Evidence | Remaining |
|---|---|---|---|
| Bounded token/string comparison | **covered** | `test_product_and_exhaustive_example2` (`{a,b}^{≤6}` plus token sequences length ≤ 4); emoji compact vs baseline; flag combinations; O1 Example 2 / unary | Token-seq bound 4 has the same hole as 6.3 uniqueness |
| Product emptiness | **partial** | `languages_agree` is a product BFS of baseline `TokenDFA` vs compact `DelayedInputDFA.step` (\(\delta^\nu\)), not raw tables. That *is* a language-equivalence check using extended transitions | Spec’s second method also says **expand defaults first**. `expand_defaults` exists (Observation 1) but tests only compare **`n_states`**, not language of the expanded DFA vs baseline |
| Stated limitations | **partial** in private/assessable design notes | `docs/design-decisions.md` says `languages_agree` is for small \(\Gamma\). No assessable sentence that product expansion is **not** run on GPT-2’s 256-byte / 50k-token alphabets | Need an explicit limitation in the 6.7 matrix / report. Do not attempt product on realistic dictionaries |

Interpretation (for the later plan, do not silently pick one):

- **Reading A:** `languages_agree` already is method 2, because it uses
  \(\delta^\nu\) instead of expanding. Then remaining work is documentation plus
  a small `expand_defaults` *language* check as belt-and-braces.
- **Reading B:** method 2 requires materialising `expand_defaults(compact)` and
  a TokenDFA–TokenDFA product. `languages_agree` is method 1-adjacent (semantic
  `step`), not method 2.

Recommend implementing the cheap belt-and-braces test on Example 2 / unary
(`expand_defaults` then agree with baseline on the same bounded set *or* a
TokenDFA product) so both readings are satisfied, and stating the large-alphabet
limit in the matrix.

**6.5 remaining implementation:** expand-then-agree test on small dictionaries;
write the GPT-2/SmolLM limitation (do not run 6.5 on 5.6 prefixes).

---

## 6.6 Pathological and robustness tests

Fault class: latency/complexity and correctness on structured adversarial inputs
(streaming BPE papers [13], [11]). **This is not Section 5.6.**

| 5.6 (done) | 6.6 (mostly missing) |
|---|---|
| Construct automata on GPT-2 / SmolLM prefixes until 60 s / 600 s / 8 GiB | Automated tests of tokenizer/DFA *behaviour* on nasty small instances |
| `make check` must *not* run the 10-minute study (D52) | These tests **should** run under `make test` at modest size |
| Experiment results in JSON | Pass/fail assertions |

| Spec stress case | Verdict | Nearby evidence | Remaining |
|---|---|---|---|
| Repeated-character \(a^n\) for increasing \(n\) | **partial** | Unary exhaustive/compact up to \(n=8\) | Need a dedicated increasing-\(n\) case (e.g. 8, 16, 32, 64) still cheap in `make test`. Huge \(n\) is §7 Q6 throughput, not this suite |
| Nested merge chain \([a≀a,\ aa≀aa,\ aaaa≀aaaa,\ \ldots]\) | **partial** | Compact `test_o1_plants_sink_on_new_uv_before_defaults_inherit_it` is the **two-rule** prefix of this family. Project unary fixture is \([a≀a,\ aa≀a]\), a **different** chain | Need a longer doubling dictionary and oracle/DFA/transducer agreement on \(a^{2^k}\) |
| Long inputs without pre-tokenization boundaries | **missing** | minbpe adapter is already byte-level (no GPT-2 regex). No long unspaced string test | One long `{a,b}` or repeated-byte string with no spaces, compare oracles + DFA |
| Initial token changes after a later symbol is appended | **missing** | Self-merge `aaa → (aa, a)` is related but not stated as a streaming prefix check | Named test: e.g. \(D=[a≀a]\), \(T^D(\texttt{a})=(a)\) but \(T^D(\texttt{aa})=(aa)\) — first token changes when one byte is appended. Stronger dictionaries if easy |
| Mixed Unicode, combining marks, whitespace, emoji | **partial** | NFC vs NFD é (combining acute as a *separate* string); 😀 as its own dictionary; no **single mixed** input; no whitespace token | One mixed string (e.g. space + combining mark + emoji) under byte identity; confirm no NFC collapse |
| Malformed dictionaries and unsupported encodings | **covered** | malformed line, duplicate, empty token, `\u` escape, improper Example 3, HF converter negatives | None required for this bullet |

Do **not** count `test_timeout_study.py` / `test_realistic_dictionaries.py` as 6.6.

**6.6 remaining implementation:** a new test module (or a clearly named group)
with the five stress cases above, sizes compatible with `make check`.

---

## 6.7 Test evidence in the submission

| Requirement | Verdict | Evidence | Remaining |
|---|---|---|---|
| Automated tests in the repo | **covered** | `tests/` | Keep filling gaps; no reorganisation required (`testing-and-correctness.md` family directories are optional) |
| A command that runs them | **covered** | `make test`, `make check` | Mention both in the report |
| Report test matrix: family, fault class, case count, outcome | **missing** | No matrix in `docs/`. Report (§9.1 “testing methodology and evidence”) is not written yet | **Report artefact**, not production code. Draft can live under `agent/` until the PDF chapter exists. Case counts should come from a real `make test` run after gap-fill |
| Screenshots are not a substitute for machine-readable logs | **covered** if pytest output / coverage is kept | `pyproject.toml` `--cov` | Store or cite pytest logs; do not screenshot the green bar |

Course §10: testing marks are assigned through the other criteria (baseline,
transducer, compact, …), not as a separate 15-point bucket in the converted
table. Unsupported correctness claims still lose marks. The matrix is still
compulsory in the report.

---

## What does *not* still need implementing for §6

These look like tests but are the wrong family:

- 5.6 timeout harness smokes, GPT-2/SmolLM parse+proper, HF mapping bijection.
- 5.4 Observation 3 / subsequentialisation unit tests (they support 5.4, not 6.x).
- Toy experiment scripts (`transducer_tokenize.py`, `compact_compare.py`,
  `timeout_study.py`) — Section 7 measurements.
- Extension 8.2 dictionary-equivalence product constructions. 6.5 is
  **baseline vs compact**, not dictionary vs dictionary.
- Replacing the 5.1 reference tokenizer or correlating expected fixtures from
  `apply_merge`.

---

## Remaining work (checklist for the later plan)

Must-do to match the spec wording:

1. **6.1** useful vs useless: language (or bounded acceptance) changes or not.
2. **6.2** full five-check helper on exhaustive Example 2 and unary families.
3. **6.3** uniqueness bound aligned with the string bound; record max length.
4. **6.4** uniqueness property; documented Hypothesis seed; how failures are logged.
5. **6.5** `expand_defaults` language agreement on small dictionaries; write
   large-alphabet limitation.
6. **6.6** new pathological module (five missing/partial bullets).
7. **6.7** test matrix for the report (after the tests exist and `make test` is
   run). Can be drafted under `agent/` first.

Nice-to-have, not blockers:

- Named 6.1 multi-predecessor / loop test (already true via Example 2 traces).
- Raise Example 2 exhaustive length 6 → 8.
- Persist the first Hypothesis shrink as a regression fixture (only if one is found).
- Split `tests/` into `unit/` `exhaustive/` `property/` directories.

Suggested later ticket grain (not written yet): **not** seven tickets mirroring
6.1–6.7. Three is enough:

1. Gap-fill 6.1–6.5 (small tests + Hypothesis seed + expand-defaults language).
2. New 6.6 pathological suite.
3. 6.7 matrix (report; maybe a short `docs/` pointer once the report exists).

## Open questions for the implementation plan

1. Example 2 exhaustive bound: keep 6 and disclose, or raise to 8?
2. Uniqueness: enumerate byte-string partitions of each \(w\), or raise the
   token-sequence product bound so it covers length-6 unmerged strings?
3. 6.5 reading A vs B (document `languages_agree` as method 2, or add an
   expanded-TokenDFA product)? Recommendation above: do both cheaply on small
   dictionaries.
4. 6.6 sizes that must stay inside `make check` (proposal: \(n \le 64\) or a
   short wall-clock budget; leave huge \(n\) to §7 Q6).
5. Where the 6.7 matrix lives before the PDF report exists (`agent/` only vs a
   small table in `26455900-CS345/docs/`).
6. Whether Hypothesis should use a fixed `seed=` in `@settings` (reproducible
   across machines) vs relying on pytest + `.hypothesis/` locally.

## Next step

Human review of this audit, then a Section 6 implementation plan with tickets.
Do not implement from this file until that plan is approved.
