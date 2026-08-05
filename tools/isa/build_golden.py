#!/usr/bin/env python3
"""
Build the compiled LinxISA catalog from the multi-file golden sources.

Golden sources live under:
  isa/<profile>/

Compiled output is checked in at:
  isa/<profile>/linxisa-<profile>.json

This builder is intentionally deterministic:
  - no timestamps
  - stable instruction IDs derived from mnemonic + raw segments
  - stable ordering of files and instructions
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


_RE_CNST_BIN = re.compile(r"^(?P<w>\d+)'b(?P<bits>[01_]+)$")
_RE_CNST_HEX = re.compile(r"^(?P<w>\d+)'h(?P<hex>[0-9a-fA-F_]+)$")
_RE_CNST_DEC = re.compile(r"^(?P<w>\d+)'d(?P<dec>[0-9_]+)$")
_RE_FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_#]*$")
_RE_CONSTRAINT = re.compile(
    r"^(?P<field>[A-Za-z_][A-Za-z0-9_#]*)\s*(?P<op>!=|==|<=|>=|<|>)\s*(?P<value>.+?)\s*$"
)
_RE_FIELD_SLICE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_#]*)(?:\[(?P<msb>\d+):(?P<lsb>\d+)\])?$")


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, obj: Any, pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if pretty:
        text = json.dumps(obj, sort_keys=True, indent=2) + "\n"
    else:
        text = json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")


def _hex_width(val: int, width_bits: int) -> str:
    hex_digits = (width_bits + 3) // 4
    return f"0x{val:0{hex_digits}x}"


def _parse_int_value(s: str) -> int:
    s = s.strip()
    if s.startswith("0x") or s.startswith("0X"):
        return int(s, 16)
    if s.startswith("0b") or s.startswith("0B"):
        return int(s, 2)
    return int(s, 10)


def _parse_const_token(token: str, width_bits: int) -> Optional[Dict[str, Any]]:
    """
    Return {"width": width_bits, "value": int} for constant-like tokens, else None.

    We accept:
      - Verilog-style: 3'b010, 7'h1f, 12'd123
      - plain: 0, 13, 0x1f, 0b101
    """
    t = token.strip()
    if not t:
        return None

    # Allow annotated constants such as `5'b0_1010(RA)` in the opcode databases.
    # The parenthetical is an annotation (e.g. register alias), not part of the value.
    t = re.sub(r"\([^)]+\)$", "", t).strip()

    m = _RE_CNST_BIN.match(t)
    if m:
        w = int(m.group("w"))
        bits = m.group("bits").replace("_", "")
        value = int(bits or "0", 2)
        return {"width": w, "value": value}

    m = _RE_CNST_HEX.match(t)
    if m:
        w = int(m.group("w"))
        hx = m.group("hex").replace("_", "")
        value = int(hx or "0", 16)
        return {"width": w, "value": value}

    m = _RE_CNST_DEC.match(t)
    if m:
        w = int(m.group("w"))
        dec = m.group("dec").replace("_", "")
        value = int(dec or "0", 10)
        return {"width": w, "value": value}

    # plain ints; interpret as value with the segment width
    try:
        value = _parse_int_value(t)
    except ValueError:
        return None
    return {"width": int(width_bits), "value": int(value)}


def _pattern_to_mask_match(pattern: str) -> Tuple[int, int]:
    # pattern is MSB->LSB with '0','1','.'
    width_bits = len(pattern)
    mask = 0
    match = 0
    for i, ch in enumerate(pattern):
        bit = width_bits - 1 - i
        if ch == ".":
            continue
        if ch not in ("0", "1"):
            raise ValueError(f"invalid pattern char {ch!r}")
        mask |= 1 << bit
        if ch == "1":
            match |= 1 << bit
    return mask, match


def _load_uop_class_map(uop_root: Path) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    if not uop_root.exists():
        return out
    for p in sorted(uop_root.rglob("*.json")):
        if p.name in {"index.json", "_index.json"}:
            continue
        obj = _read_json(p)
        big = str(obj.get("big_kind") or "").strip()
        entries = obj.get("instructions", []) or []
        declared_count = obj.get("count")
        if declared_count is not None and int(declared_count) != len(entries):
            raise ValueError(f"{p}: count={declared_count} does not match {len(entries)} instruction entries")
        for it in entries:
            m = str(it.get("mnemonic") or "").strip()
            if not m:
                continue
            if m in out:
                raise ValueError(f"{p}: duplicate uop classification for {m}")
            out[m] = {
                "big_kind": big,
                "class": it.get("class") or {},
                "group": str(it.get("group") or "").strip(),
            }
    return out


def _uop_group_str(u: Dict[str, Any]) -> str:
    big = str(u.get("big_kind") or "").strip() or "-"
    cls = u.get("class") or {}
    if big == "AGU":
        agu_kind = str(cls.get("agu_kind") or "").strip()
        addr_mode = str(cls.get("addr_mode") or "").strip()
        if agu_kind and addr_mode:
            return f"{agu_kind}/{addr_mode}"
        if agu_kind:
            return agu_kind
    uk = str(cls.get("uop_kind") or "").strip()
    if uk and uk != big:
        return f"{big}/{uk}"
    return big


def _augment_with_uop_classification(in_dir: Path, instructions: List[Dict[str, Any]]) -> None:
    # Profile convention: isa/<profile>/uop_classification_<profile>/
    profile_name = in_dir.name
    uop_root = in_dir / f"uop_classification_{profile_name}"
    uop_map = _load_uop_class_map(uop_root)
    instruction_mnemonics = {str(inst.get("mnemonic") or "").strip() for inst in instructions}
    missing = sorted(instruction_mnemonics - set(uop_map))
    extra = sorted(set(uop_map) - instruction_mnemonics)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing={missing}")
        if extra:
            details.append(f"extra={extra}")
        raise ValueError(f"uop classification must cover canonical mnemonics exactly: {'; '.join(details)}")
    for inst in instructions:
        m = str(inst.get("mnemonic") or "").strip()
        u = uop_map.get(m)
        if not u:
            continue
        inst["uop_class"] = u.get("class") or {}
        inst["uop_big_kind"] = str(u.get("big_kind") or "").strip()
        inst["uop_group"] = _uop_group_str(u)


def _compile_field_definitions(in_dir: Path, instructions: List[Dict[str, Any]]) -> Dict[str, Any]:
    source = _read_json(in_dir / "encoding" / "fields.json")
    definitions = source.get("fields")
    if not isinstance(definitions, dict):
        raise ValueError("encoding/fields.json: fields must be an object")

    observed: Dict[str, Dict[str, Any]] = {}
    for inst in instructions:
        for part in inst.get("encoding", {}).get("parts", []):
            for field in part.get("fields", []):
                name = str(field.get("name") or "").strip()
                width = sum(int(piece.get("width") or 0) for piece in field.get("pieces", []))
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
    if missing or unknown:
        details = []
        if missing:
            details.append(f"missing={missing}")
        if unknown:
            details.append(f"unknown={unknown}")
        raise ValueError(
            "encoding/fields.json must define every observed field exactly: "
            + "; ".join(details)
        )

    compiled: Dict[str, Any] = {}
    for name in sorted(definitions):
        seen = observed.get(name)
        entry = definitions[name]
        if not isinstance(entry, dict):
            raise ValueError(f"encoding/fields.json: fields.{name} must be an object")
        allowed_keys = {
            "allowed_values",
            "description",
            "documented_only",
            "namespace",
            "reserved_ranges",
            "reserved_values",
            "scale",
            "signed",
            "widths",
        }
        extra_keys = sorted(set(entry) - allowed_keys)
        if extra_keys:
            raise ValueError(f"encoding/fields.json: fields.{name} has unknown keys {extra_keys}")

        widths = entry.get("widths")
        if (
            not isinstance(widths, list)
            or not widths
            or not all(isinstance(width, int) and width > 0 for width in widths)
            or widths != sorted(set(widths))
        ):
            raise ValueError(
                f"encoding/fields.json: fields.{name}.widths must be a sorted, unique list of positive integers"
            )
        documented_only = entry.get("documented_only", False)
        if not isinstance(documented_only, bool):
            raise ValueError(f"encoding/fields.json: fields.{name}.documented_only must be boolean")
        if seen is None and not documented_only:
            raise ValueError(f"encoding/fields.json: fields.{name} is unobserved without documented_only=true")
        if seen is not None and documented_only:
            raise ValueError(f"encoding/fields.json: fields.{name} is observed and cannot be documented_only")
        observed_widths = sorted(seen["widths"]) if seen is not None else widths
        if widths != observed_widths:
            raise ValueError(
                f"encoding/fields.json: fields.{name}.widths={widths} "
                f"does not match observed {observed_widths}"
            )

        namespace = entry.get("namespace")
        valid_namespaces = {"immediate", "operand", "register-or-identifier", "reserved", "selector"}
        if namespace not in valid_namespaces:
            raise ValueError(
                f"encoding/fields.json: fields.{name}.namespace must be one of {sorted(valid_namespaces)}"
            )

        signed = entry.get("signed")
        if namespace == "immediate":
            if not isinstance(signed, bool):
                raise ValueError(
                    f"encoding/fields.json: fields.{name}.signed must be explicit for immediate fields"
                )
            scale = entry.get("scale")
            if not isinstance(scale, int) or isinstance(scale, bool) or scale <= 0:
                raise ValueError(
                    f"encoding/fields.json: fields.{name}.scale must be a positive integer"
                )
        elif "scale" in entry:
            raise ValueError(
                f"encoding/fields.json: fields.{name}.scale is only valid for immediate fields"
            )

        if seen is not None and len(seen["signed"]) == 1 and signed is not next(iter(seen["signed"])):
            raise ValueError(
                f"encoding/fields.json: fields.{name}.signed={signed!r} disagrees with opcode signedness"
            )

        reserved_values = entry.get("reserved_values")
        if namespace == "selector":
            if not isinstance(reserved_values, list) or not all(
                isinstance(value, int) and not isinstance(value, bool) and value >= 0
                for value in reserved_values
            ):
                raise ValueError(
                    f"encoding/fields.json: fields.{name}.reserved_values must be a list of non-negative integers"
                )
            if len(reserved_values) != len(set(reserved_values)):
                raise ValueError(
                    f"encoding/fields.json: fields.{name}.reserved_values contains duplicates"
                )
            maximum = (1 << min(widths)) - 1
            if any(value > maximum for value in reserved_values):
                raise ValueError(
                    f"encoding/fields.json: fields.{name}.reserved_values must fit every declared width"
                )
            reserved_ranges = entry.get("reserved_ranges", [])
            if not isinstance(reserved_ranges, list) or not all(
                isinstance(item, list)
                and len(item) == 2
                and all(isinstance(value, int) and not isinstance(value, bool) for value in item)
                and 0 <= item[0] <= item[1] <= maximum
                for item in reserved_ranges
            ):
                raise ValueError(
                    f"encoding/fields.json: fields.{name}.reserved_ranges must contain [lo, hi] pairs that fit every width"
                )
            ordered_ranges = sorted((item[0], item[1]) for item in reserved_ranges)
            if any(right[0] <= left[1] for left, right in zip(ordered_ranges, ordered_ranges[1:])):
                raise ValueError(
                    f"encoding/fields.json: fields.{name}.reserved_ranges overlap"
                )
            if any(any(lo <= value <= hi for lo, hi in ordered_ranges) for value in reserved_values):
                raise ValueError(
                    f"encoding/fields.json: fields.{name} repeats a reserved value inside reserved_ranges"
                )
        elif "reserved_values" in entry:
            raise ValueError(
                f"encoding/fields.json: fields.{name}.reserved_values is only valid for selector fields"
            )
        elif "reserved_ranges" in entry:
            raise ValueError(
                f"encoding/fields.json: fields.{name}.reserved_ranges is only valid for selector fields"
            )

        allowed_values = entry.get("allowed_values")
        if namespace == "reserved":
            if not isinstance(allowed_values, list) or not allowed_values or not all(
                isinstance(value, int) and not isinstance(value, bool) and value >= 0
                for value in allowed_values
            ):
                raise ValueError(
                    f"encoding/fields.json: fields.{name}.allowed_values must be a non-empty list of non-negative integers"
                )
            if len(allowed_values) != len(set(allowed_values)):
                raise ValueError(
                    f"encoding/fields.json: fields.{name}.allowed_values contains duplicates"
                )
            maximum = (1 << min(widths)) - 1
            if any(value > maximum for value in allowed_values):
                raise ValueError(
                    f"encoding/fields.json: fields.{name}.allowed_values must fit every declared width"
                )
        elif "allowed_values" in entry:
            raise ValueError(
                f"encoding/fields.json: fields.{name}.allowed_values is only valid for reserved fields"
            )

        compiled[name] = dict(entry)

    return {"fields": compiled, "notes": source.get("notes") or []}


def _augment_with_compression_kind(instructions: List[Dict[str, Any]]) -> None:
    for inst in instructions:
        m = str(inst.get("mnemonic") or "").strip()
        l = int(inst.get("length_bits") or 0)
        if l == 16 or m.startswith("C."):
            inst["encoding_kind"] = "C16"
        elif l == 48 or m.startswith("HL."):
            inst["encoding_kind"] = "HL48"
        elif l == 64:
            inst["encoding_kind"] = "L64"
        else:
            inst["encoding_kind"] = "L32"


def _augment_with_encoding(instructions: List[Dict[str, Any]]) -> None:
    """
    Derive `encoding` (mask/match/pattern and field pieces) from raw segments.

    This mirrors the existing generator expectations in tools/isa/*.
    """
    for inst in instructions:
        encoding_parts: List[Dict[str, Any]] = []

        for part_index, part in enumerate(inst.get("parts", [])):
            width_bits = int(part.get("width_bits", 0))
            segs: List[Dict[str, Any]] = list(part.get("segments", []))

            fixed_mask = 0
            fixed_bits = 0
            pattern: List[str] = ["." for _ in range(width_bits)]

            fields: Dict[str, Dict[str, Any]] = {}
            constraints_from_tokens: List[Dict[str, Any]] = []

            for seg in segs:
                msb = int(seg.get("msb"))
                lsb = int(seg.get("lsb"))
                seg_width = int(seg.get("width"))
                token = str(seg.get("token") or "")

                if "const" in seg:
                    value = int(seg["const"]["value"])
                    for bit_i in range(seg_width):
                        bit = lsb + bit_i
                        fixed_mask |= 1 << bit
                        if (value >> bit_i) & 1:
                            fixed_bits |= 1 << bit
                            pattern[bit] = "1"
                        else:
                            pattern[bit] = "0"
                    continue

                base_name, value_msb, value_lsb, constraint = _parse_field_token(token)
                if constraint is not None:
                    constraint["field"] = base_name
                    constraints_from_tokens.append(constraint)

                field = fields.get(base_name)
                if field is None:
                    field = {"name": base_name, "signed": _signed_hint(base_name), "pieces": []}
                    fields[base_name] = field

                piece: Dict[str, Any] = {"insn_msb": msb, "insn_lsb": lsb, "width": seg_width, "token": token}
                if value_msb is not None and value_lsb is not None:
                    piece["value_msb"] = value_msb
                    piece["value_lsb"] = value_lsb
                field["pieces"].append(piece)

            # normalize field ordering and piece ordering
            fields_list: List[Dict[str, Any]] = []
            for name in sorted(fields.keys()):
                f = fields[name]
                pieces = list(f.get("pieces", []))
                pieces.sort(key=lambda p: (int(p["insn_msb"]), int(p["insn_msb"])), reverse=True)
                f["pieces"] = pieces
                fields_list.append(f)

            enc_part: Dict[str, Any] = {
                "index": part_index,
                "width_bits": width_bits,
                "mask": _hex_width(fixed_mask, width_bits),
                "match": _hex_width(fixed_bits, width_bits),
                "pattern": "".join(pattern[::-1]),
                "fields": fields_list,
            }

            constraints = inst.get("_constraints_part0") if part_index == 0 else None
            merged_constraints: List[Dict[str, Any]] = []
            if constraints:
                merged_constraints.extend(list(constraints))
            if constraints_from_tokens and part_index == 0:
                # Avoid duplicates if both sources provide the same constraint.
                existing = {(c.get("field"), c.get("op"), c.get("value")) for c in merged_constraints}
                for c in constraints_from_tokens:
                    key = (c.get("field"), c.get("op"), c.get("value"))
                    if key in existing:
                        continue
                    existing.add(key)
                    merged_constraints.append(c)
            if merged_constraints:
                enc_part["constraints"] = merged_constraints

            encoding_parts.append(enc_part)

        inst["encoding"] = {"length_bits": int(inst.get("length_bits", 0)), "parts": encoding_parts}


def _slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_") or "inst"


def _assign_stable_ids(instructions: List[Dict[str, Any]]) -> None:
    for inst in instructions:
        h = hashlib.sha1()
        h.update(str(inst.get("mnemonic", "")).encode("utf-8"))
        h.update(str(inst.get("length_bits", 0)).encode("utf-8"))
        for part in inst.get("parts", []):
            h.update(str(part.get("width_bits", "")).encode("utf-8"))
            for seg in part.get("segments", []):
                h.update(f"{seg.get('msb')}:{seg.get('lsb')}:{seg.get('token','')}".encode("utf-8"))
        uid = h.hexdigest()[:12]
        inst["uid"] = uid
        inst["id"] = f"{_slug(str(inst.get('mnemonic','inst')))}_{inst.get('length_bits',0)}_{uid}"


def _attach_pto_source_form_ids(in_dir: Path, instructions: List[Dict[str, Any]]) -> None:
    """Attach sole-source PTO identities without replacing Linx stable IDs."""
    source_specs = (
        (in_dir / "state" / "pto_scalar_forms.json", 474),
        (
            in_dir / "state" / "pto_command_forms.json",
            96 if in_dir.name == "v0.58" else 99,
        ),
    )

    def source_key(form: Dict[str, Any]) -> Tuple[Any, ...]:
        encoding = tuple(
            (int(part["mask"], 0), int(part["match"], 0), int(part["width_bits"]))
            for part in form.get("encoding", [])
        )
        return (form.get("mnemonic"), form.get("asm"), int(form.get("length_bits", 0)), encoding)

    def instruction_key(inst: Dict[str, Any]) -> Tuple[Any, ...]:
        encoding = tuple(
            (int(part["mask"], 0), int(part["match"], 0), int(part["width_bits"]))
            for part in inst.get("encoding", {}).get("parts", [])
        )
        return (inst.get("mnemonic"), inst.get("asm"), int(inst.get("length_bits", 0)), encoding)

    by_key: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = {}
    for inst in instructions:
        by_key.setdefault(instruction_key(inst), []).append(inst)
    for source_path, expected_count in source_specs:
        if not source_path.is_file():
            continue
        source = _read_json(source_path)
        if source.get("form_count") != expected_count:
            raise ValueError(
                f"{source_path}: expected exactly {expected_count} PTO forms"
            )
        attached = set()
        for form in source.get("forms", []):
            key = source_key(form)
            matches = by_key.get(key, [])
            if len(matches) != 1:
                raise ValueError(
                    f"{source_path}: PTO form {form.get('form_id')} has {len(matches)} exact Linx encoding matches"
                )
            form_id = str(form["form_id"])
            matched = matches[0]
            matched["pto_source_form_id"] = form_id
            for part in matched.get("encoding", {}).get("parts", []):
                part.pop("constraints", None)
            widths = {
                str(field["name"]): int(field["width"])
                for field in form.get("fields", [])
            }
            compiled_constraints = []
            for constraint in form.get("constraints", []):
                field = str(constraint["field"])
                if constraint["operator"] == "one-of":
                    allowed = {int(value) for value in constraint["values"]}
                    rejected = sorted(set(range(1 << widths[field])) - allowed)
                elif constraint["operator"] == "not-equal":
                    rejected = [int(constraint["value"])]
                else:
                    raise ValueError(
                        f"{source_path}: unsupported constraint operator {constraint['operator']!r}"
                    )
                compiled_constraints.extend(
                    {"field": field, "op": "!=", "value": str(value)}
                    for value in rejected
                )
            if compiled_constraints:
                matched["encoding"]["parts"][0]["constraints"] = (
                    compiled_constraints
                )
            attached.add(form_id)
        if len(attached) != expected_count:
            raise ValueError(
                f"{source_path}: PTO source form identities are not unique"
            )


@dataclass(frozen=True)
class _OpcodeLine:
    mnemonic: str
    meta: Dict[str, Any]
    parts: List[List[Tuple[int, int, str]]]
    operands: List[str]
    constraints: List[str]
    source_file: str
    source_line: int


def _parse_mnemonic_prefix(line: str) -> Tuple[str, str]:
    line = line.lstrip()
    if not line:
        raise ValueError("empty line")
    if line[0] == '"':
        # JSON string mnemonic (needed for mnemonics with spaces)
        i = 1
        esc = False
        while i < len(line):
            ch = line[i]
            if esc:
                esc = False
                i += 1
                continue
            if ch == "\\":
                esc = True
                i += 1
                continue
            if ch == '"':
                break
            i += 1
        if i >= len(line) or line[i] != '"':
            raise ValueError("unterminated mnemonic string")
        mnemonic = json.loads(line[: i + 1])
        rest = line[i + 1 :].lstrip()
        return str(mnemonic), rest

    # bare token mnemonic
    m = re.match(r"^([^\\s\\[]+)(.*)$", line)
    if not m:
        raise ValueError("invalid mnemonic")
    return m.group(1), m.group(2).lstrip()


def _split_semicolons(s: str) -> Tuple[str, str, str]:
    parts = [p.strip() for p in s.split(";", 2)]
    if len(parts) != 3:
        raise ValueError("expected exactly two ';' separators")
    return parts[0], parts[1], parts[2]


def _parse_assignments(s: str) -> List[Tuple[int, int, str]]:
    s = s.strip()
    if not s:
        return []
    out: List[Tuple[int, int, str]] = []
    for tok in s.split():
        if "=" not in tok:
            raise ValueError(f"bad assignment token: {tok!r}")
        lhs, rhs = tok.split("=", 1)
        lhs = lhs.strip()
        rhs = rhs.strip()
        if ".." in lhs:
            msb_s, lsb_s = lhs.split("..", 1)
            msb = int(msb_s, 10)
            lsb = int(lsb_s, 10)
        else:
            msb = int(lhs, 10)
            lsb = msb
        if msb < lsb:
            raise ValueError(f"bad bit range {msb}..{lsb}")
        out.append((msb, lsb, rhs))
    return out


def _parse_operands(s: str) -> List[str]:
    s = s.strip()
    if not s:
        return []
    return [t for t in s.split() if t]


def _parse_constraints(s: str) -> List[str]:
    s = s.strip()
    if not s or s == "-":
        return []
    # allow comma-separated or whitespace-separated
    toks: List[str] = []
    for chunk in s.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        toks.extend([t for t in chunk.split() if t])
    return toks


def _parse_constraint_tokens(tokens: List[str]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for t in tokens:
        m = _RE_CONSTRAINT.match(t)
        if not m:
            raise ValueError(f"invalid constraint {t!r} (expected e.g. Field!=0)")
        out.append({"field": m.group("field"), "op": m.group("op"), "value": m.group("value")})
    return out


def _parse_meta_brackets(rest: str) -> Tuple[Dict[str, Any], str]:
    rest = rest.lstrip()
    if not rest.startswith("["):
        return {}, rest
    depth = 0
    i = 0
    for i, ch in enumerate(rest):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                break
    if depth != 0:
        raise ValueError("unterminated [...] meta")
    raw = rest[1:i].strip()
    tail = rest[i + 1 :].lstrip()
    if not raw:
        return {}, tail
    # raw must be valid JSON (string or object)
    meta_val = json.loads(raw)
    if isinstance(meta_val, str):
        return {"asm": meta_val}, tail
    if isinstance(meta_val, dict):
        return meta_val, tail
    raise ValueError("meta must be JSON string or object")


def _iter_opc_lines(path: Path, seen: set[Path]) -> Iterable[Tuple[Path, int, str]]:
    p = path.resolve()
    if p in seen:
        return
    seen.add(p)
    text = path.read_text(encoding="utf-8", errors="strict")
    for idx0, line in enumerate(text.splitlines()):
        raw = line.strip()
        if not raw:
            continue
        if raw.startswith("#"):
            continue
        if raw.startswith("$import"):
            _, rel = raw.split(None, 1)
            inc = (path.parent / rel.strip()).resolve()
            yield from _iter_opc_lines(inc, seen)
            continue
        yield path, idx0 + 1, line.rstrip("\n")


def _parse_opc_line(path: Path, lineno: int, line: str) -> _OpcodeLine:
    # MNEMONIC [JSON] : <assignments> [| <assignments>] ; <operands> ; <constraints>
    mnemonic, rest = _parse_mnemonic_prefix(line)
    mnemonic = mnemonic.strip()
    meta, rest = _parse_meta_brackets(rest)

    if ":" not in rest:
        raise ValueError("missing ':'")
    head, tail = rest.split(":", 1)
    if head.strip():
        # allow extra whitespace only
        raise ValueError("unexpected tokens before ':'")

    enc_s, ops_s, cons_s = _split_semicolons(tail)
    part_strs = [p.strip() for p in enc_s.split("|")]
    parts = [_parse_assignments(p) for p in part_strs if p or len(part_strs) == 1]

    operands = _parse_operands(ops_s)
    constraints = _parse_constraints(cons_s)

    return _OpcodeLine(
        mnemonic=mnemonic,
        meta=meta,
        parts=parts,
        operands=operands,
        constraints=constraints,
        source_file=str(path.as_posix()),
        source_line=int(lineno),
    )


def _assignments_to_part(assignments: List[Tuple[int, int, str]], width_bits: int) -> Dict[str, Any]:
    # Build segments in the given order (expected MSB->LSB from the source).
    segments: List[Dict[str, Any]] = []
    for msb, lsb, rhs in assignments:
        seg_width = msb - lsb + 1
        seg: Dict[str, Any] = {"msb": msb, "lsb": lsb, "width": seg_width, "token": rhs}
        c = _parse_const_token(rhs, seg_width)
        if c is not None:
            # ensure width matches the segment range
            if int(c["width"]) != int(seg_width):
                # Keep the token verbatim for stable IDs but record the value using the segment width.
                c = {"width": int(seg_width), "value": int(c["value"])}
            # mask to width
            if c["value"] < 0 or c["value"] >= (1 << seg_width):
                raise ValueError(f"const {rhs!r} does not fit {seg_width} bits")
            seg["const"] = c
        else:
            if not rhs.strip():
                raise ValueError("field token must be non-empty")
        segments.append(seg)
    seg_sum = sum(int(s["width"]) for s in segments)
    if seg_sum != width_bits:
        raise ValueError(f"segments cover {seg_sum} bits, expected {width_bits}")
    return {"width_bits": int(width_bits), "segments": segments}


def build(in_dir: Path) -> Dict[str, Any]:
    meta = _read_json(in_dir / "meta.json")
    formats = _read_json(in_dir / "encoding" / "formats.json")

    formats_by_len: Dict[int, List[int]] = {}
    for f in formats.get("formats", []):
        length_bits = int(f["length_bits"])
        part_widths = [int(p["width_bits"]) for p in f.get("parts", [])]
        formats_by_len[length_bits] = part_widths

    # registers
    registers: Dict[str, Any] = {}
    reg_dir = in_dir / "registers"
    for p in sorted(reg_dir.glob("*.json")):
        r = _read_json(p)
        name = str(r.get("name") or p.stem)
        r2 = dict(r)
        r2.pop("name", None)
        registers[name] = r2

    # architectural state (optional)
    state: Dict[str, Any] = {}
    state_dir = in_dir / "state"
    if state_dir.exists():
        for p in sorted(state_dir.glob("*.json")):
            state[p.stem] = _read_json(p)

    # opcodes
    opc_dir = in_dir / "opcodes"
    instructions: List[Dict[str, Any]] = []
    seen: set[Path] = set()
    for opc_path in sorted(opc_dir.glob("*.opc")):
        for src_path, lineno, raw_line in _iter_opc_lines(opc_path, seen):
            try:
                ol = _parse_opc_line(src_path, lineno, raw_line)
            except Exception as e:
                raise ValueError(f"{src_path}:{lineno}: {e}\\n  line: {raw_line}") from e

            asm = str(ol.meta.get("asm") or "").strip()
            group = str(ol.meta.get("group") or "").strip()
            length_bits = int(ol.meta.get("length_bits") or 0)
            if not length_bits:
                raise ValueError(f"{src_path}:{lineno}: meta.length_bits is required")
            part_widths = formats_by_len.get(length_bits)
            if not part_widths:
                raise ValueError(f"{src_path}:{lineno}: unknown length_bits {length_bits}")
            if len(ol.parts) != len(part_widths):
                raise ValueError(
                    f"{src_path}:{lineno}: part count {len(ol.parts)} does not match format parts {len(part_widths)}"
                )

            parts: List[Dict[str, Any]] = []
            for assigns, width in zip(ol.parts, part_widths):
                parts.append(_assignments_to_part(assigns, width))

            # Normalize sources to be stable across invocation paths.
            try:
                src_file = str(src_path.resolve().relative_to(in_dir.resolve()).as_posix())
            except Exception:
                src_file = str(src_path.as_posix())

            inst: Dict[str, Any] = {
                "mnemonic": ol.mnemonic,
                "group": group,
                "source": {"file": src_file, "line": int(lineno)},
                "parts": parts,
                "length_bits": int(length_bits),
            }
            if asm:
                inst["asm"] = asm
            # Preserve optional metadata (for example human-facing notes) from
            # opcode source entries so generated references stay self-describing.
            for mk, mv in ol.meta.items():
                if mk in {"asm", "group", "length_bits"}:
                    continue
                inst[mk] = mv

            # constraints are attached to encoding.part[0] to match legacy behavior
            if ol.constraints:
                inst["_constraints_part0"] = _parse_constraint_tokens(ol.constraints)

            instructions.append(inst)

    _augment_with_encoding(instructions)
    _assign_stable_ids(instructions)
    _attach_pto_source_form_ids(in_dir, instructions)

    # Attach uop classification + compression kind (documentation + downstream decoders).
    _augment_with_uop_classification(in_dir, instructions)
    _augment_with_compression_kind(instructions)
    field_definitions = _compile_field_definitions(in_dir, instructions)
    semantics_conventions = _read_json(in_dir / "semantics_conventions.json")
    retired_encodings = _read_json(in_dir / "encoding" / "retired_encodings.json")

    # strip internal fields
    for inst in instructions:
        inst.pop("_constraints_part0", None)

    # stable ordering (human-friendly then stable)
    instructions.sort(key=lambda i: (str(i.get("mnemonic")), int(i.get("length_bits", 0)), str(i.get("id"))))

    return {
        "schema": "linxisa.catalog.v0",
        "isa": str(meta.get("isa") or "LinxISA"),
        "version": str(meta.get("version") or "0.0"),
        "instruction_count": len(instructions),
        "instructions": instructions,
        "registers": registers,
        "field_definitions": field_definitions,
        "semantics_conventions": semantics_conventions,
        "retired_encodings": retired_encodings,
        "state": state,
    }


def _parse_field_token(token: str) -> Tuple[str, Optional[int], Optional[int], Optional[Dict[str, str]]]:
    """
    Returns:
      (base_name, value_msb, value_lsb, constraint)
    where constraint is optional and informational (e.g. RegDst != RA).
    """
    token = token.strip()
    constraint: Optional[Dict[str, str]] = None

    # A handful of source operands carry a role annotation such as
    # RegSrc0=BasePtr. The role is descriptive; the architectural field name
    # and its register namespace remain RegSrc0.
    if "=" in token and not any(op in token for op in ("!=", "==", "<=", ">=")):
        token = token.split("=", 1)[0].strip()

    # Handle simple "not equal" constraints encoded inline (historical draft style).
    for op in ("≠", "!="):
        if op in token:
            left, right = token.split(op, 1)
            token = left.strip()
            constraint = {"op": "!=", "value": right.strip()}
            break

    m = _RE_FIELD_SLICE.match(token)
    if not m:
        return token, None, None, constraint

    name = m.group("name")
    msb_s = m.group("msb")
    lsb_s = m.group("lsb")
    if msb_s is None or lsb_s is None:
        return name, None, None, constraint
    return name, int(msb_s), int(lsb_s), constraint


def _signed_hint(field_name: str) -> Optional[bool]:
    if field_name.startswith("simm"):
        return True
    if field_name.startswith("uimm"):
        return False
    return None


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _profile_defaults(profile: str = "v0.58") -> Tuple[str, str]:
    return f"isa/{profile}", f"isa/{profile}/linxisa-{profile}.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--profile",
        choices=["v0.57", "v0.58"],
        default="v0.58",
        help="ISA profile for default in/out paths",
    )
    ap.add_argument("--in", dest="in_dir", default=None, help="Golden source directory")
    ap.add_argument("--out", default=None, help="Output catalog JSON path")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    ap.add_argument("--check", action="store_true", help="Verify output is up-to-date without writing")
    args = ap.parse_args()

    default_in, default_out = _profile_defaults(args.profile)
    in_dir = Path(args.in_dir or default_in)
    out_path = Path(args.out or default_out)

    built = build(in_dir)

    if args.check and out_path.exists():
        existing = _read_json(out_path)
        if _canonical_json(existing) != _canonical_json(built):
            print(f"error: {out_path} is not up-to-date; re-run build_golden.py", file=sys.stderr)
            return 2
        print("OK")
        return 0

    if args.check and not out_path.exists():
        print(f"error: {out_path} does not exist; build is required", file=sys.stderr)
        return 2

    _write_json(out_path, built, pretty=bool(args.pretty))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
