#!/usr/bin/env python3
"""Render and validate LinxISA instruction encodings for the HTML manual.

The renderer deliberately consumes only the compiled catalog.  The raw
``parts[].segments`` representation supplies the visible boxes, while the
independently compiled ``encoding.parts`` representation supplies mask,
match, field slices, and form constraints.  ``validate_encoding`` compares
the two before any HTML is emitted.
"""

from __future__ import annotations

from html import escape
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable
from manual_tag import tagged_json

ROOT = Path(__file__).resolve().parents[2]
TILE_MANUAL_PATH = (
    ROOT / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
)


def _hex(value: int, width_bits: int) -> str:
    return f"0x{value:0{(width_bits + 3) // 4}x}"


def _ranges(values: Iterable[int]) -> str:
    ordered = sorted(set(int(value) for value in values))
    runs: list[str] = []
    start = previous = None
    for value in ordered:
        if start is None:
            start = previous = value
        elif value == previous + 1:
            previous = value
        else:
            runs.append(str(start) if start == previous else f"{start}–{previous}")
            start = previous = value
    if start is not None:
        runs.append(str(start) if start == previous else f"{start}–{previous}")
    return ", ".join(runs)


def _piece_map(encoded_part: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    pieces: dict[tuple[int, int], dict[str, Any]] = {}
    for field in encoded_part.get("fields", []):
        for piece in field.get("pieces", []):
            key = (int(piece["insn_msb"]), int(piece["insn_lsb"]))
            if key in pieces:
                raise ValueError(f"duplicate encoded field slice [{key[0]}:{key[1]}]")
            pieces[key] = {**piece, "field_name": str(field["name"])}
    return pieces


def _norm_source_encoding(source: dict[str, Any]) -> list[tuple[int, int, int]]:
    return [
        (int(p["width_bits"]), int(p["mask"], 0), int(p["match"], 0))
        for p in source["encoding"]
    ]


def _norm_catalog_encoding(row: dict[str, Any]) -> list[tuple[int, int, int]]:
    return [
        (int(p["width_bits"]), int(p["mask"], 0), int(p["match"], 0))
        for p in row["encoding"]["parts"]
    ]


@lru_cache(maxsize=1)
def _source_forms() -> dict[str, dict[str, Any]]:
    forms: dict[str, dict[str, Any]] = {}
    for name in ("pto_scalar_forms.json", "pto_command_forms.json"):
        data = tagged_json(f"isa/v0.59/state/{name}")
        forms.update({row["form_id"]: row for row in data["forms"]})
        forms.update({row["form_id"]: row for row in data.get("scoped_forms", [])})
    return forms


def _validate_normative_source(row: dict[str, Any]) -> None:
    source_id = row.get("pto_source_form_id")
    if not source_id:
        return
    source = _source_forms().get(str(source_id))
    if source is None:
        raise ValueError(f"{row['id']}: unresolved exact PTO source form {source_id}")
    if int(source["length_bits"]) != int(row["length_bits"]):
        raise ValueError(f"{row['id']}: PTO source length differs")
    source_encoding = _norm_source_encoding(source)
    catalog_encoding = _norm_catalog_encoding(row)
    if len(source_encoding) != len(catalog_encoding):
        raise ValueError(f"{row['id']}: PTO source part count differs")
    fixed_fields = {str(f["name"]): f for f in row.get("pto_source_fixed_fields", [])}
    source_fields = {str(f["name"]): f for f in source.get("fields", [])}
    for part_index, (
        (width, source_mask, source_match),
        (_, catalog_mask, catalog_match),
    ) in enumerate(zip(source_encoding, catalog_encoding)):
        if (
            source_mask & catalog_mask != source_mask
            or source_match != catalog_match & source_mask
        ):
            raise ValueError(f"{row['id']}: PTO source fixed bits differ")
        added_mask = catalog_mask & ~source_mask
        explained_mask = 0
        explained_match = 0
        for name, fixed in fixed_fields.items():
            field = source_fields.get(name)
            if field is None:
                continue
            for piece in field.get("pieces", []):
                bit = int(piece["instruction_lsb"])
                piece_width = int(piece["width"])
                if bit >= width:
                    continue
                value_lsb = int(piece.get("value_lsb", 0))
                bits = ((1 << piece_width) - 1) << bit
                explained_mask |= bits
                explained_match |= (
                    (int(fixed["value"]) >> value_lsb) & ((1 << piece_width) - 1)
                ) << bit
        if (
            added_mask & ~explained_mask
            or catalog_match & added_mask != explained_match & added_mask
        ):
            raise ValueError(
                f"{row['id']}: specialized fixed fields do not explain PTO mask delta"
            )
    if list(source.get("constraints", [])) != list(
        row.get("pto_source_constraints", [])
    ):
        raise ValueError(f"{row['id']}: PTO source form constraints differ")
    signed_map = {"signed": True, "unsigned": False, "encoding-defined": None}
    source_field_shape = {
        str(field["name"]): (
            sum(int(piece["width"]) for piece in field.get("pieces", [])),
            signed_map.get(field.get("signedness")),
        )
        for field in source.get("fields", [])
    }
    compiled_shape: dict[str, tuple[int, Any]] = {}
    for part in row["encoding"]["parts"]:
        for field in part.get("fields", []):
            name = str(field["name"])
            old_width, old_signed = compiled_shape.get(name, (0, field.get("signed")))
            if old_signed != field.get("signed"):
                raise ValueError(
                    f"{row['id']}: inconsistent signedness across field pieces"
                )
            compiled_shape[name] = (
                old_width + sum(int(p["width"]) for p in field["pieces"]),
                old_signed,
            )
    for name, shape in compiled_shape.items():
        if source_field_shape.get(name) != shape:
            raise ValueError(
                f"{row['id']}: PTO source width/signedness differs for {name}"
            )
    fixed_names = set(fixed_fields)
    source_bit_map = {
        (
            str(field["name"]),
            int(piece["instruction_lsb"]) + index,
            int(piece.get("value_lsb", 0)) + index,
        )
        for field in source.get("fields", [])
        if str(field["name"]) not in fixed_names
        for piece in field.get("pieces", [])
        for index in range(int(piece["width"]))
    }
    compiled_bit_map: set[tuple[str, int, int]] = set()
    part_offset = 0
    for part in row["encoding"]["parts"]:
        for field in part.get("fields", []):
            if str(field["name"]) in fixed_names:
                continue
            for piece in field.get("pieces", []):
                if "value_lsb" not in piece:
                    raise ValueError(
                        f"{row['id']}: PTO compiled piece lacks value_lsb for {field['name']}"
                    )
                for index in range(int(piece["width"])):
                    compiled_bit_map.add(
                        (
                            str(field["name"]),
                            part_offset + int(piece["insn_lsb"]) + index,
                            int(piece["value_lsb"]) + index,
                        )
                    )
        part_offset += int(part["width_bits"])
    if compiled_bit_map != source_bit_map:
        missing = sorted(source_bit_map - compiled_bit_map)[:4]
        extra = sorted(compiled_bit_map - source_bit_map)[:4]
        raise ValueError(
            f"{row['id']}: PTO operand bit mapping differs; missing={missing}, extra={extra}"
        )


def validate_encoding(row: dict[str, Any], catalog: dict[str, Any]) -> None:
    """Prove that a row's raw segments and compiled encoding agree exactly."""
    mnemonic = str(row.get("mnemonic") or row.get("id") or "<unknown>")
    raw_parts = list(row.get("parts", []))
    encoded_parts = list(row.get("encoding", {}).get("parts", []))
    if len(raw_parts) != len(encoded_parts):
        raise ValueError(f"{mnemonic}: raw/compiled part count differs")

    total_width = 0
    for part_index, (raw_part, encoded_part) in enumerate(
        zip(raw_parts, encoded_parts)
    ):
        width = int(raw_part.get("width_bits", 0))
        if width <= 0 or width != int(encoded_part.get("width_bits", -1)):
            raise ValueError(f"{mnemonic}: invalid width for part {part_index}")
        if int(encoded_part.get("index", part_index)) != part_index:
            raise ValueError(f"{mnemonic}: encoded part index is out of order")
        total_width += width

        occupied = 0
        raw_mask = 0
        raw_match = 0
        dynamic_ranges: set[tuple[int, int]] = set()
        for segment in raw_part.get("segments", []):
            msb = int(segment["msb"])
            lsb = int(segment["lsb"])
            segment_width = int(segment["width"])
            if lsb < 0 or msb >= width or msb - lsb + 1 != segment_width:
                raise ValueError(
                    f"{mnemonic}: malformed part {part_index} slice [{msb}:{lsb}]"
                )
            bits = ((1 << segment_width) - 1) << lsb
            if occupied & bits:
                raise ValueError(
                    f"{mnemonic}: overlapping part {part_index} slice [{msb}:{lsb}]"
                )
            occupied |= bits
            if "const" in segment:
                value = int(segment["const"]["value"])
                if value < 0 or value >= (1 << segment_width):
                    raise ValueError(f"{mnemonic}: constant does not fit [{msb}:{lsb}]")
                raw_mask |= bits
                raw_match |= value << lsb
            else:
                dynamic_ranges.add((msb, lsb))

        if occupied != (1 << width) - 1:
            raise ValueError(
                f"{mnemonic}: part {part_index} does not cover all {width} bits"
            )
        mask = int(str(encoded_part["mask"]), 0)
        match = int(str(encoded_part["match"]), 0)
        # Imported PTO forms retain singleton fields in the raw field map and
        # fold those one-value constraints into the effective compiled
        # mask/match.  Raw constants must therefore be a subset of the
        # compiled fixed bits, and must agree wherever they overlap.
        if raw_mask & mask != raw_mask or raw_match != (match & raw_mask):
            raise ValueError(
                f"{mnemonic}: part {part_index} mask/match disagrees with raw constants"
            )

        pattern = str(encoded_part.get("pattern", "")).replace(" ", "")
        expected_pattern = "".join(
            "1"
            if mask & (1 << bit) and match & (1 << bit)
            else "0"
            if mask & (1 << bit)
            else "."
            for bit in reversed(range(width))
        )
        if pattern != expected_pattern:
            raise ValueError(
                f"{mnemonic}: part {part_index} pattern disagrees with mask/match"
            )
        if set(_piece_map(encoded_part)) != dynamic_ranges:
            raise ValueError(
                f"{mnemonic}: part {part_index} field slices disagree with raw segments"
            )

    declared_length = int(
        row.get("encoding", {}).get("length_bits", row.get("length_bits", 0))
    )
    if total_width != declared_length or total_width != int(row.get("length_bits", 0)):
        raise ValueError(
            f"{mnemonic}: part widths do not sum to the declared instruction length"
        )

    definitions = catalog.get("field_definitions", {}).get("fields", {})
    for encoded_part in encoded_parts:
        for field in encoded_part.get("fields", []):
            name = str(field["name"])
            if name not in definitions:
                raise ValueError(
                    f"{mnemonic}: field {name!r} has no catalog definition"
                )
    _validate_normative_source(row)


def validate_catalog(
    catalog: dict[str, Any], baseline_catalog: dict[str, Any] | None = None
) -> list[str]:
    """Audit the released v0.59 catalog against independent exact sources."""
    errors: list[str] = []
    if catalog.get("version") not in {"0.59.1", "0.59.1-prepublication"}:
        errors.append(f"catalog version is not v0.59.1: {catalog.get('version')}")
    lock = tagged_json("isa/v0.59/pto-spec.lock.json")
    if (
        lock.get("source", {}).get("commit")
        != "a89a53d48f5708328be609fe2e6296ac8bdb4bc2"
    ):
        errors.append("PTO source is not published v0.59.1.0 commit")
    rows = list(catalog.get("instructions", []))
    classes = {
        "scoped": [r for r in rows if r.get("encoding_kind") == "SCOPED64"],
        "pto": [
            r
            for r in rows
            if r.get("encoding_kind") != "SCOPED64" and r.get("pto_source_form_id")
        ],
        "linx": [
            r
            for r in rows
            if r.get("encoding_kind") != "SCOPED64" and not r.get("pto_source_form_id")
        ],
    }
    expected = {"scoped": 705, "pto": 578, "linx": 216}
    for kind, count in expected.items():
        if len(classes[kind]) != count:
            errors.append(f"{kind} count {len(classes[kind])} != {count}")
    for row in rows:
        try:
            validate_encoding(row, catalog)
        except ValueError as exc:
            errors.append(str(exc))
    if baseline_catalog is not None:
        baseline = {r["id"]: r for r in baseline_catalog.get("instructions", [])}
        for row in classes["linx"]:
            if baseline.get(row["id"]) != row:
                errors.append(f"{row['id']}: preserved Linx form differs from baseline")
    return errors


def _field_label(
    segment: dict[str, Any],
    piece: dict[str, Any] | None,
    effective_mask: int,
    effective_match: int,
) -> tuple[str, str, bool]:
    width = int(segment["width"])
    if "const" in segment:
        value = int(segment["const"]["value"])
        return f"{value:0{width}b}", "固定值", True
    if piece is None:
        raise ValueError("dynamic segment has no compiled field piece")
    name = str(piece["field_name"])
    lsb = int(segment["lsb"])
    segment_bits = ((1 << width) - 1) << lsb
    fixed_by_constraint = effective_mask & segment_bits == segment_bits
    if effective_mask & segment_bits and not fixed_by_constraint:
        raise ValueError(
            f"field {name!r} is only partially fixed by the effective mask"
        )
    if fixed_by_constraint:
        value = (effective_match & segment_bits) >> lsb
        return f"{name} = {value:0{width}b}", "单值约束形成的固定字段", True
    value_msb = piece.get("value_msb")
    value_lsb = piece.get("value_lsb")
    if value_msb is not None and value_lsb is not None:
        suffix = (
            f"[{int(value_msb)}]"
            if value_msb == value_lsb
            else f"[{int(value_msb)}:{int(value_lsb)}]"
        )
        return f"{name}{suffix}", "字段分片", False
    return name, "字段", False


def _constraint_text(constraint: dict[str, Any]) -> str:
    field = escape(str(constraint.get("field", "?")))
    operator = str(constraint.get("operator", constraint.get("op", "?")))
    if operator in {"one-of", "in"}:
        return f"<code>{field}</code> ∈ {{{escape(_ranges(constraint.get('values', [])))}}}"
    value = escape(str(constraint.get("value", "?")))
    symbol = {"not-equal": "≠", "!=": "≠", "equal": "=", "==": "="}.get(
        operator, operator
    )
    return f"<code>{field}</code> {escape(symbol)} <code>{value}</code>"


def _render_constraints(row: dict[str, Any], catalog: dict[str, Any]) -> str:
    source_constraints = list(row.get("pto_source_constraints") or [])
    source_fields = {
        str(constraint.get("field", "")) for constraint in source_constraints
    }
    encoded_constraints_raw = [
        constraint
        for part in row.get("encoding", {}).get("parts", [])
        for constraint in part.get("constraints", [])
        if str(constraint.get("field", "")) not in source_fields
    ]
    # Collapse compiler-expanded rejection sets back into a readable exact
    # set.  This changes presentation only; every rejected value is retained.
    grouped_not_equal: dict[str, list[int]] = {}
    encoded_constraints: list[dict[str, Any]] = []
    for constraint in encoded_constraints_raw:
        operator = str(constraint.get("operator", constraint.get("op", "")))
        if operator in {"not-equal", "!="}:
            grouped_not_equal.setdefault(str(constraint.get("field", "?")), []).append(
                int(constraint["value"])
            )
        else:
            encoded_constraints.append(constraint)
    for field, values in grouped_not_equal.items():
        encoded_constraints.append(
            {"field": field, "operator": "not-one-of", "values": values}
        )
    fixed_fields = list(row.get("pto_source_fixed_fields") or [])
    field_names = {
        str(field["name"])
        for part in row.get("encoding", {}).get("parts", [])
        for field in part.get("fields", [])
    }
    if not source_constraints and not encoded_constraints and not fixed_fields:
        return ""

    items: list[str] = []
    seen: set[str] = set()
    for constraint in source_constraints + encoded_constraints:
        if constraint.get("operator") == "not-one-of":
            text = (
                f"<code>{escape(str(constraint['field']))}</code> ∉ "
                f"{{{escape(_ranges(constraint['values']))}}}"
            )
        else:
            text = _constraint_text(constraint)
        if text not in seen:
            seen.add(text)
            items.append(f"<li>{text}</li>")
    for field in fixed_fields:
        width = int(field["width"])
        value = int(field["value"])
        text = (
            f"源定义固定字段 <code>{escape(str(field['name']))}</code> = "
            f"<code>{value:#x}</code>（{width} bit）"
        )
        if text not in seen:
            seen.add(text)
            items.append(f"<li>{text}</li>")
    return (
        '<section class="encoding-constraints"><h4>编码约束</h4><ul>'
        + "".join(items)
        + "</ul></section>"
    )


def _render_field_table(row: dict[str, Any]) -> str:
    fields: dict[str, dict[str, Any]] = {}
    for part in row["encoding"]["parts"]:
        for field in part.get("fields", []):
            fields.setdefault(str(field["name"]), field)
    if not fields:
        return ""
    rows = []
    for name, field in fields.items():
        pieces = ", ".join(
            f"{p['insn_msb']}:{p['insn_lsb']}"
            if p["insn_msb"] != p["insn_lsb"]
            else str(p["insn_lsb"])
            for p in field["pieces"]
        )
        width = sum(int(p["width"]) for p in field["pieces"])
        signed = {True: "signed", False: "unsigned", None: "encoding-defined"}.get(
            field.get("signed"), str(field.get("signed"))
        )
        rows.append(
            f"<tr><td><code>{escape(name)}</code></td><td>{width}</td><td><code>{escape(pieces)}</code></td><td>{signed}</td></tr>"
        )
    return (
        '<table class="encoding-operands"><thead><tr><th>Field</th><th>Width</th><th>Instruction bits</th><th>Signedness</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table>"
    )


def _render_tepl_selectors(row: dict[str, Any]) -> str:
    if row.get("mnemonic") != "BSTART.TEPL":
        return ""
    operations = [
        op
        for op in tagged_json("isa/v0.59/state/pto_tile_operations.json")["operations"]
        if op.get("family") == "TEPL"
    ]
    references = {
        op["mnemonic"]: op
        for op in json.loads(TILE_MANUAL_PATH.read_text(encoding="utf-8"))["operations"]
    }
    if len(operations) != 79:
        raise ValueError(
            f"BSTART.TEPL: expected 79 published selectors, found {len(operations)}"
        )
    used = {(int(op["mode"]), int(op["function"])) for op in operations}
    if len(used) != len(operations):
        raise ValueError("BSTART.TEPL: duplicate published Mode/Function pair")
    rows = []
    for op in sorted(
        operations, key=lambda item: (int(item["mode"]), int(item["function"]))
    ):
        ref = references[op["name"]]
        rows.append(
            f"<tr><td><code>{op['mode']}</code></td><td><code>{op['function']}</code></td>"
            f'<td><code>{escape(str(op["selector"]))}</code></td><td><a href="{escape(ref["source_url"], quote=True)}">'
            f"{escape(op['name'])}</a></td><td>{escape(op['engine'])}</td></tr>"
        )
    reserved = 128 - len(used)
    return (
        '<section class="tepl-selectors"><h4>Published Mode/Function selectors</h4>'
        f"<p>The published PTO 0.59.1 operation set assigns {len(used)} of 128 composite selectors. "
        f"The remaining {reserved} unlisted Mode/Function pairs are reserved.</p>"
        "<table><thead><tr><th>Mode</th><th>Function</th><th>Selector</th><th>Operation</th><th>Engine</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></section>"
    )


def render_encoding(row: dict[str, Any], catalog: dict[str, Any]) -> str:
    """Return a self-contained HTML fragment for one catalog instruction form."""
    validate_encoding(row, catalog)
    raw_parts = list(row["parts"])
    encoded_parts = list(row["encoding"]["parts"])
    part_html: list[str] = []
    logical_offset = 0
    for part_index, (raw_part, encoded_part) in enumerate(
        zip(raw_parts, encoded_parts)
    ):
        width = int(raw_part["width_bits"])
        pieces = _piece_map(encoded_part)
        cells: list[str] = []
        for segment in sorted(
            raw_part["segments"], key=lambda item: int(item["msb"]), reverse=True
        ):
            msb = int(segment["msb"])
            lsb = int(segment["lsb"])
            segment_width = int(segment["width"])
            effective_mask = int(str(encoded_part["mask"]), 0)
            effective_match = int(str(encoded_part["match"]), 0)
            label, kind, is_fixed = _field_label(
                segment, pieces.get((msb, lsb)), effective_mask, effective_match
            )
            css_kind = "fixed" if is_fixed else "variable"
            cells.append(
                f'<div class="encoding-field {css_kind}" style="--field-width:{segment_width}" '
                f'title="{escape(kind)}，bit {msb}:{lsb}">'
                f'<span class="encoding-bit-range">{msb}'
                + (f":{lsb}" if msb != lsb else "")
                + f"</span><code>{escape(label)}</code></div>"
            )
        mask = int(str(encoded_part["mask"]), 0)
        match = int(str(encoded_part["match"]), 0)
        logical_msb = logical_offset + width - 1
        part_html.append(
            f'<section class="encoding-part" data-part="{part_index}">'
            f'<div class="encoding-part-heading"><strong>Part {part_index}</strong>'
            f"<span>{width} bit · 逻辑位 [{logical_msb}:{logical_offset}]</span></div>"
            f'<div class="encoding-fields" style="--encoding-width:{width}">{"".join(cells)}</div>'
            f'<dl class="encoding-exact"><div><dt>Mask</dt><dd><code>{_hex(mask, width)}</code></dd></div>'
            f"<div><dt>Match</dt><dd><code>{_hex(match, width)}</code></dd></div>"
            f"<div><dt>Pattern</dt><dd><code>{escape(str(encoded_part['pattern']))}</code></dd></div></dl>"
            f"</section>"
        )
        logical_offset += width

    ordering = ""
    if len(raw_parts) > 1:
        ordering = (
            '<p class="encoding-order">Catalog 顺序为 Part 0 → Part 1。'
            "Part 0 先出现在指令流中，并占据组合编码的最低逻辑位。</p>"
        )
    return (
        '<div class="instruction-encoding">'
        f'<div class="encoding-summary"><span>{int(row["length_bits"])} bit</span>'
        f"<span>{escape(str(row.get('encoding_kind', '')))}</span></div>"
        + ordering
        + "".join(part_html)
        + _render_field_table(row)
        + _render_constraints(row, catalog)
        + _render_tepl_selectors(row)
        + "</div>"
    )


__all__ = ["render_encoding", "validate_encoding", "validate_catalog"]
