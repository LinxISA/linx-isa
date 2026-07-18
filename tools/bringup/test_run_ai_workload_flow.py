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

    def test_pto_tload_store_catalog_case_has_standalone_harness(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        case = next(case for case in cases if case.id == "pto-kernel-tload_store")

        self.assertEqual(case.kind, "pto_kernel")
        self.assertTrue(case.produces_elf)
        self.assertTrue(case.model_eligible)
        self.assertEqual(case.metadata["standalone_harness"], "tload_store_i32")
        self.assertIn("-DPTO_QEMU_SMOKE=1", case.metadata["compile_defines"])

    def test_avs_full_parity_splits_qemu_and_model_closure(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        qemu_case = next(case for case in cases if case.id == "avs-pto-parity")
        model_case = next(case for case in cases if case.id == "avs-pto-parity-full-model")

        self.assertEqual(qemu_case.tier, 1)
        self.assertFalse(qemu_case.model_eligible)
        self.assertEqual(model_case.tier, 4)
        self.assertTrue(model_case.model_eligible)
        self.assertEqual(
            qemu_case.metadata["avs_extra_cflags"],
            model_case.metadata["avs_extra_cflags"],
        )

    def test_avs_softmax_2x_prefix_case_is_model_eligible(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        case = next(
            case
            for case in cases
            if case.id == "avs-pto-parity-prefix-flash-attention-softmax-2x"
        )

        self.assertEqual(case.tier, 1)
        self.assertTrue(case.model_eligible)
        self.assertTrue(case.produces_elf)
        self.assertIn("-DPTO_ATTENTION_SMOKE_SEQ=2", case.metadata["avs_extra_cflags"])
        self.assertIn("-DPTO_ATTENTION_LARGE_SMOKE_SEQ=2", case.metadata["avs_extra_cflags"])
        self.assertIn("-DPTO_FLASH_TILE_M=1", case.metadata["avs_extra_cflags"])
        self.assertIn(
            "-DPTO_PARITY_STOP_AFTER_STAGE=PTO_PARITY_STAGE_FLASH_ATTENTION_SOFTMAX",
            case.metadata["avs_extra_cflags"],
        )

    def test_model_smoke_is_not_applicable_without_model_cases(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        qemu_case = next(case for case in cases if case.id == "avs-pto-parity")
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

    def test_pto_gemm_catalog_case_has_standalone_harness(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        case = next(case for case in cases if case.id == "pto-kernel-gemm")

        self.assertEqual(case.kind, "pto_kernel")
        self.assertTrue(case.produces_elf)
        self.assertTrue(case.model_eligible)
        self.assertEqual(case.metadata["standalone_harness"], "gemm_i32")
        self.assertIn("-DPTO_QEMU_SMOKE=1", case.metadata["compile_defines"])

    def test_pto_integer_matmul_catalog_cases_have_standalone_harnesses(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        expected = {
            "pto-kernel-mamulb": "mamulb_i32",
            "pto-kernel-tmatmul_acc": "tmatmul_acc_i32",
        }

        for case_id, harness in expected.items():
            with self.subTest(case_id=case_id):
                case = next(case for case in cases if case.id == case_id)
                self.assertEqual(case.kind, "pto_kernel")
                self.assertTrue(case.produces_elf)
                self.assertTrue(case.model_eligible)
                self.assertEqual(case.metadata["standalone_harness"], harness)
                self.assertIn("-DPTO_QEMU_SMOKE=1", case.metadata["compile_defines"])

    def test_pto_float_elementwise_catalog_cases_have_standalone_harnesses(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        expected = {
            "pto-kernel-relu_fp32": "relu_f32",
        }

        for case_id, harness in expected.items():
            with self.subTest(case_id=case_id):
                case = next(case for case in cases if case.id == case_id)
                self.assertEqual(case.kind, "pto_kernel")
                self.assertTrue(case.produces_elf)
                self.assertTrue(case.model_eligible)
                self.assertEqual(case.metadata["standalone_harness"], harness)
                self.assertIn("-DPTO_QEMU_SMOKE=1", case.metadata["compile_defines"])

    def test_pto_layout_copy_catalog_cases_have_standalone_harnesses(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        expected = {
            "pto-kernel-flatten_fp32": "flatten_f32",
            "pto-kernel-reshape_fp32": "reshape_f32",
            "pto-kernel-squeeze_fp32": "squeeze_f32",
            "pto-kernel-unsqueeze_fp32": "unsqueeze_f32",
        }

        for case_id, harness in expected.items():
            with self.subTest(case_id=case_id):
                case = next(case for case in cases if case.id == case_id)
                self.assertEqual(case.kind, "pto_kernel")
                self.assertTrue(case.produces_elf)
                self.assertTrue(case.model_eligible)
                self.assertEqual(case.metadata["standalone_harness"], harness)
                self.assertIn("-DPTO_QEMU_SMOKE=1", case.metadata["compile_defines"])

    def test_pto_indexing_layout_catalog_cases_have_standalone_harnesses(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        expected = {
            "pto-kernel-argmax_fp32": "argmax_f32",
            "pto-kernel-concat_fp32": "concat_f32",
            "pto-kernel-gather_fp32": "gather_f32",
            "pto-kernel-hash_table_insert_fp32": "hash_table_insert_f32",
            "pto-kernel-hash_table_lookup_fp32": "hash_table_lookup_f32",
            "pto-kernel-permute_nhwc_nchw_fp32": "permute_nhwc_nchw_f32",
            "pto-kernel-scatter_fp32": "scatter_f32",
            "pto-kernel-slice_fp32": "slice_f32",
            "pto-kernel-split_fp32": "split_f32",
            "pto-kernel-stack_fp32": "stack_f32",
            "pto-kernel-transpose_large_fp32": "transpose_large_f32",
            "pto-kernel-unique_i32": "unique_i32",
            "pto-kernel-unsorted_segment_sum_fp32": "unsorted_segment_sum_f32",
            "pto-kernel-where_fp32": "where_f32",
        }

        for case_id, harness in expected.items():
            with self.subTest(case_id=case_id):
                case = next(case for case in cases if case.id == case_id)
                self.assertEqual(case.kind, "pto_kernel")
                self.assertTrue(case.produces_elf)
                self.assertTrue(case.model_eligible)
                self.assertEqual(case.metadata["standalone_harness"], harness)
                self.assertIn("-DPTO_QEMU_SMOKE=1", case.metadata["compile_defines"])

    def test_other_pto_catalog_cases_remain_compile_static(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        case = next(case for case in cases if case.id == "pto-kernel-gelu_fp32")

        self.assertEqual(case.kind, "pto_kernel")
        self.assertFalse(case.produces_elf)
        self.assertFalse(case.model_eligible)
        self.assertNotIn("standalone_harness", case.metadata)

    def test_pto_fp16_reuse_cases_have_standalone_harnesses(self) -> None:
        cases = run_ai_workload_flow.discover_cases(run_ai_workload_flow.repo_root())
        expected = {
            "pto-kernel-gemm_reuse_a_fp16": "gemm_reuse_a_f16",
            "pto-kernel-gemm_reuse_b_fp16": "gemm_reuse_b_f16",
            "pto-kernel-gemm_reuse_ab_fp16": "gemm_reuse_ab_f16",
        }

        for case_id, harness in expected.items():
            with self.subTest(case_id=case_id):
                case = next(case for case in cases if case.id == case_id)
                self.assertEqual(case.kind, "pto_kernel")
                self.assertTrue(case.produces_elf)
                self.assertTrue(case.model_eligible)
                self.assertEqual(case.metadata["standalone_harness"], harness)
                self.assertIn("-DPTO_QEMU_SMOKE=1", case.metadata["compile_defines"])

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
