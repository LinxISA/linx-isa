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
RESULT_REQUIRED_ARTIFACTS = {
    "compiler",
    "linker",
    "elf",
    "qemu",
    "qemu_source_marker",
    "ref",
    "compare",
    "manifest",
    "golden",
}
TRACE_REQUIRED_ARTIFACTS = {
    "compiler",
    "linker",
    "elf",
    "qemu",
    "qemu_source_marker",
    "model",
    "manifest",
}
CANONICAL_SUITE_RELATIVE = Path("avs/model/linx_model_diff_suite.yaml")
CANONICAL_CASE_SOURCES = {
    "MODEL-SCALAR-COMMIT-SMOKE": "emulator/qemu/tests/linxisa/mcopy_mset_basic.s",
    "MODEL-SCALAR-MCOPY-MSET": "emulator/qemu/tests/linxisa/mcopy_mset_basic.s",
    "MODEL-VECTOR-LANE-CONTROL": "emulator/qemu/tests/linxisa/vector_header_smoke.s",
    "MODEL-TILE-DESCRIPTOR-LEGALITY": "emulator/qemu/tests/linxisa/tile_descriptor_smoke.s",
    "MODEL-TILE-CONTROL-FLOW": "emulator/qemu/tests/linxisa/tile_control_flow_smoke.s",
    "MODEL-PRIVILEGED-EXCEPTION-EDGE": "emulator/qemu/tests/linxisa/privileged_ssrset_smoke.s",
    "MODEL-RELEASE-RESULT-MEMORY": "avs/model/release_result_memory.s",
}
RESULT_CASE_ID = "MODEL-RELEASE-RESULT-MEMORY"


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


def _git_identity(path: Path) -> tuple[str, str]:
    rows = []
    for revision in ("HEAD", "HEAD^{tree}"):
        proc = subprocess.run(
            ["git", "-C", str(path), "rev-parse", revision],
            check=False,
            capture_output=True,
            text=True,
        )
        _require_release_strict(
            proc.returncode == 0,
            f"release-strict cannot authenticate Git component {path}",
        )
        rows.append(proc.stdout.strip())
    return rows[0], rows[1]


def _gitlink_commit(root: Path, component: Path) -> str:
    relative = component.resolve().relative_to(root.resolve())
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "HEAD", str(relative)],
        check=False,
        capture_output=True,
        text=True,
    )
    fields = proc.stdout.split()
    _require_release_strict(
        proc.returncode == 0 and len(fields) >= 3 and fields[1] == "commit",
        f"release-strict component is not pinned by the superproject: {relative}",
    )
    return fields[2]


def _require_exact_path(row: object, expected: Path, label: str) -> None:
    _require_release_strict(isinstance(row, dict), f"release-strict missing {label}")
    actual = Path(str(row.get("path", ""))).expanduser().resolve()
    _require_release_strict(
        actual == expected.resolve(),
        f"release-strict {label} uses non-canonical path",
    )


def _validate_component_identity(
    row: object, expected: Path, label: str, *, root: Path | None = None
) -> None:
    _require_exact_path(row, expected, f"{label} component")
    assert isinstance(row, dict)
    commit, tree = _git_identity(expected)
    _require_release_strict(
        row.get("commit") == commit
        and row.get("tree") == tree
        and row.get("clean") is True,
        f"release-strict {label} component commit/tree mismatch",
    )
    status = subprocess.run(
        ["git", "-C", str(expected), "status", "--porcelain", "--untracked-files=no"],
        check=False,
        capture_output=True,
        text=True,
    )
    _require_release_strict(
        status.returncode == 0 and not status.stdout.strip(),
        f"release-strict {label} component worktree is dirty",
    )
    if root is not None:
        _require_release_strict(
            commit == _gitlink_commit(root, expected),
            f"release-strict {label} component does not match superproject gitlink",
        )


def _validate_qemu_source_marker(
    row: object, *, qemu_path: Path, expected_commit: str
) -> None:
    marker = qemu_path.resolve().parent / ".linx_qemu_clean_head"
    _require_exact_path(row, marker, "QEMU source marker")
    _, content, _ = _read_verified_file(row, "QEMU source marker")
    _require_release_strict(
        content == f"{expected_commit}:worktree\n".encode(),
        "release-strict QEMU source marker does not match component commit",
    )


