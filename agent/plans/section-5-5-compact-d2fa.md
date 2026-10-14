# Section 5.5 — Compact delayed-input token automaton

Planning document for the compact D²FA construction.

## Metadata

| Field | Value |
|---|---|
| **Status** | `approved` — blocking decisions D33–D42 locked 2026-09-13 |
| **Spec section** | Course spec §5.5 |
| **Primary sources** | Berglund, Jonsson, Martens, van der Merwe [4] Algorithm 2, Definitions 2–4, Observation 1, Lemma 1 |
| **Engineering spec** | [`../specs/compact-delayed-input-automaton.md`](../specs/compact-delayed-input-automaton.md) |
| **PDF check** | [`../../research/notes/constructing-compact-bpe-token-dfas.md`](../../research/notes/constructing-compact-bpe-token-dfas.md) 2026-09-13 |
| **Tickets** | TICKET-013 O1 model+constructor; TICKET-014 O2/O3, equivalence, comparison, docs |

## What Section 5.5 requires

Implement the compact construction of [4]. Support default transitions and state which optimisations are enabled. Minimum: O1 and sink/reject handling. O2 and O3 strongly recommended (in scope here as flags). Equivalence with the baseline via \(\delta^\nu\), not transition tables. Report baseline/compact sizes, default-transition count, construction time, and peak memory on dictionary prefixes.

## Formal procedure (PDF p. 5)

See the engineering spec. Algorithm 2 on a D²FA with distinguished unused sink. \(S\) uses explicit \(\delta(s_1,u)\) and extended \(\delta^\nu(s_2,v)\). O1 replaces inherited copies with \(\nu(\mathrm{fresh})=s_2\) plus sink edges. Blue lines are O2; red lines are O3. O4 on line 4 is ignored (deferred).

**Paper slip:** Definition 4 sets \(\Lambda=\{u\}\) when \(u\neq v\). Algorithm 2 lines 16–18 and Fig. 2 put the sink edge on \(v\). Implement the algorithm and figure (D38).

**Paper slip:** Algorithm 2 line 9 “or \(q=q_0\)” means \(s_2=q_0\) (Example 1).

## Decision register

| # | Decision | Blocking? | Status | Decision | Rationale |
|---|---|---|---|---|---|
| D33 | O1 | yes | `decided` | Always on | Course §5.5 minimum |
| D34 | O2 / O3 | yes | `decided` | Flags, default True; tests also cover False | Completeness/performance; Lemma 1 uses \(2^X\) |
| D35 | O4 | yes | `decided` | **Out of scope** | Human 2026-09-13; extension 8.5 territory |
| D36 | Sink | yes | `decided` | Compact model only; unused at lift; no `TokenDFA` sink | Baseline missing = reject (D16) |
| D37 | Module | yes | `decided` | `automaton/compact.py`; do not extend `TokenDFA` | Spec §4.3 |
| D38 | Def. 4 \(\Lambda\) | yes | `decided` | Sink labels = O1’s \(\{v\}\) / \(\{v,uv\}\) | Fig. 2 and lines 16–18 win |
| D39 | Line 9 initial | yes | `decided` | \(s_2=q_0\) ineligible for O2 | PDF Example 1 |
| D40 | CLI / Graphviz / traces | no | `decided` | **None** | Light milestone |
| D41 | Fresh ids | yes | `decided` | Next ints, sorted \(S_2'\); O3 reuse = least id | Matches D17 |
| D42 | Sink self-loops | yes | `decided` | Omit \(\delta(q_s,u)=q_s\); dead reject state | Same language; honest explicit counts |
| D43 | Line 3 overwrite | yes | `decided` | Do not sink over a live \(\delta^\nu(q,uv)\) | Lemma 3 unique-`uv` vs proper useless rules |

## Tickets

1. TICKET-013 — `DelayedInputDFA`, lift, O1-only merge, serialise, `expand_defaults`, O1 vs baseline tests
2. TICKET-014 — O2/O3, product equivalence, Hypothesis, comparison experiment, docs

Human review after TICKET-013 / `make check` before treating O2/O3 as settled. (Implementation of 014 may follow in the same session when authorised.)

## Non-goals

O4, 5.6, trimming, CLI, Graphviz, `TokenDFA` changes, 8.2/8.11, compact-in-transducer.
