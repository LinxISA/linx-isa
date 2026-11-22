#!/usr/bin/env python3
"""Check the opt-in v0.59.1 dispatch entry with pinned Sail."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
TOOLCHAIN = ROOT / "isa/sail/toolchain.json"
ACTIVE_SPEC = ROOT / "isa/v0.58/linxisa-v0.58.json"
V0591_SPEC = ROOT / "isa/v0.59/linxisa-v0.59.json"


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
        raise SystemExit("candidate dispatch Sail check failed: sail binary not found")
    version = run([sail, "--version"])
    if f"Sail {expected}" not in version:
        raise SystemExit(
            f"candidate dispatch Sail check failed: expected Sail {expected}, got {version.strip()!r}"
        )
    active = json.loads(ACTIVE_SPEC.read_text(encoding="utf-8"))
    prefix_overlaps = []
    for item in active["instructions"]:
        if int(item["length_bits"]) != 64:
            continue
        low_part = item["encoding"]["parts"][-1]
        mask = int(low_part["mask"], 0) & 0xFF
        match = int(low_part["match"], 0) & 0xFF
        if ((0x1F ^ match) & mask) == 0:
            prefix_overlaps.append(item["id"])
    if prefix_overlaps:
        raise SystemExit(
            "candidate dispatch Sail check failed: scoped prefix overlaps active "
            f"64-bit forms {prefix_overlaps}"
        )
    with tempfile.TemporaryDirectory(prefix="linx-sail-v0591-dispatch-") as directory:
        output = Path(directory)
        sail_tree = output / "sail"
        shutil.copytree(ROOT / "isa/sail", sail_tree)
        decode = sail_tree / "model/decode/decode.sail"
        run(
            [
                sys.executable,
                str(ROOT / "tools/isa/gen_sail_decode.py"),
                "--spec",
                str(V0591_SPEC),
                "--out",
                str(decode),
            ]
        )
        entry = sail_tree / "model/linxisa_v0591_candidate.sail"
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
                str(output / "linxisa_v0591_candidate"),
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
            raise RuntimeError("candidate dispatch directed tests did not complete")
    print(
        f"OK: assembled v0.59.1 catalog and scoped dispatch passed Sail {expected} "
        "parser, directed tests and C backend"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as error:
        raise SystemExit(f"candidate dispatch Sail check failed: {error}") from error
