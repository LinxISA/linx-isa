#!/usr/bin/env python3
"""Record or verify per-page English-source hashes for the Chinese mirror."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(root: Path, manifest_path: Path) -> dict[str, Any]:
    docs = root / "docs"
    zh = docs / "zh"
    existing = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing.pop("pages", None)
    existing.pop("translation_only_pages", None)

    pages: dict[str, dict[str, str]] = {}
    translation_only: list[str] = []
    for translated in sorted(zh.rglob("*.md")):
        rel = translated.relative_to(zh).as_posix()
        source = docs / rel
        if not source.is_file():
            translation_only.append(rel)
            continue
        pages[rel] = {
            "source_sha256": _sha256(source),
            "translation_sha256": _sha256(translated),
        }

    existing["pages"] = pages
    existing["translation_only_pages"] = translation_only
    return existing


def render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--manifest", type=Path, default=Path("docs/zh/translation-manifest.json"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    rendered = render(build(root, manifest))
    if args.check:
        if manifest.read_text(encoding="utf-8") != rendered:
            print(f"error: stale translation freshness metadata: {manifest}", file=sys.stderr)
            return 2
        print("OK")
        return 0
    manifest.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
