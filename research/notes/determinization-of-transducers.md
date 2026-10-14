# Notes: Determinization of transducers over finite and infinite words

**Paper id:** `determinization-of-transducers-2002`  
**Catalogue:** [`../index.yaml`](../index.yaml)  
**Markdown:** see catalogue `markdown` field  
**PDF:** see catalogue `pdf` field (authoritative)

## Conversion verification

Current catalogue status is authoritative for agents. Update both this note and `conversion.status` / `conversion.known_issues` in `index.yaml` when verification work changes.

| Date | Sections checked against PDF | Resulting status | Notes |
|------|------------------------------|------------------|-------|
| 2026-07-26 | — | (catalogue initial) | Catalogue entry created; no section verification yet. |
| 2026-09-13 | §2.2 Determinization of transducers over finite words (PDF pp. 233–234), including the subset-pair construction and final-output rule | `partially-verified` | Algorithm matches the repaired Markdown. Infinite-word half not verified. Ligature OCR remains in other sections. |

## Known conversion issues

Mirror important defects here for humans; keep the machine-readable list in the catalogue entry.

- Ligature OCR (`#nite`, `Cho2rut`, `i2`) elsewhere in the conversion; §2.2 was checked against the PDF.

## Working notes

### Question

What is the exact finite-word determinisation algorithm to apply to Observation 3 transducers?

### Sources consulted

- PDF: `research/sources/determinization-of-transducers.pdf` pages 231–235 (§2.1 twinning / Prop. 7; §2.2 algorithm; Lemmas 13, 16, 17).
- Markdown: `research/markdown/determinization-of-transducers/index.md`.

### Relevant sections

- Proposition 7 (Choffrut): subsequential iff bounded variation iff twinning (PDF p. 231).
- Section 2.2 algorithm (PDF p. 233).
- Final-output rule after Lemma 13 (PDF p. 234).
- Lemma 16: \(K = 2n^2 M\) (PDF p. 235).
- Lemma 17: delayed words in \(D\)-states are bounded, so \(D\) is finite.

### Source-derived findings

Real-time transducer \(T=(Q,E,I,F)\) labelled in \(A \times B^*\). States of \(D\) are sets of pairs \((q,w)\) with \(q\in Q\), \(w\in B^*\).

On letter \(a\) from state \(P\):

\[
R = \{(q', wu) \mid (q,w)\in P,\ q \xrightarrow{a|u} q' \in E\}.
\]

If \(R=\emptyset\), no transition. Else \(v = \mathrm{lcp}\{wu \mid (q',wu)\in R\}\) and

\[
P' = \{(q', w') \mid (q', vw')\in R\},
\]

with transition \(P \xrightarrow{a|v} P'\).

Initial state \(J = \{(i,\varepsilon) \mid i\in I\}\). Keep only the accessible part.

A state \(P\) is final if it contains at least one pair \((q,w)\) with \(q\) final in \(T\). Then \(\rho(P)=w\). Functionality implies that \(w\) is unique when several accepting pairs appear.

Lemma 16: twinning implies \(d(v,v') \le K\) with \(K=2n^2 M\), \(n=|Q|\), \(M=\) max output-label length of a transition. Lemma 17: \(|w|\le K\) for pairs in accessible \(D\)-states.

### Interpretation

Course §5.4 uses only this finite-word algorithm, not §3 (infinite words). Observation 3 transducers are real-time with \(B=\Gamma\) (tokens). Output words in \(D\) are token sequences.

Béal–Carton allow \(B^*\) on edges; [5] Definition 6 allows only \(\Gamma\cup\{\varepsilon\}\). Follow Béal–Carton / Fig. 8(b) for the subsequential machine.

### Implementation implications

- Emit a `TokenSequence` (possibly empty or length \(>1\)) on each subsequential edge.
- Cap pending-output length at \(2n^2 M\); exceeding it is an error, not truncation.
- If two accepting pairs in \(P\) have distinct \(w\), raise: \(T\) was not functional.

### Uncertainty

None blocking for §2.2 after PDF check. Infinite-word sections unused.

### Decisions required

None; locked as D24–D25, D30 in the §5.4 plan.
