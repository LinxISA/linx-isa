#!/usr/bin/env python3
"""Check the LinxISA v0.59.2 catalog with the pinned compatible Sail model."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from export_linxisa_v0592_sail import check as check_export
from export_linxisa_v0592_sail import export as export_sail


ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN = ROOT / "isa/sail/toolchain.json"


def run(command: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        command,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode:
        raise RuntimeError(f"{' '.join(command)} failed:\n{output}")
    return output


def main() -> int:
    expected = str(json.loads(TOOLCHAIN.read_text(encoding="utf-8"))["sail_version"])
    sail = shutil.which("sail")
    if sail is None:
        raise SystemExit("v0.59.2 Sail check failed: sail binary not found")
    version = run([sail, "--version"])
    if f"Sail {expected}" not in version:
        raise SystemExit(
            f"v0.59.2 Sail check failed: expected Sail {expected}, got {version.strip()!r}"
        )
    with tempfile.TemporaryDirectory(prefix="linx-sail-v0592-") as directory:
        output = Path(directory)
        sail_tree = output / "sail"
        export_sail(sail_tree)
        check_export(sail_tree)
        entry = sail_tree / "model/linxisa_v0592.sail"
        directed_path = sail_tree / "tests/v0591_candidate_dispatch_tests.sail"
        memo = output / "z3-memo"
        run([sail, "--memo-z3-path", str(memo), "--just-check", str(entry)])
        run(
            [
                sail,
                "--memo-z3-path",
                str(memo),
                "-c",
                "-o",
                str(output / "linxisa_v0592"),
                str(entry),
            ]
        )
        directed = run(
            [
                sail,
                "--memo-z3-path",
                str(memo),
                "--no-color",
                "--no-warn",
                "-i",
                str(directed_path),
            ],
            input_text="main()\n:run\n",
        )
        if "Result = ()" not in directed:
            raise RuntimeError("v0.59.1-compatible directed tests did not complete")
    print(
        f"OK: LinxISA v0.59.2 passed Sail {expected} parser, C backend and "
        "v0.59.1-compatible directed execution tests"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        raise SystemExit(f"v0.59.2 Sail check failed: {error}") from error
