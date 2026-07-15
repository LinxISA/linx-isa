#!/usr/bin/env python3
"""Atomically record a complete C-CodeGen run for coverage consumers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path


SCHEMA_VERSION = "linx-c-codegen-build-v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.absolute().relative_to(root.absolute()))
    except ValueError:
        return str(path.absolute())


def _identity(tool: Path) -> str:
    return subprocess.run(
        [str(tool), "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]


def _record(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).absolute()
    paths = {
        "source": Path(args.source).absolute(),
        "generated_assembly": Path(args.generated_assembly).absolute(),
        "object": Path(args.object).absolute(),
        "objdump": Path(args.objdump).absolute(),
    }
    for label, path in paths.items():
        if not path.is_file():
            raise SystemExit(f"error: missing {label}: {path}")
    record = {label: _rel(path, root) for label, path in paths.items()}
    record.update({f"{label}_sha256": _sha256(path) for label, path in paths.items()})
    record["compile_flags"] = args.compile_flag
    with Path(args.records_jsonl).open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
    return 0


def _complete(args: argparse.Namespace) -> int:
    root = Path(args.repo_root).absolute()
    source_dir = Path(args.source_dir).absolute()
    records_path = Path(args.records_jsonl)
    output = Path(args.output).absolute()
    records = [json.loads(line) for line in records_path.read_text().splitlines() if line]
    sources = sorted(_rel(path, root) for path in source_dir.glob("*.c"))
    recorded_sources = [record["source"] for record in records]
    if len(recorded_sources) != len(set(recorded_sources)):
        raise SystemExit("error: duplicate source records prevent a complete manifest")
    if sorted(recorded_sources) != sources:
        raise SystemExit("error: recorded source set is not the complete current C source set")

    clang = Path(args.clang).absolute()
    objdump = Path(args.llvm_objdump).absolute()
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "complete",
        "target": args.target,
        "extra_cflags": args.extra_flag,
        "source_count": len(records),
        "tools": {
            "clang": {
                "path": _rel(clang, root),
                "sha256": _sha256(clang),
                "identity": _identity(clang),
            },
            "llvm_objdump": {
                "path": _rel(objdump, root),
                "sha256": _sha256(objdump),
                "identity": _identity(objdump),
            },
        },
        "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, output)
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    record = subparsers.add_parser("record")
    record.add_argument("--repo-root", required=True)
    record.add_argument("--records-jsonl", required=True)
    record.add_argument("--source", required=True)
    record.add_argument("--generated-assembly", required=True)
    record.add_argument("--object", required=True)
    record.add_argument("--objdump", required=True)
    record.add_argument("--compile-flag", action="append", default=[])

    complete = subparsers.add_parser("complete")
    complete.add_argument("--repo-root", required=True)
    complete.add_argument("--records-jsonl", required=True)
    complete.add_argument("--source-dir", required=True)
    complete.add_argument("--target", required=True)
    complete.add_argument("--clang", required=True)
    complete.add_argument("--llvm-objdump", required=True)
    complete.add_argument("--output", required=True)
    complete.add_argument("--extra-flag", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    return _record(args) if args.command == "record" else _complete(args)


if __name__ == "__main__":
    raise SystemExit(main())
