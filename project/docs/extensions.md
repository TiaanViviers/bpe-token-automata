# Approved extensions

This repository implements three extensions from Section 8 of the project
specification: 8.2, 8.6, and 8.11.

The bounded-equivalence and canonical-tokenization definitions follow
Berglund and van der Merwe, "Formalizing BPE Tokenization", EPTCS 388 (2023);
Berglund, Martens and van der Merwe, "Constructing a BPE Tokenization DFA",
TCS 1083 (2026); and Aho and Corasick, "Efficient String Matching: An Aid to
Bibliographic Search", Communications of the ACM 18(6), 1975. Section 8.6
uses the same proper-dictionary check (Definition 5 of the 2023 paper) and
the same Algorithm 2 construction as the rest of the project.

## 8.2 Dictionary equivalence

`compare_dictionaries_bounded` compares two proper ordered dictionaries on an
explicit, deduplicated tuple of byte strings. It records the first input on
which the independent reference tokenizer produces different token sequences.
With `check_token_dfa=True`, it also constructs both token DFAs over the finite
byte alphabet observed in the inputs and rule components and checks their token
languages using product exploration. When the DFAs disagree, `dfa_witness` is a
shortest token sequence accepted by exactly one DFA. An empty input tuple is
treated as no evidence: the reference comparison is `None`, and equivalence is
only reported when some check actually ran and agreed.

This is bounded evidence for dictionary equivalence. It does not decide the
question for every string, and it does not produce one normal form for an
arbitrary dictionary. Improper dictionaries are rejected by the reference
tokenizer validation.

## 8.6 Restricted partial orders

Section 8.6 is implemented for one restricted class. A general dependency DAG
is outside this code.

A finite rule set is in the byte-disjoint base class when:

- every left and right component has length 1; and
- no two rules share a byte in their left or right components.

`OrderedRules.precedes` contains pairs `(earlier, later)` of positions, so an
earlier position must occur before a later position. A lower `MergeRule.index`
is higher BPE priority. `linear_extensions` lists the linear extensions in
lexicographic order, re-indexes each resulting dictionary from 0, and stops
if there are more than 24. Each extension is still built by one Algorithm 2
step per rule.

`check_linear_extensions` compares those dictionaries with
`compare_dictionaries_bounded`, including the token-DFA product. The flags
are independent. `disjoint_class` is only the syntactic restriction.
`extensions_agree` is the comparison. A single extension agreeing with itself
is recorded, and it is not treated as evidence that rules commute. An improper
extension comes back as a dependency failure, with `extensions_agree is None`
and no byte-string counterexample.

For `a⫽b` and `c⫽d`, both orders are proper and `abcd` tokenizes as `(ab, cd)`.
The reference check uses every string over `{a,b,c,d}` of length at most 4,
which is 341 strings including the empty string. The token-DFA product runs
on the whole token language of the rule-byte alphabet. `a⫽b` and `b⫽a` share
bytes, so they are outside the class: `aba` tokenizes as `(ab, a)` when the
first rule has priority and `(a, ba)` when the second does. Five unconstrained
byte-disjoint rules are rejected because that antichain has 120 extensions,
above the cap.

The public names are `OrderedRules`, `LinearExtensionResult`,
`is_byte_disjoint_base`, `linear_extensions`, and `check_linear_extensions`
in `src/bpe_token_automata/partial_order.py`. The live commands are:

```bash
make 8.6 data/dictionaries/demo_partial.merges
make partial_order data/dictionaries/demo_partial.merges
```

The file is an ordinary merge list. Its rules are the partial order, and each
`# text:` line is an input. Optional `# precedes: 0 1` lines require that rule
position before another. The command prints whether the rules are byte-disjoint,
lists the linear extensions, and reports the 8.2 comparison on those inputs.
Run the tests with `make test-extensions`.

## 8.11 Canonical token-sequence pattern matching

`TokenPatternMatcher` implements Aho-Corasick over complete BPE tokens. Its
`find` method reports overlapping matches in token coordinates. The
`find_canonical` method composes matching with a constructed `TokenDFA`: it
first requires the complete supplied token sequence to be accepted by the DFA,
then scans the sequence, and finally checks that each reported match span is
accepted by the DFA as a token sequence. A non-canonical segmentation does not
come back as a match.

`match_bytes` is the comparison baseline. It searches the detokenized byte
string and reports byte-coordinate matches. A real cross-boundary example is
the token sequence `(ab, cd)` against the byte pattern `bc`: the detokenized
string `abcd` contains a byte match at `[1, 3)`, while the token-level pattern
`(b, c)` does not match the canonical tokenization because the pattern crosses
a complete-token boundary.

Both matchers return matches ordered by end coordinate and then pattern index,
so equivalent match sets can be compared directly.

## Tests

```bash
make test-extensions
```

That runs `tests/test_extensions.py` and `tests/test_partial_order.py`.
`make check` runs them as well.

The 8.2 and 8.11 tests cover commuting dictionary reorderings, a bounded
counterexample, improper dictionaries, empty-input evidence, overlapping token
patterns, matching versus detokenize-then-match at a token boundary, canonical
DFA rejection, a non-canonical matched-span rejection, and empty-pattern
validation. The 8.6 tests cover lexicographic extensions, precedence filtering,
re-indexing, a cycle, the 24-extension cap, the byte-disjoint classification,
the `abcd` agreement, the `aba` disagreement, an improper `ab⫽c` extension,
and the one-rule case. Report an 8.2 or 8.6 result together with the input
set, the DFA alphabet, and, for 8.6, the extension cap.
