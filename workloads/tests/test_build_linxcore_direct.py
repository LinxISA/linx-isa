#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "direct" / "build_linxcore_direct.py"
SPEC = importlib.util.spec_from_file_location("build_linxcore_direct", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
build_linxcore_direct = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_linxcore_direct)


class DirectBenchmarkManifestTest(unittest.TestCase):
    def test_check_rejects_score_claims_and_stale_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / "workloads" / "generated" / "linxcore-r678-direct"
            elf = out / "coremark" / "coremark.elf"
            elf.parent.mkdir(parents=True)
            elf.write_bytes(b"elf")
            (out / "coremark" / "manifest.json").write_text(json.dumps({
                "workload": "coremark",
                "lane": "direct-freestanding-et-exec",
                "semantic_only": True,
                "score_claimed": True,
                "iterations": 1,
                "elf": {
                    "path": "workloads/generated/linxcore-r678-direct/coremark/coremark.elf",
                    "sha256": "not-the-real-hash",
                    "type": "EXEC",
                    "entry": "0x10000",
                },
                "terminal_oracle": {"finisher_pass": "0x5555"},
            }))
            with mock.patch.object(build_linxcore_direct, "REPO_ROOT", root), \
                 mock.patch.object(build_linxcore_direct, "OUT_ROOT", out), \
                 mock.patch.object(build_linxcore_direct, "workloads", return_value={
                     "coremark": {"iterations": 1},
                 }):
                self.assertEqual(build_linxcore_direct.check(mock.Mock()), 1)


if __name__ == "__main__":
    unittest.main()
