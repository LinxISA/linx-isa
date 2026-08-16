#!/usr/bin/env python3
"""Refresh audited QEMU L2/L3 executable evidence without overwriting old bundles.

The static test/oracle mapping remains reviewer-owned in the template manifest.
This tool owns the dynamic binding: clean QEMU SHA, fresh ELF/object offsets,
exact PC-watch runs, run digests, and atomic publication of the validated ledger.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shlex
import struct
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
REPO_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(SCRIPT.parent))

import report_qemu_executable_coverage as reporter  # noqa: E402


EVIDENCE_ROOT = Path("docs/bringup/gates/evidence/qemu-executable")
ACTIVE_RELEASE = "0.58.1"
SUITE_PREFIXES = {
    "callret": "callret",
    "executable_memory": "executable-memory",
    "executable_scalar": "executable-scalar",
    "executable_integer": "executable-integer",
    "v057_vector_ops": "v057-vector-ops",
    "atomic": "atomic-lr-srczero",
    "executable_setc_imm": "executable-setc-imm",
    "executable_maddw_bfi_mi": "executable-maddw-bfi-mi",
}
SUITE_ORDER = tuple(SUITE_PREFIXES)
RUN_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


@dataclass(frozen=True)
class Section:
    kind: int
    address: int
    offset: int
    size: int
    link: int
    entry_size: int


@dataclass(frozen=True)
class Symbol:
    value: int
    size: int
    section_index: int


class Elf64:
    """Small, strict little-endian ELF64 reader for evidence rebinding."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = path.read_bytes()
        if len(self.data) < 64 or self.data[:6] != b"\x7fELF\x02\x01":
            raise ValueError(f"expected little-endian ELF64: {path}")
        header = struct.unpack_from("<16sHHIQQQIHHHHHH", self.data, 0)
        self.elf_type = header[1]
        self.program_offset = header[5]
        self.section_offset = header[6]
        self.program_entry_size = header[9]
        self.program_count = header[10]
        self.section_entry_size = header[11]
        self.section_count = header[12]
        if self.section_entry_size < 64:
            raise ValueError(f"invalid ELF section table: {path}")
        self.sections = self._read_sections()
        self.symbols = self._read_symbols()

    def _read_sections(self) -> list[Section]:
        sections: list[Section] = []
        for index in range(self.section_count):
            offset = self.section_offset + index * self.section_entry_size
            if offset + 64 > len(self.data):
                raise ValueError(f"truncated ELF section table: {self.path}")
            raw = struct.unpack_from("<IIQQQQIIQQ", self.data, offset)
            sections.append(
                Section(
                    kind=raw[1],
                    address=raw[3],
                    offset=raw[4],
                    size=raw[5],
                    link=raw[6],
                    entry_size=raw[9],
                )
            )
        return sections

    def _read_symbols(self) -> dict[str, list[Symbol]]:
        symbols: dict[str, list[Symbol]] = {}
        for section in self.sections:
            if section.kind != 2 or not section.entry_size:
                continue
            if section.link >= len(self.sections):
                raise ValueError(f"invalid ELF symbol string table: {self.path}")
            strings_section = self.sections[section.link]
            strings = self.data[
                strings_section.offset : strings_section.offset + strings_section.size
            ]
            for offset in range(
                section.offset, section.offset + section.size, section.entry_size
            ):
                if offset + 24 > len(self.data):
                    raise ValueError(f"truncated ELF symbol table: {self.path}")
                name_offset, _, _, section_index, value, size = struct.unpack_from(
                    "<IBBHQQ", self.data, offset
                )
                if name_offset >= len(strings):
                    continue
                end = strings.find(b"\0", name_offset)
                if end < 0:
                    continue
                name = strings[name_offset:end].decode("utf-8", errors="replace")
                if name and size:
                    symbols.setdefault(name, []).append(
                        Symbol(value=value, size=size, section_index=section_index)
                    )
        return symbols

    def symbol(self, name: str) -> Symbol:
        candidates = self.symbols.get(name, [])
        distinct = {(item.value, item.size, item.section_index) for item in candidates}
        if len(distinct) != 1:
            raise ValueError(
                f"symbol {name!r} is absent or ambiguous in {self.path}"
            )
        value, size, section_index = next(iter(distinct))
        return Symbol(value=value, size=size, section_index=section_index)

    def virtual_file_offset(self, address: int, size: int) -> int:
        if self.program_entry_size < 56:
            raise ValueError(f"invalid ELF program table: {self.path}")
        for index in range(self.program_count):
            offset = self.program_offset + index * self.program_entry_size
            if offset + 56 > len(self.data):
                raise ValueError(f"truncated ELF program table: {self.path}")
            kind, _, file_offset, virtual, _, file_size, _, _ = struct.unpack_from(
                "<IIQQQQQQ", self.data, offset
            )
            if kind == 1 and virtual <= address and address + size <= virtual + file_size:
                return file_offset + address - virtual
        raise ValueError(f"address 0x{address:x} is outside ELF PT_LOAD ranges")

    def symbol_file_offset(self, symbol: Symbol, relative: int, size: int) -> int:
        if relative < 0 or relative + size > symbol.size:
            raise ValueError("instruction is outside its object symbol")
        if symbol.section_index <= 0 or symbol.section_index >= len(self.sections):
            raise ValueError("object symbol has no file-backed section")
        section = self.sections[symbol.section_index]
        offset = section.offset + symbol.value + relative
        if offset + size > section.offset + section.size or offset + size > len(self.data):
            raise ValueError("object symbol instruction is outside its section")
        return offset


