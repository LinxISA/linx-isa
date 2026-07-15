#!/usr/bin/env python3
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_BUILD_SCRIPT = ROOT / "tools" / "build_linx_llvm_cpp_runtimes.sh"


class RuntimeBuildScriptTest(unittest.TestCase):
    def test_linux_uapi_helper_rename_is_complete(self) -> None:
        script = RUNTIME_BUILD_SCRIPT.read_text(encoding="utf-8")

        legacy_calls = re.findall(r"(?m)^\s*ensure_linux_compat_headers\s*$", script)
        current_calls = re.findall(r"(?m)^\s*install_linux_uapi_headers\s*$", script)

        self.assertEqual(legacy_calls, [], "legacy helper call survived the rename")
        self.assertEqual(
            len(current_calls),
            2,
            "Linux UAPI headers must be installed before configure and after sysroot merge",
        )


if __name__ == "__main__":
    unittest.main()
