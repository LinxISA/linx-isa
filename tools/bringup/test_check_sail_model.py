#!/usr/bin/env python3
"""Focused regression coverage for the Sail model gate."""

from __future__ import annotations

import contextlib
import io
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import check_sail_model


class SailDirectedRunnerTest(unittest.TestCase):
    def _run_directed_with_output(
        self, output: str, *, returncode: int = 0
    ) -> tuple[bool, str, list[subprocess.CompletedProcess[str]]]:
        calls: list[subprocess.CompletedProcess[str]] = []

        def fake_run(argv, **kwargs):
            if argv == ["/opt/sail/bin/sail", "--version"]:
                return subprocess.CompletedProcess(argv, 0, stdout="Sail 0.20.2\n", stderr="")
            calls.append(kwargs)
            return subprocess.CompletedProcess(argv, returncode, stdout=output, stderr="")

        with mock.patch.object(check_sail_model.shutil, "which", return_value="/opt/sail/bin/sail"):
            with mock.patch.object(check_sail_model.subprocess, "run", side_effect=fake_run):
                ok, detail = check_sail_model._run_sail_directed_tests(Path("directed.sail"), "0.20.2")
        return ok, detail, calls

    def test_missing_directed_toolchain_is_distinct(self) -> None:
        with mock.patch.object(check_sail_model.shutil, "which", return_value=None):
            ok, detail = check_sail_model._run_sail_directed_tests(Path("directed.sail"), "0.20.2")

        self.assertFalse(ok)
        self.assertEqual(detail, "sail binary not found")

    def test_assertion_failure_is_detected_even_with_zero_exit(self) -> None:
        ok, detail, _calls = self._run_directed_with_output(
            "main()\n\033[H\033[2JError: Assertion failed: directed.sail:35.85-35.86\n"
        )

        self.assertFalse(ok)
        self.assertIn("Assertion failed: directed.sail:35.85-35.86", detail)

    def test_echoed_input_without_run_result_is_not_execution_evidence(self) -> None:
        ok, detail, calls = self._run_directed_with_output("main()\n")

        self.assertFalse(ok)
        self.assertIn("did not report successful main() execution", detail)
        self.assertEqual(calls[0]["input"], "main()\n:run\n")

    def test_semantic_success_requires_run_result(self) -> None:
        ok, detail, calls = self._run_directed_with_output("main()\n\033[H\033[2JResult = ()\n")

        self.assertTrue(ok, detail)
        self.assertIn("directed semantic tests executed", detail)
        self.assertEqual(calls[0]["input"], "main()\n:run\n")


class MainClassificationTest(unittest.TestCase):
    def test_parser_and_backend_failures_keep_their_classification(self) -> None:
        with tempfile.TemporaryDirectory(prefix="linx-sail-test-") as tmp:
            root = Path(tmp)
            spec = root / "spec.json"
            status = root / "status.json"
            toolchain = root / "toolchain.json"
            spec.write_text('{"instructions": [{"id": "addi", "mnemonic": "ADDI"}]}', encoding="utf-8")
            status.write_text(
                '{"schema_version": "linx-sail-status-v0.57.0", '
                '"forms": {"addi": {"mnemonic": "ADDI", "status": "architecturally-complete"}}}',
                encoding="utf-8",
            )
            toolchain.write_text('{"sail_version": "0.20.2"}', encoding="utf-8")
            stderr = io.StringIO()

            with mock.patch.object(check_sail_model, "_run_sail_entry", return_value=(False, "parser exploded")):
                with mock.patch.object(
                    check_sail_model, "_run_sail_c_backend", return_value=(False, "backend exploded")
                ):
                    with mock.patch.object(check_sail_model, "_run_sail_directed_tests", return_value=(True, "ok")):
                        with mock.patch.object(check_sail_model, "_check_generated_decode", return_value=(True, "ok")):
                            with mock.patch.object(
                                check_sail_model, "_check_generated_status", return_value=(True, "ok")
                            ):
                                with mock.patch.object(
                                    check_sail_model, "_check_coverage", return_value=(True, "ok")
                                ):
                                    with mock.patch.object(check_sail_model, "_collect_stale_hits", return_value=[]):
                                        with mock.patch.object(
                                            check_sail_model, "_collect_impl_gap_hits", return_value=[]
                                        ):
                                            with contextlib.redirect_stderr(stderr):
                                                rc = check_sail_model.main(
                                                    [
                                                        "--spec",
                                                        str(spec),
                                                        "--status",
                                                        str(status),
                                                        "--toolchain",
                                                        str(toolchain),
                                                        "--require-parser",
                                                        "--require-c-backend",
                                                    ]
                                                )

        self.assertEqual(rc, 1)
        errors = stderr.getvalue()
        self.assertIn("Sail parser check failed: parser exploded", errors)
        self.assertIn("Sail C backend check failed: backend exploded", errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
