#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_musl_smoke


class QemuInstructionFailureTests(unittest.TestCase):
    def test_driver_path_preserves_clangxx_symlink_identity(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "clang-23"
            target.write_bytes(b"driver")
            clangxx = root / "clang++"
            clangxx.symlink_to(target.name)

            self.assertEqual(run_musl_smoke._driver_path(str(clangxx)), clangxx)

    def test_v0591_mode_summary_selects_matching_compile_and_link_flags(self) -> None:
        compile_flags, link_flags = run_musl_smoke._musl_profile_flags(
            {
                "m1": "pass",
                "m2": "pass",
                "m3": "pass",
                "pto_identity_release": "0.59.1",
            }
        )

        self.assertEqual(compile_flags, ["-march=linx64+pto-v0591-scoped"])
        self.assertEqual(
            link_flags,
            [
                "-march=linx64+pto-v0591-scoped",
                "-Wl,--linx-pto-v0591-scoped",
            ],
        )

    def test_legacy_or_explicit_mode_does_not_gain_profile_flags(self) -> None:
        self.assertEqual(
            run_musl_smoke._musl_profile_flags(
                {"m1": "pass", "m2": "pass", "m3": "pass"}
            ),
            ([], []),
        )
        with self.assertRaisesRegex(ValueError, "not validated: m3"):
            run_musl_smoke._musl_profile_flags(
                {
                    "m1": "pass",
                    "m2": "pass",
                    "m3": "fail",
                    "pto_identity_release": "0.59.1",
                }
            )

    def test_runtime_convergence_preserves_workload_clang_override(self) -> None:
        script = (
            Path(__file__).resolve().parents[2]
            / "tools/bringup/run_runtime_convergence.sh"
        ).read_text(encoding="utf-8")

        self.assertIn("""printf -v WORKLOAD_CLANG '%q' "${LINX_CLANG:-$CLANG_BIN}" """.strip(), script)
        self.assertGreaterEqual(script.count("LINX_CLANG=$WORKLOAD_CLANG"), 3)
        self.assertIn("--clang $WORKLOAD_CLANG", script)
        self.assertIn("CLANG=$CLANG_BIN TARGET=linx64-linx-none-elf", script)
        self.assertIn("--clang $CLANG_BIN --gmake", script)

    def test_pto_cube_is_a_focused_system_sample(self) -> None:
        self.assertEqual(run_musl_smoke._select_samples(["pto_cube"]), ["pto_cube"])
        self.assertEqual(
            run_musl_smoke.SAMPLES["pto_cube"],
            {
                "src": "linux_musl_pto_cube_init.c",
                "start": "PTO_CUBE_START count=6",
                "pass": "PTO_CUBE_PASS count=6",
            },
        )

    def test_explicit_kernel_overrides_legacy_build_search(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            kernel = root / "fresh" / "vmlinux"
            kernel.parent.mkdir()
            kernel.write_bytes(b"fresh")

            self.assertEqual(
                run_musl_smoke._resolve_kernel(root / "linux", str(kernel)),
                kernel.resolve(),
            )

    def test_reusable_musl_requires_complete_summary_and_assets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sysroot = root / "sysroot"
            runtime = root / "runtime" / "liblinx_builtin_rt.a"
            for path in (
                sysroot / "lib" / "libc.a",
                sysroot / "lib" / "libc.so",
                sysroot / "lib" / "ld-musl-linx64.so.1",
                runtime,
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"asset")

            self.assertEqual(
                run_musl_smoke._musl_reuse_errors(
                    {"m1": "pass", "m2": "pass", "m3": "pass"},
                    sysroot,
                    runtime,
                ),
                [],
            )
            runtime.unlink()
            errors = run_musl_smoke._musl_reuse_errors(
                {"m1": "pass", "m2": "pass", "m3": "fail"},
                sysroot,
                runtime,
            )
            self.assertIn("m3", errors)
            self.assertIn(str(runtime), errors)

    def test_decode32_failure_is_not_left_as_a_generic_timeout(self) -> None:
        text = (
            "Linx: illegal instruction @ 0xffffffff80000000\n"
            "Linx: decode32 failed @ PC=0xffffffff80000000 insn=0x00000000\n"
        )

        self.assertEqual(
            run_musl_smoke._classify_system_runtime_failure(
                text,
                timed_out=True,
                start_seen=False,
                pass_seen=False,
                qemu_rc=124,
                timeout=5,
            ),
            (
                "runtime_qemu_decode_failure",
                "QEMU instruction failure before pass marker: "
                "Linx: decode32 failed @ PC=0xffffffff80000000 insn=0x00000000",
            ),
        )

    def test_illegal_instruction_has_a_distinct_classification(self) -> None:
        self.assertEqual(
            run_musl_smoke._qemu_instruction_failure(
                "Linx: illegal instruction at PC=0xffffffff80000004\n"
            ),
            (
                "runtime_qemu_illegal_instruction",
                "Linx: illegal instruction at PC=0xffffffff80000004",
            ),
        )

    def test_all_decode_widths_override_generic_illegal_diagnostic(self) -> None:
        decode_lines = (
            "Linx: decode failed @ PC=0x10 hw=0x0000 len=2",
            "Linx: decode32 failed @ PC=0x20 insn=0x00000000",
            "Linx: decode64 failed @ PC=0x30 insn=0x0000000000000000",
        )
        for decode_line in decode_lines:
            with self.subTest(decode_line=decode_line):
                self.assertEqual(
                    run_musl_smoke._qemu_instruction_failure(
                        f"Linx: illegal instruction at PC=0x4\n{decode_line}\n"
                    ),
                    ("runtime_qemu_decode_failure", decode_line),
                )

    def test_unrelated_guest_text_does_not_override_timeout_classification(self) -> None:
        self.assertIsNone(
            run_musl_smoke._qemu_instruction_failure(
                "userspace process exited after Illegal instruction\n"
            )
        )

    def test_pass_markers_do_not_hide_timeout(self) -> None:
        self.assertEqual(
            run_musl_smoke._classify_system_runtime_failure(
                "MUSL_SMOKE_START\nMUSL_SMOKE_PASS\nLinx: illegal instruction at PC=0x4\n",
                timed_out=True,
                start_seen=True,
                pass_seen=True,
                qemu_rc=124,
                timeout=5,
            ),
            ("runtime_timeout", "timeout after 5s after pass marker"),
        )

    def test_system_runtime_requires_clean_shutdown(self) -> None:
        self.assertEqual(
            run_musl_smoke._classify_system_runtime_failure(
                "MUSL_SMOKE_START\nMUSL_SMOKE_PASS\n",
                timed_out=False,
                start_seen=True,
                pass_seen=True,
                qemu_rc=0,
                timeout=5,
            ),
            ("runtime_missing_shutdown", "pass marker observed without LINX_REBOOT lisc_shutdown"),
        )
        self.assertIsNone(
            run_musl_smoke._classify_system_runtime_failure(
                "MUSL_SMOKE_START\nMUSL_SMOKE_PASS\nLINX_REBOOT lisc_shutdown\n",
                timed_out=False,
                start_seen=True,
                pass_seen=True,
                qemu_rc=0,
                timeout=5,
            )
        )

    def test_pass_without_start_does_not_claim_failure_before_pass(self) -> None:
        diagnostics = (
            "[linx trap]",
            "Kernel panic - not syncing: test",
            "Linx: decode32 failed @ PC=0x4 insn=0x0",
        )
        for diagnostic in diagnostics:
            with self.subTest(diagnostic=diagnostic, timed_out=True):
                self.assertEqual(
                    run_musl_smoke._classify_system_runtime_failure(
                        diagnostic,
                        timed_out=True,
                        start_seen=False,
                        pass_seen=True,
                        qemu_rc=124,
                        timeout=5,
                    ),
                    ("runtime_timeout", "timeout after 5s"),
                )
            with self.subTest(diagnostic=diagnostic, timed_out=False):
                self.assertEqual(
                    run_musl_smoke._classify_system_runtime_failure(
                        diagnostic,
                        timed_out=False,
                        start_seen=False,
                        pass_seen=True,
                        qemu_rc=0,
                        timeout=5,
                    ),
                    (
                        "runtime_syscall_failure",
                        "missing markers: start=False pass=True, qemu_rc=0",
                    ),
                )

    def test_guest_trap_keeps_precedence_over_qemu_decode_diagnostic(self) -> None:
        self.assertEqual(
            run_musl_smoke._classify_system_runtime_failure(
                "[linx trap]\nLinx: decode32 failed @ PC=0x4 insn=0x0\n",
                timed_out=True,
                start_seen=False,
                pass_seen=False,
                qemu_rc=124,
                timeout=5,
            ),
            ("runtime_block_trap", "linx trap before pass marker (timeout after 5s)"),
        )

    def test_timeout_without_specific_evidence_stays_generic(self) -> None:
        self.assertEqual(
            run_musl_smoke._classify_system_runtime_failure(
                "",
                timed_out=True,
                start_seen=False,
                pass_seen=False,
                qemu_rc=124,
                timeout=5,
            ),
            ("runtime_timeout", "timeout after 5s"),
        )

    def test_system_command_enables_only_guest_error_diagnostics(self) -> None:
        command = run_musl_smoke._system_qemu_command(
            Path("qemu-system-linx64"),
            Path("vmlinux"),
            Path("initramfs.cpio"),
            "console=ttyS0",
        )

        option_pairs = [command[i : i + 2] for i in range(len(command) - 1)]
        self.assertIn(["-d", "guest_errors"], option_pairs)
        self.assertNotIn("unimp", command)


if __name__ == "__main__":
    unittest.main()
