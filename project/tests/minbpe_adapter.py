"""minbpe BasicTokenizer encode loop with injected merge tables.

Source: Karpathy minbpe (MIT),
https://github.com/karpathy/minbpe/blob/master/minbpe/basic.py
https://github.com/karpathy/minbpe/blob/master/minbpe/base.py

The public BasicTokenizer API trains merges from a corpus. This adapter
injects an already-known proper BPE dictionary into the same merge tables
and runs the byte-level encode loop on raw bytes (the step after UTF-8
encoding in BasicTokenizer.encode). No regex pre-tokenization.
"""

from __future__ import annotations

from bpe_token_automata.dictionary.model import Dictionary
from bpe_token_automata.tokens import Token, TokenSequence


def get_stats(ids: list[int]) -> dict[tuple[int, int], int]:
    """Count consecutive pairs (minbpe.base.get_stats)."""
    counts: dict[tuple[int, int], int] = {}
    for pair in zip(ids, ids[1:], strict=False):
        counts[pair] = counts.get(pair, 0) + 1
    return counts


def merge(ids: list[int], pair: tuple[int, int], idx: int) -> list[int]:
    """Replace consecutive `pair` with `idx` (minbpe.base.merge)."""
    newids: list[int] = []
    index = 0
    while index < len(ids):
        if index < len(ids) - 1 and ids[index] == pair[0] and ids[index + 1] == pair[1]:
            newids.append(idx)
            index += 2
        else:
            newids.append(ids[index])
            index += 1
    return newids


class LoadedBasicTokenizer:
    """BasicTokenizer tables loaded from a project Dictionary, not trained."""

    def __init__(self, dictionary: Dictionary) -> None:
        self.merges: dict[tuple[int, int], int] = {}
        self.vocab: dict[int, bytes] = {idx: bytes([idx]) for idx in range(256)}
        token_to_id: dict[Token, int] = {bytes([idx]): idx for idx in range(256)}
        next_id = 256
        for rule in dictionary.rules:
            try:
                left_id = token_to_id[rule.left]
                right_id = token_to_id[rule.right]
            except KeyError as exc:
                raise ValueError(
                    "cannot inject merge: component token has no minbpe id"
                ) from exc
            self.merges[(left_id, right_id)] = next_id
            self.vocab[next_id] = rule.merged
            token_to_id[rule.merged] = next_id
            next_id += 1

    def encode_bytes(self, data: bytes) -> list[int]:
        """BasicTokenizer.encode after the UTF-8 encoding step."""
        ids = list(data)
        while len(ids) >= 2:
            stats = get_stats(ids)
            pair = min(stats, key=lambda item: self.merges.get(item, float("inf")))
            if pair not in self.merges:
                break
            ids = merge(ids, pair, self.merges[pair])
        return ids

    def token_sequence(self, data: bytes) -> TokenSequence:
        """Map encoded ids back to byte tokens for sequence comparison."""
        ids = self.encode_bytes(data)
        return TokenSequence(tuple(self.vocab[idx] for idx in ids))
