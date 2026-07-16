#!/usr/bin/env python3
"""Regression tests for the Linx Linux source-completeness gate."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.bringup.check_linux_source_completeness import REQUIRED_SOURCES


SCRIPT = Path(__file__).with_name("check_linux_source_completeness.py")


class LinuxSourceCompletenessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.repo = Path(self.temp_dir.name) / "linux"
        self.repo.mkdir()
        self.git("init", "-q")
        (self.repo / ".gitignore").write_text(
            "*.s\n!arch/linx/**/*.S\n", encoding="utf-8"
        )
        for relative in REQUIRED_SOURCES:
            source = self.repo / relative
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("/* fixture */\n", encoding="utf-8")
        self.git("add", ".")

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def run_gate(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--linux-root", str(self.repo)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_accepts_complete_tracked_tree(self) -> None:
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("15 tracked", result.stdout)

    def test_rejects_missing_required_source(self) -> None:
        missing = REQUIRED_SOURCES[0]
        (self.repo / missing).unlink()
        result = self.run_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"E_LINUX_SOURCE_MISSING: {missing}", result.stderr)

    def test_rejects_untracked_uppercase_assembly(self) -> None:
        extra = self.repo / "arch/linx/kernel/untracked.S"
        extra.write_text("/* untracked */\n", encoding="utf-8")
        result = self.run_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("E_LINUX_SOURCE_UNTRACKED: arch/linx/kernel/untracked.S", result.stderr)

    def test_rejects_case_insensitive_ignore_hazard(self) -> None:
        (self.repo / ".gitignore").write_text("*.s\n", encoding="utf-8")
        self.git("config", "core.ignorecase", "true")
        result = self.run_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("E_LINUX_SOURCE_IGNORED:", result.stderr)

    def test_rejects_retired_isa_spelling(self) -> None:
        source = self.repo / REQUIRED_SOURCES[0]
        source.write_text("b.attr atomic\nL.BSTART.std fall\n", encoding="utf-8")
        result = self.run_gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("E_LINUX_SOURCE_RETIRED_B_ATTR:", result.stderr)
        self.assertIn("E_LINUX_SOURCE_RETIRED_L_BSTART:", result.stderr)


if __name__ == "__main__":
    unittest.main()
