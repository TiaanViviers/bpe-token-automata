"""Token literal encoding for dictionary files."""

from __future__ import annotations

from bpe_token_automata.dictionary.errors import DictionaryIssue, IssueKind
from bpe_token_automata.tokens import Token


def decode_token_literal(literal: str) -> tuple[Token | None, DictionaryIssue | None]:
    """Decode a token literal: UTF-8 characters and \\xHH byte escapes."""
    if not literal:
        return None, DictionaryIssue(
            kind=IssueKind.EMPTY_TOKEN,
            message="token literal must not be empty",
        )

    output = bytearray()
    index = 0
    while index < len(literal):
        if literal[index] != "\\":
            output.extend(literal[index].encode("utf-8"))
            index += 1
            continue

        if index + 4 <= len(literal) and literal[index + 1] == "x":
            hex_digits = literal[index + 2 : index + 4]
            try:
                output.append(int(hex_digits, 16))
            except ValueError:
                return None, DictionaryIssue(
                    kind=IssueKind.UNSUPPORTED_ENCODING,
                    message=f"unsupported escape {literal[index : index + 4]!r}",
                )
            index += 4
            continue

        return None, DictionaryIssue(
            kind=IssueKind.UNSUPPORTED_ENCODING,
            message=f"unsupported escape at {literal[index:]!r}",
        )

    return bytes(output), None
