"""Small presentation wrapper for the library's BPE constructions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bpe_token_automata import (
    ImproperDictionaryError,
    TokenPatternMatcher,
    TokenSequence,
    compare_dictionaries_bounded,
    compile_tokenizer,
    construct_compact_token_dfa,
    construct_token_dfa,
    format_token_label,
    format_token_sequence,
    match_bytes,
    parse_dictionary_path,
    to_dot,
    tokenize,
    tokenize_reference,
    universal_token_dfa,
    validate_proper,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DICTIONARY = ROOT / "data" / "dictionaries" / "example2.merges"
IMPROPER_DICTIONARY = ROOT / "data" / "dictionaries" / "improper_example3.merges"
LARGE_DICTIONARIES = {"gpt2.merges", "smollm2.merges"}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "section",
        nargs="?",
        default="walkthrough",
        choices=(
            "walkthrough",
            "dict",
            "tokenize",
            "dfa",
            "compact",
            "transducer",
            "equivalence",
            "match",
        ),
    )
    parser.add_argument("--dictionary", type=Path, default=DEFAULT_DICTIONARY)
    parser.add_argument("--dictionary-b", type=Path)
    parser.add_argument("--text", action="append")
    parser.add_argument("--pattern", default="a")
    return parser


def _reject_large(path: Path) -> None:
    if path.name in LARGE_DICTIONARIES:
        raise ValueError(
            f"{path.name} is the Section 5.6 study dictionary and is too large "
            "to build live"
        )


def _parse(path: Path):
    _reject_large(path)
    result = parse_dictionary_path(path)
    if not result.ok or result.dictionary is None:
        details = "; ".join(issue.message for issue in result.issues)
        raise ValueError(f"could not parse {path}: {details}")
    return result.dictionary


def _texts(values: list[str] | None) -> tuple[bytes, ...]:
    return tuple(value.encode("utf-8") for value in (values or ["aba"]))


def _alphabet(*dictionaries, texts: tuple[bytes, ...]):
    values = {byte for text in texts for byte in text}
    for dictionary in dictionaries:
        for rule in dictionary.rules:
            values.update(rule.left)
            values.update(rule.right)
    return frozenset(bytes((value,)) for value in values)


def _print_rules(dictionary) -> None:
    print("Parsed rules:")
    for rule in dictionary.rules:
        print(
            f"  {rule.index}: {format_token_label(rule.left)} ⫽ "
            f"{format_token_label(rule.right)}"
        )
    validation = validate_proper(dictionary)
    if validation.ok:
        print("Dictionary is proper.")
    else:
        raise ImproperDictionaryError(validation.issues)


def _baseline(dictionary, text: bytes):
    base = universal_token_dfa(_alphabet(dictionary, texts=(text,)))
    return construct_token_dfa(dictionary, base).final


def _print_tokenization(dictionary, text: bytes) -> TokenSequence:
    sequence = tokenize_reference(dictionary, text)
    print(
        f'Reference tokenization T^D for "{text.decode("utf-8")}": '
        f"{format_token_sequence(sequence)}"
    )
    return sequence


def _print_dfa(dictionary, text: bytes):
    dfa = _baseline(dictionary, text)
    print(f"Baseline token DFA: {dfa.n_states} states, {dfa.n_transitions} transitions")
    print("DOT:")
    print(to_dot(dfa), end="")
    return dfa


def _run_dict(path: Path) -> None:
    dictionary = _parse(path)
    _print_rules(dictionary)


def _run_tokenize(path: Path, text: bytes) -> None:
    dictionary = _parse(path)
    _print_tokenization(dictionary, text)


def _run_dfa(path: Path, text: bytes):
    return _print_dfa(_parse(path), text)


def _run_compact(path: Path, text: bytes) -> None:
    dictionary = _parse(path)
    baseline = _baseline(dictionary, text)
    result = construct_compact_token_dfa(
        dictionary, universal_token_dfa(_alphabet(dictionary, texts=(text,)))
    )
    compact = result.final
    print(f"Baseline: {baseline.n_states} states, {baseline.n_transitions} transitions")
    print(
        "Compact: "
        f"{compact.n_states_excluding_sink} states (excluding sink), "
        f"{compact.n_transitions} transitions, {compact.n_defaults} defaults"
    )


def _run_transducer(path: Path, text: bytes) -> None:
    dictionary = _parse(path)
    reference = tokenize_reference(dictionary, text)
    machine = compile_tokenizer(
        dictionary, universal_token_dfa(_alphabet(dictionary, texts=(text,)))
    )
    result = tokenize(machine, text)
    print(f"Reference tokenization: {format_token_sequence(reference)}")
    print(f"Transducer tokenization: {format_token_sequence(result)}")
    print(f"Agrees with reference: {result == reference}")


def _run_equivalence(
    path_a: Path, path_b: Path | None, texts: tuple[bytes, ...]
) -> None:
    if path_b is None:
        raise ValueError("equivalence requires --dictionary-b PATH")
    left = _parse(path_a)
    right = _parse(path_b)
    result = compare_dictionaries_bounded(left, right, texts, check_token_dfa=True)
    print(
        f"Checked {len(result.checked_inputs)} input(s). "
        f"Equivalent: {result.equivalent}"
    )
    print(f"Reference agreement: {result.reference_agrees}")
    print(f"DFA agreement: {result.dfa_agrees}")


def _run_match(path: Path, text: bytes, pattern: str) -> None:
    dictionary = _parse(path)
    sequence = tokenize_reference(dictionary, text)
    pattern_sequence = tokenize_reference(dictionary, pattern.encode("utf-8"))
    dfa = _baseline(dictionary, text)
    token_matches = TokenPatternMatcher((pattern_sequence,)).find_canonical(
        sequence, dfa
    )
    byte_matches = match_bytes(text, (pattern.encode("utf-8"),))
    print(f"Canonical token match: {token_matches}")
    print(f"Byte baseline match: {byte_matches}")


def _walkthrough() -> None:
    dictionary = _parse(DEFAULT_DICTIONARY)
    text = b"aba"
    print("1. Dictionary")
    _print_rules(dictionary)
    print("2. Reference tokenizer")
    reference = _print_tokenization(dictionary, text)
    print("3. Baseline token DFA")
    _print_dfa(dictionary, text)
    print("4. Transducer")
    machine = compile_tokenizer(
        dictionary, universal_token_dfa(_alphabet(dictionary, texts=(text,)))
    )
    transducer_result = tokenize(machine, text)
    print(f"Transducer tokenization: {format_token_sequence(transducer_result)}")
    print(f"Agrees with reference: {transducer_result == reference}")
    print("5. Compact automaton")
    _run_compact(DEFAULT_DICTIONARY, text)
    print("6. Bounded dictionary comparison")
    comparison = compare_dictionaries_bounded(dictionary, dictionary, (text,))
    print(f"Equivalent on {text!r}: {comparison.equivalent}")
    print("7. Canonical pattern matching")
    _run_match(DEFAULT_DICTIONARY, text, "a")
    print("Deliberate validation check")
    try:
        _print_rules(_parse(IMPROPER_DICTIONARY))
    except (ImproperDictionaryError, ValueError) as error:
        print(f"{IMPROPER_DICTIONARY} is improper: {error}")


def main() -> int:
    args = _parser().parse_args()
    text_values = _texts(args.text)
    try:
        if args.section == "walkthrough":
            _walkthrough()
        elif args.section == "dict":
            _run_dict(args.dictionary)
        elif args.section == "tokenize":
            _run_tokenize(args.dictionary, text_values[-1])
        elif args.section == "dfa":
            _run_dfa(args.dictionary, text_values[-1])
        elif args.section == "compact":
            _run_compact(args.dictionary, text_values[-1])
        elif args.section == "transducer":
            _run_transducer(args.dictionary, text_values[-1])
        elif args.section == "equivalence":
            _run_equivalence(args.dictionary, args.dictionary_b, text_values)
        elif args.section == "match":
            _run_match(args.dictionary, text_values[-1], args.pattern)
    except (OSError, ValueError, ImproperDictionaryError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
