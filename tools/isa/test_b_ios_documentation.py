#!/usr/bin/env python3
"""Regression checks for the bilingual B.IOS mnemonic reference."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def require_tokens(path: Path, tokens: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        assert token in text, f"{path.relative_to(ROOT)} is missing {token!r}"


def main() -> int:
    catalog = json.loads((ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8"))
    records = [entry for entry in catalog["instructions"] if entry["mnemonic"] == "B.IOS"]
    assert len(records) == 1, "the v0.58 catalog must contain exactly one B.IOS record"
    record = records[0]
    assert len(record["encoding"]["parts"]) == 1
    encoding = record["encoding"]["parts"][0]
    assert encoding["mask"] == "0xf00871ff"
    assert encoding["match"] == "0x00001013"

    syntax = (
        "B.IOS S<SharedTID>, mask=<PE_MASK>",
        "B.IOS mask=<PE_MASK>, ->S<SharedTID><TSize>",
    )
    common = syntax + (
        "S0",
        "S255",
        "PE_MASK=0000",
        "TSize=0",
        "TSize=7",
        "0xf00871ff",
        "0x00001013",
    )
    require_tokens(
        ROOT / "docs/isa/header/B.IOS.md",
        common + ("strict no-op", "atomic", "descriptor", "undefined"),
    )
    require_tokens(
        ROOT / "docs/zh/isa/header/B.IOS.md",
        common + ("严格 NOP", "原子", "描述符", "未初始化"),
    )
    assert (ROOT / "docs/zh/isa/wavedrom/enc_b_ios.svg").is_file()

    for nav in (ROOT / "mkdocs.yml", ROOT / "mkdocs.zh.yml"):
        require_tokens(nav, ("isa/header/B.IOS.md",))

    language_map = json.loads((ROOT / "docs/zh/assets/lang-map.json").read_text(encoding="utf-8"))
    assert language_map["/isa/header/B.IOS/"] == "/zh/isa/header/B.IOS/"
    assert language_map["/zh/isa/header/B.IOS/"] == "/isa/header/B.IOS/"

    print("ok: B.IOS has one bilingual, catalog-bound mnemonic reference")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
