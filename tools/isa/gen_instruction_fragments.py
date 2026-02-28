#!/usr/bin/env python3
"""Generate per-instruction AsciiDoc fragments under docs/architecture/isa-manual/src/generated/instructions.

This is the include target referenced by the chapter files (e.g. 10_agu.adoc).

Inputs:
  - Compiled spec: isa/v*/linxisa-v*.json
  - Uop classification tree: isa/v*/uop_classification_v*/

Outputs:
  - docs/architecture/isa-manual/src/generated/instructions/*.adoc

Each fragment includes:
  - Syntax (asm)
  - Short description (best-effort)
  - Encoding SVG include
  - Uop classification (big/sub + class payload)
  - Compression kind (if length_bits==16)

NOTE: This is documentation-oriented and should not change the canonical spec.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _mkdirp(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _slug(mnemonic: str) -> str:
    s = mnemonic.strip().lower()
    s = s.replace(".", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "inst"


def _load_uop_class_map(uop_root: Path) -> Dict[str, Dict[str, Any]]:
    """Return mnemonic -> {big_kind, class, group_hint?} map."""
    out: Dict[str, Dict[str, Any]] = {}
    for p in sorted(uop_root.rglob("*.json")):
        if p.name in {"index.json", "_index.json"}:
            continue
        obj = _read_json(p)
        big = str(obj.get("big_kind") or "").strip()
        for it in obj.get("instructions", []) or []:
            m = str(it.get("mnemonic") or "").strip()
            if not m:
                continue
            rec = {
                "big_kind": big,
                "class": it.get("class") or {},
                "group": str(it.get("group") or "").strip(),
            }
            out[m] = rec
    return out


def _uop_group_str(u: Optional[Dict[str, Any]]) -> str:
    if not u:
        return "-"
    big = str(u.get("big_kind") or "").strip() or "-"
    cls = u.get("class") or {}
    # Prefer explicit AGU tuple.
    if big == "AGU":
        agu_kind = str(cls.get("agu_kind") or "").strip()
        addr_mode = str(cls.get("addr_mode") or "").strip()
        if agu_kind and addr_mode:
            return f"{agu_kind}/{addr_mode}"
        if agu_kind:
            return agu_kind
    # Else show uop_kind if present.
    uk = str(cls.get("uop_kind") or "").strip()
    if uk and uk != big:
        return f"{big}/{uk}"
    return big


def _compression_str(length_bits: int, mnemonic: str) -> str:
    if length_bits == 16 or mnemonic.startswith("C."):
        return "C16"
    if length_bits == 48 or mnemonic.startswith("HL."):
        return "HL48"
    if length_bits == 64:
        return "L64"
    return "L32"


def _inst_description(inst: Dict[str, Any]) -> str:
    # Very lightweight heuristics; keep stable.
    m = str(inst.get("mnemonic") or "").strip()
    if m.startswith("C."):
        return "Compressed instruction variant (16-bit encoding)."
    if m.startswith("HL."):
        return "Long (48-bit) instruction encoding."
    if m.startswith("V."):
        return "Vector instruction (VEC engine)."
    return "-"


def _emit_fragment(inst: Dict[str, Any], uop: Optional[Dict[str, Any]], out_dir: Path, enc_rel_dir: str) -> None:
    mnemonic = str(inst.get("mnemonic") or "").strip()
    asm = str(inst.get("asm") or "").strip()
    length_bits = int(inst.get("length_bits") or 0)

    desc = _inst_description(inst)
    uop_group = _uop_group_str(uop)
    comp = _compression_str(length_bits, mnemonic)

    enc_svg = f"enc_{_slug(mnemonic)}.svg"

    anchor = f"inst_{_slug(mnemonic)}"

    lines: List[str] = []
    lines.append("---")
    lines.append("// Auto-generated instruction documentation")
    lines.append("// Do not edit by hand")
    lines.append("")
    lines.append(f"[[{anchor}]]")
    lines.append(f"==== {mnemonic}")
    lines.append("")
    lines.append(f"*Syntax:* {asm}" if asm else "*Syntax:* -")
    lines.append("")
    lines.append(f"*Description:* {desc}")
    lines.append("")
    lines.append("*Encoding:*")
    lines.append("")
    lines.append(f"image::{enc_rel_dir}/{enc_svg}[{mnemonic} encoding,width=800]")
    lines.append("")
    lines.append(f"*Uop-Class:* {uop_group}")
    lines.append("")
    lines.append(f"*Compression:* {comp} (len={length_bits})")

    # Include the raw class dict to make the doc self-contained.
    if uop and uop.get("class"):
        cls = json.dumps(uop["class"], sort_keys=True)
        lines.append("")
        lines.append(f"*Uop-Class payload:* `{cls}`")

    out_path = out_dir / f"{_slug(mnemonic)}.adoc"
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="isa/v0.3/linxisa-v0.3.json")
    ap.add_argument("--uop-root", default="isa/v0.3/uop_classification_v0.3")
    ap.add_argument(
        "--out-dir",
        default="docs/architecture/isa-manual/src/generated/instructions",
        help="Output directory for generated per-instruction fragments",
    )
    ap.add_argument(
        "--enc-rel-dir",
        default="../generated/encodings",
        help="Relative path from instructions/ to encodings/ for image:: includes",
    )
    args = ap.parse_args()

    spec = _read_json(Path(args.spec))
    insts = list(spec.get("instructions", []))

    uop_map = _load_uop_class_map(Path(args.uop_root))

    out_dir = Path(args.out_dir)
    _mkdirp(out_dir)

    for inst in insts:
        m = str(inst.get("mnemonic") or "").strip()
        uop = uop_map.get(m)
        _emit_fragment(inst, uop, out_dir, args.enc_rel_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
