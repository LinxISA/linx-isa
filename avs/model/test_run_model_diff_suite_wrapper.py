#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


RUNNER_PATH = Path(__file__).resolve().parents[2] / "tools/bringup/run_model_diff_suite.py"
SPEC = importlib.util.spec_from_file_location("root_model_diff_runner", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
root_model_diff_runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(root_model_diff_runner)


class ModelDiffWrapperTests(unittest.TestCase):
    def test_release_strict_rejects_alternate_suite_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qemu = root / "qemu-system-linx64"
            qemu.write_bytes(b"qemu")
            with mock.patch.object(root_model_diff_runner.subprocess, "run") as run:
                result = root_model_diff_runner.main(
                    [
                        "--root",
                        str(root),
                        "--suite",
                        "alternate.yaml",
                        "--qemu",
                        str(qemu),
                        "--profile",
                        "release-strict",
                        "--trace-schema-version",
                        "1.0",
                    ]
                )
        self.assertEqual(result, 2)
        run.assert_not_called()

    def test_release_strict_rejects_alternate_artifact_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            expected = Path(td) / "canonical"
            alternate = Path(td) / "alternate"
            with self.assertRaisesRegex(
                root_model_diff_runner.ReleaseStrictError, "non-canonical path"
            ):
                root_model_diff_runner._require_exact_path(
                    {"path": str(alternate)}, expected, "model"
                )

    def test_release_strict_rejects_component_commit_mismatch(self) -> None:
        root = Path(__file__).resolve().parents[2]
        component = root / "tools/model"
        _, tree = root_model_diff_runner._git_identity(component)
        with self.assertRaisesRegex(
            root_model_diff_runner.ReleaseStrictError, "commit/tree mismatch"
        ):
            root_model_diff_runner._validate_component_identity(
                {
                    "path": str(component),
                    "commit": "0" * 40,
                    "tree": tree,
                },
                component,
                "model",
            )

    def test_release_strict_rejects_qemu_marker_from_other_commit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qemu = root / "qemu-system-linx64"
            marker = root / ".linx_qemu_clean_head"
            qemu.write_bytes(b"qemu")
            marker.write_text(f"{'1' * 40}:worktree\n", encoding="utf-8")
            row = {
                "path": str(marker),
                "sha256": root_model_diff_runner.hashlib.sha256(
                    marker.read_bytes()
                ).hexdigest(),
            }
            with self.assertRaisesRegex(
                root_model_diff_runner.ReleaseStrictError,
                "does not match component commit",
            ):
                root_model_diff_runner._validate_qemu_source_marker(
                    row, qemu_path=qemu, expected_commit="2" * 40
                )

    def test_release_strict_rejects_incomplete_canonical_case_set(self) -> None:
        cases = [
            {"id": case_id}
            for case_id in list(root_model_diff_runner.CANONICAL_CASE_SOURCES)[:-1]
        ]
        with self.assertRaisesRegex(
            root_model_diff_runner.ReleaseStrictError, "canonical case set"
        ):
            root_model_diff_runner._validate_canonical_case_set(cases)

    def test_release_strict_suite_contains_all_canonical_cases(self) -> None:
        import yaml

        root = Path(__file__).resolve().parents[2]
        suite = yaml.safe_load(
            (root / "avs/model/linx_model_diff_suite.yaml").read_text(
                encoding="utf-8"
            )
        )
        selected = {
            case["id"]
            for case in suite["cases"]
            if "release-strict" in case["required_in_profile"]
        }
        self.assertEqual(
            selected,
            {
                "MODEL-SCALAR-COMMIT-SMOKE",
                "MODEL-SCALAR-MCOPY-MSET",
                "MODEL-VECTOR-LANE-CONTROL",
                "MODEL-TILE-DESCRIPTOR-LEGALITY",
                "MODEL-TILE-CONTROL-FLOW",
                "MODEL-PRIVILEGED-EXCEPTION-EDGE",
                "MODEL-RELEASE-RESULT-MEMORY",
            },
        )

    def test_tile_suite_uses_authoritative_tlsu_block_kind(self) -> None:
        import yaml

        root = Path(__file__).resolve().parents[2]
        engines = json.loads(
            (root / "isa/v0.58/state/engine_ops.json").read_text(encoding="utf-8")
        )
        tload = next(
            row
            for row in engines["tlsu"]["legal_aliases"]
            if row["mnemonic"] == "BSTART.TLOAD"
        )
        self.assertEqual(tload["engine"], "TLSU")

        suite = yaml.safe_load(
            (root / "avs/model/linx_model_diff_suite.yaml").read_text(
                encoding="utf-8"
            )
        )
        tile_cases = [
            case for case in suite["cases"] if case["category"].startswith("tile_")
        ]
        self.assertEqual(len(tile_cases), 2)
        for case in tile_cases:
            self.assertEqual(case["require_block_kind_any_of"], ["tlsu"])

    def test_explicit_qemu_path_is_forwarded_to_model_suite(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qemu = root / "exact-qemu-system-linx64"
            qemu.write_bytes(b"exact merged qemu")
            completed = subprocess.CompletedProcess(
                args=[], returncode=0, stdout='{"cases": []}\n'
            )
            with mock.patch.object(
                root_model_diff_runner.subprocess,
                "run",
                return_value=completed,
            ) as run:
                with redirect_stdout(io.StringIO()):
                    result = root_model_diff_runner.main(
                        [
                            "--root",
                            str(root),
                            "--qemu",
                            str(qemu),
                            "--profile",
                            "dev",
                        ]
                    )

        self.assertEqual(result, 0)
        command = run.call_args.args[0]
        qemu_index = command.index("--qemu")
        self.assertEqual(command[qemu_index + 1], str(qemu.resolve()))
        profile_index = command.index("--profile")
        self.assertEqual(command[profile_index + 1], "dev")


if __name__ == "__main__":
    unittest.main()
