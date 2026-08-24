#!/usr/bin/env python3
from __future__ import annotations

import json
import copy
import sys
import subprocess
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_multi_agent_gates


class ReleasePhasePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.manifest = json.loads(
            (cls.root / "docs/bringup/agent_runs/manifest.yaml").read_text(
                encoding="utf-8"
            )
        )
        cls.registry = json.loads(
            (cls.root / "docs/bringup/gate_registry.json").read_text(
                encoding="utf-8"
            )
        )
        cls.waivers = json.loads(
            (cls.root / "docs/bringup/agent_runs/waivers.yaml").read_text(
                encoding="utf-8"
            )
        )

    def test_every_release_phase_has_a_non_empty_gate_set(self) -> None:
        requirements = self.manifest["phase_gate_requirements"]
        for phase in (
            "FOUNDATION",
            "LINUX-RUNTIME",
            "HOSTED-RUNTIME",
            "WORKLOAD-RUNTIME",
            "PROMOTION",
        ):
            with self.subTest(phase=phase):
                self.assertIn(phase, requirements)
                keys = requirements[phase]["required_gate_keys"]
                self.assertTrue(keys)
                self.assertEqual(len(keys), len(set(keys)))

    def test_linux_runtime_cannot_pass_without_real_boots(self) -> None:
        keys = set(
            self.manifest["phase_gate_requirements"]["LINUX-RUNTIME"]
            ["required_gate_keys"]
        )
        self.assertTrue(
            {
                "Kernel::Linux `vmlinux` build closure",
                "Kernel::Linux initramfs smoke",
                "Kernel::Linux initramfs full boot",
                "Kernel::Linux busybox rootfs boot",
            }.issubset(keys)
        )

    def test_promotion_requires_hosted_workload_model_and_nightly_evidence(self) -> None:
        keys = set(
            self.manifest["phase_gate_requirements"]["PROMOTION"]
            ["required_gate_keys"]
        )
        self.assertTrue(
            {
                "Library::musl runtime static+shared",
                "Library::glibc runtime dynamic hello",
                "Workloads::nested SuperNPU v0.58 corpus",
                "Model::QEMU vs model differential suite",
                "LinxCore::CoreMark crosscheck 1000",
                "pyCircuit::nightly simulation regression",
                "Workloads::SPECint nightly test/train gate",
                "Integration::LinxCore performance floor",
            }.issubset(keys)
        )

    def test_active_and_workload_phase_keys_match_registry_and_assignments(self) -> None:
        registry = {gate["gate_key"]: gate for gate in self.registry["gates"]}
        assignments = {
            assignment["gate_key"]: assignment
            for assignment in self.manifest["gate_assignments"]
        }
        phases = {
            self.manifest["phase_policy"]["active_phase"],
            "WORKLOAD-RUNTIME",
        }
        for phase in phases:
            for gate_key in self.manifest["phase_gate_requirements"][phase][
                "required_gate_keys"
            ]:
                with self.subTest(phase=phase, gate_key=gate_key):
                    self.assertIn(gate_key, registry)
                    self.assertIn(gate_key, assignments)
                    self.assertEqual(
                        assignments[gate_key]["agent"], registry[gate_key]["owner"]
                    )

    def test_polybench_gate_uses_bounded_mini_dataset(self) -> None:
        registry = {gate["gate_key"]: gate for gate in self.registry["gates"]}
        command = registry["Workloads::polybench"]["command"]
        self.assertIn("--cflag=-DMINI_DATASET", command)
        self.assertIn("LINX_SPEC_FORCE_STATIC=1", command)

    def test_build_gates_bind_repo_local_outputs_and_provenance(self) -> None:
        registry = {gate["gate_key"]: gate for gate in self.registry["gates"]}
        qemu = registry["Emulator::QEMU pinned binary build"]
        self.assertIn(
            "$ROOT/workloads/generated/gates/qemu-clean", qemu["command"]
        )
        self.assertEqual(
            qemu["artifacts"],
            [
                "workloads/generated/gates/qemu-clean/qemu-system-linx64",
                "workloads/generated/gates/qemu-clean/.linx_qemu_clean_head",
            ],
        )
        self.assertNotIn("QEMU_CLEAN_OUT_DIR", qemu["command"])

        linux = registry["Kernel::Linux `vmlinux` build closure"]
        self.assertIn(
            "$ROOT/workloads/generated/gates/linux-vmlinux", linux["command"]
        )
        self.assertIn("--provenance-out", linux["command"])
        self.assertEqual(
            linux["artifacts"],
            [
                "workloads/generated/gates/linux-vmlinux/vmlinux",
                "workloads/generated/gates/linux-vmlinux/vmlinux.provenance.json",
            ],
        )
        self.assertNotIn("LINUX_VMLINUX_OUT_DIR", linux["command"])
        self.assertNotIn("LINUX_VMLINUX_PROVENANCE", linux["command"])

    def test_registry_output_paths_cannot_drift_from_declared_artifacts(self) -> None:
        registry = {gate["gate_key"]: gate for gate in self.registry["gates"]}
        for gate_key in (
            "Workloads::benchmarks",
            "Workloads::polybench",
            "Workloads::portfolio",
            "Workloads::SPECint fast test/train gate",
            "Workloads::SPECint nightly test/train gate",
        ):
            with self.subTest(gate_key=gate_key):
                self.assertNotIn("WORKLOAD_OUT_DIR", registry[gate_key]["command"])

    def test_registry_parser_rejects_malformed_active_gate_fields(self) -> None:
        cases = (
            ("owner", "", "E_GATE_REGISTRY_GATE_OWNER"),
            ("owner", "missing-owner", "E_GATE_REGISTRY_GATE_OWNER_UNKNOWN"),
            ("command", "", "E_GATE_REGISTRY_COMMAND"),
            ("required", "true", "E_GATE_REGISTRY_REQUIRED"),
            ("profiles", "release-strict", "E_GATE_REGISTRY_PROFILES"),
            ("profiles", ["future"], "E_GATE_REGISTRY_PROFILES_UNKNOWN"),
            ("tiers", [], "E_GATE_REGISTRY_TIERS"),
            ("artifacts", "artifact.json", "E_GATE_REGISTRY_ARTIFACTS"),
            ("freshness_hours", 0, "E_GATE_REGISTRY_FRESHNESS"),
        )
        for field, value, expected_code in cases:
            registry = copy.deepcopy(self.registry)
            gate = next(
                row
                for row in registry["gates"]
                if row["gate_key"] == "Emulator::QEMU pinned binary build"
            )
            gate[field] = value
            errors = []
            check_multi_agent_gates._registry_gate_map(registry, errors=errors)
            with self.subTest(field=field, value=value):
                self.assertIn(expected_code, {row["code"] for row in errors})

    def test_static_checker_rejects_active_phase_gate_absent_from_registry(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["phase_gate_requirements"]["LINUX-RUNTIME"][
            "required_gate_keys"
        ][0] = "Architecture::LinxCore architecture contract lint"
        errors, _, _ = check_multi_agent_gates._validate_static(
            manifest,
            self.waivers,
            self.registry,
            self.root / "docs/bringup/agent_runs/checklists",
            root=self.root,
            strict_always=True,
        )
        self.assertIn("E_PHASE_GATE_NOT_REGISTERED", {row["code"] for row in errors})

    def test_runtime_promotion_override_fails_closed_on_registry_gaps(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(self.root / "tools/bringup/check_multi_agent_gates.py"),
                "--strict-always",
                "--mode",
                "runtime",
                "--active-phase",
                "PROMOTION",
                "--lane",
                "pin",
                "--run-id",
                "registry-alignment-negative-test",
            ],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(proc.returncode, check_multi_agent_gates.EXIT_RUNTIME_FAIL)
        self.assertIn("E_PHASE_GATE_NOT_REGISTERED", proc.stderr)
        self.assertNotIn("E_REPORT_RUN_NOT_FOUND", proc.stderr)


if __name__ == "__main__":
    unittest.main()
