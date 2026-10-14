# Design decisions (Sections 5.1–5.6, testing §6, experiments §7)

This document records implementation choices for the dictionary model, reference tokenizer, baseline token DFA, Section 5.3 worked examples, transducer, compact delayed-input automaton, the Section 5.6 timeout study, and Section 7 measurements.

## Alphabet representation (D1)

- **Choice:** UTF-8 **bytes** (values 0–255).
- **Base tokenization:** `T_∅(w)` splits input `w: bytes` into length-1 byte tokens.
- **Implication:** Non-ASCII text and emoji are multi-byte sequences; token identity follows bytes, not Unicode code points or grapheme clusters. Section 5.3 worked examples that demonstrate this are in [`token-dfa-examples.md`](token-dfa-examples.md).

## Canonical semantics (D2)

- **Choice:** SentencePiece tokenization `T^D` (Berglund & van der Merwe [6], Definition 3).
- At each step: among all applicable merge rules, pick **highest priority** (smallest rule index); merge the **leftmost** occurrence; repeat until no rule applies.
- For **proper** dictionaries this coincides with HuggingFace semantics (Lemma 1); we do not implement a separate HF mode.

## Dictionary file formats (D3–D4)

- **Merge list** (`.merges`): one rule per line, `left right` or `left⫽right`; priority = line order; `#` starts a comment.
- **YAML fixtures** (`.yaml`/`.yml`): `rules:` list of `{left, right}` mappings for small test dictionaries.
- Token literals use UTF-8 text; `\xHH` is the only escape (one raw byte). Other backslash sequences are rejected.
- Duplicate rules and empty tokens are rejected at parse time.

Paper [6] Example 1 uses `D = [a⫽b, a⫽bc, b⫽c, ab⫽c]`, which is improper (`bc` is used before it is produced). The fixture `data/dictionaries/example1.merges` is the proper reordering `[a⫽b, b⫽c, a⫽bc, ab⫽c]`. For `w = abcbcab` the SentencePiece derivation is unchanged because `a⫽bc` never applies.

## Proper dictionary validation

- Implements Definition 5 from [6]: every token of length > 1 on either side of a rule must be produced by a higher-priority rule.
- **Useless** rules (never applied) may still be proper; **improper** dictionaries are rejected by the reference tokenizer.

## Error handling

- Parsing and validation return structured issue lists with line/rule indices where available.
- `tokenize_reference` raises `ImproperDictionaryError` on improper dictionaries.

## Baseline token DFA (Section 5.2)

- **Construction:** Algorithm 2 of Berglund, Martens and van der Merwe [5], applied in dictionary-priority order. The implementation follows the PDF pseudocode (p. 4) and Figs. 3–4, not Example 2’s “non-ba” sentence (that sentence contradicts line 14 and the figures).
- **Base automata:** `universal_token_dfa(Σ)` is one accepting state with a self-loop on each length-1 token in `Σ`. Paper fixtures use `{a,b}` or `{a}`. The D5 full-byte automaton is the same constructor with `Σ = {0,…,255}` (`byte_alphabet()`). User-supplied string DFAs load from YAML (`data/automata/`).
- **Improper dictionaries:** rejected (`ImproperDictionaryError`), matching the reference tokenizer.
- **No trimming.** Per-rule counts include Algorithm 2’s untrimmed fresh states.
- **`u = v`:** fresh states inherit `Γ \ {v, uv}`. **`u ≠ v`:** they inherit `Γ \ {v}` (including `uv`). Redirect of `u`-edges includes edges just copied onto fresh states (Remark 3).
- **Empty `S`:** language unchanged; `uv` is still added to `Γ`.
- **Outputs:** `ConstructionResult` records `n_states`, `n_final`, `n_tokens`, `n_transitions`, `n_fresh` after each rule; `MergeTrace` records triples, fresh states, added \(uv\)-edges, inherited copies, omitted labels, and redirected \(u\)-edges; `serialize_token_dfa` is deterministic text; `to_dot` is optional Graphviz. The construction stays a library function; `scripts/demo.py` is a presentation wrapper only.

