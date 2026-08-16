#!/usr/bin/env python3
"""Raw/metamorphic checks for the exact two-target fused CALL forms."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


FORMS = {
    "BSTART.CALL:32": {
        "mnemonic": "BSTART.CALL",
        "pto_source_form_id": "bstart_call_32_9404418d1ae5",
        "asm": "BSTART.CALL <br_label>, <rt_label>, ->ra",
        "call_field": "simm12",
        "call_lsb": 4,
        "call_width": 12,
        "return_lsb": 22,
        "embedded_base": 2,
        "call_relocation": "CBSTART12_PCREL",
        "directed_cases": [(2, 3), (2, 29), ((1 << 12) - 1, 3)],
        "length": 32,
    },
    "HL.BSTART CALL:48": {
        "mnemonic": "HL.BSTART CALL",
        "pto_source_form_id": None,
        "asm": "HL.BSTART.CALL <br_label>, <rt_label>, ->ra",
        "call_field": "simm25",
        "call_lsb": 7,
        "call_width": 25,
        "return_lsb": 38,
        "embedded_base": 4,
        "call_relocation": "B25_PCREL",
        "directed_cases": [(2, 5), (2, 31), ((1 << 25) - 1, 5)],
        "length": 48,
    },
}


def sign_extend(value: int, width: int) -> int:
    sign = 1 << (width - 1)
    return (value ^ sign) - sign


def field_value(raw: int, lsb: int, width: int) -> int:
    return (raw >> lsb) & ((1 << width) - 1)


def encode(part: dict, contract: dict, call_bits: int, return_bits: int) -> int:
    match = int(part["match"], 0)
    return (
        match
        | (call_bits << contract["call_lsb"])
        | (return_bits << contract["return_lsb"])
    )


def targets(raw: int, contract: dict, p: int) -> tuple[int, int]:
    call_bits = field_value(raw, contract["call_lsb"], contract["call_width"])
    return_bits = field_value(raw, contract["return_lsb"], 5)
    return (
        p + (sign_extend(call_bits, contract["call_width"]) << 1),
        p + contract["embedded_base"] + (return_bits << 1),
    )


def main() -> int:
    spec = json.loads((ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8"))
    by_semantic_key: dict[str, list[dict]] = {}
    for inst in spec["instructions"]:
        key = f"{inst['mnemonic']}:{inst['length_bits']}"
        by_semantic_key.setdefault(key, []).append(inst)
    sail = (ROOT / "isa/sail/model/decode/decode.sail").read_text(encoding="utf-8")
    directed = (ROOT / "isa/sail/tests/directed.sail").read_text(encoding="utf-8")
    directed_raw_calls = {
        (int(width), int(raw.replace("_", ""), 16))
        for width, raw in re.findall(
            r"decode_execute(32|48)\((0x[0-9A-Fa-f_]+)\)", directed
        )
    }
    manual = (
        ROOT / "docs/architecture/isa-manual/src/generated/instruction_details.adoc"
    ).read_text(encoding="utf-8")
    mkdocs_pages = {
        "BSTART.CALL:32": (
            ROOT / "docs/isa/instructions/bstart_call.md"
        ).read_text(encoding="utf-8"),
        "HL.BSTART CALL:48": (
            ROOT / "docs/isa/instructions/hl_bstart_call.md"
        ).read_text(encoding="utf-8"),
    }

    for semantic_key, contract in FORMS.items():
        candidates = [
            inst
            for inst in by_semantic_key.get(semantic_key, [])
            if inst["asm"] == contract["asm"]
        ]
        assert len(candidates) == 1, (semantic_key, [item["id"] for item in candidates])
        inst = candidates[0]
        form_id = inst["id"]
        if contract["pto_source_form_id"] is not None:
            assert inst["pto_source_form_id"] == contract["pto_source_form_id"]
        assert inst["asm"] == contract["asm"]
        assert inst["semantic_contract"]["atomic"] is True
        assert inst["semantic_contract"]["transfer"] == "CALL"

        roles = {role["role"]: role for role in inst["operand_roles"]}
        assert roles["call_target"]["field"] == contract["call_field"]
        assert roles["call_target"]["pc_base"] == "P"
        assert roles["return_target"]["field"] == "uimm5"
        assert roles["return_target"]["pc_base"] == f"P+{contract['embedded_base']}"
        assert roles["link_destination"]["syntax"] == "->ra"
        assert [reloc["name"] for reloc in inst["exact_relocations"]] == [
            contract["call_relocation"],
            "CSETRET5_PCREL",
        ]

        part = inst["encoding"]["parts"][0]
        mask = int(part["mask"], 0)
        match = int(part["match"], 0)
        p = 0x1000
        baseline = encode(part, contract, 1, 3)
        call0, ra0 = targets(baseline, contract, p)

        # Same signed call field, different return field: only ra changes.
        return_variant = encode(part, contract, 1, 29)
        call1, ra1 = targets(return_variant, contract, p)
        assert call1 == call0
        assert ra1 != ra0
        assert (baseline ^ return_variant) & ~(((1 << 5) - 1) << contract["return_lsb"]) == 0

        # Same return field, different signed call field: only the call target changes.
        call_variant = encode(part, contract, (1 << contract["call_width"]) - 1, 3)
        call2, ra2 = targets(call_variant, contract, p)
        assert call2 != call0
        assert ra2 == ra0
        assert (baseline ^ call_variant) & ~(
            ((1 << contract["call_width"]) - 1) << contract["call_lsb"]
        ) == 0

        # Signed extrema and the full uimm5 boundary remain independent.
        minimum = encode(part, contract, 1 << (contract["call_width"] - 1), 0)
        maximum = encode(part, contract, (1 << (contract["call_width"] - 1)) - 1, 31)
        assert targets(minimum, contract, p) == (
            p - (1 << contract["call_width"]),
            p + contract["embedded_base"],
        )
        assert targets(maximum, contract, p) == (
            p + ((1 << contract["call_width"]) - 2),
            p + contract["embedded_base"] + 62,
        )

        expected_directed = {
            (
                contract["length"],
                encode(part, contract, call_bits, return_bits),
            )
            for call_bits, return_bits in contract["directed_cases"]
        }
        assert expected_directed <= directed_raw_calls
        assert all((raw & mask) == match for _, raw in expected_directed)

        assert form_id in manual
        assert contract["call_relocation"] in manual
        page = mkdocs_pages[semantic_key]
        assert contract["asm"] in page
        assert f"SignExtend({contract['call_field']})" in page
        assert f"(P + {contract['embedded_base']})" in page
        assert "AtomicCallTransfer(call_target, ra)" in page
        assert "This exact aggregate is distinct from the generic bare-call form" in page

    assert "exec_bstart_call(uimm5)" in sail
    assert "exec_hl_bstart_call(uimm5)" in sail
    assert "exec_bstart_call()" not in sail
    assert directed.count("reset_fused_call_case(") >= 7
    assert "exec_bstart_call(" not in directed
    assert "exec_hl_bstart_call(" not in directed
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
