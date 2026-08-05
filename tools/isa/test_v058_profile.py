#!/usr/bin/env python3
"""Small dependency-free contract test for the LinxISA 0.58 profile."""

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[2]
spec = json.loads((ROOT / "isa/v0.58/linxisa-v0.58.json").read_text(encoding="utf-8"))
assert spec["version"] == "0.58.0"
assert sum("pto_source_form_id" in item for item in spec["instructions"]) == 570
mnemonics = {item["mnemonic"] for item in spec["instructions"]}
assert {"C.B.IOS", "BSTART.GMOV", "BSTART.VPAR", "BSTART.VSEQ", "V.QPOP", "V.QPUSH"} <= mnemonics
shared = json.loads((ROOT / "isa/v0.58/state/shared_tile_registers.json").read_text(encoding="utf-8"))
assert shared["register_count"] == 256
assert shared["register_names"]["first"] == "S0"
assert shared["register_names"]["last"] == "S255"
print("OK")
