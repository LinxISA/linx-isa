#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


DOC_NAMES = [
    "overview.md",
    "microarchitecture.md",
    "interfaces.md",
    "verification-matrix.md",
    "module-catalog.md",
    "pipeline-stage-catalog.md",
]


def render_mirror_text(name: str, source_text: str) -> str:
    return source_text if source_text.endswith("\n") else source_text + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync published LinxCore architecture doc mirrors")
    ap.add_argument("--root", default=".", help="Superproject root")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    source_dir = root / "rtl/LinxCore/docs/architecture"
    mirror_dir = root / "docs/architecture/linxcore"
    mirror_dir.mkdir(parents=True, exist_ok=True)

    for name in DOC_NAMES:
        src = source_dir / name
        dst = mirror_dir / name
        text = src.read_text(encoding="utf-8")
        dst.write_text(render_mirror_text(name, text), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
