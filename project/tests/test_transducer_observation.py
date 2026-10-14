"""Observation 3: empty dictionary and Fig. 8(a)."""

from pathlib import Path

from bpe_token_automata.automaton import construct_token_dfa, universal_token_dfa
from bpe_token_automata.dictionary import Dictionary, MergeRule, parse_dictionary_path
from bpe_token_automata.tokens import TokenSequence
from bpe_token_automata.transducer import from_token_dfa, serialize_transducer, to_dot

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dictionaries"


def _alphabet(*symbols: str) -> frozenset[bytes]:
    return frozenset(symbol.encode("ascii") for symbol in symbols)


def test_empty_dictionary_is_identity_and_subsequential() -> None:
    base = universal_token_dfa(_alphabet("a", "b"))
    transducer = from_token_dfa(base)
    assert transducer.is_subsequential()
    assert transducer.states == frozenset({0})
    assert transducer.initial == 0
    assert transducer.final_of(0) == TokenSequence(())
    assert transducer.successors(0, b"a") == ((TokenSequence((b"a",)), 0),)
    assert transducer.successors(0, b"b") == ((TokenSequence((b"b",)), 0),)


def test_fig8a_self_merge_is_input_nondeterministic() -> None:
    """Fig. 8(a) of [5] PDF p. 11: Observation 3 on A1 for D=[a⫽a]."""
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    a1 = construct_token_dfa(dictionary, universal_token_dfa(_alphabet("a", "b"))).final
    transducer = from_token_dfa(a1)

    # DFA states 0=q0, 1=q1; spelling state s1 is 2 (next unused id).
    assert transducer.states == frozenset({0, 1, 2})
    assert transducer.initial == 0
    assert transducer.accepting == frozenset({0, 1})
    assert transducer.final_of(0) == TokenSequence(())
    assert transducer.final_of(1) == TokenSequence(())
    assert transducer.final_of(2) is None
    assert not transducer.is_subsequential()

    assert set(transducer.successors(0, b"a")) == {
        (TokenSequence(()), 2),
        (TokenSequence((b"a",)), 1),
    }
    assert transducer.successors(2, b"a") == ((TokenSequence((b"aa",)), 0),)
    assert transducer.successors(0, b"b") == ((TokenSequence((b"b",)), 0),)
    assert transducer.successors(1, b"b") == ((TokenSequence((b"b",)), 0),)
    assert transducer.successors(1, b"a") == ()


def test_fig8a_serialisation_is_deterministic() -> None:
    parsed = parse_dictionary_path(DATA / "example2.merges")
    assert parsed.dictionary is not None
    first_rule = Dictionary((parsed.dictionary.rules[0],))
    a1 = construct_token_dfa(first_rule, universal_token_dfa(_alphabet("a", "b"))).final
    text = serialize_transducer(from_token_dfa(a1))
    assert text == serialize_transducer(from_token_dfa(a1))
    assert "0 --a|ε--> 2" in text
    assert "0 --a|a--> 1" in text
    assert "2 --a|aa--> 0" in text
    assert "2:" not in text.split("final_outputs:")[1].split("transitions:")[0]


def test_observation3_graphviz_mentions_epsilon() -> None:
    base = universal_token_dfa(_alphabet("a"))
    dot = to_dot(from_token_dfa(base))
    assert "a|a" in dot
    assert "init -> 0" in dot
