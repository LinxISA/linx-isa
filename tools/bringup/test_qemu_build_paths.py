#!/usr/bin/env python3
from __future__ import annotations

import tempfile
from pathlib import Path
import unittest
from unittest import mock

import qemu_build_paths


class QemuBuildPathsTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
