# Implementation plan: §8.6 restricted partial orders

Give this document to the person implementing the extension. It is the build
contract. A later review will check the code against it.

Status: ready to implement. Do not implement a general DAG tokenizer.

## What this is

Specification §8.6 asks what happens if a BPE dictionary is a partial order
instead of one total order. A general DAG is a research problem: it needs a
tie-break, a confluence proof, or a restriction. This project implements the
restriction the specification already names as the concrete target.

**Class.** A finite set of merge rules is a *byte-disjoint base antichain* when:

1. every component `left` and `right` has length 1 (a single base byte), and
2. no two rules share a byte.

For that class every permutation is a proper dictionary, and every permutation
induces the same canonical tokenization. The implementation must check that
claim with the existing reference tokenizer and token-DFA product. It must
not take the claim as proof by itself.

§8.2 asks whether two total orders agree. §8.6 asks whether every linear
extension of one partial order agrees. The new code calls §8.2. It does not
reimplement the product.

## Non-goals

Do not build any of the following:

- a general dependency relation that allows multi-byte components
- a new BPE semantics, a new `apply_merge`, or a fused “apply two rules in one Algorithm 2 step”
- a claim that an arbitrary DAG is confluent
- a claim that dictionary equivalence is decidable in general
- compact-automaton work, streaming, or symbolic alphabets
- changes to `compare_dictionaries_bounded` unless a real bug blocks this ticket

“Batching” in this ticket means: the antichain is one batch, and the existing
per-rule construction is run once for every linear extension. Every extension
has exactly `len(rules)` Algorithm 2 steps, because that is what
`construct_token_dfa` does. Do not report a batch as one construction pass.

## Sources

- Specification §8.6 (restricted class, linear extensions, equivalence of the
  resulting automata). Markdown reading copy:
  `research/markdown/cs345-project-specification/index.md`.
- Berglund & van der Merwe, *Formalizing BPE Tokenization*, EPTCS 388, 2023.
  Proper dictionaries are Definition 5, already implemented by `validate_proper`.
- Berglund, Martens & van der Merwe, *Constructing a BPE Tokenization DFA*,
  TCS 1083, 2026. Algorithm 2 is `apply_merge` / `construct_token_dfa`.
- Existing §8.2 API: `compare_dictionaries_bounded` in
  `26455900-CS345/src/bpe_token_automata/dictionary_equivalence.py`.

Cite those three in `docs/extensions.md`. Do not cite a private plan, a chat,
or “the project plan”.

## Where it sits in the current code

Priority in this repository is list order. `tokenize_reference` walks
`dictionary.rules` from front to back and applies the first rule that matches.
`MergeRule.index` must be `0 .. n-1` in that same order when a dictionary is
built. A lower index is higher priority.

`validate_proper` (Definition 5) treats a component of length greater than 1 as
illegal unless an earlier rule produced that exact token. A component of
length 1 is a base byte and is always legal. That is why the class forbids
multi-byte components: a rule such as `ab ⫽ c` is proper only after some
earlier rule has produced `ab`. Swapping it with another rule can make an
improper dictionary. That is a dependency, and it is outside this class.

`construct_token_dfa(dictionary, universal_token_dfa(alphabet))` runs
Algorithm 2 and rejects an improper dictionary. `apply_merge` does not look at
`rule.index` for the merge itself; the order of calls is the dictionary order.

`compare_dictionaries_bounded(left, right, inputs, check_token_dfa=True)`
already:

- rejects an improper dictionary before comparing
- sets `reference_agrees` to `None` when `inputs` is empty
- sets `equivalent` only when some real check agreed
- on DFA disagreement, sets `dfa_witness` to a token sequence accepted by
  exactly one of the two token DFAs

Reuse that function between extensions. Do not write another product search
and do not compare state numbers across two automata.

Known behaviour the new code must respect:

- `equivalent` is about the supplied inputs and the optional DFA check. It is
  not a general decision procedure. Pass a real input tuple and
  `check_token_dfa=True`.
- An empty input tuple with `check_token_dfa=False` yields
  `reference_agrees is None` and `equivalent is False`. Do not use that call
  as evidence.
