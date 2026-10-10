#!/usr/bin/env python3
"""Contract test for the v0.58 atomic op5 layout and the Linx-only extension forms."""

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[2]
spec = json.loads((ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8"))

by_mnemonic = {}
for item in spec["instructions"]:
    by_mnemonic.setdefault(item["mnemonic"], []).append(item)


def sole(mnemonic):
    forms = by_mnemonic.get(mnemonic, [])
    assert len(forms) == 1, f"{mnemonic}: expected exactly one form, got {len(forms)}"
    return forms[0]


def enc32(item):
    parts = item["encoding"]["parts"]
    assert item["length_bits"] == 32 and len(parts) == 1
    return int(parts[0]["mask"], 0), int(parts[0]["match"], 0)


def top5(item):
    _, match = enc32(item)
    return (match >> 27) & 0x1F


# 1) The ten new Linx-only forms use the op5 layout
#    [flag(b31)][code(b30..27)] with SUB = 1000 and override = b31.
NEW_ATOMIC = {
    "SW.SUB": 0x4000300B,   # 0_1000
    "SD.SUB": 0x4000500B,   # 0_1000
    "SB.ADD": 0x8000300B,   # 1_0000
    "SB.SUB": 0xC000300B,   # 1_1000
    "SH.ADD": 0x8000500B,   # 1_0000
    "SH.SUB": 0xC000500B,   # 1_1000
}
NEW_DMA = {
    "DMA.FREE.S": 0x0400700B,
    "DMA.FREE.L": 0x0600700B,
}
NEW_MCOPY = {
    "MCOPY.DS": 0x02001031,
    "MCOPY.DL": 0x06001031,
}
for mnemonic, match in {**NEW_ATOMIC, **NEW_DMA, **NEW_MCOPY}.items():
    item = sole(mnemonic)
    mask, got = enc32(item)
    if mnemonic in NEW_MCOPY:
        assert mask == 0x600707F, f"{mnemonic}: mask {mask:#x}"
    elif mnemonic in NEW_DMA:
        assert mask == 0xFFF07FFF, f"{mnemonic}: mask {mask:#x}"
    else:
        assert mask == 0xFC007FFF, f"{mnemonic}: mask {mask:#x}"
    assert got == match, f"{mnemonic}: match {got:#x} != {match:#x}"
    assert "far" not in item["asm"], f"{mnemonic}: far leaked into asm"

# 2) Store-op base forms keep sequential op codes at b30..27 with b31 = 0.
OP4 = {
    "ADD": 0x0, "AND": 0x1, "OR": 0x2, "XOR": 0x3,
    "SMAX": 0x4, "SMIN": 0x5, "UMAX": 0x6, "UMIN": 0x7,
}
for prefix, func_bits in (("SW", 0x300B), ("SD", 0x500B)):
    for op, code in OP4.items():
        mnemonic = f"{prefix}.{op}"
        mask, match = enc32(sole(mnemonic))
        assert mask == 0xFC007FFF, f"{mnemonic}: mask {mask:#x}"
        assert match == (code << 27) | func_bits, f"{mnemonic}: match {match:#x}"
        assert top5(sole(mnemonic)) == code, mnemonic
        names = {f["name"] for p in sole(mnemonic)["encoding"]["parts"] for f in p["fields"]}
        assert "far" not in names, f"{mnemonic}: far field leaked"

# 3) Far-bearing atomic families keep far as a variable bit, now at b31,
#    with the size/op code at b30..27.
FAR_FORMS = {
    "LR.B": 0x0, "LR.H": 0x1, "LR.W": 0x2, "LR.D": 0x3,
    "SC.B": 0x0, "SC.H": 0x1, "SC.W": 0x2, "SC.D": 0x3,
    "SWAPB": 0x0, "SWAPH": 0x1, "SWAPW": 0x2, "SWAPD": 0x3,
}
for prefix, ops in (("LW", OP4), ("LD", OP4)):
    for op, code in ops.items():
        FAR_FORMS[f"{prefix}.{op}"] = code
for mnemonic, code in FAR_FORMS.items():
    item = sole(mnemonic)
    mask, match = enc32(item)
    assert mask & 0x80000000 == 0, f"{mnemonic}: b31 must stay unmasked (far)"
    assert (match >> 27) & 0xF == code, f"{mnemonic}: code {(match >> 27) & 0xF:#x} != {code:#x}"
    far = None
    for part in item["encoding"]["parts"]:
        for field in part["fields"]:
            if field["name"] == "far":
                far = field["pieces"][0]["insn_lsb"]
    assert far == 31, f"{mnemonic}: far must decode from bit 31, got {far}"

# 4) SUB never collides with the SMAX family or the size-override forms.
assert enc32(sole("SW.SUB"))[1] != enc32(sole("SW.SMAX"))[1]
assert enc32(sole("SD.SUB"))[1] != enc32(sole("SD.SMAX"))[1]
assert enc32(sole("SB.ADD"))[1] != enc32(sole("SW.ADD"))[1]
assert enc32(sole("SH.SUB"))[1] != enc32(sole("SD.UMAX"))[1]

# 5) The PTO identity surface is unchanged: still exactly 561 attached forms
#    and the ten new forms are Linx-only.
attached = [i for i in spec["instructions"] if "pto_source_form_id" in i]
assert len(attached) == 561, len(attached)
for mnemonic in {**NEW_ATOMIC, **NEW_DMA, **NEW_MCOPY}:
    assert "pto_source_form_id" not in sole(mnemonic), mnemonic

# 6) CAS keeps its own layout: SrcD occupies 31..27 and no far flag exists.
for mnemonic in ("CASB", "CASH", "CASW", "CASD"):
    item = sole(mnemonic)
    names = {f["name"] for p in item["encoding"]["parts"] for f in p["fields"]}
    assert "SrcD" in names and "far" not in names, mnemonic

print("OK")
