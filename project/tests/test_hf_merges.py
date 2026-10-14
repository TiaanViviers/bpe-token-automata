"""Unit tests for Hugging Face merge-list conversion (no network)."""

import pytest
from experiments.hf_merges import (
    HfMergesError,
    convert_hf_merges,
    decode_hf_token,
    format_merge_token,
    gpt2_bytes_to_unicode,
    gpt2_unicode_to_byte,
)

from bpe_token_automata.dictionary import parse_merge_list


def test_gpt2_mapping_is_a_256_byte_bijection() -> None:
    forward = gpt2_bytes_to_unicode()
    inverse = gpt2_unicode_to_byte()
    assert set(forward) == set(range(256))
    assert len(forward) == 256
    assert len(set(forward.values())) == 256
    assert inverse[forward[0x20]] == 0x20
    assert forward[0x20] == "Ġ"
    for byte, character in forward.items():
        assert inverse[character] == byte


def test_convert_gpt2_style_first_lines() -> None:
    text = "#version: 0.2\n\nĠ t\nĠ a\nh e\nĠt he\n"
    converted = convert_hf_merges(text)
    assert converted.splitlines() == [r"\x20 t", r"\x20 a", "h e", r"\x20\x74 he"]
    parsed = parse_merge_list(converted)
    assert parsed.ok
    assert parsed.dictionary is not None
    rules = parsed.dictionary.rules
    assert rules[0].left == b" "
    assert rules[0].right == b"t"
    assert rules[2].left == b"h"
    assert rules[2].right == b"e"
    assert rules[3].left == b" t"
    assert rules[3].right == b"he"


def test_hash_byte_is_hex_escaped_so_it_is_not_a_comment() -> None:
    token = decode_hf_token("#")
    assert token == b"#"
    assert format_merge_token(token) == r"\x23"
    converted = convert_hf_merges("#version: 0.2\n# t\n")
    parsed = parse_merge_list(converted)
    assert parsed.ok
    assert parsed.dictionary is not None
    assert parsed.dictionary.rules[0].left == b"#"
    assert parsed.dictionary.rules[0].right == b"t"


def test_unmapped_character_raises() -> None:
    with pytest.raises(HfMergesError, match="not in the GPT-2"):
        decode_hf_token("\ufffd")


def test_wrong_arity_line_raises() -> None:
    with pytest.raises(HfMergesError, match="expected two tokens"):
        convert_hf_merges("onlyone\n")


def test_empty_hf_token_raises() -> None:
    with pytest.raises(HfMergesError, match="must not be empty"):
        decode_hf_token("")
