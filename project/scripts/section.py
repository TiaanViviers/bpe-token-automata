"""Run one course section on a dictionary file and print that section's output."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import tracemalloc
from dataclasses import dataclass
from pathlib import Path

from bpe_token_automata import (
    Dictionary,
    ImproperDictionaryError,
    OrderedRules,
    TokenPatternMatcher,
    TokenSequence,
    check_linear_extensions,
    compare_dictionaries_bounded,
    construct_compact_token_dfa,
    construct_token_dfa,
    format_token_label,
    format_token_sequence,
    match_bytes,
    parse_dictionary_path,
    serialize_token_dfa,
    tokenize,
    tokenize_reference,
    universal_token_dfa,
    validate_proper,
)
from bpe_token_automata.transducer import compile_tokenizer

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "results"
LARGE_DICTIONARIES = {"gpt2.merges", "smollm2.merges"}
LIVE_RULE_LIMIT = 64

ALIASES = {
    "5.1": "5.1",
    "reference_tokenizer": "5.1",
    "5.2": "5.2",
    "token_dfa": "5.2",
    "5.3": "5.3",
    "examples": "5.3",
    "5.4": "5.4",
    "transducer": "5.4",
    "5.5": "5.5",
    "compact": "5.5",
    "5.6": "5.6",
    "timeout_study": "5.6",
    "6": "6",
    "tests": "6",
    "7": "7",
    "experiments": "7",
    "8.2": "8.2",
    "dictionary_equivalence": "8.2",
    "8.6": "8.6",
    "partial_order": "8.6",
    "8.11": "8.11",
    "pattern_match": "8.11",
}


@dataclass(frozen=True, slots=True)
class LoadedInput:
    """A dictated dictionary file plus optional text and pattern headers."""

    path: Path
    dictionary: Dictionary
    texts: tuple[bytes, ...]
    pattern: str | None
    other_dictionary: Path | None
    precedes: tuple[tuple[int, int], ...]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("section", choices=sorted(ALIASES))
    parser.add_argument("files", nargs="*", type=Path)
    parser.add_argument("--text", action="append")
    parser.add_argument("--pattern")
    return parser


def _fail(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def _sequence(sequence: TokenSequence) -> str:
    rendered = format_token_sequence(sequence)
    return rendered if rendered else "ε"


def _rule(rule_left: bytes, rule_right: bytes) -> str:
    return f"{format_token_label(rule_left)} ⫽ {format_token_label(rule_right)}"


def _headers(path: Path) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {
        "text": [],
        "pattern": [],
        "dictionary-b": [],
        "precedes": [],
    }
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            continue
        body = line[1:].strip()
        for key in found:
            prefix = f"{key}:"
            if body.startswith(prefix):
                found[key].append(body[len(prefix) :].strip())
    return found


def _is_large(loaded: LoadedInput) -> bool:
    return (
        loaded.path.name in LARGE_DICTIONARIES
        or len(loaded.dictionary) > LIVE_RULE_LIMIT
    )


def _refuse_large(loaded: LoadedInput) -> None:
    if _is_large(loaded):
        _fail(f"{loaded.path.name} is too large to build live")


def _load(path: Path, texts: list[str] | None, pattern: str | None) -> LoadedInput:
    if not path.is_file():
        _fail(f"input file not found: {path}")
    parsed = parse_dictionary_path(path)
    if not parsed.ok or parsed.dictionary is None:
        for issue in parsed.issues:
            print(f"{issue.kind}: {issue.message}")
        _fail(f"could not parse {path}")
    headers = _headers(path)
    chosen_texts = texts if texts is not None else headers["text"]
    chosen_pattern = (
        pattern if pattern is not None else next(iter(headers["pattern"]), None)
    )
    other = next(iter(headers["dictionary-b"]), None)
    other_path = None if other is None else (path.parent / other).resolve()
    return LoadedInput(
        path=path,
        dictionary=parsed.dictionary,
        texts=tuple(value.encode("utf-8") for value in chosen_texts),
        pattern=chosen_pattern,
        other_dictionary=other_path,
        precedes=_precedes(headers["precedes"]),
    )


def _precedes(lines: list[str]) -> tuple[tuple[int, int], ...]:
    pairs: list[tuple[int, int]] = []
    for line in lines:
        parts = line.replace(",", " ").split()
        if len(parts) != 2:
            _fail(f"precedes line must be two rule positions: {line}")
        try:
            earlier = int(parts[0])
            later = int(parts[1])
        except ValueError:
            _fail(f"precedes positions must be integers: {line}")
        pairs.append((earlier, later))
    return tuple(pairs)


def _flag(value: bool | None) -> str:
    if value is None:
        return "none"
    return "yes" if value else "no"


def _require_proper(loaded: LoadedInput) -> None:
    validation = validate_proper(loaded.dictionary)
    if validation.ok:
        return
    print("proper: no")
    for issue in validation.issues:
        print(issue.message)
    _fail("this section needs a proper dictionary")


def _require_text(loaded: LoadedInput) -> bytes:
    if not loaded.texts:
        _fail("add a '# text: ...' line to the input file, or pass TEXT=...")
    return loaded.texts[-1]


def _alphabet(dictionary: Dictionary, texts: tuple[bytes, ...]) -> frozenset[bytes]:
    values = {byte for text in texts for byte in text}
    for rule in dictionary.rules:
        values.update(rule.left)
        values.update(rule.right)
    if not values:
        _fail("the input has no base alphabet; add a text or a rule")
    return frozenset(bytes((value,)) for value in values)


def _print_rules(dictionary: Dictionary) -> None:
    limit = 20
    shown = dictionary.rules[:limit]
    for rule in shown:
        print(f"{rule.index}: {_rule(rule.left, rule.right)}")
    if len(dictionary) > limit:
        print(f"... {len(dictionary) - limit} more rules not shown")


def _run_51(loaded: LoadedInput) -> None:
    print("5.1 reference tokenizer")
    print(f"file: {loaded.path}")
    print(f"rules: {len(loaded.dictionary)}")
    _print_rules(loaded.dictionary)
    validation = validate_proper(loaded.dictionary)
    print(f"proper: {'yes' if validation.ok else 'no'}")
    for issue in validation.issues:
        print(issue.message)
    if not validation.ok or not loaded.texts:
        if validation.ok and not loaded.texts:
            print("text: none")
        return
    if _is_large(loaded):
        print("tokenization skipped: dictionary is too large for a live run")
        return
    for text in loaded.texts:
        sequence = tokenize_reference(loaded.dictionary, text)
        shown = text.decode("utf-8") if text else "ε"
        print(f"T^D({shown}): {_sequence(sequence)}")


def _run_52(loaded: LoadedInput) -> None:
    _require_proper(loaded)
    _refuse_large(loaded)
    print("5.2 token DFA")
    print(f"file: {loaded.path}")
    base = universal_token_dfa(_alphabet(loaded.dictionary, loaded.texts))
    result = construct_token_dfa(loaded.dictionary, base)
    for step in result.steps:
        print(f"rule {step.rule_index}")
        print(f"  states: {step.n_states}")
        print(f"  final: {step.n_final}")
        print(f"  tokens: {step.n_tokens}")
        print(f"  transitions: {step.n_transitions}")
        print(f"  fresh: {step.n_fresh}")
    if not result.steps:
        final = result.final
        print("rule none")
        print(f"  states: {final.n_states}")
        print(f"  final: {final.n_final}")
        print(f"  tokens: {final.n_tokens}")
        print(f"  transitions: {final.n_transitions}")
        print("  fresh: 0")
    print("serialisation:")
    print(serialize_token_dfa(result.final), end="")


def _run_53(loaded: LoadedInput) -> None:
    _require_proper(loaded)
    _refuse_large(loaded)
    print("5.3 examples")
    print(f"file: {loaded.path}")
    base = universal_token_dfa(_alphabet(loaded.dictionary, loaded.texts))
    result = construct_token_dfa(loaded.dictionary, base)
    for trace in result.traces:
        rule = trace.rule
        print(f"rule {rule.index}: {_rule(rule.left, rule.right)}")
        triples = ", ".join(str(item) for item in trace.triples) or "none"
        fresh = ", ".join(f"{old} -> {new}" for old, new in trace.s2_to_fresh) or "none"
        redirected = (
            ", ".join(
                f"{src} -{format_token_label(token)}-> {old} becomes {new}"
                for src, token, old, new in trace.redirected
            )
            or "none"
        )
        print(f"  triples: {triples}")
        print(f"  fresh: {fresh}")
        print(f"  redirected: {redirected}")
        if loaded.texts:
            prefix = Dictionary(loaded.dictionary.rules[: rule.index + 1])
            for text in loaded.texts:
                sequence = tokenize_reference(prefix, text)
                shown = text.decode("utf-8") if text else "ε"
                print(f"  T^D({shown}) after this rule: {_sequence(sequence)}")


def _run_54(loaded: LoadedInput) -> None:
    _require_proper(loaded)
    _refuse_large(loaded)
    text = _require_text(loaded)
    print("5.4 transducer")
    print(f"file: {loaded.path}")
    base = universal_token_dfa(_alphabet(loaded.dictionary, loaded.texts))
    machine = compile_tokenizer(loaded.dictionary, base)
    transduced = tokenize(machine, text)
    reference = tokenize_reference(loaded.dictionary, text)
    print(f"transducer: {_sequence(transduced)}")
    print(f"reference: {_sequence(reference)}")
    print(f"token_sequence_agreement: {'yes' if transduced == reference else 'no'}")
    same_bytes = transduced.detokenize() == text and reference.detokenize() == text
    print(f"detokenize_equals_input: {'yes' if same_bytes else 'no'}")


def _measure(dictionary: Dictionary, alphabet: frozenset[bytes]) -> dict[str, object]:
    def baseline() -> object:
        return construct_token_dfa(dictionary, universal_token_dfa(alphabet))

    def compact() -> object:
        return construct_compact_token_dfa(dictionary, universal_token_dfa(alphabet))

    started = time.perf_counter()
    baseline_result = baseline()
    baseline_seconds = time.perf_counter() - started
    tracemalloc.start()
    started = time.perf_counter()
    compact_result = compact()
    compact_seconds = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "baseline": baseline_result,
        "compact": compact_result,
        "baseline_seconds": baseline_seconds,
        "compact_seconds": compact_seconds,
        "compact_peak_bytes": peak,
    }


def _run_55(loaded: LoadedInput) -> None:
    _require_proper(loaded)
    _refuse_large(loaded)
    print("5.5 compact automaton")
    print(f"file: {loaded.path}")
    print("times are one live run; O4 is not implemented")
    alphabet = _alphabet(loaded.dictionary, loaded.texts)
    print(
        "rules baseline_states baseline_transitions "
        "compact_states compact_transitions defaults "
        "baseline_seconds compact_seconds compact_peak_bytes"
    )
    final_baseline = None
    final_compact = None
    for count in range(len(loaded.dictionary) + 1):
        prefix = Dictionary(loaded.dictionary.rules[:count])
        measured = _measure(prefix, alphabet)
        baseline = measured["baseline"]
        compact = measured["compact"]
        final_baseline = baseline
        final_compact = compact
        print(
            f"{count} "
            f"{baseline.final.n_states} {baseline.final.n_transitions} "
            f"{compact.final.n_states_excluding_sink} {compact.final.n_transitions} "
            f"{compact.final.n_defaults} "
            f"{measured['baseline_seconds']:.6f} {measured['compact_seconds']:.6f} "
            f"{measured['compact_peak_bytes']}"
        )
    if loaded.texts and final_baseline is not None and final_compact is not None:
        for text in loaded.texts:
            sequence = tokenize_reference(loaded.dictionary, text)
            shown = text.decode("utf-8") if text else "ε"
            print(
                f"accepted({shown}): "
                f"baseline={'yes' if final_baseline.final.accepts(sequence) else 'no'} "
                f"compact={'yes' if final_compact.final.accepts(sequence) else 'no'}"
            )


def _print_recorded_timeouts() -> None:
    payload = json.loads((RESULTS / "timeout_study.json").read_text(encoding="utf-8"))
    print("recorded realistic study (not rerun):")
    for run in payload["runs"]:
        print(
            f"  {run['dictionary']} {run['construction']} "
            f"stop_status={run['stop_status']} "
            f"largest_prefix_ok={run['largest_prefix_ok']} "
            f"prefix_at_60s={run['prefix_at_60s']}"
        )


def _run_56(loaded: LoadedInput | None) -> None:
    print("5.6 timeout study")
    if loaded is not None and _is_large(loaded):
        print(f"file: {loaded.path}")
        print("not built live")
    elif loaded is not None:
        _require_proper(loaded)
        alphabet = _alphabet(loaded.dictionary, loaded.texts)
        measured = _measure(loaded.dictionary, alphabet)
        baseline = measured["baseline"]
        compact = measured["compact"]
        print(f"file: {loaded.path}")
        print(f"completed_rules: {len(loaded.dictionary)}")
        print(f"baseline_states: {baseline.final.n_states}")
        print(f"baseline_transitions: {baseline.final.n_transitions}")
        print(f"compact_states: {compact.final.n_states_excluding_sink}")
        print(f"compact_transitions: {compact.final.n_transitions}")
        print(f"defaults: {compact.final.n_defaults}")
        print(f"baseline_seconds: {measured['baseline_seconds']:.6f}")
        print(f"compact_seconds: {measured['compact_seconds']:.6f}")
    _print_recorded_timeouts()


def _run_6() -> None:
    print("6 tests")
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "--no-cov", "-q"],
        cwd=ROOT,
        check=False,
    )
    raise SystemExit(completed.returncode)


def _run_7() -> None:
    print("7 experiments")
    print("committed results; this command does not rerun the studies")
    agreement = json.loads(
        (RESULTS / "output_agreement.json").read_text(encoding="utf-8")
    )
    print("Q5 output agreement")
    for row in agreement["rows"]:
        print(
            f"  {row['set']} {row['n_exact_sequence_match']}/{row['n_strings']} "
            f"rate={row['match_rate']} {row['comparators']}"
        )
    print("Q1 Q2 Q4 failure boundary")
    timeouts = json.loads((RESULTS / "timeout_study.json").read_text(encoding="utf-8"))
    for run in timeouts["runs"]:
        print(
            f"  {run['dictionary']} {run['construction']} "
            f"stop_status={run['stop_status']} "
            f"largest_prefix_ok={run['largest_prefix_ok']} "
            f"prefix_at_60s={run['prefix_at_60s']}"
        )
    patterns = json.loads((RESULTS / "rule_patterns.json").read_text(encoding="utf-8"))
    print("Q3 rule patterns")
    for case in patterns["cases"]:
        steps = case["steps"]
        if steps:
            last = steps[-1]
            print(
                f"  {case['case']} rules={case['n_rules']} "
                f"baseline_states={last['baseline_n_states']} "
                f"compact_states={last['compact_n_states']}"
            )
        else:
            print(f"  {case['case']} rules={case['n_rules']}")
    throughput = json.loads(
        (RESULTS / "tokenize_throughput.json").read_text(encoding="utf-8")
    )
    print(f"Q6 throughput ({throughput['unit']})")
    for row in throughput["rows"]:
        rate = row.get("bytes_per_second_median")
        rate_text = "omitted" if rate is None else f"{rate:.6g}"
        print(
            f"  {row['case']} {row['implementation']} n={row['n_bytes']} "
            f"status={row['status']} bytes_per_second={rate_text}"
        )


def _load_other(path: Path) -> Dictionary:
    if path.name in LARGE_DICTIONARIES:
        _fail(f"{path.name} is a Section 5.6 dictionary and is not built live")
    parsed = parse_dictionary_path(path)
    if not parsed.ok or parsed.dictionary is None:
        for issue in parsed.issues:
            print(f"{issue.kind}: {issue.message}")
        _fail(f"could not parse {path}")
    validation = validate_proper(parsed.dictionary)
    if not validation.ok:
        print("proper: no")
        for issue in validation.issues:
            print(issue.message)
        _fail("this section needs a proper dictionary")
    return parsed.dictionary


def _run_82(loaded: LoadedInput, files: list[Path]) -> None:
    _require_proper(loaded)
    _refuse_large(loaded)
    if len(files) >= 2:
        other_path = files[1]
    elif loaded.other_dictionary is not None:
        other_path = loaded.other_dictionary
    else:
        _fail("pass two dictionary files: make 8.2 left.merges right.merges")
    other = _load_other(other_path)
    if other_path.name in LARGE_DICTIONARIES or len(other) > LIVE_RULE_LIMIT:
        _fail(f"{other_path.name} is too large to build live")
    texts = loaded.texts
    if not texts:
        _fail("add a '# text: ...' line to the first file, or pass TEXT=...")
    print("8.2 dictionary equivalence")
    print(f"left: {loaded.path}")
    print(f"right: {other_path}")
    result = compare_dictionaries_bounded(
        loaded.dictionary, other, texts, check_token_dfa=True
    )
    shown = ", ".join(text.decode("utf-8") if text else "ε" for text in texts)
    print(f"inputs: {shown}")
    print(f"equivalent: {'yes' if result.equivalent else 'no'}")
    print(f"reference_agrees: {result.reference_agrees}")
    print(f"dfa_agrees: {result.dfa_agrees}")
    if result.counterexample is None:
        print("counterexample: none")
    else:
        print(f"counterexample: {result.counterexample.decode('utf-8')}")
    if result.left_tokens is not None and result.right_tokens is not None:
        print(f"left_tokens: {_sequence(result.left_tokens)}")
        print(f"right_tokens: {_sequence(result.right_tokens)}")
    if result.dfa_witness is None:
        print("dfa_witness: none")
    else:
        print(f"dfa_witness: {_sequence(result.dfa_witness)}")


def _run_86(loaded: LoadedInput) -> None:
    _refuse_large(loaded)
    if not loaded.texts:
        _fail("add a '# text: ...' line to the input file, or pass TEXT=...")
    print("8.6 partial order")
    print(f"file: {loaded.path}")
    order = OrderedRules(loaded.dictionary.rules, precedes=loaded.precedes)
    try:
        result = check_linear_extensions(order, loaded.texts)
    except ValueError as error:
        _fail(str(error))
    print(f"disjoint_class: {_flag(result.disjoint_class)}")
    if loaded.precedes:
        shown = ", ".join(
            f"{earlier} before {later}" for earlier, later in loaded.precedes
        )
        print(f"precedes: {shown}")
    else:
        print("precedes: none")
    print(f"extensions: {len(result.extensions)}")
    for index, extension in enumerate(result.extensions):
        rules = ", ".join(_rule(rule.left, rule.right) for rule in extension.rules)
        print(f"  {index}: {rules}")
    if len(result.extensions) == 1:
        print("one extension: not commutation evidence")
    print(f"extensions_agree: {_flag(result.extensions_agree)}")
    print(f"dfa_agrees: {_flag(result.dfa_agrees)}")
    inputs = ", ".join(text.decode("utf-8") if text else "ε" for text in loaded.texts)
    print(f"inputs: {inputs}")
    if result.counterexample_input is None:
        print("counterexample: none")
    else:
        print(f"counterexample: {result.counterexample_input.decode('utf-8')}")
    if result.left_tokens is not None and result.right_tokens is not None:
        print(f"left_extension: {result.left_extension}")
        print(f"left_tokens: {_sequence(result.left_tokens)}")
        print(f"right_extension: {result.right_extension}")
        print(f"right_tokens: {_sequence(result.right_tokens)}")
    if result.dfa_witness is None:
        print("dfa_witness: none")
    else:
        print(f"dfa_witness: {_sequence(result.dfa_witness)}")
    if result.improper_extension is None:
        print("improper_extension: none")
    else:
        rules = ", ".join(
            _rule(rule.left, rule.right) for rule in result.improper_extension.rules
        )
        print(f"improper_extension: {rules}")
    if result.state_counts is None:
        print("state_counts: none")
    else:
        print(f"state_counts: {', '.join(str(count) for count in result.state_counts)}")


def _run_811(loaded: LoadedInput) -> None:
    _require_proper(loaded)
    _refuse_large(loaded)
    text = _require_text(loaded)
    if not loaded.pattern:
        _fail("add a '# pattern: ...' line, or pass PATTERN=...")
    print("8.11 pattern matching")
    print(f"file: {loaded.path}")
    sequence = tokenize_reference(loaded.dictionary, text)
    pattern_sequence = tokenize_reference(
        loaded.dictionary, loaded.pattern.encode("utf-8")
    )
    print(f"tokens: {_sequence(sequence)}")
    print(f"pattern: {_sequence(pattern_sequence)}")
    alphabet = _alphabet(loaded.dictionary, loaded.texts)
    dfa = construct_token_dfa(loaded.dictionary, universal_token_dfa(alphabet)).final
    token_matches = TokenPatternMatcher((pattern_sequence,)).find_canonical(
        sequence, dfa
    )
    byte_matches = match_bytes(text, (loaded.pattern.encode("utf-8"),))
    token_text = (
        ", ".join(f"[{item.start},{item.end})" for item in token_matches) or "none"
    )
    byte_text = (
        ", ".join(f"[{item.start},{item.end})" for item in byte_matches) or "none"
    )
    print(f"token_matches: {token_text}")
    print(f"byte_matches: {byte_text}")


def main() -> None:
    args = _parser().parse_args()
    section = ALIASES[args.section]
    try:
        if section == "6":
            _run_6()
        elif section == "7":
            _run_7()
        elif section == "5.6" and not args.files:
            _run_56(None)
        else:
            if not args.files:
                _fail("pass an input file, for example: make 5.1 live.merges")
            loaded = _load(args.files[0], args.text, args.pattern)
            if section == "5.1":
                _run_51(loaded)
            elif section == "5.2":
                _run_52(loaded)
            elif section == "5.3":
                _run_53(loaded)
            elif section == "5.4":
                _run_54(loaded)
            elif section == "5.5":
                _run_55(loaded)
            elif section == "5.6":
                _run_56(loaded)
            elif section == "8.2":
                _run_82(loaded, args.files)
            elif section == "8.6":
                _run_86(loaded)
            elif section == "8.11":
                _run_811(loaded)
    except ImproperDictionaryError as error:
        _fail(str(error))


if __name__ == "__main__":
    main()
