#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

import run_gates


def minimal_registry(owner: str = "integration", gate_key: str = "ISA::Unit gate") -> dict:
    return {
        "schema_version": 1,
        "owners": ["integration", "llvm"],
        "gates": [
            {
                "gate_key": gate_key,
                "domain": "ISA",
                "owner": owner,
                "command": "true",
                "profiles": ["release-strict"],
                "tiers": ["pr"],
                "required": True,
                "artifacts": [],
                "freshness_hours": 24,
            }
        ],
    }


class RunGatesTests(unittest.TestCase):
    def write_registry(self, data: dict) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        with tmp:
            json.dump(data, tmp)
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        return Path(tmp.name)

    def test_registry_rejects_duplicate_gate_keys(self) -> None:
        data = minimal_registry()
        data["gates"].append(dict(data["gates"][0]))
        path = self.write_registry(data)
        with self.assertRaises(SystemExit):
            run_gates.load_registry(path)

    def test_registry_rejects_unknown_owner(self) -> None:
        path = self.write_registry(minimal_registry(owner="missing-owner"))
        with self.assertRaises(SystemExit):
            run_gates.load_registry(path)

    def test_profile_and_tier_filtering(self) -> None:
        registry = minimal_registry()
        gates = run_gates.select_gates(
            registry,
            profile="release-strict",
            tier="pr",
            gate_filter=[],
            domain_filter=[],
            include_optional=False,
        )
        self.assertEqual([g["gate_key"] for g in gates], ["ISA::Unit gate"])
        gates = run_gates.select_gates(
            registry,
            profile="dev",
            tier="pr",
            gate_filter=[],
            domain_filter=[],
            include_optional=False,
        )
        self.assertEqual(gates, [])

    def test_env_flag_filtering(self) -> None:
        registry = minimal_registry()
        registry["gates"][0]["enabled_if_env"] = "RUN_UNIT_GATE"
        old = os.environ.pop("RUN_UNIT_GATE", None)
        def restore_env() -> None:
            if old is None:
                os.environ.pop("RUN_UNIT_GATE", None)
            else:
                os.environ["RUN_UNIT_GATE"] = old

        self.addCleanup(restore_env)
        self.assertEqual(
            run_gates.select_gates(
                registry,
                profile="release-strict",
                tier="pr",
                gate_filter=[],
                domain_filter=[],
                include_optional=False,
            ),
            [],
        )
        os.environ["RUN_UNIT_GATE"] = "1"
        self.assertEqual(
            len(
                run_gates.select_gates(
                    registry,
                    profile="release-strict",
                    tier="pr",
                    gate_filter=[],
                    domain_filter=[],
                    include_optional=False,
                )
            ),
            1,
        )

    def test_stale_artifact_detection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            artifact = root / "artifact.txt"
            artifact.write_text("x", encoding="utf-8")
            old = time.time() - 3 * 3600
            os.utime(artifact, (old, old))
            gate = minimal_registry()["gates"][0]
            gate["artifacts"] = ["artifact.txt"]
            gate["freshness_hours"] = 1
            state = run_gates.check_artifacts(root, gate)
            self.assertFalse(state["ok"])
            self.assertEqual(state["artifacts"][0]["status"], "stale")

    def test_regression_wrapper_dry_run(self) -> None:
        root = Path(__file__).resolve().parents[2]
        env = os.environ.copy()
        env["LINX_GATE_DRY_RUN"] = "1"
        proc = subprocess.run(
            [
                "bash",
                str(root / "tools/regression/run.sh"),
                "--gate",
                "ISA::Golden catalog check",
            ],
            cwd=root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ISA::Golden catalog check", proc.stdout)

    def test_strict_wrapper_enables_linux_boot_gates_for_dry_run(self) -> None:
        root = Path(__file__).resolve().parents[2]
        env = os.environ.copy()
        env["LINX_GATE_DRY_RUN"] = "1"
        proc = subprocess.run(
            [
                "bash",
                str(root / "tools/regression/strict_cross_repo.sh"),
                "--gate",
                "Kernel::Linux initramfs smoke",
            ],
            cwd=root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Kernel::Linux initramfs smoke", proc.stdout)


if __name__ == "__main__":
    unittest.main()
