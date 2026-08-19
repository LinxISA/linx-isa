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
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple


EXPECTED_V058_FIRST_USE_BRINGUP_TRAPNUMS = {
    "EXEC_STATE_CHECK": 0,
    "ILLEGAL_INST": 4,
    "BLOCK_TRAP": 5,
    "SCALL": 6,
    "INST_PC_FAULT": 32,
    "INST_PAGE_FAULT": 33,
    "DATA_ALIGN_FAULT": 34,
    "DATA_PAGE_FAULT": 35,
    "INTERRUPT": 44,
    "HW_BREAKPOINT": 49,
    "SW_BREAKPOINT": 50,
    "HW_WATCHPOINT": 51,
    "ASSERT_FAIL": 52,
}

EXPECTED_V058_FIRST_USE_ECONFIG_BITS = {
    "E": 0,
    "T": 1,
    "S": 2,
    "A": 3,
    "V": 32,
    "C": 33,
}

EXPECTED_V058_FIRST_USE_TRAP = {
    "e": 1,
    "argv": 1,
    "trapnum": "E_INST",
    "trapnum_value": 0,
    "cause": "EC_PERM",
    "cause_value": 4,
    "bi": 0,
}

EXPECTED_V058_FIRST_USE_REGISTER = {
    **EXPECTED_V058_FIRST_USE_TRAP,
    "traparg0": {"VECTOR": 0, "CUBE": 1},
}

EXPECTED_V058_FIRST_USE_VECTOR_HEADERS = [
    "BSTART.MPAR",
    "BSTART.MSEQ",
    "BSTART.VPAR",
    "BSTART.VSEQ",
    "C.BSTART.MPAR",
    "C.BSTART.MSEQ",
    "C.BSTART.VPAR",
    "C.BSTART.VSEQ",
]


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
                f"state.engine_ops.tepl: {name}=0x{selector:03X} uses reserved high tile-opcode bits outside the packed v0.57 profile"
            )
        if name not in expected_by_name:
            errors.append(
                f"state.engine_ops.tepl: {name}=0x{selector:03X} is not described by the packed TEPL allocation table"
            )


def _expected_v057_tepl_selectors() -> Dict[str, int]:
    return {
        "TCMP": 0x02B,
        "TSEL": 0x02C,
        "TABS": 0x02D,
        "TNOT": 0x02E,
        "TNEG": 0x02F,
        "TREM": 0x030,
        "TAXPY": 0x031,
        "TREMS": 0x032,
        "TCMPS": 0x033,
        "TSELS": 0x034,
        "TROWPROD": 0x035,
        "TROWARGMAX": 0x036,
        "TROWARGMIN": 0x037,
        "TCOLPROD": 0x038,
        "TCOLARGMAX": 0x039,
        "TCOLARGMIN": 0x03A,
        "TROWEXPANDADD": 0x03B,
        "TROWEXPANDSUB": 0x03C,
        "TROWEXPANDMUL": 0x03D,
        "TROWEXPANDDIV": 0x03E,
        "TROWEXPANDMAX": 0x03F,
        "TROWEXPANDMIN": 0x040,
        "TROWEXPANDEXPDIF": 0x041,
        "TCOLEXPANDADD": 0x042,
        "TCOLEXPANDSUB": 0x043,
        "TCOLEXPANDMUL": 0x044,
        "TCOLEXPANDDIV": 0x045,
        "TCOLEXPANDMAX": 0x046,
        "TCOLEXPANDMIN": 0x047,
        "TCOLEXPANDEXPDIF": 0x048,
        "TCI": 0x080,
        "TTRI": 0x081,
        "TFILLPAD": 0x082,
        "TQUANT": 0x083,
        "TDEQUANT": 0x084,
        "TEXTRACT": 0x085,
        "TINSERT": 0x086,
        "TCONCAT": 0x087,
        "TIMG2COL": 0x088,
        "TGATHERB": 0x089,
        "TDEINTERLEAVE": 0x08A,
        "TINTERLEAVE": 0x08B,
        "TSORT": 0x0C0,
        "TMRGSORT": 0x0C1,
        "THISTOGRAM": 0x0C2,
        "TPARTADD": 0x0C3,
        "TPARTMUL": 0x0C4,
        "TPARTMAX": 0x0C5,
        "TPARTMIN": 0x0C6,
        "TPARTARGMAX": 0x0C7,
        "TPARTARGMIN": 0x0C8,
        "TPUSH": 0x0E0,
        "TPOP": 0x0E1,
        "TALLOC": 0x0E2,
        "TFREE": 0x0E3,
    }


def _validate_v057_tepl_extensions(tepl: Dict[str, Any], selector_by_name: Dict[str, int], errors: List[str]) -> None:
    expected = _expected_v057_tepl_selectors()
    for name, selector in sorted(expected.items(), key=lambda item: item[1]):
        got = selector_by_name.get(name)
        if got != selector:
            errors.append(f"state.engine_ops.tepl: v0.57 requires {name}=0x{selector:03X}, got {got!r}")

    forbidden = {"TFMOD", "TPOW", "TRANDOM", "TEXRACT"}
    present_forbidden = sorted(forbidden & set(selector_by_name))
    if present_forbidden:
        errors.append(f"state.engine_ops.tepl: review-only/typo names must not be architectural: {present_forbidden}")

    policy = tepl.get("extension_policy_v057")
    if not isinstance(policy, dict):
        errors.append("state.engine_ops.tepl.extension_policy_v057 must describe v0.57 TEPL ranges")
        return
    if policy.get("preserve_selectors") != [[0x000, 0x02A]]:
        errors.append("state.engine_ops.tepl.extension_policy_v057.preserve_selectors must be [[0x000, 0x02A]]")
    if policy.get("new_selector_ranges") != [[0x02B, 0x048], [0x080, 0x08B], [0x0C0, 0x0C8], [0x0E0, 0x0E3]]:
        errors.append("state.engine_ops.tepl.extension_policy_v057.new_selector_ranges do not match the frozen v0.57 map")
    if policy.get("reserved_selector_ranges") != [[0x049, 0x07F], [0x08C, 0x0BF], [0x0C9, 0x0DF], [0x0E4, 0x3FF]]:
        errors.append("state.engine_ops.tepl.extension_policy_v057.reserved_selector_ranges do not match the frozen v0.57 map")


