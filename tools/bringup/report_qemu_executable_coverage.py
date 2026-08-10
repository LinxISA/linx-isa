#!/usr/bin/env python3
"""Build a machine-readable ledger of per-form QEMU execution evidence.

L1 decoder/source mapping is deliberately out of scope.  A form enters L2/L3
only when the manifest binds a golden form, concrete bytes in an object, a
runtime test ID, a test-specific terminal PASS from a matching QEMU revision, and a source
oracle.  Failed executions remain first-class observations but never inflate
coverage counts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
AVAILABILITY_VALUES = {"available", "unavailable"}
L3_ORACLE_KINDS = {"exact_value", "architectural_state", "expected_trap", "differential"}
UART_SUCCESS_MARKERS = {
    "TEST SUITE COMPLETE",
    "LINX TESTS PASS",
    "REGRESSION PASSED",
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
HEX_RE = re.compile(r"0x[0-9a-fA-F]+")
CANONICAL_EVIDENCE_ROOT = Path("docs/bringup/gates/evidence/qemu-executable")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def _repo_path(repo_root: Path, value: object, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"missing {field}")
    relative = Path(value)
    if relative.is_absolute():
        raise ValueError(f"{field} must be repository-relative")
    resolved = (repo_root / relative).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"{field} escapes repository root") from exc
    return resolved


def _parse_int(value: object, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"invalid {field}")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value, 0)
        except ValueError as exc:
            raise ValueError(f"invalid {field}") from exc
    raise ValueError(f"missing {field}")


def _test_id(value: object) -> str:
    parsed = _parse_int(value, "test_id")
    if parsed < 0 or parsed > 0xFFFFFFFF:
        raise ValueError("test_id must fit uint32")
    return f"0x{parsed:08x}"


def _canonical_sha(value: object, field: str) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value.lower()):
        raise ValueError(f"invalid {field}")
    return value.lower()


def _spec_forms(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    instructions = spec.get("instructions")
    if not isinstance(instructions, list):
        raise ValueError("spec.instructions must be an array")
    forms: dict[str, dict[str, Any]] = {}
    form_keys: dict[tuple[int, int, int], str] = {}
    for item in instructions:
        if not isinstance(item, dict):
            continue
        form_id = item.get("id")
        mnemonic = item.get("mnemonic")
        encoding = item.get("encoding")
        if not isinstance(form_id, str) or not isinstance(mnemonic, str) or not isinstance(encoding, dict):
            continue
        if form_id in forms:
            raise ValueError(f"duplicate golden form_id: {form_id}")
        length_bits = _parse_int(encoding.get("length_bits"), f"{form_id}.length_bits")
        if length_bits <= 0 or length_bits % 8:
            raise ValueError(f"{form_id}.length_bits must be a positive whole number of bytes")
        parts = encoding.get("parts")
        if not isinstance(parts, list) or not parts:
            raise ValueError(f"{form_id}.parts must be a non-empty array")

        # Multi-part indexes name 32-bit little-endian lanes.  A singleton may
        # span the instruction's full 16/32/48-bit width.
        composite_mask = 0
        composite_match = 0
        occupied_ranges: list[tuple[int, int]] = []
        seen_indexes: set[int] = set()
        for part_number, part in enumerate(parts):
            if not isinstance(part, dict):
                raise ValueError(f"{form_id}.parts[{part_number}] must be an object")
            default_index = 0 if len(parts) == 1 else None
            default_width = length_bits if len(parts) == 1 else None
            part_index = _parse_int(
                part.get("index", default_index), f"{form_id}.parts[{part_number}].index"
            )
            width_bits = _parse_int(
                part.get("width_bits", default_width),
                f"{form_id}.parts[{part_number}].width_bits",
            )
            if part_index < 0:
                raise ValueError(f"{form_id}.parts[{part_number}].index must be non-negative")
            if part_index in seen_indexes:
                raise ValueError(f"{form_id} has duplicate part index {part_index}")
            if width_bits <= 0:
                raise ValueError(f"{form_id}.parts[{part_number}].width_bits must be positive")
            if len(parts) > 1 and width_bits > 32:
                raise ValueError(
                    f"{form_id}.parts[{part_number}].width_bits exceeds the 32-bit part stride"
                )

            bit_offset = part_index * 32
            bit_end = bit_offset + width_bits
            if bit_end > length_bits:
                raise ValueError(f"{form_id}.parts[{part_number}] exceeds instruction length")
            if any(bit_offset < end and start < bit_end for start, end in occupied_ranges):
                raise ValueError(f"{form_id}.parts[{part_number}] overlaps another part")

            part_mask = _parse_int(part.get("mask"), f"{form_id}.parts[{part_number}].mask")
            part_match = _parse_int(part.get("match"), f"{form_id}.parts[{part_number}].match")
            part_limit = 1 << width_bits
            if part_mask < 0 or part_mask >= part_limit:
                raise ValueError(f"{form_id}.parts[{part_number}].mask exceeds part width")
            if part_match < 0 or part_match >= part_limit:
                raise ValueError(f"{form_id}.parts[{part_number}].match exceeds part width")
            if part_match & ~part_mask:
                raise ValueError(f"{form_id}.parts[{part_number}].match sets bits outside mask")

            composite_mask |= part_mask << bit_offset
            composite_match |= part_match << bit_offset
            occupied_ranges.append((bit_offset, bit_end))
            seen_indexes.add(part_index)

        cursor = 0
        for start, end in sorted(occupied_ranges):
            if start != cursor:
                raise ValueError(f"{form_id}.parts do not cover the instruction contiguously")
            cursor = end
        if cursor != length_bits:
            raise ValueError(f"{form_id}.parts do not cover the full instruction length")
        instruction_limit = 1 << length_bits
        if composite_mask >= instruction_limit or composite_match >= instruction_limit:
            raise ValueError(f"{form_id} composite encoding exceeds instruction length")

        form_key = (length_bits, composite_mask, composite_match)
        if form_key in form_keys:
            raise ValueError(
                f"golden forms {form_keys[form_key]} and {form_id} have the same form_key"
            )
        form_keys[form_key] = form_id
        forms[form_id] = {
            "form_id": form_id,
            "mnemonic": mnemonic,
            "length_bits": length_bits,
            "mask": composite_mask,
            "match": composite_match,
        }
    return forms


def _extract_numeric_literals(text: str) -> set[int]:
    return {int(value, 16) for value in HEX_RE.findall(text)}


def _execution_observation(
    run_path: Path,
    run: dict[str, Any],
    *,
    test_contract: object,
    failure_attribution: object,
) -> dict[str, Any]:
    run_data = run.get("run") if isinstance(run.get("run"), dict) else {}
    failure = run.get("failure") if isinstance(run.get("failure"), dict) else None
    return {
        "run_evidence": str(run_path),
        "status": run.get("status", "unknown"),
        "oracle_verdict": run.get("oracle_verdict", "unknown"),
        "exit_code": run_data.get("exit_code"),
        "timed_out": bool(run_data.get("timed_out", False)),
        "stalled": bool(run_data.get("stalled", False)),
        "timeout_after_fail": bool(run_data.get("timeout_after_fail", False)),
        "pass_marker": run_data.get("pass_marker"),
        "failure": failure,
        "test_contract": test_contract,
        "failure_attribution": failure_attribution,
    }


def _function_body(text: str, symbol: str) -> str | None:
    match = re.search(rf"\b{re.escape(symbol)}\s*\([^;{{}}]*\)\s*\{{", text)
    if match is None:
        return None
    opening = text.find("{", match.start())
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[opening : index + 1]
    return None


def _assertion_binds(body: str, expected: int, test_id: int) -> bool:
    for match in re.finditer(r"\bTEST_[A-Z0-9_]+\s*\((.*?)\)\s*;", body, re.DOTALL):
        literals = _extract_numeric_literals(match.group(1))
        if expected in literals and test_id in literals:
            return True
    return False


def _trace_pcs(text: str) -> set[int]:
    return {
        int(match.group(1), 16)
        for match in re.finditer(r"^\s*0x([0-9a-fA-F]+):", text, re.MULTILINE)
    }


TARGET_PC_WATCH_KIND = "qemu_target_pc_watch_v1"
TARGET_PC_WATCH_RE = re.compile(
    r"^linx_pc_watch:\s+pc=0x([0-9a-fA-F]+)\s+"
    r"hit=([0-9]+)\s+printed=([0-9]+)\s+count=([0-9]+)(?:\s|$)"
)


def _target_pc_watch_packets(text: str) -> set[tuple[int, int, int]]:
    packets: set[tuple[int, int, int]] = set()
    for line in text.splitlines():
        match = TARGET_PC_WATCH_RE.match(line)
        if match is None:
            continue
        pc = int(match.group(1), 16)
        hit = int(match.group(2), 10)
        printed = int(match.group(3), 10)
        count = int(match.group(4), 10)
        if hit >= 1 and printed >= 1:
            packets.add((pc, hit, count))
    return packets


def _parse_pc_watch_env(value: object) -> list[int]:
    if not isinstance(value, str) or not value:
        raise ValueError("target PC-watch environment is missing")
    pcs: list[int] = []
    for token in value.split(","):
        pc = _parse_int(token.strip(), "target PC-watch environment")
        if pc < 0 or pc > 0xFFFFFFFFFFFFFFFF:
            raise ValueError("target PC-watch PC must fit uint64")
        if pc in pcs:
            raise ValueError("target PC-watch environment contains duplicate PCs")
        pcs.append(pc)
    if len(pcs) > 16:
        raise ValueError("target PC-watch environment exceeds QEMU's 16-PC limit")
    return pcs


def _normalize_disassembly(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _inspect_elf_instruction(
    repo_root: Path,
    elf_path: Path,
    *,
    pc: int,
    size: int,
    symbol: str,
) -> dict[str, Any]:
    """Bind a claimed instruction to its PT_LOAD offset, symbol, and objdump text."""
    data = elf_path.read_bytes()
    if len(data) < 64 or data[:6] != b"\x7fELF\x02\x01":
        raise ValueError("ELF must be little-endian ELF64")
    header = struct.unpack_from("<16sHHIQQQIHHHHHH", data, 0)
    phoff, shoff = header[5], header[6]
    phentsize, phnum = header[9], header[10]
    shentsize, shnum = header[11], header[12]
    if phentsize < 56 or shentsize < 64:
        raise ValueError("ELF header table entry size is invalid")

    mapped_offset: int | None = None
    for index in range(phnum):
        offset = phoff + index * phentsize
        if offset + 56 > len(data):
            raise ValueError("ELF program header table is truncated")
        p_type, _, p_offset, p_vaddr, _, p_filesz, _, _ = struct.unpack_from(
            "<IIQQQQQQ", data, offset
        )
        if p_type == 1 and p_vaddr <= pc and pc + size <= p_vaddr + p_filesz:
            mapped_offset = p_offset + (pc - p_vaddr)
            break
    if mapped_offset is None or mapped_offset + size > len(data):
        raise ValueError("instruction PC is not backed by an ELF PT_LOAD range")

    sections: list[tuple[int, ...]] = []
    for index in range(shnum):
        offset = shoff + index * shentsize
        if offset + 64 > len(data):
            raise ValueError("ELF section header table is truncated")
        sections.append(struct.unpack_from("<IIQQQQIIQQ", data, offset))

    symbol_range: tuple[int, int] | None = None
    for section in sections:
        _, sh_type, _, _, sym_offset, sym_size, sh_link, _, _, sym_entsize = section
        if sh_type != 2 or not sym_entsize or sh_link >= len(sections):
            continue
        string_section = sections[sh_link]
        strings_offset, strings_size = string_section[4], string_section[5]
        strings = data[strings_offset : strings_offset + strings_size]
        for entry_offset in range(sym_offset, sym_offset + sym_size, sym_entsize):
            if entry_offset + 24 > len(data):
                raise ValueError("ELF symbol table is truncated")
            name_offset, _, _, _, value, symbol_size = struct.unpack_from(
                "<IBBHQQ", data, entry_offset
            )
            if name_offset >= len(strings):
                continue
            end = strings.find(b"\0", name_offset)
            if end < 0:
                continue
            name = strings[name_offset:end].decode("utf-8", errors="replace")
            if name == symbol:
                symbol_range = (value, value + symbol_size)
                break
        if symbol_range is not None:
            break
    if symbol_range is None or symbol_range[0] >= symbol_range[1]:
        raise ValueError("instruction symbol is absent or has an empty ELF range")
    if not (symbol_range[0] <= pc and pc + size <= symbol_range[1]):
        raise ValueError("instruction PC is outside the claimed ELF symbol range")

    objdump = repo_root / "compiler/llvm/build-linxisa-clang/bin/llvm-objdump"
    if not objdump.is_file():
        discovered = shutil.which("llvm-objdump")
        if discovered is None:
            raise ValueError("llvm-objdump is unavailable for ELF instruction binding")
        objdump = Path(discovered)
    completed = subprocess.run(
        [
            str(objdump),
            "-d",
            f"--start-address=0x{pc:x}",
            f"--stop-address=0x{pc + size:x}",
            str(elf_path),
        ],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        raise ValueError(f"llvm-objdump failed for ELF instruction binding: {completed.stderr.strip()}")
    line_match = re.search(rf"^\s*{pc:x}:\s+(.+)$", completed.stdout, re.MULTILINE | re.IGNORECASE)
    if line_match is None:
        raise ValueError("llvm-objdump did not emit the claimed instruction PC")
    tokens = line_match.group(1).split()
    if len(tokens) < size + 1 or any(re.fullmatch(r"[0-9a-fA-F]{2}", token) is None for token in tokens[:size]):
        raise ValueError("llvm-objdump did not emit complete instruction bytes")
    objdump_bytes = bytes(int(token, 16) for token in tokens[:size])
    return {
        "elf_offset": mapped_offset,
        "raw_bytes": data[mapped_offset : mapped_offset + size],
        "objdump_bytes": objdump_bytes,
        "disassembly": " ".join(tokens[size:]),
        "symbol_start": symbol_range[0],
        "symbol_end": symbol_range[1],
    }


def _validate_entry(
    *,
    repo_root: Path,
    entry: object,
    forms: dict[str, dict[str, Any]],
    current_qemu_sha: str,
    qemu_root: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any], list[str]]:
    reasons: list[str] = []
    qemu_binary_verification: str | None = None
    if not isinstance(entry, dict):
        return None, {"status": "unavailable"}, ["entry must be an object"]

    form_id = entry.get("form_id")
    golden = forms.get(form_id) if isinstance(form_id, str) else None
    if golden is None:
        reasons.append("unknown golden form_id")

    mnemonic = entry.get("mnemonic")
    if not isinstance(mnemonic, str) or not mnemonic:
        reasons.append("missing mnemonic")
    elif golden is not None and mnemonic != golden["mnemonic"]:
        reasons.append("mnemonic disagrees with golden form")

    key = entry.get("form_key")
    if not isinstance(key, dict):
        reasons.append("missing form_key")
    elif golden is not None:
        try:
            candidate = {
                "length_bits": _parse_int(key.get("length_bits"), "form_key.length_bits"),
                "mask": _parse_int(key.get("mask"), "form_key.mask"),
                "match": _parse_int(key.get("match"), "form_key.match"),
            }
            if any(candidate[name] != golden[name] for name in candidate):
                reasons.append("form_key disagrees with golden form")
        except ValueError as exc:
            reasons.append(str(exc))

    suite = entry.get("suite")
    if not isinstance(suite, str) or not suite:
        reasons.append("missing suite")
    try:
        test_id = _test_id(entry.get("test_id"))
    except ValueError as exc:
        test_id = None
        reasons.append(str(exc))

    try:
        elf_path = _repo_path(repo_root, entry.get("elf"), "elf")
        if not elf_path.is_file():
            raise ValueError("ELF does not exist")
    except ValueError as exc:
        elf_path = None
        reasons.append(str(exc))
    try:
        object_path = _repo_path(repo_root, entry.get("object"), "object")
        if not object_path.is_file():
            raise ValueError("object does not exist")
    except ValueError as exc:
        object_path = None
        reasons.append(str(exc))

    instruction = entry.get("instruction")
    raw_bytes = None
    disassembly = None
    object_offset = None
    elf_offset = None
    instruction_pc = None
    instruction_symbol = None
    if not isinstance(instruction, dict):
        reasons.append("missing instruction evidence")
    else:
        raw_text = instruction.get("raw_bytes_le")
        disassembly = instruction.get("disassembly")
        instruction_symbol = instruction.get("symbol")
        if not isinstance(raw_text, str) or not raw_text:
            reasons.append("missing raw byte evidence")
        else:
            try:
                raw_bytes = bytes.fromhex(raw_text)
            except ValueError:
                reasons.append("invalid raw byte evidence")
        if not isinstance(disassembly, str) or not disassembly:
            reasons.append("missing disassembly evidence")
        elif isinstance(mnemonic, str) and mnemonic.lower() not in disassembly.lower():
            reasons.append("disassembly does not name the bound mnemonic")
        try:
            object_offset = _parse_int(instruction.get("object_offset"), "instruction.object_offset")
            elf_offset = _parse_int(instruction.get("elf_offset"), "instruction.elf_offset")
            instruction_pc = _parse_int(instruction.get("pc"), "instruction.pc")
            if object_offset < 0 or elf_offset < 0 or instruction_pc < 0:
                raise ValueError("instruction offsets and PC must be non-negative")
        except ValueError as exc:
            reasons.append(str(exc))
        if not isinstance(instruction_symbol, str) or not instruction_symbol:
            reasons.append("missing instruction symbol")

    if raw_bytes is not None and golden is not None:
        expected_size = (golden["length_bits"] + 7) // 8
        if len(raw_bytes) != expected_size:
            reasons.append("raw byte length disagrees with golden form")
        else:
            word = int.from_bytes(raw_bytes, "little")
            if word & golden["mask"] != golden["match"]:
                reasons.append("raw bytes do not match golden form encoding")
        if object_path is not None and object_offset is not None:
            data = object_path.read_bytes()
            if data[object_offset : object_offset + len(raw_bytes)] != raw_bytes:
                reasons.append("raw bytes do not match bound object offset")
        if elf_path is not None and elf_offset is not None:
            data = elf_path.read_bytes()
            if data[elf_offset : elf_offset + len(raw_bytes)] != raw_bytes:
                reasons.append("raw bytes do not match bound ELF offset")
        if (
            elf_path is not None
            and elf_offset is not None
            and instruction_pc is not None
            and isinstance(instruction_symbol, str)
            and instruction_symbol
            and isinstance(disassembly, str)
            and disassembly
        ):
            try:
                elf_binding = _inspect_elf_instruction(
                    repo_root,
                    elf_path,
                    pc=instruction_pc,
                    size=len(raw_bytes),
                    symbol=instruction_symbol,
                )
                if elf_binding["elf_offset"] != elf_offset:
                    reasons.append("instruction PC maps to a different ELF offset")
                if elf_binding["raw_bytes"] != raw_bytes or elf_binding["objdump_bytes"] != raw_bytes:
                    reasons.append("ELF/objdump bytes disagree with claimed instruction bytes")
                if _normalize_disassembly(elf_binding["disassembly"]) != _normalize_disassembly(
                    disassembly
                ):
                    reasons.append("ELF disassembly disagrees with claimed instruction text")
            except (OSError, ValueError, struct.error) as exc:
                reasons.append(str(exc))

    reachability = entry.get("reachability")
    if not isinstance(reachability, dict):
        reasons.append("missing test-to-symbol reachability")
    else:
        test_symbol = reachability.get("test_symbol")
        target_symbol = reachability.get("target_symbol")
        try:
            reachability_path = _repo_path(repo_root, reachability.get("source"), "reachability.source")
            source_text = reachability_path.read_text(encoding="utf-8", errors="replace")
            if not isinstance(test_symbol, str) or not test_symbol:
                reasons.append("missing reachability test_symbol")
            else:
                body = _function_body(source_text, test_symbol)
                if body is None or not isinstance(target_symbol, str) or target_symbol not in body:
                    reasons.append("target symbol is not reachable from bound test symbol")
            if target_symbol != instruction_symbol:
                reasons.append("reachability target disagrees with instruction symbol")
        except (OSError, ValueError) as exc:
            reasons.append(str(exc))

    try:
        entry_qemu_sha = _canonical_sha(entry.get("qemu_sha"), "QEMU SHA")
        if entry_qemu_sha != current_qemu_sha:
            reasons.append("QEMU SHA does not match current emulator/qemu HEAD")
    except ValueError as exc:
        entry_qemu_sha = None
        reasons.append(str(exc))

    oracle = entry.get("oracle")
    oracle_kind = None
    if not isinstance(oracle, dict):
        reasons.append("missing oracle evidence")
    else:
        oracle_kind = oracle.get("kind")
        locator = oracle.get("locator")
        expected = oracle.get("expected")
        if not isinstance(oracle_kind, str) or not oracle_kind or oracle_kind == "none":
            reasons.append("missing oracle kind")
        try:
            oracle_path = _repo_path(repo_root, oracle.get("source"), "oracle.source")
            if not oracle_path.is_file():
                raise ValueError("oracle source does not exist")
            source_text = oracle_path.read_text(encoding="utf-8", errors="replace")
            locator_body = _function_body(source_text, locator) if isinstance(locator, str) else None
            if not isinstance(locator, str) or not locator or locator_body is None:
                reasons.append("oracle locator absent from source")
            try:
                expected_value = _parse_int(expected, "oracle.expected")
                if (
                    locator_body is None
                    or test_id is None
                    or not _assertion_binds(locator_body, expected_value, int(test_id, 16))
                ):
                    reasons.append("expected value and test_id are not bound by one locator assertion")
            except ValueError as exc:
                reasons.append(str(exc))
        except ValueError as exc:
            reasons.append(str(exc))

    run = None
    run_path = None
    audited_run_record = False
    try:
        run_path = _repo_path(repo_root, entry.get("run_evidence"), "run_evidence")
        if not run_path.is_file():
            raise ValueError("run evidence does not exist")
        run_relative = run_path.relative_to(repo_root)
        try:
            run_relative.relative_to(CANONICAL_EVIDENCE_ROOT)
            canonical_run_path = True
        except ValueError:
            canonical_run_path = False
        recorded_run_digest = entry.get("run_evidence_sha256")
        if not isinstance(recorded_run_digest, str) or not SHA256_RE.fullmatch(recorded_run_digest):
            reasons.append("audited run evidence SHA-256 is missing")
        elif recorded_run_digest != _sha256(run_path):
            reasons.append("audited run evidence SHA-256 does not match")
        elif not canonical_run_path:
            reasons.append("audited run evidence is outside the canonical evidence bundle")
        else:
            audited_run_record = True
        run = _load_json(run_path)
    except (ValueError, json.JSONDecodeError) as exc:
        reasons.append(str(exc))
    test_contract = entry.get("test_contract")
    failure_attribution = entry.get("failure_attribution")
    if test_contract not in {"valid", "invalid", "under_review"}:
        reasons.append("invalid test_contract")
    elif test_contract != "valid":
        reasons.append("test_contract is not valid")
    if test_contract in {"invalid", "under_review"} and failure_attribution != "test_contract":
        reasons.append("invalid/under_review tests must attribute failure to test_contract")

    observation = _execution_observation(
        run_path,
        run,
        test_contract=test_contract,
        failure_attribution=failure_attribution,
    ) if run_path is not None and run is not None else {
        "run_evidence": str(run_path) if run_path else None,
        "status": "unavailable",
        "oracle_verdict": "unavailable",
        "exit_code": None,
        "timed_out": None,
        "stalled": None,
        "timeout_after_fail": None,
        "pass_marker": None,
        "failure": None,
        "test_contract": test_contract,
        "failure_attribution": failure_attribution,
    }
    if run_path is not None:
        observation["run_evidence"] = str(run_path.relative_to(repo_root))
    observation["suite"] = suite
    observation["test_id"] = test_id

    if run is not None:
        if run.get("status") != "PASS":
            reasons.append("run PASS is missing")
        if run.get("oracle_verdict") != "PASS":
            reasons.append("oracle verdict is not PASS")
        suites = run.get("suites")
        if not isinstance(suites, list) or suite not in suites:
            reasons.append("suite absent from run evidence")
        observed = run.get("required_test_ids_observed")
        normalized_observed: set[str] = set()
        if isinstance(observed, list):
            for value in observed:
                try:
                    normalized_observed.add(_test_id(value))
                except ValueError:
                    pass
        if test_id is None or test_id not in normalized_observed:
            reasons.append("test_id absent from run evidence")

        events = run.get("test_events")
        matching_events: list[tuple[int, str]] = []
        malformed_event = False
        saw_fail_event = False
        if isinstance(events, list):
            for event in events:
                if not isinstance(event, dict) or event.get("kind") not in {"START", "PASS", "FAIL"}:
                    malformed_event = True
                    continue
                try:
                    event_id = _test_id(event.get("test_id"))
                    sequence = _parse_int(event.get("seq"), "test event sequence")
                except ValueError:
                    malformed_event = True
                    continue
                if event_id == test_id:
                    matching_events.append((sequence, event["kind"]))
                if event["kind"] == "FAIL":
                    saw_fail_event = True
        else:
            malformed_event = True
        if malformed_event:
            reasons.append("anonymous or malformed test event")
        if saw_fail_event:
            reasons.append("run contains a test-specific FAIL event")
        if sorted(matching_events) != matching_events or [kind for _, kind in matching_events] != ["START", "PASS"]:
            reasons.append("test-specific START/PASS events are missing, duplicate, or out of order")

        pc_evidence = run.get("pc_evidence")
        target_pc_watch = (
            isinstance(pc_evidence, dict)
            and pc_evidence.get("kind") == TARGET_PC_WATCH_KIND
        )
        requested_watch_pcs: list[int] = []
        if target_pc_watch:
            if pc_evidence.get("packet_prefix") != "linx_pc_watch:":
                reasons.append("target PC-watch packet prefix is invalid")
            requested = pc_evidence.get("requested_pcs")
            if not isinstance(requested, list) or not requested:
                reasons.append("target PC-watch requested PC list is missing")
            else:
                try:
                    requested_watch_pcs = [
                        _parse_int(value, "target PC-watch requested PC")
                        for value in requested
                    ]
                    if (
                        len(set(requested_watch_pcs)) != len(requested_watch_pcs)
                        or any(pc < 0 or pc > 0xFFFFFFFFFFFFFFFF for pc in requested_watch_pcs)
                    ):
                        raise ValueError("target PC-watch requested PCs are invalid or duplicate")
                except ValueError as exc:
                    requested_watch_pcs = []
                    reasons.append(str(exc))
            debug_env = run.get("qemu_debug_env")
            if not isinstance(debug_env, dict):
                reasons.append("target PC-watch QEMU debug environment is missing")
            else:
                try:
                    env_watch_pcs = _parse_pc_watch_env(
                        debug_env.get("LINX_DEBUG_PC_WATCH")
                    )
                    if env_watch_pcs != requested_watch_pcs:
                        reasons.append(
                            "target PC-watch requested PCs disagree with QEMU debug environment"
                        )
                except ValueError as exc:
                    reasons.append(str(exc))
                if debug_env.get("LINX_DEBUG_PC_WATCH_HIT_LIMIT") != "1":
                    reasons.append("target PC-watch hit limit must be one")
                if debug_env.get("LINX_DEBUG_PC_WATCH_PRINT") != "1":
                    reasons.append("target PC-watch printing must be enabled")
            if instruction_pc is not None and instruction_pc not in requested_watch_pcs:
                reasons.append("instruction PC was not requested from target PC-watch")

        pc_hits = run.get("pc_hits")
        exact_pc_hit = False
        selected_watch_packet: tuple[int, int, int] | None = None
        if isinstance(pc_hits, list) and instruction_pc is not None and elf_offset is not None and raw_bytes is not None:
            for hit in pc_hits:
                if not isinstance(hit, dict):
                    continue
                try:
                    hit_pc = _parse_int(hit.get("pc"), "pc hit")
                except ValueError:
                    continue
                if hit_pc != instruction_pc:
                    continue
                if target_pc_watch:
                    if hit.get("evidence_kind") != TARGET_PC_WATCH_KIND:
                        continue
                    try:
                        hit_index = _parse_int(hit.get("hit"), "target PC-watch hit")
                        hit_count = _parse_int(hit.get("count"), "target PC-watch count")
                    except ValueError:
                        continue
                    if hit_index < 1 or hit_count < 0:
                        continue
                    selected_watch_packet = (hit_pc, hit_index, hit_count)
                exact_pc_hit = True
                break
        if not exact_pc_hit:
            reasons.append("exact executed PC hit is missing")
        run_qemu_sha = None
        try:
            run_qemu = run.get("qemu") if isinstance(run.get("qemu"), dict) else {}
            run_qemu_sha = _canonical_sha(
                run_qemu.get("sha"),
                "run QEMU SHA",
            )
            if entry_qemu_sha is not None and run_qemu_sha != entry_qemu_sha:
                reasons.append("run QEMU SHA disagrees with entry")
        except ValueError as exc:
            reasons.append(str(exc))
        qemu_version = run_qemu.get("version")
        if not isinstance(qemu_version, str) or not qemu_version:
            reasons.append("run QEMU version provenance is missing")
        elif isinstance(run_qemu_sha, str):
            version_shas = re.findall(r"\bg([0-9a-f]{7,40})\b", qemu_version.lower())
            if run_qemu_sha not in qemu_version.lower() and not any(
                run_qemu_sha.startswith(version_sha) for version_sha in version_shas
            ):
                reasons.append("run QEMU version does not identify the bound source SHA")
        if run_qemu.get("source_dirty") is True:
            patch_digest = run_qemu.get("patch_sha256")
            bound_digest = entry.get("qemu_patch_sha256")
            if (
                not isinstance(patch_digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", patch_digest)
                or bound_digest != patch_digest
            ):
                reasons.append("dirty QEMU requires an explicitly bound patch digest")
        elif run_qemu.get("source_dirty") is not False:
            reasons.append("run QEMU dirty provenance is missing")

        binary_digest = run_qemu.get("binary_sha256")
        if not isinstance(binary_digest, str) or not SHA256_RE.fullmatch(binary_digest):
            reasons.append("run QEMU binary SHA-256 is missing")
        try:
            qemu_binary_path = _repo_path(repo_root, run_qemu.get("path"), "run QEMU path")
            try:
                qemu_build_relative = qemu_binary_path.relative_to(qemu_root.resolve())
            except ValueError as exc:
                raise ValueError("run QEMU path is outside the selected QEMU root/build") from exc
            if (
                not qemu_build_relative.parts
                or not qemu_build_relative.parts[0].startswith("build")
                or qemu_binary_path.name != "qemu-system-linx64"
            ):
                reasons.append("run QEMU path is outside the selected QEMU root/build")
            elif qemu_binary_path.is_file():
                if isinstance(binary_digest, str) and _sha256(qemu_binary_path) == binary_digest:
                    qemu_binary_verification = "local_binary_sha256"
                else:
                    reasons.append("run QEMU binary SHA-256 does not match local binary")
            elif audited_run_record and isinstance(binary_digest, str) and SHA256_RE.fullmatch(binary_digest):
                qemu_binary_verification = "audited_recorded_digest"
            else:
                reasons.append("missing QEMU binary requires an audited canonical run record")
        except ValueError as exc:
            reasons.append(str(exc))

        run_data = run.get("run") if isinstance(run.get("run"), dict) else {}
        marker = run_data.get("pass_marker") if isinstance(run_data.get("pass_marker"), dict) else {}
        exit_code = run_data.get("exit_code")
        finisher_pass = False
        if marker.get("kind") == "finisher_exit_low8":
            try:
                finisher_pass = (
                    _parse_int(marker.get("value"), "finisher marker") == 0x55
                    and isinstance(exit_code, int)
                    and (exit_code & 0xFF) == 0x55
                )
            except ValueError:
                pass
        test_event_pass = (
            marker.get("kind") == "test_event_sequence"
            and marker.get("value") == "START/PASS"
            and exit_code == 0
        )
        uart_marker_candidate = (
            marker.get("kind") == "uart_success_marker"
            and marker.get("value") in UART_SUCCESS_MARKERS
            and exit_code == 0
        )
        uart_completion_valid = False
        if uart_marker_candidate:
            try:
                completion_id = _test_id(entry.get("suite_completion_test_id"))
                declared_completion_ids = {
                    _test_id(value)
                    for value in run_data.get("declared_suite_completion_test_ids", [])
                }
            except (TypeError, ValueError):
                completion_id = None
                declared_completion_ids = set()
            missing_required = run_data.get("missing_required_test_ids")
            missing_completion = run_data.get("missing_suite_completion_test_ids")
            final_completion = False
            if isinstance(events, list) and len(events) >= 2 and completion_id is not None:
                start_event, pass_event = events[-2:]
                try:
                    final_completion = (
                        isinstance(start_event, dict)
                        and isinstance(pass_event, dict)
                        and start_event.get("kind") == "START"
                        and pass_event.get("kind") == "PASS"
                        and _test_id(start_event.get("test_id")) == completion_id
                        and _test_id(pass_event.get("test_id")) == completion_id
                        and _parse_int(start_event.get("seq"), "completion START sequence") == len(events) - 2
                        and _parse_int(pass_event.get("seq"), "completion PASS sequence") == len(events) - 1
                    )
                except ValueError:
                    final_completion = False
            uart_completion_valid = (
                completion_id is not None
                and declared_completion_ids == {completion_id}
                and missing_required == []
                and missing_completion == []
                and final_completion
            )
            if not uart_completion_valid:
                reasons.append(
                    "suite UART marker lacks a declared, fully observed final completion test ID"
                )
        uart_pass = uart_marker_candidate and uart_completion_valid
        if not (finisher_pass or test_event_pass or uart_pass):
            reasons.append("verified finisher, suite UART, or test-specific PASS marker is missing")
        if run_data.get("timed_out") or run_data.get("stalled"):
            reasons.append("run timed out or stalled")

        artifacts = run.get("artifacts") if isinstance(run.get("artifacts"), dict) else {}
        for label, bound_path in (("elf", elf_path), ("object", object_path)):
            artifact = artifacts.get(label) if isinstance(artifacts.get(label), dict) else {}
            if label == "object" and isinstance(artifacts.get("objects"), list) and bound_path is not None:
                for candidate in artifacts["objects"]:
                    if not isinstance(candidate, dict):
                        continue
                    try:
                        candidate_path = _repo_path(
                            repo_root, candidate.get("path"), "run.artifacts.objects.path"
                        )
                    except ValueError:
                        continue
                    if candidate_path == bound_path:
                        artifact = candidate
                        break
            try:
                artifact_path = _repo_path(repo_root, artifact.get("path"), f"run.artifacts.{label}.path")
                digest = artifact.get("sha256")
                if bound_path is not None and artifact_path != bound_path:
                    reasons.append(f"run {label} path disagrees with entry")
                if not isinstance(digest, str) or bound_path is None or digest != _sha256(bound_path):
                    reasons.append(f"run {label} SHA-256 does not match artifact")
            except ValueError as exc:
                reasons.append(str(exc))
        for label in ("uart",):
            artifact = artifacts.get(label) if isinstance(artifacts.get(label), dict) else {}
            try:
                artifact_path = _repo_path(
                    repo_root, artifact.get("path"), f"run.artifacts.{label}.path"
                )
                digest = artifact.get("sha256")
                if not artifact_path.is_file() or not isinstance(digest, str) or digest != _sha256(artifact_path):
                    reasons.append(f"run {label} SHA-256 does not match artifact")
                elif label == "uart" and uart_pass and marker["value"] not in artifact_path.read_text(
                    encoding="utf-8", errors="replace"
                ):
                    reasons.append("suite UART marker is absent from the hashed UART artifact")
            except ValueError as exc:
                reasons.append(str(exc))

        pc_artifact_label = "pc_watch" if target_pc_watch else "pc_trace"
        pc_artifact = (
            artifacts.get(pc_artifact_label)
            if isinstance(artifacts.get(pc_artifact_label), dict)
            else {}
        )
        try:
            pc_artifact_path = _repo_path(
                repo_root,
                pc_artifact.get("path"),
                f"run.artifacts.{pc_artifact_label}.path",
            )
            pc_artifact_digest = pc_artifact.get("sha256")
            if (
                not pc_artifact_path.is_file()
                or not isinstance(pc_artifact_digest, str)
                or pc_artifact_digest != _sha256(pc_artifact_path)
            ):
                reasons.append(
                    f"run {pc_artifact_label} SHA-256 does not match artifact"
                )
            else:
                pc_text = pc_artifact_path.read_text(
                    encoding="utf-8", errors="replace"
                )
                if target_pc_watch:
                    if (
                        selected_watch_packet is None
                        or selected_watch_packet not in _target_pc_watch_packets(pc_text)
                    ):
                        reasons.append(
                            "claimed exact PC hit is absent from the hashed target PC-watch packet"
                        )
                elif (
                    instruction_pc is None
                    or instruction_pc not in _trace_pcs(pc_text)
                ):
                    reasons.append("claimed PC hit is absent from the hashed PC trace")
        except ValueError as exc:
            reasons.append(str(exc))

    max_level = entry.get("max_level")
    if max_level not in {"L2", "L3"}:
        reasons.append("max_level must be L2 or L3")
    if max_level == "L3" and oracle_kind not in L3_ORACLE_KINDS:
        reasons.append("L3 requires a semantic oracle kind")

    if reasons:
        return None, observation, list(dict.fromkeys(reasons))

    assert golden is not None and test_id is not None and elf_path is not None and object_path is not None
    admitted = {
        "form_id": golden["form_id"],
        "mnemonic": golden["mnemonic"],
        "form_key": {
            "length_bits": golden["length_bits"],
            "mask": f"0x{golden['mask']:x}",
            "match": f"0x{golden['match']:x}",
        },
        "suite": suite,
        "test_id": test_id,
        "elf": str(elf_path.relative_to(repo_root)),
        "elf_sha256": _sha256(elf_path),
        "object": str(object_path.relative_to(repo_root)),
        "object_sha256": _sha256(object_path),
        "raw_bytes_le": raw_bytes.hex() if raw_bytes is not None else None,
        "disassembly": disassembly,
        "pc": f"0x{instruction_pc:x}",
        "symbol": instruction_symbol,
        "qemu_sha": entry_qemu_sha,
        "qemu_binary_verification": qemu_binary_verification,
        "run_evidence": str(run_path.relative_to(repo_root)) if run_path else None,
        "oracle": oracle,
        "max_level": max_level,
    }
    return admitted, observation, []


def build_report(
    *,
    repo_root: Path,
    spec_path: Path,
    manifest_path: Path,
    current_qemu_sha: str,
    qemu_root: Path | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    spec_path = spec_path.resolve()
    manifest_path = manifest_path.resolve()
    current_qemu_sha = _canonical_sha(current_qemu_sha, "current QEMU SHA")
    qemu_root = (qemu_root or repo_root / "emulator" / "qemu").resolve()
    spec = _load_json(spec_path)
    manifest = _load_json(manifest_path)
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"manifest schema_version must be {SCHEMA_VERSION}")
    availability = manifest.get("availability")
    if not isinstance(availability, dict):
        raise ValueError("manifest.availability must be an object")
    for level in ("L2", "L3"):
        if availability.get(level) not in AVAILABILITY_VALUES:
            raise ValueError(f"manifest availability for {level} must be available or unavailable")
    entries = manifest.get("evidence")
    if not isinstance(entries, list):
        raise ValueError("manifest.evidence must be an array")

    forms = _spec_forms(spec)
    admitted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    seen_observations: set[str] = set()
    for index, entry in enumerate(entries):
        accepted, observation, reasons = _validate_entry(
            repo_root=repo_root,
            entry=entry,
            forms=forms,
            current_qemu_sha=current_qemu_sha,
            qemu_root=qemu_root,
        )
        observation_key = json.dumps(observation, sort_keys=True)
        if observation_key not in seen_observations:
            observations.append(observation)
            seen_observations.add(observation_key)
        if accepted is not None:
            admitted.append(accepted)
        else:
            rejected.append(
                {
                    "index": index,
                    "form_id": entry.get("form_id") if isinstance(entry, dict) else None,
                    "suite": entry.get("suite") if isinstance(entry, dict) else None,
                    "test_id": entry.get("test_id") if isinstance(entry, dict) else None,
                    "reasons": reasons,
                }
            )

    declared_observations = manifest.get("execution_observations", [])
    if not isinstance(declared_observations, list):
        raise ValueError("manifest.execution_observations must be an array")
    for item in declared_observations:
        if not isinstance(item, dict):
            raise ValueError("manifest execution observation must be an object")
        contract = item.get("test_contract")
        attribution = item.get("failure_attribution")
        if contract not in {"valid", "invalid", "under_review"}:
            raise ValueError("manifest execution observation has invalid test_contract")
        if contract != "valid" and attribution != "test_contract":
            raise ValueError("invalid/under_review observation must use test_contract attribution")
        observations.append(item)

    evidence: dict[str, Any] = {}
    for level in ("L2", "L3"):
        if availability[level] == "unavailable":
            evidence[level] = {
                "availability": "unavailable",
                "claim": "runtime_execution" if level == "L2" else "semantic_oracle",
                "form_count": None,
                "mnemonic_count": None,
            }
            continue
        selected = admitted if level == "L2" else [item for item in admitted if item["max_level"] == "L3"]
        evidence[level] = {
            "availability": "available",
            "claim": "runtime_execution" if level == "L2" else "semantic_oracle",
            "form_count": len({item["form_id"] for item in selected}),
            "mnemonic_count": len({item["mnemonic"] for item in selected}),
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": _utc_now(),
        "claim": "per_form_qemu_executable_coverage",
        "policy": {
            "L1_suite_exit_is_coverage": False,
            "exit_zero_or_stdout_alone_is_coverage": False,
            "failed_execution_is_counted": False,
            "failed_execution_is_persisted": True,
            "L3_requires_oracle_pass": True,
        },
        "inputs": {
            "spec": str(spec_path.relative_to(repo_root)),
            "manifest": str(manifest_path.relative_to(repo_root)),
            "qemu_sha": current_qemu_sha,
        },
        "evidence": evidence,
        "admitted": sorted(admitted, key=lambda item: (item["form_id"], item["test_id"])),
        "rejected": rejected,
        "execution_observations": observations,
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# QEMU Executable Coverage Ledger",
        "",
        f"Generated: `{report['generated_at_utc']}`",
        "",
        "This ledger counts only per-form evidence bound to golden identity, bytes, test ID,",
        "artifacts, QEMU SHA, a test-specific terminal PASS, and an oracle. Suite exit 0 and stdout alone do not count.",
        "",
        "## Evidence Levels",
        "",
        "| Level | Availability | Forms | Mnemonics |",
        "| --- | --- | ---: | ---: |",
    ]
    for level in ("L2", "L3"):
        item = report["evidence"][level]
        forms = "unavailable" if item["form_count"] is None else str(item["form_count"])
        mnemonics = "unavailable" if item["mnemonic_count"] is None else str(item["mnemonic_count"])
        lines.append(f"| {level} | `{item['availability']}` | {forms} | {mnemonics} |")
    lines.extend(["", "## Admitted Forms", ""])
    if report["admitted"]:
        lines.extend(
            [
                "| Form | Suite / Test | Level | Oracle | Bytes |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for item in report["admitted"]:
            lines.append(
                f"| `{item['form_id']}` | `{item['suite']} / {item['test_id']}` | "
                f"`{item['max_level']}` | `{item['oracle']['kind']}` | `{item['raw_bytes_le']}` |"
            )
    else:
        lines.append("None.")
    lines.extend(["", "## Failed / Rejected Evidence", ""])
    if report["rejected"]:
        for item in report["rejected"]:
            lines.append(
                f"- `{item['form_id'] or 'unknown'}` (`{item['suite'] or 'unknown'}`): "
                + "; ".join(item["reasons"])
            )
    else:
        lines.append("None.")
    lines.extend(["", "## Execution Observations", ""])
    if report["execution_observations"]:
        for item in report["execution_observations"]:
            suffix = ""
            identity = ""
            if item.get("suite") or item.get("test_id"):
                identity = f" `{item.get('suite', 'unknown')} / {item.get('test_id', 'unknown')}`:"
            if item.get("failure"):
                failure = item["failure"]
                suffix = (
                    f", failure `{failure.get('test_id')}` expected `{failure.get('expected')}` "
                    f"actual `{failure.get('actual')}`"
                )
            if item.get("test_contract"):
                suffix += f", test-contract `{item['test_contract']}`"
            if item.get("failure_attribution"):
                suffix += f", attribution `{item['failure_attribution']}`"
            if item.get("review_note"):
                suffix += f", note: {item['review_note']}"
            lines.append(
                f"-{identity} status `{item['status']}`, oracle `{item['oracle_verdict']}`, "
                f"timeout-after-fail `{item['timeout_after_fail']}`{suffix}"
            )
    else:
        lines.append("None.")
    lines.append("")
    return "\n".join(lines)


def _git_head(path: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        raise ValueError(f"cannot read Git HEAD for {path}: {proc.stderr.strip()}")
    return _canonical_sha(proc.stdout.strip(), "QEMU HEAD")


def _gate_failed(
    report: dict[str, Any], *, require_nonzero: bool, require_clean: bool
) -> bool:
    l2 = report["evidence"]["L2"]["form_count"]
    l3 = report["evidence"]["L3"]["form_count"]
    if require_nonzero and (
        not isinstance(l2, int) or l2 == 0 or not isinstance(l3, int) or l3 == 0
    ):
        return True
    return bool(require_clean and report["rejected"])


def main(argv: list[str] | None = None) -> int:
    script = Path(__file__).resolve()
    default_root = script.parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=default_root)
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--qemu-root", type=Path)
    parser.add_argument("--report-out", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--require-nonzero", action="store_true")
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="Fail when any manifest evidence entry is rejected.",
    )
    args = parser.parse_args(argv)

    root = args.repo_root.resolve()
    spec = (args.spec or root / "isa/v0.58/linxisa-v0.58.json").resolve()
    manifest = (args.manifest or root / "avs/qemu/qemu_executable_coverage_manifest.json").resolve()
    qemu_root = (args.qemu_root or root / "emulator/qemu").resolve()
    report_out = (args.report_out or root / "docs/bringup/gates/qemu_executable_coverage_latest.json").resolve()
    out_md = (args.out_md or root / "docs/bringup/gates/qemu_executable_coverage_latest.md").resolve()

    try:
        report = build_report(
            repo_root=root,
            spec_path=spec,
            manifest_path=manifest,
            current_qemu_sha=_git_head(qemu_root),
            qemu_root=qemu_root,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report_out.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(_render_markdown(report), encoding="utf-8")

    l2 = report["evidence"]["L2"]["form_count"]
    l3 = report["evidence"]["L3"]["form_count"]
    print(f"QEMU executable coverage: L2={l2} L3={l3} rejected={len(report['rejected'])}")
    if _gate_failed(
        report,
        require_nonzero=args.require_nonzero,
        require_clean=args.require_clean,
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
