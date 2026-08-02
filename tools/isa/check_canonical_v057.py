#!/usr/bin/env python3
"""Validate the standalone, legacy-free LinxISA v0.57 release."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGACY_PATTERNS = [
    ("legacy B.IOD descriptor", re.compile(r"\bB\.IOD\b")),
    ("legacy BSTART.PAR mnemonic", re.compile(r"\bBSTART\.PAR\b")),
]
TEXTUAL_TMA = re.compile(r"\bBSTART\.TMA(?=\s|[\"'])")
RETIRED_COMPILER_SYMBOLS = (
    "parseTMAFunctionKeyword",
    "IsBStartTMA",
    "IsTypedTMA",
)
ACTIVE_TEXT_SUFFIXES = {
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".inc",
    ".ll",
    ".md",
    ".py",
    ".s",
    ".S",
    ".td",
}


def _load_spec(root: Path) -> dict:
    return json.loads((root / "isa/v0.57/linxisa-v0.57.json").read_text(encoding="utf-8"))


def _scan_active_legacy_surfaces(root: Path) -> list[str]:
    """Reject production-facing generic TMA syntax without scanning history/tests."""
    errors: list[str] = []
    scan_roots = (
        root / "docs/isa/blockIntro",
        root / "docs/isa/header/tileblock",
        root / "docs/zh/isa/blockIntro",
        root / "docs/zh/isa/header/tileblock",
        root / "compiler/llvm/llvm/lib/Target/Linx",
        root / "compiler/ptoas",
        root / "workloads/SuperNPUBench",
        root / "workloads/pto_kernels",
    )
    excluded_parts = {
        "archive",
        "test",
        "tests",
        "unittests",
        "negative",
        "reject",
    }
    for scan_root in scan_roots:
        if not scan_root.is_dir():
            continue
        for path in scan_root.rglob("*"):
            if (
                not path.is_file()
                or path.suffix not in ACTIVE_TEXT_SUFFIXES
                or excluded_parts.intersection(part.lower() for part in path.parts)
            ):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(text.splitlines(), start=1):
                if TEXTUAL_TMA.search(line):
                    errors.append(
                        f"{path}:{lineno}: generic BSTART.TMA textual form is retired"
                    )
                for symbol in RETIRED_COMPILER_SYMBOLS:
                    if symbol in line:
                        errors.append(
                            f"{path}:{lineno}: retired compiler TMA helper remains: {symbol}"
                        )
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    spec_path = root / "isa/v0.57/linxisa-v0.57.json"
    if not spec_path.is_file():
        return [f"missing v0.57 compiled spec: {spec_path}"]
    spec = _load_spec(root)
    if spec.get("version") != "0.57.1":
        errors.append(f"{spec_path}: expected version 0.57.1, got {spec.get('version')!r}")

    mnemonics = {str(inst.get("mnemonic") or "") for inst in spec.get("instructions", [])}
    required = {
        "BSTART.TLOAD",
        "BSTART.TSTORE",
        "BSTART.TMOV",
        "BSTART.TPREFETCH",
        "BSTART.MGATHER",
        "BSTART.MSCATTER",
        "BSTART.MGATHER.MASK",
        "BSTART.MSCATTER.MASK",
        "BSTART.MGATHER.CAS",
        "BSTART.TMATMUL.BIAS",
        "BSTART.TMATMULMX",
        "BSTART.TMATMULMX.BIAS",
        "BSTART.TMATMULMX.ACC",
        "BSTART.TGEMV",
        "BSTART.TGEMV.BIAS",
        "BSTART.TGEMV.ACC",
        "BSTART.TGEMVMX",
        "BSTART.TGEMVMX.BIAS",
        "BSTART.TGEMVMX.ACC",
        "CASB",
        "CASH",
        "CASW",
        "CASD",
        "DMA",
    }
    for name in sorted(required - mnemonics):
        errors.append(f"{spec_path}: required v0.57 mnemonic missing: {name}")
    for name in ["B.IOD", "BSTART.PAR", "BSTART.TMA"]:
        if name in mnemonics:
            errors.append(f"{spec_path}: legacy/non-textual mnemonic must not decode: {name}")

    release_manifest = root / "isa/v0.57/release_manifest.json"
    if not release_manifest.is_file():
        errors.append(f"missing v0.57 release manifest: {release_manifest}")
    else:
        manifest = json.loads(release_manifest.read_text(encoding="utf-8"))
        if manifest.get("profile") != "v0.57" or manifest.get("version") != "0.57.1":
            errors.append(f"{release_manifest}: expected standalone v0.57.1 release identity")
        if not manifest.get("policy", {}).get("pto_spec_is_sole_source"):
            errors.append(f"{release_manifest}: pto_spec_is_sole_source policy is required")

    retired_profile = root / "isa/v0.56"
    if retired_profile.exists():
        errors.append(f"retired active profile must be removed: {retired_profile}")

    source_files = [
        root / "isa/v0.57/opcodes/lx_32.opc",
        root / "isa/v0.57/state/engine_ops.json",
        root / "isa/v0.57/meta.json",
        release_manifest,
    ]
    for path in source_files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in LEGACY_PATTERNS:
            for lineno, line in enumerate(text.splitlines(), start=1):
                if "remains" in line or "non-textual" in line or "reserved" in line:
                    continue
                if pattern.search(line):
                    errors.append(f"{path}:{lineno}: {label}: {line.strip()!r}")

    sys.path.insert(0, str(root / "tools/isa"))
    import check_pto_v057_manifest  # type: ignore

    errors.extend(check_pto_v057_manifest.validate(root))
    errors.extend(_scan_active_legacy_surfaces(root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    errors = validate(args.root.resolve())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
