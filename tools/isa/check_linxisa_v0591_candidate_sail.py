#!/usr/bin/env python3
"""Run the pinned Sail parser and C backend on the inactive v0.59.1 catalog."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "isa/v0.59/linxisa-v0.59-candidate.json"
TOOLCHAIN = ROOT / "isa/sail/toolchain.json"


def run(command: list[str], *, cwd: Path | None = None) -> None:
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr or result.stdout or "unknown failure"
        raise RuntimeError(f"{' '.join(command)} failed:\n{detail}")


def main() -> int:
    expected = str(json.loads(TOOLCHAIN.read_text(encoding="utf-8"))["sail_version"])
    sail = shutil.which("sail")
    if sail is None:
        raise SystemExit("candidate Sail check failed: sail binary not found")
    version = subprocess.run(
        [sail, "--version"], capture_output=True, text=True, check=False
    )
    version_text = version.stdout or version.stderr
    if version.returncode or f"Sail {expected}" not in version_text:
        raise SystemExit(
            f"candidate Sail check failed: expected Sail {expected}, got {version_text.strip()!r}"
        )

    with tempfile.TemporaryDirectory(prefix="linx-sail-v0591-candidate-") as directory:
        output = Path(directory)
        sail_tree = output / "sail"
        shutil.copytree(ROOT / "isa/sail", sail_tree)
        decode = sail_tree / "model/decode/decode.sail"
        run(
            [
                sys.executable,
                str(ROOT / "tools/isa/gen_sail_decode.py"),
                "--spec",
                str(SPEC),
                "--out",
                str(decode),
            ],
            cwd=ROOT,
        )
        entry = sail_tree / "model/linxisa.sail"
        memo = output / "z3-memo"
        run([sail, "--memo-z3-path", str(memo), "--just-check", str(entry)])
        run(
            [
                sail,
                "--memo-z3-path",
                str(memo),
                "-c",
                "-o",
                str(output / "linxisa"),
                str(entry),
            ]
        )
    print(f"OK: inactive v0.59.1 catalog passed Sail {expected} parser and C backend")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        raise SystemExit(f"candidate Sail check failed: {error}") from error
