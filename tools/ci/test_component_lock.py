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

    def test_linxcoremodel_topic_pin_must_be_explicitly_review_only(self) -> None:
        checker = load_checker()
        path = "tools/LinxCoreModel"
        lock = {
            "schema_version": 1,
            "profile": "v0.58",
            "components": [
                {
                    "path": path,
                    "url": "https://github.com/LinxISA/LinxCoreModel.git",
                    "branch": "main",
                    "commit": "2" * 40,
                }
            ],
        }
        modules = {
            path: {
                "url": "https://github.com/LinxISA/LinxCoreModel.git",
                "branch": "main",
                "update": "checkout",
            }
        }

        errors = checker.validate(lock, modules, {path: "2" * 40})

        self.assertTrue(
            any("review-only open PR" in error for error in errors), errors
        )

    def test_linxcoremodel_review_only_pin_rejects_release_metadata(self) -> None:
        checker = load_checker()
        path = "tools/LinxCoreModel"
        lock = {
            "schema_version": 1,
            "profile": "v0.58",
            "components": [
                {
                    "path": path,
                    "url": "https://github.com/LinxISA/LinxCoreModel.git",
                    "branch": "main",
                    "commit": "3" * 40,
                    "integration_status": "review_only_open_pr",
                    "review_url": "https://github.com/LinxISA/LinxCoreModel/pull/36",
                    "release_tag": "linxisa-v0.58.0",
                }
            ],
        }
        modules = {
            path: {
                "url": "https://github.com/LinxISA/LinxCoreModel.git",
                "branch": "main",
                "update": "checkout",
            }
        }

        errors = checker.validate(lock, modules, {path: "3" * 40})

        self.assertTrue(any("must not have release metadata" in e for e in errors), errors)

    def test_every_component_requires_tree_and_role_provenance(self) -> None:
        checker = load_checker()
        path = "lib/mesa3d"
        lock = {
            "schema_version": 1,
            "profile": "v0.58",
            "components": [
                {
                    "path": path,
                    "url": "https://github.com/LinxISA/mesa3d.git",
                    "branch": "main",
                    "commit": "4" * 40,
                }
            ],
        }
        modules = {
            path: {
                "url": "https://github.com/LinxISA/mesa3d.git",
                "branch": "main",
                "update": "checkout",
            }
        }

        errors = checker.validate(lock, modules, {path: "4" * 40})

        self.assertTrue(any("invalid locked tree" in error for error in errors), errors)
        self.assertTrue(any("role must be non-empty" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
