#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_glibc_smoke


def _qemu_result(
    output: str,
    *,
    timed_out: bool,
    saw_pass: bool,
    returncode: int | None,
    termination: str,
) -> SimpleNamespace:
    return SimpleNamespace(
        output=output,
        timed_out=timed_out,
        saw_pass=saw_pass,
        returncode=returncode,
        termination=termination,
    )


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
                _qemu_result(
                    "",
                    timed_out=True,
                    saw_pass=False,
                    returncode=-9,
                    termination="timeout",
                ),
                _qemu_result(
                    pass_output,
                    timed_out=False,
                    saw_pass=True,
                    returncode=-9,
                    termination="pass_marker",
                ),
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
            return_value=_qemu_result(
                "SWRAP_INIT_START\n",
                timed_out=True,
                saw_pass=False,
                returncode=-9,
                termination="timeout",
            ),
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
            side_effect=[
                _qemu_result(
                    "",
                    timed_out=True,
                    saw_pass=False,
                    returncode=-9,
                    termination="timeout",
                ),
                _qemu_result(
                    "",
                    timed_out=True,
                    saw_pass=False,
                    returncode=-9,
                    termination="timeout",
                ),
            ],
        ) as run_qemu:
            result = run_glibc_smoke._run_system_runtime(["qemu"], 60)

        self.assertFalse(result.ok)
        self.assertEqual(result.classification, "guest_boot_timeout")
        self.assertEqual(result.attempts, 2)
        self.assertEqual(run_qemu.call_count, 2)

    def test_nonempty_pre_wrapper_timeout_is_retried_once(self) -> None:
        pass_output = "\n".join(
            ["SWRAP_INIT_START", *run_glibc_smoke.SYSTEM_PASS_MARKERS]
        )
        with mock.patch.object(
            run_glibc_smoke,
            "_run_qemu",
            side_effect=[
                _qemu_result(
                    "early kernel output\n",
                    timed_out=True,
                    saw_pass=False,
                    returncode=-9,
                    termination="timeout",
                ),
                _qemu_result(
                    pass_output,
                    timed_out=False,
                    saw_pass=True,
                    returncode=-9,
                    termination="pass_marker",
                ),
            ],
        ) as run_qemu:
            result = run_glibc_smoke._run_system_runtime(["qemu"], 60)

        self.assertTrue(result.ok)
        self.assertEqual(result.classification, "runtime_pass")
        self.assertEqual(result.attempts, 2)
        self.assertEqual(run_qemu.call_count, 2)

    def test_failure_marker_is_not_hidden_by_timeout_or_retry(self) -> None:
        with mock.patch.object(
            run_glibc_smoke,
            "_run_qemu",
            return_value=_qemu_result(
                "LINX_USER_TRAP addr=0\n",
                timed_out=True,
                saw_pass=False,
                returncode=-9,
                termination="timeout",
            ),
        ) as run_qemu:
            result = run_glibc_smoke._run_system_runtime(["qemu"], 60)

        self.assertFalse(result.ok)
        self.assertEqual(result.classification, "glibc_runtime_failure_marker")
        self.assertEqual(result.failure_marker, "LINX_USER_TRAP")
        self.assertEqual(result.returncode, -9)
        self.assertEqual(result.termination, "timeout")
        self.assertEqual(result.attempts, 1)
        self.assertEqual(run_qemu.call_count, 1)

    def test_natural_nonzero_exit_is_not_hidden_by_retry(self) -> None:
        with mock.patch.object(
            run_glibc_smoke,
            "_run_qemu",
            return_value=_qemu_result(
                "qemu: fatal startup error\n",
                timed_out=True,
                saw_pass=False,
                returncode=7,
                termination="natural_exit",
            ),
        ) as run_qemu:
            result = run_glibc_smoke._run_system_runtime(["qemu"], 60)

        self.assertFalse(result.ok)
        self.assertEqual(result.classification, "qemu_exit_failure")
        self.assertEqual(result.returncode, 7)
        self.assertEqual(result.termination, "natural_exit")
        self.assertEqual(result.attempts, 1)
        self.assertEqual(run_qemu.call_count, 1)

        self.assertEqual(
            run_glibc_smoke._system_runtime_summary(result),
            {
                "ok": False,
                "classification": "qemu_exit_failure",
                "attempts": 1,
                "returncode": 7,
                "termination": "natural_exit",
                "failure_marker": None,
            },
        )

    def test_deadline_race_with_positive_exit_is_not_retried_as_timeout(self) -> None:
        with mock.patch.object(
            run_glibc_smoke,
            "_run_qemu",
            return_value=_qemu_result(
                "qemu: fatal startup error\n",
                timed_out=True,
                saw_pass=False,
                returncode=7,
                termination="timeout",
            ),
        ) as run_qemu:
            result = run_glibc_smoke._run_system_runtime(["qemu"], 60)

        self.assertFalse(result.ok)
        self.assertEqual(result.classification, "qemu_exit_failure")
        self.assertEqual(result.returncode, 7)
        self.assertEqual(result.termination, "natural_exit")
        self.assertEqual(result.attempts, 1)
        self.assertEqual(run_qemu.call_count, 1)


if __name__ == "__main__":
    unittest.main()
