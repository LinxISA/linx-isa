#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
IMPORTER = ROOT / "tools" / "isa" / "import_pto_v0580.py"


def load_importer():
    spec = importlib.util.spec_from_file_location("import_pto_v0580", IMPORTER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {IMPORTER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()


class ImportSourceIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="linx-pto-import-")
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test")
        git(self.root, "config", "user.email", "test@example.com")
        self.source = self.root / "spec/release-manifest.json"
        self.source.parent.mkdir(parents=True)
        self.source.write_text('{"release":"test"}\n', encoding="utf-8")
        git(self.root, "add", "spec/release-manifest.json")
        git(self.root, "commit", "-q", "-m", "fixture")
        git(self.root, "tag", "-a", "vtest", "-m", "fixture publication")
        self.commit = git(self.root, "rev-parse", "HEAD")
        self.tree = git(self.root, "rev-parse", "HEAD^{tree}")
        self.importer = load_importer()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def validate(self, tag: str = "vtest") -> tuple[str, str]:
        return self.importer.validate_source_git_identity(
            self.root,
            {"manifest": self.source},
            expected_commit=self.commit,
            expected_tree=self.tree,
            publication_tag=tag,
        )

    def test_accepts_exact_annotated_tagged_source(self) -> None:
        self.assertEqual(self.validate(), (self.commit, self.tree))

    def test_rejects_dirty_canonical_input(self) -> None:
        self.source.write_text('{"release":"forged"}\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs from"):
            self.validate()

    def test_rejects_lightweight_publication_tag(self) -> None:
        git(self.root, "tag", "lightweight")
        with self.assertRaisesRegex(ValueError, "must be annotated"):
            self.validate("lightweight")

    def test_rejects_unexpected_commit_identity(self) -> None:
        with self.assertRaisesRegex(ValueError, "frozen publication identity"):
            self.importer.validate_source_git_identity(
                self.root,
                {"manifest": self.source},
                expected_commit="0" * 40,
                expected_tree=self.tree,
                publication_tag="vtest",
            )

    def test_rejects_unexpected_tree_identity(self) -> None:
        with self.assertRaisesRegex(ValueError, "frozen publication identity"):
            self.importer.validate_source_git_identity(
                self.root,
                {"manifest": self.source},
                expected_commit=self.commit,
                expected_tree="0" * 40,
                publication_tag="vtest",
            )

    def test_rejects_tag_that_does_not_peel_to_head(self) -> None:
        self.source.write_text('{"release":"next"}\n', encoding="utf-8")
        git(self.root, "add", "spec/release-manifest.json")
        git(self.root, "commit", "-q", "-m", "next")
        with self.assertRaisesRegex(ValueError, "does not peel to HEAD"):
            self.validate()


if __name__ == "__main__":
    unittest.main()
