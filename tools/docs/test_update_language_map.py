#!/usr/bin/env python3
"""Tests for deterministic English/Chinese documentation route mapping."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/docs/update_language_map.py"


class LanguageMapTest(unittest.TestCase):
    def test_mirrored_pages_are_symmetric_and_generated_trees_are_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for rel in (
                "index.md",
                "isa/header/B.IOS.md",
                "archive/v0.57/old.md",
                "architecture/isa-manual/vendor/dependency.md",
            ):
                (root / "docs" / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / "docs" / "zh" / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / "docs" / rel).write_text("en\n", encoding="utf-8")
                (root / "docs" / "zh" / rel).write_text("zh\n", encoding="utf-8")

            manifest = root / "docs/zh/assets/lang-map.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("{}\n", encoding="utf-8")

            subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root)],
                check=True,
            )
            mapping = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(mapping["/"], "/zh/")
            self.assertEqual(mapping["/zh/"], "/")
            self.assertEqual(mapping["/isa/header/B.IOS/"], "/zh/isa/header/B.IOS/")
            self.assertEqual(mapping["/zh/isa/header/B.IOS/"], "/isa/header/B.IOS/")
            self.assertFalse(any("archive" in route for route in mapping))
            self.assertFalse(any("vendor" in route for route in mapping))

            subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--check"],
                check=True,
            )


if __name__ == "__main__":
    unittest.main()
