#!/usr/bin/env python3
"""Mutation tests for the exact PTO runtime-startup projection."""

from __future__ import annotations

import importlib.util
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/isa/pto_runtime_startup.py"


def load_module():
    spec = importlib.util.spec_from_file_location("pto_runtime_startup", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PtoRuntimeStartupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.outputs = {
            cls.module.LOCK_PATH: cls.module.LOCK_PATH.read_text(encoding="utf-8"),
            cls.module.STATE_PATH: cls.module.STATE_PATH.read_text(encoding="utf-8"),
        }
        cls.state = json.loads(cls.outputs[cls.module.STATE_PATH])

    def validate_mutated_bindings(self, *, systems=None, scalars=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state_dir = root / "isa/v0.58/state"
            state_dir.mkdir(parents=True)
            current_systems = json.loads(
                (ROOT / "isa/v0.58/state/system_registers.json").read_text()
            )
            current_scalars = json.loads(
                (ROOT / "isa/v0.58/state/pto_scalar_forms.json").read_text()
            )
            (state_dir / "system_registers.json").write_text(json.dumps(
                current_systems if systems is None else systems
            ))
            (state_dir / "pto_scalar_forms.json").write_text(json.dumps(
                current_scalars if scalars is None else scalars
            ))
            return self.module.validate_linx_bindings(root, self.state)

    def test_checked_in_projection_is_exact_and_current(self) -> None:
        self.assertEqual(self.module.check_outputs(ROOT, self.outputs), [])
        lock = json.loads((ROOT / "isa/v0.58/pto-runtime-startup.lock.json").read_text())
        state = json.loads((ROOT / "isa/v0.58/state/pto_runtime_startup.json").read_text())
        self.assertEqual(lock["source"]["commit"], self.module.SOURCE_COMMIT)
        self.assertEqual(lock["source"]["tree"], self.module.SOURCE_TREE)
        self.assertEqual(
            lock["projection"]["sha256"],
            hashlib.sha256(self.module.STATE_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(state["status"], "required-downstream-adaptation")
        self.assertEqual(
            state["pto_runtime_startup"]["execution_support"]["sail"],
            "decode-only-single-context",
        )
        self.assertEqual(
            {row["id"] for row in state["pto_runtime_startup"]["clauses"]},
            {clause for clauses in self.module.CLAUSES.values() for clause in clauses},
        )
        by_id = {
            row["id"]: row for row in state["pto_runtime_startup"]["clauses"]
        }
        for source in lock["sources"].values():
            for clause in source.get("clauses", []):
                text = by_id[clause["id"]]["text"].encode()
                self.assertEqual(hashlib.sha256(text).hexdigest(), clause["sha256"])

    def test_missing_clause_is_rejected(self) -> None:
        source = b"// NDF-BEGIN: PTO-OTHER-001\n// NDF-END: PTO-OTHER-001\n"
        with self.assertRaisesRegex(ValueError, "found 0"):
            self.module.extract_clause(source, "PTO-ARCH-RUNTIME-STARTUP-ABI-001")

    def test_duplicate_clause_is_rejected(self) -> None:
        region = (
            b"// NDF-BEGIN: PTO-ARCH-RUNTIME-STARTUP-ABI-001\n"
            b"// NDF-END: PTO-ARCH-RUNTIME-STARTUP-ABI-001\n"
        )
        with self.assertRaisesRegex(ValueError, "found 2"):
            self.module.extract_clause(region + region, "PTO-ARCH-RUNTIME-STARTUP-ABI-001")

    def test_wrong_source_binding_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repository = Path(directory)
            subprocess.run(["git", "init", "-q", repository], check=True)
            subprocess.run(
                ["git", "-C", repository, "config", "user.email", "test@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", repository, "config", "user.name", "test"], check=True
            )
            for path, clause_ids in self.module.CLAUSES.items():
                source = repository / path
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("".join(
                    f"// NDF-BEGIN: {clause_id}\n// NDF-END: {clause_id}\n"
                    for clause_id in clause_ids
                ))
            scalar_catalog = repository / "spec/catalog/scalar-forms.json"
            scalar_catalog.parent.mkdir(parents=True, exist_ok=True)
            scalar_catalog.write_text(json.dumps({"forms": [{
                "mnemonic": "SYNC.CORE", "encoding": [{"match": "fixture"}]
            }]}))
            (repository / "spec/catalog/system-registers.json").write_text(
                json.dumps({"registers": [{
                    "access": "RO", "address": "0x0026",
                    "name": "THREAD_ID", "scope": "base",
                }]})
            )
            subprocess.run(["git", "-C", repository, "add", "."], check=True)
            subprocess.run(
                ["git", "-C", repository, "commit", "-q", "-m", "fixture"], check=True
            )
            commit = subprocess.check_output(
                ["git", "-C", repository, "rev-parse", "HEAD"], text=True
            ).strip()
            tree = subprocess.check_output(
                ["git", "-C", repository, "rev-parse", "HEAD^{tree}"], text=True
            ).strip()
            self.assertEqual(
                set(self.module.load_frozen_sources(
                    repository, commit=commit, tree=tree
                )),
                set(self.module.CLAUSES) | set(self.module.CATALOGS),
            )
            with self.assertRaisesRegex(ValueError, "source tree mismatch"):
                self.module.load_frozen_sources(
                    repository, commit=commit, tree="0" * 40
                )
            with self.assertRaisesRegex(ValueError, "source commit is unavailable"):
                self.module.load_frozen_sources(repository, commit="0" * 40)

    def test_stale_projection_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for canonical_path, text in self.outputs.items():
                path = root / canonical_path.relative_to(ROOT)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            state = root / "isa/v0.58/state/pto_runtime_startup.json"
            state.write_text(state.read_text().replace(
                "required-downstream-adaptation", "implemented", 1
            ))
            errors = self.module.check_outputs(root, self.outputs)
        self.assertTrue(any("stale generated" in error for error in errors), errors)

    def test_thread_id_address_and_access_mutations_are_rejected(self) -> None:
        systems = json.loads(
            (ROOT / "isa/v0.58/state/system_registers.json").read_text()
        )
        thread = next(
            row for row in self.module.nested_records(systems)
            if row.get("name") == "THREAD_ID"
        )
        for field, value in (("id", "0x0802"), ("access", "RW"), ("width_bits", 32)):
            with self.subTest(field=field):
                mutated = copy.deepcopy(systems)
                target = next(
                    row for row in self.module.nested_records(mutated)
                    if row.get("name") == "THREAD_ID"
                )
                target[field] = value
                errors = self.validate_mutated_bindings(systems=mutated)
                self.assertTrue(any("THREAD_ID" in error for error in errors), errors)

    def test_duplicate_thread_id_address_is_rejected(self) -> None:
        systems = json.loads(
            (ROOT / "isa/v0.58/state/system_registers.json").read_text()
        )
        systems["ssr"]["base"][0]["id"] = "0x26"
        errors = self.validate_mutated_bindings(systems=systems)
        self.assertTrue(any("uniquely" in error for error in errors), errors)

    def test_retired_alias_and_sync_encoding_mutations_are_rejected(self) -> None:
        systems = json.loads(
            (ROOT / "isa/v0.58/state/system_registers.json").read_text()
        )
        aliased = copy.deepcopy(systems)
        next(row for row in self.module.nested_records(aliased)
             if row.get("name") == "THREAD_ID")["id"] = "0x0802"
        errors = self.validate_mutated_bindings(systems=aliased)
        self.assertTrue(any("0x0802" in error for error in errors), errors)

        scalars = json.loads(
            (ROOT / "isa/v0.58/state/pto_scalar_forms.json").read_text()
        )
        mutated = copy.deepcopy(scalars)
        sync = next(row for row in mutated["forms"] if row["mnemonic"] == "SYNC.CORE")
        sync["encoding"][0]["match"] = "0x00000000"
        errors = self.validate_mutated_bindings(scalars=mutated)
        self.assertTrue(any("SYNC.CORE" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
