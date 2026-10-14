# Notes: Constructing Compact BPE Token DFAs

**Paper id:** `constructing-compact-bpe-token-dfas-2025`  
**Catalogue:** [`../index.yaml`](../index.yaml)  
**Markdown:** see catalogue `markdown` field  
**PDF:** see catalogue `pdf` field (authoritative)

## Conversion verification

Current catalogue status is authoritative for agents. Update both this note and `conversion.status` / `conversion.known_issues` in `index.yaml` when verification work changes.

| Date | Sections checked against PDF | Resulting status | Notes |
|------|------------------------------|------------------|-------|
| 2026-07-26 | — | (catalogue initial) | Catalogue entry created; no section verification yet. |
| 2026-09-13 | Def. 2, Observation 1, Def. 3–4, Algorithm 2, Lemma 1 statement, Examples 1–3 | `partially-verified` | Algorithm 2 and Def. 2–4 checked from PDF pp. 3–5. O4 / §5 not used this milestone. |

## Known conversion issues

Mirror important defects here for humans; keep the machine-readable list in `catalogue` `conversion.known_issues`.

- Marker mixes the “O4, see Section 5” annotation into Algorithm 2 line 4.
- Definition 4’s \(\Lambda=\{u\}\) when \(u\neq v\) does not match Algorithm 2 lines 16–18 or Fig. 2 (sink is on \(v\)). Implement the algorithm.
- Algorithm 2 line 9 typesets `or q = q0`; Example 1 shows this means \(s_2=q_0\).

## Working notes

### Question

What does Algorithm 2 construct, and which optimisations are O1–O4?

### Sources consulted

- PDF `research/sources/constructing-compact-bpe-token-dfas.pdf` pp. 3–7 (pdftotext `-layout`, 2026-09-13).
- Markdown conversion used only for navigation.

### Relevant sections

- Definition 2, \(\delta^\nu\), Observation 1 (p. 3).
- Definitions 3–4 (p. 4).
- Algorithm 2 (p. 5).
- Lemma 1 / Corollary 1 / Lemma 2 / Theorem 1 (pp. 5–7).

### Source-derived findings

- A D²FA is \((Q,\Gamma,q_0,\delta,\nu,F)\) with acyclic partial \(\nu\). \(\delta^\nu\) takes the explicit edge if present, else recurses on \(\nu(q)\) with the **same** token.
- Observation 1: the DFA with transition function \(\delta^\nu\) has the same language.
- Distinguished sink \(q_s\notin F\), \(\nu(q_s)=\bot\). The prose also says \(\delta(q_s,u)=q_s\) for all \(u\); Algorithm 2 starts with an **unused** sink (no incoming from \(Q\)).
- Algorithm 2 \(S\): \(\delta(s_1,u)=s_2\) explicit, \(\delta^\nu(s_2,v)=s_3\). Blue lines = O2, red = O3.
- O1: \(\nu(\mathrm{fresh}(s_2))=s_2\); sink on \(v\); sink on \(uv\) iff \(u=v\).
- Def. 3: \(P_{q,u}\) is \(q\) plus states that default into that set with no explicit \(u\)-edge. \(S_{q,u}\) is incoming explicit labels to \(P_{q,u}\). Multiple-use iff \(|S_{q,u}|>1\).
- Def. 4 as typeset: \(\Lambda=\{u,uv\}\) if \(u=v\) else \(\{u\}\). Fig. 2 A1 after \(a⫽b\) has the fresh state’s sink on \(b=v\), not on \(a=u\).

### Interpretation

- Line 9 “or \(q=q_0\)” = \(s_2=q_0\) is never O2-eligible (Example 1: start state disables O2).
- Clean-copy \(\Lambda\) for implementation = the O1 sink labels \(\{v\}\) or \(\{v,uv\}\), not Def. 4’s \(u\neq v\) branch.
- Represent \(q_s\) without \(|\Gamma|\) self-loops; `step` maps sink and \(\bot\) to reject. Language-equivalent to a complete self-loop sink.

### Implementation implications

- Do not copy baseline triple-finding (`δ` on both \(u\) and \(v\)).
- Lemma 1 check: O1-only, expand defaults, drop sink; non-sink state count equals baseline.
- O4 ignored.

### Uncertainty

None blocking for O1–O3. Section 5 / O4 unread in detail.

### Decisions required

Recorded in the 5.5 plan as D33–D42.
