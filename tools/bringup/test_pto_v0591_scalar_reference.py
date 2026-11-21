import json
from pathlib import Path
import tempfile
import unittest

from tools.bringup.check_pto_v0591_scalar_reference import (
    FINISHER_ADDRESS,
    FINISHER_PASS,
    require_pass_finisher,
    validate_cases,
)


class ScopedScalarReferenceTest(unittest.TestCase):
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
