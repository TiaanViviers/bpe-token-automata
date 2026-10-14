# Canonical and original token-DFA examples (Section 5.3)

Engineering specification for reproducing paper examples, recording merge traces, and documenting original Unicode/emoji worked examples.

## Goal

Satisfy course spec §5.3: reproduce the principal small examples from Berglund, Martens and van der Merwe [5], explain each merge (triples, fresh states, redirects, tokenizations), add at least three original worked examples (including non-ASCII and emoji/multi-byte Unicode), and state the symbol model.

The Algorithm 2 constructor already exists (Section 5.2). This milestone adds merge-step traces, fixtures, independent tests, and assessable documentation.

## Background

- **Course requirement:** spec §5.3 (reproduction, per-merge explanation, original examples, symbol-model statement). Spec §6.1 Unicode/emoji token-identity tests. Spec §9.1 PDF report is a later submission artefact; this milestone writes the 5.3 chapter as Markdown under `26455900-CS345/docs/`.
- **Research:** [5] Algorithm 2 (PDF p. 4), Example 2, Figs. 3–4 (PDF p. 5), Remarks 2–3. No unary self-merge figure appears in [5]; the unary chain is a project fixture.
- **Locked decisions:** D1 UTF-8 bytes; D22 follow Algorithm 2 and Figs. 3–4, not Example 2’s “non-ba” sentence.

ASSUMPTIONS (locked with the Section 5.3 plan):

1. Do not change D1. Base symbols remain length-1 UTF-8 bytes.
2. Do not start the §9.1 PDF/LaTeX report, transducer, compact automaton, or timeout experiments.
3. Paper Examples 3–5 (non-context-invariant / improper) are not canonical reproductions.
4. Universal-language tokenization tables use a stated finite bound; tests use length ≤ 4, the write-up may show a representative subset.
5. Automaton production code still must not import `tokenize_reference`.

## Scope

- `MergeTrace` returned by `apply_merge` and stored on `ConstructionResult`.
- Byte-safe token-sequence formatting (`format_token_label` / `format_token_sequence`).
- Tests locking Example 2 and unary triples against paper text / hand-applied Algorithm 2.
- Three original fixtures: restricted finite language; precomposed `é` as two bytes; emoji 😀 as four bytes.
- Unicode/emoji token-identity tests, including NFC vs NFD.
- Assessable write-up `26455900-CS345/docs/token-dfa-examples.md`.

## Non-goals

Rewriting Algorithm 2, trimming, CLI, rendering PNG/SVG in CI, changing the alphabet to code points or grapheme clusters, full technical-report PDF.

## Authoritative sources

| Source | What it governs |
|---|---|
| Course spec §5.3, §6.1 Unicode/emoji | Requirements |
| [5] PDF Algorithm 2 p. 4; Example 2; Figs. 3–4 p. 5 | Paper examples and merge steps |
| D1, D22 | Bytes; ignore “non-ba” prose |
| Section 5.2 implementation | Constructor, serialisation, Graphviz |

## Interfaces

```text
format_token_label(token) -> str     # printable ASCII or \xHH; lives in tokens.py
format_token_sequence(seq) -> str    # joins labels with ⫽; must not UTF-8-decode

MergeTrace
  rule: MergeRule
  before: TokenDFA
  after: TokenDFA
  triples: ((s1, s2, s3), ...)                 # line 2, s1 order
  s2_to_fresh: ((s2, fresh_id), ...)           # sorted S2
  added_uv: ((s1, uv, s3), ...)
  inherited: ((fresh, α, target), ...)         # copies from lines 12–18, before redirect
  omitted_labels: frozenset[Token]             # {v} or {v, uv}
  redirected: ((q, u, old_s2, fresh), ...)     # line 19, including fresh states
  n_fresh -> |S2|

apply_merge(dfa, rule) -> (TokenDFA, MergeTrace)

ConstructionResult
  final, automata, steps
  traces: tuple[MergeTrace, ...]               # one per rule
```

`inherited` records the Algorithm 2 copy *before* line 19. A copied `u`-edge that Remark 3 then loops on the fresh state appears in both `inherited` (old target) and `redirected`.

## Original examples

Diagrams use only the relevant length-1 bytes as \(\Sigma\), not `byte_alphabet()`. Merge files use `\xHH` for non-ASCII bytes.

1. **Restricted \(L=\{ab\}\).** Existing YAML `data/automata/finite_ab.yaml` with `D=[a⫽b]`. Shows Algorithm 2 on a non-universal, non-accepting intermediate state.
2. **Non-ASCII `é`.** U+00E9 is UTF-8 `C3 A9`. `D=[\xc3 ⫽ \xa9]` over \(\{\mathtt{C3},\mathtt{A9}\}\).
3. **Emoji 😀.** U+1F600 is UTF-8 `F0 9F 98 80`. Proper chain `\xf0 ⫽ \x9f`, `\xf0\x9f ⫽ \x98`, `\xf0\x9f\x98 ⫽ \x80`.

NFC `é` (`C3 A9`) vs NFD `e` + U+0301 (`65 CC 81`) must be shown: same grapheme, different bytes, different tokenizations.

A merges line `é é` would encode two length-2 tokens and must not be used as a base-alphabet example.

## Invariants

- Expected Example 2 triples come from the paper: \(A_0\to A_1\) has \(S=\{(q_0,q_0,q_0)\}\); \(A_1\to A_2\) has \(S=\{(q_0,q_0,q_1),(q_1,q_0,q_1)\}\).
- Unary expected traces come from hand-applied Algorithm 2, not from reading `apply_merge` back into the test.
- Token identity is byte equality. The parser must not NFC-normalise.
- `format_token_sequence` remains defined on incomplete UTF-8 tokens.

## Testing and acceptance

- Example 2 / unary: traces and Fig. 3 / hand-applied edges.
- Each original example: hand-expected triples/edges; `tokenize_reference` agreement on a stated bound.
- Prefix dictionaries \(D_i\): \(A_i\) accepts \(\mathbb{T}^{D_i}(w)\) and rejects the pre-merge sequence when it is no longer canonical.
- Parser: `\xc3 \xa9` (two length-1 tokens) vs a UTF-8 `é` literal (one length-2 token).
- NFC vs NFD strings are distinct inputs.

## Documentation

Assessable path: `26455900-CS345/docs/token-dfa-examples.md`, linked from the README.

Must include: D1 restatement; Example 2 with Fig. 4-style intermediates and D22; unary chain; three original examples; per-merge triples, fresh states, redirects, bounded tokenization tables; how to regenerate DOT via `to_dot`.

## Validation commands

```bash
cd 26455900-CS345
make check
```

## Open questions

None blocking.
