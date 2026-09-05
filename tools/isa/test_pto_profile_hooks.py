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
                "commit": "dea0b75e803cffa873982c90f9aa0cd17c6d243b",
                "tree": "64571b898e5acb437b93fdedb415e193bb63f60f",
                "path": "asl/arch/profile/extension-first-use.asl",
                "sha256": "ef0bbe915fc5fd01cc93cca2a176844dcbdcb6d48af9bf36404c0bfa897615f3",
            },
        )
        self.assertEqual(
            hook["linx_mapping_sha256"],
            "69cd0e30b7923f6ea31d9e5a54cbac387b45c2026be770e55a9c4325138e7f0d",
        )
        self.assertEqual(lock["common_pto_release"], "0.58.6")
        self.assertEqual(
            lock["common_pto_lock_sha256"],
            "77e792fb0add49a2cf4a0dcc6853a715d6b1c98490f48649b85f923579ba36be",
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
