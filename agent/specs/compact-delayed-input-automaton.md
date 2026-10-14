# Compact delayed-input token automaton (Section 5.5)

Engineering specification for the compact D²FA construction of Berglund, Jonsson, Martens and van der Merwe [4].

## Goal

Given a proper dictionary \(D\) and a string/token DFA for a regular language \(L\), construct a delayed-input DFA \(A\) such that \(\mathcal{L}(A)=\mathbb{T}^D(L)\). Equivalence with the Section 5.2 baseline is semantic: compare languages via the extended transition function \(\delta^\nu\), not raw transition tables (Observation 1, Lemma 1, Theorem 1).

O1 (default transitions) and explicit sink/reject handling are required. O2 and O3 are in scope as flags. O4 is out of scope.

## Background

- **Course requirement:** spec §5.5 (default transitions, named optimisations, semantic equivalence, comparison columns). Spec §4.3 (default transitions as a distinct concept). Spec §6.4–6.5 (baseline/compact agreement; product emptiness where practical). Spec §7.1 comparison metrics on dictionary prefixes.
- **Research:** [4] Definition 2, \(\delta^\nu\), Observation 1 (PDF p. 3); Algorithm 2 (PDF p. 5); Definitions 3–4 (PDF p. 4); Lemma 1 / Theorem 1 (PDF pp. 5–7).
- **Locked project decisions:** D1 bytes; D2 SentencePiece \(T^D\); D15 reject improper dictionaries; D14 no trim; D17 sorted fresh ids.

ASSUMPTIONS (locked 2026-09-13 with the human):

1. O1 is always on. CompactOptions exposes `o2_state_avoidance` and `o3_clean_copy` (default **True**). Tests also run with both False (Algorithm \(2^X\)).
2. O4 (prefix-forest sink predicates) is deferred.
3. Explicit sink \(q_s\) lives only on the compact model. Do not add a sink to `TokenDFA`.
4. Independent module `automaton/compact.py`. Do not extend `TokenDFA` with \(\nu\).
5. Algorithm 2 line 9 “or \(q=q_0\)” means \(s_2=q_0\) (PDF Example 1).
6. Definition 4’s \(\Lambda=\{u\}\) when \(u\neq v\) contradicts Algorithm 2 lines 16–18 and Fig. 2. Implement \(\Lambda=\{v\}\) if \(u\neq v\) and \(\Lambda=\{v,uv\}\) if \(u=v\) (the sink labels O1 writes on a fresh state).
7. No CLI. No Graphviz. No merge-trace bookkeeping beyond comparison counts.
8. Compact production code must not import `tokenize_reference`.
9. Paper sink completeness \(\delta(q_s,u)=q_s\) for all \(u\) is represented by treating \(q_s\) as a dead reject state with **no** outgoing edges. Language-equivalent; avoids \(|\Gamma|\) counted self-loops.
10. [4] Algorithm 1 is the existing baseline ([5] Algorithm 2). [4] Algorithm 2 is this section.
11. Algorithm 2 lines 2–3 do not overwrite a live \(\delta^\nu(q,uv)\). Needed because proper dictionaries may reuse a concatenation (Lemma 3 of [4] assumes unique useful `uv`).

## Scope

- `DelayedInputDFA` with partial \(\delta\), partial acyclic \(\nu\), distinguished \(q_s\notin F\), `step` via \(\delta^\nu\), `accepts`.
- Lift a `TokenDFA` by adding an unused sink.
- `apply_compact_merge` = [4] Algorithm 2; `construct_compact_token_dfa` applies rules in dictionary order.
- `expand_defaults` = Observation 1 with sink and edges-to-sink removed (Lemma 1’s \(C\)).
- Deterministic textual serialisation.
- Product-style language agreement with the baseline on small alphabets.
- Thin prefix comparison experiment on existing small dictionaries (not §5.6).

## Non-goals

O4; §5.6 timeouts / realistic dictionaries; trimming; CLI; Graphviz; changing `TokenDFA`; compact merge traces; 8.2/8.11; feeding the compact automaton into the 5.4 transducer.

## Authoritative sources

| Source | What it governs |
|---|---|
| Course spec §5.5, §4.3, §6.4–6.5, §7.1 | Requirements, tests, comparison columns |
| [4] PDF Def. 2 p. 3; Alg. 2 p. 5; Def. 3–4 p. 4; Lemma 1 | Construction and equivalence |
| [5] / existing `construct_token_dfa` | Independent language oracle |
| Human-approved 5.5 plan | O2/O3 flags, no O4, compact-only sink, Def. 4 \(\Lambda\) |

## Interfaces

Package: `bpe_token_automata.automaton` (types live in `automaton/compact.py`).

