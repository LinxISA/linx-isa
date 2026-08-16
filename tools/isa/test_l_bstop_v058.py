#!/usr/bin/env python3
"""Lock the accepted LinxISA/PTO 64-bit bundle-stop encoding."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = json.loads(
    (ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8")
)

forms = [
    instruction
    for instruction in SPEC["instructions"]
    if instruction["mnemonic"] == "L.BSTOP"
]
assert len(forms) == 1
form = forms[0]
assert form["asm"] == "L.BSTOP"
assert form["length_bits"] == 64
assert form["pto_source_form_id"].startswith("l_bstop_64_")
assert [
    (int(part["mask"], 0), int(part["match"], 0))
    for part in form["encoding"]["parts"]
] == [
    (0xFFFFFFFF, 0x0000000F),
    (0xFFFFFFFF, 0x00000001),
]
print("OK")
