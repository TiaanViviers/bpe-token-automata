# Baseline token automaton (Section 5.2)

Engineering specification for the successive-merge token-DFA construction.

## Goal

Implement Algorithm 2 of Berglund, Martens and van der Merwe [5] so that, given a proper dictionary \(D\) and a string DFA for a regular language \(L\), the constructor produces \(A_0, A_1, \ldots, A_n\) with \(\mathcal{L}(A_i)=\mathbb{T}^{D_i}(L)\) (Theorem 4). \(A_n\) accepts exactly the canonical tokenizations of \(L\) under \(D\).

This is the marked baseline construction. The Section 5.1 reference tokenizer is an independent oracle, not part of this module.

## Background

- **Course requirement:** spec §5.2 (construction, universal and user-supplied bases, \(u=v\) special case, per-rule counts, textual serialisation, optional Graphviz). Spec §6.1–6.3 unit and bounded checks that do not need the transducer. Spec §4.3: states, accepting states, partial transitions as distinct types.
- **Research:** [5] Definitions 1–2, Algorithm 2 (PDF p. 4), Remarks 2–3, Example 2 / Figs. 3–4 (PDF p. 5), Theorem 4.
- **Project decisions already locked:** UTF-8 bytes as tokens (D1/D5); SentencePiece \(T^D\) (D2); reject improper dictionaries (D6, confirmed for 5.2); self-merge allowed (D4).

ASSUMPTIONS (locked 2026-09-11 with the human):

1. Improper dictionaries raise `ImproperDictionaryError`; paper Example 5 is out of scope.
2. Do not trim useless states.
3. Universal \(A_0\) is parameterized by \(\Sigma\); paper fixtures use \(\{a,b\}\) or \(\{a\}\); the D5 full-byte automaton is the same constructor with \(\Sigma=\{0,\ldots,255\}\).
4. No CLI in this milestone.
5. Automaton code must not import `tokenize_reference`.
6. Follow Algorithm 2 and Figs. 3–4, not Example 2’s “non-ba” sentence (PDF prose error).

## Scope

- `TokenDFA` model (partial \(\delta\)).
- `universal_token_dfa(alphabet)` and user-supplied string DFAs (Python + YAML).
- `apply_merge` = Algorithm 2; `construct_token_dfa` applies rules in dictionary order.
- Per-rule machine-readable counts; deterministic text; optional Graphviz.
- Tests: §6.1 units, paper Example 2, a unary self-merge chain, bounded oracle agreement.

## Non-goals

Transducer (5.4), compact automaton (5.5), large-dictionary timeouts (5.6), 5.3 report prose, original Unicode/emoji examples, trimming, CLI, third-party automata libraries.

## Authoritative sources

| Source | What it governs |
|---|---|
| Course spec §5.2, §4.3, §6.1–6.3 | Requirements, outputs, tests |
| [5] PDF Algorithm 2 p. 4; Figs. 3–4 p. 5; Theorem 4 | Construction |
| [6] Definition 5; 5.1 validator | Properness gate |
| Human-approved 5.2 plan | Improper/trim/alphabet/CLI |

## Interfaces

Package: `bpe_token_automata.automaton`.

```text
TokenDFA
  states: frozenset[int]
  alphabet: frozenset[Token]      # tokens, not just base symbols
  initial: int
  accepting: frozenset[int]
  delta: (q, Token) -> q          # partial
  step(q, token) -> q | None
  accepts(TokenSequence) -> bool

universal_token_dfa(alphabet) -> TokenDFA
from_string_dfa(...) -> TokenDFA
parse_string_dfa_yaml(text) -> TokenDFA

apply_merge(dfa, rule) -> (TokenDFA, n_fresh)
construct_token_dfa(dictionary, base) -> ConstructionResult

ConstructionResult
  final: TokenDFA                 # A_n
  automata: tuple[TokenDFA, ...]  # A_0 .. A_n
  steps: tuple[ConstructionStep, ...]  # one per rule

ConstructionStep
  rule_index, n_states, n_final, n_tokens, n_transitions, n_fresh

serialize_token_dfa(dfa) -> str
to_dot(dfa) -> str
```

Fresh state ids: next unused integers, created in **sorted \(S_2\)** order.

YAML string DFA:

```yaml
states: [0, 1, 2]
initial: 0
accepting: [2]
transitions:
  - from: 0
    symbol: a
    to: 1
```

Symbols use the same token literals as dictionaries (UTF-8 / `\xHH`). They must decode to length-1 tokens.

## Invariants

- \(\delta\) is a partial function: at most one target per \((q,\alpha)\).
- Missing transition = reject.
- Empty tokenization is accepted iff `initial ∈ accepting`.
- After `apply_merge(u,v)` there is no remaining run \(s_1\xrightarrow{u}s_2\xrightarrow{v}s_3\) (those were replaced by \(uv\)).
- If \(u=v\), a fresh state has no outgoing \(v\) and no outgoing \(uv\).
- If \(u\neq v\), a fresh state has no outgoing \(v\); it may have outgoing \(uv\).
- Fresh states are accepting iff the \(s_2\) they copy is accepting.
- `construct_token_dfa` requires a proper dictionary.
- Automaton modules do not import the reference tokenizer.

## Error and edge behaviour

| Case | Behaviour |
|---|---|
| Improper \(D\) | `ImproperDictionaryError` |
| Empty \(D\) | \(A_n=A_0\) |
| \(S=\emptyset\) | language unchanged; \(uv\) still added to \(\Gamma\) (Algorithm 2 line 7) |
| Conflicting \(\delta(s_1,uv)\) | raise `TokenDFAError` (should not occur on context-invariant inputs) |
| Base alphabet token of length ≠ 1 | raise `TokenDFAError` |
| Useless but proper rule | construct; language may be unchanged |

## Testing and acceptance

Independent oracles: hand-written Fig. 3 transitions; `tokenize_reference` for bounded strings. Do not generate expected graphs from `apply_merge`.

- Empty dictionary; no-op/useless rule; fresh-state copy/omit/accept; \(u=v\); \(u\neq v\); loops and multiple predecessors; final vs non-final \(s_2\); improper rejection.
- Example 2: \(D=[a⫽a,b⫽a]\) over \(\{a,b\}\), match Fig. 3 after each merge.
- Unary: \(D=[a⫽a, aa⫽a]\) over \(\{a\}\); record triples conceptually via resulting automata (paper has no unary figure).
- Exhaustive: all \(w\in\{a,b\}^{\le 6}\); canonical token sequence accepted; base tokenization rejected when it differs from canonical.

## Risks

- Line 19 must include freshly copied \(u\)-edges (Remark 3). Easy to get wrong.
- Example 2 prose vs algorithm: implement the algorithm.
- Full-byte universal DFA is large to serialise; tests use small \(\Sigma\).
- Untrimmed growth is exponential in the worst case; this milestone uses tiny dictionaries only.

## Open questions

None blocking. Unary fixture is project-constructed because [5] has no unary figure.

## Validation commands

```bash
cd 26455900-CS345
make check
```