Worked paper and original examples, including Unicode/emoji token identity, are in [`token-dfa-examples.md`](token-dfa-examples.md).

## String-to-tokenization transducer (Section 5.4)

- **Construction:** Observation 3 of [5] (PDF p. 10) on the token DFA, then Béal–Carton [3, §2.2] (PDF pp. 233–234). Public tokenizer: `compile_tokenizer` / `tokenize`.
- **Fig. 8:** locked against the PDF (p. 11). Observation 3 is input-nondeterministic on leftover `a` vs `aa`. The subsequential machine delays that `a` in \(F(q)=a\) and may emit two tokens on one edge (`b|a ⫽ b`).
- **Outputs on edges:** `TokenSequence` (empty = \(\varepsilon\)). Observation 3 emits \(\varepsilon\) or one token; the subsequential machine may emit a longer word (Fig. 8(b), Béal–Carton).
- **Independence:** transducer modules do not import `tokenize_reference`.
- **Errors:** improper dictionaries raise `ImproperDictionaryError`; strings outside the base language raise `TokenizationError`. Determinisation caps pending output at \(2n^2 M\) (Lemma 16) and raises `TransducerError` instead of truncating.
- **No trimming** of Observation 3 spelling states. The construction stays a library function; `scripts/demo.py` is a presentation wrapper only. Intermediate ids: next integers after the DFA, in sorted DFA-transition order; Béal–Carton subset ids by BFS on sorted input bytes.
- **minbpe:** test adapter injects our merge list into the BasicTokenizer encode loop (MIT, Karpathy). Byte-level only; no regex pre-tokenization.
- **Performance:** thin `experiments/transducer_tokenize.py` measurements; not the §5.6 timeout study. Interpret as in [5] Corollary 14: linear *after* compile; compiled state space may still be large.

Walkthrough: [`transducer.md`](transducer.md).

## Compact delayed-input automaton (Section 5.5)

- **Construction:** Algorithm 2 of Berglund, Jonsson, Martens and van der Merwe [4] (PDF p. 5) on a D²FA. [4] Algorithm 1 is this project's baseline ([5] Algorithm 2).
- **O1** (default transitions) is always on: `fresh(s2)` gets \(\nu=\mathrm{s}_2\) and sink edges on \(v\) (and on \(uv\) iff \(u=v\)) instead of copying outgoing transitions.
- **O2** (state-avoidance) and **O3** (clean-copy reuse) are `CompactOptions` flags, default **on**. Tests also run with both off (Algorithm \(2^X\)). **O4** (prefix-forest sink predicates) is not implemented.
- **Sink:** compact model only. Lift adds an unused non-accepting \(q_s\) with no outgoing edges. `step` treats the sink and \(\bot\) as reject. The paper's complete self-loops on \(q_s\) are omitted so they are not counted as explicit transitions.
- **Triples:** explicit \(\delta(s_1,u)\) and extended \(\delta^\nu(s_2,v)\). Do not copy baseline triple-finding.
- **Clean-copy \(\Lambda\):** sink labels written by O1 (\(\{v\}\), or \(\{v,uv\}\) if \(u=v\)). Definition 4's \(\Lambda=\{u\}\) when \(u\neq v\) contradicts Fig. 2; the algorithm wins.
- **Line 9:** \(s_2=q_0\) is never O2-eligible.
- **Equivalence:** `accepts` via \(\delta^\nu\), plus `languages_agree` (product BFS on the compact extended transition) and `token_dfa_languages_agree(baseline, expand_defaults(compact))` (Observation 1, sink dropped). Not raw \(\delta\) tables. Compact modules do not import `tokenize_reference`. Product expansion is **not** run on GPT-2 / SmolLM (256-byte / ~50k-token alphabets); see [`testing.md`](testing.md).
- **Counts:** `n_states` in `CompactStep` excludes the sink. The construction stays a library function; `scripts/demo.py` is a presentation wrapper only. There is no Graphviz or merge-trace output for the compact automaton.
- **Line 3 guard:** if \(\delta(q,u)=q_s\) but \(\delta^\nu(q,uv)\) already reaches a live state, do not overwrite that path with a sink. Paper [4] Lemma 3 assumes unique useful concatenations; this project allows proper useless rules that reuse `uv` (Hypothesis dictionary \([a⫽a, aa⫽a, a⫽aa]\)).
- **Performance:** thin `experiments/compact_compare.py` on existing small dictionary prefixes; not the §5.6 timeout study.

