#!/usr/bin/env python3
"""Focused encoding checks for the standalone v0.57 profile."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(profile: str) -> dict:
    return json.loads((ROOT / f"isa/{profile}/linxisa-{profile}.json").read_text(encoding="utf-8"))


def _one_part(spec: dict, mnemonic: str) -> tuple[int, int]:
    inst = next(inst for inst in spec["instructions"] if inst["mnemonic"] == mnemonic)
    parts = inst["encoding"]["parts"]
    assert len(parts) == 1
    return int(parts[0]["mask"], 0), int(parts[0]["match"], 0)


def main() -> int:
    v057 = _load("v0.57")
    v057_names = {inst["mnemonic"] for inst in v057["instructions"]}

    assert {
        "BSTART.TPREFETCH",
        "BSTART.MGATHER",
        "BSTART.MSCATTER",
        "BSTART.MGATHER.MASK",
        "BSTART.MSCATTER.MASK",
        "BSTART.MGATHER.CAS",
        "BSTART.TMATMUL.BIAS",
        "BSTART.TMATMULMX",
        "BSTART.TMATMULMX.BIAS",
        "BSTART.TMATMULMX.ACC",
        "BSTART.TGEMV",
        "BSTART.TGEMV.BIAS",
        "BSTART.TGEMV.ACC",
        "BSTART.TGEMVMX",
        "BSTART.TGEMVMX.BIAS",
        "BSTART.TGEMVMX.ACC",
        "CASB",
        "CASH",
        "CASW",
        "CASD",
        "DMA",
    } <= v057_names
    assert {"BSTART.TMA", "B.IOD", "BSTART.PAR"} & v057_names == set()

    expected_tma = {
        "BSTART.TLOAD": (0x07FFFFFF, 0x00011181),
        "BSTART.TSTORE": (0x07FFFFFF, 0x00111181),
        "BSTART.TMOV": (0x07FFFFFF, 0x00211181),
        "BSTART.TPREFETCH": (0x07FFFFFF, 0x00311181),
        "BSTART.MGATHER": (0x07FFFFFF, 0x00411181),
        "BSTART.MSCATTER": (0x07FFFFFF, 0x00511181),
        "BSTART.MGATHER.MASK": (0x07FFFFFF, 0x00611181),
        "BSTART.MSCATTER.MASK": (0x07FFFFFF, 0x00711181),
        "BSTART.MGATHER.CAS": (0x07FFFFFF, 0x00811181),
    }
    for mnemonic, expected in expected_tma.items():
        assert _one_part(v057, mnemonic) == expected

    expected_pr139 = {
        "CASB": (0x0000707F, 0x0000001B),
        "CASH": (0x0000707F, 0x0000101B),
        "CASW": (0x0000707F, 0x0000201B),
        "CASD": (0x0000707F, 0x0000301B),
        "DMA": (0xFE007FFF, 0x0000700B),
    }
    for mnemonic, expected in expected_pr139.items():
        assert _one_part(v057, mnemonic) == expected

    one_part_32 = [
        (
            inst["mnemonic"],
            int(inst["encoding"]["parts"][0]["mask"], 0),
            int(inst["encoding"]["parts"][0]["match"], 0),
        )
        for inst in v057["instructions"]
        if inst["length_bits"] == 32 and len(inst["encoding"]["parts"]) == 1
    ]
    tma_base = 0x00011181
    expected_by_function = {
        0: "BSTART.TLOAD",
        1: "BSTART.TSTORE",
        2: "BSTART.TMOV",
        3: "BSTART.TPREFETCH",
        4: "BSTART.MGATHER",
        5: "BSTART.MSCATTER",
        6: "BSTART.MGATHER.MASK",
        7: "BSTART.MSCATTER.MASK",
        8: "BSTART.MGATHER.CAS",
    }
    for dtype in range(32):
        for function in range(32):
            word = (dtype << 27) | (function << 20) | tma_base
            matches = sorted(name for name, mask, match in one_part_32 if word & mask == match)
            if function in expected_by_function:
                assert matches == [expected_by_function[function]], (dtype, function, matches)
            else:
                assert matches == [], (dtype, function, matches)

    expected_cube = {
        0: "BSTART.TMATMUL",
        1: "BSTART.TMATMUL.BIAS",
        2: "BSTART.TMATMUL.ACC",
        4: "BSTART.TMATMULMX",
        5: "BSTART.TMATMULMX.BIAS",
        6: "BSTART.TMATMULMX.ACC",
        8: "BSTART.ACCCVT",
        16: "BSTART.TGEMV",
        17: "BSTART.TGEMV.BIAS",
        18: "BSTART.TGEMV.ACC",
        20: "BSTART.TGEMVMX",
        21: "BSTART.TGEMVMX.BIAS",
        22: "BSTART.TGEMVMX.ACC",
    }
    cube_base = 0x00031181
    for dtype in range(32):
        for function in range(32):
            word = (dtype << 27) | (function << 20) | cube_base
            matches = sorted(name for name, mask, match in one_part_32 if word & mask == match)
            if function in expected_cube:
                assert matches == sorted(["BSTART.CUBE", expected_cube[function]]), (dtype, function, matches)
            else:
                assert matches == ["BSTART.CUBE"], (dtype, function, matches)

    v057_tepl = {
        op["name"]: int(op["tile_opcode"])
        for op in v057["state"]["engine_ops"]["tepl"]["ops"]
    }
    expected_new_tepl = {
        "TCMP": 0x02B,
        "TSEL": 0x02C,
        "TABS": 0x02D,
        "TNOT": 0x02E,
        "TNEG": 0x02F,
        "TREM": 0x030,
        "TAXPY": 0x031,
        "TREMS": 0x032,
        "TCMPS": 0x033,
        "TSELS": 0x034,
        "TROWPROD": 0x035,
        "TROWARGMAX": 0x036,
        "TROWARGMIN": 0x037,
        "TCOLPROD": 0x038,
        "TCOLARGMAX": 0x039,
        "TCOLARGMIN": 0x03A,
        "TROWEXPANDADD": 0x03B,
        "TROWEXPANDSUB": 0x03C,
        "TROWEXPANDMUL": 0x03D,
        "TROWEXPANDDIV": 0x03E,
        "TROWEXPANDMAX": 0x03F,
        "TROWEXPANDMIN": 0x040,
        "TROWEXPANDEXPDIF": 0x041,
        "TCOLEXPANDADD": 0x042,
        "TCOLEXPANDSUB": 0x043,
        "TCOLEXPANDMUL": 0x044,
        "TCOLEXPANDDIV": 0x045,
        "TCOLEXPANDMAX": 0x046,
        "TCOLEXPANDMIN": 0x047,
        "TCOLEXPANDEXPDIF": 0x048,
        "TCI": 0x080,
        "TTRI": 0x081,
        "TFILLPAD": 0x082,
        "TQUANT": 0x083,
        "TDEQUANT": 0x084,
        "TEXTRACT": 0x085,
        "TINSERT": 0x086,
        "TCONCAT": 0x087,
        "TIMG2COL": 0x088,
        "TGATHERB": 0x089,
        "TDEINTERLEAVE": 0x08A,
        "TINTERLEAVE": 0x08B,
        "TSORT": 0x0C0,
        "TMRGSORT": 0x0C1,
        "THISTOGRAM": 0x0C2,
        "TPARTADD": 0x0C3,
        "TPARTMUL": 0x0C4,
        "TPARTMAX": 0x0C5,
        "TPARTMIN": 0x0C6,
        "TPARTARGMAX": 0x0C7,
        "TPARTARGMIN": 0x0C8,
        "TPUSH": 0x0E0,
        "TPOP": 0x0E1,
        "TALLOC": 0x0E2,
        "TFREE": 0x0E3,
    }
    for name, selector in expected_new_tepl.items():
        assert v057_tepl[name] == selector
    assert {"TFMOD", "TPOW", "TRANDOM", "TEXRACT"} & set(v057_tepl) == set()

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
