"""Token-sequence agreement and tokenize throughput (course spec §7.3 Q5–Q6)."""

from __future__ import annotations

import importlib.util
import statistics
import sys
import time
from collections.abc import Callable
from itertools import product
from pathlib import Path
from types import ModuleType
from typing import Protocol

from bpe_token_automata.automaton import universal_token_dfa
from bpe_token_automata.dictionary import Dictionary, parse_dictionary_path
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.tokens import Token
from bpe_token_automata.transducer import compile_tokenizer, tokenize
from bpe_token_automata.transducer.model import SubsequentialTransducer
from experiments.host import (
    DeadlineExceeded,
    call_with_timeout,
    host_metadata,
    median_seconds,
    peak_tracemalloc,
    write_csv,
    write_json,
)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "results"
DATA = ROOT / "data" / "dictionaries"


def _load_minbpe_adapter() -> ModuleType:
    path = ROOT / "tests" / "minbpe_adapter.py"
    spec = importlib.util.spec_from_file_location("minbpe_adapter", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("minbpe_adapter", module)
    spec.loader.exec_module(module)
    return module


_MINBPE = _load_minbpe_adapter()


class _HasTokenSequence(Protocol):
    def token_sequence(self, data: bytes) -> object: ...


LENGTHS = (256, 1024, 4096, 16384, 65536)
REPEATS = 7
TIMEOUT_S = 60.0
AGREEMENT_FIELDS = (
    "set",
    "n_strings",
    "n_exact_sequence_match",
    "match_rate",
    "comparators",
)
THROUGHPUT_FIELDS = (
    "case",
    "dictionary",
    "kind",
    "n_bytes",
    "implementation",
    "status",
    "tokenize_seconds_median",
    "bytes_per_second_median",
    "tokenize_peak_bytes",
    "compile_seconds_median",
)


def _require_dictionary(path: Path) -> Dictionary:
    parsed = parse_dictionary_path(path)
    if parsed.dictionary is None:
        raise ValueError(f"failed to parse {path}")
    return parsed.dictionary


def enumerate_strings(alphabet: bytes, max_length: int) -> list[bytes]:
    texts: list[bytes] = []
    for length in range(max_length + 1):
        for symbols in product(alphabet, repeat=length):
            texts.append(bytes(symbols))
    return texts


def agreement_row(
    *,
    name: str,
    texts: list[bytes],
    left: Callable[[bytes], object],
    right: Callable[[bytes], object],
    comparators: str,
) -> dict[str, object]:
    matches = 0
    for text in texts:
        if left(text) == right(text):
            matches += 1
    n_strings = len(texts)
    rate = 0.0 if n_strings == 0 else matches / n_strings
    return {
        "set": name,
        "n_strings": n_strings,
        "n_exact_sequence_match": matches,
        "match_rate": rate,
        "comparators": comparators,
    }


def measure_timed(
    fn: Callable[[], object],
    *,
    n_bytes: int,
    repeats: int,
    timeout_s: float,
    warmup: bool,
) -> dict[str, object]:
    """Warmup + repeats under a single wall-clock budget. Timeouts omit medians."""
    timeout_row: dict[str, object] = {
        "status": "timeout_60s",
        "tokenize_seconds_median": None,
        "bytes_per_second_median": None,
        "tokenize_peak_bytes": None,
    }
    if timeout_s <= 0:
        return timeout_row
    deadline = time.perf_counter() + timeout_s
    try:
        if warmup:
            call_with_timeout(fn, deadline - time.perf_counter())
        samples: list[float] = []
        for _ in range(repeats):
            remaining = deadline - time.perf_counter()
            start = time.perf_counter()
            call_with_timeout(fn, remaining)
            samples.append(time.perf_counter() - start)
        remaining = deadline - time.perf_counter()

        def traced() -> tuple[object, int]:
            return peak_tracemalloc(fn)

        if remaining > 0:
            _, peak = call_with_timeout(traced, remaining)
        else:
            _, peak = traced()
    except DeadlineExceeded:
        return timeout_row
    median = statistics.median(samples)
    bytes_per_second = None if median <= 0 else n_bytes / median
    return {
        "status": "ok",
        "tokenize_seconds_median": median,
        "bytes_per_second_median": bytes_per_second,
        "tokenize_peak_bytes": peak,
    }


def _minbpe_or_none(dictionary: Dictionary) -> _HasTokenSequence | None:
    try:
        tokenizer = _MINBPE.LoadedBasicTokenizer(dictionary)
    except ValueError:
        return None
    return tokenizer  # type: ignore[no-any-return]


def _thunk(fn: Callable[..., object], *args: object) -> Callable[[], object]:
    def run() -> object:
        return fn(*args)

    return run


def throughput_row(
    *,
    case: str,
    dictionary_name: str,
    kind: str,
    n_bytes: int,
    implementation: str,
    fn: Callable[[], object],
    repeats: int,
    timeout_s: float,
    warmup: bool,
    compile_seconds_median: float | None,
) -> dict[str, object]:
    timed = measure_timed(
        fn,
        n_bytes=n_bytes,
        repeats=repeats,
        timeout_s=timeout_s,
        warmup=warmup,
    )
    return {
        "case": case,
        "dictionary": dictionary_name,
        "kind": kind,
        "n_bytes": n_bytes,
        "implementation": implementation,
        "compile_seconds_median": compile_seconds_median,
        **timed,
    }


def compiled_transducer(
    dictionary: Dictionary,
    alphabet: frozenset[Token],
) -> tuple[SubsequentialTransducer, float]:
    base = universal_token_dfa(alphabet)

    def compile_once() -> SubsequentialTransducer:
        return compile_tokenizer(dictionary, base)

    compile_s = median_seconds(compile_once, repeats=3, warmup=True)
    machine = compile_once()
    return machine, compile_s


def agreement_rows() -> list[dict[str, object]]:
    example2 = _require_dictionary(DATA / "example2.merges")
    unary = _require_dictionary(DATA / "unary_self_merge.merges")
    ab = frozenset({b"a", b"b"})
    a_only = frozenset({b"a"})
    example2_machine = compile_tokenizer(example2, universal_token_dfa(ab))
    unary_machine = compile_tokenizer(unary, universal_token_dfa(a_only))
    minbpe = _MINBPE.LoadedBasicTokenizer(example2)
    example2_texts = enumerate_strings(b"ab", 8)
    unary_texts = [b"a" * n for n in range(9)]
    minbpe_texts = enumerate_strings(b"ab", 6)
    return [
        agreement_row(
            name="example2_ab_le8",
            texts=example2_texts,
            left=lambda text: tokenize(example2_machine, text),
            right=lambda text: tokenize_reference(example2, text),
            comparators="transducer_vs_reference",
        ),
        agreement_row(
            name="unary_a_le8",
            texts=unary_texts,
            left=lambda text: tokenize(unary_machine, text),
            right=lambda text: tokenize_reference(unary, text),
            comparators="transducer_vs_reference",
        ),
        agreement_row(
            name="example2_ab_le6_minbpe",
            texts=minbpe_texts,
            left=lambda text: tokenize(example2_machine, text),
            right=minbpe.token_sequence,
            comparators="transducer_vs_minbpe",
        ),
    ]


def throughput_jobs(
    *,
    lengths: tuple[int, ...],
    repeats: int,
    timeout_s: float,
    warmup: bool,
) -> list[dict[str, object]]:
    example2 = _require_dictionary(DATA / "example2.merges")
    unary = _require_dictionary(DATA / "unary_self_merge.merges")
    doubling = _require_dictionary(DATA / "doubling_self_merge.merges")
    empty = Dictionary(())
    ab = frozenset({b"a", b"b"})
    a_only = frozenset({b"a"})

    specs: list[
        tuple[str, str, str, Dictionary, frozenset[Token], Callable[[int], bytes]]
    ] = [
        (
            "example2_ordinary_ab",
            "example2",
            "ordinary",
            example2,
            ab,
            lambda n: (b"ab" * (n // 2))[:n],
        ),
        (
            "empty_ordinary_ab",
            "empty",
            "ordinary",
            empty,
            ab,
            lambda n: (b"ab" * (n // 2))[:n],
        ),
        (
            "unary_pathological_a_n",
            "unary_self_merge",
            "pathological",
            unary,
            a_only,
            lambda n: b"a" * n,
        ),
        (
            "doubling_pathological_a_n",
            "doubling_self_merge",
            "pathological",
            doubling,
            a_only,
            lambda n: b"a" * n,
        ),
    ]
    rows: list[dict[str, object]] = []
    for case, dict_name, kind, dictionary, alphabet, make_text in specs:
        machine, compile_s = compiled_transducer(dictionary, alphabet)
        reference_fn_factory = dictionary
        minbpe = _minbpe_or_none(dictionary)
        for n_bytes in lengths:
            text = make_text(n_bytes)
            assert len(text) == n_bytes
            rows.append(
                throughput_row(
                    case=case,
                    dictionary_name=dict_name,
                    kind=kind,
                    n_bytes=n_bytes,
                    implementation="transducer",
                    fn=_thunk(tokenize, machine, text),
                    repeats=repeats,
                    timeout_s=timeout_s,
                    warmup=warmup,
                    compile_seconds_median=compile_s,
                )
            )
            rows.append(
                throughput_row(
                    case=case,
                    dictionary_name=dict_name,
                    kind=kind,
                    n_bytes=n_bytes,
                    implementation="reference",
                    fn=_thunk(tokenize_reference, reference_fn_factory, text),
                    repeats=repeats,
                    timeout_s=timeout_s,
                    warmup=warmup,
                    compile_seconds_median=None,
                )
            )
            if minbpe is not None:
                rows.append(
                    throughput_row(
                        case=case,
                        dictionary_name=dict_name,
                        kind=kind,
                        n_bytes=n_bytes,
                        implementation="minbpe",
                        fn=_thunk(minbpe.token_sequence, text),
                        repeats=repeats,
                        timeout_s=timeout_s,
                        warmup=warmup,
                        compile_seconds_median=None,
                    )
                )
    return rows


def build_agreement_payload(rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "host": host_metadata(),
        "notes": (
            "Exact token-sequence match rate. Comparable sets match Section 6. "
            "A rate other than 1.0 is a bug. Broader evidence: docs/testing.md."
        ),
        "rows": rows,
    }


def build_throughput_payload(
    rows: list[dict[str, object]],
    *,
    repeats: int,
    timeout_s: float,
) -> dict[str, object]:
    return {
        "host": host_metadata(),
        "repeats": repeats,
        "timeout_s": timeout_s,
        "unit": "bytes_per_second",
        "notes": (
            "Compile time is separate from tokenize time and is not under the "
            "60 s row cap. Peak memory is tracemalloc, not RSS. Timeouts omit "
            "medians and are not averaged into successful rows. No pre-tokenization. "
            "Dictionaries are small; this is not the §5.6 timeout study."
        ),
        "rows": rows,
    }


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    agree = agreement_rows()
    through = throughput_jobs(
        lengths=LENGTHS, repeats=REPEATS, timeout_s=TIMEOUT_S, warmup=True
    )
    agree_path = RESULTS / "output_agreement.json"
    through_path = RESULTS / "tokenize_throughput.json"
    write_json(agree_path, build_agreement_payload(agree))
    write_csv(RESULTS / "output_agreement.csv", agree, AGREEMENT_FIELDS)
    write_json(
        through_path,
        build_throughput_payload(through, repeats=REPEATS, timeout_s=TIMEOUT_S),
    )
    write_csv(RESULTS / "tokenize_throughput.csv", through, THROUGHPUT_FIELDS)
    print(agree_path)
    print(through_path)


if __name__ == "__main__":
    main()
