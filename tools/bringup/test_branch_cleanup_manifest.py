#!/usr/bin/env python3
"""Regression tests for fail-closed branch cleanup manifest validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools/bringup/check_branch_cleanup_manifest.py"


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)


class BranchCleanupManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        run("git", "init", "-b", "main", cwd=self.root)
        run("git", "config", "user.name", "Test", cwd=self.root)
        run("git", "config", "user.email", "test@example.invalid", cwd=self.root)
        (self.root / "seed").write_text("one\n", encoding="utf-8")
        run("git", "add", "seed", cwd=self.root)
        run("git", "commit", "-m", "seed", cwd=self.root)
        self.base = run("git", "rev-parse", "HEAD", cwd=self.root).stdout.strip()
        run("git", "branch", "stale", cwd=self.root)
        run("git", "tag", "release", cwd=self.root)
        self.manifest = self.root / "cleanup.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def entry(self, *, scope: str, ref: str, action: str, present: bool = True) -> dict[str, object]:
        return {
            "repository": ".",
            "scope": scope,
            "ref": ref,
            "oid": self.base,
            "action": action,
            "classification": "test-fixture",
            "evidence": {
                "kind": "ancestry",
                "replacement_oid": self.base,
                "summary": "fixture content is retained by the integration commit",
            },
            "required_integration_commit": self.base,
            "attached_worktree_prohibited": action == "delete",
            "pre_state": {"expected_present": present},
            "post_state": {"expected_present": action == "retain"},
        }

    def write_manifest(self, entries: list[dict[str, object]]) -> None:
        self.manifest.write_text(
            json.dumps({"schema": "linx-branch-cleanup-v1", "entries": entries}),
            encoding="utf-8",
        )

    def check(self, mode: str) -> subprocess.CompletedProcess[str]:
        return run(
            sys.executable,
            str(CHECKER),
            "--manifest",
            str(self.manifest),
            "--mode",
            mode,
            cwd=self.root,
            check=False,
        )

    def test_exact_refs_pass_static_and_pre_delete(self) -> None:
        self.write_manifest(
            [
                self.entry(scope="local", ref="stale", action="delete"),
                self.entry(scope="tag", ref="release", action="retain"),
            ]
        )
        self.assertEqual(self.check("static").returncode, 0)
        self.assertEqual(self.check("pre-delete").returncode, 0)

    def test_moved_delete_oid_fails(self) -> None:
        self.write_manifest([self.entry(scope="local", ref="stale", action="delete")])
        run("git", "switch", "stale", cwd=self.root)
        (self.root / "seed").write_text("two\n", encoding="utf-8")
        run("git", "commit", "-am", "move", cwd=self.root)
        run("git", "switch", "main", cwd=self.root)
        result = self.check("pre-delete")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("OID mismatch", result.stderr)

    def test_missing_retained_tag_fails_post_delete(self) -> None:
        self.write_manifest([self.entry(scope="tag", ref="release", action="retain")])
        run("git", "tag", "-d", "release", cwd=self.root)
        result = self.check("post-delete")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected present", result.stderr)

    def test_attached_delete_worktree_fails(self) -> None:
        self.write_manifest([self.entry(scope="local", ref="stale", action="delete")])
        worktree = Path(self.temp.name) / "attached"
        run("git", "worktree", "add", str(worktree), "stale", cwd=self.root)
        result = self.check("pre-delete")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("attached worktree", result.stderr)

    def test_transient_integration_commit_fails_static_validation(self) -> None:
        run("git", "switch", "--detach", self.base, cwd=self.root)
        (self.root / "transient").write_text("review-only\n", encoding="utf-8")
        run("git", "add", "transient", cwd=self.root)
        run("git", "commit", "-m", "transient review commit", cwd=self.root)
        transient = run("git", "rev-parse", "HEAD", cwd=self.root).stdout.strip()
        run("git", "switch", "main", cwd=self.root)

        entry = self.entry(scope="local", ref="stale", action="delete")
        entry["required_integration_commit"] = transient
        entry["evidence"]["replacement_oid"] = transient
        self.write_manifest([entry])

        result = self.check("static")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be an ancestor of HEAD", result.stderr)


if __name__ == "__main__":
    unittest.main()
