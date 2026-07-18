#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import refresh_qemu_executable_coverage as refresh


class RefreshQemuExecutableCoverageTests(unittest.TestCase):
    def test_relative_candidate_is_preferred_without_pc_shift_guessing(self) -> None:
        self.assertEqual(refresh._select_candidate(6, [2, 6, 10], "form"), 6)
        self.assertEqual(refresh._select_candidate(6, [10], "form"), 10)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            refresh._select_candidate(6, [2, 10], "form")
        with self.assertRaisesRegex(ValueError, "no fresh"):
            refresh._select_candidate(6, [], "form")

    def test_manifest_requires_unique_forms_and_all_suites(self) -> None:
        evidence = [
            {"suite": suite, "form_id": f"form-{index}"}
            for index, suite in enumerate(refresh.SUITE_ORDER)
        ]
        grouped = refresh._suite_entries({"evidence": evidence})
        self.assertEqual(set(grouped), set(refresh.SUITE_ORDER))
        evidence[-1]["form_id"] = evidence[0]["form_id"]
        with self.assertRaisesRegex(ValueError, "duplicate form_id"):
            refresh._suite_entries({"evidence": evidence})

    def test_bundle_check_rejects_split_or_absolute_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bundle = root / "bundle"
            bundle.mkdir()
            names = ["test.elf", "test.o", "source.o", "watch.log", "uart.log"]
            for name in names:
                (bundle / name).write_bytes(b"evidence")
            run = {
                "artifacts": {
                    "elf": {"path": "bundle/test.elf"},
                    "object": {"path": "bundle/test.o"},
                    "objects": [{"path": "bundle/source.o"}],
                    "pc_watch": {"path": "bundle/watch.log"},
                    "uart": {"path": "bundle/uart.log"},
                }
            }
            run_path = bundle / "run.json"
            run_path.write_text(json.dumps(run), encoding="utf-8")
            refresh._check_bundle_artifacts(root, bundle, run_path)

            run["artifacts"]["uart"]["path"] = "outside.log"
            (root / "outside.log").write_bytes(b"not bundled")
            run_path.write_text(json.dumps(run), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "escapes"):
                refresh._check_bundle_artifacts(root, bundle, run_path)

            run["artifacts"]["uart"]["path"] = str((bundle / "uart.log").resolve())
            run_path.write_text(json.dumps(run), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "absolute"):
                refresh._check_bundle_artifacts(root, bundle, run_path)

    def test_repo_relative_keeps_an_in_repo_tool_symlink_name(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "generic-driver"
            target.write_bytes(b"tool")
            alias = root / "ld.lld"
            alias.symlink_to(target.name)
            self.assertEqual(refresh._repo_relative(root, alias), "ld.lld")

    def test_prepare_and_runtime_commands_use_the_same_test_log_macros(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = {
                name: root / "bin" / name
                for name in ("clang", "clangxx", "lld", "llvm_objdump", "llc")
            }
            kwargs = {
                "repo_root": root,
                "suite": "callret",
                "bundle": root / "bundle",
                "qemu": root / "qemu-system-linx64",
                "tools": tools,
                "timeout": 30.0,
                "test_ids": [0x140B],
            }
            prepare = refresh._runner_command(**kwargs, pcs=None)
            runtime = refresh._runner_command(**kwargs, pcs=[0x10000])
            for command in (prepare, runtime):
                index = command.index("--require-test-id")
                self.assertEqual(command[index + 1], "0x0000140b")
            self.assertIn("--prepare-only", prepare)
            self.assertNotIn("--evidence-out", prepare)
            self.assertIn("--evidence-out", runtime)

    def test_published_command_does_not_capture_host_python_or_repo_path(self) -> None:
        root = refresh.REPO_ROOT
        command = [
            sys.executable,
            str(root / "avs/qemu/run_tests.py"),
            "--suite",
            "callret",
        ]
        portable = refresh._portable_command(root, command)
        self.assertEqual(
            portable,
            "python3 avs/qemu/run_tests.py --suite callret",
        )

    def test_checked_in_bundle_rebinds_object_and_elf_to_same_instruction(self) -> None:
        root = refresh.REPO_ROOT
        manifest = json.loads(
            (root / "avs/qemu/qemu_executable_coverage_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        entry = manifest["evidence"][0]
        rebound = refresh._resolve_entry(
            repo_root=root,
            old_entry=entry,
            new_elf_path=root / entry["elf"],
            new_object_path=root / entry["object"],
        )
        self.assertEqual(rebound, entry["instruction"])


if __name__ == "__main__":
    unittest.main()
