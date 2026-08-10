#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_ai_workload_flow


class AiWorkloadFlowTests(unittest.TestCase):
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

    def flow(self) -> dict[str, object]:
        root = run_ai_workload_flow.repo_root()
        return run_ai_workload_flow.load_flow(
            run_ai_workload_flow.default_flow_path(root)
        )


if __name__ == "__main__":
    unittest.main()