def _run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    print("+", shlex.join(command), flush=True)
    completed = subprocess.run(command, cwd=cwd, env=env, check=False)
    if completed.returncode:
        raise RuntimeError(
            f"command failed with exit status {completed.returncode}: {shlex.join(command)}"
        )


def _capture(command: list[str], *, cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode:
        raise ValueError(completed.stderr.strip() or shlex.join(command))
    return completed.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_relative(repo_root: Path, path: Path) -> str:
    absolute = path if path.is_absolute() else repo_root / path
    resolved = absolute.resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"path must remain inside the repository: {path}") from exc
    lexical_root = Path(os.path.abspath(repo_root))
    return Path(os.path.abspath(absolute)).relative_to(lexical_root).as_posix()


def _require_clean_git(path: Path, label: str) -> str:
    head = _capture(["git", "rev-parse", "HEAD"], cwd=path)
    if re.fullmatch(r"[0-9a-f]{40}", head) is None:
        raise ValueError(f"invalid {label} HEAD: {head}")
    dirty = _capture(["git", "status", "--porcelain", "--untracked-files=no"], cwd=path)
    if dirty:
        raise ValueError(f"{label} source is dirty")
    return head


def _git_head_and_dirty(path: Path, label: str) -> tuple[str, bool]:
    head = _capture(["git", "rev-parse", "HEAD"], cwd=path)
    if re.fullmatch(r"[0-9a-f]{40}", head) is None:
        raise ValueError(f"invalid {label} HEAD: {head}")
    dirty = bool(
        _capture(["git", "status", "--porcelain", "--untracked-files=no"], cwd=path)
    )
    return head, dirty


def _parse_int(value: object, field: str) -> int:
    try:
        if isinstance(value, bool):
            raise ValueError
        return value if isinstance(value, int) else int(str(value), 0)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {field}") from exc