def _validate_engine_ops_v0571(spec: Dict[str, Any], engine_ops: Dict[str, Any], errors: List[str]) -> None:
    """Validate the PTO 0.57.1 projection without retaining pre-0.57.1 ABI rules."""
    tepl = engine_ops.get("tepl", {})
    ops = tepl.get("ops", []) if isinstance(tepl, dict) else []
    if tepl.get("kind") != "mode_function":
        errors.append("state.engine_ops.tepl.kind must be mode_function")
    if tepl.get("selector_formula") != "(mode << 5) | function":
        errors.append("state.engine_ops.tepl.selector_formula must be (mode << 5) | function")
    if tepl.get("accepted_selector_count") != 98 or len(ops) != 98:
        errors.append("state.engine_ops.tepl must contain exactly 98 accepted operations")
    selectors: Dict[int, str] = {}
    forbidden = {"TADDC", "TADDSC", "TFMA", "TFMOD", "TFMODS", "TLRELU", "TRANDOM", "TSUBC", "TSUBSC", "TTRANSPOSE", "TSORT32"}
    for idx, op in enumerate(ops):
        name = str(op.get("name") or "")
        mode, function = op.get("mode"), op.get("function")
        if not isinstance(mode, int) or not 0 <= mode <= 3 or not isinstance(function, int) or not 0 <= function <= 31:
            errors.append(f"state.engine_ops.tepl.ops[{idx}] has invalid Mode/Function")
            continue
        selector = (mode << 5) | function
        if op.get("logical_selector") != selector:
            errors.append(f"state.engine_ops.tepl.ops[{idx}] logical_selector does not match Mode/Function")
        if selector in selectors:
            errors.append(f"state.engine_ops.tepl selector {selector:#04x} is shared by {selectors[selector]} and {name}")
        selectors[selector] = name
        if op.get("semantic_status") != "reviewed-complete":
            errors.append(f"state.engine_ops.tepl.ops[{idx}] is not reviewed-complete")
    leaked = sorted(forbidden & {str(op.get("name")) for op in ops})
    if leaked:
        errors.append(f"deleted or migration-only TEPL names leaked: {leaked}")

    expected = {
        "tma": set(range(9)),
        "cube": {0, 1, 2, 4, 5, 6, 8, 16, 17, 18, 20, 21, 22},
    }
    for family, functions in expected.items():
        state = engine_ops.get(family, {})
        actual = {int(item["function"]) for item in state.get("legal_aliases", [])}
        if actual != functions:
            errors.append(f"state.engine_ops.{family} functions differ from PTO ISA 0.57.1")
    if engine_ops.get("cube", {}).get("unassigned_function_behavior") != "illegal_instruction":
        errors.append("state.engine_ops.cube unassigned functions must be illegal_instruction")

    instructions = spec.get("instructions", [])
    mnemonics = {str(item.get("mnemonic") or "") for item in instructions}
    if "BSTART.CUBE" in mnemonics:
        errors.append("generic BSTART.CUBE must not be a legal decode in PTO ISA 0.57.1")
    tepl_forms = [item for item in instructions if item.get("mnemonic") == "BSTART.TEPL"]
    if len(tepl_forms) != 1:
        errors.append("PTO ISA 0.57.1 requires exactly one BSTART.TEPL form")
    else:
        part = tepl_forms[0].get("encoding", {}).get("parts", [{}])[0]
        if (int(part.get("mask", "0"), 0), int(part.get("match", "0"), 0)) != (0x000FFFFF, 0x00019181):
            errors.append("BSTART.TEPL must use the PTO ISA 0.57.1 Mode/Function encoding")


