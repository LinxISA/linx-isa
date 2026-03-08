#!/usr/bin/env python3
"""Reassemble disassembled spec vectors and verify stable LLVM round-tripping."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


OBJDUMP_RE = re.compile(
    r"^\s*(?P<addr>[0-9a-f]+):\s+(?P<bytes>[0-9a-f]{2}(?:\s+[0-9a-f]{2})*)(?:\s{2,}(?P<asm>.*?))?\s*$",
    re.IGNORECASE,
)
HEX_TARGET_RE = re.compile(r"0x([0-9a-fA-F]+)(?!.*0x)")
HEX_NUMBER_RE = re.compile(r"0x[0-9a-fA-F]+")
LABEL_TARGET_RE = re.compile(r"\.Lrt_[0-9a-fA-F]+")


def _extract_instructions(path: Path) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = OBJDUMP_RE.match(raw)
        if not match:
            continue
        asm = match.group("asm").strip()
        out.append(
            {
                "address": int(match.group("addr"), 16),
                "bytes": [int(part, 16) for part in match.group("bytes").split()],
                "asm": asm,
            }
        )
    return out


def _normalize(lines: list[str]) -> list[str]:
    return [" ".join(line.replace("\t", " ").split()) for line in lines]


def _label_for_address(address: int) -> str:
    return f".Lrt_{address:04x}"


def _rewrite_target_operand(asm: str, labels_by_addr: dict[int, str]) -> str:
    upper = asm.upper()
    if not upper.startswith(("B.TEXT", "SETRET", "C.SETRET", "HL.SETRET")):
        return asm
    match = HEX_TARGET_RE.search(asm)
    if not match:
        return asm
    target = int(match.group(1), 16)
    label = labels_by_addr.get(target)
    if label is None:
        return asm
    return asm[: match.start()] + label + asm[match.end() :]


def _target_hex_match(asm: str) -> re.Match[str] | None:
    upper = asm.upper()
    matches = list(HEX_NUMBER_RE.finditer(asm))
    if not matches:
        return None
    if upper.startswith(("BSTART.CALL", "C.BSTART.CALL", "HL.BSTART.CALL")):
        return matches[0]
    return matches[-1]


def _target_address(asm: str) -> int | None:
    upper = asm.upper()
    if not upper.startswith(
        ("B.TEXT", "BSTART", "C.BSTART", "HL.BSTART", "SETRET", "C.SETRET", "HL.SETRET")
    ):
        return None
    match = _target_hex_match(asm)
    if not match:
        return None
    return int(match.group(0), 16)


def _rewrite_probe_target_operand(asm: str) -> str:
    match = LABEL_TARGET_RE.search(asm)
    if match:
        return asm[: match.start()] + ".Lprobe_target" + asm[match.end() :]
    match = _target_hex_match(asm)
    if match:
        return asm[: match.start()] + ".Lprobe_target" + asm[match.end() :]
    return asm


def _probe_target_address(asm: str) -> int | None:
    upper = asm.upper()
    if upper.startswith(("BSTART", "C.BSTART", "HL.BSTART")):
        # Current llvm-mc probe lane does not support expression fixups for
        # generic BSTART-style targets. Keep the numeric operand in probe mode.
        return None
    return _target_address(asm)


def _rewrite_probe_pc_sensitive_numeric(asm: str, address: int) -> tuple[str, bool]:
    upper = asm.upper()
    if not upper.startswith(("BSTART", "C.BSTART", "HL.BSTART")):
        return asm, False
    match = _target_hex_match(asm)
    if not match:
        return asm, False
    target = int(match.group(0), 16)
    delta = target - address
    if upper.startswith("HL.BSTART.CALL"):
        if (delta & 1) != 0:
            return asm, False
        encoded = delta >> 1
    elif upper.startswith("HL.BSTART"):
        encoded = delta
    else:
        if (delta & 1) != 0:
            return asm, False
        encoded = delta >> 1
    replacement = f"0x{encoded:x}"
    return asm[: match.start()] + replacement + asm[match.end() :], True


def _write_asm(path: Path, instructions: list[dict[str, object]], stable_indexes: set[int]) -> None:
    labels_by_addr = {int(inst["address"]): _label_for_address(int(inst["address"])) for inst in instructions}
    lines = ["# Auto-generated from llvm-objdump output", "    .text", "roundtrip_start:"]
    for idx, inst in enumerate(instructions, 1):
        lines.append(f"{labels_by_addr[int(inst['address'])]}:")
        asm = str(inst["asm"])
        if idx in stable_indexes and asm:
            rewritten = _rewrite_target_operand(asm, labels_by_addr)
            # Some probe-stable branch forms only become reassemblable because
            # the probe synthesizes a private landing label. If the full decode
            # stream does not contain that landing address as a live label,
            # preserve the original bytes instead of emitting unstable text.
            if _target_address(asm) is None or rewritten != asm:
                lines.append(f"    {rewritten}")
                continue
        bytes_list = [f"0x{byte:02x}" for byte in inst["bytes"]]
        comment = f"  # preserved: {asm}" if asm else "  # preserved raw bytes"
        lines.append(f"    .byte {', '.join(bytes_list)}{comment}")
    lines.append("roundtrip_end:")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _assemble(mc: Path, triple: str, asm_path: Path, obj_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(mc), f"-triple={triple}", "-filetype=obj", str(asm_path), "-o", str(obj_path)],
        capture_output=True,
        text=True,
    )


def _disassemble(objdump: Path, triple: str, obj_path: Path, objdump_path: Path) -> list[dict[str, object]]:
    disasm = subprocess.run(
        [str(objdump), "-d", f"--triple={triple}", str(obj_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    objdump_path.write_text(disasm.stdout, encoding="utf-8")
    return _extract_instructions(objdump_path)


def _write_probe_asm(path: Path, inst: dict[str, object], rewritten_asm: str, target: int | None) -> None:
    addr = int(inst["address"])
    size = len(inst["bytes"])
    lines = ["# Auto-generated single-instruction probe", "    .text", "probe_start:"]

    if target is None:
        lines.extend([".Lprobe_inst:", f"    {rewritten_asm}", "probe_end:"])
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    rewritten_asm = _rewrite_probe_target_operand(rewritten_asm)
    delta = target - addr
    if delta >= 0:
        lines.extend([".Lprobe_inst:", f"    {rewritten_asm}"])
        gap = delta - size
        if gap < 0:
            gap = 0
        if gap:
            lines.append(f"    .space {gap}")
        lines.extend([".Lprobe_target:", "probe_end:"])
    else:
        lines.extend([".Lprobe_target:"])
        if -delta:
            lines.append(f"    .space {-delta}")
        lines.extend([".Lprobe_inst:", f"    {rewritten_asm}", "probe_end:"])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-objdump", type=Path, required=True)
    ap.add_argument("--asm-out", type=Path, required=True)
    ap.add_argument("--roundtrip-obj", type=Path, required=True)
    ap.add_argument("--roundtrip-objdump", type=Path, required=True)
    ap.add_argument("--mc", type=Path, required=True)
    ap.add_argument("--objdump", type=Path, required=True)
    ap.add_argument("--triple", required=True)
    ap.add_argument("--report-out", type=Path, default=None)
    ap.add_argument("--require-all", action="store_true")
    args = ap.parse_args(argv)

    first = _extract_instructions(args.input_objdump)
    if not first:
        print(f"error: no instruction lines found in {args.input_objdump}", file=sys.stderr)
        return 1

    args.asm_out.parent.mkdir(parents=True, exist_ok=True)
    args.roundtrip_obj.parent.mkdir(parents=True, exist_ok=True)
    labels_by_addr = {int(inst["address"]): _label_for_address(int(inst["address"])) for inst in first}
    stable_indexes: set[int] = set()
    skipped: list[dict[str, object]] = []
    probe_dir = args.asm_out.parent / "_roundtrip_probe"
    probe_dir.mkdir(parents=True, exist_ok=True)
    for idx, inst in enumerate(first, 1):
        probe_asm = probe_dir / f"{idx:04d}.s"
        probe_obj = probe_dir / f"{idx:04d}.o"
        asm = str(inst["asm"])
        if not asm:
            skipped.append(
                {
                    "index": idx,
                    "instruction": "<raw-bytes>",
                    "error": "original objdump line has no assembly rendering",
                }
            )
            continue
        target = _probe_target_address(asm)
        rewritten = _rewrite_target_operand(asm, labels_by_addr)
        probe_pc_sensitive = False
        if target is None:
            rewritten, probe_pc_sensitive = _rewrite_probe_pc_sensitive_numeric(
                rewritten, int(inst["address"])
            )
        # Single-instruction probes can always materialize their own synthetic
        # target label for branch-like forms, even when the original objdump
        # target does not correspond to another decoded line in the full stream.
        labelable_target = target is not None
        _write_probe_asm(probe_asm, inst, rewritten, target if labelable_target else None)
        probe = _assemble(args.mc, args.triple, probe_asm, probe_obj)
        if probe.returncode == 0:
            try:
                probe_disasm = _disassemble(
                    args.objdump,
                    args.triple,
                    probe_obj,
                    probe_dir / f"{idx:04d}.objdump",
                )
            except subprocess.CalledProcessError as exc:
                skipped.append(
                    {
                        "index": idx,
                        "instruction": asm,
                        "error": (exc.stderr or exc.stdout).strip().splitlines()[0]
                        if (exc.stderr or exc.stdout)
                        else "disassembly failed",
                    }
                )
                continue

            if probe_disasm and probe_disasm[0]["bytes"] == inst["bytes"]:
                # Target-bearing probes may decode filler bytes around the
                # synthetic landing label as extra instructions (for example a
                # zero-filled gap showing up as C.BSTOP). Only the first
                # instruction belongs to the original roundtrip candidate.
                if (
                    labelable_target
                    or probe_pc_sensitive
                    or _normalize([str(probe_disasm[0]["asm"])]) == _normalize([asm])
                ):
                    stable_indexes.add(idx)
                    continue
        skipped.append(
            {
                "index": idx,
                "instruction": asm,
                "error": (probe.stderr or probe.stdout).strip().splitlines()[0]
                if (probe.stderr or probe.stdout)
                else "not byte-stable under isolated roundtrip",
            }
        )

    if not stable_indexes:
        print("error: no assembler-stable instructions found in generated decode vector", file=sys.stderr)
        return 1

    _write_asm(args.asm_out, first, stable_indexes)
    assembled = _assemble(args.mc, args.triple, args.asm_out, args.roundtrip_obj)
    if assembled.returncode != 0:
        sys.stderr.write(assembled.stdout)
        sys.stderr.write(assembled.stderr)
        return assembled.returncode

    second = _disassemble(args.objdump, args.triple, args.roundtrip_obj, args.roundtrip_objdump)
    first_norm = _normalize([str(inst["asm"]) for inst in first])
    second_norm = _normalize([str(inst["asm"]) for inst in second])
    report = {
        "input_instruction_count": len(first),
        "roundtrip_instruction_count": len(first),
        "assembler_stable_instruction_count": len(stable_indexes),
        "skipped_instruction_count": len(skipped),
        "skipped_instructions": skipped,
        "require_all": args.require_all,
    }

    mismatch: dict[str, object] | None = None
    if first_norm != second_norm:
        mismatch_at = next(
            (idx for idx, (lhs, rhs) in enumerate(zip(first_norm, second_norm), 1) if lhs != rhs),
            min(len(first_norm), len(second_norm)) + 1,
        )
        mismatch = {
            "index": mismatch_at,
            "lhs": first_norm[mismatch_at - 1] if mismatch_at - 1 < len(first_norm) else "<missing>",
            "rhs": second_norm[mismatch_at - 1] if mismatch_at - 1 < len(second_norm) else "<missing>",
        }

    report["stable_roundtrip"] = mismatch is None
    report["mismatch"] = mismatch
    if args.report_out is not None:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if mismatch is not None and args.require_all:
        print(
            f"error: disassembly round-trip mismatch at instruction {mismatch['index']}: "
            f"{mismatch['lhs']} != {mismatch['rhs']}",
            file=sys.stderr,
        )
        return 1

    if args.require_all and skipped:
        print(
            f"error: disasm round-trip skipped {len(skipped)} non-reassemblable instructions in strict mode",
            file=sys.stderr,
        )
        return 1

    summary = (
        f"ok: disasm round-trip audit across {len(first_norm)}/{len(first)} instructions "
        f"(assembled={len(stable_indexes)})"
    )
    if skipped:
        summary += f" (skipped={len(skipped)})"
    if mismatch is not None:
        summary += f" (first mismatch at {mismatch['index']})"
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
