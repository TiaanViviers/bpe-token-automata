# String-to-tokenization transducer (Section 5.4)

This note records the compiled tokenizer: Observation 3 of Berglund, Martens and van der Merwe [5] followed by Béal–Carton determinisation [3, §2.2]. The public API is `compile_tokenizer` / `tokenize`. It computes the same function \(T^D\) as `tokenize_reference`, on **token sequences**.

Symbols are UTF-8 bytes (D1). There is no pre-tokenization (D9).

## Pipeline

1. Build the token DFA \(A_n\) with Algorithm 2.
2. **Observation 3.** Each DFA edge labelled by a token \(u=\alpha_1\cdots\alpha_k\) becomes a \(k\)-step spelling: the first \(k-1\) bytes emit \(\varepsilon\); the last byte emits \(u\). DFA accepting states have \(F=\varepsilon\). Spelling states are not accepting.
3. **Béal–Carton §2.2.** States of the new machine are sets of pairs \((q,w)\) (old state, delayed token sequence). On an input byte, emit the longest common prefix of the possible outputs and keep the remainders. If a subset contains an accepting old state, \(F\) is that delayed remainder.
4. **`tokenize`.** One deterministic walk over the input bytes, then append \(F\).

The Observation 3 machine is a public intermediate (`from_token_dfa`). `tokenize` runs only on the subsequential machine.

## Fig. 8: \(D=[a⫽a]\) over \(\{a,b\}\)

Source: [5] Fig. 8, PDF p. 11, applied to \(A_1\) of Fig. 3.

### Observation 3 (Fig. 8(a))

From \(q_0\) the input \(a\) is nondeterministic: it may start the token \(aa\) (via \(s_1\)) or finish the leftover token \(a\) (to \(q_1\)).

```text
q0 --a|ε--> s1 --a|aa--> q0
q0 --a|a--> q1
q0 --b|b--> q0
q1 --b|b--> q0
```

\(q_0\) and \(q_1\) are accepting with \(F=\varepsilon\). \(s_1\) is not accepting.

### Subsequential (Fig. 8(b))

After one \(a\) the machine has not yet emitted; \(F=a\) (end of string, leftover odd \(a\)). A second \(a\) emits \(aa\). A following \(b\) emits \(a\) then \(b\) on **one** edge. That two-token output is required by the PDF figure and by Béal–Carton (output words in \(\Gamma^*\)). Observation 3 itself still emits at most one token per edge ([5] Definition 6).

```text
q0 --a|ε--> q1 --a|aa--> q0
q0 --b|b--> q0
q1 --b|a ⫽ b--> q0
F(q1)=a, F(q0)=ε
```

| input | tokens |
|---|---|
| `a` | `a` |
| `aa` | `aa` |
| `aaa` | `aa` `a` |
| `ab` | `a` `b` |
| `b` | `b` |

## Correctness

`tokenize` is checked against `tokenize_reference` (token-sequence equality, detokenization, DFA acceptance, rejection of split non-canonical boundaries). Exhaustive `{a,b}^{≤6}` on Example 2 includes the transducer. The transducer package does not import the reference tokenizer.

minbpe `BasicTokenizer` is compared via an attributed adapter that **injects** our merge list into the same byte-level encode loop (no `train()`, no GPT-2 regex). For proper dictionaries SentencePiece and HuggingFace-style merge selection coincide ([6] Lemma 1).

## Performance

See [`../experiments/results/transducer_tokenize.json`](../experiments/results/transducer_tokenize.json). Compile time is reported separately from tokenize time. Peak figures are `tracemalloc`, not RSS. After compilation a run is linear in \(|w|\) ([5] Corollary 14), but the compiled state space can be large; these fixtures are tiny. Practical pre-tokenization is **not** used, so timings are not comparable to GPT-2-style tokenizers.

## References

- Berglund, Martens and van der Merwe, *Constructing a BPE Tokenization DFA*, TCS 1083 (2026), §6
- Béal and Carton, *Determinization of transducers over finite and infinite words*, TCS 289 (2002), §2.2
- Karpathy, minbpe BasicTokenizer (MIT)