def _validate_canonical_case_set(cases: object) -> list[dict]:
    _require_release_strict(isinstance(cases, list), "release-strict cases must be a list")
    typed = [case for case in cases if isinstance(case, dict)]
    _require_release_strict(
        len(typed) == len(cases)
        and [case.get("id") for case in typed] == list(CANONICAL_CASE_SOURCES),
        "release-strict requires the exact ordered canonical case set",
    )
    return typed


def validate_canonical_release_payload(
    payload: dict, *, root: Path, suite_path: Path, qemu_path: Path
) -> None:
    canonical_suite = (root / CANONICAL_SUITE_RELATIVE).resolve()
    _require_release_strict(
        suite_path.resolve() == canonical_suite,
        "release-strict requires the canonical model suite",
    )
    _require_release_strict(
        payload.get("suite") == str(canonical_suite),
        "release-strict report names a non-canonical suite",
    )
    suite_bytes = canonical_suite.read_bytes()
    suite_hash = hashlib.sha256(suite_bytes).hexdigest()
    _require_release_strict(
        payload.get("suite_sha256") == suite_hash,
        "release-strict suite SHA-256 mismatch",
    )
    cases = _validate_canonical_case_set(payload.get("cases"))
    component_paths = {
        "compiler": root / "compiler/llvm",
        "model": root / "tools/model",
        "qemu": root / "emulator/qemu",
    }
    canonical_artifact_paths = {
        "compiler": root / "compiler/llvm/build-linxisa-clang/bin/llvm-mc",
        "linker": root / "compiler/llvm/build-linxisa-clang/bin/ld.lld",
        "qemu": qemu_path,
        "model": root / "tools/model/build/linx_model_cli",
        "ref": root / "tools/model/build/linx_model_cli",
        "compare": root / "tools/model/build/linx_model_cli",
    }
    for case in cases:
        case_id = str(case["id"])
        source_path = (root / CANONICAL_CASE_SOURCES[case_id]).resolve()
        source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        _require_release_strict(
            case.get("source") == str(source_path)
            and case.get("source_sha256") == source_hash,
            f"release-strict case {case_id} source identity mismatch",
        )
        provenance = case.get("provenance")
        _require_release_strict(
            isinstance(provenance, dict),
            f"release-strict case {case_id} lacks provenance",
        )
        inputs = provenance.get("inputs")
        _require_release_strict(
            isinstance(inputs, dict) and set(inputs) == {"source", "suite"},
            f"release-strict case {case_id} lacks exact input provenance",
        )
        verified_source = _read_verified_file(inputs["source"], "source input")
        verified_suite = _read_verified_file(inputs["suite"], "suite input")
        _require_release_strict(
            verified_source[0] == source_path
            and verified_source[2] == source_hash
            and verified_suite[0] == canonical_suite
            and verified_suite[2] == suite_hash,
            f"release-strict case {case_id} input identity mismatch",
        )
        components = provenance.get("components")
        _require_release_strict(
            isinstance(components, dict) and set(components) == set(component_paths),
            f"release-strict case {case_id} lacks exact component identities",
        )
        for name, path in component_paths.items():
            _validate_component_identity(
                components[name], path.resolve(), name, root=root
            )
        artifacts = provenance.get("artifacts")
        _require_release_strict(
            isinstance(artifacts, dict),
            f"release-strict case {case_id} lacks artifacts",
        )
        for name, path in canonical_artifact_paths.items():
            if name in artifacts:
                _require_exact_path(artifacts[name], path, f"{case_id} {name}")
        _validate_qemu_source_marker(
            artifacts.get("qemu_source_marker"),
            qemu_path=qemu_path,
            expected_commit=str(components["qemu"]["commit"]),
        )
        expected_manifest = (
            root / "avs/model/release_result_memory.json"
            if case_id == RESULT_CASE_ID
            else canonical_suite
        )
        _require_exact_path(artifacts.get("manifest"), expected_manifest, f"{case_id} manifest")
        if case_id == RESULT_CASE_ID:
            _require_exact_path(
                artifacts.get("golden"),
                root / "avs/model/release_result_memory.golden.bin",
                f"{case_id} golden",
            )
    validate_release_strict_payload(payload)


