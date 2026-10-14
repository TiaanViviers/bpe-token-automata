"""Download pinned Hugging Face merge lists and convert them (optional, networked)."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "experiments" / ".cache" / "huggingface"
OUT = ROOT / "data" / "dictionaries"
USER_AGENT = "bpe-token-automata/0.1 (CS345 Stellenbosch)"


@dataclass(frozen=True, slots=True)
class Source:
    name: str
    repo: str
    revision: str
    sha256: str
    licence: str
    output_name: str
    expected_rules: int

    @property
    def url(self) -> str:
        return f"https://huggingface.co/{self.repo}/resolve/{self.revision}/merges.txt"

    @property
    def cache_path(self) -> Path:
        return CACHE / self.name / "merges.txt"

    @property
    def output_path(self) -> Path:
        return OUT / self.output_name


SOURCES: tuple[Source, ...] = (
    Source(
        name="gpt2",
        repo="openai-community/gpt2",
        revision="607a30d783dfa663caf39e06633721c8d4cfcd7e",
        sha256="1ce1664773c50f3e0cc8842619a93edc4624525b728b188a9e0be33b7726adc5",
        licence="MIT",
        output_name="gpt2.merges",
        expected_rules=50_000,
    ),
    Source(
        name="smollm2",
        repo="HuggingFaceTB/SmolLM2-1.7B",
        revision="effd688a12921b4cc83e3312b6feb579f70f9c71",
        sha256="0b54e8aa4e53d5383e2e4bc635a56b43f9647f7b13832d5d9ecd8f82dac4f510",
        licence="Apache-2.0",
        output_name="smollm2.merges",
        expected_rules=48_900,
    ),
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload: bytes = bytes(response.read())
        return payload


def load_raw(source: Source, *, allow_network: bool) -> bytes:
    cache = source.cache_path
    if cache.is_file():
        data = cache.read_bytes()
        digest = _sha256(data)
        if digest != source.sha256:
            raise SystemExit(
                f"{source.name}: cache SHA-256 {digest} != pin {source.sha256}"
            )
        return data
    if not allow_network:
        raise SystemExit(f"{source.name}: cache missing at {cache}")
    data = _download(source.url)
    digest = _sha256(data)
    if digest != source.sha256:
        raise SystemExit(
            f"{source.name}: downloaded SHA-256 {digest} != pin {source.sha256}"
        )
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(data)
    return data


def _ensure_root_on_path() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))


def convert_source(source: Source, raw: bytes) -> str:
    _ensure_root_on_path()
    from experiments.hf_merges import convert_hf_merges

    header = (
        f"# Converted from {source.repo} merges.txt\n"
        f"# revision {source.revision}\n"
        f"# raw sha256 {source.sha256}\n"
        f"# See data/dictionaries/REALISTIC.md.\n"
    )
    body = convert_hf_merges(raw.decode("utf-8"))
    n_rules = sum(1 for line in body.splitlines() if line.strip())
    if n_rules != source.expected_rules:
        raise SystemExit(
            f"{source.name}: converted {n_rules} rules, "
            f"expected {source.expected_rules}"
        )
    return header + body


def main() -> None:
    allow_network = "--offline" not in sys.argv
    CACHE.mkdir(parents=True, exist_ok=True)
    summary: list[dict[str, str | int]] = []
    for source in SOURCES:
        raw = load_raw(source, allow_network=allow_network)
        converted = convert_source(source, raw)
        source.output_path.write_text(converted, encoding="utf-8")
        summary.append(
            {
                "name": source.name,
                "url": source.url,
                "revision": source.revision,
                "sha256": source.sha256,
                "licence": source.licence,
                "rules": source.expected_rules,
                "output": str(source.output_path.relative_to(ROOT)),
            }
        )
        print(f"wrote {source.output_path} ({source.expected_rules} rules)")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
