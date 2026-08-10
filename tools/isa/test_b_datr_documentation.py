#!/usr/bin/env python3
"""Regression checks for the B.DATR overloaded PadValue/ByteId field."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "tools/isa/gen_encoding_svg.py"

spec = importlib.util.spec_from_file_location("gen_encoding_svg", GENERATOR)
assert spec is not None and spec.loader is not None
generator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = generator
spec.loader.exec_module(generator)


def main() -> int:
    assert generator._label("PadValueOrByteId", None, 2) == "Pad/Byte"

    active_legacy = (
        ROOT / "docs/figs/bitfield/json/BlockHeader_32bit/B.DATR.json",
        ROOT / "docs/figs/bitfield/svg/BlockHeader_32bit/B.DATR.svg",
        ROOT / "docs/zh/figs/bitfield/svg/BlockHeader_32bit/B.DATR.svg",
    )
    for path in active_legacy:
        assert not path.exists(), f"legacy B.DATR encoding remains active: {path.relative_to(ROOT)}"

    archive = ROOT / "docs/archive/v0.56/figs/bitfield"
    for relative in (
        Path("json/BlockHeader_32bit/B.DATR.json"),
        Path("svg/BlockHeader_32bit/B.DATR.svg"),
    ):
        assert (archive / relative).is_file(), f"missing archived B.DATR artifact: {relative}"

    navigation = (ROOT / "docs/zh/isa/header/B.DATR.md").read_text(encoding="utf-8")
    assert "非规范导航页" in navigation
    assert "isa/v0.58/linxisa-v0.58.json" in navigation
    assert "ByteId" not in navigation
    assert "PadValue" not in navigation
    assert "figs/bitfield" not in navigation

    print("ok: B.DATR documentation uses one v0.58 owner and archives the legacy diagram")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
