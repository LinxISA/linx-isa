#!/usr/bin/env python3
"""Build per-owner Chinese Tile semantics from the pinned PTO 0.59.1 reader."""

from __future__ import annotations
import argparse, json, re
from pathlib import Path
from build_manual_semantics_zh import ROLES, _git, _section

ROOT = Path(__file__).resolve().parents[2]
READER = ROOT / "docs/architecture/isa-manual/reference/data/manual-reader-zh.json"
ENGLISH = (
    ROOT / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
)
OUTPUT = (
    ROOT / "docs/architecture/isa-manual/reference/data/manual-tile-semantics-zh.json"
)
COMMIT = "a89a53d48f5708328be609fe2e6296ac8bdb4bc2"


def build(pto_root: Path) -> dict:
    if _git(pto_root, "rev-parse", "HEAD").strip() != COMMIT:
        raise ValueError("PTO checkout is not the pinned 0.59.1 source commit")
    reader = json.loads(READER.read_text(encoding="utf-8"))["records"]
    english = {
        row["mnemonic"]: row
        for row in json.loads(ENGLISH.read_text(encoding="utf-8"))["operations"]
    }
    operations = {}
    for source_path, record in reader.items():
        tile_ids = [
            value for value in record["identities"] if value.startswith("tile:")
        ]
        if not tile_ids:
            continue
        if len(tile_ids) != 1:
            raise ValueError(f"ambiguous Tile identity: {source_path}")
        name = tile_ids[0].rsplit(":", 1)[-1]
        owner = english.get(name)
        if owner is None or owner["source_path"] != source_path:
            raise ValueError(f"Tile owner mismatch for {name}")
        first = _git(pto_root, "show", f"{COMMIT}:{source_path}").splitlines()[0]
        if not first.startswith("// PTO-INSTRUCTION: "):
            raise ValueError(f"missing ASL metadata: {source_path}")
        asl = json.loads(first.split(": ", 1)[1])
        if (
            asl["mnemonic"] != name
            or asl["contract"] != owner["contract"]
            or asl["summary"] != owner["summary"]
        ):
            raise ValueError(f"English contract drift for {name}")
        markdown = _git(pto_root, "show", f"{COMMIT}:{record['reader_path']}")
        roles = {role: _section(markdown, role) for role in ROLES}
        if any(
            not any(
                re.search(r"[\u4e00-\u9fff]", statement)
                for statement in value["statements"]
            )
            for value in roles.values()
        ):
            raise ValueError(f"reader role lacks Chinese prose for {name}")
        operations[name] = {
            "mnemonic": name,
            "source_path": source_path,
            "reader_path": record["reader_path"],
            "source_commit": COMMIT,
            "roles": roles,
        }
    if len(operations) != 119:
        raise ValueError(f"expected 119 Tile Chinese owners, found {len(operations)}")
    return {
        "schema": "linxisa.manual.tile-semantics-zh.v1",
        "source_commit": COMMIT,
        "operations": dict(sorted(operations.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pto-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = (
        json.dumps(
            build(args.pto_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True
        )
        + "\n"
    )
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale Chinese Tile semantics: {OUTPUT}")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Chinese Tile semantics: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
