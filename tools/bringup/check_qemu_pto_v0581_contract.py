#!/usr/bin/env python3
"""Fail-closed release checker for the QEMU PTO ISA 0.58.1 contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


EXPECTED_ENGINES = {"VEC": 31, "SFU": 56, "TLSU": 10, "CUBE": 12}
EXPECTED_NUMERIC_SHA256 = "59c96cc2f45f8e8f3eebb8230338b21ec3a77a99e8fb5e1c7c7b391819a6aa81"
FIELD_BITS = {
    "Sat": 0x01,
    "Canonicalize": 0x02,
    "DataType": 0x04,
    "RMode": 0x08,
    "Layout": 0x10,
    "PadValueOrByteId": 0x20,
    "CMode": 0x40,
}


@dataclass(frozen=True)
class CheckResult:
    errors: list[str]
    mnemonics: int
    forms: int
    engine_counts: dict[str, int]
    operation_count: int
    numeric_vector_count: int


def validate_catalog(catalog: dict[str, object]) -> None:
    if catalog.get("version") != "0.58.1":
        raise ValueError("catalog release/version must be 0.58.1")
    instructions = catalog.get("instructions")
    if not isinstance(instructions, list) or len(instructions) != 765:
        raise ValueError("catalog must contain exactly 765 forms")
    if len({str(item.get("mnemonic")) for item in instructions}) != 731:
        raise ValueError("catalog must contain exactly 731 mnemonics")


def validate_elf_loader_order(source: str) -> None:
    loader = source.find("static bool linx_load_elf(")
    if loader < 0:
        raise ValueError("linx_load_elf is missing")
    body = source[loader : source.find("\n}\n", loader) + 3]
    validation = body.find("linx_validate_pto_isa_identity(buf, len, errp)")
    if validation < 0:
        raise ValueError("ELF identity validation is missing")
    first_mutating_loader = min(
        pos for name in ("linx_load_elf32_rel(", "linx_load_elf32_exec(",
                         "linx_load_elf64_rel(", "linx_load_elf64_exec(")
        if (pos := body.find(name)) >= 0
    )
    if validation > first_mutating_loader:
        raise ValueError("ELF identity validation occurs after loader mutation")
    required = (
        '"release\\\":\\\"0.58.1\\\"}"',
        "identity_count == 0",
        "namesz != 4",
        "descsz != sizeof(linx_pto_isa_identity) - 1",
    )
    missing = [marker for marker in required if marker not in source]
    if missing:
        raise ValueError(f"ELF fail-closed markers missing: {missing}")


def _array(text: str, function: str, size: int) -> list[int]:
    match = re.search(
        rf"{re.escape(function)}.*?allowed\[{size}\]\s*=\s*\{{(.*?)\}};",
        text,
        re.S,
    )
    if not match:
        raise ValueError(f"missing {function} DATR table")
    values = [int(item, 16) for item in re.findall(r"0x([0-9a-fA-F]+)", match.group(1))]
    if len(values) != size:
        raise ValueError(f"{function} DATR table has {len(values)} entries, expected {size}")
    return values


def _expected_datr(operations: list[dict[str, object]], family: str, size: int) -> list[int]:
    out = [0] * size
    for operation in operations:
        if operation.get("family") != family:
            continue
        selector = int(str(operation["selector"]), 0) if family == "TEPL" else int(operation["function"])
        fields = operation.get("datr_contract", {}).get("allowed_nonzero_fields", [])
        out[selector] = sum(FIELD_BITS[str(field)] for field in fields)
    return out


def check_contract(root: Path) -> CheckResult:
    errors: list[str] = []
    catalog = json.loads((root / "isa/v0.58/linxisa-v0.58.json").read_text())
    try:
        validate_catalog(catalog)
    except ValueError as exc:
        errors.append(str(exc))
    instructions = catalog.get("instructions", [])
    forms = len(instructions)
    mnemonics = len({str(item.get("mnemonic")) for item in instructions})

    state = json.loads((root / "isa/v0.58/state/pto_ops.json").read_text())
    engine_counts = state.get("engine_counts", {})
    operation_count = state.get("operation_count", -1)
    if engine_counts != EXPECTED_ENGINES:
        errors.append(f"engine counts mismatch: {engine_counts}")
    if operation_count != 109 or len(state.get("operations", [])) != 109:
        errors.append("PTO operation catalog must contain exactly 109 direct operations")

    qemu_table = (root / "emulator/qemu/target/linx/tile_isa_058.h").read_text()
    operations = state.get("operations", [])
    for function, family, size in (
        ("linx_tile_operation_datr_allowed", "TEPL", 128),
        ("linx_tile_tlsu_datr_allowed", "TLSU", 32),
        ("linx_tile_cube_datr_allowed", "CUBE", 32),
    ):
        try:
            if _array(qemu_table, function, size) != _expected_datr(operations, family, size):
                errors.append(f"{function} does not match canonical DATR contracts")
        except ValueError as exc:
            errors.append(str(exc))

    numeric = root / "emulator/qemu/tests/linxisa/pto-isa-0581-hardware-numeric-vectors.json"
    numeric_bytes = numeric.read_bytes()
    numeric_obj = json.loads(numeric_bytes)
    numeric_vector_count = sum(
        len(group) for group in numeric_obj.get("vector_groups", {}).values()
    )
    if hashlib.sha256(numeric_bytes).hexdigest() != EXPECTED_NUMERIC_SHA256:
        errors.append("official numeric vector SHA-256 mismatch")
    if numeric_vector_count != 104:
        errors.append(f"numeric vector count is {numeric_vector_count}, expected 104")

    virt = (root / "emulator/qemu/hw/linx/virt.c").read_text()
    try:
        validate_elf_loader_order(virt)
    except ValueError as exc:
        errors.append(str(exc))

    insn16 = (root / "emulator/qemu/target/linx/insn16.decode").read_text()
    for retired in ("c_bstart_std_direct", "c_bstart_std_cond", "c_bstart_std_call",
                    "c_bstart_std_icall"):
        if re.search(rf"(?m)^{retired}\s", insn16):
            errors.append(f"retired decode form remains accepted: {retired}")

    with tempfile.TemporaryDirectory(prefix="qemu-v0581-check-") as tmp:
        report = Path(tmp) / "coverage.json"
        proc = subprocess.run(
            ["python3", str(root / "tools/bringup/report_qemu_isa_coverage.py"),
             "--spec", str(root / "isa/v0.58/linxisa-v0.58.json"),
             "--qemu-root", str(root / "emulator/qemu"),
             "--qemu-meta", str(root / "emulator/qemu/target/linx/linx_opcode_meta_gen.h"),
             "--report-out", str(report), "--out-md", str(Path(tmp) / "coverage.md"),
             "--require-full"],
            cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        if proc.returncode:
            errors.append(f"exact coverage gate failed: {proc.stdout.strip()}")

    return CheckResult(errors, mnemonics, forms, dict(engine_counts), operation_count,
                       numeric_vector_count)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = check_contract(Path(args.root).resolve())
    if result.errors:
        for error in result.errors:
            print(f"error: {error}")
        return 1
    print(f"ok: PTO ISA 0.58.1 QEMU contract ({result.mnemonics}/731 mnemonics, "
          f"{result.forms}/765 forms, {result.operation_count} operations, "
          f"{result.numeric_vector_count} numeric vectors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
