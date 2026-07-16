#!/usr/bin/env python3
"""Contract tests for the canonical benchmark QEMU/Linux flow."""
from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FLOW = ROOT / "docs" / "bringup" / "benchmark_qemu_linux_flow.json"
RUNNER = ROOT / "tools" / "bringup" / "run_benchmark_linux_flow.py"


class BenchmarkFlowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.flow = json.loads(FLOW.read_text(encoding="utf-8"))
        cls.stages = {stage["id"]: stage for stage in cls.flow["stages"]}

    def test_spec_lanes_attest_before_runtime(self) -> None:
        expected = {
            "specint-fast-gate": [
                "specint-build-static-phase-b",
                "specint-attest-static-phase-b",
                "specint-fast-test-train",
            ],
            "full-benchmarks": [
                "coremark-dhrystone",
                "specint-build-static-nightly",
                "specint-attest-static-nightly",
                "specint-nightly-test-train",
            ],
        }
        for stage_id, command_ids in expected.items():
            with self.subTest(stage=stage_id):
                self.assertEqual(
                    [command["id"] for command in self.stages[stage_id]["commands"]],
                    command_ids,
                )

    def test_source_contract_checks_linux_source_completeness(self) -> None:
        commands = self.stages["source-contract"]["commands"]
        self.assertEqual(commands[1]["id"], "linux-source-completeness")
        self.assertIn("check_linux_source_completeness.py", commands[1]["command"])

    def test_linux_stage_builds_smp_head_before_vmlinux(self) -> None:
        commands = self.stages["linux-userspace-entry"]["commands"]
        self.assertEqual(
            [command["id"] for command in commands[:2]],
            ["smp-head-clean-build", "vmlinux-clean-build"],
        )
        self.assertIn("run_linux_smp_head_build_clean.sh", commands[0]["command"])

    def test_attestation_commands_bind_build_manifest_and_verify(self) -> None:
        cases = {
            "specint-fast-gate": (
                "specint-attest-static-phase-b",
                "SPECINT_BUILD_MANIFEST",
                "SPECINT_BUILD_ATTESTATION",
            ),
            "full-benchmarks": (
                "specint-attest-static-nightly",
                "SPECINT_NIGHTLY_BUILD_MANIFEST",
                "SPECINT_NIGHTLY_BUILD_ATTESTATION",
            ),
        }
        for stage_id, (command_id, manifest_env, attestation_env) in cases.items():
            commands = {
                command["id"]: command["command"]
                for command in self.stages[stage_id]["commands"]
            }
            command = commands[command_id]
            with self.subTest(stage=stage_id):
                self.assertIn(f"${{{manifest_env}:-", command)
                self.assertIn(f"${{{attestation_env}:-", command)
                self.assertIn("check_build_manifest.py attest", command)
                self.assertIn("check_build_manifest.py verify", command)
                self.assertIn('--repo-root "$PWD"', command)
                self.assertIn('--manifest "$BUILD_MANIFEST"', command)
                self.assertIn('--attestation "$BUILD_ATTESTATION"', command)
                self.assertIn(" && ", command)

    def test_full_benchmark_stage_requires_runtime_launcher(self) -> None:
        command = next(
            row["command"]
            for row in self.stages["full-benchmarks"]["commands"]
            if row["id"] == "coremark-dhrystone"
        )
        self.assertIn('BENCHMARK_RUN_COMMAND="${LINX_BENCHMARK_RUN_COMMAND:-}"', command)
        self.assertIn('if [[ -z "$BENCHMARK_RUN_COMMAND" ]]', command)
        self.assertIn('--run-command "$BENCHMARK_RUN_COMMAND"', command)
        self.assertIn("exit 2", command)
        env = os.environ.copy()
        env.pop("LINX_BENCHMARK_RUN_COMMAND", None)
        result = subprocess.run(
            ["bash", "-c", command],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("LINX_BENCHMARK_RUN_COMMAND is required", result.stderr)

    def test_every_command_is_valid_bash_syntax(self) -> None:
        for stage in self.flow["stages"]:
            for command in stage["commands"]:
                with self.subTest(stage=stage["id"], command=command["id"]):
                    result = subprocess.run(
                        ["bash", "-n", "-c", command["command"]],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_dry_run_does_not_require_a_qemu_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            report = Path(td) / "report.json"
            env = os.environ.copy()
            env.pop("QEMU", None)
            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER),
                    "--profile",
                    "linux",
                    "--stage",
                    "specint-fast-gate",
                    "--dry-run",
                    "--report-out",
                    str(report),
                ],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(report.read_text(encoding="utf-8"))
            commands = payload["stages"][0]["commands"]
            self.assertEqual([row["status"] for row in commands], ["not_run"] * 3)
            self.assertTrue(all(row["resolved_qemu"] is None for row in commands))

    def test_timeout_kills_the_entire_command_process_group(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            child_pid = root / "child.pid"
            script = root / "spawn_child.py"
            script.write_text(
                "import pathlib, subprocess, sys, time\n"
                "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])\n"
                f"pathlib.Path({str(child_pid)!r}).write_text(str(child.pid))\n"
                "time.sleep(30)\n",
                encoding="utf-8",
            )
            flow = root / "flow.json"
            flow.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "flow_id": "process-group-timeout-test",
                        "stages": [
                            {
                                "id": "timeout",
                                "profiles": ["pr"],
                                "owner": "test",
                                "hard_break": True,
                                "commands": [
                                    {
                                        "id": "spawn",
                                        "timeout_seconds": 1,
                                        "command": f"{shlex.quote(sys.executable)} {shlex.quote(str(script))}",
                                    }
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["QEMU"] = "/bin/true"
            result = subprocess.run(
                [sys.executable, str(RUNNER), "--flow", str(flow), "--profile", "pr"],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 1)
            self.assertTrue(child_pid.is_file())
            pid = int(child_pid.read_text(encoding="utf-8"))
            alive = True
            for _ in range(50):
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    alive = False
                    break
                time.sleep(0.02)
            if alive:
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    alive = False
            self.assertFalse(alive, f"timed-out descendant still alive: {pid}")


if __name__ == "__main__":
    unittest.main()
