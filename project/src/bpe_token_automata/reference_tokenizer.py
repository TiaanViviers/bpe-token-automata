"""Independent reference BPE tokenizer (SentencePiece semantics T^D)."""

from __future__ import annotations

from bpe_token_automata.dictionary.errors import ImproperDictionaryError
from bpe_token_automata.dictionary.model import Dictionary, MergeRule
from bpe_token_automata.dictionary.validator import validate_proper
from bpe_token_automata.tokens import Token, TokenSequence


def _find_best_merge(
    tokens: list[Token],
    dictionary: Dictionary,
) -> tuple[int, MergeRule] | None:
    """Return the leftmost pair matching the highest-priority applicable rule."""
    for rule in dictionary.rules:
        for position in range(len(tokens) - 1):
            if tokens[position] == rule.left and tokens[position + 1] == rule.right:
                return position, rule
    return None


def tokenize_reference(dictionary: Dictionary, text: bytes) -> TokenSequence:
    """Tokenize using Definition 3 (highest priority, then leftmost each step)."""
    validation = validate_proper(dictionary)
    if not validation.ok:
        raise ImproperDictionaryError(validation.issues)

    tokens = list(TokenSequence.from_bytes(text).tokens)

    while True:
        merge = _find_best_merge(tokens, dictionary)
        if merge is None:
            break
        position, rule = merge
        tokens[position : position + 2] = [rule.merged]

    return TokenSequence(tuple(tokens))
