# Section 5.2 — Baseline BPE tokenization DFA

Planning document for the successive-merge token-DFA construction.

## Metadata

| Field | Value |
|---|---|
| **Status** | `approved` — blocking decisions D13–D22 locked 2026-09-11 |
| **Spec section** | Course spec §5.2 |
| **Primary sources** | Berglund, Martens, van der Merwe [5] Algorithm 2, Example 2, Figs. 3–4, Theorem 4 |
| **Engineering spec** | [`../specs/baseline-token-automaton.md`](../specs/baseline-token-automaton.md) |
| **PDF check** | [`../../research/notes/constructing-bpe-token-dfa.md`](../../research/notes/constructing-bpe-token-dfa.md) 2026-09-11 |
| **Tickets** | TICKET-002 constructor; TICKET-003 outputs; TICKET-004 tests |

## What Section 5.2 requires

Produce \(A_0,\ldots,A_n\) by applying Algorithm 2 in dictionary order. Support the universal one-state base DFA and user-supplied string DFAs. Handle \(u=v\) explicitly. Record counts after each rule. Provide deterministic text and optional Graphviz.

## Formal procedure (PDF p. 4)

See the engineering spec. Order: triples → add \(uv\) transitions → add \(uv\) to \(\Gamma\) → create fresh states → inherit outgoing (skip \(v\); also skip \(uv\) iff \(u=v\)) → redirect all current \(u\)-edges into \(S_2\), including edges on fresh states (Remark 3).

**Paper slip:** Example 2 says \(q_2\) inherits “non-\(ba\)” transitions. Algorithm 2 line 14 and Figs. 3–4 copy \(ba\). Implement the algorithm.

## Decision register

| # | Decision | Blocking? | Status | Decision | Rationale |
|---|---|---|---|---|---|
| D13 | Universal alphabet | yes | `decided` | Parameterized \(\Sigma\); D5 full-byte is \(\Sigma=\{0..255\}\) | Paper figures use \(\{a,b\}\) |
| D14 | Trimming | yes | `decided` | **No trim** | Lemma 7 / Remark 2; honest counts |
| D15 | Improper \(D\) | yes | `decided` | Reject (`ImproperDictionaryError`) | Matches 5.1 tokenizer; Theorem 4 assumes proper |
| D16 | Representation | yes | `decided` | Frozen `TokenDFA`; int states; partial \(\delta\) | Spec §4.3 |
| D17 | Fresh ids | yes | `decided` | Next ints, **sorted \(S_2\)** | Deterministic serialisation |
| D18 | User base DFA | yes | `decided` | Python constructor + YAML fixture | Same pattern as dictionary YAML |
| D19 | CLI | no | `decided` | **Defer** | Same as D11 |
| D20 | Text serialisation | no | `decided` | Sorted states/transitions; printable ASCII or `\xHH` | Automated tests |
| D21 | Empty \(S\) | yes | `decided` | Language unchanged; still add \(uv\) to \(\Gamma\) | Algorithm 2 line 7 |
| D22 | Example 2 prose | yes | `decided` | Follow Algorithm 2 + Figs. 3–4, not “non-ba” | PDF figure and line 14 win |

## Tickets

1. TICKET-002 — `TokenDFA`, bases, `apply_merge`, `construct_token_dfa`
2. TICKET-003 — construction stats, `serialize_token_dfa`, `to_dot`
3. TICKET-004 — Example 2, unary chain, §6.1, bounded oracle tests

Human review after TICKET-004 / `make check`.

## Non-goals

5.4 transducer, 5.5 compact automaton, 5.6 experiments, 5.3 report, Unicode/emoji original examples, trimming, CLI.
