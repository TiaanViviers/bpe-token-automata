"""Property-based tests for the subsequential tokenizer (spec §6.4)."""

from hypothesis import given, note, seed, settings
from hypothesis import strategies as st

from bpe_token_automata.automaton import (
    construct_compact_token_dfa,
    construct_token_dfa,
    languages_agree,
    universal_token_dfa,
)
from bpe_token_automata.dictionary.model import Dictionary, MergeRule
from bpe_token_automata.reference_tokenizer import tokenize_reference
from bpe_token_automata.transducer import compile_tokenizer, tokenize
from differential import assert_unique_tokenization
from hypothesis_log import (
    HYPOTHESIS_SEED,
    example_note,
    record_example,
    write_failure_log,
)

ALPHABET_BYTES = (b"a", b"b", b"c")


@st.composite
def proper_dictionaries(draw: st.DrawFn) -> tuple[Dictionary, frozenset[bytes]]:
    symbols = draw(
        st.lists(
            st.sampled_from(ALPHABET_BYTES),
            min_size=1,
            max_size=3,
            unique=True,
        )
    )
    alphabet = frozenset(symbols)
    tokens = list(symbols)
    n_rules = draw(st.integers(min_value=0, max_value=3))
    rules: list[MergeRule] = []
    seen: set[tuple[bytes, bytes]] = set()
    for _index in range(n_rules):
        left = draw(st.sampled_from(tokens))
        right = draw(st.sampled_from(tokens))
        pair = (left, right)
        if pair in seen or len(left) + len(right) > 6:
            continue
        seen.add(pair)
        rules.append(MergeRule(left=left, right=right, index=len(rules)))
        merged = left + right
        if merged not in tokens:
            tokens.append(merged)
    return Dictionary(tuple(rules)), alphabet


@st.composite
def dictionary_and_text(
    draw: st.DrawFn,
) -> tuple[Dictionary, frozenset[bytes], bytes]:
    dictionary, alphabet = draw(proper_dictionaries())
    symbols = tuple(sorted(alphabet))
    parts = draw(st.lists(st.sampled_from(symbols), min_size=0, max_size=6))
    text = b"".join(parts)
    return dictionary, alphabet, text


@seed(HYPOTHESIS_SEED)
@settings(derandomize=True, max_examples=40, deadline=None, print_blob=True)
@given(dictionary_and_text())
def test_random_proper_dictionary_agrees_with_oracle(
    payload: tuple[Dictionary, frozenset[bytes], bytes],
) -> None:
    dictionary, alphabet, text = payload
    recorded = record_example(dictionary, alphabet, text)
    note(example_note(recorded))
    try:
        base = universal_token_dfa(alphabet)
        dfa = construct_token_dfa(dictionary, base).final
        machine = compile_tokenizer(dictionary, base)
        output = tokenize(machine, text)
        expected = tokenize_reference(dictionary, text)
        assert output == expected
        assert output.detokenize() == text
        assert dfa.accepts(output)
        assert tokenize(machine, output.detokenize()) == output
        assert tokenize_reference(dictionary, expected.detokenize()) == expected
        compact = construct_compact_token_dfa(dictionary, base).final
        assert compact.accepts(output) == dfa.accepts(output)
        assert languages_agree(dfa, compact)
        assert_unique_tokenization(dfa, dictionary, text, output)
    except Exception as exc:
        write_failure_log(error=repr(exc))
        raise
