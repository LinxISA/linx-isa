#!/usr/bin/env python3
"""
Compatibility wrapper for the tools/model-owned differential suite runner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path


class ReleaseStrictError(ValueError):
    """A differential report lacks release-promotion evidence."""


def _require_release_strict(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseStrictError(message)


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


REQUIRED_CONSUMERS = ("qemu", "ref", "compare")
REQUIRED_ARTIFACTS = {
    "compiler",
    "linker",
    "elf",
    "qemu",
    "ref",
    "compare",
    "manifest",
    "golden",
}


def _read_verified_file(row: object, label: str) -> tuple[Path, bytes, str]:
    _require_release_strict(isinstance(row, dict), f"release-strict missing {label}")
    path_text = row.get("path")
    expected_hash = row.get("sha256")
    _require_release_strict(
        isinstance(path_text, str) and bool(path_text) and _is_sha256(expected_hash),
        f"release-strict {label} missing path/SHA-256",
    )
    path = Path(path_text).expanduser().resolve()
    _require_release_strict(path.is_file(), f"release-strict {label} is missing: {path}")
    content = path.read_bytes()
    actual_hash = hashlib.sha256(content).hexdigest()
    _require_release_strict(
        actual_hash == expected_hash,
        f"release-strict {label} SHA-256 mismatch",
    )
    return path, content, actual_hash


def _elf_symbols(elf: bytes) -> dict[str, tuple[int, int, int]]:
    _require_release_strict(elf[:4] == b"\x7fELF", "release-strict ELF artifact is not ELF")
    _require_release_strict(
        len(elf) >= 64 and elf[4] == 2 and elf[5] in (1, 2),
        "release-strict supports only ELF64 symbol validation",
    )
    endian = "<" if elf[5] == 1 else ">"
    header = struct.unpack_from(endian + "HHIQQQIHHHHHH", elf, 16)
    section_offset, section_entry_size, section_count = header[5], header[10], header[11]
    _require_release_strict(
        section_entry_size >= 64
        and section_count > 0
        and section_offset + section_entry_size * section_count <= len(elf),
        "release-strict ELF section table is malformed",
    )
    sections = [
        struct.unpack_from(endian + "IIQQQQIIQQ", elf, section_offset + index * section_entry_size)
        for index in range(section_count)
    ]
    symbols: dict[str, tuple[int, int, int]] = {}
    for section in sections:
        section_type, offset, size, link, entry_size = (
            section[1],
            section[4],
            section[5],
            section[6],
            section[9],
        )
        if section_type not in (2, 11) or entry_size < 24 or link >= len(sections):
            continue
        strings_section = sections[link]
        strings = elf[strings_section[4] : strings_section[4] + strings_section[5]]
        _require_release_strict(
            offset + size <= len(elf), "release-strict ELF symbol table is malformed"
        )
        for symbol_offset in range(offset, offset + size, entry_size):
            name_offset, _, _, section_index, value, symbol_size = struct.unpack_from(
                endian + "IBBHQQ", elf, symbol_offset
            )
            if name_offset >= len(strings):
                continue
            name = strings[name_offset:].split(b"\0", 1)[0].decode("utf-8", errors="replace")
            if name:
                symbols[name] = (value, symbol_size, section_index)
    return symbols


def _result_contract(elf: bytes, manifest_bytes: bytes) -> tuple[int, int]:
    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as exc:
        raise ReleaseStrictError(f"release-strict manifest is invalid JSON: {exc}") from exc
    contract = manifest.get("result_memory") if isinstance(manifest, dict) else None
    _require_release_strict(isinstance(contract, dict), "release-strict manifest lacks result_memory")
    result_name = contract.get("result_symbol")
    size_name = contract.get("size_symbol")
    _require_release_strict(
        result_name == "cross_model_result" and size_name == "cross_model_result_size",
        "release-strict manifest uses unexpected result symbols",
    )
    symbols = _elf_symbols(elf)
    _require_release_strict(result_name in symbols and size_name in symbols, "release-strict ELF lacks result symbols")
    result_address, result_symbol_size, _ = symbols[result_name]
    size_value, _, size_section = symbols[size_name]
    _require_release_strict(
        size_section == 0xFFF1 and size_value > 0,
        "release-strict ELF size symbol must be a positive absolute symbol",
    )
    if result_symbol_size:
        _require_release_strict(
            result_symbol_size == size_value,
            "release-strict ELF result and size symbols disagree",
        )
    _require_release_strict(
        contract.get("address") == result_address,
        "release-strict manifest address disagrees with ELF symbol",
    )
    _require_release_strict(
        contract.get("size") == size_value,
        "release-strict manifest size disagrees with ELF symbol size",
    )
    return result_address, size_value


def validate_release_strict_payload(payload: dict) -> None:
    cases = payload.get("cases")
    _require_release_strict(
        isinstance(cases, list) and bool(cases),
        "release-strict requires at least one differential case",
    )
    for case in cases:
        case_id = str(case.get("id", "<unknown>")) if isinstance(case, dict) else "<unknown>"
        provenance = (
            case.get("provenance", payload.get("provenance"))
            if isinstance(case, dict)
            else payload.get("provenance")
        )
        _require_release_strict(
            isinstance(provenance, dict),
            "release-strict requires immutable artifact provenance",
        )
        artifacts = provenance.get("artifacts") if isinstance(provenance, dict) else None
        _require_release_strict(
            isinstance(artifacts, dict) and set(artifacts) == REQUIRED_ARTIFACTS,
            "release-strict requires immutable artifact provenance",
        )
        verified_artifacts = {
            name: _read_verified_file(artifacts[name], name) for name in sorted(REQUIRED_ARTIFACTS)
        }
        _require_release_strict(
            provenance.get("verified_after_run") is True,
            "release-strict provenance was not re-verified after the run",
        )
        _require_release_strict(
            isinstance(case, dict) and case.get("status") == "pass",
            f"release-strict case {case_id} did not pass",
        )
        result_memory = case.get("result_memory")
        _require_release_strict(
            isinstance(result_memory, dict) and set(result_memory) == set(REQUIRED_CONSUMERS),
            f"release-strict case {case_id} has invalid consumer set",
        )
        _, expected_size = _result_contract(
            verified_artifacts["elf"][1], verified_artifacts["manifest"][1]
        )
        golden_bytes = verified_artifacts["golden"][1]
        golden_hash = verified_artifacts["golden"][2]
        _require_release_strict(
            len(golden_bytes) == expected_size,
            f"release-strict case {case_id} golden size does not match ELF symbols",
        )
        verified_results: dict[str, tuple[bytes, str]] = {}
        for model_name in REQUIRED_CONSUMERS:
            row = result_memory[model_name]
            _, result_bytes, result_hash = _read_verified_file(row, f"{model_name} result")
            _require_release_strict(
                row.get("size") == expected_size
                and len(result_bytes) == expected_size
                and row.get("consumer_sha256") == verified_artifacts[model_name][2],
                f"release-strict case {case_id} {model_name} result size mismatch",
            )
            _require_release_strict(
                result_bytes == golden_bytes,
                f"release-strict case {case_id} {model_name} result differs from golden",
            )
            verified_results[model_name] = (result_bytes, result_hash)

        golden = case.get("golden_comparisons")
        _require_release_strict(
            isinstance(golden, dict) and set(golden) == set(REQUIRED_CONSUMERS),
            f"release-strict case {case_id} lacks passing independent golden comparisons",
        )
        for name in REQUIRED_CONSUMERS:
            row = golden[name]
            _require_release_strict(
                isinstance(row, dict)
                and row.get("status") == "pass"
                and row.get("actual_sha256") == verified_results[name][1]
                and row.get("golden_sha256") == golden_hash
                and row.get("consumer_sha256") == verified_artifacts[name][2]
                and row.get("size") == expected_size,
                f"release-strict case {case_id} comparison hash binding failed for {name}",
            )
        pairwise = case.get("pairwise_comparisons")
        expected_pairs = {
            "qemu:ref": ("qemu", "ref"),
            "qemu:compare": ("qemu", "compare"),
            "ref:compare": ("ref", "compare"),
        }
        _require_release_strict(
            isinstance(pairwise, dict) and set(pairwise) == set(expected_pairs),
            f"release-strict case {case_id} lacks passing pairwise comparisons",
        )
        for pair, (left, right) in expected_pairs.items():
            row = pairwise[pair]
            _require_release_strict(
                verified_results[left][0] == verified_results[right][0]
                and isinstance(row, dict)
                and row.get("status") == "pass"
                and row.get("left_sha256") == verified_results[left][1]
                and row.get("right_sha256") == verified_results[right][1]
                and row.get("left_consumer_sha256") == verified_artifacts[left][2]
                and row.get("right_consumer_sha256") == verified_artifacts[right][2]
                and row.get("size") == expected_size,
                f"release-strict case {case_id} comparison hash binding failed for {pair}",
            )


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Compatibility wrapper for the tools/model differential suite")
    ap.add_argument("--root", default="")
    ap.add_argument("--suite", default="avs/model/linx_model_diff_suite.yaml")
    ap.add_argument("--workdir", default="")
    ap.add_argument("--profile", default="", help="Compatibility-only metadata field.")
    ap.add_argument("--trace-schema-version", default="", help="Compatibility-only metadata field.")
    ap.add_argument("--report-out", default="", help="Optional path to write the JSON summary.")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    runner = root / "tools" / "model" / "tests" / "avs" / "run_model_diff_suite.py"

    env = dict(os.environ)
    env["LINX_VIRT_TEST_FINISHER"] = "1"
    cmd = [
        sys.executable,
        str(runner),
        "--root",
        str(root),
        "--suite",
        args.suite,
        "--qemu",
        str(root / "emulator" / "qemu" / "build-linx" / "qemu-system-linx64"),
        "--qemu-bios",
        "none",
    ]
    if args.workdir:
        cmd.extend(["--workdir", args.workdir])

    proc = subprocess.run(
        cmd,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        return proc.returncode

    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.stdout.write(proc.stdout)
        return proc.returncode

    if args.profile:
        payload["profile"] = args.profile
    if args.trace_schema_version:
        payload["trace_schema_version"] = args.trace_schema_version

    if args.profile == "release-strict":
        if args.trace_schema_version != "1.0":
            print("error: release-strict requires --trace-schema-version 1.0", file=sys.stderr)
            return 2
        try:
            validate_release_strict_payload(payload)
        except ReleaseStrictError as exc:
            payload["release_strict"] = {"status": "fail", "error": str(exc)}
            rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
            if args.report_out:
                report_out = Path(args.report_out)
                report_out.parent.mkdir(parents=True, exist_ok=True)
                report_out.write_text(rendered, encoding="utf-8")
            sys.stdout.write(rendered)
            return 1
        payload["release_strict"] = {"status": "pass"}

    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.report_out:
        report_out = Path(args.report_out)
        report_out.parent.mkdir(parents=True, exist_ok=True)
        report_out.write_text(rendered, encoding="utf-8")

    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
