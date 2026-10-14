"""Béal–Carton subsequentialisation and Fig. 8(b)."""

import pytest

from bpe_token_automata.automaton import (
    TokenDFA,
    construct_token_dfa,
    universal_token_dfa,
)
from bpe_token_automata.dictionary import Dictionary, MergeRule
from bpe_token_automata.tokens import TokenSequence
from bpe_token_automata.transducer import (
    TransducerError,
    from_token_dfa,
    subsequentialise,
)
from bpe_token_automata.transducer.model import make_transducer


def _alphabet(*symbols: str) -> frozenset[bytes]:
    return frozenset(symbol.encode("ascii") for symbol in symbols)


def _self_merge_a1() -> TokenDFA:
    dictionary = Dictionary((MergeRule(left=b"a", right=b"a", index=0),))
    return construct_token_dfa(
        dictionary, universal_token_dfa(_alphabet("a", "b"))
    ).final


def test_empty_dictionary_subsequentialise_is_identity() -> None:
    base = universal_token_dfa(_alphabet("a", "b"))
    machine = subsequentialise(from_token_dfa(base))
    assert machine.step(machine.initial, b"a") == (
        TokenSequence((b"a",)),
        machine.initial,
    )
    assert machine.final_of(machine.initial) == TokenSequence(())


def test_fig8b_delays_odd_a_until_end_or_b() -> None:
    """Fig. 8(b) of [5] PDF p. 11: subsequential T' for D=[a⫽a]."""
    machine = subsequentialise(from_token_dfa(_self_merge_a1()))
    start = machine.initial
    emitted, after_a = machine.step(start, b"a") or (None, None)
    assert emitted == TokenSequence(())
    assert after_a is not None
    assert machine.final_of(after_a) == TokenSequence((b"a",))

    emitted_aa, after_aa = machine.step(after_a, b"a") or (None, None)
    assert emitted_aa == TokenSequence((b"aa",))
    assert after_aa == start
    assert machine.final_of(start) == TokenSequence(())

    emitted_ab, after_ab = machine.step(after_a, b"b") or (None, None)
    assert emitted_ab == TokenSequence((b"a", b"b"))
    assert after_ab == start

    emitted_b, after_b = machine.step(start, b"b") or (None, None)
    assert emitted_b == TokenSequence((b"b",))
    assert after_b == start


def test_subsequentialise_is_input_deterministic() -> None:
    machine = subsequentialise(from_token_dfa(_self_merge_a1()))
    keys = [(src, symbol) for src, symbol, _output, _dst in machine.transitions]
    assert len(keys) == len(set(keys))


def test_pending_output_cap_raises() -> None:
    transducer = from_token_dfa(_self_merge_a1())
    with pytest.raises(TransducerError, match="pending output"):
        subsequentialise(transducer, max_pending=0)


def test_state_budget_cap_raises() -> None:
    transducer = from_token_dfa(_self_merge_a1())
    with pytest.raises(TransducerError, match="state budget"):
        subsequentialise(transducer, max_states=1)


def test_conflicting_accepting_delay_raises() -> None:
    """Functionality failure: two accepting pairs with distinct delayed words."""
    empty = TokenSequence(())
    bogus = make_transducer(
        states=frozenset({0, 1, 2}),
        input_alphabet=frozenset({b"a"}),
        output_alphabet=frozenset({b"a", b"b"}),
        initial=0,
        final_output={1: empty, 2: empty},
        transitions=[
            (0, b"a", TokenSequence((b"a",)), 1),
            (0, b"a", TokenSequence((b"b",)), 2),
        ],
    )
    with pytest.raises(TransducerError, match="distinct delayed output"):
        subsequentialise(bogus)
