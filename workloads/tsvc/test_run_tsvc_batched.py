#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


RUNNER = Path(__file__).with_name("run_tsvc_batched.py")


def _load_runner_module():
    runner_dir = str(RUNNER.parent)
    if runner_dir not in sys.path:
        sys.path.insert(0, runner_dir)
    spec = importlib.util.spec_from_file_location("linx_tsvc_batched_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BatchProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = _load_runner_module()
        self.receipt = {
            "tools": {
                "clang": {"path": "/tools/clang", "sha256": "1" * 64},
                "lld": {"path": "/tools/lld", "sha256": "2" * 64},
                "llvm_objdump": {"path": "/tools/llvm-objdump", "sha256": "3" * 64},
                "qemu": {"path": "/tools/qemu", "sha256": "4" * 64},
            },
            "clang_revision": "a" * 40,
            "llvm_head": "a" * 40,
            "qemu": {
                "qemu_repo_head": "b" * 40,
                "clean_build_marker": f"{'b' * 40}:worktree",
            },
            "scoped_dirty": {
                "tsvc": {"available": True, "dirty_paths": []},
                "llvm": {"available": True, "dirty_paths": []},
                "qemu": {"available": True, "dirty_paths": []},
            },
        }

    def test_identical_batch_provenance_passes(self) -> None:
        self.runner._require_matching_provenance(self.receipt, dict(self.receipt), 2)

    def test_batch_provenance_mismatch_fails_closed(self) -> None:
        changed = {**self.receipt, "clang_revision": "c" * 40}
        with self.assertRaisesRegex(self.runner.BatchFailure, "provenance mismatch"):
            self.runner._require_matching_provenance(self.receipt, changed, 2)

    def _batch_payload(
        self, root: Path, batch_index: int, provenance: dict[str, object]
    ) -> dict[str, object]:
        stdout_path = root / f"batch-{batch_index}.stdout"
        stderr_path = root / f"batch-{batch_index}.stderr"
        driver_stdout = root / f"batch-{batch_index}.driver.stdout"
        driver_stderr = root / f"batch-{batch_index}.driver.stderr"
        stdout_path.write_text(
            f"Loop \tTime(sec) \tChecksum\n s{batch_index}\t1\t0x1\n",
            encoding="utf-8",
        )
        for path in (stderr_path, driver_stdout, driver_stderr):
            path.write_text("", encoding="utf-8")
        return {
            "batch_index": batch_index,
            "status": "pass",
            "returncode": 0,
            "elapsed_seconds": 0.1,
            "kernels": [f"s{batch_index}"],
            "coverage": {"vectorized": 1, "total": 1},
            "gate": {"provenance": provenance},
            "provenance": provenance,
            "stdout_path": stdout_path,
            "stderr_path": stderr_path,
            "driver_stdout": driver_stdout,
            "driver_stderr": driver_stderr,
        }

    def test_aggregate_preserves_identical_batch_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            payloads = [
                self._batch_payload(root, 1, copy.deepcopy(self.receipt)),
                self._batch_payload(root, 2, copy.deepcopy(self.receipt)),
            ]
            with (
                mock.patch.object(
                    self.runner,
                    "_resolve_kernel_list",
                    return_value=(root / "src", ["s1", "s2"]),
                ),
                mock.patch.object(self.runner, "_run_batch", side_effect=payloads),
            ):
                self.assertEqual(
                    self.runner.main(["--batch-size", "1", "--out-dir", td]), 0
                )

            gate = json.loads(
                (root / "reports" / "tsvc" / "gate_result.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertTrue(gate["provenance_consistent"])
            self.assertEqual(gate["provenance"], self.receipt)
            self.assertEqual(
                [batch["provenance"] for batch in gate["batches"]],
                [self.receipt, self.receipt],
            )

    def test_aggregate_fails_on_changed_batch_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            changed = copy.deepcopy(self.receipt)
            changed["tools"]["qemu"]["sha256"] = "9" * 64
            payloads = [
                self._batch_payload(root, 1, copy.deepcopy(self.receipt)),
                self._batch_payload(root, 2, changed),
            ]
            with (
                mock.patch.object(
                    self.runner,
                    "_resolve_kernel_list",
                    return_value=(root / "src", ["s1", "s2"]),
                ),
                mock.patch.object(self.runner, "_run_batch", side_effect=payloads),
                self.assertRaisesRegex(SystemExit, "provenance mismatch"),
            ):
                self.runner.main(["--batch-size", "1", "--out-dir", td])

            gate = json.loads(
                (root / "reports" / "tsvc" / "gate_result.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertFalse(gate["ok"])
            self.assertFalse(gate["provenance_consistent"])
            self.assertIn("provenance mismatch", gate["error"])


if __name__ == "__main__":
    unittest.main()
