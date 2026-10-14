# Notes: Constructing a BPE Tokenization DFA

**Paper id:** `constructing-bpe-token-dfa-2026`  
**Catalogue:** [`../index.yaml`](../index.yaml)  
**Markdown:** see catalogue `markdown` field  
**PDF:** see catalogue `pdf` field (authoritative)

## Conversion verification

Current catalogue status is authoritative for agents. Update both this note and `conversion.status` / `conversion.known_issues` in `index.yaml` when verification work changes.

| Date | Sections checked against PDF | Resulting status | Notes |
|------|------------------------------|------------------|-------|
| 2026-07-26 | — | (catalogue initial) | Catalogue entry created; no section verification yet. |
| 2026-09-11 | Algorithm 2 (p. 4); Example 2; Remarks 2–3; Figs. 3–4 (p. 5); Defs. 1–2; Theorem 4 statement | `partially-verified` | Pseudocode matches Markdown. Fig. 3 transition structure confirmed from the PDF figure. |
| 2026-09-13 | Section 6 (pp. 10–12): Def. 6, Observation 3, Lemma 11, Fig. 8, Lemma 12, Thm. 13, Cor. 14 | `partially-verified` | Observation 3 and Fig. 8(a)–(b) match the Markdown. Fig. 8(b) emits a two-token word \(a \wr b\) on one edge. |

## Known conversion issues

Mirror important defects here for humans; keep the machine-readable list in `index.yaml`.

- See `conversion.known_issues` in the catalogue entry.

## Working notes

### Question

Does the Markdown conversion of Algorithm 2 and Example 2 match the PDF closely enough to implement?

### Sources consulted

- PDF: `research/sources/constructing-bpe-token-dfa.pdf` pages 3–6 (Algorithm 2, Example 2, Figs. 3–5, Lemma 1, Theorem 4).
- Markdown: `research/markdown/constructing-bpe-token-dfa/index.md`.

### Relevant sections

- Definition 1 (token DFA, partial \(\delta\)), Definition 2 (context-invariance).
- Algorithm 2, lines 1–22, page 4.
- Example 2 and Figs. 3–4, pages 4–5.
- Theorem 4: \(\mathcal{L}(A_i)=\mathbb{T}^{D_i}(\mathcal{L}(A))\).

### Source-derived findings

Algorithm 2 in the PDF is:

1. Collect \(S=\{(s_1,s_2,s_3)\mid \delta(s_1,u)=s_2,\ \delta(s_2,v)=s_3\}\).
2. Add \(\delta(s_1,uv)=s_3\) for each triple.
3. Add \(uv\) to \(\Gamma\).
4. Create `fresh(s2)` for each distinct \(s_2\in S_2\); copy accepting status.
5. If \(u\neq v\), copy outgoing \(\Gamma\setminus\{v\}\); if \(u=v\), copy \(\Gamma\setminus\{v,uv\}\).
6. Redirect every current \(\delta(q,u)\in S_2\) to `fresh(\(\delta(q,u)\))`, including edges just copied onto fresh states (Remark 3).

Fig. 3 (verified visually from the PDF):

- \(A_0\): one accepting state \(q_0\), self-loops \(a,b\).
- \(A_1\): \(q_0\xrightarrow{aa,b}q_0\), \(q_0\xrightarrow{a}q_1\), \(q_1\xrightarrow{b}q_0\); both accepting. No \(aa\) on \(q_1\).
- \(A_2\): \(q_0\xrightarrow{aa}q_0\), \(q_0\xrightarrow{b}q_2\), \(q_0\xrightarrow{a,ba}q_1\); \(q_2\xrightarrow{b}q_2\), \(q_2\xrightarrow{aa}q_0\), \(q_2\xrightarrow{ba}q_1\); \(q_1\xrightarrow{ba}q_1\), \(q_1\xrightarrow{b}q_2\).

No unary self-merge-chain figure appears in this PDF.

### Interpretation

Example 2 prose says \(q_2\) “gets all non-\(ba\) transitions from \(q_0\) on line 14”. That contradicts Algorithm 2 line 14 (\(\Gamma\setminus\{v\}=\Gamma\setminus\{a\}\), so \(ba\) **is** copied) and Fig. 3 / Fig. 4 (both show \(q_2\xrightarrow{ba}q_1\)). **Follow Algorithm 2 and the figures, not that sentence.**

