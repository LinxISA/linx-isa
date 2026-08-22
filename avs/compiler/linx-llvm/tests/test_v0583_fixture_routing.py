#!/usr/bin/env python3

import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[4]
CURRENT_ASM = REPO / "avs/compiler/linx-llvm/tests/asm"
ARCHIVED_ASM = REPO / "avs/archive/v0.57/compiler/linx-llvm/tests/asm"
RUNNER = REPO / "avs/compiler/linx-llvm/tests/run.sh"


class V0583FixtureRoutingTest(unittest.TestCase):
    def test_current_lane_routes_only_v0583_fixture(self) -> None:
        self.assertTrue((CURRENT_ASM / "41_v0583_isa_forms.s").is_file())
        self.assertFalse((CURRENT_ASM / "41_v057_isa_forms.s").exists())
        self.assertTrue((ARCHIVED_ASM / "41_v057_isa_forms.s").is_file())

        runner = RUNNER.read_text()
        self.assertIn("41_v0583_isa_forms)", runner)
        self.assertNotIn("41_v057_isa_forms)", runner)
        self.assertIn("isa/v0.58/linxisa-v0.58.json", runner)


if __name__ == "__main__":
    unittest.main()
