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
import re
import sys
from collections import defaultdict
from pathlib import Path
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
                f"state.engine_ops.tepl: {name}=0x{selector:03X} uses reserved high tile-opcode bits outside the packed v0.56 profile"
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

    tma = engine_ops.get("tma")
    expected_tma_aliases = [
        {"function": 0, "mnemonic": "BSTART.TLOAD"},
        {"function": 1, "mnemonic": "BSTART.TSTORE"},
        {"function": 2, "mnemonic": "BSTART.TMOV"},
    ]
    if not isinstance(tma, dict):
        errors.append("state.engine_ops.tma must be a mapping")
    else:
        if tma.get("kind") != "function_u5":
            errors.append("state.engine_ops.tma.kind must be function_u5")
        if tma.get("function_field_bits") != [0, 4]:
            errors.append("state.engine_ops.tma.function_field_bits must be [0, 4]")
        if tma.get("legal_aliases") != expected_tma_aliases:
            errors.append("state.engine_ops.tma.legal_aliases must assign only TLOAD=0, TSTORE=1, TMOV=2")
        if tma.get("reserved_function_range") != [3, 31]:
            errors.append("state.engine_ops.tma.reserved_function_range must be [3, 31]")
        if tma.get("reserved_behavior") != "illegal_instruction":
            errors.append("state.engine_ops.tma.reserved_behavior must be illegal_instruction")

    instructions = spec.get("instructions", [])
    if any(str(inst.get("mnemonic") or "") == "BSTART.TMA" for inst in instructions):
        errors.append("BSTART.TMA is an encoding-family name, not a legal v0.56 instruction form")

    one_part_32 = []
    for inst in instructions:
        parts = inst.get("encoding", {}).get("parts", [])
        if len(parts) != 1 or int(inst.get("length_bits", 0)) != 32:
            continue
        one_part_32.append(
            (
                str(inst.get("mnemonic") or ""),
                int(parts[0]["mask"], 0),
                int(parts[0]["match"], 0),
            )
        )

    tma_base = 0x00011181
    for function, expected in enumerate(("BSTART.TLOAD", "BSTART.TSTORE", "BSTART.TMOV")):
        word = (1 << 27) | (function << 20) | tma_base
        matches = sorted(name for name, mask, match in one_part_32 if word & mask == match)
        if matches != [expected]:
            errors.append(
                f"TMA Function={function} FP32 must decode only as {expected}, got {matches}"
            )

    for dtype in range(32):
        for function in range(3, 32):
            word = (dtype << 27) | (function << 20) | tma_base
            matches = sorted(name for name, mask, match in one_part_32 if word & mask == match)
            if matches:
                errors.append(
                    f"reserved TMA dtype={dtype} Function={function} matches legal forms {matches}"
                )
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