- `dfa_witness` may be the token sequence `(a, ba)` for the rules `a⫽b, b⫽a`
  versus `b⫽a, a⫽b`. The right DFA accepts it and the left DFA rejects it.
  The underlying string `aba` is the reference counterexample:
  `(ab, a)` versus `(a, ba)`.

## Public API

New module: `26455900-CS345/src/bpe_token_automata/partial_order.py`.

Export the types and functions from `bpe_token_automata/__init__.py` and
`__all__`, in the same style as `compare_dictionaries_bounded`.

```python
MAX_LINEAR_EXTENSIONS = 24


@dataclass(frozen=True, slots=True)
class OrderedRules:
    """Rules identified by position, plus precedence constraints.

    `precedes` holds pairs `(earlier, later)` of positions into `rules`.
    Every linear extension must place `earlier` before `later`.
    An empty `precedes` is an antichain: every permutation is an extension.
    `MergeRule.index` on the input rules is ignored. Identity is the position
    in `rules`.
    """

    rules: tuple[MergeRule, ...]
    precedes: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True, slots=True)
class LinearExtensionResult:
    """Evidence for one partial order. The flags are independent on purpose."""

    disjoint_class: bool
    extensions: tuple[Dictionary, ...]
    extensions_agree: bool | None
    improper_extension: Dictionary | None
    compared_inputs: tuple[bytes, ...]
    counterexample_input: bytes | None
    left_extension: int | None
    right_extension: int | None
    left_tokens: TokenSequence | None
    right_tokens: TokenSequence | None
    dfa_agrees: bool | None
    dfa_witness: TokenSequence | None
    state_counts: tuple[int, ...] | None


def is_byte_disjoint_base(rules: Sequence[MergeRule]) -> bool:
    """True iff every component has length 1 and the rules share no byte."""


def linear_extensions(order: OrderedRules) -> tuple[Dictionary, ...]:
    """Lexicographic linear extensions, each re-indexed as a Dictionary."""


def check_linear_extensions(
    order: OrderedRules,
    inputs: Iterable[bytes],
) -> LinearExtensionResult:
    """Classify the rules, enumerate extensions, and compare them."""
```

### `is_byte_disjoint_base`

Return `True` only when all of the following hold:

- there is at least one rule (the empty set is not evidence of commutation)
- `len(rule.left) == 1` and `len(rule.right) == 1` for every rule
- the sets `set(rule.left) | set(rule.right)` are pairwise disjoint

`a⫽b` and `c⫽d` is in the class. `a⫽a` and `b⫽b` is in the class.
`a⫽b` and `b⫽a` is not. `ab⫽c` and `d⫽e` is not, because `ab` has length 2.
Two copies of `a⫽b` are not, because they share bytes.

Do not treat “the merged tokens are different strings” as disjointness.
`a⫽b` produces `ab` and `b⫽a` produces `ba`; they still share `a` and `b`.

### `linear_extensions`

1. Reject a precedence endpoint that is not in `range(len(rules))` with
   `ValueError`.
2. Reject a self-loop `(i, i)` as a cycle, with `ValueError`.
3. Detect a cycle before search (Kahn’s algorithm is enough). On a cycle,
   raise `ValueError`. Do not return an empty tuple and call that success.
4. If the number of linear extensions would exceed `MAX_LINEAR_EXTENSIONS`
   (24, which is `4!`), raise `ValueError` before building any DFA. Five
   unconstrained rules are 120 permutations and must fail this check.
   Count first, or abort the backtracking when the count would pass 24.
5. Emit extensions in lexicographic order of the position tuples.
   Backtracking that tries positions `0, 1, 2, ...` does this.
   A node `v` may be appended only when every position that must precede `v`
   is already chosen.
6. Each emitted `Dictionary` is a new tuple of `MergeRule` values whose
   `index` is `0 .. n-1` in extension order. Copy `left` and `right`.
   Do not keep the input rules’ original indices.

Worked precedence. Rules `(a⫽b, c⫽d, e⫽f)` with `precedes=((0, 1),)` have
exactly these position orders:

```text
(0, 1, 2), (0, 2, 1), (2, 0, 1)
```

These are absent: `(1, 0, 2), (1, 2, 0), (2, 1, 0)`.

### `check_linear_extensions`

Steps, in this order:

