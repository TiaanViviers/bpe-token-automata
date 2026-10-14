# BPE Token Automata

CS345 semester project. The code builds the finite-state constructions for canonical byte-pair-encoding tokenization from the project spec: a dictionary model, a reference tokenizer, a baseline token DFA, a string-to-tokenization transducer, a compact delayed-input automaton, tests, and measurements.

Symbols are UTF-8 bytes. The canonical tokenization is the SentencePiece function $T^D$ from Berglund and van der Merwe. On a proper dictionary that function agrees with the Hugging Face reading of the same rules.

## Recorded presentation

{Link to video will be here once we record it}

`VIDEO: `


## What is implemented

| Section | Contents | Where to read more |
|---|---|---|
| 5.1 | Merge-list parser, proper-dictionary validator, independent reference tokenizer | [`docs/design-decisions.md`](docs/design-decisions.md) |
| 5.2 | Baseline token DFA, Algorithm 2 of Berglund, Martens and van der Merwe, with a merge trace and a text serialisation | [`docs/design-decisions.md`](docs/design-decisions.md) |
| 5.3 | Paper Example 2, the unary self-merge chain, and three original examples (a finite language, `é` as two bytes, U+1F600 as four bytes) | [`docs/token-dfa-examples.md`](docs/token-dfa-examples.md) |
| 5.4 | Subsequential string-to-tokenization transducer (Observation 3, then Béal and Carton) | [`docs/transducer.md`](docs/transducer.md) |
| 5.5 | Compact delayed-input automaton with default transitions, state avoidance, and clean-copy reuse (O1, O2, O3) | [`docs/design-decisions.md`](docs/design-decisions.md) |
| 5.6 | Prefix study of converted GPT-2 and SmolLM 2 dictionaries, with a one-minute mark, a ten-minute stop, and an 8 GiB RSS limit | [`data/dictionaries/REALISTIC.md`](data/dictionaries/REALISTIC.md), [`docs/experiments.md`](docs/experiments.md) |
| 6 | Automated tests: unit, differential, exhaustive, property-based, negative, and equivalence | [`docs/testing.md`](docs/testing.md) |
| 7 | Measurements for the six required questions, with raw JSON and CSV | [`docs/experiments.md`](docs/experiments.md) |
| 8.2 | Bounded dictionary equivalence | [`docs/extensions.md`](docs/extensions.md) |
| 8.6 | Linear extensions of a byte-disjoint partial order, compared with the 8.2 check, cap 24 | [`docs/extensions.md`](docs/extensions.md) |
| 8.11 | Canonical token-sequence pattern matching | [`docs/extensions.md`](docs/extensions.md) |

O4 (prefix-forest sink predicates) is not in the compact construction. The technical report PDF is not in the repository yet. `report/` is the place for it.

## Chosen extensions

CS345 requires at least two extensions from Section 8. This repository has three.

**8.2 Equivalence of BPE dictionaries.** `compare_dictionaries_bounded` runs the reference tokenizer on an explicit list of byte strings and, when asked, compares the two token DFAs on the byte alphabet that actually appears. Agreement on that set is the result. It is bounded evidence. It does not decide equivalence for every string, and it does not produce a unique normal form for an arbitrary dictionary.

**8.6 Partially ordered dictionaries.** The implemented class is byte-disjoint base rules: each side of a rule is one byte, and the rules do not share bytes. `OrderedRules.precedes` can force one rule before another. `check_linear_extensions` lists the linear extensions, up to 24, rebuilds each one as an ordinary dictionary, and compares them with the 8.2 check. `a⫽b` with `c⫽d` agrees on `abcd`, both orders giving `(ab, cd)`. `a⫽b` with `b⫽a` shares bytes, so it is outside the class, and `aba` is `(ab, a)` or `(a, ba)` depending on order. One extension on its own is not commutation evidence. An improper extension is a validation failure, not a fake byte counterexample. A general dependency DAG is outside this class. The live command is `make partial_order`. The tests are `make test-extensions`.

**8.11 Pattern matching on canonical tokenizations.** `TokenPatternMatcher` is Aho-Corasick over whole tokens. `find_canonical` accepts a token sequence only when the token DFA accepts that sequence and each reported span. `match_bytes` is the detokenize-then-match baseline, including patterns that cross a token boundary.

## Installation

