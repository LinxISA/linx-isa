#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_pto_cube_system


class PtoCubeSystemTests(unittest.TestCase):
    def test_runtime_requires_every_case_and_clean_shutdown(self) -> None:
        lines = ["PTO_CUBE_START count=6"]
        lines.extend(
            f"PTO_CUBE_CASE_PASS {name} value=0"
            for name in run_pto_cube_system.CUBE_CASES
        )
        lines.extend(["PTO_CUBE_PASS count=6", "LINX_REBOOT lisc_shutdown"])
        self.assertEqual(
            run_pto_cube_system._classify_runtime("\n".join(lines), 0, False),
            (True, "runtime_pass", "all 6 cases passed and powered off"),
        )

    def test_case_failure_is_first_class(self) -> None:
        self.assertEqual(
            run_pto_cube_system._classify_runtime(
                "PTO_CUBE_START count=6\nPTO_CUBE_CASE_FAIL_EXIT case value=4\n",
                0,
                False,
            ),
            (False, "runtime_case_failure", "PTO_CUBE_CASE_FAIL_EXIT case value=4"),
        )

    def test_pre_pid1_breakpoint_is_not_reported_as_timeout(self) -> None:
        line = "Linx: EBREAK trap imm=0 acr=0 at PC=0x6050ca (LINX_SEMIHOST=0)"
        self.assertEqual(
            run_pto_cube_system._classify_runtime(line, -15, False),
            (False, "runtime_kernel_breakpoint", line),
        )

    def test_timeout_reports_completed_case_count(self) -> None:
        text = "\n".join(
            ["PTO_CUBE_START count=6"]
            + [
                f"PTO_CUBE_CASE_PASS {name} value=0"
                for name in run_pto_cube_system.CUBE_CASES[:2]
            ]
        )
        self.assertEqual(
            run_pto_cube_system._classify_runtime(text, 124, True),
            (False, "runtime_timeout", "timeout: start=True case_passes=2 pass=False"),
        )

    def test_initramfs_packages_exact_six_and_runtime_aliases(self) -> None:
        elves = [Path("/build") / f"{name}.elf" for name in run_pto_cube_system.CUBE_CASES]
        lines = run_pto_cube_system._initramfs_lines(
            Path("/build/init"), elves, Path("/sysroot/lib/libc.so")
        )
        self.assertEqual(sum(line.startswith("file /pto_cube/") for line in lines), 6)
        self.assertIn("file /lib/libm.so /sysroot/lib/libc.so 0755 0 0", lines)
        self.assertIn(
            "file /lib/ld-musl-linx64.so.1 /sysroot/lib/libc.so 0755 0 0",
            lines,
        )

    def test_nonempty_build_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "stale").write_text("stale", encoding="utf-8")
            with self.assertRaisesRegex(run_pto_cube_system.GateError, "absent or empty"):
                run_pto_cube_system._require_empty_output(root)


if __name__ == "__main__":
    unittest.main()