def _suite_entries(
    manifest: dict[str, Any],
    *,
    require_all_suites: bool = True,
) -> dict[str, list[dict[str, Any]]]:
    entries = manifest.get("evidence")
    if not isinstance(entries, list) or not entries:
        raise ValueError("manifest.evidence must be a non-empty array")
    grouped = {suite: [] for suite in SUITE_ORDER}
    form_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("manifest evidence entries must be objects")
        suite = entry.get("suite")
        if suite not in grouped:
            raise ValueError(f"unsupported executable evidence suite: {suite}")
        form_id = entry.get("form_id")
        if not isinstance(form_id, str) or form_id in form_ids:
            raise ValueError(f"missing or duplicate form_id: {form_id}")
        form_ids.add(form_id)
        grouped[suite].append(entry)
    if require_all_suites and any(not grouped[suite] for suite in SUITE_ORDER):
        raise ValueError("manifest must contain all executable evidence suites")
    if any(len(grouped[suite]) > 16 for suite in SUITE_ORDER):
        raise ValueError("a suite exceeds QEMU's 16-PC watch limit")
    grouped = {suite: items for suite, items in grouped.items() if items}
    return grouped


def _select_candidate(old_relative: int | None, candidates: list[int], identity: str) -> int:
    unique = sorted(set(candidates))
    if old_relative is not None and old_relative in unique:
        return old_relative
    if len(unique) == 1:
        return unique[0]
    if not unique:
        raise ValueError(f"no fresh encoding candidate for {identity}")
    raise ValueError(f"ambiguous fresh encoding candidates for {identity}: {unique}")


def _mnemonic_matches(disassembly: str, mnemonic: str) -> bool:
    normalized = reporter._normalize_disassembly(disassembly)
    expected = mnemonic.strip().lower()
    return normalized == expected or normalized.startswith(expected + " ")


def _resolve_entry(
    *,
    repo_root: Path,
    old_entry: dict[str, Any],
    new_elf_path: Path,
    new_object_path: Path,
) -> dict[str, str]:
    instruction = old_entry.get("instruction")
    form_key = old_entry.get("form_key")
    if not isinstance(instruction, dict) or not isinstance(form_key, dict):
        raise ValueError("entry lacks instruction/form_key")
    symbol_name = instruction.get("symbol")
    if not isinstance(symbol_name, str) or not symbol_name:
        raise ValueError("entry lacks instruction symbol")
    size = (_parse_int(form_key.get("length_bits"), "length_bits") + 7) // 8
    mask = _parse_int(form_key.get("mask"), "mask")
    match = _parse_int(form_key.get("match"), "match")
    old_relative: int | None = None
    old_elf_path = repo_root / str(old_entry["elf"])
    if old_elf_path.is_file():
        old_elf = Elf64(old_elf_path)
        old_symbol = old_elf.symbol(symbol_name)
        old_pc = _parse_int(instruction.get("pc"), "instruction.pc")
        old_relative = old_pc - old_symbol.value

    new_elf = Elf64(new_elf_path)
    new_symbol = new_elf.symbol(symbol_name)
    if old_relative is None:
        try:
            old_pc = _parse_int(instruction.get("pc"), "instruction.pc")
            pc_relative = old_pc - new_symbol.value
            if 0 <= pc_relative <= new_symbol.size - size:
                old_relative = pc_relative
        except ValueError:
            pass
    candidates: list[int] = []
    for relative in range(0, new_symbol.size - size + 1, 2):
        pc = new_symbol.value + relative
        elf_offset = new_elf.virtual_file_offset(pc, size)
        raw = new_elf.data[elf_offset : elf_offset + size]
        if int.from_bytes(raw, "little") & mask != match:
            continue
        binding = reporter._inspect_elf_instruction(
            repo_root, new_elf_path, pc=pc, size=size, symbol=symbol_name
        )
        if _mnemonic_matches(binding["disassembly"], str(old_entry["mnemonic"])):
            candidates.append(relative)
    identity = str(old_entry.get("form_id"))
    relative = _select_candidate(old_relative, candidates, identity)
    pc = new_symbol.value + relative
    binding = reporter._inspect_elf_instruction(
        repo_root, new_elf_path, pc=pc, size=size, symbol=symbol_name
    )
    raw = binding["raw_bytes"]
    if int.from_bytes(raw, "little") & mask != match:
        raise ValueError(f"fresh bytes do not match golden encoding for {identity}")

    new_object = Elf64(new_object_path)
    object_symbol = new_object.symbol(symbol_name)
    object_offset = new_object.symbol_file_offset(object_symbol, relative, size)
    if new_object.data[object_offset : object_offset + size] != raw:
        raise ValueError(f"object/ELF bytes disagree for {identity}")
    return {
        "raw_bytes_le": raw.hex(),
        "disassembly": binding["disassembly"],
        "object_offset": f"0x{object_offset:x}",
        "elf_offset": f"0x{binding['elf_offset']:x}",
        "pc": f"0x{pc:016x}",
        "symbol": symbol_name,
    }


