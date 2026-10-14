# Realistic BPE dictionaries (Section 5.6)

Converted Hugging Face merge lists for the compulsory larger-dictionary experiments. Raw `merges.txt` files are **not** stored in git; regenerate them with:

```bash
uv run python experiments/fetch_dictionaries.py
```

Tokens are this project's byte-level merge syntax. Hugging Face files use the GPT-2 `bytes_to_unicode` display encoding (`Ġ` is byte `0x20`). Conversion lives in `experiments/hf_merges.py`. The tokenizer constructors do not import Hugging Face or tiktoken.

| File | Source | Revision | Raw SHA-256 | Licence | Rules | Converted |
|---|---|---|---|---|---|---|
| [`gpt2.merges`](gpt2.merges) | [openai-community/gpt2](https://huggingface.co/openai-community/gpt2) `merges.txt` | `607a30d783dfa663caf39e06633721c8d4cfcd7e` | `1ce1664773c50f3e0cc8842619a93edc4624525b728b188a9e0be33b7726adc5` | MIT | 50 000 | 2026-09-14 |
| [`smollm2.merges`](smollm2.merges) | [HuggingFaceTB/SmolLM2-1.7B](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B) `merges.txt` | `effd688a12921b4cc83e3312b6feb579f70f9c71` | `0b54e8aa4e53d5383e2e4bc635a56b43f9647f7b13832d5d9ecd8f82dac4f510` | Apache-2.0 | 48 900 | 2026-09-14 |

Pinned download URLs:

- `https://huggingface.co/openai-community/gpt2/resolve/607a30d783dfa663caf39e06633721c8d4cfcd7e/merges.txt`
- `https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B/resolve/effd688a12921b4cc83e3312b6feb579f70f9c71/merges.txt`

The GPT-2 raw hash matches tiktoken's published `vocab.bpe` SHA-256. SmolLM 2 used the same `bytes_to_unicode` map (no unmapped characters). Both converted dictionaries are *proper* in the sense of Berglund & van der Merwe Definition 5.

A `#` byte is written as `\x23` so `parse_merge_list` does not treat it as a comment. Full-line `#version: 0.2` headers are skipped; later `# #` merge rules are kept.

These files are the inputs for the Section 5.6 timeout study (`uv run python experiments/timeout_study.py`). The committed summary is `experiments/results/timeout_study.json`. `make check` does not download the raw Hugging Face files and does not run that study.
