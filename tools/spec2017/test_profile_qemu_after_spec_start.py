#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import profile_qemu_after_spec_start as profiler


class ProfileQemuAfterSpecStartTests(unittest.TestCase):
    def test_parse_ps_table_ignores_headers_and_bad_rows(self) -> None:
        rows = profiler._parse_ps_table(
            """
              PID  PPID COMMAND
              10     1 /bin/sh runner
              11    10 /tmp/qemu-system-linx64 -machine virt
              bad row
            """
        )

        self.assertEqual(rows[10], (1, "/bin/sh runner"))
        self.assertEqual(rows[11], (10, "/tmp/qemu-system-linx64 -machine virt"))
        self.assertNotIn("bad", rows)

    def test_descendants_finds_nested_qemu_child(self) -> None:
        rows = {
            100: (1, "python run_stage_qemu_matrix.py"),
            101: (100, "python run_int_rate_qemu.py"),
            102: (101, "/tmp/qemu-system-linx64 -machine virt"),
            200: (1, "/tmp/qemu-system-linx64 unrelated"),
        }

        self.assertEqual(profiler._descendants(rows, 100), {101, 102})

    def test_command_basename_ignores_qemu_argument(self) -> None:
        self.assertEqual(
            profiler._command_basename(
                "python3 run_stage_qemu_matrix.py --qemu /tmp/qemu-system-linx64"
            ),
            "python3",
        )
        self.assertEqual(
            profiler._command_basename("/tmp/qemu-system-linx64 -machine virt"),
            "qemu-system-linx64",
        )

    def test_marker_log_prefers_newest_matching_qemu_log(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            old = root / "old" / "qemu.log"
            new = root / "new" / "qemu.log"
            old.parent.mkdir()
            new.parent.mkdir()
            old.write_text("boot\nLINX_SPEC_START 505.mcf_r\n")
            new.write_text("boot\nLINX_SPEC_START 531.deepsjeng_r\n")
            os.utime(old, (1, 1))
            os.utime(new, (2, 2))

            self.assertEqual(profiler._find_marker_log(root, "LINX_SPEC_START"), new)

    def test_parse_top_stack_sample_extracts_qemu_and_unknown_frames(self) -> None:
        rows = profiler._parse_top_stack_sample(
            """
Call graph:
    omitted

Sort by top of stack, same collapsed (when >= 5):
        __select  (in libsystem_kernel.dylib)        22355
        probe_access_internal  (in qemu-system-linx64)        876
        ???  (in <unknown binary>)  [0x30008a7a4]        502
        tb_lookup  (in qemu-system-linx64)        548

Sort by top of stack, exclusive:
        ignored  (in qemu-system-linx64)        1
"""
        )

        self.assertEqual(rows[0]["symbol"], "__select")
        self.assertEqual(rows[1]["symbol"], "probe_access_internal")
        self.assertEqual(rows[1]["image"], "qemu-system-linx64")
        self.assertEqual(rows[1]["count"], 876)
        self.assertEqual(rows[2]["symbol"], "???")
        self.assertEqual(rows[2]["image"], "<unknown binary>")
        self.assertEqual(rows[2]["address"], "0x30008a7a4")
        self.assertEqual(rows[3]["symbol"], "tb_lookup")
        self.assertEqual(len(rows), 4)


if __name__ == "__main__":
    unittest.main()
