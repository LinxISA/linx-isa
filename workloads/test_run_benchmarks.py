#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("run_benchmarks.py")
SPEC = importlib.util.spec_from_file_location("run_benchmarks", MODULE_PATH)
assert SPEC and SPEC.loader
RUNNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUNNER
SPEC.loader.exec_module(RUNNER)


class BenchmarkEvidenceTests(unittest.TestCase):
    def _fake_readelf(
        self,
        root: Path,
        *,
        machine: str = "Linx",
        elf_class: str = "ELF64",
        interp: bool = False,
        needed: str | None = None,
    ) -> Path:
        readelf = root / "llvm-readelf"
        interp_line = "  INTERP         0x000000 0x0 0x0 0x1 0x1 R 0x1\n" if interp else ""
        needed_line = (
            f" 0x0000000000000001 (NEEDED)             Shared library: [{needed}]\n" if needed else ""
        )
        readelf.write_text(
            "#!/bin/sh\n"
            "cat <<'EOF'\n"
            f"  Class:                             {elf_class}\n"
            "  Data:                              2's complement, little endian\n"
            "  Type:                              DYN (Shared object file)\n"
            f"  Machine:                           {machine}\n"
            "  Entry point address:               0x40000000\n"
            "Program Headers:\n"
            f"{interp_line}"
            "  LOAD           0x000000 0x0 0x0 0x10 0x10 R E 0x1000\n"
            "Dynamic section at offset 0x100 contains 1 entries:\n"
            f"{needed_line}"
            "EOF\n",
            encoding="utf-8",
        )
        readelf.chmod(readelf.stat().st_mode | stat.S_IXUSR)
        return readelf

    def _elf(self, root: Path, name: str = "sample.elf") -> Path:
        path = root / name
        path.write_bytes(b"\x7fELF\x02\x01\x01" + b"\0" * 57)
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def test_fake_elf_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fake = root / "not-elf"
            fake.write_text("not an ELF", encoding="utf-8")
            evidence = RUNNER._inspect_elf(
                fake,
                readelf=self._fake_readelf(root),
                expected_machine="Linx",
                expected_class="ELF64",
                expected_static=True,
                logs_dir=root,
                name="fake",
            )
            self.assertEqual(evidence["status"], "FAIL")
            self.assertIn("invalid ELF magic", evidence["errors"])

    def test_wrong_architecture_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = RUNNER._inspect_elf(
                self._elf(root),
                readelf=self._fake_readelf(root, machine="Advanced Micro Devices X86-64"),
                expected_machine="Linx",
                expected_class="ELF64",
                expected_static=True,
                logs_dir=root,
                name="wrong-arch",
            )
            self.assertEqual(evidence["status"], "FAIL")
            self.assertTrue(any("machine mismatch" in item for item in evidence["errors"]))

    def test_readelf_symlink_invocation_name_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "llvm-readobj"
            target.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            target.chmod(target.stat().st_mode | stat.S_IXUSR)
            link = root / "llvm-readelf"
            link.symlink_to(target.name)
            self.assertEqual(RUNNER._check_exe(link, "readelf"), link.absolute())

    def test_auto_link_mode_selects_static_for_linx_sysroot(self) -> None:
        self.assertEqual(
            RUNNER._effective_link_mode("auto", target="linx64-unknown-linux-musl", sysroot="/sysroot"),
            "musl-static",
        )
        self.assertEqual(
            RUNNER._effective_link_mode("auto", target="linx64-unknown-linux-musl", sysroot=None),
            "default",
        )

    def test_coremark_zero_iterations_uses_volatile_auto_calibration(self) -> None:
        flags = RUNNER._coremark_iteration_flags(0)
        self.assertIn("-DITERATIONS=0", flags)
        self.assertIn("-DSEED_METHOD=SEED_VOLATILE", flags)
        RUNNER._validate_run_parameters(coremark_iterations=0, dhrystone_runs=1, timeout=1)

    def test_negative_coremark_iterations_are_rejected(self) -> None:
        with self.assertRaisesRegex(SystemExit, "zero .* or positive"):
            RUNNER._validate_run_parameters(coremark_iterations=-1, dhrystone_runs=1, timeout=1)
        self.assertEqual(
            RUNNER._effective_link_mode("default", target="linx64-unknown-linux-musl", sysroot="/sysroot"),
            "default",
        )

    def test_dynamic_elf_is_rejected_when_static_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = RUNNER._inspect_elf(
                self._elf(root),
                readelf=self._fake_readelf(root, interp=True),
                expected_machine="Linx",
                expected_class="ELF64",
                expected_static=True,
                logs_dir=root,
                name="dynamic",
            )
            self.assertEqual(evidence["status"], "FAIL")
            self.assertIn("staticity mismatch: expected static, observed dynamic", evidence["errors"])

    def test_dt_needed_without_interp_is_rejected_as_non_static(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = RUNNER._inspect_elf(
                self._elf(root),
                readelf=self._fake_readelf(root, needed="libc.so"),
                expected_machine="Linx",
                expected_class="ELF64",
                expected_static=True,
                logs_dir=root,
                name="needed-without-interp",
            )
            self.assertEqual(evidence["status"], "FAIL")
            self.assertFalse(evidence["has_interp"])
            self.assertEqual(evidence["dynamic_needed"], ["libc.so"])
            self.assertTrue(any("DT_NEEDED" in item for item in evidence["errors"]))

    def test_missing_semantic_marker_fails_even_with_zero_exit(self) -> None:
        evidence = RUNNER._classify_runtime("coremark", exit_code=0, timed_out=False, output="finished\n")
        self.assertEqual(evidence["status"], "FAIL")
        self.assertTrue(any(marker.startswith("Correct operation validated.") for marker in evidence["missing_markers"]))

    def test_nonzero_exit_fails_even_with_semantic_markers(self) -> None:
        output = "Correct operation validated. See README.md for run and reporting rules.\n"
        evidence = RUNNER._classify_runtime("coremark", exit_code=9, timed_out=False, output=output)
        self.assertEqual(evidence["status"], "FAIL")
        self.assertEqual(evidence["exit_code"], 9)

    def test_workload_specific_semantic_contracts_can_pass(self) -> None:
        coremark = "Correct operation validated. See README.md for run and reporting rules.\n"
        self.assertEqual(
            RUNNER._classify_runtime("coremark", exit_code=0, timed_out=False, output=coremark)["status"],
            "PASS",
        )
        dhrystone = "\n".join(RUNNER.SEMANTIC_MARKERS["dhrystone"]["required"])
        self.assertEqual(
            RUNNER._classify_runtime("dhrystone", exit_code=0, timed_out=False, output=dhrystone)["status"],
            "PASS",
        )

    def test_timeout_is_distinct_failure_state_and_writes_logs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            exe = self._elf(root)
            evidence = RUNNER._run_with_wrapper(
                name="coremark",
                exe=exe,
                run_command=f"{sys.executable} -c 'import time; time.sleep(2)'",
                timeout=0.01,
                out_dir=root,
                verbose=False,
            )
            self.assertEqual(evidence["status"], "TIMEOUT")
            self.assertTrue(Path(evidence["stdout"]).exists())
            self.assertTrue(Path(evidence["stderr"]).exists())

    def test_python_wrapper_script_is_bound_as_a_command_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            exe = self._elf(root)
            wrapper = root / "wrapper.py"
            wrapper.write_text(
                "print('Correct operation validated. See README.md for run and reporting rules.')\n",
                encoding="utf-8",
            )
            evidence = RUNNER._run_with_wrapper(
                name="coremark",
                exe=exe,
                run_command=f"{sys.executable} {wrapper} {{exe}}",
                timeout=2,
                out_dir=root,
                verbose=False,
            )
            self.assertEqual(evidence["status"], "PASS")
            bound_paths = {item["resolved_path"] for item in evidence["command_file_identities"]}
            self.assertIn(str(wrapper.resolve()), bound_paths)
            self.assertIn(str(Path(sys.executable).resolve()), bound_paths)
            self.assertNotIn(str(exe.resolve()), bound_paths)

    def test_wrapper_mutation_changes_identity_and_forces_failure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            exe = self._elf(root)
            wrapper = root / "mutating-wrapper"
            wrapper.write_text(
                "#!/bin/sh\n"
                "echo 'Correct operation validated. See README.md for run and reporting rules.'\n"
                "echo '# changed' >> \"$0\"\n",
                encoding="utf-8",
            )
            wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
            evidence = RUNNER._run_with_wrapper(
                name="coremark",
                exe=exe,
                run_command=f"{wrapper} {{exe}}",
                timeout=2,
                out_dir=root,
                verbose=False,
            )
            self.assertEqual(evidence["status"], "FAIL")
            self.assertIn("a command file argument changed while it was being run", evidence["errors"])
            before = evidence["command_file_identities"][0]
            after = evidence["command_file_identities_after"][0]
            self.assertNotEqual(before["sha256"], after["sha256"])

    def test_build_only_state_is_not_runtime_pass(self) -> None:
        result = RUNNER._compose_result(
            name="coremark",
            build={"status": "PASS"},
            artifact={"status": "PASS"},
            runtime=None,
        )
        self.assertEqual(result["status"], "BUILD_ONLY")
        self.assertEqual(result["runtime_status"], "NOT_RUN")
        self.assertFalse(result["runtime_pass"])

    def test_build_only_manifest_never_sets_runtime_all_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cc = root / "clang"
            readelf = root / "llvm-readelf"
            for tool in (cc, readelf):
                tool.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                tool.chmod(tool.stat().st_mode | stat.S_IXUSR)
            result = RUNNER._compose_result(
                name="coremark",
                build={"status": "PASS"},
                artifact={"status": "PASS"},
                runtime=None,
            )
            out = root / "result.json"
            self.assertTrue(
                RUNNER._write_json(
                    out,
                    [result],
                    target="linx64-unknown-linux-musl",
                    cc=cc,
                    readelf=readelf,
                    run_command=None,
                )
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(payload["build_all_pass"])
            self.assertTrue(payload["requested_gate_pass"])
            self.assertIsNone(payload["runtime_all_pass"])
            self.assertFalse(payload["all_pass"])
            self.assertEqual(payload["evidence_level"], "build-only")


if __name__ == "__main__":
    unittest.main()
