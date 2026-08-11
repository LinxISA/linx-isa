#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path


class ReleasePhasePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[2]
        cls.manifest = json.loads(
            (cls.root / "docs/bringup/agent_runs/manifest.yaml").read_text(
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
                "Regression::Nested SuperNPU v0.58 corpus",
                "Model::QEMU vs model differential suite",
                "LinxCore::CoreMark crosscheck 1000",
                "pyCircuit::nightly simulation regression",
                "Regression::SPECint nightly test/train gate",
                "Integration::LinxCore performance floor",
            }.issubset(keys)
        )


if __name__ == "__main__":
    unittest.main()
