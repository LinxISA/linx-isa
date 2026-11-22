import json
from pathlib import Path
import tempfile
import unittest

from tools.bringup.check_pto_v0591_scalar_reference import (
    FINISHER_ADDRESS,
    FINISHER_PASS,
    build_case,
    compare_models,
    require_pass_finisher,
    validate_cases,
)


class ScopedScalarReferenceTest(unittest.TestCase):
    def test_symbolic_pcr_preserves_oracle_and_uses_carrier_offsets(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            _, numeric_golden, numeric_segments, numeric_relocs = build_case(path)
            source, golden, segments, relocations = build_case(path, symbolic_pcr=True)
            self.assertEqual(golden, numeric_golden)
            self.assertEqual(segments, numeric_segments)
            self.assertEqual(numeric_relocs, [])
            self.assertEqual(len(relocations), 66)
            self.assertEqual({number for _, _, number in relocations}, {33, 34, 35, 36})
            self.assertTrue(all(offset % 4 == 2 for offset, _, _ in relocations))
            self.assertEqual(source.read_text().count("[.Lcell"), len(relocations))

    def test_compares_each_model_with_golden_and_every_other_model(self):
        good = bytes(8)
        wrong = b"\x01" + bytes(7)
        results = compare_models(
            {"qemu": good, "gfrun": good, "gfsim": wrong},
            good,
            [{"offset": 0, "form_id": "case"}],
        )
        self.assertEqual(len(results), 6)
        self.assertTrue(results["qemu_to_gfrun"]["pass"])
        self.assertFalse(results["gfsim_to_golden"]["pass"])
        self.assertEqual(results["gfrun_to_gfsim"]["form_id"], "case")

    def test_complete_result_without_pass_finisher_is_rejected(self):
        record = {
            "trap_valid": 0,
            "mem_valid": 1,
            "mem_is_store": 1,
            "mem_addr": 0x10000,
            "mem_size": 4,
            "mem_wdata": FINISHER_PASS,
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "result.bin").write_bytes(bytes(1440))
            trace = root / "commits.jsonl"
            trace.write_text(json.dumps(record) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "did not retire the pass finisher"):
                require_pass_finisher(trace)
            record["mem_addr"] = FINISHER_ADDRESS
            trace.write_text(json.dumps(record) + "\n", encoding="utf-8")
            require_pass_finisher(trace)

    def test_catalog_requires_distinct_carriers_and_full_scope_coverage(self):
        cases = [
            (
                {
                    "base_form_id": f"base_{i}",
                    "form_id": f"form_{i}_{scope}",
                    "scope_code": scope,
                },
                {},
            )
            for i in range(60)
            for scope in range(3)
        ]
        validate_cases(cases)
        with self.assertRaisesRegex(ValueError, "form IDs must be unique"):
            validate_cases(cases[:-1] + [cases[-2]])
        cases[-1][0]["scope_code"] = 0
        with self.assertRaisesRegex(ValueError, "all three scopes"):
            validate_cases(cases)


if __name__ == "__main__":
    unittest.main()
