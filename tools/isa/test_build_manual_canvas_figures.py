#!/usr/bin/env python3
"""Focused provenance checks for the Silicon Canvas manual builder."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_manual_canvas_figures import TOOL_COMMIT, verify_tool


class ToolIdentityTests(unittest.TestCase):
    def make_repo(self, root: Path) -> str:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(
            ["git", "-C", str(root), "config", "user.email", "test@example.com"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(root), "config", "user.name", "Test"], check=True
        )
        package = root / "src" / "silicon_canvas"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "fixture"], check=True)
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()

    def test_rejects_wrong_checkout_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            actual = self.make_repo(root)
            self.assertNotEqual(actual, TOOL_COMMIT)
            with self.assertRaisesRegex(RuntimeError, "expected"):
                verify_tool(Path("/bin/true"), root)

    def test_rejects_foreign_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            root = temporary_root / "repo"
            commit = self.make_repo(root)
            executable = temporary_root / "foreign-mcp"
            executable.write_text(
                f"#!{sys.executable}\nfrom silicon_canvas.mcp_server import main\n",
                encoding="utf-8",
            )
            executable.chmod(0o755)
            with mock.patch("build_manual_canvas_figures.TOOL_COMMIT", commit):
                with self.assertRaisesRegex(RuntimeError, "cannot import|differs"):
                    verify_tool(executable, root)


if __name__ == "__main__":
    unittest.main()
