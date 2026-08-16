#!/usr/bin/env python3
from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_ai_workload_flow
import run_model_diff_suite


class AiWorkloadFlowTests(unittest.TestCase):
    @staticmethod
    def set_elf_symbol_value(elf_path: Path, symbol_name: str, value: int) -> None:
        elf = bytearray(elf_path.read_bytes())
        endian = "<" if elf[5] == 1 else ">"
        header = struct.unpack_from(endian + "HHIQQQIHHHHHH", elf, 16)
        section_offset, section_entry_size, section_count = (
            header[5],
            header[10],
            header[11],
        )
        sections = [
            struct.unpack_from(
                endian + "IIQQQQIIQQ",
                elf,
                section_offset + index * section_entry_size,
            )
            for index in range(section_count)
        ]
        for section in sections:
            if section[1] not in (2, 11) or section[9] < 24:
                continue
            strings_section = sections[section[6]]
            strings = elf[
                strings_section[4] : strings_section[4] + strings_section[5]
            ]
            for symbol_offset in range(
                section[4], section[4] + section[5], section[9]
            ):
                name_offset = struct.unpack_from(endian + "I", elf, symbol_offset)[0]
                name = strings[name_offset:].split(b"\0", 1)[0].decode()
                if name == symbol_name:
                    struct.pack_into(endian + "Q", elf, symbol_offset + 8, value)
                    elf_path.write_bytes(elf)
                    return
        raise AssertionError(f"missing ELF symbol {symbol_name}")

    def test_release_strict_rejects_trace_only_payload(self) -> None:
        with self.assertRaisesRegex(
            run_model_diff_suite.ReleaseStrictError,
            r"immutable artifact provenance",
        ):
            run_model_diff_suite.validate_release_strict_payload(
                {"cases": [{"id": "trace-only", "status": "pass"}]}
            )

    def test_release_strict_accepts_complete_result_memory_proof(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, _ = self.release_strict_payload(Path(td))
            run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_reopens_and_rehashes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, paths = self.release_strict_payload(Path(td))
            paths["qemu"].write_bytes(b"mutated qemu")
            with self.assertRaisesRegex(
                run_model_diff_suite.ReleaseStrictError,
                r"qemu SHA-256 mismatch",
            ):
                run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_rejects_arbitrary_consumer_set(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, _ = self.release_strict_payload(Path(td))
            case = payload["cases"][0]
            case["result_memory"]["arbitrary"] = case["result_memory"].pop("compare")
            with self.assertRaisesRegex(
                run_model_diff_suite.ReleaseStrictError,
                r"consumer set",
            ):
                run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_rejects_missing_short_long_or_mutated_results(self) -> None:
        for mode in ("missing", "short", "long", "mutated"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as td:
                payload, paths = self.release_strict_payload(Path(td))
                result = paths["qemu_result"]
                if mode == "missing":
                    result.unlink()
                elif mode == "short":
                    result.write_bytes(b"short")
                elif mode == "long":
                    result.write_bytes(b"too-long-result")
                else:
                    result.write_bytes(b"87654321")
                with self.assertRaises(run_model_diff_suite.ReleaseStrictError):
                    run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_binds_comparisons_to_result_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, _ = self.release_strict_payload(Path(td))
            payload["cases"][0]["golden_comparisons"]["qemu"][
                "actual_sha256"
            ] = "0" * 64
            with self.assertRaisesRegex(
                run_model_diff_suite.ReleaseStrictError,
                r"comparison hash binding",
            ):
                run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_validates_manifest_size_against_elf_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, paths = self.release_strict_payload(Path(td))
            manifest = json.loads(paths["manifest"].read_text())
            manifest["result_memory"]["size"] = 7
            paths["manifest"].write_text(json.dumps(manifest), encoding="utf-8")
            payload["cases"][0]["provenance"]["artifacts"]["manifest"][
                "sha256"
            ] = run_ai_workload_flow.sha256_file(paths["manifest"])
            with self.assertRaisesRegex(
                run_model_diff_suite.ReleaseStrictError,
                r"ELF symbol size",
            ):
                run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_rejects_relocatable_elf(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, _ = self.release_strict_payload(Path(td), elf_kind="relocatable")
            with self.assertRaisesRegex(
                run_model_diff_suite.ReleaseStrictError, r"ET_EXEC"
            ):
                run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_rejects_undefined_result_symbol(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, _ = self.release_strict_payload(Path(td), elf_kind="undefined")
            with self.assertRaisesRegex(
                run_model_diff_suite.ReleaseStrictError, r"defined result symbol"
            ):
                run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_rejects_result_in_nonalloc_section(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, _ = self.release_strict_payload(Path(td), elf_kind="nonalloc")
            with self.assertRaisesRegex(
                run_model_diff_suite.ReleaseStrictError, r"allocatable section"
            ):
                run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_rejects_undefined_size_symbol(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, _ = self.release_strict_payload(
                Path(td), elf_kind="undefined_size"
            )
            with self.assertRaisesRegex(
                run_model_diff_suite.ReleaseStrictError, r"positive absolute symbol"
            ):
                run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_rejects_zero_result_address(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, _ = self.release_strict_payload(Path(td), elf_kind="zero_address")
            with self.assertRaisesRegex(
                run_model_diff_suite.ReleaseStrictError, r"nonzero address"
            ):
                run_model_diff_suite.validate_release_strict_payload(payload)

    def test_release_strict_rejects_result_range_outside_load_segment(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload, _ = self.release_strict_payload(Path(td), elf_kind="oversized")
            with self.assertRaisesRegex(
                run_model_diff_suite.ReleaseStrictError, r"PT_LOAD"
            ):
                run_model_diff_suite.validate_release_strict_payload(payload)

    def test_immutable_artifact_manifest_rejects_mutation_before_second_consumer(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            artifact = Path(td) / "case.elf"
            artifact.write_bytes(b"linked ELF bytes")
            manifest = run_ai_workload_flow.capture_immutable_artifacts(
                {"elf": artifact}
            )

            run_ai_workload_flow.verify_immutable_artifacts(
                manifest, {"elf": artifact}, consumer="qemu"
            )
            artifact.write_bytes(b"mutated ELF bytes")

            with self.assertRaisesRegex(
                run_ai_workload_flow.ArtifactIntegrityError,
                r"elf SHA-256 changed before model",
            ):
                run_ai_workload_flow.verify_immutable_artifacts(
                    manifest, {"elf": artifact}, consumer="model"
                )

    def test_immutable_artifact_manifest_requires_every_input(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "missing.bin"
            with self.assertRaisesRegex(
                run_ai_workload_flow.ArtifactIntegrityError,
                r"compiler is missing",
            ):
                run_ai_workload_flow.capture_immutable_artifacts(
                    {"compiler": missing}
                )

    def classify(self, text: str) -> tuple[str, str]:
        with tempfile.TemporaryDirectory() as td:
            log_path = Path(td) / "compile.log"
            log_path.write_text(text, encoding="utf-8")
            return run_ai_workload_flow.classify_supernpu_compile_failure(log_path)

    def test_supernpu_missing_linx_tile_api_is_benchmark_owned(self) -> None:
        owner, evidence = self.classify(
            "tileop_api.hpp:59:3: error: use of undeclared identifier 'TAND_Impl'\n"
        )
        self.assertEqual(owner, "benchmark")
        self.assertIn("tile API", evidence)

    def test_supernpu_unsupported_linx_runtime_contract_is_benchmark_owned(self) -> None:
        owner, evidence = self.classify(
            "error: static assertion failed due to requirement "
            "'tile_shape::isBoxedLayout == false': "
            "Linx smoke TCOPYIN supports only unboxed tiles\n"
        )
        self.assertEqual(owner, "benchmark")
        self.assertIn("runtime contract", evidence)

    def test_supernpu_matmul_acc_contract_is_benchmark_owned(self) -> None:
        owner, evidence = self.classify(
            "error: static assertion failed: Linx scalar MATMUL does not support ACC tile operands\n"
        )
        self.assertEqual(owner, "benchmark")
        self.assertIn("runtime contract", evidence)

    def test_supernpu_direct_boot_libc_dependency_is_benchmark_owned(self) -> None:
        owner, evidence = self.classify("ld.lld: error: undefined symbol: malloc\n")
        self.assertEqual(owner, "benchmark")
        self.assertIn("direct-boot runtime", evidence)

    def test_supernpu_stale_data_object_toolchain_is_benchmark_owned(self) -> None:
        owner, evidence = self.classify(
            "Building ../../../output/kernel/sort/topk/data_obj/input_131072.o\n"
            "clang -cc1as: error: unknown target triple 'linx64v5'\n"
            "Done building data object files\n"
        )
        self.assertEqual(owner, "benchmark")
        self.assertIn("source/toolchain", evidence)

    def test_supernpu_missing_benchmark_header_is_benchmark_owned(self) -> None:
        owner, evidence = self.classify("fatal error: 'benchmark.h' file not found\n")
        self.assertEqual(owner, "benchmark")
        self.assertIn("source/toolchain", evidence)

    def test_supernpu_missing_elf_uses_benchmark_classification_when_log_matches(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            log_path = Path(td) / "compile.log"
            elf_path = Path(td) / "missing.elf"
            log_path.write_text(
                "clang -cc1as: error: unknown target triple 'linx64v5'\n",
                encoding="utf-8",
            )

            owner, evidence = run_ai_workload_flow.classify_supernpu_missing_elf(
                log_path, elf_path
            )

        self.assertEqual(owner, "benchmark")
        self.assertIn("source/toolchain", evidence)

    def test_supernpu_missing_elf_without_known_marker_stays_compiler_owned(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            log_path = Path(td) / "compile.log"
            elf_path = Path(td) / "missing.elf"
            log_path.write_text("make: nothing to be done\n", encoding="utf-8")

            owner, evidence = run_ai_workload_flow.classify_supernpu_missing_elf(
                log_path, elf_path
            )

        self.assertEqual(owner, "compiler")
        self.assertIn("expected ELF was not produced", evidence)

    def test_unknown_supernpu_compile_failure_remains_compiler_owned(self) -> None:
        owner, evidence = self.classify("clang++: error: backend crashed unexpectedly\n")
        self.assertEqual(owner, "compiler")
        self.assertEqual(evidence, "SuperNPUBench compile failed")

    def test_case_filter_supports_exact_id_match(self) -> None:
        cases = [
            self.case("supernpu-tileop_api-TSub"),
            self.case("supernpu-tileop_api-TSubs"),
        ]
        selected = run_ai_workload_flow.filter_cases(
            cases, {1}, [], ["=supernpu-tileop_api-TSub"], 0
        )
        self.assertEqual([case.id for case in selected], ["supernpu-tileop_api-TSub"])

    def test_execution_stage_prefix_accepts_full_profile(self) -> None:
        flow = self.flow()
        stages = run_ai_workload_flow.selected_stages(flow, "smoke", [], None, None)

        run_ai_workload_flow.validate_execution_stage_prefix(flow, "smoke", [], stages)

    def test_execution_stage_prefix_rejects_profile_without_enabled_stages(self) -> None:
        flow = {
            "profiles": {"smoke": {"tiers": [0]}, "other": {"tiers": [0]}},
            "stages": [{"id": "other-only", "profiles": ["other"]}],
        }

        with self.assertRaisesRegex(
            SystemExit, r"profile smoke has no enabled execution stages"
        ):
            run_ai_workload_flow.validate_execution_stage_prefix(
                flow, "smoke", [], []
            )

    def test_execution_stage_prefix_accepts_repeated_stage_prefix(self) -> None:
        flow = self.flow()
        requested = ["source-contract", "compiler-contract"]
        stages = run_ai_workload_flow.selected_stages(
            flow, "smoke", requested, None, None
        )

        run_ai_workload_flow.validate_execution_stage_prefix(
            flow, "smoke", requested, stages
        )

    def test_execution_stage_prefix_accepts_stop_after(self) -> None:
        flow = self.flow()
        stages = run_ai_workload_flow.selected_stages(
            flow, "smoke", [], None, "compiler-contract"
        )

        run_ai_workload_flow.validate_execution_stage_prefix(flow, "smoke", [], stages)

    def test_execution_stage_prefix_rejects_qemu_only(self) -> None:
        flow = self.flow()
        requested = ["qemu-execution"]
        stages = run_ai_workload_flow.selected_stages(
            flow, "smoke", requested, None, None
        )

        with self.assertRaisesRegex(
            SystemExit,
            r"missing prerequisite stage\(s\): source-contract, compiler-contract",
        ):
            run_ai_workload_flow.validate_execution_stage_prefix(
                flow, "smoke", requested, stages
            )

    def test_execution_stage_prefix_rejects_non_root_start_at(self) -> None:
        flow = self.flow()
        stages = run_ai_workload_flow.selected_stages(
            flow, "smoke", [], "qemu-execution", None
        )

        with self.assertRaisesRegex(
            SystemExit,
            r"missing prerequisite stage\(s\): source-contract, compiler-contract",
        ):
            run_ai_workload_flow.validate_execution_stage_prefix(
                flow, "smoke", [], stages
            )

    def test_execution_stage_prefix_rejects_gap(self) -> None:
        flow = self.flow()
        requested = ["source-contract", "qemu-execution"]
        stages = run_ai_workload_flow.selected_stages(
            flow, "smoke", requested, None, None
        )

        with self.assertRaisesRegex(
            SystemExit,
            r"missing prerequisite stage\(s\): compiler-contract",
        ):
            run_ai_workload_flow.validate_execution_stage_prefix(
                flow, "smoke", requested, stages
            )

    def test_execution_stage_prefix_rejects_reordered_arguments(self) -> None:
        flow = self.flow()
        requested = ["compiler-contract", "source-contract"]
        stages = run_ai_workload_flow.selected_stages(
            flow, "smoke", requested, None, None
        )

        with self.assertRaisesRegex(
            SystemExit,
            r"expected canonical prefix: source-contract, compiler-contract",
        ):
            run_ai_workload_flow.validate_execution_stage_prefix(
                flow, "smoke", requested, stages
            )

    def test_invalid_execution_stage_prefix_creates_no_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "must-not-exist"
            with self.assertRaisesRegex(SystemExit, r"missing prerequisite stage"):
                run_ai_workload_flow.main(
                    [
                        "--profile",
                        "smoke",
                        "--stage",
                        "qemu-execution",
                        "--dry-run",
                        "--out-dir",
                        str(out_dir),
                    ]
                )

            self.assertFalse(out_dir.exists())

    def test_empty_execution_profile_fails_before_discovery_or_output(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            temp_dir = Path(td)
            flow_path = temp_dir / "flow.json"
            out_dir = temp_dir / "must-not-exist"
            flow_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "profiles": {
                            "smoke": {"tiers": [0]},
                            "other": {"tiers": [0]},
                        },
                        "stages": [
                            {
                                "id": "other-only",
                                "profiles": ["other"],
                                "owner": "test",
                                "hard_break": True,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(run_ai_workload_flow, "discover_cases") as discover:
                with self.assertRaisesRegex(
                    SystemExit, r"profile smoke has no enabled execution stages"
                ):
                    run_ai_workload_flow.main(
                        [
                            "--flow",
                            str(flow_path),
                            "--profile",
                            "smoke",
                            "--dry-run",
                            "--out-dir",
                            str(out_dir),
                        ]
                    )

            discover.assert_not_called()
            self.assertFalse(out_dir.exists())

    def test_supernpu_matmul_source_uses_type_when_testcase_is_generic(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            suite = Path(td)
            src_dir = suite / "src"
            src_dir.mkdir()
            hif4 = src_dir / "HiF4_HiF4.cpp"
            a16w4 = src_dir / "A16W4.cpp"
            hif4.write_text("hif4\n", encoding="utf-8")
            a16w4.write_text("a16w4\n", encoding="utf-8")

            self.assertEqual(
                run_ai_workload_flow.supernpu_source_paths(
                    suite, {"TESTCASE": "matmul", "TYPE": "HIF4_HIF4"}
                ),
                [hif4],
            )
            self.assertEqual(
                run_ai_workload_flow.supernpu_source_paths(
                    suite, {"TESTCASE": "matmul", "TYPE": "A16W4"}
                ),
                [a16w4],
            )

    def test_skill_evolve_note_preserves_no_update_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            payload = run_ai_workload_flow.write_skill_doc_evolution(
                Path(td), [], "no-update classifier-only evidence"
            )
        self.assertEqual(
            payload["skill_evolve"],
            "skill-evolve: no-update classifier-only evidence",
        )

    def test_v058_supernpu_smoke_comes_from_nested_pto_kernels(self) -> None:
        root = run_ai_workload_flow.repo_root()
        cases = run_ai_workload_flow.discover_cases(root)
        expected = {
            "supernpu-microbenchmark-vector-tadd_fp32_16x16",
            "supernpu-microbenchmark-memory-tload_fp32_16x16",
            "supernpu-microbenchmark-cube-tmatmul_fp16_64x64x64",
        }
        discovered = {case.id for case in cases if case.tier == 0 and case.kind == "supernpu"}
        self.assertTrue(expected <= discovered, discovered)
        for case in cases:
            if case.kind != "supernpu":
                continue
            self.assertIn("workloads/pto_kernels/benchmarks/supernpu", case.workdir.as_posix())
            self.assertNotIn("status/legacy", case.workdir.as_posix())

    def test_supernpu_tiers_reject_retired_manifest_layouts(self) -> None:
        self.assertEqual(
            run_ai_workload_flow.supernpu_tier(
                "microbenchmark/vector", {"TESTCASE": "tadd_fp32_16x16"}
            ),
            0,
        )
        self.assertEqual(
            run_ai_workload_flow.supernpu_tier(
                "one-level/kernel/deepseek", {"TESTCASE": "attention"}
            ),
            3,
        )
        with self.assertRaises(ValueError):
            run_ai_workload_flow.supernpu_tier(
                "tileop_api", {"TESTCASE": "retired-layout"}
            )

    def test_removed_pto_kernel_catalog_does_not_publish_stale_parity_cases(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        self.assertFalse(any(case.kind == "pto_kernel" for case in cases))
        retired = {"tile", "pto_parity", "deepseek_tilekernels"}
        self.assertTrue(retired.isdisjoint(case.suite for case in cases))

    def test_supernpu_make_command_pins_tileop_api_root(self) -> None:
        case = self.case("supernpu-microbenchmark-vector-tadd_fp32_16x16")
        case.metadata["make_vars"] = {"TESTCASE": "tadd_fp32_16x16"}
        command = run_ai_workload_flow.supernpu_make_command(
            case,
            {"clang": "/toolchain/bin/clang"},
            tileop_api_root=Path("/repo/tools/Linx-TileOP-API"),
            obj_root=Path("/tmp/out"),
        )
        self.assertIn("LINX_TILEOP_API_ROOT=/repo/tools/Linx-TileOP-API", command)
        self.assertIn("OBJ_ROOT=/tmp/out", command)

    def test_model_smoke_is_not_applicable_without_model_cases(self) -> None:
        qemu_case = self.case("non-model-case")
        qemu_case.model_eligible = False
        with tempfile.TemporaryDirectory() as td:
            state = run_ai_workload_flow.CaseState(
                case=qemu_case,
                case_dir=Path(td) / "cases" / qemu_case.id,
            )
            row = run_ai_workload_flow.model_build_smoke(
                run_ai_workload_flow.repo_root(),
                [state],
                {
                    "model_root": "/tmp/no-model-root",
                    "gfsim": "/tmp/no-gfsim",
                    "clangxx": "/tmp/no-clangxx",
                },
                dry_run=False,
                build_timeout=1,
                smoke_timeout=1,
                skip_build=False,
                smoke_elf_override=None,
            )

        self.assertEqual(row["status"], "not_applicable")
        self.assertEqual(row["commands"], [])
        self.assertEqual(
            state.stages["model-build-smoke"]["evidence"],
            "no selected model-eligible executable cases",
        )

    def case(self, case_id: str) -> run_ai_workload_flow.Case:
        return run_ai_workload_flow.Case(
            id=case_id,
            kind="supernpu",
            suite="tileop_api",
            tier=1,
            source_paths=[Path(f"{case_id}.cpp")],
            manifest_path=None,
            workdir=Path("."),
            compile_command=None,
            qemu_command=None,
            model_eligible=True,
            produces_elf=True,
            expected="test",
            metadata={},
        )

    def release_strict_payload(
        self, temp: Path, *, elf_kind: str = "executable"
    ) -> tuple[dict[str, object], dict[str, Path]]:
        llvm_mc = run_ai_workload_flow.repo_root() / "compiler/llvm/build-linxisa-clang/bin/llvm-mc"
        ld_lld = run_ai_workload_flow.repo_root() / "compiler/llvm/build-linxisa-clang/bin/ld.lld"
        self.assertTrue(llvm_mc.is_file(), llvm_mc)
        self.assertTrue(ld_lld.is_file(), ld_lld)
        asm = temp / "result.s"
        obj = temp / "case.o"
        elf = obj if elf_kind == "relocatable" else temp / "case.elf"
        section_flags = "" if elf_kind == "nonalloc" else "a"
        result_size = 1048576 if elf_kind == "oversized" else 8
        if elf_kind == "undefined":
            result_definition = ".weak cross_model_result\n"
        else:
            result_definition = (
                ".globl cross_model_result\n"
                ".type cross_model_result,@object\n"
                f".size cross_model_result,{result_size}\n"
                "cross_model_result:\n.zero 8\n"
            )
        size_definition = (
            ".weak cross_model_result_size\n"
            if elf_kind == "undefined_size"
            else ".globl cross_model_result_size\n"
            f".set cross_model_result_size,{result_size}\n"
        )
        asm.write_text(
            ".text\n.globl _start\n_start:\n.long 0\n"
            f'.section .result,"{section_flags}",@progbits\n'
            + result_definition
            + size_definition,
            encoding="utf-8",
        )
        built = subprocess.run(
            [str(llvm_mc), "-triple=linx64", "-filetype=obj", str(asm), "-o", str(obj)],
            capture_output=True,
        )
        self.assertEqual(built.returncode, 0, built.stderr.decode(errors="replace"))
        if elf_kind != "relocatable":
            link_command = [
                str(ld_lld),
                "-e",
                "_start",
                "-Ttext=0x10000",
                "--section-start=.result=0x20000",
                str(obj),
                "-o",
                str(elf),
            ]
            linked = subprocess.run(link_command, capture_output=True)
            self.assertEqual(
                linked.returncode, 0, linked.stderr.decode(errors="replace")
            )
            if elf_kind == "zero_address":
                self.set_elf_symbol_value(elf, "cross_model_result", 0)

        manifest_address = 0 if elf_kind in {"relocatable", "undefined", "zero_address"} else 0x20000

        manifest = temp / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "result_memory": {
                        "result_symbol": "cross_model_result",
                        "size_symbol": "cross_model_result_size",
                        "address": manifest_address,
                        "size": result_size,
                    }
                }
            ),
            encoding="utf-8",
        )
        golden = temp / "golden.bin"
        golden.write_bytes(b"12345678")
        paths: dict[str, Path] = {
            "compiler": temp / "compiler",
            "linker": temp / "linker",
            "qemu": temp / "qemu",
            "qemu_source_marker": temp / ".linx_qemu_clean_head",
            "ref": temp / "ref-model",
            "compare": temp / "compare-model",
            "elf": elf,
            "manifest": manifest,
            "golden": golden,
        }
        for name in (
            "compiler",
            "linker",
            "qemu",
            "qemu_source_marker",
            "ref",
            "compare",
        ):
            paths[name].write_bytes(name.encode())
        result_memory: dict[str, dict[str, object]] = {}
        for consumer in ("qemu", "ref", "compare"):
            result = temp / f"{consumer}.result.bin"
            result.write_bytes(golden.read_bytes())
            paths[f"{consumer}_result"] = result
            result_memory[consumer] = {
                "path": str(result),
                "sha256": run_ai_workload_flow.sha256_file(result),
                "size": 8,
            }
        artifacts = {
            name: {
                "path": str(path),
                "sha256": run_ai_workload_flow.sha256_file(path),
            }
            for name, path in paths.items()
            if name
            in {
                "compiler",
                "linker",
                "elf",
                "qemu",
                "qemu_source_marker",
                "ref",
                "compare",
                "manifest",
                "golden",
            }
        }
        for consumer in result_memory:
            result_memory[consumer]["consumer_sha256"] = artifacts[consumer]["sha256"]
        golden_hash = artifacts["golden"]["sha256"]
        comparisons = {
            consumer: {
                "status": "pass",
                "actual_sha256": result_memory[consumer]["sha256"],
                "golden_sha256": golden_hash,
                "consumer_sha256": artifacts[consumer]["sha256"],
                "size": 8,
            }
            for consumer in result_memory
        }
        pairwise = {}
        consumers = ("qemu", "ref", "compare")
        for index, left in enumerate(consumers):
            for right in consumers[index + 1 :]:
                pairwise[f"{left}:{right}"] = {
                    "status": "pass",
                    "left_sha256": result_memory[left]["sha256"],
                    "right_sha256": result_memory[right]["sha256"],
                    "left_consumer_sha256": artifacts[left]["sha256"],
                    "right_consumer_sha256": artifacts[right]["sha256"],
                    "size": 8,
                }
        payload: dict[str, object] = {
            "cases": [
                {
                    "id": "complete",
                    "status": "pass",
                    "provenance": {
                        "artifacts": artifacts,
                        "verified_after_run": True,
                    },
                    "result_memory": result_memory,
                    "golden_comparisons": comparisons,
                    "pairwise_comparisons": pairwise,
                }
            ]
        }
        return payload, paths

    def flow(self) -> dict[str, object]:
        root = run_ai_workload_flow.repo_root()
        return run_ai_workload_flow.load_flow(
            run_ai_workload_flow.default_flow_path(root)
        )


if __name__ == "__main__":
    unittest.main()
