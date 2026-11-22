#!/usr/bin/env python3
"""Build/check the offline PTO 0.59.1 manual semantics index from ASL owners."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PIN = "a89a53d48f5708328be609fe2e6296ac8bdb4bc2"


def build(source: Path) -> dict:
    forms = {}
    for path in sorted((source / "asl").rglob("*.asl")):
        instruction = review = None
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("// PTO-INSTRUCTION: "):
                instruction = json.loads(line.split(": ", 1)[1])
            elif line.startswith("// PTO-REVIEW: "):
                review = json.loads(line.split(": ", 1)[1])
                break
        if not instruction:
            continue
        contract = instruction.get("contract", {})
        for form in instruction.get("catalog_records", []):
            form_id = form.get("form_id")
            if not form_id:
                continue
            forms[form_id] = {
                "source_path": str(path.relative_to(source)),
                "source_commit": PIN,
                "instruction_id": instruction.get("id"),
                "summary": instruction.get("summary"),
                "handler": form.get("semantic_handler"),
                "operands": contract.get("operands", []),
                "state_effects": contract.get("state_effects", []),
                "memory_effects": contract.get("memory_effects", []),
                "ordering": contract.get("ordering", []),
                "exceptions": contract.get("exceptions", []),
                "legality": contract.get("legality", []),
                "defaults": contract.get("defaults", []),
                "field_zero_meanings": contract.get("field_zero_meanings", {}),
                "review": review,
            }
    return {
        "schema": "linxisa.manual.pto-v0591-semantics.v1",
        "source_commit": PIN,
        "forms": dict(sorted(forms.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/architecture/isa-manual/reference/pto-v0591-semantics.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    head = (
        __import__("subprocess")
        .check_output(["git", "-C", args.source, "rev-parse", "HEAD"], text=True)
        .strip()
    )
    if head != PIN:
        raise SystemExit(f"error: PTO source HEAD {head} != pinned {PIN}")
    text = (
        json.dumps(build(args.source), indent=2, ensure_ascii=False, sort_keys=True)
        + "\n"
    )
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != text:
            raise SystemExit("error: manual semantics reference is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
