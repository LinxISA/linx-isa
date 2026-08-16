#!/usr/bin/env python3
"""Focused regressions for Sail decode generation ordering."""

from __future__ import annotations

import json
from pathlib import Path

import gen_sail_decode


ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "isa/v0.58/linxisa-v0.58.json"
RETIRED_PATH = ROOT / "isa/v0.58/encoding/retired_encodings.json"


def _load_spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def _load_retired() -> dict:
    return json.loads(RETIRED_PATH.read_text(encoding="utf-8"))


def _one_part(inst: dict) -> tuple[int, int]:
    parts = inst["encoding"]["parts"]
    assert len(parts) == 1
    return int(parts[0]["mask"], 0), int(parts[0]["match"], 0)


def _bstart_entries(spec: dict) -> list[dict]:
    return [
        inst
        for inst in spec["instructions"]
        if inst["length_bits"] == 32 and inst["mnemonic"].startswith("BSTART")
    ]


def test_tepl_mode_function_decode_precedes_broad_overlaps() -> None:
    spec = _load_spec()
    retired = _load_retired()
    ordered = gen_sail_decode.order_decode_entries(_bstart_entries(spec), retired)
    tepl = next(inst for inst in ordered if inst["mnemonic"] == "BSTART.TEPL")
    assert _one_part(tepl) == (0x000FFFFF, 0x00019181)


def test_tepl_mode_function_decode_is_deterministic() -> None:
    spec = _load_spec()
    retired = _load_retired()
    entries = _bstart_entries(spec)
    first = [inst["uid"] for inst in gen_sail_decode.order_decode_entries(entries, retired)]
    second = [inst["uid"] for inst in gen_sail_decode.order_decode_entries(list(reversed(entries)), retired)]
    assert first == second


def test_tepl_mode_function_decode_render_selects_tepl_first() -> None:
    spec = _load_spec()
    retired = _load_retired()
    execute_text = (ROOT / "isa/sail/model/execute/execute.sail").read_text(encoding="utf-8")
    rendered = gen_sail_decode.render(spec, execute_text, "isa/v0.58/linxisa-v0.58.json", retired)

    tepl_pos = rendered.index("// BSTART.TEPL |")
    tepl_body = rendered[tepl_pos : rendered.index("  }", tepl_pos)]
    assert "decoded_block_type_shadow = 0b1101;" in tepl_body


def test_decode32_dispatch_is_partitioned_by_exact_opcode() -> None:
    spec = _load_spec()
    retired = _load_retired()
    execute_text = (ROOT / "isa/sail/model/execute/execute.sail").read_text(encoding="utf-8")
    rendered = gen_sail_decode.render(spec, execute_text, "isa/v0.58/linxisa-v0.58.json", retired)

    assert "function decode_execute32_opcode_0b0001011" in rendered
    assert "function decode_execute32_opcode_0b0001011_funct3_0b010" in rendered
    assert "function decode_execute32_opcode_0b0001011_funct3_0b010_match_0" in rendered
    assert "match inst[6..0]" in rendered
    assert "match inst[14..12]" in rendered
    assert "0b0001011 => decode_execute32_opcode_0b0001011(inst)" in rendered

    assert "and_bool_no_flow" in rendered

    dispatcher = rendered[rendered.index("function decode_execute32(inst") :]
    wildcard_pos = dispatcher.index("// BSTART.CALL |")
    match_pos = dispatcher.index("match inst[6..0]")
    assert wildcard_pos < match_pos
    assert "Reserved retired encoding: BSTART.PAR" not in dispatcher


def test_malformed_canonical_redecode_metadata_fails_closed() -> None:
    bad = {"entries": [{"disposition": "canonical-redecode", "length_bits": 32}]}
    try:
        gen_sail_decode.canonical_redecode_entries(bad)
    except ValueError as exc:
        assert "missing required field" in str(exc)
    else:
        raise AssertionError("malformed canonical-redecode metadata was accepted")


def test_unresolved_canonical_redecode_metadata_fails_closed() -> None:
    spec = _load_spec()
    bad = {
        "entries": [
            {
                "disposition": "canonical-redecode",
                "length_bits": 32,
                "mask": "0xffffffff",
                "match": "0x12345678",
                "replacement_mnemonic": "BSTART.TEPL",
                "retired_mnemonic": "BSTART.PAR",
            }
        ]
    }
    try:
        gen_sail_decode.order_decode_entries(_bstart_entries(spec), bad)
    except ValueError as exc:
        assert "must resolve to exactly one" in str(exc)
    else:
        raise AssertionError("unresolved canonical-redecode metadata was accepted")


def test_ambiguous_canonical_redecode_metadata_fails_closed() -> None:
    bad = {
        "entries": [
            {
                "disposition": "canonical-redecode",
                "length_bits": 32,
                "mask": "0x06007fff",
                "match": "0x02001181",
                "replacement_mnemonic": "BSTART.TEPL",
                "retired_mnemonic": "BSTART.PAR",
            },
            {
                "disposition": "canonical-redecode",
                "length_bits": 32,
                "mask": "0x06007fff",
                "match": "0x02001181",
                "replacement_mnemonic": "BSTART.MPAR",
                "retired_mnemonic": "BSTART.OLDPAR",
            },
        ]
    }
    try:
        gen_sail_decode.canonical_redecode_entries(bad)
    except ValueError as exc:
        assert "maps to both" in str(exc)
    else:
        raise AssertionError("ambiguous canonical-redecode metadata was accepted")


def test_fixed_source_field_supplies_execute_parameter() -> None:
    inst = {
        "mnemonic": "FRET.STK",
        "pto_source_fixed_fields": [
            {"name": "DstBegin", "value": 10, "width": 5}
        ],
    }
    assert gen_sail_decode.param_expr(inst, "DstBegin", {}) == "0b01010"


def main() -> int:
    tests = [
        test_tepl_mode_function_decode_precedes_broad_overlaps,
        test_tepl_mode_function_decode_is_deterministic,
        test_tepl_mode_function_decode_render_selects_tepl_first,
        test_decode32_dispatch_is_partitioned_by_exact_opcode,
        test_malformed_canonical_redecode_metadata_fails_closed,
        test_unresolved_canonical_redecode_metadata_fails_closed,
        test_ambiguous_canonical_redecode_metadata_fails_closed,
        test_fixed_source_field_supplies_execute_parameter,
    ]
    for test in tests:
        test()
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
