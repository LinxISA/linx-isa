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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_multi_agent_gates


ROOT = Path(__file__).resolve().parents[2]
FLOW = ROOT / "docs" / "bringup" / "benchmark_qemu_linux_flow.json"
RUNNER = ROOT / "tools" / "bringup" / "run_benchmark_linux_flow.py"
REGISTRY = ROOT / "docs" / "bringup" / "gate_registry.json"


class BenchmarkFlowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.flow = json.loads(FLOW.read_text(encoding="utf-8"))
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
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

    def test_canonical_flow_requires_head_matched_clean_qemu(self) -> None:
        self.assertTrue(self.flow["require_clean_qemu"])

    def test_compiler_contract_covers_linx64_then_linx32(self) -> None:
        commands = self.stages["compiler-contract"]["commands"]
        self.assertEqual(
            [command["id"] for command in commands],
            ["linx64-compile-coverage", "linx32-compile-coverage"],
        )
        self.assertIn("Compiler::AVS compile suites linx64", commands[0]["command"])
        self.assertIn("Compiler::Coverage 100% linx64", commands[0]["command"])
        self.assertIn("Compiler::AVS compile suites linx32", commands[1]["command"])
        self.assertIn("Compiler::Coverage 100% linx32", commands[1]["command"])

    def test_nightly_coverage_closure_precedes_expensive_runtime_lanes(self) -> None:
        stage_ids = [stage["id"] for stage in self.flow["stages"]]
        coverage_index = stage_ids.index("coverage-closure")
        self.assertGreater(coverage_index, stage_ids.index("qemu-contract"))
        for downstream in (
            "tsvc-qemu-hardbreak",
            "linux-userspace-entry",
            "specint-fast-gate",
            "full-benchmarks",
        ):
            with self.subTest(downstream=downstream):
                self.assertLess(coverage_index, stage_ids.index(downstream))

        stage = self.stages["coverage-closure"]
        self.assertEqual(stage["profiles"], ["nightly"])
        self.assertTrue(stage["hard_break"])
        commands = stage["commands"]
        self.assertEqual(
            [command["id"] for command in commands],
            [
                "llvm-c-codegen-breadth",
                "qemu-isa-l1-full",
                "qemu-translation-full",
                "isa-llvm-qemu-coherent",
            ],
        )
        self.assertIn(
            "Compiler::C-CodeGen mnemonic breadth report", commands[0]["command"]
        )
        self.assertIn(
            "Emulator::ISA vs QEMU coverage report", commands[1]["command"]
        )
        self.assertIn(
            "Emulator::AVS QEMU translation coverage report", commands[2]["command"]
        )
        self.assertIn(
            "Integration::ISA-LLVM-QEMU coverage coherence report",
            commands[3]["command"],
        )

        isa_l1_strict = "QEMU_ISA_COVERAGE_REQUIRE_FULL=1"
        translation_strict = "QEMU_TRANSLATION_COVERAGE_REQUIRE_FULL=1"
        coherence_strict = "ISA_LLVM_QEMU_COVERAGE_REQUIRE_COHERENT=1"
        for strict_variable in (
            isa_l1_strict,
            translation_strict,
            coherence_strict,
        ):
            self.assertNotIn(strict_variable, commands[0]["command"])
        self.assertIn(isa_l1_strict, commands[1]["command"])
        self.assertNotIn(translation_strict, commands[1]["command"])
        self.assertNotIn(coherence_strict, commands[1]["command"])
        self.assertNotIn(isa_l1_strict, commands[2]["command"])
        self.assertIn(translation_strict, commands[2]["command"])
        self.assertNotIn(coherence_strict, commands[2]["command"])
        self.assertNotIn(isa_l1_strict, commands[3]["command"])
        self.assertNotIn(translation_strict, commands[3]["command"])
        self.assertIn(coherence_strict, commands[3]["command"])

    def test_source_contract_checks_linux_source_completeness(self) -> None:
        commands = self.stages["source-contract"]["commands"]
        self.assertEqual(commands[1]["id"], "linux-source-completeness")
        self.assertIn("check_linux_source_completeness.py", commands[1]["command"])

    def test_flow_gate_references_are_exact_registry_keys(self) -> None:
        registry = {gate["gate_key"]: gate for gate in self.registry["gates"]}
        references = check_multi_agent_gates._flow_gate_references(self.flow)
        self.assertTrue(references)
        for reference in references:
            with self.subTest(**reference):
                self.assertIn(reference["gate_key"], registry)

    def test_flow_gate_validator_rejects_unregistered_reference(self) -> None:
        flow = json.loads(json.dumps(self.flow))
        flow["stages"][0]["commands"][2]["command"] += " --gate 'ISA::missing'"
        registry = {gate["gate_key"]: gate for gate in self.registry["gates"]}
        errors = []
        check_multi_agent_gates._validate_flow_gate_references(
            flow, registry, errors=errors
        )
        self.assertIn("E_BENCHMARK_FLOW_GATE_UNKNOWN", {row["code"] for row in errors})

    def test_tsvc_hard_break_uses_active_v058_source_policy(self) -> None:
        commands = self.stages["tsvc-qemu-hardbreak"]["commands"]
        for command in commands:
            with self.subTest(command=command["id"]):
                self.assertIn("--source-policy linx-v058", command["command"])
                self.assertNotIn("linx-v057", command["command"])

    def test_linux_stage_builds_smp_head_before_vmlinux(self) -> None:
        commands = self.stages["linux-userspace-entry"]["commands"]
        self.assertEqual(
            [command["id"] for command in commands[:2]],
            ["smp-head-clean-build", "vmlinux-clean-build"],
        )
        self.assertIn("run_linux_smp_head_build_clean.sh", commands[0]["command"])
        self.assertIn("--fresh", commands[1]["command"])
        self.assertIn("/tmp/linx-linux-vmlinux-clean-build", commands[1]["command"])
        self.assertIn('O="${LINUX_VMLINUX_OUT_DIR', commands[2]["command"])
        self.assertIn('O="${LINUX_VMLINUX_OUT_DIR', commands[3]["command"])
        self.assertIn('KERNEL="${LINUX_VMLINUX_OUT_DIR', commands[3]["command"])
        self.assertIn('KERNEL_CONFIG="${LINUX_VMLINUX_OUT_DIR', commands[3]["command"])
        self.assertIn("LINX_BUSYBOX_BOOT_RETRY=0", commands[3]["command"])
        self.assertIn("LINX_BUSYBOX_BOOT_BLIND_SEND_AFTER=0", commands[3]["command"])
        self.assertEqual(
            commands[3]["artifact_env"],
            {
                "report": "LINX_BUSYBOX_BOOT_REPORT",
                "transcript": "LINX_BUSYBOX_BOOT_TRANSCRIPT",
            },
        )

    def test_libc_runtime_reuses_one_build_and_binds_fresh_kernel_evidence(self) -> None:
        commands = self.stages["libc-hosted-runtime"]["commands"]
        self.assertEqual(
            [command["id"] for command in commands],
            [
                "musl-build-phase-b",
                "cpp-runtime-noeh-phase-b",
                "musl-runtime-both",
                "glibc-build-g1b",
                "glibc-runtime",
            ],
        )
        musl = commands[2]
        self.assertIn("--skip-build", musl["command"])
        self.assertIn("--kernel", musl["command"])
        self.assertIn("LINUX_VMLINUX_OUT_DIR", musl["command"])
        self.assertEqual(
            musl["artifact_env"],
            {
                "report": "LINX_MUSL_RUNTIME_REPORT",
                "transcript": "LINX_MUSL_RUNTIME_TRANSCRIPT",
            },
        )
        self.assertIn("GLIBC_G1B_ALLOW_BLOCKED=0", commands[3]["command"])
        glibc = commands[4]
        self.assertIn("--kernel", glibc["command"])
        self.assertIn("LINUX_VMLINUX_OUT_DIR", glibc["command"])
        self.assertEqual(
            glibc["artifact_env"],
            {
                "report": "LINX_GLIBC_RUNTIME_REPORT",
                "transcript": "LINX_GLIBC_RUNTIME_TRANSCRIPT",
            },
        )

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

    def test_spec_runtime_lanes_bind_the_fresh_kernel(self) -> None:
        cases = (
            ("specint-fast-gate", "specint-fast-test-train"),
            ("full-benchmarks", "specint-nightly-test-train"),
        )
        for stage_id, command_id in cases:
            command = next(
                row["command"]
                for row in self.stages[stage_id]["commands"]
                if row["id"] == command_id
            )
            with self.subTest(stage=stage_id):
                self.assertIn(
                    '--kernel "${LINUX_VMLINUX_OUT_DIR:-/tmp/linx-linux-vmlinux-clean-build}/vmlinux"',
                    command,
                )

    def test_full_benchmark_stage_has_attested_default_runtime_launcher(self) -> None:
        row = next(
            row
            for row in self.stages["full-benchmarks"]["commands"]
            if row["id"] == "coremark-dhrystone"
        )
        command = row["command"]
        self.assertIn('if [[ -n "${LINX_BENCHMARK_RUN_COMMAND:-}" ]]', command)
        self.assertIn("tools/bringup/run_c_benchmark_matrix.py", command)
        self.assertIn("--kernel ${LINUX_VMLINUX_OUT_DIR", command)
        self.assertIn("--qemu ${QEMU", command)
        self.assertIn("--exe {exe}", command)
        self.assertIn('--coremark-iterations "${LINX_COREMARK_ITERATIONS:-15000}"', command)
        self.assertIn('--dhrystone-runs "${LINX_DHRYSTONE_RUNS:-1}"', command)
        self.assertIn('--run-command "$BENCHMARK_RUN_COMMAND"', command)
        self.assertIn('${LINX_BENCHMARK_TRANSCRIPT:-', command)
        self.assertEqual(
            row["artifact_env"],
            {
                "report": "LINX_BENCHMARK_RESULT",
                "transcript": "LINX_BENCHMARK_TRANSCRIPT",
            },
        )

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

    def test_coverage_closure_is_visible_only_in_nightly_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for profile in ("pr", "linux", "nightly"):
                with self.subTest(profile=profile):
                    report = root / f"{profile}.json"
                    env = os.environ.copy()
                    env.pop("QEMU", None)
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(RUNNER),
                            "--profile",
                            profile,
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
                    stages = {stage["id"]: stage for stage in payload["stages"]}
                    if profile == "nightly":
                        self.assertIn("coverage-closure", stages)
                        self.assertEqual(
                            [
                                row["status"]
                                for row in stages["coverage-closure"]["commands"]
                            ],
                            ["not_run", "not_run", "not_run", "not_run"],
                        )
                    else:
                        self.assertNotIn("coverage-closure", stages)

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
            env["QEMU"] = "/usr/bin/true"
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
