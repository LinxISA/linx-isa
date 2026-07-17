#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("check_build_manifest.py")
SPEC = importlib.util.spec_from_file_location("check_build_manifest", MODULE_PATH)
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


EXPECTED_EXECUTABLES = {
    "500.perlbench_r": ["perlbench_r_base.mytest-m64"],
    "502.gcc_r": ["cpugcc_r_base.mytest-m64"],
    "505.mcf_r": ["mcf_r_base.mytest-m64"],
    "520.omnetpp_r": ["omnetpp_r_base.mytest-m64"],
    "523.xalancbmk_r": ["cpuxalan_r_base.mytest-m64"],
    "525.x264_r": [
        "x264_r_base.mytest-m64",
        "ldecod_r_base.mytest-m64",
        "imagevalidate_525_base.mytest-m64",
    ],
    "531.deepsjeng_r": ["deepsjeng_r_base.mytest-m64"],
    "541.leela_r": ["leela_r_base.mytest-m64"],
    "557.xz_r": ["xz_r_base.mytest-m64"],
    "999.specrand_ir": ["specrand_ir_base.mytest-m64"],
}


def _run(*args: str, cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


class BuildManifestEvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name).resolve()
        self._init_repo(self.root)
        (self.root / ".gitignore").write_text(
            "compiler/\nemulator/\nkernel/\nlib/\nout/\ntools/\nspec/\n", encoding="utf-8"
        )
        self._commit_all(self.root, "root")

        self.llvm = self.root / "compiler" / "llvm"
        self.qemu = self.root / "emulator" / "qemu"
        self.linux = self.root / "kernel" / "linux"
        self.musl = self.root / "lib" / "musl"
        for repo, label in (
            (self.llvm, "llvm"),
            (self.qemu, "qemu"),
            (self.linux, "linux"),
            (self.musl, "musl"),
        ):
            repo.mkdir(parents=True)
            self._init_repo(repo)
            (repo / "identity.txt").write_text(label + "\n", encoding="utf-8")
            self._commit_all(repo, label)

        self.tools = self.root / "tools" / "bin"
        self.tools.mkdir(parents=True)
        self.clang = self.tools / "clang"
        self.readelf = self.tools / "llvm-readelf"
        self.clang.write_text("#!/bin/sh\necho 'clang version test-1'\n", encoding="utf-8")
        self.readelf.write_text(
            """#!/bin/sh
if [ "$1" = "--version" ]; then
  echo 'LLVM readelf version test-1'
elif [ "$1" = "-h" ]; then
  echo '  Machine: Linx'
  echo '  Entry point address: 0x4000'
elif [ "$1" = "-l" ]; then
  echo 'Program Headers:'
elif [ "$1" = "-s" ]; then
  echo '1: 0000000000004000 0 FUNC GLOBAL DEFAULT 1 _start'
  echo '2: 0000000000004010 0 FUNC GLOBAL DEFAULT 1 main'
else
  exit 2
fi
""",
            encoding="utf-8",
        )
        self.clang.chmod(0o755)
        self.readelf.chmod(0o755)

        self.sysroot = self.root / "out" / "libc" / "musl" / "install" / "phase-b"
        (self.sysroot / "lib").mkdir(parents=True)
        (self.sysroot / "lib" / "libc.a").write_bytes(b"fake-libc")

        self.spec_dir = self.root / "spec"
        logs = self.spec_dir / "tmp" / "linx-build-logs"
        logs.mkdir(parents=True)
        self.baseline = logs / "src-baseline.sha256"
        self.post = logs / "src-postbuild.sha256"
        self.source_file = (
            self.spec_dir / "benchspec" / "CPU" / "999.specrand_ir" / "src" / "main.c"
        )
        self.source_file.parent.mkdir(parents=True)
        self.source_file.write_bytes(b"licensed-source-fixture\n")
        source_row = (
            hashlib.sha256(self.source_file.read_bytes()).hexdigest()
            + "  "
            + str(self.source_file)
            + "\n"
        )
        self.baseline.write_text(source_row, encoding="utf-8")
        self.post.write_text(source_row, encoding="utf-8")
        self.drift_paths = logs / "src-drift-paths.txt"

        bench_results: dict[str, object] = {}
        for bench, names in EXPECTED_EXECUTABLES.items():
            rows = []
            for name in names:
                path = self.spec_dir / "benchspec" / "CPU" / bench / "exe" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f"ELF:{bench}:{name}".encode())
                rows.append(
                    {
                        "name": name,
                        "path": str(path),
                        "exists": True,
                        "machine": "Linx",
                        "is_linx_machine": True,
                        "entry_point": "0x4000",
                        "start_symbol": "0000000000004000",
                        "main_symbol": "0000000000004010",
                        "static_entry_ok": True,
                    }
                )
            bench_results[bench] = {
                "build_ok": True,
                "all_expected_exes_present": True,
                "all_expected_exes_linx_machine": True,
                "optimize_flags": "-O0",
                "uses_global_optimize_flags": True,
                "executables": rows,
            }

        self.manifest = self.root / "stage-a.json"
        self.manifest.write_text(
            json.dumps(
                {
                    "schema_version": "linx-spec-build-manifest-v1",
                    "generated_at_utc": "2026-07-15 00:00:00Z",
                    "spec_dir": str(self.spec_dir),
                    "mode": "phase-b",
                    "target": "linx64-unknown-linux-musl",
                    "sysroot": str(self.sysroot),
                    "clang": str(self.clang),
                    "llvm_readelf": str(self.readelf),
                    "optimize_flags": "-O0",
                    "bench_optimize_flags": {
                        bench: "-O0" for bench in EXPECTED_EXECUTABLES
                    },
                    "link_mode": "canonical-crt",
                    "force_static": True,
                    "selected_benchmarks": list(EXPECTED_EXECUTABLES),
                    "bench_results": bench_results,
                    "source_immutability": {
                        "baseline_manifest": str(self.baseline),
                        "post_manifest": str(self.post),
                        "manifests_match": True,
                        "drift_paths": None,
                    },
                    "failed_entries": [],
                    "overall_ok": True,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @staticmethod
    def _init_repo(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        _run("git", "init", "-q", cwd=path)
        _run("git", "config", "user.email", "test@example.com", cwd=path)
        _run("git", "config", "user.name", "Evidence Test", cwd=path)

    @staticmethod
    def _commit_all(path: Path, message: str) -> None:
        _run("git", "add", ".", cwd=path)
        _run("git", "commit", "-q", "-m", message, cwd=path)

    def _attest(
        self,
        *,
        selected_benchmarks: list[str] | None = None,
        bound_repo_heads: dict[str, str] | None = None,
        bound_artifacts: dict[str, str] | None = None,
    ) -> dict[str, object]:
        return checker.build_attestation(
            self.root,
            self.manifest,
            selected_benchmarks=selected_benchmarks,
            bound_repo_heads=bound_repo_heads,
            bound_artifacts=bound_artifacts,
        )

    def test_refresh_source_drift_removes_stale_files_and_reports_current_drift(self) -> None:
        diff_out = self.baseline.with_name("src-drift.diff")
        paths_out = self.drift_paths
        self.baseline.write_text("a" * 64 + "  /licensed/source.c\n", encoding="utf-8")
        self.post.write_text("a" * 64 + "  /licensed/source.c\n", encoding="utf-8")
        diff_out.write_text("stale\n", encoding="utf-8")
        paths_out.write_text("/stale/path.c\n", encoding="utf-8")

        self.assertFalse(
            checker.refresh_source_drift(
                self.baseline, self.post, diff_out=diff_out, paths_out=paths_out
            )
        )
        self.assertFalse(diff_out.exists())
        self.assertFalse(paths_out.exists())

        self.post.write_text("b" * 64 + "  /licensed/source.c\n", encoding="utf-8")
        self.assertTrue(
            checker.refresh_source_drift(
                self.baseline, self.post, diff_out=diff_out, paths_out=paths_out
            )
        )
        self.assertEqual(paths_out.read_text(encoding="utf-8"), "/licensed/source.c\n")
        self.assertIn("-" + "a" * 64, diff_out.read_text(encoding="utf-8"))
        self.assertIn("+" + "b" * 64, diff_out.read_text(encoding="utf-8"))

    def test_attestation_covers_exact_stage_a_set(self) -> None:
        attestation = self._attest()
        self.assertTrue(attestation["ok"])
        self.assertEqual(attestation["counts"]["benchmarks"], 10)
        self.assertEqual(attestation["counts"]["executables"], 12)
        self.assertEqual(
            attestation["evidence"]["repositories"]["llvm"]["head"],
            subprocess.check_output(
                ["git", "-C", str(self.llvm), "rev-parse", "HEAD"], text=True
            ).strip(),
        )
        self.assertEqual(attestation["evidence"]["tools"]["clang"]["identity"], "clang version test-1")

    def test_explicit_subset_attests_only_selected_benchmark(self) -> None:
        self.select_manifest_benchmarks(["999.specrand_ir"])
        attestation = self._attest(selected_benchmarks=["999.specrand_ir"])
        self.assertEqual(attestation["counts"], {"benchmarks": 1, "executables": 1})
        self.assertEqual(
            [row["benchmark"] for row in attestation["evidence"]["executables"]],
            ["999.specrand_ir"],
        )
        self.assertEqual(
            attestation["input"]["attestation_options"]["selected_benchmarks"],
            ["999.specrand_ir"],
        )
        checker.verify_attestation(self.root, attestation)

    def test_explicit_subset_rejects_unapproved_benchmark(self) -> None:
        with self.assertRaisesRegex(checker.EvidenceError, "unsupported selected benchmark"):
            self._attest(selected_benchmarks=["998.not-approved"])

    def test_explicit_subset_rejects_missing_requested_benchmark(self) -> None:
        self.select_manifest_benchmarks([])
        with self.assertRaisesRegex(checker.EvidenceError, "does not match requested subset"):
            self._attest(selected_benchmarks=["999.specrand_ir"])

    def test_default_mode_still_rejects_subset_manifest(self) -> None:
        self.select_manifest_benchmarks(["999.specrand_ir"])
        with self.assertRaisesRegex(checker.EvidenceError, "required exact 10"):
            self._attest()

    def test_verify_subset_rejects_selected_elf_hash_drift(self) -> None:
        self.select_manifest_benchmarks(["999.specrand_ir"])
        attestation = self._attest(selected_benchmarks=["999.specrand_ir"])
        self.first_elf("999.specrand_ir").write_bytes(b"changed-selected-elf")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_caller_bindings_cover_stack_heads_and_runtime_artifacts(self) -> None:
        self.select_manifest_benchmarks(["999.specrand_ir"])
        test_summary = self.root / "out" / "test-summary.json"
        train_summary = self.root / "out" / "train-summary.json"
        provenance = self.root / "out" / "vmlinux.provenance.json"
        for path, content in (
            (test_summary, b"test-summary"),
            (train_summary, b"train-summary"),
            (provenance, b"vmlinux-provenance"),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        repo_heads = {
            name: subprocess.check_output(
                ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
            ).strip()
            for name, repo in (
                ("root", self.root),
                ("llvm", self.llvm),
                ("qemu", self.qemu),
                ("linux", self.linux),
                ("musl", self.musl),
            )
        }
        artifacts = {
            "vmlinux-provenance": str(provenance),
            "test-summary": str(test_summary),
            "train-summary": str(train_summary),
        }
        attestation = self._attest(
            selected_benchmarks=["999.specrand_ir"],
            bound_repo_heads=repo_heads,
            bound_artifacts=artifacts,
        )
        self.assertEqual(
            set(attestation["evidence"]["caller_bindings"]["repo_heads"]),
            set(repo_heads),
        )
        checker.verify_attestation(self.root, attestation)
        train_summary.write_bytes(b"changed-train-summary")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_verify_rejects_wrong_pin(self) -> None:
        attestation = self._attest()
        attestation["evidence"]["repositories"]["llvm"]["head"] = "0" * 40
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_verify_accepts_unchanged_attestation(self) -> None:
        checker.verify_attestation(self.root, self._attest())

    def test_verify_rejects_same_superproject_dirty_path_with_new_content(self) -> None:
        self._append(self.root / ".gitignore", "# first\n")
        attestation = self._attest()
        self._append(self.root / ".gitignore", "# second\n")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_verify_rejects_same_llvm_staged_path_with_new_content(self) -> None:
        identity = self.llvm / "identity.txt"
        identity.write_text("llvm-staged-one\n", encoding="utf-8")
        _run("git", "add", "identity.txt", cwd=self.llvm)
        attestation = self._attest()
        identity.write_text("llvm-staged-two\n", encoding="utf-8")
        _run("git", "add", "identity.txt", cwd=self.llvm)
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_verify_rejects_same_musl_untracked_path_with_new_content(self) -> None:
        untracked = self.musl / "untracked.bin"
        untracked.write_bytes(b"one")
        attestation = self._attest()
        untracked.write_bytes(b"two")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_verify_rejects_untracked_symlink_target_change(self) -> None:
        link = self.musl / "untracked-link"
        link.symlink_to("first-target")
        attestation = self._attest()
        link.unlink()
        link.symlink_to("second-target")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_verify_handles_nul_safe_untracked_filename(self) -> None:
        untracked = self.musl / "line\nbreak.bin"
        untracked.write_bytes(b"one")
        attestation = self._attest()
        untracked.write_bytes(b"two")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_verify_rejects_changed_tool(self) -> None:
        attestation = self._attest()
        self.clang.write_text("#!/bin/sh\necho 'clang version changed'\n", encoding="utf-8")
        self.clang.chmod(0o755)
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_verify_rejects_changed_readelf(self) -> None:
        attestation = self._attest()
        self._append(self.readelf, "# changed\n")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_verify_rejects_changed_elf(self) -> None:
        attestation = self._attest()
        first = next(iter(EXPECTED_EXECUTABLES))
        elf = Path(self.manifest_payload()["bench_results"][first]["executables"][0]["path"])
        elf.write_bytes(b"changed")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_attest_rejects_changed_source_digest(self) -> None:
        self.post.write_text("b" * 64 + "  " + str(self.source_file) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(checker.EvidenceError, "source manifests differ"):
            self._attest()

    def test_attest_rejects_current_source_change(self) -> None:
        self.source_file.write_bytes(b"changed-current-source\n")
        with self.assertRaisesRegex(checker.EvidenceError, "current source tree"):
            self._attest()

    def test_attest_rejects_source_symlink_file(self) -> None:
        (self.source_file.parent / "linked.c").symlink_to(self.source_file.name)
        with self.assertRaisesRegex(checker.EvidenceError, "source tree symlink"):
            self._attest()

    def test_attest_rejects_source_symlink_directory(self) -> None:
        real_dir = self.source_file.parent / "real-dir"
        real_dir.mkdir()
        (self.source_file.parent / "linked-dir").symlink_to(
            real_dir.name, target_is_directory=True
        )
        with self.assertRaisesRegex(checker.EvidenceError, "source tree symlink"):
            self._attest()

    def test_attest_rejects_noncanonical_source_manifest_path(self) -> None:
        payload = self.manifest_payload()
        payload["source_immutability"]["baseline_manifest"] = str(
            self.baseline.parent / "nested" / ".." / self.baseline.name
        )
        self.manifest.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(checker.EvidenceError, "canonical lexical path"):
            self._attest()

    def test_attest_rejects_malformed_source_manifest(self) -> None:
        self.baseline.write_text("not-a-sha-manifest\n", encoding="utf-8")
        self.post.write_text("not-a-sha-manifest\n", encoding="utf-8")
        with self.assertRaisesRegex(checker.EvidenceError, "invalid source manifest"):
            self._attest()

    def test_attest_rejects_duplicate_source_manifest_path(self) -> None:
        row = self.baseline.read_text(encoding="utf-8")
        self.baseline.write_text(row + row, encoding="utf-8")
        self.post.write_text(row + row, encoding="utf-8")
        with self.assertRaisesRegex(checker.EvidenceError, "duplicate source manifest path"):
            self._attest()

    def test_verify_rejects_changed_matching_source_manifests(self) -> None:
        attestation = self._attest()
        self.source_file.write_bytes(b"changed-and-remanifested\n")
        changed = (
            hashlib.sha256(self.source_file.read_bytes()).hexdigest()
            + "  "
            + str(self.source_file)
            + "\n"
        )
        self.baseline.write_text(changed, encoding="utf-8")
        self.post.write_text(changed, encoding="utf-8")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_attest_rejects_missing_benchmark(self) -> None:
        payload = self.manifest_payload()
        payload["selected_benchmarks"].pop()
        payload["bench_results"].pop("999.specrand_ir")
        self.manifest.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(checker.EvidenceError, "required exact 10"):
            self._attest()

    def test_attest_rejects_missing_elf(self) -> None:
        first = next(iter(EXPECTED_EXECUTABLES))
        elf = Path(self.manifest_payload()["bench_results"][first]["executables"][0]["path"])
        elf.unlink()
        with self.assertRaisesRegex(checker.EvidenceError, "missing ELF"):
            self._attest()

    def test_attest_rejects_elf_symlink(self) -> None:
        elf = self.first_elf()
        target = elf.with_name("real-elf")
        elf.rename(target)
        elf.symlink_to(target.name)
        with self.assertRaisesRegex(checker.EvidenceError, "ELF symlink"):
            self._attest()

    def test_attest_rejects_noncanonical_elf_path(self) -> None:
        payload = self.manifest_payload()
        first = next(iter(EXPECTED_EXECUTABLES))
        row = payload["bench_results"][first]["executables"][0]
        path = Path(row["path"])
        row["path"] = str(path.parent / "nested" / ".." / path.name)
        self.manifest.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(checker.EvidenceError, "canonical lexical path"):
            self._attest()

    def test_attest_rejects_elf_symlink_component(self) -> None:
        elf = self.first_elf()
        exe_dir = elf.parent
        real_dir = exe_dir.with_name("real-exe")
        exe_dir.rename(real_dir)
        exe_dir.symlink_to(real_dir.name, target_is_directory=True)
        with self.assertRaisesRegex(checker.EvidenceError, "ELF symlink component"):
            self._attest()

    def test_attest_rejects_broken_sysroot_symlink(self) -> None:
        (self.sysroot / "broken").symlink_to("missing")
        with self.assertRaisesRegex(checker.EvidenceError, "broken sysroot symlink"):
            self._attest()

    def test_attest_rejects_sysroot_symlink_escape(self) -> None:
        outside = self.root / "outside-lib"
        outside.write_bytes(b"outside")
        (self.sysroot / "escape").symlink_to(os.path.relpath(outside, self.sysroot))
        with self.assertRaisesRegex(checker.EvidenceError, "escapes sysroot"):
            self._attest()

    def test_verify_binds_internal_sysroot_symlink_referent(self) -> None:
        alias = self.sysroot / "libc-alias.a"
        alias.symlink_to("lib/libc.a")
        attestation = self._attest()
        self.assertEqual(attestation["evidence"]["sysroot"]["symlink_referents"][0]["kind"], "file")
        (self.sysroot / "lib" / "libc.a").write_bytes(b"changed-libc")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def test_verify_rejects_changed_sysroot_regular_file(self) -> None:
        attestation = self._attest()
        (self.sysroot / "lib" / "libc.a").write_bytes(b"changed-regular-file")
        with self.assertRaisesRegex(checker.EvidenceError, "attestation does not match"):
            checker.verify_attestation(self.root, attestation)

    def first_elf(self, bench: str | None = None) -> Path:
        first = bench or next(iter(EXPECTED_EXECUTABLES))
        return Path(self.manifest_payload()["bench_results"][first]["executables"][0]["path"])

    def select_manifest_benchmarks(self, benches: list[str]) -> None:
        payload = self.manifest_payload()
        payload["selected_benchmarks"] = benches
        payload["bench_results"] = {
            bench: payload["bench_results"][bench] for bench in benches
        }
        payload["bench_optimize_flags"] = {
            bench: payload["bench_optimize_flags"][bench] for bench in benches
        }
        self.manifest.write_text(json.dumps(payload), encoding="utf-8")

    @staticmethod
    def _append(path: Path, text: str) -> None:
        with path.open("a", encoding="utf-8") as stream:
            stream.write(text)

    def manifest_payload(self) -> dict[str, object]:
        return json.loads(self.manifest.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
