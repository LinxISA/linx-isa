#!/usr/bin/env python3
"""
Fail when archived v0.3 or pre-canonical draft content leaks into active v0.4 surfaces,
and when the live v0.4 TEPL selector catalogs drift or become non-injective.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, DefaultDict, Iterable, List, Pattern, Sequence, Tuple


ALLOWED_EXTS = {
    ".adoc",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".json",
    ".md",
    ".opc",
    ".py",
    ".S",
    ".s",
    ".sh",
    ".yaml",
    ".yml",
    ".decode",
    ".txt",
    ".ll",
    ".mir",
}


def _local_targets(root: Path) -> List[Path]:
    return [
        root / "AGENTS.md",
        root / "README.md",
        root / "mkdocs.yml",
        root / "isa" / "README.md",
        root / "isa" / "generated" / "codecs" / "README.md",
        root / "isa" / "sail" / "README.md",
        root / "isa" / "v0.4",
        root / "docs" / "index.md",
        root / "docs" / "architecture" / "README.md",
        root / "docs" / "architecture" / "v0.4-architecture-contract.md",
        root / "docs" / "architecture" / "isa-manual" / "src",
        root / "docs" / "architecture" / "linxcore",
        root / "docs" / "bringup" / "README.md",
        root / "docs" / "bringup" / "GETTING_STARTED.md",
        root / "docs" / "bringup" / "PROGRESS.md",
        root / "docs" / "bringup" / "ALIGNMENT_MATRIX.md",
        root / "docs" / "bringup" / "CHECK26_CONTRACT.md",
        root / "docs" / "bringup" / "check26_contract.yaml",
        root / "docs" / "bringup" / "agent_runs" / "checklists",
        root / "docs" / "bringup" / "gates" / "qemu_isa_coverage_latest.json",
        root / "docs" / "bringup" / "gates" / "qemu_isa_coverage_latest.md",
        root / "docs" / "project" / "README.md",
        root / "docs" / "reference" / "README.md",
        root / "docs" / "reference" / "examples" / "README.md",
        root / "docs" / "reference" / "examples" / "v0.4",
        root / "docs" / "releases" / "v0.4.0.md",
        root / "tools" / "analysis",
        root / "tools" / "isa",
        root / "tools" / "regression" / "run.sh",
        root / "avs" / "compiler" / "linx-llvm" / "tests",
    ]


def _should_skip(path: Path) -> bool:
    p = str(path)
    if any(
        token in p
        for token in (
            "/isa/v0.3/",
            "/docs/architecture/v0.4-draft/",
            "/docs/architecture/research/",
            "/docs/reference/examples/v0.3/",
            "/docs/bringup/plan/",
            "/docs/releases/v0.3.0.md",
            "/avs/compiler/linx-llvm/tests/out/",
            "/avs/compiler/linx-llvm/tests/out-linx32/",
            "/avs/compiler/linx-llvm/tests/out-linx64/",
        )
    ):
        return True
    if path.name in {
        "check_no_legacy_v02.py",
        "check_no_legacy_v03.py",
        "check_canonical_v04.py",
        "normalize_v03_example_asm.py",
        "reconcile_v03_raw.py",
    }:
        return True
    return False


def _iter_files(targets: Sequence[Path]) -> Iterable[Path]:
    for t in targets:
        if t.is_file():
            if t.suffix in ALLOWED_EXTS and not _should_skip(t):
                yield t
            continue
        if not t.exists():
            continue
        for p in t.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix in ALLOWED_EXTS and not _should_skip(p):
                yield p


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return path.read_text(encoding="latin-1", errors="replace")


def _parse_selector(raw: Any, *, path: Path, field: str) -> int:
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str):
        try:
            return int(raw.strip(), 0)
        except ValueError as exc:
            raise ValueError(f"{path}: invalid {field} value {raw!r}") from exc
    raise ValueError(f"{path}: invalid {field} value {raw!r}")


def _selector_value(op: dict[str, Any], *, fields: Sequence[str]) -> Tuple[Any, str]:
    for field in fields:
        if field in op:
            return op.get(field), field
    return None, fields[0]


def _collect_selector_pairs(path: Path, ops: Any, *, fields: Sequence[str]) -> Tuple[List[Tuple[int, str]], List[str]]:
    failures: List[str] = []
    pairs: List[Tuple[int, str]] = []
    if not isinstance(ops, list):
        return [], [f"{path}: expected ops list"]
    for idx, op in enumerate(ops):
        if not isinstance(op, dict):
            failures.append(f"{path}: ops[{idx}] must be an object")
            continue
        name = op.get("name")
        if not isinstance(name, str) or not name.strip():
            failures.append(f"{path}: ops[{idx}] missing non-empty name")
            continue
        raw_selector, field = _selector_value(op, fields=fields)
        try:
            selector = _parse_selector(raw_selector, path=path, field=field)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        if not 0 <= selector <= 0x3FF:
            failures.append(f"{path}: ops[{idx}] {field}={selector} out of tile opcode range 0..1023")
            continue
        pairs.append((selector, name.strip()))
    return pairs, failures


def _check_duplicate_selectors(path: Path, pairs: Sequence[Tuple[int, str]], *, label: str) -> List[str]:
    failures: List[str] = []
    names_by_selector: DefaultDict[int, List[str]] = defaultdict(list)
    for selector, name in pairs:
        names_by_selector[selector].append(name)
    for selector, names in sorted(names_by_selector.items()):
        unique_names = sorted(set(names))
        if len(unique_names) > 1:
            rendered = ", ".join(unique_names)
            failures.append(f"{path}: duplicate {label} 0x{selector:03X} shared by {rendered}")
    return failures


def _expected_tepl_pairs_from_packing(path: Path, tepl: Any) -> Tuple[List[Tuple[int, str]], List[str]]:
    failures: List[str] = []
    if not isinstance(tepl, dict):
        return [], [f"{path}: expected top-level tepl object"]

    packing = tepl.get("packing")
    if packing is None:
        return [], []
    if not isinstance(packing, dict):
        return [], [f"{path}: tepl.packing must be an object"]

    if packing.get("kind") != "mode_function_u6":
        failures.append(f"{path}: tepl.packing.kind must be mode_function_u6")
    if packing.get("reserved_high_bits_zero") is not True:
        failures.append(f"{path}: tepl.packing.reserved_high_bits_zero must be true")
    if packing.get("mode_field_bits") != [5, 5]:
        failures.append(f"{path}: tepl.packing.mode_field_bits must be [5, 5]")
    if packing.get("function_field_bits") != [0, 4]:
        failures.append(f"{path}: tepl.packing.function_field_bits must be [0, 4]")

    modes = packing.get("modes")
    if not isinstance(modes, list):
        return [], failures + [f"{path}: tepl.packing.modes must be a list"]

    expected: List[Tuple[int, str]] = []
    seen_names: dict[str, int] = {}
    for idx, mode_entry in enumerate(modes):
        ctx = f"{path}: tepl.packing.modes[{idx}]"
        if not isinstance(mode_entry, dict):
            failures.append(f"{ctx} must be an object")
            continue

        mode = mode_entry.get("mode")
        if not isinstance(mode, int) or not 0 <= mode <= 1:
            failures.append(f"{ctx}.mode must be an integer in range 0..1")
            continue

        function_names = mode_entry.get("function_names")
        if not isinstance(function_names, list):
            failures.append(f"{ctx}.function_names must be a list")
            continue
        if len(function_names) > 32:
            failures.append(f"{ctx}.function_names must not exceed 32 entries")
            continue

        for function, raw_name in enumerate(function_names):
            if not isinstance(raw_name, str) or not raw_name.strip():
                failures.append(f"{ctx}.function_names[{function}] must be a non-empty string")
                continue
            name = raw_name.strip()
            selector = (mode << 5) | function
            prev = seen_names.get(name)
            if prev is not None and prev != selector:
                failures.append(f"{ctx}: {name} assigned to both 0x{prev:03X} and 0x{selector:03X}")
                continue
            seen_names[name] = selector
            expected.append((selector, name))

        reserved = mode_entry.get("reserved_function_range")
        if reserved is not None:
            if (
                not isinstance(reserved, list)
                or len(reserved) != 2
                or not all(isinstance(v, int) for v in reserved)
                or not 0 <= reserved[0] <= reserved[1] <= 31
            ):
                failures.append(f"{ctx}.reserved_function_range must be [lo, hi] within 0..31")

    return expected, failures


def _check_tepl_catalog_alignment(root: Path) -> List[str]:
    failures: List[str] = []
    engine_path = root / "isa" / "v0.4" / "state" / "engine_ops.json"
    status_path = root / "docs" / "bringup" / "tepl_status.yaml"

    try:
        engine = json.loads(engine_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{engine_path}: failed to load JSON: {exc}"]

    tepl = engine.get("tepl")
    if not isinstance(tepl, dict):
        return [f"{engine_path}: expected top-level tepl object"]
    engine_pairs, engine_failures = _collect_selector_pairs(engine_path, tepl.get("ops"), fields=("tile_opcode",))
    failures.extend(engine_failures)
    failures.extend(_check_duplicate_selectors(engine_path, engine_pairs, label="tile opcode"))

    expected_pairs, packing_failures = _expected_tepl_pairs_from_packing(engine_path, tepl)
    failures.extend(packing_failures)
    if expected_pairs:
        engine_counter = Counter(engine_pairs)
        expected_counter = Counter(expected_pairs)
        for selector, name in sorted((expected_counter - engine_counter).elements()):
            failures.append(
                f"{engine_path}: missing packed TEPL assignment 0x{selector:03X} ({name}) declared by tepl.packing"
            )
        for selector, name in sorted((engine_counter - expected_counter).elements()):
            failures.append(
                f"{engine_path}: extra TEPL assignment 0x{selector:03X} ({name}) not described by tepl.packing"
            )
        for selector, name in sorted(engine_pairs):
            if selector > 0x03F:
                failures.append(
                    f"{engine_path}: {name} uses reserved high tile-opcode bits outside packed v0.4 profile (0x{selector:03X})"
                )

    try:
        import yaml  # type: ignore
    except Exception as exc:
        failures.append(f"{status_path}: PyYAML required to validate TEPL status alignment: {exc}")
        return failures

    try:
        status = yaml.safe_load(status_path.read_text(encoding="utf-8"))
    except Exception as exc:
        failures.append(f"{status_path}: failed to load YAML: {exc}")
        return failures

    if not isinstance(status, dict):
        failures.append(f"{status_path}: expected top-level mapping")
        return failures

    status_pairs, status_failures = _collect_selector_pairs(status_path, status.get("ops"), fields=("tile_opcode",))
    failures.extend(status_failures)
    failures.extend(_check_duplicate_selectors(status_path, status_pairs, label="tile opcode"))

    engine_counter = Counter(engine_pairs)
    status_counter = Counter(status_pairs)
    for selector, name in sorted((engine_counter - status_counter).elements()):
        failures.append(
            f"{status_path}: missing TEPL status entry for tile opcode 0x{selector:03X} ({name}) present in engine_ops.json"
        )
    for selector, name in sorted((status_counter - engine_counter).elements()):
        failures.append(
            f"{status_path}: extra TEPL status entry for tile opcode 0x{selector:03X} ({name}) not present in engine_ops.json"
        )
    return failures


def _scan_root(root: Path, targets: Sequence[Path], checks: Sequence[Tuple[str, Pattern[str]]]) -> List[str]:
    failures: List[str] = []
    for path in sorted(set(_iter_files(targets))):
        text = _read_text(path)
        rel = path.relative_to(root)
        for label, pat in checks:
            if rel == Path("AGENTS.md") and label == "forbidden legacy repo path":
                continue
            if (
                rel.parts[:4] == ("docs", "bringup", "agent_runs", "checklists")
                and label == "unresolved normative marker"
            ):
                continue
            for m in pat.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                failures.append(f"{rel}:{line}: {label}: {m.group(0)!r}")
                if len([f for f in failures if f.startswith(f"{rel}:")]) > 20:
                    break
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Repo root")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    checks: List[Tuple[str, Pattern[str]]] = [
        (
            "archived v0.3 canonical reference",
            re.compile(r"(?:isa/v0\.3/|linxisa-v0\.3|docs/architecture/v0\.3-architecture-contract\.md|docs/reference/examples/v0\.3/)"),
        ),
        (
            "pre-canonical draft citation",
            re.compile(r"docs/architecture/v0\.4-draft/"),
        ),
        (
            "obsolete manual chapter path",
            re.compile(r"(?:02_programming_model\.adoc|04_encoding_and_formats\.adoc|05_block_isa\.adoc|08_memory_operations\.adoc|09_system_and_privilege\.adoc)"),
        ),
        (
            "forbidden legacy repo path",
            re.compile(r"(?:examples/assembly/|docs/validation/avs/|\bspec/|/spec/)"),
        ),
        (
            "unresolved normative marker",
            re.compile(r"\b(?:TBD|TODO|defer|deferred|unresolved)\b"),
        ),
    ]

    failures = _scan_root(root, _local_targets(root), checks)
    failures.extend(_check_tepl_catalog_alignment(root))
    if failures:
        for failure in failures[:200]:
            print(failure, file=sys.stderr)
        if len(failures) > 200:
            print(f"... {len(failures) - 200} more", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
