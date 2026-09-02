#!/usr/bin/env python3
"""Exact PTO profile-hook provenance contract."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "isa/v0.58/pto-profile-hooks.lock.json"
CHECKER = ROOT / "tools/isa/check_pto_profile_hooks.py"


class PtoProfileHookLockTests(unittest.TestCase):
    def test_exact_extension_first_use_lock(self) -> None:
        self.assertTrue(LOCK.is_file(), "PTO profile-hook lock is missing")
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        hook = lock["profile_hooks"]["extension_first_use"]
        self.assertEqual(hook["profile_id"], "PTO-ARCH-EXTENSION-FIRST-USE-PROFILE-001")
        self.assertEqual(
            hook["source"],
            {
                "repository": "https://github.com/PTO-ISA/pto-spec.git",
                "commit": "33637171b96b402a14319561662cb741e9cc6f87",
                "tree": "d880e84dc9efd41e7aa29377196723e256cad1dd",
                "path": "asl/arch/profile/extension-first-use.asl",
                "sha256": "ef0bbe915fc5fd01cc93cca2a176844dcbdcb6d48af9bf36404c0bfa897615f3",
            },
        )
        self.assertEqual(
            hook["linx_mapping_sha256"],
            "69cd0e30b7923f6ea31d9e5a54cbac387b45c2026be770e55a9c4325138e7f0d",
        )
        self.assertEqual(lock["common_pto_release"], "0.58.5")
        self.assertEqual(
            lock["common_pto_lock_sha256"],
            "fe7bd4c6a521f652e6430a6b010b3513c21dfe70aaa17c104bb196cd69d469cd",
        )

    def test_checker_rejects_mapping_mutation(self) -> None:
        self.assertTrue(CHECKER.is_file(), "PTO profile-hook checker is missing")
        module_spec = importlib.util.spec_from_file_location("pto_profile_hooks", CHECKER)
        assert module_spec and module_spec.loader
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)

        conventions = json.loads(
            (ROOT / "isa/v0.58/semantics_conventions.json").read_text()
        )
        conventions["extension_first_use"]["trap"]["cause_value"] = 5
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            (temp / "isa/v0.58").mkdir(parents=True)
            (temp / "isa/v0.58/pto-profile-hooks.lock.json").write_bytes(
                LOCK.read_bytes()
            )
            (temp / "isa/v0.58/pto-spec.lock.json").write_bytes(
                (ROOT / "isa/v0.58/pto-spec.lock.json").read_bytes()
            )
            (temp / "isa/v0.58/semantics_conventions.json").write_text(
                json.dumps(conventions), encoding="utf-8"
            )
            errors = module.check(temp)
        self.assertTrue(any("mapping SHA-256 mismatch" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
