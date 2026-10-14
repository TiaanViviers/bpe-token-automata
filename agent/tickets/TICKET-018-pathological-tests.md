# TICKET-018: Section 6.6 pathological and robustness tests

## Status

```text
done
```

## Owner

- Human owner: (group)
- Supporting partner: (group)
- Agent use: implementation

## Goal

Add an automated pathological suite that `make test` can run: increasing \(a^n\), a nested doubling merge chain, a long unspaced string, a streaming first-token change, and one mixed Unicode/whitespace/emoji input.

## Background

Course §6.6 cites streaming/incremental BPE work [13], [11]. Section 5.6 timeout smokes are **not** this family. Malformed dictionaries are already covered by parser tests; cite them in TICKET-019 rather than duplicating.

Depends on TICKET-017 helpers (`assert_section_62`, `compositions` if uniqueness is cheap on these strings).

## Authoritative sources

- Project specification: §6.6
- Paper and section: [13], [11] as motivation only; do not copy their benchmarks
- Approved decision: D57
- Existing implementation/documentation: unary `[a⫽a, aa⫽a]` is a **different** chain from doubling `[a⫽a, aa⫽aa, …]`

## Scope

The ticket includes:

- `tests/test_pathological.py`
- \(n\in\{8,16,32,64\}\) for \(a^n\) on `[a⫽a, aa⫽a]` (existing unary fixture) with full §6.2 checks
- Doubling dictionary `[a⫽a, aa⫽aa, aaaa⫽aaaa, aaaaaaaa⫽aaaaaaaa]` and agreement on \(a^{2^k}\) for \(k\le 4\) plus mixed lengths up to 64
- One length-64 string over `{a,b}` with no spaces, Example 2 dictionary
- Streaming: `D=[a⫽a]`, \(T^D(\mathtt{a})=(a)\) and \(T^D(\mathtt{aa})=(aa)\)
- Mixed bytes: space + NFD combining acute (`e\xcc\x81`) + grinning-face UTF-8; token identity is bytes; NFC `é` is a different string
- Sizes compatible with `make check`

## Non-goals

The ticket explicitly excludes:

- Huge \(n\) / throughput (Section 7 Q6)
- 5.6 timeout study
- New parser negative tests
- Test matrix (TICKET-019)
- Changing production algorithms

## Preconditions

Before implementation:

- [ ] TICKET-017 helpers exist (`tests/differential.py`)
- [ ] Relevant formal definitions are understood.
- [ ] `26455900-CS345/` is on `main` and its working state is understood.
- [ ] Pre-existing changes have been identified and can be preserved.

## Proposed design

Reuse `assert_section_62` for oracle/transducer/DFA agreement. For \(a^n\) uniqueness, compositions of length 64 is \(2^{63}\) — **do not** enumerate compositions for \(n>8\). Uniqueness on pathological strings: only compare the canonical sequence and a handful of altered splits (first-long-token, fully-split base). Bound-8 uniqueness stays in TICKET-017.

Commit the doubling dictionary as `data/dictionaries/doubling_self_merge.merges` so the matrix can name the fixture.

## Files likely to change

```text
26455900-CS345/tests/test_pathological.py
26455900-CS345/data/dictionaries/doubling_self_merge.merges
```

## Acceptance criteria

- [ ] All five §6.6 bullets have a named test (malformed cites existing parser tests in comments / TICKET-019)
- [ ] `make check` stays well under a minute for this module
- [ ] Doubling chain is not the unary `[aa⫽a]` fixture
- [ ] Mixed input does not NFC-normalise

## Required test evidence

### Unit tests

- Streaming first-token change
- Mixed Unicode identity

### Differential or exhaustive tests

- `a^n` and doubling vs `tokenize_reference` + transducer + DFA
- Long unspaced Example 2 string

### Negative and special cases

- Cite existing malformed dictionary tests

## Documentation changes

- [ ] Deferred to TICKET-019 matrix rows

## Validation commands

```bash
cd 26455900-CS345
make check
```

Additional commands:

```bash
uv run pytest tests/test_pathological.py
```

## Risks

- Performance: uniqueness via full compositions on \(n=64\) would hang — forbidden
- Correctness: doubling chain construction cost is small (four rules, unary alphabet)
- Scope: do not start the report matrix here

## Open questions

None blocking.

## Definition of done

- [ ] Approved scope implemented.
- [ ] Acceptance criteria satisfied.
- [ ] Required tests added and passing.
- [ ] `make check` passes.
- [ ] No private workspace material entered `26455900-CS345/`.
- [ ] Both partners can explain why doubling \(\neq\) unary `[aa⫽a]`.
