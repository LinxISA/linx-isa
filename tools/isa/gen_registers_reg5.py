#!/usr/bin/env python3
"""Generate the architectural reg5 table from the checked-in ISA catalog."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


_KIND_TITLES = {
    "gpr": "General-Purpose Registers (GPR)",
    "tq": "T Result Queue Registers",
    "uq": "U Result Queue Registers",
}

_DESCRIPTIONS = {
    "R0": "Constant zero",
    "R1": "Stack pointer register",
    "R2": "Function argument 0",
    "R3": "Function argument 1",
    "R4": "Function argument 2",
    "R5": "Function argument 3",
    "R6": "Function argument 4",
    "R7": "Function argument 5",
    "R8": "Function argument 6",
    "R9": "Function argument 7",
    "R10": "Function return-address register",
    "R11": "Frame pointer / callee-saved register 0",
    "R12": "Callee-saved register 1",
    "R13": "Callee-saved register 2",
    "R14": "Callee-saved register 3",
    "R15": "Callee-saved register 4",
    "R16": "Callee-saved register 5",
    "R17": "Callee-saved register 6",
    "R18": "Callee-saved register 7",
    "R19": "Callee-saved register 8",
    "R20": "Caller-saved register 0",
    "R21": "Caller-saved register 1",
    "R22": "Caller-saved register 2",
    "R23": "Caller-saved register 3",
}


def _anchor(label: str) -> str:
    return "reg5-" + re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def _description(entry: dict[str, Any]) -> str:
    name = str(entry["name"])
    if name in _DESCRIPTIONS:
        return _DESCRIPTIONS[name]
    kind = str(entry.get("kind") or "")
    if kind == "tq":
        return f"T result queue entry {name.removeprefix('T#')}"
    if kind == "uq":
        return f"U result queue entry {name.removeprefix('U#')}"
    return "Architectural five-bit register"


def render(spec_path: Path) -> tuple[str, int]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    reg5 = (spec.get("registers") or {}).get("reg5") or {}
    if int(reg5.get("bits") or 0) != 5:
        raise ValueError(f"{spec_path}: registers.reg5.bits must be 5")
    entries = reg5.get("entries")
    if not isinstance(entries, list):
        raise ValueError(f"{spec_path}: registers.reg5.entries must be a list")

    codes = [int(entry["code"]) for entry in entries]
    if sorted(codes) != list(range(32)) or len(set(codes)) != 32:
        raise ValueError(f"{spec_path}: reg5 must define each encoding 0..31 exactly once")

    resolved_parts = spec_path.resolve().parts
    try:
        isa_index = max(index for index, part in enumerate(resolved_parts) if part == "isa")
    except ValueError:
        source_label = spec_path.name
    else:
        source_label = Path(*resolved_parts[isa_index:]).as_posix()

    lines = [
        "// Generated file; do not edit by hand.",
        f"// Source: {source_label} registers.reg5",
        "",
    ]
    kinds: list[str] = []
    for entry in sorted(entries, key=lambda item: int(item["code"])):
        kind = str(entry.get("kind") or "other")
        if kind not in kinds:
            kinds.append(kind)

    for kind in kinds:
        title = _KIND_TITLES.get(kind, kind.upper())
        lines.extend(
            [
                f"[[{_anchor(title)}]]",
                f"==== {title}",
                "",
                '[cols="1,1,2,4",options="header"]',
                "|===",
                "|Code |Name |Preferred asm |Description",
                "",
            ]
        )
        for entry in sorted(entries, key=lambda item: int(item["code"])):
            if str(entry.get("kind") or "other") != kind:
                continue
            aliases = ", ".join(str(alias) for alias in entry.get("aliases", []))
            lines.extend(
                [
                    f"|`{int(entry['code'])}`",
                    f"|`{entry['name']}`",
                    f"|`{entry['asm']}`",
                    f"|{_description(entry)}  __({aliases})__",
                ]
            )
        lines.extend(["|===", ""])

    return "\n".join(lines), len(entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=Path("isa/v0.58/linxisa-v0.58.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("docs/architecture/isa-manual/src/generated"))
    parser.add_argument("--check", action="store_true", help="Compare output without writing")
    args = parser.parse_args()
    out = args.out_dir / "registers_reg5.adoc"
    rendered, count = render(args.spec)
    if args.check:
        if not out.is_file() or out.read_text(encoding="utf-8") != rendered:
            print(f"error: {out} is out of date", file=sys.stderr)
            return 2
        print("OK")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(rendered, encoding="utf-8")
    print(f"Wrote {out} ({count} architectural reg5 encodings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
