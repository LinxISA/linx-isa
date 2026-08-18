#!/usr/bin/env python3
"""Exact LinxISA first-use exception source and projection contract."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "isa/v0.58/state/system_registers.json"
COMPILED_PATH = ROOT / "isa/v0.58/linxisa-v0.58.json"
CONVENTIONS_PATH = ROOT / "isa/v0.58/semantics_conventions.json"
PTO_OPS_PATH = ROOT / "isa/v0.58/state/pto_ops.json"
ENGINE_OPS_PATH = ROOT / "isa/v0.58/state/engine_ops.json"

EXPECTED_FIRST_USE = {
    "e": 1,
    "argv": 1,
    "trapnum": "E_INST",
    "trapnum_value": 0,
    "cause": "EC_PERM",
    "cause_value": 4,
    "bi": 0,
    "traparg0": {"VECTOR": 0, "CUBE": 1},
}

VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "linx_validate_spec", ROOT / "tools/isa/validate_spec.py"
)
assert VALIDATOR_SPEC and VALIDATOR_SPEC.loader
validate_spec = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(validate_spec)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class FirstUseExceptionContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.source = load_json(SOURCE_PATH)
        compiled = load_json(COMPILED_PATH)
        self.compiled = compiled["state"]["system_registers"]
        self.conventions = load_json(CONVENTIONS_PATH)
        self.compiled_conventions = compiled["semantics_conventions"]

    def test_first_use_exception_envelope_is_exact(self) -> None:
        trapno = self.source["trapno_encoding"]
        self.assertEqual(trapno["first_use_exception"], EXPECTED_FIRST_USE)
        self.assertNotIn("E_PEREM", json.dumps(trapno, sort_keys=True))
        e_field = next(
            field
            for field in self.source["trapno_encoding"]["fields"]
            if field["name"] == "E"
        )
        self.assertEqual(e_field["synchronous_exception_value"], 1)
        self.assertEqual(e_field["asynchronous_interrupt_value"], 0)

    def test_econfig_layout_and_reset_are_exact(self) -> None:
        econfig = self.source.get("econfig_contract")
        self.assertIsInstance(econfig, dict)
        self.assertEqual(econfig["width_bits"], 64)
        self.assertEqual(econfig["reset_value"], "0x0000000300000008")
        self.assertTrue(econfig["per_hardware_thread"])
        self.assertEqual(econfig["fields"]["V"]["bit"], 32)
        self.assertEqual(econfig["fields"]["C"]["bit"], 33)
        self.assertEqual(econfig["reserved_ranges"], [[4, 31], [34, 63]])
        self.assertEqual(econfig["reserved_write"], "must-zero")
        self.assertEqual(econfig["reserved_read"], "zero")

    def test_compiled_system_register_projection_is_exact(self) -> None:
        self.assertEqual(self.compiled, self.source)

    def test_validator_rejects_wrong_first_use_numeric_contract(self) -> None:
        fixture = load_json(COMPILED_PATH)
        system_registers = fixture["state"]["system_registers"]
        system_registers["trapno_encoding"] = self.source["trapno_encoding"]
        system_registers["econfig_contract"] = self.source["econfig_contract"]
        system_registers["trapno_encoding"]["first_use_exception"][
            "cause_value"
        ] = 5

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            errors = validate_spec.validate(str(path))

        self.assertTrue(
            any("first-use exception envelope mismatch" in error for error in errors),
            errors,
        )

    def test_first_use_trap_envelope_and_vector_headers_are_exact(self) -> None:
        first_use = self.conventions.get("extension_first_use")
        self.assertIsInstance(first_use, dict)
        self.assertEqual(first_use["source_acr"], 2)
        self.assertEqual(first_use["manager_acr"], 1)
        self.assertEqual(
            first_use["trap"],
            {
                "e": 1,
                "argv": 1,
                "trapnum": "E_INST",
                "trapnum_value": 0,
                "cause": "EC_PERM",
                "cause_value": 4,
                "bi": 0,
            },
        )
        self.assertEqual(first_use["kinds"], {"VECTOR": 0, "CUBE": 1})
        self.assertEqual(
            first_use["vector_headers"],
            [
                "BSTART.MPAR",
                "BSTART.MSEQ",
                "BSTART.VPAR",
                "BSTART.VSEQ",
                "C.BSTART.MPAR",
                "C.BSTART.MSEQ",
                "C.BSTART.VPAR",
                "C.BSTART.VSEQ",
            ],
        )
        self.assertNotIn("BSTART.VEC", first_use["vector_headers"])
        self.assertNotIn("BSTART.SFU", first_use["vector_headers"])

    def test_first_use_ordering_and_cube_membership_source_are_exact(self) -> None:
        first_use = self.conventions.get("extension_first_use")
        self.assertIsInstance(first_use, dict)
        self.assertEqual(
            first_use["cube_membership"],
            "state.pto_ops.operations entries with family=CUBE and engine=CUBE",
        )
        self.assertEqual(
            first_use["ordering"],
            [
                "legal-decode",
                "acr-permission",
                "first-use",
                "resource-allocation",
                "effects",
            ],
        )
        self.assertEqual(
            first_use["zero_effects"],
            ["BARG", "BSTATE", "queues", "memory-requests", "completion-state"],
        )
        pto_ops = load_json(PTO_OPS_PATH)
        cube_ops = [
            operation
            for operation in pto_ops["operations"]
            if operation["family"] == "CUBE" and operation["engine"] == "CUBE"
        ]
        self.assertEqual(len(cube_ops), 12)
        self.assertEqual(load_json(ENGINE_OPS_PATH)["semantic_engine_counts"]["CUBE"], 12)
        self.assertEqual(self.compiled_conventions, self.conventions)

    def test_validator_rejects_wrong_first_use_semantic_envelope(self) -> None:
        fixture = load_json(COMPILED_PATH)
        fixture["semantics_conventions"] = self.conventions
        fixture["semantics_conventions"]["extension_first_use"]["trap"][
            "cause_value"
        ] = 5

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            errors = validate_spec.validate(str(path))

        self.assertTrue(
            any("extension-first-use trap envelope mismatch" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
