#!/usr/bin/env python3
"""Export a self-contained Sail package for the canonical LinxISA v0.59 profile."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "isa/sail"
SPEC = ROOT / "isa/v0.59/linxisa-v0.59.json"
ENTRY_TEXT = """// Generated LinxISA v0.59.1 published specification entry.
// The package exporter replaces decode/decode.sail from the canonical catalog.

$include "linxisa.sail"
$include "execute/v0591_candidate_dispatch.sail"
"""
MANIFEST = "linxisa-v0591-sail-package.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def package_files(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name not in {MANIFEST, "SHA256SUMS"}
    }


def run_generator(output: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/isa/gen_sail_decode.py"),
            "--spec",
            str(SPEC),
            "--out",
            str(output / "model/decode/decode.sail"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(result.stderr or result.stdout or "Sail decoder generation failed")


def export(output: Path) -> dict:
    if output.exists():
        raise ValueError(f"output already exists: {output}")
    shutil.copytree(SOURCE, output)
    run_generator(output)
    entry = output / "model/linxisa_v0591.sail"
    entry.write_text(ENTRY_TEXT, encoding="utf-8")
    files = package_files(output)
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    package = {
        "schema": "linxisa.sail-package.v1",
        "profile": "v0.59",
        "version": "0.59.1",
        "state": "published-specification",
        "entry": "model/linxisa_v0591.sail",
        "catalog": {
            "path": "isa/v0.59/linxisa-v0.59.json",
            "sha256": sha256(SPEC),
            "instruction_count": spec["instruction_count"],
        },
        "toolchain": json.loads(
            (ROOT / "isa/sail/toolchain.json").read_text(encoding="utf-8")
        ),
        "files": files,
        "files_sha256": canonical_sha256(files),
    }
    (output / MANIFEST).write_text(
        json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output / "SHA256SUMS").write_text(
        "\n".join(f"{digest}  {path}" for path, digest in files.items()) + "\n",
        encoding="utf-8",
    )
    return package


def check(output: Path) -> None:
    package_path = output / MANIFEST
    package = json.loads(package_path.read_text(encoding="utf-8"))
    if package.get("schema") != "linxisa.sail-package.v1":
        raise ValueError("Sail package has the wrong schema")
    if package.get("entry") != "model/linxisa_v0591.sail":
        raise ValueError("Sail package has the wrong canonical entry")
    if (output / package["entry"]).read_text(encoding="utf-8") != ENTRY_TEXT:
        raise ValueError("Sail package entry is stale")
    files = package_files(output)
    if package.get("files") != files or package.get("files_sha256") != canonical_sha256(files):
        raise ValueError("Sail package file hashes are stale")
    expected_sums = (
        "\n".join(f"{digest}  {path}" for path, digest in files.items()) + "\n"
    )
    if (output / "SHA256SUMS").read_text(encoding="utf-8") != expected_sums:
        raise ValueError("Sail package checksums are stale")
    with tempfile.TemporaryDirectory(prefix="linx-sail-v0591-export-check-") as directory:
        expected = Path(directory) / "sail"
        export(expected)
        expected_files = package_files(expected)
    if files != expected_files:
        raise ValueError("Sail package differs from a fresh export")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        if args.output is not None:
            package = export(args.output.resolve())
            print(json.dumps({"output": str(args.output.resolve()), **package}, sort_keys=True))
        else:
            check(args.check.resolve())
            print(f"LinxISA v0.59.1 Sail package is current: {args.check.resolve()}")
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"v0.59.1 Sail export failed: {error}") from error
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
