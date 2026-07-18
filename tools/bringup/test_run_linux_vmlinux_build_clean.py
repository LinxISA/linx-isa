#!/usr/bin/env python3
"""Regression tests for the clean Linux vmlinux build wrapper."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("run_linux_vmlinux_build_clean.sh")
PROVENANCE = Path(__file__).with_name("linux_vmlinux_provenance.py")


class LinuxVmlinuxBuildCleanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.base = Path(self.temp_dir.name)
        self.linux_root = self.base / "linux"
        self.out_dir = self.base / "out"
        self.linux_root.mkdir()

        (self.linux_root / "README").write_text("fixture\n", encoding="utf-8")
        self._run_git("init", "-q")
        self._run_git("config", "user.email", "vmlinux-test@example.invalid")
        self._run_git("config", "user.name", "Vmlinux Test")
        self._run_git("add", ".")
        self._run_git("commit", "-qm", "fixture")

        self.clang = self.base / "clang"
        self.clang.write_text(
            "#!/bin/sh\nprintf 'clang fixture 1.0\\n'\n", encoding="utf-8"
        )
        self.clang.chmod(0o755)
        self.ld_lld = self.base / "ld.lld"
        self.ld_lld.write_text(
            "#!/bin/sh\nprintf 'LLD fixture 1.0\\n'\n", encoding="utf-8"
        )
        self.ld_lld.chmod(0o755)
        self.hostcc = self.base / "hostcc"
        self.hostcc.write_text(
            "#!/bin/sh\nprintf 'hostcc fixture 1.0\\n'\n", encoding="utf-8"
        )
        self.hostcc.chmod(0o755)
        self.hostcxx = self.base / "hostcxx"
        self.hostcxx.write_text(
            "#!/bin/sh\nprintf 'hostcxx fixture 1.0\\n'\n", encoding="utf-8"
        )
        self.hostcxx.chmod(0o755)

        self.gmake = self.base / "gmake"
        self.gmake.write_text(
            """#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "--version" ]]; then
  printf 'gmake fixture 1.0\n'
  exit 0
fi
out=''
configure=0
build=0
for arg in "$@"; do
  case "$arg" in
    O=*) out="${arg#O=}" ;;
    linx_v150_defconfig|olddefconfig) configure=1 ;;
    vmlinux) build=1 ;;
  esac
done
mkdir -p "$out"
if [[ "$configure" == "1" ]]; then
  printf 'CONFIG_FAKE=y\\n' > "$out/.config"
fi
if [[ "$build" == "1" ]]; then
  if [[ -e "$out/stale-object" ]]; then
    echo 'stale output survived fresh mode' >&2
    exit 9
  fi
  if [[ "${FAKE_FAIL_BUILD:-0}" == "1" ]]; then
    exit 8
  fi
  if [[ "${FAKE_NOOP_BUILD:-0}" == "1" ]]; then
    exit 0
  fi
  if [[ "${FAKE_MUTATE_CONFIG:-0}" == "1" ]]; then
    printf 'CONFIG_DRIFT=y\\n' >> "$out/.config"
  fi
  if [[ -n "${FAKE_MUTATE_SOURCE:-}" ]]; then
    printf 'source drift\\n' >> "$FAKE_MUTATE_SOURCE"
  fi
  if [[ -n "${FAKE_MUTATE_CLANG:-}" ]]; then
    printf '# drift\\n' >> "$FAKE_MUTATE_CLANG"
  fi
  if [[ -n "${FAKE_MUTATE_GMAKE:-}" ]]; then
    printf '# drift\\n' >> "$FAKE_MUTATE_GMAKE"
  fi
  if [[ -n "${FAKE_MUTATE_HOSTCC:-}" ]]; then
    printf '# drift\\n' >> "$FAKE_MUTATE_HOSTCC"
  fi
  if [[ -n "${FAKE_MUTATE_HOSTCXX:-}" ]]; then
    printf '# drift\\n' >> "$FAKE_MUTATE_HOSTCXX"
  fi
  case "${FAKE_VMLINUX_KIND:-regular}" in
    empty) : > "$out/vmlinux" ;;
    symlink) printf 'target\\n' > "$out/vmlinux.real"; ln -sf vmlinux.real "$out/vmlinux" ;;
    *) printf 'fresh-vmlinux\\n' > "$out/vmlinux" ;;
  esac
