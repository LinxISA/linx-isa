from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.isa.v0591_sail_hard_break import EXPECTED_INSTRUCTION_COUNT
from tools.isa.v0591_sail_hard_break import OBSOLETE_NAMED
from tools.isa.export_linxisa_v0591_sail import export
from tools.isa.v0591_sail_hard_break import is_obsolete
from tools.isa.v0591_sail_hard_break import reservations
from tools.isa.v0591_sail_hard_break import validate_catalog


ROOT = Path(__file__).resolve().parents[2]


def packed_word(row: dict) -> int:
    value = 0
    offset = 0
    for part in row["encoding"]["parts"]:
        value |= int(part["match"], 0) << offset
        offset += int(part["width_bits"])
    return value


def reservation_matches(entry: dict, value: int) -> bool:
    offset = 0
    for part in entry["parts"]:
        mask = int(part["mask"])
        match = int(part["match"])
        if ((value >> offset) & mask) != match:
            return False
        offset += int(part["width_bits"])
    return True


class V0591SailHardBreakTest(unittest.TestCase):
    def test_export_omits_v058_only_status_and_directed_artifacts(self):
        from tools.isa.export_linxisa_v0591_sail import export

        with tempfile.TemporaryDirectory(prefix="linx-v0591-export-") as directory:
            output = Path(directory) / "sail"
            package = export(output)
            self.assertNotIn("coverage.json", package["files"])
            self.assertNotIn("semantics_status.json", package["files"])
            self.assertNotIn("tests/directed.sail", package["files"])
            self.assertIn("tests/v0591_hard_break_tests.sail", package["files"])
            self.assertIn(
                "canonical entry is `model/linxisa_v0591.sail`",
                (output / "README.md").read_text(encoding="utf-8"),
            )

    def test_repository_catalog_is_the_hardened_v0591_edition(self):
        spec = json.loads(
            (ROOT / "isa/v0.59/linxisa-v0.59.json").read_text(encoding="utf-8")
        )
        validate_catalog(spec)
        self.assertEqual(spec["instruction_count"], EXPECTED_INSTRUCTION_COUNT)

        counts = Counter(row["mnemonic"] for row in spec["instructions"])
        self.assertEqual(
            sum(
                row["mnemonic"] == "HL.BSTART CALL"
                and row["asm"].startswith("HL.BSTART.CALL")
                for row in spec["instructions"]
            ),
            1,
        )
        for mnemonic in (
            "HL.BSTART.FP",
            "HL.BSTART.STD",
            "L.BSTART.FP",
            "L.BSTART.STD",
        ):
            self.assertEqual(counts[mnemonic], 4)
        for mnemonic in ("HL.BSTART.SYS", "L.BSTART.SYS"):
            self.assertEqual(counts[mnemonic], 1)
        for mnemonic in ("DMA.FREE.L", "DMA.FREE.S", "MCOPY.DL", "MCOPY.DS"):
            self.assertEqual(counts[mnemonic], 1)

    def test_signed_193_forms_are_owned_by_exactly_one_reservation(self):
        historical = json.loads(
            subprocess.check_output(
                ["git", "show", "v0.59.1:isa/v0.59/linxisa-v0.59.json"],
                cwd=ROOT,
                text=True,
            )
        )
        reserved = reservations()
        obsolete = []
        for row in historical["instructions"]:
            owners = [
                entry
                for entry in reserved
                if entry["length_bits"] == row["length_bits"]
                and reservation_matches(entry, packed_word(row))
            ]
            if is_obsolete(row["mnemonic"]):
                self.assertEqual(len(owners), 1, row["id"])
                obsolete.append(row["id"])
            else:
                self.assertEqual(owners, [], row["id"])
        self.assertEqual(len(obsolete), 193)

    def test_ten_reservation_records_include_the_full_vector_wildcard(self):
        reserved = reservations()
        self.assertEqual(len(reserved), 10)
        self.assertEqual(
            {entry["mnemonic"] for entry in reserved},
            {"V.*", *OBSOLETE_NAMED},
        )
        vector = next(entry for entry in reserved if entry["mnemonic"] == "V.*")
        self.assertEqual(vector["length_bits"], 64)
        self.assertTrue(reservation_matches(vector, 0xDEADBEEF0000007F))
        self.assertFalse(reservation_matches(vector, 0xDEADBEEF0000007E))

    def test_export_uses_version_owned_state_and_execute(self):
        with tempfile.TemporaryDirectory(prefix="linx-v0591-hard-break-") as directory:
            output = Path(directory) / "sail"
            export(output)
            for relative in ("model/state/state.sail", "model/execute/execute.sail"):
                self.assertEqual(
                    (output / relative).read_bytes(),
                    (ROOT / "isa/v0.59/sail" / relative).read_bytes(),
                )
            execute = (output / "model/execute/execute.sail").read_text(
                encoding="utf-8"
            )
            state = (output / "model/state/state.sail").read_text(encoding="utf-8")
            decode = (output / "model/decode/decode.sail").read_text(encoding="utf-8")
            self.assertNotIn("function exec_v_", execute)
            self.assertNotIn("register vreg", state)
            self.assertNotIn("function exec_b_text", execute)
            self.assertEqual(decode.count("PTO reserved in v0.59.1:"), 10)
            self.assertIn("PTO reserved in v0.59.1: V.*", decode)


if __name__ == "__main__":
    unittest.main()