```text
DelayedInputDFA
  states, alphabet, initial, accepting, transitions, defaults, sink
  step(q, token) -> q | None     # δ^ν; sink and ⊥ → None
  accepts(TokenSequence) -> bool
  n_states_excluding_sink, n_transitions, n_defaults

CompactOptions
  o2_state_avoidance: bool = True
  o3_clean_copy: bool = True

lift_to_delayed(base: TokenDFA) -> DelayedInputDFA
apply_compact_merge(d2fa, rule, options) -> DelayedInputDFA
construct_compact_token_dfa(dictionary, base: TokenDFA, options=None) -> CompactResult

CompactResult
  final: DelayedInputDFA
  automata: tuple[DelayedInputDFA, ...]   # lifted A0 .. An
  steps: tuple[CompactStep, ...]
  options: CompactOptions

CompactStep
  rule_index, n_states, n_final, n_tokens, n_transitions, n_defaults, n_fresh
  # n_states excludes the sink

expand_defaults(d2fa) -> TokenDFA
languages_agree(baseline: TokenDFA, compact: DelayedInputDFA) -> bool
serialize_delayed_input_dfa(d2fa) -> str
```

Fresh state ids: next unused integers (including not reusing the sink id), created in **sorted \(S_2'\)** order. O3 reuse picks the **least** existing clean-copy id.

## Invariants

- \(\delta\) is a partial function on \(Q\cup\{q_s\}\); \(q_s\notin F\); \(\nu(q_s)=\bot\); no outgoing edges from \(q_s\).
- \(\nu\) is acyclic.
- `step` implements \(\delta^\nu\); an explicit edge wins; otherwise follow defaults on the **same** token.
- Missing edge and sink are both reject for `accepts`.
- Empty tokenization is accepted iff `initial ∈ accepting`.
- Triple set \(S\) uses **explicit** \(\delta(s_1,u)=s_2\in Q\) and **extended** \(\delta^\nu(s_2,v)=s_3\in Q\) (not \(q_s\)).
- O1: \(\nu(\mathrm{fresh}(s_2))=s_2\); \(\delta(\mathrm{fresh},v)=q_s\); also \(\delta(\mathrm{fresh},uv)=q_s\) iff \(u=v\).
- O2 off \(\Rightarrow S_2'=S_2\). O2 on \(\Rightarrow S_2'=\{s_2\in S_2\mid s_2=q_0\text{ or }s_2\text{ is multiple-use wrt }v\}\).
- O3 off \(\Rightarrow\) always allocate a new fresh state. O3 on \(\Rightarrow\) reuse a clean-copy when one exists.
- `construct_compact_token_dfa` requires a proper dictionary.
- Compact modules do not import the reference tokenizer.

## Error and edge behaviour

| Case | Behaviour |
|---|---|
| Improper \(D\) | `ImproperDictionaryError` |
| Empty \(D\) | lifted base (unused sink); language = baseline |
| \(S=\emptyset\) | language unchanged; \(uv\) still added to \(\Gamma\) |
| Conflicting \(\delta(s_1,uv)\) | `TokenDFAError` |
| Cyclic \(\nu\) | `TokenDFAError` at model construction / `step` |

## Testing and acceptance

Independent oracles: existing `construct_token_dfa` and `tokenize_reference` (tests only). Do not derive expected compact tables from `apply_compact_merge`.

- \(\delta^\nu\): explicit wins; default chain; sink rejects; cycle rejected.
- O1-only vs baseline: `accepts` agreement on Example 2 and unary; `expand_defaults(compact).n_states == baseline.n_states`.
- Exhaustive: all \(w\in\{a,b\}^{\le 6}\) on Example 2; compact vs baseline on canonical and non-canonical token sequences.
- Product emptiness on small \(\Gamma\).
- Hypothesis: random proper dictionaries, compact vs baseline `accepts`.
- O2/O3 flag combinations preserve language; O2/O3 on may reduce `n_states`.
- Fig. 2 structural facts after \(a⫽b\): default \(q_1\to q_0\); sink on \(b\) from the fresh state.
- Improper rejected; Unicode dictionary compact agrees with baseline on a declared bound.

## Risks

- Definition 3 (\(P_{q,u}\), multiple-use) is easy to get wrong; lock against PDF and Example 2 of [4].
- \(S\) must use \(\delta^\nu\) on \(v\), not only explicit \(\delta\).
- Equivalence is language via \(\delta^\nu\), never raw \(\delta\) tables.
- Def. 4 \(\Lambda\) vs Algorithm 2: recorded as D38.

## Open questions

None blocking. O4 remains explicitly deferred.

## Validation commands

```bash
cd 26455900-CS345
make check
uv run python experiments/compact_compare.py
```
