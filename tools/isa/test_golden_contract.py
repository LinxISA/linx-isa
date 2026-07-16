#!/usr/bin/env python3
"""Focused regression checks for the v0.56.5 hard-break ISA contract."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    spec = json.loads((ROOT / "isa/v0.56/linxisa-v0.56.json").read_text(encoding="utf-8"))
    instructions = spec["instructions"]
    mnemonics = {str(inst["mnemonic"]) for inst in instructions}
    assert spec["version"] == "0.56.5"
    assert "B.IOD" not in mnemonics
    assert "BSTART.PAR" not in mnemonics
    assert {
        "B.IOR",
        "B.IOT",
        "BSTART.TEPL",
        "B.CATR",
        "B.DATR",
        "L.BSTART.FP",
        "L.BSTART.STD",
        "L.BSTART.SYS",
    } <= mnemonics

    long_bstarts = [inst for inst in instructions if str(inst["mnemonic"]).startswith("L.BSTART.")]
    assert len(long_bstarts) == 9
    assert {inst["length_bits"] for inst in long_bstarts} == {64}
    assert {inst["asm"].split()[1] for inst in long_bstarts} >= {"FALL<,", "DIRECT,", "COND,", "CALL,"}

    retired = {entry["retired_mnemonic"]: entry for entry in spec["retired_encodings"]["entries"]}
    assert retired["B.IOD"]["disposition"] == "reserved"
    assert retired["BSTART.PAR"]["replacement_mnemonic"] == "BSTART.TEPL"

    calls = [
        inst
        for inst in instructions
        if inst["mnemonic"] in {"BSTART CALL", "HL.BSTART CALL"}
        or (str(inst["mnemonic"]).startswith("L.BSTART.") and " CALL," in inst["asm"])
    ]
    assert len(calls) == 4
    for call in calls:
        note = str(call.get("note") or "")
        assert "preserves ra" in note
        assert "SETRET or C.SETRET" in note

    form_ids = [str(inst["id"]) for inst in instructions]
    assert len(form_ids) == len(set(form_ids)) == int(spec["instruction_count"])
    assert all(inst.get("uop_big_kind") and inst.get("uop_class") for inst in instructions)
    assert spec["field_definitions"]["fields"]
    assert spec["semantics_conventions"]

    field_source = json.loads(
        (ROOT / "isa/v0.56/encoding/fields.json").read_text(encoding="utf-8")
    )
    assert spec["field_definitions"] == field_source
    for name, definition in field_source["fields"].items():
        assert definition["widths"] == sorted(set(definition["widths"])), name
        if definition["namespace"] == "immediate":
            assert isinstance(definition["signed"], bool), name
            assert isinstance(definition["scale"], int) and definition["scale"] > 0, name
        if definition["namespace"] == "selector":
            assert isinstance(definition["reserved_values"], list), name
    assert field_source["fields"]["reserve"]["allowed_values"] == [0]
    assert field_source["fields"]["reserve"]["documented_only"] is True
    assert field_source["fields"]["TileOpcode"]["reserved_ranges"] == [[64, 1023]]

    tma = spec["state"]["engine_ops"]["tma"]
    assert tma == {
        "function_field_bits": [0, 4],
        "kind": "function_u5",
        "legal_aliases": [
            {"function": 0, "mnemonic": "BSTART.TLOAD"},
            {"function": 1, "mnemonic": "BSTART.TSTORE"},
            {"function": 2, "mnemonic": "BSTART.TMOV"},
        ],
        "reserved_behavior": "illegal_instruction",
        "reserved_function_range": [3, 31],
    }
    assert "BSTART.TMA" not in mnemonics
    exact_tma = {
        inst["mnemonic"]: inst["encoding"]["parts"][0]
        for inst in instructions
        if inst["mnemonic"] in {"BSTART.TLOAD", "BSTART.TSTORE", "BSTART.TMOV"}
    }
    assert {
        name: (int(part["mask"], 0), int(part["match"], 0))
        for name, part in exact_tma.items()
    } == {
        "BSTART.TLOAD": (0x07FFFFFF, 0x00011181),
        "BSTART.TSTORE": (0x07FFFFFF, 0x00111181),
        "BSTART.TMOV": (0x07FFFFFF, 0x00211181),
    }

    observed_fields = {
        field["name"]
        for inst in instructions
        for part in inst["encoding"]["parts"]
        for field in part.get("fields", [])
    }
    assert "reserve" not in observed_fields
    b_catr = next(inst for inst in instructions if inst["mnemonic"] == "B.CATR")
    assert int(b_catr["encoding"]["parts"][0]["mask"], 0) == 0x03FFFFFF
    trace_hint = next(inst for inst in instructions if inst["asm"] == "B.HINT TRACE.{begin, end}")
    assert int(trace_hint["encoding"]["parts"][0]["mask"], 0) == 0xFFFF7FFF

    status = json.loads((ROOT / "isa/sail/semantics_status.json").read_text(encoding="utf-8"))
    assert set(status["forms"]) == set(form_ids)
    assert {
        entry["status"] for entry in status["forms"].values()
    } <= {"decode-only", "executable-subset", "architecturally-complete"}
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