def _validate_field_definitions(spec: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
    field_definitions = spec.get("field_definitions")
    if not isinstance(field_definitions, dict) or not isinstance(field_definitions.get("fields"), dict):
        errors.append("missing compiled field_definitions.fields")
        return {}

    definitions = field_definitions["fields"]
    observed: Dict[str, Dict[str, set[Any]]] = {}
    for inst in spec.get("instructions", []):
        for part in inst.get("encoding", {}).get("parts", []):
            for field in part.get("fields", []):
                name = str(field.get("name") or "")
                width = sum(int(piece.get("width", 0)) for piece in field.get("pieces", []))
                item = observed.setdefault(name, {"widths": set(), "signed": set()})
                item["widths"].add(width)
                if field.get("signed") is not None:
                    item["signed"].add(bool(field["signed"]))

    missing = sorted(set(observed) - set(definitions))
    unknown = sorted(
        name
        for name in set(definitions) - set(observed)
        if not isinstance(definitions[name], dict) or definitions[name].get("documented_only") is not True
    )
    if missing:
        errors.append(f"compiled field definitions are missing observed fields: {missing}")
    if unknown:
        errors.append(f"compiled field definitions contain unknown fields: {unknown}")

    valid_namespaces = {"immediate", "operand", "register-or-identifier", "reserved", "selector"}
    for name, definition in definitions.items():
        if not isinstance(definition, dict):
            errors.append(f"field definition {name!r} must be an object")
            continue
        widths = definition.get("widths")
        if (
            not isinstance(widths, list)
            or not widths
            or not all(isinstance(width, int) and width > 0 for width in widths)
            or widths != sorted(set(widths))
        ):
            errors.append(f"field definition {name!r} has invalid widths {widths!r}")
            continue
        if name not in observed and definition.get("documented_only") is not True:
            errors.append(f"unobserved field definition {name!r} requires documented_only=true")
        if name in observed and definition.get("documented_only") is True:
            errors.append(f"observed field definition {name!r} cannot be documented_only")
        if name in observed and widths != sorted(observed[name]["widths"]):
            errors.append(
                f"field definition {name!r} widths {widths} do not match observed {sorted(observed[name]['widths'])}"
            )
        namespace = definition.get("namespace")
        if namespace not in valid_namespaces:
            errors.append(f"field definition {name!r} has invalid namespace {namespace!r}")
            continue
        if namespace == "immediate":
            if not isinstance(definition.get("signed"), bool):
                errors.append(f"immediate field {name!r} must declare boolean signedness")
            scale = definition.get("scale")
            if not isinstance(scale, int) or isinstance(scale, bool) or scale <= 0:
                errors.append(f"immediate field {name!r} has invalid scale {scale!r}")
        if namespace == "selector":
            reserved_values = definition.get("reserved_values")
            if not isinstance(reserved_values, list) or not all(
                isinstance(value, int) and not isinstance(value, bool) and 0 <= value < (1 << min(widths))
                for value in reserved_values
            ):
                errors.append(f"selector field {name!r} has invalid reserved_values {reserved_values!r}")
            maximum = (1 << min(widths)) - 1
            reserved_ranges = definition.get("reserved_ranges", [])
            if not isinstance(reserved_ranges, list) or not all(
                isinstance(item, list)
                and len(item) == 2
                and all(isinstance(value, int) and not isinstance(value, bool) for value in item)
                and 0 <= item[0] <= item[1] <= maximum
                for item in reserved_ranges
            ):
                errors.append(f"selector field {name!r} has invalid reserved_ranges {reserved_ranges!r}")
        if namespace == "reserved":
            allowed_values = definition.get("allowed_values")
            if not isinstance(allowed_values, list) or not allowed_values or not all(
                isinstance(value, int) and not isinstance(value, bool) and 0 <= value < (1 << min(widths))
                for value in allowed_values
            ):
                errors.append(f"reserved field {name!r} has invalid allowed_values {allowed_values!r}")
        seen_signed = observed.get(name, {}).get("signed", set())
        if len(seen_signed) == 1 and definition.get("signed") is not next(iter(seen_signed)):
            errors.append(
                f"field definition {name!r} signedness {definition.get('signed')!r} disagrees with encoded pieces"
            )
    return definitions


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

    compiled_fields = _validate_field_definitions(spec, errors)

    if not isinstance(spec.get("semantics_conventions"), dict):
        errors.append("missing compiled semantics_conventions")

    retired = spec.get("retired_encodings")
    retired_entries = retired.get("entries") if isinstance(retired, dict) else None
    if not isinstance(retired_entries, list):
        errors.append("missing compiled retired_encodings.entries")
    else:
        retired_names = {str(entry.get("retired_mnemonic") or "") for entry in retired_entries}
        if retired_names != {"B.IOD", "BSTART.PAR"}:
            errors.append(f"retired encoding identities must be exactly B.IOD and BSTART.PAR, got {retired_names}")

    for inst in spec.get("instructions", []):
        inst_id = inst.get("id", inst.get("mnemonic", "<missing-id>"))
        mnemonic = str(inst.get("mnemonic", "")).strip().upper()

        # Historical cleanup guard: the vector block headers are VPAR/VSEQ.
        # If an older mnemonic spelling ("BSTART.VEC") reappears in golden/spec,
        # treat it as a hard error so it cannot silently regress.
        forbidden_mnemonics = {
            "BSTART.VEC": "use BSTART.VPAR/VSEQ",
            "BSTART.PAR": "use BSTART.TEPL",
            "B.IOD": "use B.IOR/B.IOT",
        }
        if mnemonic in forbidden_mnemonics:
            errors.append(
                f"{inst_id}: forbidden mnemonic present in spec: {mnemonic} "
                f"({forbidden_mnemonics[mnemonic]})"
            )

        if not inst.get("uop_big_kind") or not isinstance(inst.get("uop_class"), dict):
            errors.append(f"{inst_id}: missing canonical uop classification")

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

            for field in enc_part.get("fields", []):
                name = str(field.get("name") or "").strip()
                definition = compiled_fields.get(name)
                if not isinstance(definition, dict):
                    errors.append(f"{inst_id}: field {name!r} missing from compiled field definitions")
                    continue
                width = sum(int(piece.get("width", 0)) for piece in field.get("pieces", []))
                if width not in definition.get("widths", []):
                    errors.append(
                        f"{inst_id}: field {name!r} width {width} is absent from definition widths "
                        f"{definition.get('widths')}"
                    )

    return errors


LEGACY_CONTRACT_TOKEN = "check" + "26"


ACTIVE_SURFACE_PATTERNS = [
    (
        "removed legacy contract citation",
        re.compile(
            rf"(?:{LEGACY_CONTRACT_TOKEN}|{LEGACY_CONTRACT_TOKEN}_contract\.py|{LEGACY_CONTRACT_TOKEN}_contract\.yaml|CHECK26_CONTRACT\.md)"
        ),
    ),
    ("pre-canonical draft citation", re.compile(r"\bv0\.4-draft\b")),
    ("stale Sail/docs wording", re.compile(r"\b(?:skeleton|placeholder)\b", re.IGNORECASE)),
]


def validate_active_surfaces(root: Path) -> List[str]:
    files = [
        root / "README.md",
        root / "docs" / "README.md",
        root / "docs" / "index.md",
        root / "docs" / "architecture" / "README.md",
        root / "docs" / "architecture" / "v0.56-architecture-contract.md",
        root / "docs" / "bringup" / "README.md",
        root / "docs" / "bringup" / "AVS_CONTRACT.md",
        root / "docs" / "bringup" / "GETTING_STARTED.md",
        root / "docs" / "bringup" / "PROGRESS.md",
        root / "docs" / "bringup" / "GATE_STATUS.md",
        root / "isa" / "README.md",
        root / "isa" / "sail" / "README.md",
        root / "isa" / "sail" / "model" / "decode" / "decode.sail",
        root / "isa" / "sail" / "model" / "state" / "state.sail",
        root / "isa" / "sail" / "model" / "linxisa.sail_project",
    ]
    errors: List[str] = []
    for path in files:
        if not path.is_file():
            errors.append(f"active surface missing: {path}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in ACTIVE_SURFACE_PATTERNS:
            for idx, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    errors.append(f"{path}:{idx}: {label}: {line.strip()!r}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--profile",
        choices=["v0.56"],
        default="v0.56",
        help="ISA profile for default --spec path (v0.56 is canonical)",
    )
    ap.add_argument(
        "--spec",
        default=None,
        help="Path to the generated ISA spec JSON",
    )
    args = ap.parse_args()

    default_spec = "isa/v0.56/linxisa-v0.56.json"
    errors = validate(args.spec or default_spec)
    errors.extend(validate_active_surfaces(Path(".")))
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