def _artifact_paths(run: dict[str, Any]) -> list[str]:
    artifacts = run.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("run evidence lacks artifacts")
    records: list[object] = [artifacts.get("elf"), artifacts.get("object")]
    objects = artifacts.get("objects")
    if not isinstance(objects, list):
        raise ValueError("run evidence lacks per-source objects")
    records.extend(objects)
    for key in ("pc_watch", "uart"):
        records.append(artifacts.get(key))
    paths: list[str] = []
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise ValueError("run evidence contains an invalid artifact record")
        paths.append(record["path"])
    return paths


def _check_bundle_artifacts(repo_root: Path, bundle: Path, run_path: Path) -> None:
    run = json.loads(run_path.read_text(encoding="utf-8"))
    bundle_resolved = bundle.resolve()
    for value in _artifact_paths(run):
        relative = Path(value)
        if relative.is_absolute():
            raise ValueError(f"artifact path is absolute: {value}")
        resolved = (repo_root / relative).resolve()
        try:
            resolved.relative_to(bundle_resolved)
        except ValueError as exc:
            raise ValueError(f"artifact escapes its evidence bundle: {value}") from exc
        if not resolved.is_file():
            raise ValueError(f"artifact is missing: {value}")


def _tool_paths(repo_root: Path, args: argparse.Namespace) -> dict[str, Path]:
    llvm_bin = repo_root / "compiler/llvm/build-linxisa-clang/bin"
    defaults = {
        "clang": llvm_bin / "clang",
        "clangxx": llvm_bin / "clang++",
        "lld": llvm_bin / "ld.lld",
        "llvm_objdump": llvm_bin / "llvm-objdump",
        "llc": llvm_bin / "llc",
    }
    tools: dict[str, Path] = {}
    for name, default in defaults.items():
        selected = Path(getattr(args, name) or default)
        if not selected.is_absolute():
            selected = repo_root / selected
        if not selected.is_file() or not os.access(selected, os.X_OK):
            raise ValueError(f"missing executable {name}: {selected}")
        tools[name] = selected
    return tools


def _command_path(repo_root: Path, path: Path) -> str:
    try:
        return _repo_relative(repo_root, path)
    except ValueError:
        return str(path)


def _runner_command(
    *,
    repo_root: Path,
    suite: str,
    bundle: Path,
    qemu: Path,
    tools: dict[str, Path],
    timeout: float,
    test_ids: list[int],
    pcs: list[int] | None,
) -> list[str]:
    command = [
        sys.executable,
        str(repo_root / "avs/qemu/run_tests.py"),
        "--suite",
        suite,
        "--out-dir",
        _repo_relative(repo_root, bundle),
        "--qemu",
        _repo_relative(repo_root, qemu),
        "--clang",
        _command_path(repo_root, tools["clang"]),
        "--clangxx",
        _command_path(repo_root, tools["clangxx"]),
        "--lld",
        _command_path(repo_root, tools["lld"]),
        "--llvm-objdump",
        _command_path(repo_root, tools["llvm_objdump"]),
        "--llc",
        _command_path(repo_root, tools["llc"]),
        "--timeout",
        str(timeout),
    ]
    for test_id in test_ids:
        command.extend(["--require-test-id", f"0x{test_id:08x}"])
    if pcs is None:
        return [*command, "--prepare-only"]
    run_path = bundle / "run-evidence.json"
    command.extend(["--evidence-out", _repo_relative(repo_root, run_path)])
    for pc in pcs:
        command.extend(["--evidence-pc", f"0x{pc:016x}"])
    return command


