#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import refresh_qemu_executable_coverage as refresh


class RefreshQemuExecutableCoverageTests(unittest.TestCase):
    def test_scoped_elf_requires_exactly_one_matching_pto_note(self) -> None:
        identity = {"release": "0.59.1"}
        note = {
            "Owner": "PTO", "Type": "NT_VERSION (version)",
            "Description data": {"Bytes": list(b'{"release":"0.59.1"}')},
        }
        def inspect(notes):
            payload = [{"NoteSections": [{"NoteSection": {
                "Name": ".note.pto.isa", "Notes": notes,
            }}]}]
            with patch.object(refresh.subprocess, "check_output", return_value=json.dumps(payload)):
                refresh._check_elf_identity(Path("llvm-readobj"), Path("test.elf"), identity)
        inspect([note])
        for notes in ([], [note, note], [{**note, "Owner": "GNU"}],
                      [{**note, "Description data": {"Bytes": list(b'{"release":"0.58.7"}')}}]):
            with self.subTest(notes=notes), self.assertRaisesRegex(ValueError, "incorrect"):
                inspect(notes)

    def test_form_identity_rebind_is_exact_and_changed_keys_are_allowlisted(self) -> None:
        def form(form_id: str, mnemonic: str, mask: int, match: int) -> dict:
            return {
                "id": form_id,
                "mnemonic": mnemonic,
                "encoding": {
                    "length_bits": 32,
                    "parts": [
                        {
                            "index": 0,
                            "width_bits": 32,
                            "mask": f"0x{mask:08x}",
                            "match": f"0x{match:08x}",
                        }
                    ],
                },
            }

        spec = {
            "instructions": [
                form("new-same-key", "ADD", 0x7F, 0x33),
                form("fret_stk_32_1c6ea1521169", "FRET.STK", 0xFF07F, 0x53041),
            ]
        }
        manifest = {
            "evidence": [
                {
                    "form_id": "old-same-key",
                    "mnemonic": "ADD",
                    "form_key": {
                        "length_bits": 32,
                        "mask": "0x0000007f",
                        "match": "0x00000033",
                    },
                },
                {
                    "form_id": "fret_stk_32_4fe246bd8241",
                    "mnemonic": "FRET.STK",
                    "form_key": {
                        "length_bits": 32,
                        "mask": "0x0000707f",
                        "match": "0x00003041",
                    },
                },
            ]
        }
        rebinds = refresh._rebind_manifest_forms(manifest, spec)
        self.assertEqual(
            [entry["form_id"] for entry in manifest["evidence"]],
            ["new-same-key", "fret_stk_32_1c6ea1521169"],
        )
        self.assertEqual(
            [row["reason"] for row in rebinds],
            ["exact-form-key", "reviewed-encoding-migration"],
        )
        self.assertEqual(
            manifest["evidence"][1]["form_key"],
            {"length_bits": 32, "mask": "0x000ff07f", "match": "0x00053041"},
        )
        manifest["evidence"][1]["mnemonic"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "changes mnemonic"):
            refresh._rebind_manifest_forms(manifest, spec)

    def test_relative_candidate_is_preferred_without_pc_shift_guessing(self) -> None:
        self.assertEqual(refresh._select_candidate(6, [2, 6, 10], "form"), 6)
        self.assertEqual(refresh._select_candidate(6, [10], "form"), 10)
        self.assertEqual(refresh._select_candidate(None, [10], "form"), 10)
        self.assertEqual(refresh._select_candidate(None, [2, 10], "form", 1), 10)
        with self.assertRaisesRegex(ValueError, "outside"):
            refresh._select_candidate(None, [2, 10], "form", 2)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            refresh._select_candidate(6, [2, 10], "form")
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            refresh._select_candidate(None, [2, 10], "form")
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
            for command in (prepare, runtime):
                self.assertEqual(command[command.index("--isa-profile") + 1], "v0.58")
            scoped = refresh._runner_command(**kwargs, pcs=[0x10000], profile="v0.59")
            self.assertEqual(scoped[scoped.index("--isa-profile") + 1], "v0.59")
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

    def test_rebound_manifest_is_staged_inside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            path = refresh._candidate_manifest_path(root, "review-r1")
            self.assertEqual(
                path,
                root / "out/qemu-executable-coverage-review-r1.refresh-candidate.json",
            )
            self.assertTrue(path.is_relative_to(root))

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
