"""Paper Example 2, unary chain, serialisation, and construction stats."""

from itertools import product
from pathlib import Path

from bpe_token_automata.automaton import (
    TokenDFA,
    construct_token_dfa,
    serialize_token_dfa,
    to_dot,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import (
    Dictionary,
    parse_dictionary_path,
    parse_merge_list,
)
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.tokens import TokenSequence

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dictionaries"


def _alphabet(*symbols: str) -> frozenset[bytes]:
    return frozenset(symbol.encode("ascii") for symbol in symbols)


def _edges(dfa: TokenDFA) -> set[tuple[int, bytes, int]]:
    return set(dfa.transitions)


def test_example2_matches_figure_3() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    result = construct_token_dfa(
        parsed.dictionary,
        universal_token_dfa(_alphabet("a", "b")),
    )
    a0, a1, a2 = result.automata

    assert a0.states == frozenset({0})
    assert _edges(a0) == {(0, b"a", 0), (0, b"b", 0)}

    assert a1.states == frozenset({0, 1})
    assert a1.accepting == frozenset({0, 1})
    assert _edges(a1) == {
        (0, b"a", 1),
        (0, b"b", 0),
        (0, b"aa", 0),
        (1, b"b", 0),
    }

    assert a2.states == frozenset({0, 1, 2})
    assert a2.accepting == frozenset({0, 1, 2})
    assert _edges(a2) == {
        (0, b"aa", 0),
        (0, b"b", 2),
        (0, b"a", 1),
        (0, b"ba", 1),
        (1, b"b", 2),
        (1, b"ba", 1),
        (2, b"b", 2),
        (2, b"aa", 0),
        (2, b"ba", 1),
    }


def test_example2_merge_traces_match_paper() -> None:
    """Triples and fresh states from [5] Example 2, not from apply_merge."""
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    result = construct_token_dfa(
        parsed.dictionary,
        universal_token_dfa(_alphabet("a", "b")),
    )
    first, second = result.traces

    assert first.triples == ((0, 0, 0),)
    assert first.s2_to_fresh == ((0, 1),)
    assert first.added_uv == ((0, b"aa", 0),)
    assert first.omitted_labels == frozenset({b"a", b"aa"})
    assert first.inherited == ((1, b"b", 0),)
    assert first.redirected == ((0, b"a", 0, 1),)

    assert second.triples == ((0, 0, 1), (1, 0, 1))
    assert second.s2_to_fresh == ((0, 2),)
    assert second.added_uv == ((0, b"ba", 1), (1, b"ba", 1))
    assert second.omitted_labels == frozenset({b"a"})
    assert (2, b"ba", 1) in second.inherited
    assert (2, b"b", 0) in second.inherited
    assert second.redirected == (
        (0, b"b", 0, 2),
        (1, b"b", 0, 2),
        (2, b"b", 0, 2),
    )


def test_example2_redirects_every_b_predecessor_including_loop() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    result = construct_token_dfa(
        parsed.dictionary,
        universal_token_dfa(_alphabet("a", "b")),
    )
    redirected = result.traces[1].redirected
    assert redirected == (
        (0, b"b", 0, 2),
        (1, b"b", 0, 2),
        (2, b"b", 0, 2),
    )
    sources = {src for src, _label, _old, _new in redirected}
    assert sources == {0, 1, 2}


def test_example2_construction_stats() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    result = construct_token_dfa(
        parsed.dictionary,
        universal_token_dfa(_alphabet("a", "b")),
    )
    first, second = result.steps
    assert first.n_states == 2
    assert first.n_fresh == 1
    assert first.n_final == 2
    assert first.n_tokens == 3
    assert first.n_transitions == 4
    assert second.n_states == 3
    assert second.n_fresh == 1
    assert second.n_final == 3
    assert second.n_tokens == 4
    assert second.n_transitions == 9


def test_unary_self_merge_chain() -> None:
    parsed = parse_merge_list("a a\naa a")
    assert parsed.dictionary is not None
    result = construct_token_dfa(
        parsed.dictionary,
        universal_token_dfa(_alphabet("a")),
    )
    a0, a1, a2 = result.automata

    assert _edges(a0) == {(0, b"a", 0)}
    assert _edges(a1) == {(0, b"a", 1), (0, b"aa", 0)}
    assert a1.step(1, b"aa") is None
    assert a1.step(1, b"a") is None

    assert result.steps[1].n_fresh == 1
    assert a2.step(0, b"aa") == 2
    assert a2.step(2, b"aa") == 2
    assert a2.step(0, b"aaa") == 1
    assert a2.accepts(TokenSequence((b"aaa",)))
    assert a2.accepts(TokenSequence((b"aa", b"a"))) is False

    first, second = result.traces
    assert first.triples == ((0, 0, 0),)
    assert first.s2_to_fresh == ((0, 1),)
    assert first.omitted_labels == frozenset({b"a", b"aa"})
    assert first.inherited == ()
    assert first.redirected == ((0, b"a", 0, 1),)

    assert second.triples == ((0, 0, 1),)
    assert second.s2_to_fresh == ((0, 2),)
    assert second.added_uv == ((0, b"aaa", 1),)
    assert second.omitted_labels == frozenset({b"a"})
    assert (2, b"aa", 0) in second.inherited
    assert (2, b"aaa", 1) in second.inherited
    assert second.redirected == ((0, b"aa", 0, 2), (2, b"aa", 0, 2))


def _assert_prefix_agreement(
    dictionary: Dictionary,
    alphabet: bytes,
    automata: tuple[TokenDFA, ...],
    max_length: int,
) -> None:
    for index, dfa in enumerate(automata):
        prefix = Dictionary(dictionary.rules[:index])
        for length in range(max_length + 1):
            for symbols in product(alphabet, repeat=length):
                text = bytes(symbols)
                canonical = tokenize_reference(prefix, text)
                assert dfa.accepts(canonical)
                base = TokenSequence.from_bytes(text)
                if base.tokens != canonical.tokens:
                    assert not dfa.accepts(base)


def test_example2_each_prefix_agrees_with_reference_up_to_length_4() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    result = construct_token_dfa(
        parsed.dictionary,
        universal_token_dfa(_alphabet("a", "b")),
    )
    _assert_prefix_agreement(parsed.dictionary, b"ab", result.automata, 4)


def test_unary_each_prefix_agrees_with_reference_up_to_length_6() -> None:
    parsed = parse_merge_list("a a\naa a")
    assert parsed.dictionary is not None
    result = construct_token_dfa(
        parsed.dictionary,
        universal_token_dfa(_alphabet("a")),
    )
    _assert_prefix_agreement(parsed.dictionary, b"a", result.automata, 6)


def test_serialize_is_deterministic() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    dfa = construct_token_dfa(
        parsed.dictionary,
        universal_token_dfa(_alphabet("a", "b")),
    ).final
    first = serialize_token_dfa(dfa)
    second = serialize_token_dfa(dfa)
    assert first == second
    assert first.startswith("states: 0,1,2")
    assert "0 --a--> 1" in first


def test_graphviz_contains_accepting_and_initial() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    dfa = construct_token_dfa(
        parsed.dictionary,
        universal_token_dfa(_alphabet("a", "b")),
    ).final
    dot = to_dot(dfa)
    assert "doublecircle" in dot
    assert "init -> 0" in dot
    assert "rankdir=LR" in dot