def _validate_engine_ops_v058(spec: Dict[str, Any], engine_ops: Dict[str, Any], errors: List[str]) -> None:
    """Validate the exact PTO 0.58 tile projection and Shared tile contract."""
    tepl = engine_ops.get("tepl", {})
    ops = tepl.get("ops", []) if isinstance(tepl, dict) else []
    if tepl.get("kind") != "mode_function" or tepl.get("selector_formula") != "(mode << 5) | function":
        errors.append("state.engine_ops.tepl must use the PTO 0.58 Mode/Function contract")
    if tepl.get("accepted_selector_count") != 87 or len(ops) != 87:
        errors.append("state.engine_ops.tepl must contain exactly 87 PTO 0.58 operations")
    selectors = set()
    engine_counts: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()
    for idx, op in enumerate(ops):
        mode, function = op.get("mode"), op.get("function")
        if not isinstance(mode, int) or not isinstance(function, int):
            errors.append(f"state.engine_ops.tepl.ops[{idx}] has invalid Mode/Function")
            continue
        selector = (mode << 5) | function
        if op.get("logical_selector") != selector or selector in selectors:
            errors.append(f"state.engine_ops.tepl.ops[{idx}] has invalid or duplicate selector")
        selectors.add(selector)
        engine_counts[str(op.get("engine"))] += 1
        classification_counts[str(op.get("classification"))] += 1

    expected = {
        "tlsu": {0, 1, 2, 3, 4, 5, 6, 7, 8, 13},
        "cube": {0, 1, 2, 4, 5, 6, 16, 17, 18, 20, 21, 22},
    }
    for family, functions in expected.items():
        state = engine_ops.get(family, {})
        actual = {int(item["function"]) for item in state.get("legal_aliases", [])}
        if actual != functions:
            errors.append(f"state.engine_ops.{family} functions differ from PTO ISA 0.58")
        for operation in state.get("legal_aliases", []):
            engine_counts[str(operation.get("engine"))] += 1
            classification_counts[str(operation.get("classification"))] += 1
    expected_engine_counts = {"CUBE": 12, "SFU": 56, "TLSU": 10, "VEC": 31}
    if dict(sorted(engine_counts.items())) != expected_engine_counts:
        errors.append("state.engine_ops semantic engines must be exactly 31 VEC / 56 SFU / 10 TLSU / 12 CUBE")
    if engine_ops.get("semantic_engine_counts") != expected_engine_counts:
        errors.append("state.engine_ops.semantic_engine_counts differs from the PTO 0.58 projection")
    expected_classification_counts = {
        "elementwise-tile-tile": 25,
        "irregular-and-complex": 13,
        "layout-and-rearrangement": 7,
        "matrix-and-matrix-vector": 12,
        "memory-and-data-movement": 9,
        "reduce-and-expand": 28,
        "tile-scalar-and-immediate": 15,
    }
    if dict(sorted(classification_counts.items())) != expected_classification_counts:
        errors.append("state.engine_ops semantic classifications differ from the PTO 0.58 projection")
    if engine_ops.get("tlsu", {}).get("reserved_function_ranges") != [[15, 31]]:
        errors.append("state.engine_ops.tlsu reserved ranges must be [[15, 31]]")
    if engine_ops.get("cube", {}).get("unassigned_function_behavior") != "illegal_instruction":
        errors.append("state.engine_ops.cube unassigned functions must be illegal_instruction")
    shared = engine_ops.get("shared_tile_registers", {})
    if shared.get("registers_per_core") != 256 or shared.get("addressing") != "absolute-index":
        errors.append("state.engine_ops Shared tile registers must be absolute S0..S255")
    mnemonics = {str(item.get("mnemonic") or "") for item in spec.get("instructions", [])}
    if "B.IOS" not in mnemonics or "BSTART.GMOV" not in mnemonics:
        errors.append("PTO ISA 0.58 requires B.IOS and BSTART.GMOV")
    if {"B.IOD", "BSTART.PAR", "C.B.IOS"} & mnemonics:
        errors.append("PTO ISA 0.58 deleted scalar/block spellings must not decode")
    tfma = [op for op in ops if op.get("name") == "TFMA"]
    if len(tfma) != 1 or (tfma[0].get("mode"), tfma[0].get("function")) != (0, 28):
        errors.append("PTO ISA 0.58 requires TFMA at TEPL Mode=0 Function=28")


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

    if str(spec.get("version") or "") == "0.57.1":
        _validate_engine_ops_v0571(spec, engine_ops, errors)
        return
    if str(spec.get("version") or "") in {"0.58.0", "0.58.1"}:
        _validate_engine_ops_v058(spec, engine_ops, errors)
        return

    tma = engine_ops.get("tma")
    version = str(spec.get("version") or "")
    is_v057 = version.startswith("0.57")
    expected_tma_aliases = [
        {"function": 0, "mnemonic": "BSTART.TLOAD"},
        {"function": 1, "mnemonic": "BSTART.TSTORE"},
        {"function": 2, "mnemonic": "BSTART.TMOV"},
    ]
    if is_v057:
        expected_tma_aliases.extend(
            [
                {"function": 3, "mnemonic": "BSTART.TPREFETCH", "semantic_delta": "Same address, layout, memory, fault, ordering, and restart contract as BSTART.TLOAD, with destination binding, destination allocation, and destination writeback removed."},
                {"function": 4, "mnemonic": "BSTART.MGATHER"},
                {"function": 5, "mnemonic": "BSTART.MSCATTER"},
                {"function": 6, "mnemonic": "BSTART.MGATHER.MASK"},
                {"function": 7, "mnemonic": "BSTART.MSCATTER.MASK"},
                {"function": 8, "mnemonic": "BSTART.MGATHER.CAS"},
            ]
        )
    if not isinstance(tma, dict):
        errors.append("state.engine_ops.tma must be a mapping")
    else:
        if tma.get("kind") != "function_u5":
            errors.append("state.engine_ops.tma.kind must be function_u5")
        if tma.get("function_field_bits") != [0, 4]:
            errors.append("state.engine_ops.tma.function_field_bits must be [0, 4]")
        if tma.get("legal_aliases") != expected_tma_aliases:
            if is_v057:
                errors.append("state.engine_ops.tma.legal_aliases must assign v0.57 TMA Functions 0..8 exactly")
            else:
                errors.append("state.engine_ops.tma.legal_aliases must assign only TLOAD=0, TSTORE=1, TMOV=2")
        expected_reserved = [9, 31] if is_v057 else [3, 31]
        if tma.get("reserved_function_range") != expected_reserved:
            errors.append(f"state.engine_ops.tma.reserved_function_range must be {expected_reserved}")
        if tma.get("reserved_behavior") != "illegal_instruction":
            errors.append("state.engine_ops.tma.reserved_behavior must be illegal_instruction")

    instructions = spec.get("instructions", [])
    if any(str(inst.get("mnemonic") or "") == "BSTART.TMA" for inst in instructions):
        errors.append("BSTART.TMA is an encoding-family name, not a legal instruction form")

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
    expected_tma_decodes = ("BSTART.TLOAD", "BSTART.TSTORE", "BSTART.TMOV")
    if is_v057:
        expected_tma_decodes = (
            "BSTART.TLOAD",
            "BSTART.TSTORE",
            "BSTART.TMOV",
            "BSTART.TPREFETCH",
            "BSTART.MGATHER",
            "BSTART.MSCATTER",
            "BSTART.MGATHER.MASK",
            "BSTART.MSCATTER.MASK",
            "BSTART.MGATHER.CAS",
        )
    for function, expected in enumerate(expected_tma_decodes):
        word = (1 << 27) | (function << 20) | tma_base
        matches = sorted(name for name, mask, match in one_part_32 if word & mask == match)
        if matches != [expected]:
            errors.append(
                f"TMA Function={function} FP32 must decode only as {expected}, got {matches}"
            )

    legal_tma_functions = set(range(len(expected_tma_decodes)))
    if is_v057:
        legal_tma_functions.update(range(4, 9))
    for dtype in range(32):
        for function in range(32):
            if function in legal_tma_functions:
                continue
            word = (dtype << 27) | (function << 20) | tma_base
            matches = sorted(name for name, mask, match in one_part_32 if word & mask == match)
            if matches:
                errors.append(
                    f"reserved TMA dtype={dtype} Function={function} matches legal forms {matches}"
                )
                return

    if is_v057:
        expected_cube_aliases = [
            {"function": 0, "mnemonic": "BSTART.TMATMUL"},
            {"function": 1, "mnemonic": "BSTART.TMATMUL.BIAS"},
            {"function": 2, "mnemonic": "BSTART.TMATMUL.ACC"},
            {"function": 4, "mnemonic": "BSTART.TMATMULMX"},
            {"function": 5, "mnemonic": "BSTART.TMATMULMX.BIAS"},
            {"function": 6, "mnemonic": "BSTART.TMATMULMX.ACC"},
            {"function": 8, "mnemonic": "BSTART.ACCCVT"},
            {"function": 16, "mnemonic": "BSTART.TGEMV"},
            {"function": 17, "mnemonic": "BSTART.TGEMV.BIAS"},
            {"function": 18, "mnemonic": "BSTART.TGEMV.ACC"},
            {"function": 20, "mnemonic": "BSTART.TGEMVMX"},
            {"function": 21, "mnemonic": "BSTART.TGEMVMX.BIAS"},
            {"function": 22, "mnemonic": "BSTART.TGEMVMX.ACC"},
        ]
        unassigned_cube_aliases = [3, 7, *range(9, 16), 19, *range(23, 32)]
        cube = engine_ops.get("cube")
        if not isinstance(cube, dict):
            errors.append("state.engine_ops.cube must be a mapping for v0.57")
        else:
            if cube.get("kind") != "function_u5":
                errors.append("state.engine_ops.cube.kind must be function_u5")
            if cube.get("function_field_bits") != [0, 4]:
                errors.append("state.engine_ops.cube.function_field_bits must be [0, 4]")
            if cube.get("legal_aliases") != expected_cube_aliases:
                errors.append("state.engine_ops.cube.legal_aliases must match the frozen v0.57 CUBE map")
            if cube.get("unassigned_alias_functions") != unassigned_cube_aliases:
                errors.append("state.engine_ops.cube.unassigned_alias_functions must match the frozen v0.57 CUBE map")
            if cube.get("unassigned_alias_behavior") != "inherit_generic_bstart_cube_decode_without_canonical_alias":
                errors.append("state.engine_ops.cube must preserve the inherited generic BSTART.CUBE decode")

        cube_base = 0x00031181
        expected_cube_decodes = {
            entry["function"]: entry["mnemonic"] for entry in expected_cube_aliases
        }
        for dtype in range(32):
            for function in range(32):
                word = (dtype << 27) | (function << 20) | cube_base
                matches = sorted(
                    name for name, mask, match in one_part_32 if word & mask == match
                )
                expected = expected_cube_decodes.get(function)
                if expected is None:
                    if matches != ["BSTART.CUBE"]:
                        errors.append(
                            f"unassigned CUBE alias dtype={dtype} Function={function} must retain only BSTART.CUBE, got {matches}"
                        )
                        return
                elif matches != sorted(["BSTART.CUBE", expected]):
                    errors.append(
                        f"CUBE dtype={dtype} Function={function} must decode as BSTART.CUBE plus {expected}, got {matches}"
                    )

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

    if is_v057:
        _validate_v057_tepl_extensions(tepl, selector_by_name, errors)
    else:
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


