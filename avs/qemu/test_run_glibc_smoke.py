#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_glibc_smoke


class GlibcRuntimeInputTests(unittest.TestCase):
    def test_explicit_kernel_overrides_legacy_build_search(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kernel = root / "fresh" / "vmlinux"
            kernel.parent.mkdir()
            kernel.write_bytes(b"fresh")

            self.assertEqual(
                run_glibc_smoke._resolve_kernel(root / "linux", str(kernel)),
                kernel.resolve(),
            )


if __name__ == "__main__":
    unittest.main()
