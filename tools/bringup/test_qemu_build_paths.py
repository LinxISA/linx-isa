#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import os
from pathlib import Path
import unittest
from unittest import mock

import qemu_build_paths


class QemuBuildPathsTests(unittest.TestCase):
    def test_default_requires_explicit_or_head_matched_clean_binary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "emulator" / "qemu").mkdir(parents=True)
            with (
                mock.patch.dict(os.environ, {"QEMU_CLEAN_OUT_DIR": str(root / "out")}, clear=True),
                mock.patch.object(qemu_build_paths, "_qemu_head", return_value="abc123"),
            ):
                with self.assertRaisesRegex(FileNotFoundError, "HEAD-matched clean build"):
                    qemu_build_paths.default_qemu_binary(root)

    def test_default_accepts_explicit_qemu_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            binary = Path(td) / "qemu-system-linx64"
            binary.write_text("#!/bin/sh\n", encoding="utf-8")
            binary.chmod(0o755)
            with mock.patch.dict(os.environ, {"QEMU": str(binary)}, clear=True):
                self.assertEqual(qemu_build_paths.default_qemu_binary(Path(td)), binary)

    def test_default_accepts_head_matched_clean_binary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "emulator" / "qemu").mkdir(parents=True)
            out = root / "out"
            out.mkdir()
            binary = out / "qemu-system-linx64"
            binary.write_text("#!/bin/sh\n", encoding="utf-8")
            binary.chmod(0o755)
            (out / ".linx_qemu_clean_head").write_text("abc123:worktree\n", encoding="utf-8")
            with (
                mock.patch.dict(os.environ, {"QEMU_CLEAN_OUT_DIR": str(out)}, clear=True),
                mock.patch.object(qemu_build_paths, "_qemu_head", return_value="abc123"),
            ):
                self.assertEqual(qemu_build_paths.default_qemu_binary(root), binary)

    def test_qemu_binary_provenance_reports_clean_marker_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qemu_root = root / "emulator" / "qemu"
            out_dir = root / "out"
            qemu_root.mkdir(parents=True)
            out_dir.mkdir()
            binary = out_dir / "qemu-system-linx64"
            binary.write_text("#!/bin/sh\n", encoding="utf-8")
            marker = out_dir / ".linx_qemu_clean_head"
            marker.write_text("abc123:worktree\n", encoding="utf-8")

            with (
                mock.patch.object(qemu_build_paths, "_qemu_head", return_value="abc123"),
                mock.patch.object(qemu_build_paths, "_qemu_tracked_dirty", return_value=False),
                mock.patch.object(qemu_build_paths, "_qemu_version", return_value="QEMU test version"),
            ):
                info = qemu_build_paths.qemu_binary_provenance(root, binary)

        self.assertEqual(info["qemu_repo_head"], "abc123")
        self.assertEqual(info["clean_build_marker"], "abc123:worktree")
        self.assertTrue(info["clean_build_marker_matches_head"])
        self.assertTrue(info["clean_build_for_head"])
        self.assertEqual(info["version"], "QEMU test version")
        self.assertEqual(
            info["sha256"],
            "a8076d3d28d21e02012b20eaf7dbf75409a6277134439025f282e368e3305abf",
        )

    def test_qemu_binary_provenance_flags_missing_marker(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qemu_root = root / "emulator" / "qemu"
            out_dir = root / "out"
            qemu_root.mkdir(parents=True)
            out_dir.mkdir()
            binary = out_dir / "qemu-system-linx64"
            binary.write_text("#!/bin/sh\n", encoding="utf-8")

            with (
                mock.patch.object(qemu_build_paths, "_qemu_head", return_value="abc123"),
                mock.patch.object(qemu_build_paths, "_qemu_tracked_dirty", return_value=False),
                mock.patch.object(qemu_build_paths, "_qemu_version", return_value="QEMU test version"),
            ):
                info = qemu_build_paths.qemu_binary_provenance(root, binary)

        self.assertEqual(info["clean_build_marker"], "")
        self.assertFalse(info["clean_build_marker_matches_head"])
        self.assertFalse(info["clean_build_for_head"])
        self.assertEqual(
            info["sha256"],
            "a8076d3d28d21e02012b20eaf7dbf75409a6277134439025f282e368e3305abf",
        )

    def test_require_clean_qemu_rejects_unattested_binary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "emulator" / "qemu").mkdir(parents=True)
            binary = root / "qemu-system-linx64"
            binary.write_text("#!/bin/sh\n", encoding="utf-8")
            binary.chmod(0o755)
            with (
                mock.patch.object(qemu_build_paths, "_qemu_head", return_value="abc123"),
                mock.patch.object(qemu_build_paths, "_qemu_tracked_dirty", return_value=False),
                mock.patch.object(qemu_build_paths, "_qemu_version", return_value="QEMU test version"),
            ):
                with self.assertRaisesRegex(RuntimeError, "HEAD-matched clean QEMU"):
                    qemu_build_paths.require_clean_qemu_binary(root, binary)


if __name__ == "__main__":
    unittest.main()