## Larger-dictionary timeouts (Section 5.6)

- **Dictionaries:** converted GPT-2 and SmolLM 2 merge lists (`data/dictionaries/gpt2.merges`, `smollm2.merges`). Attribution and pins: [`data/dictionaries/REALISTIC.md`](../data/dictionaries/REALISTIC.md).
- **Alphabet:** every study construction starts from `universal_token_dfa(byte_alphabet())`.
- **Constructions:** baseline `apply_merge` and compact `apply_compact_merge` with public defaults (O1 on, O2/O3 on). **O4 is not implemented.** The transducer is not in this table.
- **Limits:** 60 s cutoff (annotation only), 600 s wall-clock stop, 8 GiB RSS. Child process uses `RLIMIT_AS` (virtual size, not RSS) plus an `ru_maxrss` poll. Linux `ru_maxrss` is KiB and is converted to bytes in the JSON.
- **Run shape:** one 10-minute child per `(dictionary, construction)`, sequential. Incremental merges from \(A_0\); JSONL checkpoints at geometric prefixes, at the 60 s crossing, and at stop. Timeouts and OOM are results; they are not estimated or averaged into successful times.
- **Comparison:** shared-prefix rows only where both constructions finished; plus per-construction failure boundaries.
- **Runner:** `uv run python experiments/timeout_study.py`. Not part of `make check`. Toy scripts `transducer_tokenize.py` and `compact_compare.py` remain §5.4–5.5 only.

## Experimental evaluation (Section 7)

- **Reuse §5.6** for Q1/Q2/Q4. Do not rerun the 10-minute study for this document.
- **Q3:** per-rule `n_fresh` from existing `ConstructionStep` / `CompactStep`. `compact_reused` means compact `n_fresh == 0`. Paper-chain O2/O3 on vs off is the reuse witness. GPT-2 / SmolLM rows are prefix 250 only.
- **Q5:** match-rate JSON on Example 2 `{a,b}^{≤8}`, unary \(a^{≤8}\), and minbpe `{a,b}^{≤6}`. Expect rate 1.0. Broader evidence remains [`testing.md`](testing.md).
- **Q6:** input **bytes per second** on lengths 256…65536. Ordinary `(ab)^{n/2}`; pathological \(a^n\). Compile once; warmup + 7; median. 60 s row cap. Peak memory is `tracemalloc`, not RSS. No GPT-2 transducer compile.
- **Tables:** [`experiments.md`](experiments.md). No matplotlib in this phase.
- **Runners:** `uv run python -m experiments.rule_patterns` and `uv run python -m experiments.tokenize_eval`. Not part of `make check`.

## Module layout

```text
src/bpe_token_automata/
├── tokens.py
├── reference_tokenizer.py
├── dictionary_equivalence.py
├── partial_order.py
├── pattern_matching.py
├── dictionary/
├── automaton/
│   └── compact.py
└── transducer/
    ├── model.py
    ├── observation.py
    ├── determinize.py
    ├── tokenize.py
    ├── serialize.py
    └── graphviz.py
```

## References

- CS345 project specification Sections 5.1–7
- Berglund & van der Merwe, *Formalizing BPE Tokenization* (EPTCS 388, 2023)
- Berglund, Martens & van der Merwe, *Constructing a BPE Tokenization DFA* (TCS 1083, 2026)
- Berglund, Jonsson, Martens & van der Merwe, *Constructing Compact BPE Token DFAs* (CIAA 2025)
- Béal & Carton, *Determinization of transducers over finite and infinite words* (TCS 289, 2002)