def _validate_frame_template_contract(spec: Dict[str, Any], errors: List[str]) -> None:
    expected_owner_fields = {
        "placement": [
            "lxcpu_id",
            "lxcpu_context_generation",
            "pe_id",
            "stid",
            "engine_local_tid",
        ],
        "group": [
            "bid",
            "bid_robid(valid,wrap,value)",
            "gid",
            "gid_robid(valid,wrap,value)",
            "group_base_rid",
            "group_base_rid_robid(valid,wrap,value)",
            "group_base_rob_slot",
            "group_row_count",
            "checkpoint_id",
            "template_generation",
            "source_pc",
            "source_raw",
            "form_id",
            "encoded_N",
        ],
        "row": [
            "row_present",
            "row_kind",
            "child_ordinal",
            "rid",
            "rid_robid(valid,wrap,value)",
            "rob_slot",
            "row_generation",
        ],
        "memory": [
            "lsid_valid",
            "lsid_value",
            "lsid_wrap_or_generation",
            "load_id_valid",
            "load_id_value",
            "load_id_generation",
            "load_replay_generation",
            "store_id_valid",
            "store_id_value",
            "store_id_generation",
        ],
    }
    expected_lease_id = [
        "lease_generation",
        "validation_generation",
        "validation_token_hash",
        "exact_vtgt_TemplateOwnerID",
        "exact_vload_TemplateOwnerID_or_canonical_invalid",
        "retained_target_mapping_visibility_share_domain_key",
    ]
    expected_txn_base_fields = [
        "producer_domain",
        "producer_kind",
        "producer_lxcpu_id",
        "producer_context_generation",
        "producer_pe_id",
        "producer_stid_valid",
        "producer_stid",
        "producer_tid_valid",
        "producer_engine_local_tid",
        "producer_endpoint_id",
        "transaction_sequence_value",
        "transaction_sequence_wrap_or_generation",
        "architectural_operation",
        "exact_operation_scope",
    ]
    expected_txn_id_fields = [
        "complete InvalidationTxnBase",
        "matched_LeaseID_or_explicit_NO_LEASE",
        "lease_directory_generation_at_lookup",
        "status_generation",
    ]
    expected_ack_id_fields = [
        "complete InvalidationTxnID",
        "exact_lease_owner_TemplateOwnerID_or_canonical_invalid",
        "terminal_kind",
    ]
    expected_target_proof = {
        "actual_current_marker_proof": "required before every FRET effect",
        "coherent_marker_provenance_cache": "legal only when it proves the same target marker bytes, address-space state, code-visibility epoch, and invalidation scope as an actual current marker proof",
        "metadata_only_continuation_or_fallthrough": "non-conforming compatibility; must be rejected",
        "deferred_demand_paging": "qualified only while every FRET effect remains withheld",
        "fault_owner": "VTGT owns translation, execute-permission, marker, and CFI faults",
    }
    expected_event_zero_seal_transaction = [
        "recheck_all_identities_and_generations",
        "acquire_complete_FRET_lease",
        "retire_successful_validation_rows_with_distinct_traces",
        "commit_event_zero",
        "advance_StepIndex_0_to_1",
    ]
    expected_ebstate_recoverable_retention = [
        "exact TemplateOwnerID",
        "phase and StepIndex cursors",
        "sealed VLOAD state when applicable",
        "validation token",
        "retained lease",
        "complete pending InvalidationTxnID/status set",
    ]
    expected_ebstate_retention_forbidden = [
        "renumber pending invalidation entries",
        "merge pending invalidation entries",
        "reacquire lease entries",
        "restore a pre-template checkpoint",
    ]
    expected_final_identity = {
        "required_matches": [
            "group",
            "checkpoint",
            "template",
            "validation",
            "lease",
            "VTGT key",
            "VLOAD key or canonical invalid",
            "visibility/share-domain",
            "FINAL RID/slot/generation",
            "final ordinal",
        ],
        "shortcut_authority_forbidden": ["queue head", "BID", "RID value", "PC", "opcode", "hash alone"],
    }
    expected_fatal_teardown_order = [
        "stop source-context issue, commit, wakeup, redirect, FINAL transfer, and new lease acquisition",
        "snapshot exact envelope, state, owner, token, and pending transactions",
        "advance template, row, and load generations",
        "cancel every uncommitted row and request",
        "invalidate VLOAD data, VTGT proof, token, and queued transfer",
        "obtain quiescence from every listed owner before releasing the lease",
        "atomically release the lease and create one RELEASED_AFTER_ABORT per pending matching invalidation",
        "publish the fatal record for managing-ring inspection",
    ]
    expected_reset_reuse = {
        "platform_reset_only": True,
        "new_context_generation_required": True,
        "global_quiescence_before_reset": True,
        "no_pre_reset_ack_after_new_context_generation": True,
        "pre_template_state_restore": "forbidden",
    }
    expected_exact_scope_fields = [
        "ACR/regime/root/ASID",
        "VA/PA page or marker range",
        "TLB/code/coherence domain",
        "global/wildcard selectors",
    ]
    expected_physical_sharing_rule = (
        "physical lookup/cancel/drain/release work may be shared only for transactions "
        "matching the same exact LeaseID; producer transaction bases, status, and AckID remain independent"
    )
    expected_stale_ack_rule = (
        "wrong producer, sequence, operation/scope, match, directory, owner, or status-generation is rejected; "
        "identical terminal AckID retransmission is idempotent"
    )
    expected_status_rules = [
        "each state transition increments status_generation",
        "matching post-seal transactions independently record DEFERRED_ACTIVE",
        "FINAL creates one RELEASED_AFTER_FINAL per pending match",
        "fatal release creates one RELEASED_AFTER_ABORT per pending match",
        "post-release admission performs a new lookup at new directory generation",
    ]
    expected_terminal_rules = [
        "NO_MATCH after lookup at the transaction directory generation for nonmatches",
        "CANCELED_PRE_EVENT only after cancellation prevents stale event-zero seal",
        "DEFERRED_ACTIVE recorded independently for each post-seal match and is nonterminal",
        "RELEASED_AFTER_FINAL created atomically by FINAL per pending match",
        "RELEASED_AFTER_ABORT created atomically by fatal release per pending match after quiescence",
        "post-release admission performs a new lookup at the new directory generation and normally receives NO_MATCH",
    ]

    def expect_exact(path: str, got: Any, expected: Any) -> None:
        if got != expected:
            errors.append(f"{path} must exactly equal {expected!r}")

    conventions = spec.get("semantics_conventions")
    if not isinstance(conventions, dict):
        errors.append("missing compiled semantics_conventions")
        return

    frame = conventions.get("frame_templates_r975")
    if not isinstance(frame, dict):
        errors.append("semantics_conventions.frame_templates_r975 must be present")
        return

    if frame.get("applies_to") != ["FENTRY", "FEXIT", "FRET.RA", "FRET.STK"]:
        errors.append("frame_templates_r975.applies_to must name the four canonical frame forms")
    if frame.get("arithmetic", {}).get("kind") != "immediate_only":
        errors.append("frame_templates_r975.arithmetic.kind must be immediate_only")
    if frame.get("register_ring", {}).get("inclusive_range") != [2, 23]:
        errors.append("frame_templates_r975.register_ring.inclusive_range must be [2, 23]")
    target_proof = frame.get("target_proof")
    if not isinstance(target_proof, dict):
        errors.append("frame_templates_r975.target_proof must be present")
    else:
        expect_exact("frame_templates_r975.target_proof", target_proof, expected_target_proof)

    legality = frame.get("legality")
    if not isinstance(legality, dict):
        errors.append("frame_templates_r975.legality must be a mapping")
    else:
        if legality.get("fret_ra_target") != "fixed pre-restore R10":
            errors.append("frame_templates_r975 must fix FRET.RA target to pre-restore R10")
        if legality.get("fret_stk_target") != "fixed R10 restored from slot zero":
            errors.append("frame_templates_r975 must fix FRET.STK target to restored R10")
        stk = legality.get("fret_stk_stack_slot_zero")
        if not isinstance(stk, dict):
            errors.append("frame_templates_r975.legality.fret_stk_stack_slot_zero must be a mapping")
        else:
            if stk.get("required_memory_type") != "Normal" or stk.get("requires_idempotent") is not True:
                errors.append("FRET.STK slot-zero VLOAD must require Normal idempotent memory")
            zero_read = str(stk.get("device_mmio_or_mixed_or_non_idempotent") or "")
            if "before any cache, fabric, device, or MMIO physical read" not in zero_read:
                errors.append("FRET.STK Device/MMIO rejection must occur before any physical read")

    expected_forms = {
        "FENTRY": ("N+3", {"N=1": 4, "N=22": 25}, "N+2=FINAL"),
        "FEXIT": ("N+3", {"N=1": 4, "N=22": 25}, "N+2=FINAL"),
        "FRET.RA": ("N+5", {"N=1": 6, "N=22": 27}, "N+4=FINAL"),
        "FRET.STK": ("N+6", {"N=1": 7, "N=22": 28}, "N+5=FINAL"),
    }
    forms = frame.get("forms")
    if not isinstance(forms, dict):
        errors.append("frame_templates_r975.forms must be a mapping")
    else:
        for name, (total, examples, final_ordinal) in expected_forms.items():
            form = forms.get(name)
            if not isinstance(form, dict):
                errors.append(f"frame_templates_r975.forms.{name} must be present")
                continue
            if form.get("d3_total_rows") != total:
                errors.append(f"frame_templates_r975.forms.{name}.d3_total_rows must be {total}")
            if form.get("examples") != examples:
                errors.append(f"frame_templates_r975.forms.{name}.examples must be {examples}")
            if final_ordinal not in form.get("ordinals", []):
                errors.append(f"frame_templates_r975.forms.{name}.ordinals must include {final_ordinal}")
        malformed = forms.get("malformed")
        if not isinstance(malformed, dict) or malformed.get("d3_total_rows") != 1 or malformed.get("final_row_present") is not False:
            errors.append("frame_templates_r975.forms.malformed must be exactly one VFORM_TRAP row with no FINAL")

    ownership = frame.get("d3_ownership")
    if not isinstance(ownership, dict):
        errors.append("frame_templates_r975.d3_ownership must be a mapping")
    else:
        for forbidden in ("hidden_parent_row", "private_validator", "rowless_validator"):
            if ownership.get(forbidden) is not False:
                errors.append(f"frame_templates_r975.d3_ownership.{forbidden} must be false")

    vload = frame.get("vload")
    if not isinstance(vload, dict):
        errors.append("frame_templates_r975.vload must be a mapping")
    else:
        if "Device/MMIO" not in vload.get("forbidden_memory_zero_read", []):
            errors.append("frame_templates_r975.vload.forbidden_memory_zero_read must include Device/MMIO")
        if vload.get("post_seal_replacement") != "forbidden; enters template_integrity_fail FatalReason=2":
            errors.append("frame_templates_r975.vload.post_seal_replacement must be fatal reason 2")
        expect_exact(
            "frame_templates_r975.vload.identity_fields",
            vload.get("identity_fields"),
            [
                "owner_key",
                "VA",
                "translation_generation",
                "permission_type_generation",
                "LSID",
                "load_id",
                "older_store_forwarding_state",
                "response_source",
                "miss_refill_coherence_generation",
                "load_generation",
                "data",
            ],
        )

    recovery = frame.get("seal_and_recovery")
    if not isinstance(recovery, dict):
        errors.append("frame_templates_r975.seal_and_recovery must be a mapping")
    else:
        expect_exact(
            "frame_templates_r975.seal_and_recovery.event_zero_seal_transaction",
            recovery.get("event_zero_seal_transaction"),
            expected_event_zero_seal_transaction,
        )
        expect_exact(
            "frame_templates_r975.seal_and_recovery.before_seal_invalidation",
            recovery.get("before_seal_invalidation"),
            "wins and cancels phase zero with no effect",
        )
        expect_exact(
            "frame_templates_r975.seal_and_recovery.after_seal_invalidation",
            recovery.get("after_seal_invalidation"),
            "lease wins; producer completion waits through traps, ACRE, suspension, FINAL, or fatal release",
        )
        expect_exact(
            "frame_templates_r975.seal_and_recovery.rollback_after_seal",
            recovery.get("rollback_after_seal"),
            "forbidden for SP, GPR, memory, target, progress, and trace effects",
        )
        expect_exact(
            "frame_templates_r975.seal_and_recovery.final",
            recovery.get("final"),
            "qualifies full token, performs boundary transfer/retirement, and releases lease atomically",
        )
        expect_exact(
            "frame_templates_r975.seal_and_recovery.ebstate_recoverable_retention",
            recovery.get("ebstate_recoverable_retention"),
            expected_ebstate_recoverable_retention,
        )
        expect_exact(
            "frame_templates_r975.seal_and_recovery.ebstate_retention_forbidden",
            recovery.get("ebstate_retention_forbidden"),
            expected_ebstate_retention_forbidden,
        )
        expect_exact(
            "frame_templates_r975.seal_and_recovery.lease_directory_suspend_rule",
            recovery.get("lease_directory_suspend_rule"),
            "lease directory retains discoverability during suspension; a manager must resume through FINAL or choose fatal abandonment and cannot wait on its own deferred invalidation",
        )
        final_identity = recovery.get("final_identity")
        if not isinstance(final_identity, dict):
            errors.append("frame_templates_r975.seal_and_recovery.final_identity must be present")
        else:
            expect_exact("frame_templates_r975.seal_and_recovery.final_identity", final_identity, expected_final_identity)

    fatal = frame.get("template_integrity_fail")
    if not isinstance(fatal, dict):
        errors.append("frame_templates_r975.template_integrity_fail must be a mapping")
    else:
        if fatal.get("trapnum") != "ASSERT_FAIL (52)" or fatal.get("maskable_by_ECONFIG3") is not False:
            errors.append("template_integrity_fail must be unmaskable ASSERT_FAIL (52)")
        reasons = fatal.get("fatal_reasons")
        expected_reasons = {
            "0": "explicit abandonment",
            "1": "dirty-template RRAT_DEFAULT",
            "2": "sealed-VLOAD replay/withdrawal",
            "3": "poisoned response/token",
            "4": "exact-live ownership/generation/lease/FINAL contradiction",
            "5": "suspended drain failure",
            "6..255": "reserved",
        }
        if reasons != expected_reasons:
            errors.append("template_integrity_fail.fatal_reasons must match R975 exactly")
        expect_exact(
            "frame_templates_r975.template_integrity_fail.fatal_teardown_order",
            fatal.get("fatal_teardown_order"),
            expected_fatal_teardown_order,
        )
        reset_reuse = fatal.get("reset_reuse")
        if not isinstance(reset_reuse, dict):
            errors.append("template_integrity_fail.reset_reuse must be present")
        else:
            expect_exact(
                "frame_templates_r975.template_integrity_fail.reset_reuse",
                reset_reuse,
                expected_reset_reuse,
            )

    owner = frame.get("template_owner_id")
    if not isinstance(owner, dict):
        errors.append("frame_templates_r975.template_owner_id must be a mapping")
    else:
        groups = owner.get("field_groups")
        if not isinstance(groups, dict):
            errors.append("template_owner_id.field_groups must be a mapping")
        else:
            expect_exact("template_owner_id.field_groups", groups, expected_owner_fields)
        if owner.get("exact_live_post_seal_contradiction") != "template_integrity_fail FatalReason=4":
            errors.append("template_owner_id exact-live post-seal contradiction must be fatal reason 4")
    expect_exact("frame_templates_r975.lease_id", frame.get("lease_id"), expected_lease_id)

    invalidation = frame.get("invalidation")
    if not isinstance(invalidation, dict):
        errors.append("frame_templates_r975.invalidation must be a mapping")
    else:
        if invalidation.get("producer_bases_coalesce") is not False:
            errors.append("invalidation producer transaction bases must not coalesce")
        if invalidation.get("terminal_kinds") != [
            "NO_MATCH",
            "CANCELED_PRE_EVENT",
            "RELEASED_AFTER_FINAL",
            "RELEASED_AFTER_ABORT",
        ]:
            errors.append("invalidation terminal kinds must match R975")
        if invalidation.get("nonterminal_kinds") != ["DEFERRED_ACTIVE"]:
            errors.append("invalidation DEFERRED_ACTIVE must be nonterminal")
        expect_exact("invalidation.txn_base_fields", invalidation.get("txn_base_fields"), expected_txn_base_fields)
        expect_exact("invalidation.txn_id_fields", invalidation.get("txn_id_fields"), expected_txn_id_fields)
        expect_exact("invalidation.ack_id_fields", invalidation.get("ack_id_fields"), expected_ack_id_fields)
        expect_exact("invalidation.exact_scope_fields", invalidation.get("exact_scope_fields"), expected_exact_scope_fields)
        expect_exact("invalidation.physical_sharing_rule", invalidation.get("physical_sharing_rule"), expected_physical_sharing_rule)
        expect_exact("invalidation.stale_ack_rule", invalidation.get("stale_ack_rule"), expected_stale_ack_rule)
        expect_exact("invalidation.status_rules", invalidation.get("status_rules"), expected_status_rules)
        expect_exact("invalidation.terminal_rules", invalidation.get("terminal_rules"), expected_terminal_rules)
        expect_exact(
            "invalidation.admission_rules",
            invalidation.get("admission_rules"),
            [
                "capacity may backpressure before admission",
                "an admitted transaction cannot be dropped",
                "an admitted matching transaction cannot complete before FINAL or fatal release",
                "a manager cannot roll back or wait on its own deferred invalidation",
            ],
        )

    fixup = conventions.get("fixup_blocks", {})
    assert_contract = fixup.get("assert", {}) if isinstance(fixup, dict) else {}
    masking = assert_contract.get("masking", {}) if isinstance(assert_contract, dict) else {}
    if masking.get("scope") != "ASSERT-instruction-generated ASSERT_FAIL only (other synchronous exceptions are unaffected)":
        errors.append("instruction ASSERT masking scope must not cover template-integrity ASSERT_FAIL")
    producers = fixup.get("assert_fail_producers") if isinstance(fixup, dict) else None
    if not isinstance(producers, dict):
        errors.append("fixup_blocks.assert_fail_producers must describe both ASSERT_FAIL producers")
    else:
        instruction = producers.get("instruction_assert", {})
        integrity = producers.get("template_integrity_fail", {})
        if instruction.get("ecconfig_maskable") is not True or instruction.get("local_fixup") != "existing instruction behavior":
            errors.append("instruction ASSERT producer must preserve masking and local fixup")
        if integrity.get("ecconfig_maskable") is not False or integrity.get("local_fixup") != "forbidden":
            errors.append("template-integrity ASSERT_FAIL producer must be unmaskable with no fixup")


