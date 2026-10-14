# Section 5.4 — String-to-tokenization transducer

Planning document for compiling the token DFA into a subsequential tokenizer.

## Metadata

- **Status:** `approved` — D23–D32 locked with the implementation plan (2026-09-13); PDF check recorded the same day
- **Spec section:** Course spec §5.4
- **Primary sources:** [5] Section 6, Fig. 8; [3] §2.2
- **Engineering spec:** [`../specs/string-to-tokenization-transducer.md`](../specs/string-to-tokenization-transducer.md)
- **PDF check:** [`../../research/notes/constructing-bpe-token-dfa.md`](../../research/notes/constructing-bpe-token-dfa.md) and [`../../research/notes/determinization-of-transducers.md`](../../research/notes/determinization-of-transducers.md)
- **Tickets:** TICKET-008 Observation 3; TICKET-009 determinise; TICKET-010 tokenize/tests; TICKET-011 minbpe; TICKET-012 performance/docs

## Formal procedure

1. Build \(A_n\) with existing `construct_token_dfa`.
2. Observation 3: spell each token-edge into input bytes; emit the token on the last byte.
3. Béal–Carton §2.2: subset of \((q,w)\) pairs, emit LCP, keep remainders, \(F\) = delayed word of an accepting pair.
4. `tokenize`: one deterministic walk, append \(F\) at the end.

Fig. 8(b) confirms multi-token output on a single subsequential edge (`b|a ⫽ b`).

## Decision register

- **D23** Observation 3 exactly, including \(F=\varepsilon\) on DFA accepting states
- **D24** Béal–Carton §2.2 only (finite words)
- **D25** Transition output is `TokenSequence` (empty = \(\varepsilon\))
- **D26** No `tokenize_reference` import in transducer modules
- **D27** `TokenizationError` off-domain
- **D28** Improper \(D\) rejected by DFA constructor
- **D29** No CLI; no trim; deterministic ids
- **D30** Hard cap \(2n^2 M\) on pending output; error not truncate
- **D31** minbpe later ticket, byte-level only
- **D32** Thin performance experiment, not §5.6

## Tickets

1. TICKET-008 — model, Observation 3, serialise, DOT, Fig. 8(a)
2. TICKET-009 — subsequentialise, Fig. 8(b)
3. TICKET-010 — compile/tokenize, §6.2–6.4
4. TICKET-011 — minbpe
5. TICKET-012 — experiments and docs

Human review after TICKET-008, TICKET-010, and TICKET-012.

## Non-goals

§5.5 compact automaton, §5.6 timeouts, streaming extensions, CLI, pre-tokenization.
