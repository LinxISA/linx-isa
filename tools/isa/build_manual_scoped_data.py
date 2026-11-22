#!/usr/bin/env python3
"""Extract reviewed Tile contracts from the exact published PTO 0.59.1 ASL."""

from __future__ import annotations
import argparse, json
from pathlib import Path

COMMIT = "a89a53d48f5708328be609fe2e6296ac8bdb4bc2"
TREE = "13807a8af41c4481ebcc88bbf33357cda8041f5d"


def build(pto_root: Path) -> dict:
    operations = []
    for path in sorted((pto_root / "asl/tile").rglob("*.asl")):
        first = path.read_text(encoding="utf-8").splitlines()[0].strip()
        if not first.startswith("// PTO-INSTRUCTION: "):
            continue
        row = json.loads(first.split(": ", 1)[1])
        rel = str(path.relative_to(pto_root))
        operations.append(
            {
                "mnemonic": row["mnemonic"],
                "id": row["id"],
                "engine": row["engine"],
                "summary": row["summary"],
                "assembly": row["assembly"],
                "block": row["block"],
                "classification": row["classification"],
                "contract": row["contract"],
                "source_path": rel,
                "source_url": f"https://github.com/PTO-ISA/pto-spec/blob/{COMMIT}/{rel}",
            }
        )
    if len(operations) != 119 or len({row["mnemonic"] for row in operations}) != 119:
        raise ValueError("published PTO source must contain 119 unique Tile operations")
    return {
        "schema": "linxisa.manual.tile-contracts.v1",
        "pto_release": "0.59.1",
        "pto_publication": "v0.59.1.0",
        "source_commit": COMMIT,
        "source_tree": TREE,
        "operation_count": 119,
        "operations": operations,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pto-root", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
        ),
    )
    args = parser.parse_args()
    args.out.write_text(
        json.dumps(build(args.pto_root.resolve()), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