def _validate_first_use_register_contract(
    spec: Dict[str, Any], errors: List[str]
) -> None:
    if str(spec.get("version") or "") != "0.58.1":
        return

    system_registers = ((spec.get("state") or {}).get("system_registers") or {})
    trapno = system_registers.get("trapno_encoding") or {}
    rows = trapno.get("bringup_trapnums") or []
    bringup = {row.get("name"): row.get("trapnum") for row in rows}
    if len(rows) != len(bringup) or bringup != EXPECTED_V058_FIRST_USE_BRINGUP_TRAPNUMS:
        errors.append(f"v0.58: existing bring-up trap numbers changed: {bringup}")
    if trapno.get("first_use_exception") != EXPECTED_V058_FIRST_USE_REGISTER:
        errors.append("v0.58: first-use exception envelope mismatch")
    if "E_PEREM" in json.dumps(system_registers, sort_keys=True):
        errors.append("v0.58: active system-register contract contains E_PEREM")

    e_field = next(
        (field for field in trapno.get("fields", []) if field.get("name") == "E"),
        {},
    )
    if e_field.get("synchronous_exception_value") != 1:
        errors.append("v0.58: TRAPNO.E synchronous exception value must be 1")
    if e_field.get("asynchronous_interrupt_value") != 0:
        errors.append("v0.58: TRAPNO.E asynchronous interrupt value must be 0")

    econfig = system_registers.get("econfig_contract") or {}
    fields = {
        name: row.get("bit")
        for name, row in (econfig.get("fields") or {}).items()
        if isinstance(row, dict)
    }
    if fields != EXPECTED_V058_FIRST_USE_ECONFIG_BITS:
        errors.append(f"v0.58: ECONFIG field map mismatch: {fields}")
    if econfig.get("reset_value") != "0x0000000300000008":
        errors.append("v0.58: ECONFIG reset must be 0x0000000300000008")
    if econfig.get("reserved_ranges") != [[4, 31], [34, 63]]:
        errors.append("v0.58: ECONFIG reserved ranges must be [[4, 31], [34, 63]]")
    if econfig.get("reserved_write") != "must-zero":
        errors.append("v0.58: ECONFIG reserved writes must be must-zero")
    if econfig.get("reserved_read") != "zero":
        errors.append("v0.58: ECONFIG reserved reads must be zero")
    if econfig.get("per_hardware_thread") is not True:
        errors.append("v0.58: ECONFIG must be per hardware thread")


