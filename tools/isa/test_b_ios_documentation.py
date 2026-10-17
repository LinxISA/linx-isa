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
    assert len(records) == 2, "PTO golden defines reuse and last-use B.IOS forms"
    record = records[0]
    assert len(record["encoding"]["parts"]) == 1
    encoding = record["encoding"]["parts"][0]
    assert encoding["mask"] == "0xfc0871ff"
    assert encoding["match"] == "0x00001013"
    fields = {
        field["name"]: field["pieces"]
        for field in encoding["fields"]
    }
    assert fields["SharedTileID"] == [
        {"insn_lsb": 20, "insn_msb": 25, "token": "SharedTileID", "width": 6}
    ]
    assert fields["SizeCode"] == [
        {"insn_lsb": 15, "insn_msb": 18, "token": "SizeCode", "width": 4}
    ]
    assert fields["PEMode"] == [
        {"insn_lsb": 9, "insn_msb": 11, "token": "PEMode", "width": 3}
    ]

    for rel in ("docs/isa/header/B.IOS.md", "docs/zh/isa/header/B.IOS.md"):
        page = ROOT / rel
        for form in records:
            require_tokens(page, (*tuple(form["asm"].split(" | ")), form["pto_source_form_id"],
                                  form["encoding"]["parts"][0]["mask"], form["encoding"]["parts"][0]["match"]))
        require_tokens(page, (".reuse", "PTO-SPEC golden", "PEMode=000"))

    for nav in (ROOT / "mkdocs.yml", ROOT / "mkdocs.zh.yml"):
        require_tokens(nav, ("isa/header/B.IOS.md",))

    language_map = json.loads((ROOT / "docs/zh/assets/lang-map.json").read_text(encoding="utf-8"))
    assert language_map["/isa/header/B.IOS/"] == "/zh/isa/header/B.IOS/"
    assert language_map["/zh/isa/header/B.IOS/"] == "/isa/header/B.IOS/"

    print("ok: B.IOS has one bilingual, catalog-bound mnemonic reference")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