1. Set `disjoint_class = is_byte_disjoint_base(order.rules)`.
   Precedence edges do not affect this flag. Disjoint rules plus one legal
   precedence edge are still in the class.
2. `extensions = linear_extensions(order)`.
3. Run `validate_proper` on every extension. If any fails, return
   `extensions_agree=None`, `improper_extension` set to that dictionary,
   `dfa_agrees=None`, `dfa_witness=None`, `state_counts=None`, and no
   counterexample tokens. Do not raise. An improper extension is a dependency
   problem, not a tokenization mismatch.
4. Deduplicate `inputs` with `tuple(dict.fromkeys(inputs))`, same as §8.2.
   If the tuple is empty, raise `ValueError`. This check always requires a
   stated input bound. Do not fall through to the §8.2 empty-input rule.
5. Compare extension `0` with extension `i` for `i = 1, 2, ...` by calling
   `compare_dictionaries_bounded(extensions[0], extensions[i], checked, check_token_dfa=True)`.
   Language agreement is transitive on a shared alphabet, so pairwise
   comparison with the first extension is enough.
6. On the first result that is not an agreement, stop.
   Agreement means `reference_agrees is True` and `dfa_agrees is True`.
   Record `counterexample_input`, `left_tokens`, `right_tokens`,
   `left_extension=0`, `right_extension=i`, `dfa_agrees`, and `dfa_witness`
   from that call. Set `extensions_agree = False`.
7. If every comparison agrees, set `extensions_agree = True`,
   `dfa_agrees = True`, and `dfa_witness = None`.
   A single extension has no pair to compare. Then `extensions_agree` is
   `True` only as a vacuous fact. Callers must not describe that as
   commutation. The demo evidence is `disjoint_class and len(extensions) >= 2
   and extensions_agree`.
8. When every extension is proper, also record `state_counts`:
   for each extension, `construct_token_dfa(extension, universal_token_dfa(alphabet)).final.n_states`.
   Build `alphabet` as the frozenset of length-1 tokens `bytes((b,))` for
   every byte that appears in any rule component. Do not add a fake `0` byte.
   Do not require the counts to be equal. Record them. Language agreement is
   the correctness claim; equal size is not.

`disjoint_class` and `extensions_agree` stay separate. A one-extension poset
of overlapping rules can have `extensions_agree is True` and
`disjoint_class is False`. That must not be reported as “the partial order
commutes”.

## Tests

New file: `26455900-CS345/tests/test_partial_order.py`.

Expected token sequences in tests are handwritten literals. Do not compute the
expected `TokenSequence` by calling `tokenize_reference` in the test.

| Test | Setup | Required assertions |
|---|---|---|
| Disjoint commutation | `a⫽b`, `c⫽d`, no precedence. Inputs: every string in `{a,b,c,d}` of length at most 4 (341 strings, including empty). | `disjoint_class`. Exactly two extensions. `extensions_agree`. `dfa_agrees is True`. `dfa_witness is None`. Both orders tokenize `abcd` as `(ab, cd)`. `state_counts` has length 2. |
| Three-rule precedence | `a⫽b`, `c⫽d`, `e⫽f`, `precedes=((0, 1),)`. Inputs may be `{a,b,c,d,e,f}` of length at most 2, and `check_token_dfa` still runs inside the API. | Extension position tuples are exactly `(0,1,2), (0,2,1), (2,0,1)`. `disjoint_class`. `extensions_agree`. |
| Overlapping orders | `a⫽b`, `b⫽a`, no precedence. Inputs include `b"aba"`. | `disjoint_class is False`. Two extensions. `extensions_agree is False`. `counterexample_input == b"aba"`. Tokens are `(ab, a)` and `(a, ba)` in extension order (first extension is `a⫽b` then `b⫽a`). `dfa_witness` is accepted by exactly one of the two token DFAs built the same way as §8.2, over `{a,b}`. |
| Dependency, not a mismatch | `ab⫽c` and `d⫽e`, no precedence. | `disjoint_class is False`. `extensions_agree is None`. `improper_extension` is the extension that puts `ab⫽c` first. `counterexample_input is None`. |
| Precedence is enforced | the three-rule case above is enough if the absent permutations are asserted | Do not only test the unconstrained antichain. |
| Cycle | `precedes=((0, 1), (1, 0))` on two length-1 rules | `ValueError`. No result object. |
| Cap | five byte-disjoint rules and empty precedence | `ValueError` mentioning the cap. No DFA construction required beyond the guard; the test’s point is that it raises. |
| Vacuous one rule | a single rule `a⫽b`, inputs `(b"ab",)` | `disjoint_class`. One extension. `extensions_agree is True`. This test exists so the vacuous case stays obviously different from the two-rule demo. |
| Empty input rejected | two disjoint rules, inputs `()` | `ValueError`. |

