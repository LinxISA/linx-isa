#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools" / "ci" / "check_component_lock.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_component_lock", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {CHECKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ComponentLockTests(unittest.TestCase):
    def test_current_v058_component_lock_matches_staged_topology(self) -> None:
        checker = load_checker()
        self.assertEqual(checker.check_repository(ROOT), [])

    def test_standalone_supernpu_gitlink_is_forbidden(self) -> None:
        checker = load_checker()
        lock = {
            "schema_version": 1,
            "profile": "v0.58",
            "components": [
                {
                    "path": "workloads/SuperNPUBench",
                    "url": "https://github.com/PTO-ISA/SuperNPUBench.git",
                    "branch": "main",
                    "commit": "1" * 40,
                }
            ],
        }
        modules = {
            "workloads/SuperNPUBench": {
                "url": "https://github.com/PTO-ISA/SuperNPUBench.git",
                "branch": "main",
            }
        }
        errors = checker.validate(lock, modules, {"workloads/SuperNPUBench": "1" * 40})
        self.assertTrue(any("SuperNPUBench" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
