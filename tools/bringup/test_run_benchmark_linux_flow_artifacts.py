#!/usr/bin/env python3
"""Artifact contract tests for the benchmark/Linux flow runner."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_benchmark_linux_flow import run_command


class BenchmarkFlowArtifactContractTest(unittest.TestCase):
    def test_declared_artifacts_are_mapped_and_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / "command.log"
            command = {
                "id": "writes-artifacts",
                "command": "printf '{}\\n' > \"$TEST_REPORT\"; printf 'ok\\n' > \"$TEST_TRANSCRIPT\"",
                "timeout_seconds": 10,
                "artifact_env": {
                    "report": "TEST_REPORT",
                    "transcript": "TEST_TRANSCRIPT",
                },
            }

            row = run_command(
                root=root,
                stage_id="test-stage",
                command=command,
                dry_run=False,
                env={},
                log_path=log,
            )

            self.assertEqual(row["status"], "pass")
            self.assertTrue(Path(row["artifact_report"]).is_file())
            self.assertTrue(Path(row["artifact_transcript"]).is_file())

    def test_missing_declared_artifacts_turn_success_into_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            row = run_command(
                root=root,
                stage_id="test-stage",
                command={
                    "id": "missing-artifacts",
                    "command": ":",
                    "timeout_seconds": 10,
                    "artifact_env": {
                        "report": "TEST_REPORT",
                        "transcript": "TEST_TRANSCRIPT",
                    },
                },
                dry_run=False,
                env={},
                log_path=root / "command.log",
            )

            self.assertEqual(row["status"], "fail")
            self.assertEqual(row["returncode"], 3)

    def test_undeclared_commands_do_not_publish_phantom_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            row = run_command(
                root=root,
                stage_id="test-stage",
                command={"id": "plain", "command": ":", "timeout_seconds": 10},
                dry_run=False,
                env={},
                log_path=root / "command.log",
            )

            self.assertEqual(row["status"], "pass")
            self.assertIsNone(row["artifact_report"])
            self.assertIsNone(row["artifact_transcript"])


if __name__ == "__main__":
    unittest.main()
