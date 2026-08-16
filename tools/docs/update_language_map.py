#!/usr/bin/env python3
"""Generate symmetric routes for mirrored English and Chinese Markdown pages."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ISA_MANUAL_EXCLUDES = {".bundle", "build", "vendor"}


def _excluded(rel: Path) -> bool:
    if rel.parts and rel.parts[0] == "archive":
        return True
    return (
        len(rel.parts) >= 3
        and rel.parts[:2] == ("architecture", "isa-manual")
        and rel.parts[2] in ISA_MANUAL_EXCLUDES
    )


def _route(rel: Path) -> str:
    if rel == Path("index.md"):
        return "/"
    if rel.name == "index.md":
        return f"/{rel.parent.as_posix()}/"
    return f"/{rel.with_suffix('').as_posix()}/"


def build(root: Path) -> dict[str, str]:
    docs = root / "docs"
    zh = docs / "zh"
    mapping: dict[str, str] = {}
    for translated in sorted(zh.rglob("*.md")):
        rel = translated.relative_to(zh)
        if _excluded(rel) or not (docs / rel).is_file():
            continue
        english_route = _route(rel)
        chinese_route = "/zh/" if english_route == "/" else f"/zh{english_route}"
        mapping[english_route] = chinese_route
        mapping[chinese_route] = english_route
    return dict(sorted(mapping.items()))


def render(mapping: dict[str, str]) -> str:
    return json.dumps(mapping, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("docs/zh/assets/lang-map.json"),
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    rendered = render(build(root))
    if args.check:
        if not manifest.is_file() or manifest.read_text(encoding="utf-8") != rendered:
            print(f"error: stale language map: {manifest}", file=sys.stderr)
            return 2
        print("OK")
        return 0
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