def _validate_first_use_semantics_contract(
    spec: Dict[str, Any], errors: List[str]
) -> None:
    if str(spec.get("version") or "") != "0.58.1":
        return

    conventions = spec.get("semantics_conventions") or {}
    first_use = conventions.get("extension_first_use") or {}
    if first_use.get("trap") != EXPECTED_V058_FIRST_USE_TRAP:
        errors.append("v0.58: extension-first-use trap envelope mismatch")
    if first_use.get("source_acr") != 2 or first_use.get("manager_acr") != 1:
        errors.append("v0.58: extension-first-use ACR route must be ACR2 to ACR1")
    if first_use.get("kinds") != {"VECTOR": 0, "CUBE": 1}:
        errors.append("v0.58: extension-first-use kind map mismatch")
    if first_use.get("vector_headers") != EXPECTED_V058_FIRST_USE_VECTOR_HEADERS:
        errors.append("v0.58: extension-first-use VECTOR header set mismatch")
    if first_use.get("cube_membership") != (
        "state.pto_ops.operations entries with family=CUBE and engine=CUBE"
    ):
        errors.append("v0.58: extension-first-use CUBE membership source mismatch")
    if first_use.get("ordering") != [
        "legal-decode",
        "acr-permission",
        "first-use",
        "resource-allocation",
        "effects",
    ]:
        errors.append("v0.58: extension-first-use ordering mismatch")
    if first_use.get("zero_effects") != [
        "BARG",
        "BSTATE",
        "queues",
        "memory-requests",
        "completion-state",
    ]:
        errors.append("v0.58: extension-first-use zero-effect set mismatch")

    mnemonics = {str(item.get("mnemonic") or "") for item in spec.get("instructions", [])}
    missing_headers = set(EXPECTED_V058_FIRST_USE_VECTOR_HEADERS) - mnemonics
    if missing_headers:
        errors.append(
            f"v0.58: extension-first-use VECTOR headers missing: {sorted(missing_headers)}"
        )
    if {"BSTART.VEC", "BSTART.SFU"} & set(first_use.get("vector_headers") or []):
        errors.append("v0.58: TEPL VEC/SFU aliases must not trigger VECTOR first use")

    state = spec.get("state") or {}
    pto_ops = (state.get("pto_ops") or {}).get("operations") or []
    cube_ops = [
        operation
        for operation in pto_ops
        if operation.get("family") == "CUBE" and operation.get("engine") == "CUBE"
    ]
    if len(cube_ops) != 12:
        errors.append(f"v0.58: expected 12 derived CUBE first-use operations, got {len(cube_ops)}")
    cube_count = ((state.get("engine_ops") or {}).get("semantic_engine_counts") or {}).get(
        "CUBE"
    )
    if cube_count != 12:
        errors.append(f"v0.58: engine CUBE count must be 12, got {cube_count!r}")