fi
""",
            encoding="utf-8",
        )
        self.gmake.chmod(0o755)
        self.gmake_baseline = self.gmake.read_bytes()

    def _run_git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.linux_root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def _run(
        self,
        out_dir: Path,
        *extra: str,
        env_overrides: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(env_overrides or {})
        return subprocess.run(
            [
                "bash",
                str(SCRIPT),
                "--linux-root",
                str(self.linux_root),
                "--out-dir",
                str(out_dir),
                "--clang",
                str(self.clang),
                "--gmake",
                str(self.gmake),
                "--hostcc",
                str(self.hostcc),
                "--hostcxx",
                str(self.hostcxx),
                "--jobs",
                "1",
                *extra,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

    def _report(self, out_dir: Path | None = None) -> dict[str, object]:
        path = (out_dir or self.out_dir) / "vmlinux.provenance.json"
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_fresh_mode_removes_previous_output_before_build(self) -> None:
        first = self._run(self.out_dir, "--fresh")
        self.assertEqual(first.returncode, 0, first.stderr)
        (self.out_dir / "stale-object").write_text("stale\n", encoding="utf-8")

        result = self._run(self.out_dir, "--fresh")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.out_dir / "stale-object").exists())
        self.assertEqual(
            (self.out_dir / "vmlinux").read_text(encoding="utf-8"),
            "fresh-vmlinux\n",
        )
        self.assertTrue((self.out_dir / "vmlinux.provenance.json").is_file())

    def test_fresh_mode_refuses_unowned_nonempty_output(self) -> None:
        self.out_dir.mkdir()
        (self.out_dir / "unrelated").write_text("keep\n", encoding="utf-8")
        stale_report = self.out_dir / "vmlinux.provenance.json"
        stale_report.write_text("unowned-report\n", encoding="utf-8")

        result = self._run(self.out_dir, "--fresh")

        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to remove unowned", result.stderr)
        self.assertTrue((self.out_dir / "unrelated").exists())
        self.assertEqual(stale_report.read_text(encoding="utf-8"), "unowned-report\n")

    def test_fresh_mode_refuses_output_inside_source_tree(self) -> None:
        result = self._run(self.linux_root / "build", "--fresh")

        self.assertEqual(result.returncode, 2)
        self.assertIn("fresh output directory must be outside", result.stderr)

    def test_fresh_mode_refuses_symlink_output(self) -> None:
        target = self.base / "target"
        target.mkdir()
        link = self.base / "out-link"
        link.symlink_to(target, target_is_directory=True)

        result = self._run(link, "--fresh")

        self.assertEqual(result.returncode, 2)
        self.assertIn("must not be a symbolic link", result.stderr)

    def test_incremental_mode_refuses_symlink_output_without_deleting_target(self) -> None:
        target = self.base / "incremental-real-out"
        target.mkdir()
        identities = {
            "vmlinux": b"existing-vmlinux\n",
            ".config": b"CONFIG_EXISTING=y\n",
            "vmlinux.provenance.json": b"existing-provenance\n",
        }
        for name, contents in identities.items():
            (target / name).write_bytes(contents)
        link = self.base / "incremental-out-link"
        link.symlink_to(target, target_is_directory=True)

        result = self._run(
            link,
            env_overrides={"FAKE_NOOP_BUILD": "1"},
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("must not be a symbolic link", result.stderr)
        self.assertTrue(link.is_symlink())
        for name, contents in identities.items():
            self.assertEqual((target / name).read_bytes(), contents)

    def test_success_writes_and_self_verifies_complete_provenance(self) -> None:
        result = self._run(self.out_dir, "--fresh", "--refresh-defconfig")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = self._report()
        self.assertEqual(report["schema_version"], "linx-linux-vmlinux-build-provenance-v1")
        self.assertTrue(report["ok"])
        self.assertEqual(report["source"]["head"], self._run_git("rev-parse", "HEAD").stdout.strip())
        self.assertTrue(report["source"]["clean"])
        self.assertEqual(report["source"]["dirty_paths"], [])
        self.assertEqual(report["tools"]["clang"]["sha256"], self._sha(self.clang))
        self.assertEqual(report["tools"]["ld_lld"]["sha256"], self._sha(self.ld_lld))
        self.assertEqual(report["tools"]["gmake"]["sha256"], self._sha(self.gmake))
        self.assertEqual(report["tools"]["hostcc"]["sha256"], self._sha(self.hostcc))
        self.assertEqual(report["tools"]["hostcxx"]["sha256"], self._sha(self.hostcxx))
        self.assertEqual(report["inputs"]["config"]["sha256"], self._sha(self.out_dir / ".config"))
        self.assertEqual(report["inputs"]["script"]["sha256"], self._sha(SCRIPT))
        self.assertEqual(
            report["inputs"]["provenance_helper"]["sha256"], self._sha(PROVENANCE)
        )
        self.assertEqual(report["output"]["sha256"], self._sha(self.out_dir / "vmlinux"))
        self.assertEqual(report["build"]["mode"], "fresh")
        self.assertEqual(report["build"]["target"], "vmlinux")
        self.assertEqual(len(report["build"]["commands"]), 2)
        fresh_marker = self.out_dir / ".linx_linux_vmlinux_fresh_generation"
        self.assertEqual(
            report["inputs"]["fresh_generation"]["sha256"], self._sha(fresh_marker)
        )
        self.assertEqual(
            report["constraints"], ["trusted_parent_manifest_must_bind_report_sha256"]
        )
        verify = subprocess.run(
            [
                "python3", str(PROVENANCE), "verify",
                "--provenance", str(self.out_dir / "vmlinux.provenance.json"),
                "--require-clean-source", "--require-fresh",
                "--require-linux-head", report["source"]["head"],
                "--require-clang-sha", report["tools"]["clang"]["sha256"],
                "--require-ld-lld-sha", report["tools"]["ld_lld"]["sha256"],
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(verify.returncode, 0, verify.stderr)

    def test_dirty_source_is_content_bound_and_promotion_rejects_it(self) -> None:
        (self.linux_root / "README").write_text("dirty tracked\n", encoding="utf-8")
        (self.linux_root / "untracked file").write_text("payload\n", encoding="utf-8")
        (self.linux_root / "untracked-link").symlink_to("untracked file")

        result = self._run(self.out_dir, "--fresh")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = self._report()
        self.assertFalse(report["source"]["clean"])
        self.assertEqual(
            [row["path"] for row in report["source"]["dirty_paths"]],
            ["README", "untracked file", "untracked-link"],
        )
        verify = subprocess.run(
            ["python3", str(PROVENANCE), "verify", "--provenance", str(self.out_dir / "vmlinux.provenance.json")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.assertEqual(verify.returncode, 0, verify.stderr)
        promoted = subprocess.run(
            ["python3", str(PROVENANCE), "verify", "--provenance", str(self.out_dir / "vmlinux.provenance.json"), "--require-clean-source"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.assertEqual(promoted.returncode, 2)
        (self.linux_root / "untracked file").write_text("changed\n", encoding="utf-8")
        drifted = subprocess.run(
            ["python3", str(PROVENANCE), "verify", "--provenance", str(self.out_dir / "vmlinux.provenance.json")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.assertEqual(drifted.returncode, 2)

    def test_failed_rebuild_removes_stale_provenance(self) -> None:
        first = self._run(self.out_dir, "--fresh")
        self.assertEqual(first.returncode, 0, first.stderr)

        failed = self._run(
            self.out_dir,
            "--fresh",
            env_overrides={"FAKE_FAIL_BUILD": "1"},
        )

        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse((self.out_dir / "vmlinux.provenance.json").exists())

    def test_noop_incremental_make_cannot_certify_stale_vmlinux(self) -> None:
        first = self._run(self.out_dir, "--fresh")
        self.assertEqual(first.returncode, 0, first.stderr)

        noop = self._run(
            self.out_dir,
            env_overrides={"FAKE_NOOP_BUILD": "1"},
        )

        self.assertNotEqual(noop.returncode, 0)
        self.assertFalse((self.out_dir / "vmlinux").exists())
        self.assertFalse((self.out_dir / "vmlinux.provenance.json").exists())

    def test_dangling_relative_stashed_symlink_restored_on_success_and_failure(self) -> None:
        generated = self.linux_root / "include/generated"
        generated.parent.mkdir(parents=True)
        generated.symlink_to("../missing-generated")
        expected_target = os.readlink(generated)

        success = self._run(self.out_dir, "--fresh")
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertTrue(generated.is_symlink())
        self.assertEqual(os.readlink(generated), expected_target)

        failure = self._run(
            self.out_dir,
            "--fresh",
            env_overrides={"FAKE_FAIL_BUILD": "1"},
        )
        self.assertNotEqual(failure.returncode, 0)
        self.assertTrue(generated.is_symlink())
        self.assertEqual(os.readlink(generated), expected_target)
        self.assertFalse((self.out_dir / "vmlinux.provenance.json").exists())

    def test_fallible_validation_invalidates_owned_stale_report(self) -> None:
        scenarios = ("jobs", "clang", "gmake")
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                first = self._run(self.out_dir, "--fresh")
                self.assertEqual(first.returncode, 0, first.stderr)
                report = self.out_dir / "vmlinux.provenance.json"
                self.assertTrue(report.is_file())

                if scenario == "jobs":
                    result = self._run(self.out_dir, "--jobs", "invalid")
                else:
                    tool = self.clang if scenario == "clang" else self.gmake
                    backup = tool.with_suffix(".missing")
                    tool.rename(backup)
                    try:
                        result = self._run(self.out_dir)
                    finally:
                        backup.rename(tool)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(report.exists())

    def test_provenance_aliases_never_delete_bound_paths(self) -> None:
        first = self._run(self.out_dir, "--fresh")
        self.assertEqual(first.returncode, 0, first.stderr)
        bound_paths = (
            self.clang,
            self.ld_lld,
            self.gmake,
            self.hostcc,
            self.hostcxx,
            SCRIPT,
            PROVENANCE,
            self.out_dir / ".config",
            self.out_dir / "vmlinux",
            self.out_dir / ".linx_linux_vmlinux_build_dir",
            self.out_dir / ".linx_linux_vmlinux_fresh_generation",
        )
        for bound in bound_paths:
            with self.subTest(bound=bound):
                before = bound.read_bytes()
                result = self._run(
                    self.out_dir,
                    "--fresh",
                    "--provenance-out",
                    str(bound),
                )
                self.assertEqual(result.returncode, 2)
                self.assertEqual(bound.read_bytes(), before)

    def test_missing_lld_and_empty_tool_version_fail_without_report(self) -> None:
        self.ld_lld.unlink()
        missing = self._run(self.out_dir, "--fresh")
        self.assertEqual(missing.returncode, 2)
        self.assertFalse((self.out_dir / "vmlinux.provenance.json").exists())

        self.ld_lld.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.ld_lld.chmod(0o755)
        empty = self._run(self.out_dir, "--fresh")
        self.assertEqual(empty.returncode, 2)
        self.assertIn("did not succeed with output", empty.stderr)
        self.assertFalse((self.out_dir / "vmlinux.provenance.json").exists())

    def test_empty_and_symlink_vmlinux_fail_without_report(self) -> None:
        for kind in ("empty", "symlink"):
            with self.subTest(kind=kind):
                result = self._run(
                    self.out_dir,
                    "--fresh",
                    env_overrides={"FAKE_VMLINUX_KIND": kind},
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.out_dir / "vmlinux.provenance.json").exists())

    def test_config_source_and_tool_drift_fail_closed(self) -> None:
        cases = (
            {"FAKE_MUTATE_CONFIG": "1"},
            {"FAKE_MUTATE_SOURCE": str(self.linux_root / "README")},
            {"FAKE_MUTATE_CLANG": str(self.clang)},
            {"FAKE_MUTATE_GMAKE": str(self.gmake)},
            {"FAKE_MUTATE_HOSTCC": str(self.hostcc)},
            {"FAKE_MUTATE_HOSTCXX": str(self.hostcxx)},
        )
        for environment in cases:
            with self.subTest(environment=environment):
                # Restore test fixture identities between subtests.
                self._run_git("checkout", "--", "README")
                self.clang.write_text("#!/bin/sh\nprintf 'clang fixture 1.0\\n'\n", encoding="utf-8")
                self.clang.chmod(0o755)
                self.gmake.write_bytes(self.gmake_baseline)
                self.gmake.chmod(0o755)
                self.hostcc.write_text("#!/bin/sh\nprintf 'hostcc fixture 1.0\\n'\n", encoding="utf-8")
                self.hostcc.chmod(0o755)
                self.hostcxx.write_text("#!/bin/sh\nprintf 'hostcxx fixture 1.0\\n'\n", encoding="utf-8")
                self.hostcxx.chmod(0o755)
                result = self._run(self.out_dir, "--fresh", env_overrides=environment)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.out_dir / "vmlinux.provenance.json").exists())

    def test_verifier_detects_output_and_promotion_mismatch(self) -> None:
        result = self._run(self.out_dir, "--fresh")
        self.assertEqual(result.returncode, 0, result.stderr)
        provenance = self.out_dir / "vmlinux.provenance.json"
        wrong_head = subprocess.run(
            ["python3", str(PROVENANCE), "verify", "--provenance", str(provenance), "--require-linux-head", "0" * 40],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.assertEqual(wrong_head.returncode, 2)
        (self.out_dir / "vmlinux").write_text("tampered\n", encoding="utf-8")
        tampered = subprocess.run(
            ["python3", str(PROVENANCE), "verify", "--provenance", str(provenance)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        self.assertEqual(tampered.returncode, 2)

    def test_incremental_build_is_valid_evidence_but_not_fresh_promotion(self) -> None:
        first = self._run(self.out_dir, "--fresh")
        self.assertEqual(first.returncode, 0, first.stderr)

        incremental = self._run(self.out_dir)

        self.assertEqual(incremental.returncode, 0, incremental.stderr)
        report = self._report()
        self.assertEqual(report["build"]["mode"], "incremental")
        verifier = subprocess.run(
            [
                "python3", str(PROVENANCE), "verify",
                "--provenance", str(self.out_dir / "vmlinux.provenance.json"),
                "--require-fresh",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(verifier.returncode, 2)
        self.assertFalse(
            (self.out_dir / ".linx_linux_vmlinux_fresh_generation").exists()
        )

    def test_editing_incremental_mode_to_fresh_does_not_promote(self) -> None:
        first = self._run(self.out_dir, "--fresh")
        self.assertEqual(first.returncode, 0, first.stderr)
        incremental = self._run(self.out_dir)
        self.assertEqual(incremental.returncode, 0, incremental.stderr)
        provenance = self.out_dir / "vmlinux.provenance.json"
        report = self._report()
        self.assertIsNone(report["inputs"]["fresh_generation"])

        report["build"]["mode"] = "fresh"
        provenance.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        verifier = subprocess.run(
            [
                "python3", str(PROVENANCE), "verify",
                "--provenance", str(provenance), "--require-fresh",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(verifier.returncode, 2)

    def test_verifier_rejects_path_and_command_metadata_tampering(self) -> None:
        result = self._run(self.out_dir, "--fresh")
        self.assertEqual(result.returncode, 0, result.stderr)
        provenance = self.out_dir / "vmlinux.provenance.json"
        baseline = self._report()

        def wrong_config_path(report: dict[str, object]) -> None:
            report["inputs"]["config"] = dict(report["output"])

        def wrong_fresh_marker_path(report: dict[str, object]) -> None:
            report["inputs"]["fresh_generation"] = dict(report["inputs"]["config"])

        def wrong_output_path(report: dict[str, object]) -> None:
            report["output"] = dict(report["inputs"]["config"])

        def wrong_command_output(report: dict[str, object]) -> None:
            command = report["build"]["commands"][-1]
            command[command.index(f"O={self.out_dir}")] = "O=/tmp/not-the-build-output"

        def wrong_jobs_metadata(report: dict[str, object]) -> None:
            report["build"]["jobs"] = 2

        def wrong_cc_target(report: dict[str, object]) -> None:
            command = report["build"]["commands"][-1]
            expected = (
                f"CC={self.clang} "
                "--target=linx64-unknown-linux-gnu -fintegrated-as"
            )
            command[command.index(expected)] = f"CC={self.clang} --target=wrong"

        def duplicate_output_override(report: dict[str, object]) -> None:
            report["build"]["commands"][-1].append("O=/tmp/attacker-output")

        def duplicate_cc_override(report: dict[str, object]) -> None:
            report["build"]["commands"][-1].append(
                f"CC={self.clang} --target=wrong"
            )

        def duplicate_jobs_override(report: dict[str, object]) -> None:
            report["build"]["commands"][-1].append("-j999")

        mutations = (
            wrong_config_path,
            wrong_fresh_marker_path,
            wrong_output_path,
            wrong_command_output,
            wrong_jobs_metadata,
            wrong_cc_target,
            duplicate_output_override,
            duplicate_cc_override,
            duplicate_jobs_override,
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate.__name__):
                report = json.loads(json.dumps(baseline))
                mutate(report)
                provenance.write_text(
                    json.dumps(report, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                verifier = subprocess.run(
                    ["python3", str(PROVENANCE), "verify", "--provenance", str(provenance)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                self.assertEqual(verifier.returncode, 2)


if __name__ == "__main__":
    unittest.main()
