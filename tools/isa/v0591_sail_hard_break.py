#!/usr/bin/env python3
"""Generate and verify the PTO reservation guards for the 0.59.1 Sail decoder."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "isa/v0.59/linxisa-v0.59.json"
RESERVATIONS = ROOT / "isa/v0.59/state/extension_encoding_reservations.json"

OBSOLETE_NAMED = frozenset(
    {
        "BSTART.MPAR",
        "BSTART.MSEQ",
        "C.BSTART.MPAR",
        "C.BSTART.MSEQ",
        "BSTART.VPAR",
        "BSTART.VSEQ",
        "C.BSTART.VPAR",
        "C.BSTART.VSEQ",
        "B.TEXT",
    }
)
RESERVED_NAMES = frozenset({"V.*", *OBSOLETE_NAMED})
EXPECTED_INSTRUCTION_COUNT = 1306


def is_obsolete(mnemonic: str) -> bool:
    return mnemonic.startswith("V.") or mnemonic in OBSOLETE_NAMED


def validate_catalog(spec: dict[str, Any]) -> None:
    instructions = spec.get("instructions", [])
    obsolete = [
        row.get("id", row.get("mnemonic"))
        for row in instructions
        if is_obsolete(str(row.get("mnemonic", "")))
    ]
    if obsolete:
        raise ValueError(
            f"v0.59.1 catalog still contains {len(obsolete)} obsolete forms"
        )
    if len(instructions) != EXPECTED_INSTRUCTION_COUNT:
        raise ValueError(
            f"v0.59.1 catalog has {len(instructions)} forms; expected {EXPECTED_INSTRUCTION_COUNT}"
        )


def reservations(path: Path = RESERVATIONS) -> tuple[dict[str, Any], ...]:
    document = json.loads(path.read_text(encoding="utf-8"))
    selected: dict[str, dict[str, Any]] = {}
    for record in document["reservations"]:
        name = str(record["mnemonic"])
        if name not in RESERVED_NAMES:
            continue
        if record.get("status") != "reserved-in-pto":
            raise ValueError(f"{name}: encoding is not reserved in PTO")
        parts = tuple(
            {
                "index": index,
                "width_bits": int(part["width_bits"]),
                "mask": int(str(part["mask"]), 0),
                "match": int(str(part["match"]), 0),
            }
            for index, part in enumerate(record["encoding"])
        )
        if any(part["match"] & ~part["mask"] for part in parts):
            raise ValueError(f"{name}: match sets bits outside the mask")
        if sum(part["width_bits"] for part in parts) != int(record["length_bits"]):
            raise ValueError(f"{name}: reservation width differs")
        selected[name] = {
            "mnemonic": name,
            "length_bits": int(record["length_bits"]),
            "parts": parts,
        }
    if set(selected) != RESERVED_NAMES or len(selected) != 10:
        raise ValueError("v0.59.1 must own exactly the ten PTO reservation records")
    return tuple(selected[name] for name in sorted(selected))


def _function_span(value: str, name: str) -> tuple[int, int, str]:
    marker = f"function {name}("
    start = value.find(marker)
    if start < 0:
        raise ValueError(f"generated Sail decoder is missing {name}")
    open_brace = value.find("{", start)
    depth = 0
    for index in range(open_brace, len(value)):
        if value[index] == "{":
            depth += 1
        elif value[index] == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1, value[open_brace + 1 : index]
    raise ValueError(f"generated Sail decoder has an unterminated {name}")


def _reservation_condition(entry: dict[str, Any]) -> str:
    width = entry["length_bits"]
    if width == 64:
        clauses = []
        for part in entry["parts"]:
            high = 63 - 32 * int(part["index"])
            low = high - int(part["width_bits"]) + 1
            clauses.append(
                f"(inst[{high}..{low}] & 0x{int(part['mask']):08x}) == 0x{int(part['match']):08x}"
            )
        return " & ".join(f"({clause})" for clause in clauses)
    part = entry["parts"][0]
    digits = width // 4
    return f"(inst & 0x{int(part['mask']):0{digits}x}) == 0x{int(part['match']):0{digits}x}"


def harden_decoder(value: str) -> str:
    if "function decode_vec_reg_selector(" in value:
        start, end, _ = _function_span(value, "decode_vec_reg_selector")
        while end < len(value) and value[end] == "\n":
            end += 1
        value = value[:start] + value[end:]
    bior_guard = "    if inst[26] == 0b1 then trap_illegal_inst(read_pc_or_tpc()) else {\n      // B.IOR"
    if value.count(bior_guard) != 1:
        raise ValueError("generated Sail decoder B.IOR guard differs")
    value = value.replace(bior_guard, "    // B.IOR")
    old_bior_call = (
        "      set_decoded_bior(regsrc0, regsrc1, regsrc2, regdst);\n"
        "      exec_b_ior()\n"
        "    }\n"
        "  }\n"
        "  else {"
    )
    new_bior_call = (
        "      set_decoded_bior(regsrc0, regsrc1, regsrc2, regdst, execmaskpresent);\n"
        "      exec_b_ior()\n"
        "  }\n"
        "  else {"
    )
    if value.count(old_bior_call) != 1:
        raise ValueError("generated Sail decoder B.IOR dispatch differs")
    value = value.replace(old_bior_call, new_bior_call)
    by_width: dict[int, list[dict[str, Any]]] = {16: [], 32: [], 64: []}
    for entry in reservations():
        by_width[entry["length_bits"]].append(entry)
    for width in (16, 32, 64):
        name = f"decode_execute{width}"
        start, end, body = _function_span(value, name)
        guards = []
        for index, entry in enumerate(by_width[width]):
            prefix = "if" if index == 0 else "else if"
            guards.append(
                f"  {prefix} {_reservation_condition(entry)} then {{\n"
                f"    // PTO reserved in v0.59.1: {entry['mnemonic']}\n"
                "    trap_illegal_inst(read_pc_or_tpc())\n"
                "  }"
            )
        original = body.strip("\n")
        wrapped = (
            f"function {name}(inst : bits({width})) -> unit = {{\n"
            + "\n".join(guards)
            + "\n  else {\n"
            + "\n".join("    " + line for line in original.splitlines())
            + "\n  }\n}"
        )
        value = value[:start] + wrapped + value[end:]
    return value


def verify_hardened_tree(root: Path) -> None:
    execute = (root / "model/execute/execute.sail").read_text(encoding="utf-8")
    state = (root / "model/state/state.sail").read_text(encoding="utf-8")
    decode = (root / "model/decode/decode.sail").read_text(encoding="utf-8")
    forbidden = {
        "V execution": r"\bfunction exec_v_",
        "vector arithmetic helper": r"\bfunction vec_(?:int|fp)_",
        "VGPR state": r"\bregister vreg\d+\b",
        "vector BSTART": r"\bfunction exec_(?:c_)?bstart_(?:mpar|mseq|vpar|vseq)\b",
        "B.TEXT execution": r"\bfunction exec_b_text\b",
        "RI binding": r"\bri_binding_",
    }
    combined = execute + "\n" + state
    present = [
        label for label, pattern in forbidden.items() if re.search(pattern, combined)
    ]
    if present:
        raise ValueError("v0.59.1 Sail export retains " + ", ".join(present))
    for entry in reservations():
        marker = f"PTO reserved in v0.59.1: {entry['mnemonic']}"
        if decode.count(marker) != 1:
            raise ValueError(
                f"v0.59.1 decoder does not own exactly one {entry['mnemonic']} guard"
            )
    for name in ("exec_xb", "exec_esave", "exec_ercov"):
        start = execute.find(f"function {name}(")
        end = execute.find("\n}\n", start)
        if (
            start < 0
            or end < 0
            or "trap_illegal_inst(read_pc_or_tpc())" not in execute[start:end]
        ):
            raise ValueError(f"v0.59.1 {name} does not reject before effects")


__all__ = [
    "EXPECTED_INSTRUCTION_COUNT",
    "OBSOLETE_NAMED",
    "harden_decoder",
    "is_obsolete",
    "reservations",
    "validate_catalog",
    "verify_hardened_tree",
]