Lemma 1’s proof says \(S=\emptyset\) yields unchanged \(A'=A\). Line 7 still adds \(uv\) to \(\Gamma\). Language is unchanged; the alphabet may grow. Implement line 7 as written.

### Implementation implications

- Do not trim (Remark 2; Lemma 7 counts untrimmed \(|S_2|\)).
- Fresh-state id order: sorted \(S_2\).
- Copy only defined outgoing transitions (partial \(\delta\)).
- Unary chain fixture is project-constructed, not a paper figure.

### Uncertainty

None blocking for Algorithm 2 itself. Locality (Section 5) remains unverified; not needed for §5.4.

### Decisions required

None remaining for 5.2 construction; locked in the Section 5.2 plan (reject improper; no trim; parameterized \(\Sigma\)).

---

## Working notes — Section 6 transducer (2026-09-13)

### Question

Does Observation 3 / Fig. 8 / Theorem 13 in the Markdown match the PDF closely enough to implement §5.4?

### Sources consulted

- PDF: `research/sources/constructing-bpe-token-dfa.pdf` pages 10–12 (Section 6, Fig. 8, Theorem 13, Corollary 14).
- Markdown: `research/markdown/constructing-bpe-token-dfa/index.md` from “6. Building a transducer”.

### Relevant sections

- Definition 6 (restricted real-time transducer), PDF p. 10.
- Observation 3, PDF p. 10.
- Lemma 11, Example 6, Definition 7 (bounded variation), PDF p. 10.
- Fig. 8(a)–(b), Lemma 12, Examples 7–9, PDF p. 11.
- Theorem 13, Corollary 14, PDF p. 12.

### Source-derived findings

Observation 3 (PDF p. 10) matches the Markdown:

1. Start with \(Q'=Q\).
2. For each DFA edge \(p \xrightarrow{u} q\) with \(u=\alpha_1\cdots\alpha_k\), add \(k-1\) intermediate states \(s_1,\ldots,s_{k-1}\) (\(s_0=p\)).
3. First \(k-1\) steps emit \(\varepsilon\); last step emits the token \(u\).
4. \(F'(q)=\varepsilon\) for DFA accepting states; undefined elsewhere. Intermediate states are neither initial nor accepting.

Fig. 8(a) applied to \(A_1\) of Fig. 3 (\(D=[a\wr a]\), \(\Sigma=\{a,b\}\)):

- \(q_0 \xrightarrow{a|\varepsilon} s_1 \xrightarrow{a|aa} q_0\)
- \(q_0 \xrightarrow{a|a} q_1\)
- \(q_0 \xrightarrow{b|b} q_0\)
- \(q_1 \xrightarrow{b|b} q_0\)
- \(q_0,q_1\) accepting with \(F=\varepsilon\); \(s_1\) not accepting.
- Input-nondeterminism: two \(a\)-edges out of \(q_0\).

Fig. 8(b) subsequential equivalent:

- \(q_0 \xrightarrow{a|\varepsilon} q_1 \xrightarrow{a|aa} q_0\)
- \(q_0 \xrightarrow{b|b} q_0\)
- \(q_1 \xrightarrow{b|a\wr b} q_0\) (two-token output on one edge)
- Both accepting; extra arrow \(F(q_1)=a\); \(F(q_0)=\varepsilon\).

Definition 6 allows only \(\Gamma\cup\{\varepsilon\}\) on edges. Fig. 8(b) and Béal–Carton use output *words*. Implement Observation 3 in the Definition 6 fragment; allow `TokenSequence` on subsequential edges to match Fig. 8(b).

Theorem 13: \(T^D\) has bounded variation, so Béal and Carton [12] = [3] in the course bibliography yields \(T'\) from Observation 3.

### Interpretation

Fig. 8(b) is the Béal–Carton result on Fig. 8(a), drawn with paper state names, not subset-pair labels. Tests should lock Fig. 8(a) transitions from Observation 3 and lock Fig. 8(b) **behaviour** plus \(F\) after one \(a\); raw subset ids may differ from the drawing.

### Implementation implications

- Do not trim Observation 3 spelling states.
- Public `tokenize` uses the subsequential machine only.
- Pending-output length cap: Béal–Carton Lemma 16 bound \(K=2n^2 M\).

### Uncertainty

None blocking for Observation 3 / Fig. 8 after PDF check.
