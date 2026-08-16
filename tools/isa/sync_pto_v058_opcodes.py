#!/usr/bin/env python3
"""Replace PTO-owned opcode rows with the locked PTO 0.58 catalog."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from build_golden import effective_pto_encoding, singleton_pto_fields


ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "isa/v0.58"
TARGETS = {
    16: PROFILE / "opcodes/lx_c.opc",
    32: PROFILE / "opcodes/lx_32.opc",
    48: PROFILE / "opcodes/lx_hl48.opc",
    64: PROFILE / "opcodes/lx_64_prefix.opc",
}
GENERATED_MARKER = "# PTO ISA 0.58.1 canonical scalar and command forms"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def reservation_covers(reservation: dict[str, Any], instruction: dict[str, Any]) -> bool:
    reserved = reservation.get("encoding", [])
    concrete = instruction.get("encoding", {}).get("parts", [])
    if len(reserved) != len(concrete):
        return False
    return all(
        int(reserved_part["width_bits"]) == int(concrete_part["width_bits"])
        and int(concrete_part["mask"], 0) & int(reserved_part["mask"], 0)
        == int(reserved_part["mask"], 0)
        and int(concrete_part["match"], 0) & int(reserved_part["mask"], 0)
        == int(reserved_part["match"], 0)
        for reserved_part, concrete_part in zip(reserved, concrete)
    )


def classify_owned_instruction(
    instruction: dict[str, Any],
    *,
    scalar_form_ids: set[str],
    command_form_ids: set[str],
    reservations: list[dict[str, Any]],
) -> str:
    """Classify one formerly PTO-owned row for the current profile rebuild."""
    source_form_id = str(instruction.get("pto_source_form_id") or "")
    if source_form_id in scalar_form_ids or source_form_id in command_form_ids:
        return "replace"
    if any(reservation_covers(reservation, instruction) for reservation in reservations):
        return "preserve"
    return "drop"


def current_owned_lines(
    scalar_catalog: dict[str, Any],
    command_catalog: dict[str, Any],
    reservations: dict[str, Any],
) -> tuple[dict[Path, set[int]], dict[Path, list[str]]]:
    """Locate the currently projected PTO rows in the active v0.58 files."""
    spec = load(PROFILE / "linxisa-v0.58.json")
    scalar_form_ids = {str(form["form_id"]) for form in scalar_catalog["forms"]}
    command_form_ids = {str(form["form_id"]) for form in command_catalog["forms"]}
    reserved_entries = reservations["reservations"]
    result: dict[Path, set[int]] = {}
    preserved: dict[Path, list[str]] = {}
    source_lines: dict[Path, list[str]] = {}
    for instruction in spec["instructions"]:
        is_canonical_form = bool(instruction.get("pto_source_form_id"))
        is_command_variant = bool(instruction.get("pto_source_form_variant"))
        if not (is_canonical_form or is_command_variant):
            continue
        action = classify_owned_instruction(
            instruction,
            scalar_form_ids=scalar_form_ids,
            command_form_ids=command_form_ids,
            reservations=reserved_entries,
        )
        source = instruction["source"]
        relative = Path(str(source["file"]))
        lines = source_lines.setdefault(
            relative, (PROFILE / relative).read_text(encoding="utf-8").splitlines()
        )
        asm_token = '"asm":' + json.dumps(
            str(instruction.get("asm") or ""), ensure_ascii=False, separators=(",", ":")
        )
        matching_lines = [line for line in lines if asm_token in line]
        if action == "preserve" and not is_command_variant:
            if not matching_lines:
                repository_path = PROFILE.relative_to(ROOT) / relative
                committed = subprocess.check_output(
                    ["git", "show", f"HEAD:{repository_path.as_posix()}"],
                    cwd=ROOT,
                    text=True,
                ).splitlines()
                matching_lines = [line for line in committed if asm_token in line]
            if len(matching_lines) != 1:
                raise ValueError(
                    f"cannot identify the unique retained Linx extension row for {instruction.get('asm')!r}"
                )
            preserved.setdefault(relative, []).append(matching_lines[0])
            continue
        line_number = int(source["line"])
        if 1 <= line_number <= len(lines) and asm_token in lines[line_number - 1]:
            result.setdefault(relative, set()).add(line_number)
    return result, preserved


def field_bits(form: dict[str, Any], part_index: int) -> dict[int, tuple[str, int]]:
    result: dict[int, tuple[str, int]] = {}
    part_base = part_index * 32
    part_width = form["encoding"][part_index]["width_bits"]
    for field in form["fields"]:
        for piece in field["pieces"]:
            global_lsb = int(piece["instruction_lsb"])
            if not (part_base <= global_lsb < part_base + part_width):
                continue
            local_lsb = global_lsb - part_base
            for offset in range(int(piece["width"])):
                bit = local_lsb + offset
                if bit in result:
                    raise ValueError(f"{form['form_id']}: overlapping field bit {bit}")
                result[bit] = (str(field["name"]), int(piece["value_lsb"]) + offset)
    return result


def part_assignments(form: dict[str, Any], part: dict[str, Any]) -> str:
    width = int(part["width_bits"])
    mask = int(part["mask"], 0)
    match = int(part["match"], 0)
    fields = field_bits(form, int(part["index"]))
    labels: dict[int, tuple[str, Any]] = {}
    for bit in range(width):
        if mask & (1 << bit):
            labels[bit] = ("const", (match >> bit) & 1)
        elif bit in fields:
            labels[bit] = ("field", fields[bit])
        else:
            # PTO intentionally leaves some semantically inactive bits outside
            # the mask.  Give each such bit an explicit parser-only name so the
            # Linx opcode DSL preserves the exact upstream don't-care mask.
            labels[bit] = ("field", (f"PTOU{part['index']}_{bit}", 0))

    segments: list[tuple[int, int, tuple[str, Any]]] = []
    high = width - 1
    while high >= 0:
        kind, value = labels[high]
        low = high
        if kind == "const":
            while low > 0 and labels[low - 1][0] == "const":
                low -= 1
        else:
            name, value_bit = value
            while low > 0:
                next_kind, next_value = labels[low - 1]
                if (
                    next_kind != "field"
                    or next_value[0] != name
                    or next_value[1] != value_bit - (high - (low - 1))
                ):
                    break
                low -= 1
        segments.append((high, low, (kind, value)))
        high = low - 1

    rendered = []
    field_widths = {str(field["name"]): int(field["width"]) for field in form["fields"]}
    for high, low, (kind, value) in segments:
        lhs = str(high) if high == low else f"{high}..{low}"
        segment_width = high - low + 1
        if kind == "const":
            constant = (match >> low) & ((1 << segment_width) - 1)
            rhs = str(constant) if segment_width == 1 else f"{segment_width}'b{constant:0{segment_width}b}"
        else:
            name, high_value_bit = value
            low_value_bit = high_value_bit - segment_width + 1
            declared_width = field_widths.get(name, segment_width)
            if low_value_bit == 0 and segment_width == declared_width:
                rhs = name
            else:
                rhs = f"{name}[{high_value_bit}:{low_value_bit}]"
        rendered.append(f"{lhs}={rhs}")
    return " ".join(rendered)


def retained_call_metadata() -> dict[str, dict[str, Any]]:
    """Keep reviewed Linx CALL metadata that is not carried by the PTO catalog."""
    spec = load(ROOT / "isa/v0.57/linxisa-v0.57.json")
    keys = ("exact_relocations", "note", "operand_roles", "semantic_contract")
    return {
        str(instruction["id"]): {
            key: instruction[key] for key in keys if key in instruction
        }
        for instruction in spec["instructions"]
        if instruction.get("mnemonic") in {"BSTART CALL", "HL.BSTART CALL"}
        or (
            str(instruction.get("mnemonic") or "").startswith("L.BSTART.")
            and " CALL," in str(instruction.get("asm") or "")
        )
    }


def opcode_line(
    form: dict[str, Any],
    encoding: list[dict[str, Any]],
    variant: str | None,
    call_metadata: dict[str, dict[str, Any]],
) -> str:
    projected = dict(form)
    effective_encoding = effective_pto_encoding(form, encoding)
    projected["encoding"] = effective_encoding
    meta: dict[str, Any] = {
        "asm": form["asm"],
        "group": form["semantic_group"],
        "length_bits": form["length_bits"],
        "note": form.get("semantic_summary", "PTO ISA 0.58.1 canonical form."),
        "pto_source_constraints": form.get("constraints", []),
    }
    fixed_fields = singleton_pto_fields(form)
    if fixed_fields:
        meta["pto_source_fixed_fields"] = fixed_fields
    for key in (
        "accepted_assembly_mnemonics",
        "canonical_assembly_by_engine",
        "carrier_mnemonic",
    ):
        if key in form:
            meta[key] = form[key]
    if variant is not None:
        meta["pto_source_form_variant"] = variant
        meta["pto_source_form_variant_of"] = form["form_id"]
    meta.update(call_metadata.get(str(form["form_id"]), {}))
    mnemonic = str(form["mnemonic"])
    mnemonic_token = json.dumps(mnemonic) if any(char.isspace() for char in mnemonic) else mnemonic
    parts = " | ".join(
        part_assignments(projected, part) for part in effective_encoding
    )
    exposed_fields = {
        name
        for part in effective_encoding
        for bit, (name, _) in field_bits(projected, int(part["index"])).items()
        if not (int(part["mask"], 0) & (1 << bit))
    }
    operands = " ".join(
        str(field["name"])
        for field in form["fields"]
        if str(field["name"]) in exposed_fields
    )
    return (
        f"{mnemonic_token} [{json.dumps(meta, ensure_ascii=False, separators=(',', ':'))}] : "
        f"{parts} ; {operands} ; -"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    scalar_catalog = load(args.source_root / "spec/catalog/scalar-forms.json")
    command_catalog = load(args.source_root / "spec/catalog/command-forms.json")
    reservations = load(
        args.source_root / "spec/catalog/extension-encoding-reservations.json"
    )
    if command_catalog.get("form_count") != 74:
        raise ValueError("PTO 0.58.1 must publish exactly 74 command forms")
    if scalar_catalog.get("form_count") != 474:
        raise ValueError("PTO 0.58.1 must publish exactly 474 scalar forms")
    if reservations.get("reservation_count") != 32:
        raise ValueError("PTO 0.58.1 must publish exactly 32 extension reservations")

    removals, preserved = current_owned_lines(
        scalar_catalog, command_catalog, reservations
    )
    call_metadata = retained_call_metadata()
    generated: dict[Path, list[str]] = {target: [] for target in TARGETS.values()}
    for form in scalar_catalog["forms"] + command_catalog["forms"]:
        target = TARGETS[int(form["length_bits"])]
        generated[target].append(
            opcode_line(form, form["encoding"], None, call_metadata)
        )
        for variant in form.get("encoding_variants", []):
            generated[target].append(
                opcode_line(
                    form,
                    variant["encoding"],
                    str(variant["name"]),
                    call_metadata,
                )
            )

    for target, new_lines in generated.items():
        relative_profile_path = Path("opcodes") / target.name
        removed = removals.get(relative_profile_path, set())
        original = target.read_text(encoding="utf-8").splitlines()
        marker_index = next(
            (
                index
                for index, line in enumerate(original)
                if line.startswith("# PTO ISA 0.58.")
            ),
            len(original),
        )
        retained = [
            line
            for number, line in enumerate(original[:marker_index], 1)
            if number not in removed and line not in set(new_lines)
        ]
        while retained and not retained[-1].strip():
            retained.pop()
        for line in preserved.get(relative_profile_path, []):
            if line not in retained:
                retained.append(line)
        retained.extend(["", GENERATED_MARKER, *new_lines])
        target.write_text("\n".join(retained) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