def validate(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    errors: List[str] = []

    # ---------------------------------------------------------------------
    # Legacy v0.2 bring-up profile sanity checks (system/privileged contract).
    # These only activate when version == "0.2" and are inert for v0.57+.
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

    _validate_first_use_register_contract(spec, errors)
    _validate_first_use_semantics_contract(spec, errors)

    _validate_engine_ops(spec, errors)

    compiled_fields = _validate_field_definitions(spec, errors)

    _validate_frame_template_contract(spec, errors)

    retired = spec.get("retired_encodings")
    retired_entries = retired.get("entries") if isinstance(retired, dict) else None
    if not isinstance(retired_entries, list):
        errors.append("missing compiled retired_encodings.entries")
    else:
        retired_names = {str(entry.get("retired_mnemonic") or "") for entry in retired_entries}
        expected_retired = (
            set()
            if str(spec.get("version") or "") in {"0.58.0", "0.58.1"}
            else {"B.IOD", "BSTART.PAR"}
        )
        if retired_names != expected_retired:
            errors.append(
                f"retired encoding identities must be exactly {sorted(expected_retired)}, got {retired_names}"
            )

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
        root / "docs" / "architecture" / "v0.58-architecture-contract.md",
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
        choices=["v0.57", "v0.58"],
        default="v0.58",
        help="ISA profile for default --spec path",
    )
    ap.add_argument(
        "--spec",
        default=None,
        help="Path to the generated ISA spec JSON",
    )
    args = ap.parse_args()

    default_spec = f"isa/{args.profile}/linxisa-{args.profile}.json"
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
