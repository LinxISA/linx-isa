#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import report_llvm_c_codegen_coverage as coverage


ROOT = Path(__file__).resolve().parents[2]
ANALYZER = ROOT / "avs/compiler/linx-llvm/tests/analyze_coverage.py"
MANIFEST_HELPER = ROOT / "avs/compiler/linx-llvm/tests/write_c_codegen_manifest.py"


def _load_manifest_helper():
    spec = importlib.util.spec_from_file_location("write_c_codegen_manifest", MANIFEST_HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def _reachable_contract_fixture() -> tuple[dict, dict]:
    baseline = ["BASE.0", "BASE.1", "BASE.2"]
    tranche_one = ["DELTA.1", "DELTA.2"]
    tranche_two = ["DELTA.3"]
    tranche_one_sources = ["c/41_plain.c", "c/42_plain.c"]
    tranche_two_sources = ["c/43_plain.c"]
    observed_by_source = {
        "c/baseline.c": baseline,
        tranche_one_sources[0]: tranche_one[:1],
        tranche_one_sources[1]: tranche_one[1:],
        tranche_two_sources[0]: tranche_two,
    }
    entries = [
        {
            "mnemonic": mnemonic,
            "witness_source": "c/baseline.c",
            "evidence_kind": "direct",
        }
        for mnemonic in baseline
    ]
    entries.extend(
        {
            "mnemonic": mnemonic,
            "witness_source": tranche_one_sources[index],
            "evidence_kind": "direct",
        }
        for index, mnemonic in enumerate(tranche_one)
    )
    entries.extend(
        {
            "mnemonic": mnemonic,
            "witness_source": tranche_two_sources[0],
            "evidence_kind": "direct",
        }
        for mnemonic in tranche_two
    )
    contract = {
        "schema_version": coverage.REACHABLE_CONTRACT_SCHEMA_VERSION,
        "target": coverage.CANONICAL_TARGET,
        "status": "frozen",
        "tranches": [
            {
                "id": "plain-c-1",
                "sources": tranche_one_sources,
                "baseline_alias_closure_count": len(baseline),
                "new_direct_mnemonics": tranche_one,
                "expected_coverage_count": len(baseline + tranche_one),
            },
            {
                "id": "plain-c-2",
                "sources": tranche_two_sources,
                "baseline_alias_closure_count": len(baseline + tranche_one),
                "new_direct_mnemonics": tranche_two,
                "expected_coverage_count": len(
                    baseline + tranche_one + tranche_two
                ),
            },
        ],
        "expected_coverage_count": len(baseline + tranche_one + tranche_two),
        "entries": entries,
    }
    context = {
        "spec_mnemonics": set(baseline + tranche_one + tranche_two),
        "observed_by_source": observed_by_source,
        "included": [
            {"source": "c/baseline.c", "provenance_class": "pure_c_cpp"},
            *[
                {"source": source, "provenance_class": "pure_c_cpp"}
                for source in tranche_one_sources + tranche_two_sources
            ],
        ],
        "pure_direct": set(baseline + tranche_one + tranche_two),
        "pure_closed": set(baseline + tranche_one + tranche_two),
    }
    return contract, context


class LLVMCodeGenCoverageTests(unittest.TestCase):
    def test_compiler_identity_must_match_current_llvm_head(self) -> None:
        head = "a" * 40
        identity = (
            "clang version 23.0.0git "
            f"(https://github.com/LinxISA/llvm-project.git {head})"
        )

        self.assertEqual(
            coverage._verify_compiler_identity_revision(identity, head), head
        )
        with self.assertRaisesRegex(coverage.ProvenanceError, "does not match"):
            coverage._verify_compiler_identity_revision(identity, "b" * 40)
        with self.assertRaisesRegex(coverage.ProvenanceError, "does not report"):
            coverage._verify_compiler_identity_revision(
                "clang version 23.0.0git", head
            )

    def test_dirty_llvm_worktree_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            llvm_root = root / "compiler/llvm"
            llvm_root.mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(llvm_root)], check=True)
            subprocess.run(
                ["git", "-C", str(llvm_root), "config", "user.name", "Test"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(llvm_root), "config", "user.email", "test@example.com"],
                check=True,
            )
            tracked = llvm_root / "tracked.txt"
            tracked.write_text("clean\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(llvm_root), "add", "tracked.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(llvm_root), "commit", "-q", "-m", "fixture"],
                check=True,
            )

            coverage._verify_clean_llvm_worktree(root)
            tracked.write_text("dirty\n", encoding="utf-8")
            with self.assertRaisesRegex(
                coverage.ProvenanceError, "worktree is dirty"
            ):
                coverage._verify_clean_llvm_worktree(root)

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

    def _verify_contract_fixture(
        self,
        root: Path,
        contract: dict,
        context: dict,
        *,
        enforce_canonical_anchor: bool = False,
    ) -> dict:
        contract_path = root / "contract.json"
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        return coverage._verify_reachable_contract(
            root=root,
            contract_path=contract_path,
            spec_mnemonics=context["spec_mnemonics"],
            observed_by_source=context["observed_by_source"],
            included=context["included"],
            pure_direct=context["pure_direct"],
            pure_closed=context["pure_closed"],
            enforce_canonical_anchor=enforce_canonical_anchor,
        )

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

    def test_default_paths_and_temp_aliases_use_shared_canonical_resolution(self) -> None:
        args = coverage._parse_args([])
        self.assertEqual(
            args.clang, "compiler/llvm/build-linxisa-clang/bin/clang"
        )
        self.assertEqual(
            args.compiler_out_dir, "avs/compiler/linx-llvm/tests/out"
        )
        producer = _load_manifest_helper()
        with tempfile.TemporaryDirectory(dir="/tmp") as td:
            root = Path(td)
            real_tool = root / "clang-real"
            real_tool.write_bytes(b"tool")
            tool_alias = root / "clang"
            tool_alias.symlink_to(real_tool.name)
            self.assertEqual(
                producer._rel(tool_alias, root),
                coverage._relative(tool_alias, root),
            )
            self.assertEqual(producer._rel(tool_alias, root), "clang-real")

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

    def test_reachable_contract_rejects_hostile_entries(self) -> None:
        base, context = _reachable_contract_fixture()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.assertEqual(
                self._verify_contract_fixture(root, base, context)["status"], "PASS"
            )
            cases = []

            unknown = deepcopy(base)
            unknown["entries"][0]["mnemonic"] = "UNKNOWN"
            cases.append((unknown, "mnemonic is unknown"))

            duplicate = deepcopy(base)
            duplicate["entries"][1] = deepcopy(duplicate["entries"][0])
            cases.append((duplicate, "duplicated"))

            missing = deepcopy(base)
            missing["entries"][0]["witness_source"] = "c/missing.c"
            cases.append((missing, "witness is missing"))

            bad_kind = deepcopy(base)
            bad_kind["entries"][0]["evidence_kind"] = "inferred"
            cases.append((bad_kind, "evidence kind is unknown"))

            old_as_new = deepcopy(base)
            old_as_new["tranches"][0]["new_direct_mnemonics"][0] = base[
                "entries"
            ][0]["mnemonic"]
            cases.append((old_as_new, "witness is outside tranche sources"))

            synchronized_delete = deepcopy(base)
            removed = synchronized_delete["tranches"][-1][
                "new_direct_mnemonics"
            ].pop()
            synchronized_delete["entries"] = [
                entry
                for entry in synchronized_delete["entries"]
                if entry["mnemonic"] != removed
            ]
            synchronized_delete["tranches"][-1]["expected_coverage_count"] -= 1
            synchronized_delete["expected_coverage_count"] -= 1
            cases.append((synchronized_delete, "mnemonic list is unknown"))

            deleted_tranche = deepcopy(base)
            removed_tranche = deleted_tranche["tranches"].pop()
            removed_mnemonics = set(removed_tranche["new_direct_mnemonics"])
            deleted_tranche["entries"] = [
                entry
                for entry in deleted_tranche["entries"]
                if entry["mnemonic"] not in removed_mnemonics
            ]
            deleted_tranche["expected_coverage_count"] -= len(removed_mnemonics)
            cases.append((deleted_tranche, "contract mnemonic set differs"))

            for contract, message in cases:
                with self.subTest(message=message):
                    with self.assertRaisesRegex(coverage.ProvenanceError, message):
                        self._verify_contract_fixture(root, contract, context)

            directed_context = deepcopy(context)
            directed_context["included"][1]["provenance_class"] = "source_directed"
            with self.assertRaisesRegex(coverage.ProvenanceError, "source-directed"):
                self._verify_contract_fixture(root, base, directed_context)

    def test_reachable_contract_survives_new_lowering_in_older_source(self) -> None:
        contract, context = _reachable_contract_fixture()
        # A generic backend improvement can make a pre-tranche source emit an
        # instruction whose reviewed witness remains in a later tranche. The
        # historical chain stays valid as long as current pure-C disassembly
        # still proves every frozen entry and contains no unregistered gap.
        context["observed_by_source"]["c/baseline.c"].append("DELTA.3")
        with tempfile.TemporaryDirectory() as td:
            result = self._verify_contract_fixture(Path(td), contract, context)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["coverage_count"], 6)

    def test_canonical_anchor_rejects_coordinated_corpus_and_contract_shrink(
        self,
    ) -> None:
        contract = json.loads(
            (ROOT / coverage.CANONICAL_REACHABLE_CONTRACT_PATH).read_text(
                encoding="utf-8"
            )
        )
        report = json.loads(
            (
                ROOT / "docs/bringup/gates/llvm_c_codegen_coverage_latest.json"
            ).read_text(encoding="utf-8")
        )
        spec_mnemonics = {
            instruction["mnemonic"].upper()
            for instruction in json.loads(
                (ROOT / "isa/v0.56/linxisa-v0.56.json").read_text(
                    encoding="utf-8"
                )
            )["instructions"]
        }
        context = {
            "spec_mnemonics": spec_mnemonics,
            "observed_by_source": deepcopy(report["observed_by_source"]),
            "included": deepcopy(report["included_artifacts"]),
            "pure_direct": set(
                report["pure_codegen"]["direct_covered_mnemonics"]
            ),
            "pure_closed": set(
                report["pure_codegen"]["alias_closure_covered_mnemonics"]
            ),
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            anchored = self._verify_contract_fixture(
                root,
                contract,
                context,
                enforce_canonical_anchor=True,
            )
            self.assertEqual(
                anchored["canonical_non_regression_anchor"]["status"], "PASS"
            )

            renamed_contract = deepcopy(contract)
            renamed_contract["tranches"][-1]["id"] = "renamed-tranche"
            self.assertEqual(
                self._verify_contract_fixture(
                    root, renamed_contract, context
                )["coverage_count"],
                146,
            )
            with self.assertRaisesRegex(
                coverage.ProvenanceError, "non-regression anchor"
            ):
                self._verify_contract_fixture(
                    root,
                    renamed_contract,
                    context,
                    enforce_canonical_anchor=True,
                )

            shrunk_contract = deepcopy(contract)
            removed_tranche = shrunk_contract["tranches"].pop()
            removed_source = removed_tranche["sources"][0]
            removed_mnemonics = set(removed_tranche["new_direct_mnemonics"])
            shrunk_contract["entries"] = [
                entry
                for entry in shrunk_contract["entries"]
                if entry["mnemonic"] not in removed_mnemonics
            ]
            shrunk_contract["expected_coverage_count"] = removed_tranche[
                "baseline_alias_closure_count"
            ]

            shrunk_context = deepcopy(context)
            shrunk_context["observed_by_source"].pop(removed_source)
            for source, mnemonics in shrunk_context["observed_by_source"].items():
                shrunk_context["observed_by_source"][source] = [
                    mnemonic
                    for mnemonic in mnemonics
                    if mnemonic not in removed_mnemonics
                ]
            shrunk_context["included"] = [
                artifact
                for artifact in shrunk_context["included"]
                if artifact["source"] != removed_source
            ]
            shrunk_context["pure_direct"] -= removed_mnemonics
            shrunk_context["pure_closed"], _ = coverage._apply_alias_closure(
                shrunk_context["pure_direct"], spec_mnemonics
            )

            unanchored = self._verify_contract_fixture(
                root, shrunk_contract, shrunk_context
            )
            self.assertEqual(unanchored["coverage_count"], 143)
            self.assertIsNone(unanchored["canonical_non_regression_anchor"])
            with self.assertRaisesRegex(
                coverage.ProvenanceError, "non-regression minimum"
            ):
                self._verify_contract_fixture(
                    root,
                    shrunk_contract,
                    shrunk_context,
                    enforce_canonical_anchor=True,
                )

    def test_canonical_anchor_digest_covers_every_tranche_descriptor_field(
        self,
    ) -> None:
        contract = json.loads(
            (ROOT / coverage.CANONICAL_REACHABLE_CONTRACT_PATH).read_text(
                encoding="utf-8"
            )
        )
        tranches = contract["tranches"]
        expected = coverage.CANONICAL_REACHABLE_CONTRACT_ANCHOR[
            "tranche_chain_sha256"
        ]
        self.assertEqual(coverage._tranche_chain_sha256(tranches), expected)

        mutations = []
        for field, value in (
            ("id", "renamed-tranche"),
            ("sources", ["c/replaced.c"]),
            ("baseline_alias_closure_count", 118),
            ("expected_coverage_count", 142),
            ("new_direct_mnemonics", ["REPLACED"]),
        ):
            mutated = deepcopy(tranches)
            mutated[-1][field] = value
            mutations.append((field, mutated))
        for field, mutated in mutations:
            with self.subTest(field=field):
                self.assertNotEqual(
                    coverage._tranche_chain_sha256(mutated), expected
                )

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
        self.assertEqual(report["direct"]["coverage_count"], 146)
        self.assertEqual(report["alias_closure"]["coverage_count"], 147)
        self.assertEqual(report["pure_codegen"]["direct_coverage_count"], 145)
        self.assertEqual(report["pure_codegen"]["alias_closure_coverage_count"], 146)
        self.assertEqual(report["spec_unique_mnemonics"], 710)
        self.assertIn("`146/710`", markdown)
        self.assertIn("`147/710`", markdown)
        self.assertIn("`145/710`", markdown)
        self.assertIn("`146/146` (`PASS`)", markdown)
        self.assertIn("`barbara-liskov-plain-c-sub-immediate`", markdown)
        self.assertIn("`HL.SUBIW`", markdown)
        self.assertIsNone(report["threshold"])
        self.assertIsNone(report["threshold_met"])
        self.assertEqual(report["inputs"]["manifest_status"], "complete")
        self.assertEqual(report["inputs"]["target"], coverage.CANONICAL_TARGET)
        self.assertEqual(report["inputs"]["replay_verified_source_count"], 44)
        self.assertEqual(len(report["inputs"]["clang_sha256"]), 64)
        contract = report["plain_c_reachable_contract"]
        self.assertEqual(contract["status"], "PASS")
        self.assertEqual(contract["coverage_count"], 146)
        self.assertEqual(contract["coverage_denominator"], 146)
        self.assertEqual(len(contract["new_direct_mnemonics"]), 27)
        self.assertEqual(contract["baseline_alias_closure_count"], 119)
        self.assertEqual(len(contract["tranches"]), 3)
        self.assertEqual(
            contract["canonical_non_regression_anchor"],
            {
                "status": "PASS",
                **coverage.CANONICAL_REACHABLE_CONTRACT_ANCHOR,
            },
        )
        self.assertEqual(
            contract["tranches"][-1]["new_direct_mnemonics"],
            [
                "HL.SUBI",
                "HL.SUBIW",
                "SUBI",
            ],
        )
        excluded = {item["artifact"] for item in report["excluded_artifacts"]}
        self.assertIn(
            "avs/compiler/linx-llvm/tests/out/99_spec_decode/99_spec_decode.objdump",
            excluded,
        )


if __name__ == "__main__":
    unittest.main()
