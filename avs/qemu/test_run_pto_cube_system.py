#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_pto_cube_system
import run_pto_cube_system_matrix


class PtoCubeSystemTests(unittest.TestCase):
    def test_full_suite_timeout_and_streaming_are_bounded(self) -> None:
        self.assertEqual(run_pto_cube_system.DEFAULT_TIMEOUT, 1200)
        source = Path(run_pto_cube_system.__file__).read_text(encoding="utf-8")
        self.assertIn("os.set_blocking(process.stdout.fileno(), False)", source)
        self.assertIn("os.read(process.stdout.fileno(), 65536)", source)
        self.assertNotIn("key.fileobj.readline()", source)
        self.assertIn('if args.qemu_guest_errors:', source)
        self.assertNotIn('"-no-reboot", "-d", "guest_errors"', source)
        self.assertIn('"timeout", "case", "qemu_guest_errors", "append"', source)

    def test_runtime_requires_every_case_and_clean_shutdown(self) -> None:
        lines = ["PTO_CUBE_START count=6"]
        lines.extend(
            f"PTO_CUBE_CASE_PASS {name} value=0"
            for name in run_pto_cube_system.CUBE_CASES
        )
        lines.extend(["PTO_CUBE_PASS count=6", "LINX_REBOOT lisc_shutdown"])
        self.assertEqual(
            run_pto_cube_system._classify_runtime("\n".join(lines), 0, False),
            (True, "runtime_pass", "all 6 cases passed and powered off"),
        )

    def test_case_failure_is_first_class(self) -> None:
        self.assertEqual(
            run_pto_cube_system._classify_runtime(
                "PTO_CUBE_START count=6\nPTO_CUBE_CASE_FAIL_EXIT case value=4\n",
                0,
                False,
            ),
            (False, "runtime_case_failure", "PTO_CUBE_CASE_FAIL_EXIT case value=4"),
        )

    def test_single_case_runtime_requires_selected_case_and_shutdown(self) -> None:
        name = run_pto_cube_system.CUBE_CASES[2]
        text = "\n".join(
            [
                "PTO_CUBE_START count=1",
                f"PTO_CUBE_CASE_START {name}",
                f"PTO_CUBE_CASE_PASS {name} value=0",
                "PTO_CUBE_PASS count=1",
                "LINX_REBOOT lisc_shutdown",
            ]
        )
        self.assertEqual(
            run_pto_cube_system._classify_runtime(text, 0, False, (name,)),
            (True, "runtime_pass", "all 1 cases passed and powered off"),
        )

    def test_pre_pid1_breakpoint_is_not_reported_as_timeout(self) -> None:
        line = "Linx: EBREAK trap imm=0 acr=0 at PC=0x6050ca (LINX_SEMIHOST=0)"
        self.assertEqual(
            run_pto_cube_system._classify_runtime(line, -15, False),
            (False, "runtime_kernel_breakpoint", line),
        )

    def test_pid1_panic_overrides_timeout(self) -> None:
        line = "LINX_EXIT_INIT code=0x000000000000000b"
        self.assertEqual(
            run_pto_cube_system._classify_runtime(
                "PTO_CUBE_START count=6\n" + line, 124, True
            ),
            (False, "runtime_kernel_panic", line),
        )

    def test_pid1_source_avoids_formatted_io(self) -> None:
        source = (
            Path(__file__).resolve().parent
            / "tests"
            / "linux_musl_pto_cube_init.c"
        ).read_text(encoding="utf-8")
        self.assertNotIn("snprintf", source)
        self.assertNotIn("printf(", source)
        self.assertNotIn("struct cube_case", source)
        self.assertNotIn("cases[]", source)
        self.assertEqual(source.count("run_case(\"/pto_cube/"), 6)
        self.assertIn("PTO_CUBE_CASE_INDEX", source)

    def test_timeout_reports_completed_case_count(self) -> None:
        text = "\n".join(
            ["PTO_CUBE_START count=6"]
            + [
                f"PTO_CUBE_CASE_PASS {name} value=0"
                for name in run_pto_cube_system.CUBE_CASES[:2]
            ]
        )
        self.assertEqual(
            run_pto_cube_system._classify_runtime(text, 124, True),
            (False, "runtime_timeout", "timeout: start=True case_passes=2 pass=False"),
        )

    def test_initramfs_packages_exact_six_and_runtime_aliases(self) -> None:
        elves = [Path("/build") / f"{name}.elf" for name in run_pto_cube_system.CUBE_CASES]
        lines = run_pto_cube_system._initramfs_lines(
            Path("/build/init"), elves, Path("/sysroot/lib/libc.so")
        )
        self.assertEqual(sum(line.startswith("file /pto_cube/") for line in lines), 6)
        self.assertIn("file /lib/libm.so /sysroot/lib/libc.so 0755 0 0", lines)
        self.assertIn(
            "file /lib/ld-musl-linx64.so.1 /sysroot/lib/libc.so 0755 0 0",
            lines,
        )

    def test_initramfs_can_package_one_allowlisted_case(self) -> None:
        case = run_pto_cube_system.CUBE_CASES[0]
        lines = run_pto_cube_system._initramfs_lines(
            Path("/build/init"), [Path("/build") / f"{case}.elf"],
            Path("/sysroot/lib/libc.so"),
        )
        self.assertEqual(sum(line.startswith("file /pto_cube/") for line in lines), 1)

    def test_cold_boot_matrix_is_exact_six_case_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            expected = {
                "pto_kernels": "p", "tileop": "t", "llvm": "c",
                "qemu": "q", "linux": "l",
            }
            source_tool = {
                component: {"expected_commit": expected[component]}
                for component in ("pto_kernels", "tileop", "linux", "qemu")
            }
            source_tool["clang"] = {"expected_commit": expected["llvm"]}
            provenance = {
                "source_tool": source_tool,
                "libc_sha256": "a" * 64,
                "loader_sha256": "b" * 64,
                "identity_parser_sha256": "c" * 64,
                "needed": {"case.elf": ["libc.so", "libm.so"]},
            }
            results = {}
            for case in run_pto_cube_system.CUBE_CASES:
                summary = root / f"{case}.summary.json"
                log = root / f"{case}.log"
                summary.write_text("{}\n", encoding="utf-8")
                log.write_text("PASS\n", encoding="utf-8")
                results[case] = {
                    "ok": True,
                    "returncode": 0,
                    "classification": "runtime_pass",
                    "selected_cases": [case],
                    "summary": run_pto_cube_system_matrix._evidence(summary),
                    "log": run_pto_cube_system_matrix._evidence(log),
                    "expected": copy.deepcopy(expected),
                    "provenance": copy.deepcopy(provenance),
                }

            self.assertTrue(run_pto_cube_system_matrix._aggregate_results(results)["result"]["ok"])

            hostile = copy.deepcopy(results)
            hostile[run_pto_cube_system.CUBE_CASES[0]].pop("expected")
            self.assertFalse(run_pto_cube_system_matrix._aggregate_results(hostile)["result"]["ok"])

            hostile = copy.deepcopy(results)
            hostile[run_pto_cube_system.CUBE_CASES[0]].pop("provenance")
            self.assertFalse(run_pto_cube_system_matrix._aggregate_results(hostile)["result"]["ok"])

            hostile = copy.deepcopy(results)
            hostile[run_pto_cube_system.CUBE_CASES[0]]["provenance"]["source_tool"]["qemu"]["binary"] = "mismatch"
            self.assertFalse(run_pto_cube_system_matrix._aggregate_results(hostile)["result"]["ok"])

            hostile = copy.deepcopy(results)
            hostile[run_pto_cube_system.CUBE_CASES[0]]["provenance"]["libc_sha256"] = "d" * 64
            self.assertFalse(run_pto_cube_system_matrix._aggregate_results(hostile)["result"]["ok"])

            hostile = copy.deepcopy(results)
            hostile.pop(run_pto_cube_system.CUBE_CASES[0])
            self.assertFalse(run_pto_cube_system_matrix._aggregate_results(hostile)["result"]["ok"])

            hostile = copy.deepcopy(results)
            hostile["extra"] = copy.deepcopy(next(iter(results.values())))
            self.assertFalse(run_pto_cube_system_matrix._aggregate_results(hostile)["result"]["ok"])

            hostile = copy.deepcopy(results)
            Path(hostile[run_pto_cube_system.CUBE_CASES[0]]["log"]["path"]).unlink()
            self.assertFalse(run_pto_cube_system_matrix._aggregate_results(hostile)["result"]["ok"])

    def test_nonempty_build_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "stale").write_text("stale", encoding="utf-8")
            with self.assertRaisesRegex(run_pto_cube_system.GateError, "absent or empty"):
                run_pto_cube_system._require_empty_output(root)


if __name__ == "__main__":
    unittest.main()
