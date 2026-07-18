from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).with_name("run_milepost_codelets.py")
SPEC = importlib.util.spec_from_file_location("run_milepost_codelets", MODULE_PATH)
assert SPEC and SPEC.loader
MILEPOST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MILEPOST)


class MilepostSourceDiscoveryTests(unittest.TestCase):
    def test_generated_out_tree_is_not_accepted_as_source_tree(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "out" / "milepost-codelet-stale").mkdir(parents=True)

            self.assertIsNone(MILEPOST._codelet_base_dir(root))

    def test_missing_source_tree_fails_before_runtime_build(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            clang = root / "clang"
            lld = root / "ld.lld"
            clang.touch(mode=0o755)
            lld.touch(mode=0o755)

            with mock.patch.object(MILEPOST, "_build_runtime", return_value=[]) as build_runtime:
                with self.assertRaisesRegex(SystemExit, "ctuning root does not look valid"):
                    MILEPOST.main(
                        [
                            "--ctuning-root",
                            str(root),
                            "--out-dir",
                            str(root / "results"),
                            "--target",
                            "linx64-linx-none-elf",
                            "--clang",
                            str(clang),
                            "--lld",
                            str(lld),
                            "--compile-only",
                        ]
                    )

            build_runtime.assert_not_called()


class MilepostSummaryTests(unittest.TestCase):
    def test_missing_sources_fail_the_requested_gate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            codelet = root / "program" / "milepost-codelet-missing"
            codelet.mkdir(parents=True)
            clang = root / "clang"
            lld = root / "ld.lld"
            clang.touch(mode=0o755)
            lld.touch(mode=0o755)
            summary = root / "summary.json"

            with mock.patch.object(MILEPOST, "_build_runtime", return_value=[]):
                rc = MILEPOST.main(
                    [
                        "--ctuning-root",
                        str(root),
                        "--out-dir",
                        str(root / "results"),
                        "--target",
                        "linx64-linx-none-elf",
                        "--clang",
                        str(clang),
                        "--lld",
                        str(lld),
                        "--compile-only",
                        "--summary-json",
                        str(summary),
                    ]
                )

            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(rc, 1)
            self.assertEqual(payload["selected_codelets"], 1)
            self.assertEqual(payload["passed"], 0)
            self.assertEqual(payload["failed"], 0)
            self.assertEqual(payload["skipped"], 1)
            self.assertFalse(payload["all_pass"])


if __name__ == "__main__":
    unittest.main()
