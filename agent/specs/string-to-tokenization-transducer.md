# String-to-tokenization transducer (Section 5.4)

Engineering specification for compiling a token DFA into a subsequential tokenizer.

## Goal

Given a proper dictionary \(D\) and a token DFA \(A\) with \(\mathcal{L}(A)=\mathbb{T}^D(L)\), construct a subsequential transducer \(T'\) that maps each string \(w\in L\) to the canonical token sequence \(\mathbb{T}^D(w)\). The public tokenizer must agree with `tokenize_reference` on token sequences, not only on detokenized text.

## Background

- **Course requirement:** spec §5.4, §4.3 (input transitions, emitted output, final output), §6.2–6.4, §7.1/7.3 questions 5–6.
- **Research:** [5] Section 6 (PDF pp. 10–12): Definition 6, Observation 3, Lemma 11, Fig. 8, Theorem 13. [3] §2.2 (PDF pp. 233–234) finite-word determinisation.
- **Locked project decisions:** D1 bytes; D2 SentencePiece \(T^D\); D9 no pre-tokenization; D13 parameterized \(\Sigma\); D15 reject improper dictionaries.

ASSUMPTIONS (locked with the §5.4 plan):

1. Observation 3 is a public intermediate; `tokenize` runs only on the subsequential machine.
2. Transducer modules do not import `tokenize_reference`.
3. No CLI. No trimming of Observation 3 spelling states.
4. Subsequential edges may emit a `TokenSequence` of length \(\ge 1\) (Fig. 8(b) \(b|a\wr b\)); Observation 3 emits \(\varepsilon\) or one token.
5. minbpe comparison and thin performance measurements are in-scope as later tickets, not the core constructor.

## Scope

- Frozen transducer models with separate transitions and final output.
- `from_token_dfa` = Observation 3.
- `subsequentialise` = Béal–Carton §2.2.
- `compile_tokenizer` / `tokenize`.
- Deterministic serialisation and optional Graphviz.
- Tests: Fig. 8, §6.2 differential, exhaustive, Hypothesis, Unicode, negatives; then minbpe and a small experiment.

## Non-goals

Compact automaton (§5.5), large-dictionary timeouts (§5.6), streaming/incremental extensions, CLI, pre-tokenization, using the Observation 3 NFA as the shipped tokenizer.

## Authoritative sources

| Source | What it governs |
|---|---|
| Course spec §5.4, §4.3, §6.2–6.4 | Requirements, tests, performance |
| [5] PDF Observation 3 p. 10; Fig. 8 p. 11; Thm. 13 p. 12 | Construction and Fig. 8 lock |
| [3] PDF §2.2 pp. 233–234; Lemma 16 p. 235 | Determinisation and pending-output bound |
| Human-approved 5.4 plan D23–D32 | Local engineering locks |

## Interfaces

Package: `bpe_token_automata.transducer`.

```text
Transducer
  states, input_alphabet, output_alphabet, initial
  final_output: state -> TokenSequence     # domain = accepting
  transitions: (src, input_byte, output, dst)*   # output may be empty
  successors(state, input) -> ((output, dst), ...)
  is_subsequential() -> bool

SubsequentialTransducer
  same fields; at most one successor per (state, input)
  step(state, input) -> (output, dest) | None
  final_of(state) -> TokenSequence | None

from_token_dfa(dfa) -> Transducer
subsequentialise(transducer) -> SubsequentialTransducer
compile_tokenizer(dictionary, base) -> SubsequentialTransducer
tokenize(machine, text: bytes) -> TokenSequence

serialize_transducer(...) -> str
to_dot(...) -> str
```

Observation 3 intermediate ids: next unused integers after `max(dfa.states)`, created in **sorted DFA-transition order**, then left-to-right along the spelling.

Béal–Carton subset ids: BFS from \(J=\{(q_0,\varepsilon)\}\), exploring **sorted input bytes**.

## Invariants

- Observation 3: \(\mathcal{L}(T)=\{(\pi(\varphi),\varphi)\mid \varphi\in\mathcal{L}(A)\}\).
- Intermediate spelling states are not accepting.
- Subsequential: \(\lvert\{(v,q)\mid p \xrightarrow{a|v} q\}\rvert \le 1\).
- `tokenize` on \(T'\) equals \(T^D(w)\) for \(w\) in the domain of \(A\).
- Concatenating output tokens yields \(w\).
- Transducer modules do not import the reference tokenizer.

## Error and edge behaviour

| Case | Behaviour |
|---|---|
| Improper \(D\) | `ImproperDictionaryError` from `construct_token_dfa` |
| Empty \(D\) | identity byte-to-token transducer (already subsequential) |
| Missing transition / non-accepting end | `TokenizationError` |
| Pending output longer than \(2n^2 M\) | `TransducerError` (never truncate) |
| Two accepting pairs with distinct delayed \(w\) | `TransducerError` (not functional) |
| Empty input | \(F(q_0)\) if \(q_0\) accepting, else `TokenizationError` |

## Testing and acceptance

Independent oracles: hand-coded Fig. 8(a) from the PDF; `tokenize_reference` for strings; token DFA acceptance as a third check. Do not take Observation 3 search as the ground truth for the subsequential machine.

- Fig. 8(a) transitions on \(A_1\) for \(D=[a⫽a]\).
- Fig. 8(b) behaviour: one \(a\) delays output; \(F=a\); `aa` emits `aa`; `ab` emits `a` then `b`.
- §6.2 on Example 2, unary chain, Unicode/emoji fixtures.
- Exhaustive \(\{a,b\}^{\le 6}\) (existing bound) including the transducer.
- Hypothesis: random proper dictionaries (rules from existing tokens) and strings.

## Risks

- Subsequential state space can explode; tests use small \(\Sigma\).
- minbpe may not expose merge loading.
- Definition 6 vs Fig. 8(b) multi-token outputs: follow the figure for \(T'\).

## Open questions

None blocking after the 2026-09-13 PDF check.

## Validation commands

```bash
cd 26455900-CS345
make check
```
