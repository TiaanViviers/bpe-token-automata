"""Convert Hugging Face GPT-2-style ``merges.txt`` into this project's merge lists.

Hugging Face BPE files use the GPT-2 ``bytes_to_unicode`` display encoding
(Radford et al., ``encoder.py``; tiktoken ``data_gym_to_mergeable_bpe_ranks``).
The character ``Ġ`` is byte 32 (ASCII space), not U+0120 as UTF-8 text.

Converted lines use the project merge-list syntax. Tokens are formatted like
``format_token_label``, except ``#`` (0x23) is also hex-escaped so it cannot be
parsed as a comment by ``parse_merge_list``.
"""

from __future__ import annotations

from functools import lru_cache

from bpe_token_automata.tokens import Token


class HfMergesError(ValueError):
    """Raised when a Hugging Face merge list cannot be converted."""


@lru_cache(maxsize=1)
def gpt2_bytes_to_unicode() -> dict[int, str]:
    """GPT-2 printable mapping: each byte 0–255 to one Unicode character."""
    bs = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    cs = bs[:]
    n = 0
    for byte in range(256):
        if byte not in bs:
            bs.append(byte)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, (chr(code) for code in cs), strict=True))


@lru_cache(maxsize=1)
def gpt2_unicode_to_byte() -> dict[str, int]:
    """Inverse of ``gpt2_bytes_to_unicode``."""
    return {character: byte for byte, character in gpt2_bytes_to_unicode().items()}


def decode_hf_token(literal: str) -> Token:
    """Decode one Hugging Face merge-file token into raw bytes."""
    mapping = gpt2_unicode_to_byte()
    output = bytearray()
    for character in literal:
        byte = mapping.get(character)
        if byte is None:
            raise HfMergesError(
                f"character {character!r} is not in the GPT-2 bytes_to_unicode map"
            )
        output.append(byte)
    if not output:
        raise HfMergesError("Hugging Face token literal must not be empty")
    return bytes(output)


def format_merge_token(token: Token) -> str:
    """Format a token for a ``.merges`` file (hex-escape ``#`` as well as controls)."""
    if all(
        0x21 <= byte <= 0x7E and byte not in {ord("\\"), ord("#")} for byte in token
    ):
        return token.decode("ascii")
    return "".join(f"\\x{byte:02x}" for byte in token)


def convert_hf_merges(text: str) -> str:
    """Convert a Hugging Face ``merges.txt`` body to project merge-list text."""
    lines: list[str] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#version"):
            continue
        parts = stripped.split()
        if len(parts) != 2:
            raise HfMergesError(
                f"line {line_number}: expected two tokens, got {raw_line!r}"
            )
        left = format_merge_token(decode_hf_token(parts[0]))
        right = format_merge_token(decode_hf_token(parts[1]))
        lines.append(f"{left} {right}")
    return "\n".join(lines) + ("\n" if lines else "")
