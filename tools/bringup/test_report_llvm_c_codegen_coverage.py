#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_llvm_c_codegen_coverage as coverage


ROOT = Path(__file__).resolve().parents[2]
ANALYZER = ROOT / "avs/compiler/linx-llvm/tests/analyze_coverage.py"


def _write_objdump(path: Path, mnemonic: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "input.o:\tfile format elf64-linx\n\n"
        "Disassembly of section .text:\n\n"
        f"0000000000000000 <f>:\n       0: 25 81 21 06  {mnemonic}\ta0, a1, ->a0\n",
        encoding="utf-8",
    )


def _write_codegen_artifacts(root: Path, stem: str, mnemonic: str) -> None:
    out = root / "out" / stem
    out.mkdir(parents=True, exist_ok=True)
    asm = out / f"{stem}.s"
    obj = out / f"{stem}.o"
    asm.write_text(
        f"\t{mnemonic}\ta0, a1, ->a0\n"
        '\t.ident\t"clang version test-provenance"\n',
        encoding="utf-8",
    )
    obj.write_bytes(b"ELF-test-object")
    _write_objdump(out / f"{stem}.objdump", mnemonic)


def _write_tool(path: Path, identity: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{identity}'\n", encoding="utf-8")
    path.chmod(0o755)


def _manifest_fixture(root: Path) -> tuple[dict, dict[str, Path]]:
    c_dir = root / "c"
    asm_dir = root / "asm"
    out_dir = root / "out"
    c_dir.mkdir()
    asm_dir.mkdir()
    source = c_dir / "01_real.c"
    source.write_text("int f(void) { return 1; }\n", encoding="utf-8")
    _write_codegen_artifacts(root, "01_real", "addw")
    clang = root / "tools/clang"
    objdump_tool = root / "tools/llvm-objdump"
    _write_tool(clang, "clang version fixture")
    _write_tool(objdump_tool, "llvm-objdump version fixture")
    record = {
        "source": "c/01_real.c",
        "source_sha256": coverage._sha256(source),
        "generated_assembly": "out/01_real/01_real.s",
        "generated_assembly_sha256": coverage._sha256(out_dir / "01_real/01_real.s"),
        "object": "out/01_real/01_real.o",
        "object_sha256": coverage._sha256(out_dir / "01_real/01_real.o"),
        "objdump": "out/01_real/01_real.objdump",
        "objdump_sha256": coverage._sha256(out_dir / "01_real/01_real.objdump"),
        "compile_flags": coverage._expected_compile_flags(
            root, "linx64-linx-none-elf", "01_real"
        ),
    }
    manifest = {
        "schema_version": coverage.MANIFEST_SCHEMA_VERSION,
        "status": "complete",
        "target": "linx64-linx-none-elf",
        "extra_cflags": [],
        "source_count": 1,
        "tools": {
            "clang": {
                "path": "tools/clang",
                "sha256": coverage._sha256(clang),
                "identity": "clang version fixture",
            },
            "llvm_objdump": {
                "path": "tools/llvm-objdump",
                "sha256": coverage._sha256(objdump_tool),
                "identity": "llvm-objdump version fixture",
            },
        },
        "records": [record],
    }
    return manifest, {
        "c_dir": c_dir,
        "out_dir": out_dir,
        "clang": clang,
        "objdump": objdump_tool,
    }


class LLVMCodeGenCoverageTests(unittest.TestCase):
    def _verify_fixture_manifest(
        self, root: Path, manifest: dict, paths: dict[str, Path]
    ) -> None:
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        coverage._verify_build_manifest(
            root=root,
            manifest_path=manifest_path,
            c_source_dir=paths["c_dir"],
            out_dir=paths["out_dir"],
            clang_path=paths["clang"],
            llvm_objdump_path=paths["objdump"],
            replay=False,
        )

    def _fixture(self, base: Path) -> tuple[Path, Path, Path, Path]:
        c_dir = base / "c"
        asm_dir = base / "asm"
        out_dir = base / "out"
        c_dir.mkdir()
        asm_dir.mkdir()
        spec = base / "spec.json"
        spec.write_text(
            json.dumps(
                {
                    "instructions": [
                        {"mnemonic": "ADDW", "group": "Integer"},
                        {"mnemonic": "SUBW", "group": "Integer"},
                        {"mnemonic": "MULW", "group": "Integer"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        return c_dir, asm_dir, out_dir, spec

    def test_generated_and_assembly_artifacts_cannot_inflate_c_codegen(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            c_dir, asm_dir, out_dir, spec = self._fixture(root)
            source = c_dir / "01_real.c"
            source.write_text("int f(int x) { return x + 1; }\n", encoding="utf-8")
            _write_codegen_artifacts(root, "01_real", "addw")
            directed = c_dir / "02_inline.c"
            directed.write_text(
                '__asm__("subw a0, a1, ->a0");\n', encoding="utf-8"
            )
            _write_codegen_artifacts(root, "02_inline", "subw")

            (asm_dir / "41_forms.s").write_text("mulw a0, a1, ->a0\n", encoding="utf-8")
            _write_objdump(out_dir / "41_forms/41_forms.objdump", "mulw")
            _write_objdump(out_dir / "99_spec_decode/99_spec_decode.objdump", "subw")
            _write_objdump(
                out_dir / "99_spec_decode/99_spec_decode.roundtrip.objdump", "mulw"
            )

            report = coverage.build_report(
                root=root,
                spec_path=spec,
                analyzer_path=ANALYZER,
                c_source_dir=c_dir,
                asm_source_dir=asm_dir,
                out_dir=out_dir,
                generated_at_utc="test-time",
            )

            self.assertEqual(report["direct"]["covered_mnemonics"], ["ADDW", "SUBW"])
            self.assertEqual(report["direct"]["coverage_count"], 2)
            self.assertEqual(report["pure_codegen"]["direct_covered_mnemonics"], ["ADDW"])
            self.assertEqual(report["pure_codegen"]["direct_coverage_count"], 1)
            self.assertEqual(report["included_artifact_count"], 2)
            excluded = {item["artifact"]: item["reason"] for item in report["excluded_artifacts"]}
            self.assertIn("out/99_spec_decode/99_spec_decode.objdump", excluded)
            self.assertIn("generated ISA disassembly vector", excluded["out/99_spec_decode/99_spec_decode.objdump"])
            self.assertIn(
                "roundtrip-only",
                excluded["out/99_spec_decode/99_spec_decode.roundtrip.objdump"],
            )
            self.assertIn("hand-authored assembly", excluded["out/41_forms/41_forms.objdump"])

    def test_stale_artifact_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            c_dir, asm_dir, out_dir, spec = self._fixture(root)
            source = c_dir / "01_real.c"
            source.write_text("int f(void) { return 1; }\n", encoding="utf-8")
            _write_codegen_artifacts(root, "01_real", "addw")
            old = source.stat().st_mtime - 10
            artifact = out_dir / "01_real/01_real.objdump"
            os.utime(artifact, (old, old))

            with self.assertRaisesRegex(coverage.ProvenanceError, "stale artifact"):
                coverage.build_report(
                    root=root,
                    spec_path=spec,
                    analyzer_path=ANALYZER,
                    c_source_dir=c_dir,
                    asm_source_dir=asm_dir,
                    out_dir=out_dir,
                )

    def test_wrong_compiler_identity_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            c_dir, asm_dir, out_dir, spec = self._fixture(root)
            (c_dir / "01_real.c").write_text("int f(void) { return 1; }\n")
            _write_codegen_artifacts(root, "01_real", "addw")

            with self.assertRaisesRegex(
                coverage.ProvenanceError, "does not match canonical Clang"
            ):
                coverage.build_report(
                    root=root,
                    spec_path=spec,
                    analyzer_path=ANALYZER,
                    c_source_dir=c_dir,
                    asm_source_dir=asm_dir,
                    out_dir=out_dir,
                    expected_compiler_identity="clang version other-build",
                )

    def test_partial_manifest_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest, paths = _manifest_fixture(root)
            manifest["status"] = "incomplete"
            with self.assertRaisesRegex(coverage.ProvenanceError, "not complete"):
                self._verify_fixture_manifest(root, manifest, paths)

            manifest["status"] = "complete"
            manifest["records"] = []
            manifest["source_count"] = 0
            with self.assertRaisesRegex(coverage.ProvenanceError, "source set"):
                self._verify_fixture_manifest(root, manifest, paths)

    def test_wrong_tool_or_artifact_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest, paths = _manifest_fixture(root)
            cases = (
                (("tools", "clang", "sha256"), "clang SHA"),
                (("records", 0, "object_sha256"), "object hash"),
                (("records", 0, "objdump_sha256"), "objdump hash"),
            )
            for key_path, message in cases:
                with self.subTest(field=key_path):
                    mutated = deepcopy(manifest)
                    target = mutated
                    for key in key_path[:-1]:
                        target = target[key]
                    target[key_path[-1]] = "0" * 64
                    with self.assertRaisesRegex(coverage.ProvenanceError, message):
                        self._verify_fixture_manifest(root, mutated, paths)

    def test_injected_compile_flag_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest, paths = _manifest_fixture(root)
            manifest["records"][0]["compile_flags"].extend(
                ["-include", "/tmp/injected-isa.h"]
            )
            with self.assertRaisesRegex(
                coverage.ProvenanceError, "canonical run.sh policy"
            ):
                self._verify_fixture_manifest(root, manifest, paths)

            manifest["records"][0]["compile_flags"] = coverage._expected_compile_flags(
                root, "linx64-linx-none-elf", "01_real"
            )
            manifest["extra_cflags"] = ["-DINJECTED=1"]
            with self.assertRaisesRegex(coverage.ProvenanceError, "EXTRA_CFLAGS"):
                self._verify_fixture_manifest(root, manifest, paths)

    def test_self_consistent_linx32_target_and_flags_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest, paths = _manifest_fixture(root)
            manifest["target"] = "linx32-linx-none-elf"
            manifest["records"][0]["compile_flags"] = coverage._expected_compile_flags(
                root, "linx32-linx-none-elf", "01_real"
            )
            with self.assertRaisesRegex(coverage.ProvenanceError, "not canonical"):
                self._verify_fixture_manifest(root, manifest, paths)

    def test_asm_volatile_and_builtin_spellings_are_source_directed(self) -> None:
        hostile_sources = (
            'asm volatile("add a0, a1, ->a0");',
            '__asm volatile("add a0, a1, ->a0");',
            '__asm__ __volatile__("add a0, a1, ->a0");',
            '#define RAW_OP() asm volatile("add a0, a1, ->a0")',
            '__builtin_prefetch(pointer);',
        )
        for source in hostile_sources:
            with self.subTest(source=source):
                self.assertIsNotNone(coverage.SOURCE_DIRECTIVE_RE.search(source))

    def test_wrong_output_lane_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                rc = coverage.main(
                    [
                        "--repo-root",
                        str(ROOT),
                        "--compiler-out-dir",
                        str(Path(td) / "not-canonical"),
                        "--report-out",
                        str(Path(td) / "report.json"),
                        "--out-md",
                        str(Path(td) / "report.md"),
                    ]
                )
            self.assertEqual(rc, 2)
            self.assertIn("must use canonical lane", stderr.getvalue())

    def test_checked_in_json_and_markdown_publish_same_boundary(self) -> None:
        report_path = ROOT / "docs/bringup/gates/llvm_c_codegen_coverage_latest.json"
        markdown_path = ROOT / "docs/bringup/gates/llvm_c_codegen_coverage_latest.md"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        markdown = markdown_path.read_text(encoding="utf-8")

        self.assertEqual(report["schema_version"], coverage.SCHEMA_VERSION)
        self.assertEqual(report["direct"]["coverage_count"], 120)
        self.assertEqual(report["alias_closure"]["coverage_count"], 121)
        self.assertEqual(report["pure_codegen"]["direct_coverage_count"], 118)
        self.assertEqual(report["pure_codegen"]["alias_closure_coverage_count"], 119)
        self.assertEqual(report["spec_unique_mnemonics"], 711)
        self.assertIn("`120/711`", markdown)
        self.assertIn("`121/711`", markdown)
        self.assertIn("`118/711`", markdown)
        self.assertIn("`119/711`", markdown)
        self.assertIsNone(report["threshold"])
        self.assertIsNone(report["threshold_met"])
        self.assertEqual(report["inputs"]["manifest_status"], "complete")
        self.assertEqual(report["inputs"]["target"], coverage.CANONICAL_TARGET)
        self.assertEqual(report["inputs"]["replay_verified_source_count"], 40)
        self.assertEqual(len(report["inputs"]["clang_sha256"]), 64)
        excluded = {item["artifact"] for item in report["excluded_artifacts"]}
        self.assertIn(
            "avs/compiler/linx-llvm/tests/out/99_spec_decode/99_spec_decode.objdump",
            excluded,
        )


if __name__ == "__main__":
    unittest.main()