def _portable_command(repo_root: Path, command: list[str]) -> str:
    portable = list(command)
    portable[0] = "python3"
    portable[1] = _repo_relative(repo_root, Path(portable[1]))
    return shlex.join(portable)


def _atomic_write(path: Path, data: bytes) -> None:
    temporary = path.with_name(path.name + ".refresh-tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--run-id", required=True, help="Unique suffix, e.g. ca3e11b-20260717-r1")
    parser.add_argument("--qemu-root", type=Path, default=Path("emulator/qemu"))
    parser.add_argument("--qemu", type=Path, required=True)
    parser.add_argument("--clang", type=Path)
    parser.add_argument("--clangxx", type=Path)
    parser.add_argument("--lld", type=Path)
    parser.add_argument("--llvm-objdump", dest="llvm_objdump", type=Path)
    parser.add_argument("--llc", type=Path)
    parser.add_argument("--llvm-root", type=Path, default=Path("compiler/llvm"))
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create bundles and publish the validated manifest/reports. Default is preflight only.",
    )
    parser.add_argument(
        "--allow-partial-manifest",
        action="store_true",
        help="Allow a manifest containing only the suites present in its evidence list.",
    )
    parser.add_argument(
        "--prune-generated-artifacts",
        action="store_true",
        help="After strict validation and publication, remove generated ELF/object/linker files from evidence bundles.",
    )
    parser.add_argument(
        "--allow-dirty-llvm-tools",
        action="store_true",
        help="Allow dirty LLVM tool source when using existing compiler binaries; QEMU source must still be clean.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    if RUN_ID_RE.fullmatch(args.run_id) is None:
        raise SystemExit("error: --run-id must use lowercase letters, digits, dot, dash, or underscore")
    if args.timeout <= 0:
        raise SystemExit("error: --timeout must be positive")
    manifest_path = (args.manifest or repo_root / "avs/qemu/qemu_executable_coverage_manifest.json").resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("active_release") is not True or manifest.get("release") != ACTIVE_RELEASE:
        raise SystemExit(
            "error: executable coverage manifest is archival; provide an active "
            f"{ACTIVE_RELEASE} --manifest template"
        )
    grouped = _suite_entries(manifest, require_all_suites=not args.allow_partial_manifest)

    qemu_root = (args.qemu_root if args.qemu_root.is_absolute() else repo_root / args.qemu_root).resolve()
    qemu = (args.qemu if args.qemu.is_absolute() else repo_root / args.qemu).resolve()
    try:
        qemu_relative = qemu.relative_to(qemu_root)
    except ValueError as exc:
        raise SystemExit("error: --qemu must be under emulator/qemu/build*") from exc
    if (
        not qemu_relative.parts
        or not qemu_relative.parts[0].startswith("build")
        or qemu.name != "qemu-system-linx64"
        or not qemu.is_file()
    ):
        raise SystemExit("error: --qemu must name emulator/qemu/build*/qemu-system-linx64")
    qemu_sha = _require_clean_git(qemu_root, "QEMU")
    llvm_root = (args.llvm_root if args.llvm_root.is_absolute() else repo_root / args.llvm_root).resolve()
    llvm_sha, llvm_dirty = _git_head_and_dirty(llvm_root, "LLVM")
    if llvm_dirty and not args.allow_dirty_llvm_tools:
        raise ValueError("LLVM source is dirty; pass --allow-dirty-llvm-tools to use existing compiler binaries")
    tools = _tool_paths(repo_root, args)
    os.environ["PATH"] = (
        str(tools["llvm_objdump"].parent) + os.pathsep + os.environ.get("PATH", "")
    )

    evidence_root = (repo_root / EVIDENCE_ROOT).resolve()
    bundles = {
        suite: evidence_root / f"{SUITE_PREFIXES[suite]}-{args.run_id}"
        for suite in grouped
    }
    existing = [str(path) for path in bundles.values() if path.exists()]
    if existing:
        raise SystemExit("error: refusing to overwrite evidence bundles: " + ", ".join(existing))

    print(
        f"preflight: QEMU={qemu_sha} LLVM={llvm_sha} "
        f"llvm_dirty={llvm_dirty} forms={sum(map(len, grouped.values()))}"
    )
    for suite in grouped:
        print(f"preflight: {suite}: forms={len(grouped[suite])} bundle={bundles[suite].relative_to(repo_root)}")
    if not args.apply:
        print("preflight complete; rerun with --apply to create and publish evidence")
        return 0

    candidate = copy.deepcopy(manifest)
    candidate_grouped = _suite_entries(
        candidate,
        require_all_suites=not args.allow_partial_manifest,
    )
    suite_commands: list[str] = []
    pc_deltas: list[dict[str, str]] = []
    env = os.environ.copy()
    env["LINX_VIRT_TEST_FINISHER"] = "1"
    for suite in grouped:
        bundle = bundles[suite]
        bundle.mkdir(parents=True, exist_ok=False)
        test_ids = sorted({_parse_int(entry["test_id"], "test_id") for entry in grouped[suite]})
        prepare = _runner_command(
            repo_root=repo_root,
            suite=suite,
            bundle=bundle,
            qemu=qemu,
            tools=tools,
            timeout=args.timeout,
            test_ids=test_ids,
            pcs=None,
        )
        _run(prepare, cwd=repo_root, env=env)
        new_elf = bundle / "linx-qemu-tests.elf"
        resolved: list[dict[str, str]] = []
        for old_entry in grouped[suite]:
            object_name = Path(str(old_entry["object"])).name
            binding = _resolve_entry(
                repo_root=repo_root,
                old_entry=old_entry,
                new_elf_path=new_elf,
                new_object_path=bundle / "obj" / object_name,
            )
            resolved.append(binding)
            pc_deltas.append(
                {
                    "form_id": str(old_entry["form_id"]),
                    "old_pc": str(old_entry["instruction"]["pc"]),
                    "new_pc": binding["pc"],
                }
            )
        pcs = [_parse_int(binding["pc"], "pc") for binding in resolved]
        if len(set(pcs)) != len(pcs):
            raise ValueError(f"suite {suite} resolves multiple forms to one PC")
        runtime = _runner_command(
            repo_root=repo_root,
            suite=suite,
            bundle=bundle,
            qemu=qemu,
            tools=tools,
            timeout=args.timeout,
            test_ids=test_ids,
            pcs=pcs,
        )
        _run(runtime, cwd=repo_root, env=env)
        (bundle / "linx-qemu-tests-directboot.ld").unlink(missing_ok=True)
        suite_commands.append(
            "LINX_VIRT_TEST_FINISHER=1 " + _portable_command(repo_root, runtime)
        )
        run_path = bundle / "run-evidence.json"
        _check_bundle_artifacts(repo_root, bundle, run_path)
        run_digest = _sha256(run_path)
        for old_entry, new_entry, expected_binding in zip(
            grouped[suite], candidate_grouped[suite], resolved, strict=True
        ):
            object_name = Path(str(old_entry["object"])).name
            final_binding = _resolve_entry(
                repo_root=repo_root,
                old_entry=old_entry,
                new_elf_path=new_elf,
                new_object_path=bundle / "obj" / object_name,
            )
            if final_binding != expected_binding:
                raise ValueError(f"non-deterministic rebuild changed {old_entry['form_id']}")
            new_entry["elf"] = _repo_relative(repo_root, new_elf)
            new_entry["object"] = _repo_relative(repo_root, bundle / "obj" / object_name)
            new_entry["instruction"] = final_binding
            new_entry["qemu_sha"] = qemu_sha
            new_entry["run_evidence"] = _repo_relative(repo_root, run_path)
            new_entry["run_evidence_sha256"] = run_digest

    candidate["producer"] = {
        "refresh_command": "python3 tools/bringup/refresh_qemu_executable_coverage.py "
        f"--run-id {args.run_id} --qemu-root {_repo_relative(repo_root, qemu_root)} "
        f"--qemu {_repo_relative(repo_root, qemu)} --llvm-root {_command_path(repo_root, llvm_root)} --apply",
        "suite_commands": suite_commands,
        "qemu_sha": qemu_sha,
        "llvm_sha": llvm_sha,
        "llvm_source_dirty": llvm_dirty,
        "bundle_policy": "Never overwrite old evidence bundles; publish only after all selected suites pass strict validation.",
        "report_command": "python3 tools/bringup/report_qemu_executable_coverage.py --require-nonzero --require-clean",
    }
    candidate_bytes = (json.dumps(candidate, indent=2) + "\n").encode()
    candidate_manifest = manifest_path.with_name(manifest_path.name + ".refresh-candidate")
    candidate_manifest.write_bytes(candidate_bytes)
    try:
        report = reporter.build_report(
            repo_root=repo_root,
            spec_path=repo_root / "isa/v0.58/linxisa-v0.58.json",
            manifest_path=candidate_manifest,
            current_qemu_sha=qemu_sha,
            qemu_root=qemu_root,
        )
    finally:
        candidate_manifest.unlink(missing_ok=True)
    expected_count = len(candidate["evidence"])
    l2 = report["evidence"]["L2"]["form_count"]
    l3 = report["evidence"]["L3"]["form_count"]
    if report["rejected"] or l2 != expected_count or l3 != expected_count:
        raise ValueError(
            f"strict validation failed: L2={l2} L3={l3} rejected={len(report['rejected'])}"
        )

    report_json = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    report_markdown = reporter._render_markdown(report).encode()
    _atomic_write(manifest_path, candidate_bytes)
    _atomic_write(repo_root / "docs/bringup/gates/qemu_executable_coverage_latest.json", report_json)
    _atomic_write(repo_root / "docs/bringup/gates/qemu_executable_coverage_latest.md", report_markdown)
    summary_path = evidence_root / f"refresh-{args.run_id}.json"
    changed_pcs = [row for row in pc_deltas if row["old_pc"] != row["new_pc"]]
    _atomic_write(
        summary_path,
        (
            json.dumps(
                {
                    "qemu_sha": qemu_sha,
                    "llvm_sha": llvm_sha,
                    "form_count": len(pc_deltas),
                    "unchanged_pc_count": len(pc_deltas) - len(changed_pcs),
                    "pc_changes": changed_pcs,
                },
                indent=2,
            )
            + "\n"
        ).encode(),
    )
    if args.prune_generated_artifacts:
        for suite in grouped:
            bundle = bundles.get(suite)
            if bundle is None or not bundle.exists():
                continue
            for pattern in (
                "linx-qemu-tests.elf",
                "linx-qemu-tests.o",
                "linx-qemu-tests-directboot.ld",
                "obj/*.o",
                "obj/*.s",
            ):
                for path in bundle.glob(pattern):
                    path.unlink()
            obj_dir = bundle / "obj"
            if obj_dir.exists() and not any(obj_dir.iterdir()):
                obj_dir.rmdir()
    print(f"published: L2={l2} L3={l3} rejected=0 summary={summary_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