You need Python 3.12 or newer, GNU make, and [uv](https://docs.astral.sh/uv/getting-started/installation/). From a clean checkout of this repository:

```bash
make install
```

That runs `uv sync`. It creates `.venv` and installs the locked dependencies from `uv.lock`, including PyYAML and the development tools (pytest, Hypothesis, Ruff, mypy).

Confirm the checkout:

```bash
make check
```

`make check` is formatting, lint, type checking, and the test suite. It finishes in seconds. It does not download dictionaries and it does not rerun the long experiments.

## Running the code

`make demo` walks through paper Example 2 on the text `aba`: parse and validate, reference tokenization, baseline DFA (including DOT), transducer, compact counts, a dictionary comparison of that dictionary with itself, canonical pattern matching, and one improper dictionary that must be rejected.

[`data/dictionaries/demo.merges`](data/dictionaries/demo.merges) is the same example, with comment headers for the text, the pattern, and a second dictionary. Pass it to a named target:

```bash
make reference_tokenizer data/dictionaries/demo.merges
make token_dfa data/dictionaries/demo.merges
make examples data/dictionaries/demo.merges
make transducer data/dictionaries/demo.merges
make compact data/dictionaries/demo.merges
make dictionary_equivalence data/dictionaries/demo.merges
make partial_order data/dictionaries/demo_partial.merges
make pattern_match data/dictionaries/demo.merges
```

`dictionary_equivalence` reads the second dictionary named in the file (`demo_other.merges`). You can also pass two files: `make dictionary_equivalence left.merges right.merges`. `partial_order` reads the rules in the file as one partial order and compares every linear extension on the `# text:` lines. Optional `# precedes: 0 1` lines force rule 0 before rule 1. [`data/dictionaries/demo_partial.merges`](data/dictionaries/demo_partial.merges) is `a⫽b` and `c⫽d` on the text `abcd`. The same command is `make 8.6`.

To use your own rules, put a merge list in this directory. Optional `# text:` and `# pattern:` lines are comments, so the file is still a normal merge list.

```text
# text: aba
# pattern: a
a a
b a
```

`TEXT=` and `PATTERN=` override those headers, for example `make transducer live.merges TEXT=aba`.

Each command prints that piece of the pipeline: the reference token sequence, the token-DFA counts and text serialisation, the merge trace, the transducer sequence, the compact comparison, the equivalence result, or the pattern matches. Graphviz DOT is available from the demo. The text serialisation is what the tests use.

`make tests` runs pytest. `make experiments` prints the committed experiment tables. `make timeout_study` prints the recorded GPT-2 and SmolLM 2 study and does not rebuild those dictionaries. A merge list longer than 64 rules is refused by the live commands.

## Tests

```bash
make test
make check
```

`make test` is pytest with coverage. The Section 6 matrix, including family, fault class, bounds, case counts, and the recorded run (160 passed on 2026-10-05), is [`docs/testing.md`](docs/testing.md).

Focused suites:

```bash
make test-dict
make test-reference
make test-dfa
make test-transducer
make test-compact
make test-extensions
```

`make test-extensions` runs `tests/test_extensions.py` and `tests/test_partial_order.py` (sections 8.2, 8.6, and 8.11).

The only randomised tests are the Hypothesis properties in `tests/test_transducer_properties.py`. They use seed 0, `derandomize=True`, and `max_examples=40`. A failure is written to `tests/hypothesis_failures/latest.json` with the seed, the dictionary, and the input. See [`tests/hypothesis_failures/README.md`](tests/hypothesis_failures/README.md).

## Experiments

Committed tables are already in [`docs/experiments.md`](docs/experiments.md). Raw files are under `experiments/results/`. To regenerate them from this checkout:

```bash
uv run python experiments/transducer_tokenize.py
uv run python experiments/compact_compare.py
uv run python -m experiments.rule_patterns
uv run python -m experiments.tokenize_eval
uv run python experiments/timeout_study.py
```

The first two are small-dictionary timings for Sections 5.4 and 5.5. They are not the scaling results. `rule_patterns` answers question 3. `tokenize_eval` answers questions 5 and 6 and can take several minutes because each reference-tokenizer row stops at 60 seconds. `timeout_study.py` is the Section 5.6 run used for questions 1, 2, and 4. It can take about 40 minutes. One child process per dictionary and construction, 600 second wall-clock stop, 8 GiB RSS. Timeouts stay in the JSON. They are not filled in with an estimate.

| Result file | Question |
|---|---|
| `experiments/results/timeout_study.json` (and `.csv`) | 5.6, and questions 1, 2, and 4 |
| `experiments/results/rule_patterns.json` (and `.csv`) | question 3 |
| `experiments/results/output_agreement.json` (and `.csv`) | question 5 |
| `experiments/results/tokenize_throughput.json` (and `.csv`) | question 6 |
| `experiments/results/transducer_tokenize.json` | small transducer timings |
| `experiments/results/compact_compare.json` | small compact timings |

Construction peak memory is process RSS (`ru_maxrss`). Tokenize peak memory is `tracemalloc`. Short tokenize timings use one warmup and seven repeats, and the reported figure is the median. The Hypothesis seed above is the only recorded random seed. These experiment scripts are single runs, not random samples.

Optional, and it needs a network connection: rebuild the GPT-2 and SmolLM 2 merge lists from the pinned Hugging Face revisions.

```bash
uv run python experiments/fetch_dictionaries.py
```

Sources, licences, and hashes are in [`data/dictionaries/REALISTIC.md`](data/dictionaries/REALISTIC.md).

## Repository layout

```text
26455900-CS345/
├── src/bpe_token_automata/     # library
│   ├── dictionary/             # parse and validate
│   ├── reference_tokenizer.py  # T^D
│   ├── automaton/              # baseline DFA and compact DFA
│   ├── transducer/             # Observation 3 and subsequential tokenize
│   ├── dictionary_equivalence.py
│   ├── partial_order.py        # section 8.6
│   └── pattern_matching.py
├── tests/                      # pytest suite
├── experiments/                # measurement scripts
│   └── results/                # committed JSON and CSV
├── data/
│   ├── dictionaries/           # merge lists, including GPT-2 and SmolLM 2
│   └── automata/               # small string-DFA fixtures
├── scripts/                    # demo.py and section.py
├── docs/                       # design notes, test matrix, experiments, extensions
├── report/                     # technical report PDF goes here
├── Makefile
├── pyproject.toml
└── uv.lock
```

`configs/experiments/` and `results/` are empty placeholders from the initial repository. The files that back the tables live in `experiments/results/`.

## Known limitations

- The compact automaton implements O1, O2, and O3. O4 is absent, so these tables are not a reproduction of the full compact-paper numbers.
- Algorithm 2 does not trim unreachable states. Counts include those states.
- There is no pre-tokenization and no separate Hugging Face encode mode. Proper dictionaries use $T^D$.
- The live commands refuse GPT-2, SmolLM 2, and any merge list longer than 64 rules. The realistic study is the committed timeout run.
- Token-DFA product checks run on small alphabets. They are not run on the GPT-2 or SmolLM 2 automata.
- Section 8.2 reports agreement on the inputs you pass, plus the token language over the bytes that appear in those inputs and in the rules. Empty input is not treated as a successful proof.
- Section 8.6 covers byte-disjoint base rules only, and it refuses more than 24 linear extensions. It does not give a semantics for an overlapping dependency DAG.
- Section 8.11 matches whole canonical tokens. A byte pattern that crosses a token boundary can hit in `match_bytes` and miss in the token matcher. That difference is the point of the comparison.
- Question 3 on the realistic dictionaries stops at a prefix of 250 rules. Question 6 does not compile a GPT-2 or SmolLM 2 transducer.
- The 8 GiB cap was not what stopped the timeout study. Both constructions stopped on the 600 second limit, and the JSON records that.
- `make check` does not rerun `timeout_study.py`, `rule_patterns`, or `tokenize_eval`.
- The report PDF and the presentation URL are still missing.

## External material

[`tests/minbpe_adapter.py`](tests/minbpe_adapter.py) vendors the byte-level encode loop of Karpathy's [minbpe](https://github.com/karpathy/minbpe) `BasicTokenizer` (MIT). Tests inject this project's merge list. It is a third comparison oracle. It is not the project tokenizer, and it does not apply the GPT-2 regular-expression pre-tokenizer.

GPT-2 `merges.txt` (MIT) and SmolLM 2 `merges.txt` (Apache-2.0) were converted into this repository's merge syntax. Pins, hashes, and licences are in [`data/dictionaries/REALISTIC.md`](data/dictionaries/REALISTIC.md). The constructors do not import Hugging Face or tiktoken.

PyYAML, pytest, Hypothesis, Ruff, and mypy are installed from `uv.lock` with `make install`.

Generative-AI was used to help understand concepts, planning implementations, generating some parts of the code and reviewing our code. We also used it for documentation purposes but the report is hand written.

## Documentation map

- [`docs/design-decisions.md`](docs/design-decisions.md): alphabet, semantics, file format, token DFA, transducer, compact automaton, timeout method, measurement policy
- [`docs/testing.md`](docs/testing.md): Section 6 test matrix
- [`docs/experiments.md`](docs/experiments.md): Section 7 method, tables, and limits
- [`docs/extensions.md`](docs/extensions.md): extensions 8.2, 8.6, and 8.11
- [`docs/token-dfa-examples.md`](docs/token-dfa-examples.md): Section 5.3 walkthroughs
- [`docs/transducer.md`](docs/transducer.md): Observation 3 and Figure 8