def _elf_metadata(
    elf: bytes,
) -> tuple[
    dict[str, tuple[int, int, int]],
    list[tuple[int, ...]],
    list[tuple[int, int]],
]:
    _require_release_strict(elf[:4] == b"\x7fELF", "release-strict ELF artifact is not ELF")
    _require_release_strict(
        len(elf) >= 64 and elf[4] == 2 and elf[5] in (1, 2),
        "release-strict supports only ELF64 symbol validation",
    )
    endian = "<" if elf[5] == 1 else ">"
    header = struct.unpack_from(endian + "HHIQQQIHHHHHH", elf, 16)
    _require_release_strict(
        header[0] == 2,
        "release-strict requires an ET_EXEC ELF artifact",
    )
    program_offset, program_entry_size, program_count = (
        header[4],
        header[8],
        header[9],
    )
    section_offset, section_entry_size, section_count = header[5], header[10], header[11]
    _require_release_strict(
        program_entry_size >= 56
        and program_count > 0
        and program_offset + program_entry_size * program_count <= len(elf),
        "release-strict ELF program header table is malformed",
    )
    load_segments: list[tuple[int, int]] = []
    for index in range(program_count):
        program = struct.unpack_from(
            endian + "IIQQQQQQ", elf, program_offset + index * program_entry_size
        )
        if program[0] == 1:
            load_segments.append((program[3], program[3] + program[6]))
    _require_release_strict(
        bool(load_segments), "release-strict ELF has no PT_LOAD segment"
    )
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
    return symbols, sections, load_segments


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
    symbols, sections, load_segments = _elf_metadata(elf)
    _require_release_strict(result_name in symbols and size_name in symbols, "release-strict ELF lacks result symbols")
    result_address, result_symbol_size, result_section = symbols[result_name]
    size_value, _, size_section = symbols[size_name]
    _require_release_strict(
        result_section != 0 and result_section < len(sections),
        "release-strict ELF requires a defined result symbol",
    )
    _require_release_strict(
        sections[result_section][2] & 0x2 != 0,
        "release-strict ELF result symbol must be in an allocatable section",
    )
    _require_release_strict(
        result_address > 0,
        "release-strict ELF result symbol must have a nonzero address",
    )
    _require_release_strict(
        size_section == 0xFFF1 and size_value > 0,
        "release-strict ELF size symbol must be a positive absolute symbol",
    )
    if result_symbol_size:
        _require_release_strict(
            result_symbol_size == size_value,
            "release-strict ELF result and size symbols disagree",
        )
    result_end = result_address + size_value
    _require_release_strict(
        result_end > result_address
        and any(start <= result_address and result_end <= end for start, end in load_segments),
        "release-strict ELF result range must be fully contained in a PT_LOAD segment",
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
        has_result_proof = isinstance(case, dict) and "result_memory" in case
        required_artifacts = (
            RESULT_REQUIRED_ARTIFACTS if has_result_proof else TRACE_REQUIRED_ARTIFACTS
        )
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
            isinstance(artifacts, dict) and set(artifacts) == required_artifacts,
            "release-strict requires immutable artifact provenance",
        )
        verified_artifacts = {
            name: _read_verified_file(artifacts[name], name)
            for name in sorted(required_artifacts)
        }
        _require_release_strict(
            provenance.get("verified_after_run") is True,
            "release-strict provenance was not re-verified after the run",
        )
        _require_release_strict(
            isinstance(case, dict) and case.get("status") == "pass",
            f"release-strict case {case_id} did not pass",
        )
        if not has_result_proof:
            continue
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
    ap.add_argument(
        "--qemu",
        default="",
        help="Exact QEMU executable to authenticate and use for every case.",
    )
    ap.add_argument("--profile", default="", help="Compatibility-only metadata field.")
    ap.add_argument("--trace-schema-version", default="", help="Compatibility-only metadata field.")
    ap.add_argument("--report-out", default="", help="Optional path to write the JSON summary.")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[2]
    runner = root / "tools" / "model" / "tests" / "avs" / "run_model_diff_suite.py"
    qemu = (
        Path(args.qemu).expanduser().resolve()
        if args.qemu
        else root / "emulator" / "qemu" / "build-linx" / "qemu-system-linx64"
    )
    suite_path = (root / args.suite).resolve()
    if args.profile == "release-strict" and suite_path != (
        root / CANONICAL_SUITE_RELATIVE
    ).resolve():
        print("error: release-strict requires the canonical model suite", file=sys.stderr)
        return 2

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
        str(qemu),
        "--qemu-bios",
        "none",
    ]
    if args.workdir:
        cmd.extend(["--workdir", args.workdir])
    if args.profile:
        cmd.extend(["--profile", args.profile])

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
            validate_canonical_release_payload(
                payload,
                root=root,
                suite_path=suite_path,
                qemu_path=qemu,
            )
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