The 341-string bound is the same shape as the §8.2 commuting test. State it in
the test docstring and in `docs/extensions.md`. With `check_token_dfa=True`
the product check is exhaustive for the token language on that byte alphabet.
Say both bounds. Do not describe the DFA check as “only strings of length ≤ 4”.

## Documentation

Update `26455900-CS345/docs/extensions.md` with a §8.6 section that states:

- the byte-disjoint base class, in the two bullets above
- precedence means “earlier position before later position”, and lower index
  is higher priority
- the result flags are separate
- one extension agreeing with itself is not commutation evidence
- an improper extension is reported and is not a tokenization counterexample
- the extension cap is 24
- the `abcd` / `aba` examples and the 341-string bound
- construction still performs one Algorithm 2 step per rule
- this is not a general DAG semantics and not a decidability result

Add the three citations listed under Sources.

Update `26455900-CS345/README.md` so the status line and the extensions
sentence include §8.6.

Update `26455900-CS345/docs/testing.md`:

- add a matrix row for §8.6 whose case count equals the number of new test
  functions
- after implementation, run `make check` and put **that** collected count and
  **that** elapsed time in the recorded-run line and in the notes bullet
- do not copy a count or a time from this plan, from chat, or from an older
  commit
- the current suite before this work collects 141 tests; the new file adds
  more, so 141 will be wrong after the change

## Demo script

Both partners should be able to say this without looking at the code.

1. A normal dictionary is one total order. §8.6 allows several orders, but
   only when a restriction makes them safe.
2. `a⫽b` and `c⫽d` share no bytes. Both orders are proper. `abcd` tokenizes
   as `(ab, cd)` either way. The token DFAs accept the same language.
3. `a⫽b` and `b⫽a` share bytes, so they are outside the class. `aba` is
   `(ab, a)` if `a⫽b` is first and `(a, ba)` if `b⫽a` is first.
4. We did not define what an arbitrary DAG of overlapping rules means.

## Reviewer will reject the change if

- `disjoint_class` is true for `a⫽b` together with `b⫽a`, or for any rule
  whose component has length greater than 1
- a cycle returns an empty extension list instead of `ValueError`
- five unconstrained rules run to completion
- dictionaries keep the caller’s original `MergeRule.index` values
- the code reports commutation when there is only one linear extension
- `extensions_agree` is `True` for the `aba` pair
- the `aba` test builds its expected tokens by calling `tokenize_reference`
- `dfa_witness` is only checked for being non-empty, or is a sequence both
  DFAs accept (the §8.2 bug was comparing state ids; do not reintroduce it)
- an improper extension is reported as `extensions_agree is False` with a
  fake byte counterexample
- a new product search or a new `apply_merge` appears
- the docs say every partial order was proved confluent, or that batching
  runs Algorithm 2 once for the whole antichain
- `docs/testing.md` states a pytest count or a runtime that `make check` did
  not just print
- private workspace files are copied into `26455900-CS345/`

## Validation

From `26455900-CS345/`:

```bash
uv run pytest tests/test_partial_order.py
make check
```

`make check` is the gate. Do not commit or push unless a human asks.

## Suggested short argument for the report

This is a sufficient condition for this class, not a theorem about all
dictionaries. Write it in the report later; the code’s evidence is still the
enumeration.

Take rules whose components are single bytes and whose byte sets are
disjoint. A match of rule A is two adjacent base tokens whose bytes belong
to A. Replacing them with `A`’s merged token does not create, destroy, or
relabel a match of any other rule, because that rule’s bytes do not occur in
A’s tokens. Every order therefore performs the same replacements. The tests
check that conclusion on every linear extension up to the cap, by reference
tokenization on a stated bound and by token-DFA language agreement.
