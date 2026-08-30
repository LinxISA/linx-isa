#!/usr/bin/env python3

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("analyze_coverage.py")
SPEC = importlib.util.spec_from_file_location("analyze_coverage", SCRIPT)
assert SPEC and SPEC.loader
coverage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(coverage)

VECTOR_SCRIPT = Path(__file__).with_name("gen_disasm_vectors.py")
VECTOR_SPEC = importlib.util.spec_from_file_location("gen_disasm_vectors", VECTOR_SCRIPT)
assert VECTOR_SPEC and VECTOR_SPEC.loader
vectors = importlib.util.module_from_spec(VECTOR_SPEC)
VECTOR_SPEC.loader.exec_module(vectors)


class AnalyzeCoverageTest(unittest.TestCase):
    def write_spec(self, root: Path, *mnemonics: str) -> Path:
        path = root / "spec.json"
        path.write_text(
            json.dumps(
                {
                    "instructions": [
                        {"mnemonic": mnemonic, "group": "Test"}
                        for mnemonic in mnemonics
                    ]
                }
            )
        )
        return path

    def write_objdump(self, out_dir: Path, test_name: str, mnemonic: str) -> Path:
        test_dir = out_dir / test_name
        test_dir.mkdir(parents=True)
        path = test_dir / f"{test_name}.objdump"
        path.write_text(f"       0: 01 00 {mnemonic} r1, r2\n")
        return path

    def run_script(self, script: Path, *args: object) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(script), *(str(arg) for arg in args)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_default_uses_run_sh_out_even_when_stale_archives_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            copied_script = root / SCRIPT.name
            copied_script.write_text(SCRIPT.read_text())
            spec_path = self.write_spec(root, "XOR", "SUB")
            self.write_objdump(root / "out", "fresh", "XOR")
            self.write_objdump(root / "out" / "alternate-lane", "nested", "SUB")
            self.write_objdump(root / "out", "_neg", "SUB")
            self.write_objdump(root / "out-linx64", "stale", "SUB")
            self.write_objdump(root / "out-linx32", "older", "SUB")

            proc = self.run_script(copied_script, "--spec", spec_path, "--json")

            self.assertEqual(proc.returncode, 0, proc.stderr)
            report = json.loads(proc.stdout)
            self.assertEqual(report["covered_spec_mnemonics"], 1)
            self.assertEqual(report["missing_mnemonics"], ["SUB"])
            self.assertIn("fresh", report["emitted_by_test"])
            self.assertNotIn("stale", report["emitted_by_test"])

    def test_one_level_scratch_objdump_does_not_count(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_data = coverage.load_isa_spec(self.write_spec(root, "XOR", "SUB"))
            self.write_objdump(root / "out", "primary", "XOR")
            scratch = root / "out" / "grace-l-bstart-smoke"
            scratch.mkdir(parents=True)
            (scratch / "forms.objdump").write_text("       0: 01 00 SUB r1, r2\n")

            report = coverage.analyze_coverage(spec_data, root / "out")

            self.assertEqual(report["covered_spec_mnemonics"], 1)
            self.assertEqual(report["missing_mnemonics"], ["SUB"])
            self.assertNotIn("grace-l-bstart-smoke", report["emitted_by_test"])

    def test_extra_objdump_cannot_supplement_or_overwrite_primary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_data = coverage.load_isa_spec(self.write_spec(root, "XOR", "SUB"))
            primary = self.write_objdump(root / "out", "canonical", "XOR")
            (primary.parent / "extra.objdump").write_text(
                "       0: 01 00 SUB r1, r2\n"
            )

            report = coverage.analyze_coverage(spec_data, root / "out")

            self.assertEqual(report["covered_spec_mnemonics"], 1)
            self.assertEqual(report["missing_mnemonics"], ["SUB"])
            self.assertEqual(report["emitted_by_test"]["canonical"], ["XOR"])

    def test_spec_decode_comments_do_not_count_as_observed_disassembly(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_data = coverage.load_isa_spec(self.write_spec(root, "COMMENT.ONLY"))
            test_dir = root / "out" / "99_spec_decode"
            test_dir.mkdir(parents=True)
            (test_dir / "99_spec_decode.objdump").write_text("file format elf64-linx\n")
            (test_dir / "99_spec_decode.s").write_text(
                "# COMMENT.ONLY (generated vector) [0]\n"
            )

            report = coverage.analyze_coverage(spec_data, root / "out")

            self.assertEqual(report["covered_spec_mnemonics"], 0)
            self.assertEqual(report["missing_mnemonics"], ["COMMENT.ONLY"])
            self.assertEqual(report["emitted_by_test"]["99_spec_decode"], [])

    def test_hex_spelled_mnemonic_is_not_consumed_as_encoding_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_data = coverage.load_isa_spec(self.write_spec(root, "ADD"))
            self.write_objdump(root / "out", "arithmetic", "ADD")

            report = coverage.analyze_coverage(spec_data, root / "out")

            self.assertEqual(report["covered_spec_mnemonics"], 1)
            self.assertEqual(report["missing_mnemonics"], [])

    def test_hex_prefixed_float_mnemonic_is_not_treated_as_glued_byte(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_data = coverage.load_isa_spec(self.write_spec(root, "FADD"))
            self.write_objdump(root / "out", "floating", "FADD.FS")

            report = coverage.analyze_coverage(spec_data, root / "out")

            self.assertEqual(report["covered_spec_mnemonics"], 1)
            self.assertEqual(report["missing_mnemonics"], [])
            self.assertEqual(
                coverage.canonicalize_mnemonic("00HL.BSTART.STD"),
                "HL.BSTART.STD",
            )
            self.assertEqual(
                coverage.canonicalize_mnemonic("ffBSTART.STD"),
                "BSTART.STD",
            )

    def test_grouped_encoding_words_are_skipped_before_mnemonic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_data = coverage.load_isa_spec(self.write_spec(root, "L.BSTOP"))
            test_dir = root / "out" / "legacy"
            test_dir.mkdir(parents=True)
            (test_dir / "legacy.objdump").write_text(
                "       0: 0000000f 00000001    \tL.BSTOP\n"
            )

            report = coverage.analyze_coverage(spec_data, root / "out")

            self.assertEqual(report["covered_spec_mnemonics"], 1)
            self.assertEqual(report["unmapped_emitted_mnemonics"], [])

    def test_tepl_friendly_alias_covers_raw_carrier_not_generic_bstart(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_data = coverage.load_isa_spec(
                self.write_spec(root, "BSTART", "BSTART.TEPL")
            )
            self.write_objdump(root / "out", "tepl", "BSTART.TDIVS")

            report = coverage.analyze_coverage(spec_data, root / "out")

            self.assertEqual(report["covered_spec_mnemonics"], 1)
            self.assertEqual(report["missing_mnemonics"], ["BSTART"])
            self.assertEqual(report["mapped_by_test"]["tepl"], ["BSTART.TEPL"])

    def test_vec_projection_also_covers_tepl_carrier(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_data = coverage.load_isa_spec(self.write_spec(root, "BSTART.TEPL"))
            self.write_objdump(root / "out", "vec", "BSTART.VEC")

            report = coverage.analyze_coverage(spec_data, root / "out")

            self.assertEqual(report["covered_spec_mnemonics"], 1)
            self.assertEqual(report["missing_mnemonics"], [])

    def test_frame_vector_seed_uses_legal_minimum_stack_size(self) -> None:
        for mnemonic in ("FENTRY", "FEXIT", "FRET.RA", "FRET.STK"):
            self.assertEqual(
                vectors._default_field_value("DstBegin", 5, mnemonic), 10
            )
            self.assertEqual(vectors._default_field_value("DstEnd", 5, mnemonic), 10)
            self.assertEqual(vectors._default_field_value("uimm", 12, mnemonic), 8)

    def test_fail_under_returns_two_for_incomplete_observed_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_path = self.write_spec(root, "XOR", "SUB")
            out_dir = root / "out"
            self.write_objdump(out_dir, "one", "XOR")

            proc = self.run_script(
                SCRIPT,
                "--spec",
                spec_path,
                "--out-dir",
                out_dir,
                "--fail-under",
                100,
            )

            self.assertEqual(proc.returncode, 2)
            self.assertIn("observed disassembly mnemonic breadth", proc.stdout.lower())
            self.assertIn("coverage 50.0% < 100.0%", proc.stderr)

    def test_report_out_is_written_even_when_threshold_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_path = self.write_spec(root, "XOR", "SUB")
            out_dir = root / "out"
            report_path = root / "reports" / "coverage.json"
            self.write_objdump(out_dir, "one", "XOR")

            proc = self.run_script(
                SCRIPT,
                "--spec",
                spec_path,
                "--out-dir",
                out_dir,
                "--fail-under",
                100,
                "--report-out",
                report_path,
            )

            self.assertEqual(proc.returncode, 2)
            report = json.loads(report_path.read_text())
            self.assertEqual(report["covered_spec_mnemonics"], 1)
            self.assertEqual(report["missing_mnemonics"], ["SUB"])
            self.assertEqual(list(report_path.parent.glob(".coverage.json.*.tmp")), [])

    def test_report_out_matches_json_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_path = self.write_spec(root, "XOR")
            out_dir = root / "out"
            report_path = root / "coverage.json"
            self.write_objdump(out_dir, "one", "XOR")

            proc = self.run_script(
                SCRIPT,
                "--spec",
                spec_path,
                "--out-dir",
                out_dir,
                "--json",
                "--report-out",
                report_path,
            )

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(report_path.read_text()), json.loads(proc.stdout))

    def test_empty_output_is_an_error_not_zero_percent_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec_path = self.write_spec(root, "ADD")
            out_dir = root / "out"
            out_dir.mkdir()

            proc = self.run_script(
                SCRIPT, "--spec", spec_path, "--out-dir", out_dir, "--json"
            )

            self.assertEqual(proc.returncode, 1)
            self.assertIn("no *.objdump files found", proc.stderr)
            self.assertEqual(proc.stdout, "")

    def test_help_states_metric_scope(self) -> None:
        proc = self.run_script(SCRIPT, "--help")

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("observed disassembly mnemonic breadth", proc.stdout.lower())
        self.assertIn("not form-level", proc.stdout.lower())
        self.assertIn("not source-assembly", proc.stdout.lower())
        self.assertIn("not c-codegen", proc.stdout.lower())
        self.assertIn("--report-out", proc.stdout)


if __name__ == "__main__":
    unittest.main()
