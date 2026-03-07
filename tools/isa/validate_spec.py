#!/usr/bin/env python3
"""
Validate basic invariants of the compiled ISA JSON spec.

This is intentionally lightweight and does not attempt to validate semantics.
It checks that the derived `encoding` view is internally consistent with the
raw `parts[].segments` view.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from typing import Any, Dict, List, Tuple


def _parse_hex(s: str) -> int:
    s = s.strip().lower()
    if not s.startswith("0x"):
        raise ValueError(f"expected hex string, got {s!r}")
    return int(s, 16)


def _mask_for_width(width_bits: int) -> int:
    return (1 << width_bits) - 1 if width_bits > 0 else 0


def _pattern_to_mask_match(pattern: str) -> Tuple[int, int]:
    # pattern is MSB->LSB with '0','1','.'
    width_bits = len(pattern)
    mask = 0
    match = 0
    for i, ch in enumerate(pattern):
        bit = width_bits - 1 - i  # convert to bit index
        if ch == ".":
            continue
        if ch not in ("0", "1"):
            raise ValueError(f"invalid pattern char {ch!r}")
        mask |= 1 << bit
        if ch == "1":
            match |= 1 << bit
    return mask, match


def _parse_selector(value: Any, *, ctx: str) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip(), 0)
        except ValueError as exc:
            raise ValueError(f"{ctx}: invalid tile opcode value {value!r}") from exc
    raise ValueError(f"{ctx}: invalid tile opcode value {value!r}")


def _validate_tepl_packing(
    tepl: Dict[str, Any], selector_by_name: Dict[str, int], errors: List[str]
) -> None:
    packing = tepl.get("packing")
    if packing is None:
        return
    if not isinstance(packing, dict):
        errors.append("state.engine_ops.tepl.packing must be a mapping")
        return

    if packing.get("kind") != "mode_function_u6":
        errors.append("state.engine_ops.tepl.packing.kind must be mode_function_u6")

    if packing.get("reserved_high_bits_zero") is not True:
        errors.append("state.engine_ops.tepl.packing.reserved_high_bits_zero must be true")

    if packing.get("mode_field_bits") != [5, 5]:
        errors.append("state.engine_ops.tepl.packing.mode_field_bits must be [5, 5]")

    if packing.get("function_field_bits") != [0, 4]:
        errors.append("state.engine_ops.tepl.packing.function_field_bits must be [0, 4]")

    modes = packing.get("modes")
    if not isinstance(modes, list):
        errors.append("state.engine_ops.tepl.packing.modes must be a list")
        return

    expected_by_name: Dict[str, int] = {}
    for idx, mode_entry in enumerate(modes):
        ctx = f"state.engine_ops.tepl.packing.modes[{idx}]"
        if not isinstance(mode_entry, dict):
            errors.append(f"{ctx} must be an object")
            continue

        mode = mode_entry.get("mode")
        if not isinstance(mode, int) or not 0 <= mode <= 1:
            errors.append(f"{ctx}.mode must be an integer in range 0..1")
            continue

        function_names = mode_entry.get("function_names")
        if not isinstance(function_names, list):
            errors.append(f"{ctx}.function_names must be a list")
            continue
        if len(function_names) > 32:
            errors.append(f"{ctx}.function_names must not exceed 32 entries")
            continue

        for function, raw_name in enumerate(function_names):
            if not isinstance(raw_name, str) or not raw_name.strip():
                errors.append(f"{ctx}.function_names[{function}] must be a non-empty string")
                continue
            name = raw_name.strip()
            selector = (mode << 5) | function
            prev = expected_by_name.get(name)
            if prev is not None and prev != selector:
                errors.append(
                    f"state.engine_ops.tepl.packing assigns {name} to both 0x{prev:03X} and 0x{selector:03X}"
                )
                continue
            expected_by_name[name] = selector

        reserved = mode_entry.get("reserved_function_range")
        if reserved is not None:
            if (
                not isinstance(reserved, list)
                or len(reserved) != 2
                or not all(isinstance(v, int) for v in reserved)
                or not 0 <= reserved[0] <= reserved[1] <= 31
            ):
                errors.append(f"{ctx}.reserved_function_range must be [lo, hi] within 0..31")

    for name, selector in sorted(expected_by_name.items()):
        got = selector_by_name.get(name)
        if got is None:
            errors.append(f"state.engine_ops.tepl: packing requires {name}=0x{selector:03X}, but the op is missing")
            continue
        if got != selector:
            errors.append(
                f"state.engine_ops.tepl: {name}=0x{got:03X} does not match packed selector 0x{selector:03X}"
            )

    for name, selector in sorted(selector_by_name.items()):
        if selector > 0x03F:
            errors.append(
                f"state.engine_ops.tepl: {name}=0x{selector:03X} uses reserved high tile-opcode bits outside the packed v0.4 profile"
            )
        if name not in expected_by_name:
            errors.append(
                f"state.engine_ops.tepl: {name}=0x{selector:03X} is not described by the packed TEPL allocation table"
            )


def _validate_engine_ops(spec: Dict[str, Any], errors: List[str]) -> None:
    state = spec.get("state")
    if not isinstance(state, dict):
        return

    engine_ops = state.get("engine_ops")
    if engine_ops is None:
        return
    if not isinstance(engine_ops, dict):
        errors.append("state.engine_ops must be a mapping")
        return

    tepl = engine_ops.get("tepl")
    if tepl is None:
        return
    if not isinstance(tepl, dict):
        errors.append("state.engine_ops.tepl must be a mapping")
        return

    ops = tepl.get("ops")
    if not isinstance(ops, list):
        errors.append("state.engine_ops.tepl.ops must be a list")
        return

    names_by_selector: Dict[int, List[str]] = defaultdict(list)
    selector_by_name: Dict[str, int] = {}
    for idx, op in enumerate(ops):
        ctx = f"state.engine_ops.tepl.ops[{idx}]"
        if not isinstance(op, dict):
            errors.append(f"{ctx} must be an object")
            continue
        name = op.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{ctx}: missing non-empty name")
            continue
        raw_selector = op.get("tile_opcode")
        try:
            selector = _parse_selector(raw_selector, ctx=ctx)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not 0 <= selector <= 0x3FF:
            errors.append(f"{ctx}: tile opcode {selector} out of range 0..1023")
            continue
        names_by_selector[selector].append(name.strip())
        selector_by_name[name.strip()] = selector

    for selector, names in sorted(names_by_selector.items()):
        unique_names = sorted(set(names))
        if len(unique_names) > 1:
            rendered = ", ".join(unique_names)
            errors.append(f"state.engine_ops.tepl: duplicate tile opcode 0x{selector:03X} shared by {rendered}")

    _validate_tepl_packing(tepl, selector_by_name, errors)


def validate(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    errors: List[str] = []

    # ---------------------------------------------------------------------
    # v0.2 bring-up profile sanity checks (system/privileged contract)
    # ---------------------------------------------------------------------
    version = str(spec.get("version", "")).strip()
    if version == "0.2":
        state = spec.get("state", {})
        sysregs = state.get("system_registers")
        if not isinstance(sysregs, dict):
            errors.append("v0.2: missing state.system_registers (expected dict)")
        else:
            legacy = {"EBPC_ACRn", "ETPC_ACRn", "EBPCN_ACRn"}

            def _walk_names(obj: Any) -> List[str]:
                out: List[str] = []
                if isinstance(obj, dict):
                    n = obj.get("name")
                    if isinstance(n, str):
                        out.append(n)
                    fmt = obj.get("name_fmt")
                    if isinstance(fmt, str):
                        out.append(fmt)
                    for v in obj.values():
                        out.extend(_walk_names(v))
                elif isinstance(obj, list):
                    for it in obj:
                        out.extend(_walk_names(it))
                return out

            names = set(_walk_names(sysregs))
            for bad in sorted(legacy):
                if bad in names:
                    errors.append(f"v0.2: forbidden legacy SSR name present in system_registers: {bad}")

            ebarg = sysregs.get("ebarg_group") or {}
            if not isinstance(ebarg, dict):
                errors.append("v0.2: system_registers.ebarg_group missing/invalid")

    _validate_engine_ops(spec, errors)

    for inst in spec.get("instructions", []):
        inst_id = inst.get("id", inst.get("mnemonic", "<missing-id>"))
        mnemonic = str(inst.get("mnemonic", "")).strip().upper()

        # Historical cleanup guard: the vector block headers are VPAR/VSEQ.
        # If an older mnemonic spelling ("BSTART.VEC") reappears in golden/spec,
        # treat it as a hard error so it cannot silently regress.
        if mnemonic == "BSTART.VEC":
            errors.append(f"{inst_id}: forbidden mnemonic present in spec: BSTART.VEC (use BSTART.VPAR/VSEQ)")

        parts = inst.get("parts", [])
        enc = inst.get("encoding", {})
        enc_parts = enc.get("parts", [])

        if len(parts) != len(enc_parts):
            errors.append(f"{inst_id}: parts count {len(parts)} != encoding.parts count {len(enc_parts)}")
            continue

        for i, (part, enc_part) in enumerate(zip(parts, enc_parts)):
            width_bits = int(part.get("width_bits", 0))
            if int(enc_part.get("width_bits", -1)) != width_bits:
                errors.append(
                    f"{inst_id}: part[{i}] width_bits {width_bits} != encoding.width_bits {enc_part.get('width_bits')}"
                )
                continue

            # Segments should cover full width.
            segs = part.get("segments", [])
            seg_sum = sum(int(s.get("width", 0)) for s in segs)
            if seg_sum != width_bits:
                errors.append(f"{inst_id}: part[{i}] segments cover {seg_sum} bits, expected {width_bits}")

            # Derived mask/match should be within width.
            mask = _parse_hex(enc_part.get("mask", "0x0"))
            match = _parse_hex(enc_part.get("match", "0x0"))
            width_mask = _mask_for_width(width_bits)
            if (mask & ~width_mask) != 0:
                errors.append(f"{inst_id}: part[{i}] mask has bits outside width")
            if (match & ~width_mask) != 0:
                errors.append(f"{inst_id}: part[{i}] match has bits outside width")
            if (match & ~mask) != 0:
                errors.append(f"{inst_id}: part[{i}] match sets bits not covered by mask")

            pattern = enc_part.get("pattern", "")
            if len(pattern) != width_bits:
                errors.append(f"{inst_id}: part[{i}] pattern length {len(pattern)} != width {width_bits}")
            else:
                pmask, pmatch = _pattern_to_mask_match(pattern)
                if pmask != mask or pmatch != match:
                    errors.append(
                        f"{inst_id}: part[{i}] pattern-derived mask/match disagree "
                        f"(mask {pmask:#x} vs {mask:#x}, match {pmatch:#x} vs {match:#x})"
                    )

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--profile",
        choices=["v0.3", "v0.4"],
        default="v0.4",
        help="ISA profile for default --spec path (v0.4 is canonical)",
    )
    ap.add_argument(
        "--spec",
        default=None,
        help="Path to the generated ISA spec JSON",
    )
    args = ap.parse_args()

    default_spec = "isa/v0.4/linxisa-v0.4.json"
    errors = validate(args.spec or default_spec)
    if errors:
        for e in errors[:200]:
            print(e, file=sys.stderr)
        if len(errors) > 200:
            print(f"... {len(errors) - 200} more", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
