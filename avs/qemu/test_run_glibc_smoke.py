#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import unittest
from unittest import mock

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


class GlibcSystemRuntimeTests(unittest.TestCase):
    def test_empty_pre_wrapper_timeout_is_guest_boot_timeout(self) -> None:
        result = run_glibc_smoke._classify_system_runtime(
            output="",
            timed_out=True,
            saw_pass=False,
        )

        self.assertFalse(result.ok)
        self.assertEqual(result.classification, "guest_boot_timeout")

    def test_empty_pre_wrapper_timeout_is_retried_once_then_can_pass(self) -> None:
        pass_output = "\n".join(
            ["SWRAP_INIT_START", *run_glibc_smoke.SYSTEM_PASS_MARKERS]
        )
        with mock.patch.object(
            run_glibc_smoke,
            "_run_qemu",
            side_effect=[
                ("", True, False),
                (pass_output, False, True),
            ],
        ) as run_qemu:
            result = run_glibc_smoke._run_system_runtime(["qemu"], 60)

        self.assertTrue(result.ok)
        self.assertEqual(result.classification, "runtime_pass")
        self.assertEqual(result.attempts, 2)
        self.assertEqual(run_qemu.call_count, 2)

    def test_post_wrapper_timeout_is_not_retried(self) -> None:
        with mock.patch.object(
            run_glibc_smoke,
            "_run_qemu",
            return_value=("SWRAP_INIT_START\n", True, False),
        ) as run_qemu:
            result = run_glibc_smoke._run_system_runtime(["qemu"], 60)

        self.assertFalse(result.ok)
        self.assertEqual(result.classification, "glibc_runtime_timeout")
        self.assertEqual(result.attempts, 1)
        self.assertEqual(run_qemu.call_count, 1)

    def test_repeated_pre_wrapper_timeout_stops_after_one_retry(self) -> None:
        with mock.patch.object(
            run_glibc_smoke,
            "_run_qemu",
            side_effect=[("", True, False), ("", True, False)],
        ) as run_qemu:
            result = run_glibc_smoke._run_system_runtime(["qemu"], 60)

        self.assertFalse(result.ok)
        self.assertEqual(result.classification, "guest_boot_timeout")
        self.assertEqual(result.attempts, 2)
        self.assertEqual(run_qemu.call_count, 2)


if __name__ == "__main__":
    unittest.main()
