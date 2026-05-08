#!/usr/bin/env python3
"""Generate canonical Sail decode/dispatch from the compiled v0.56 catalog."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


WIDTH_FUNCS = {
    16: "decode_execute16",
    32: "decode_execute32",
    48: "decode_execute48",
    64: "decode_execute64",
}

VECTOR_FP_MNEMONICS = {
    "V.FABS",
    "V.FADD",
    "V.FCLASS",
    "V.FDIV",
    "V.FEQ",
    "V.FEQS",
    "V.FEXP",
    "V.FGE",
    "V.FGES",
    "V.FLT",
    "V.FLTS",
    "V.FMADD",
    "V.FMAX",
    "V.FMIN",
    "V.FMSUB",
    "V.FMUL",
    "V.FNE",
    "V.FNES",
    "V.FNMADD",
    "V.FNMSUB",
    "V.FRECIP",
    "V.FSQRT",
    "V.FSUB",
}

VECTOR_CONVERT_MNEMONICS = {
    "V.FCVT",
    "V.FCVTI",
    "V.ICVT",
    "V.ICVTF",
}

VECTOR_SIGNED_INT_MNEMONICS = {
    "V.CMP.GE",
    "V.CMP.GEI",
    "V.CMP.LT",
    "V.CMP.LTI",
    "V.DIV",
    "V.LD.MAX",
    "V.LD.MIN",
    "V.LW.MAX",
    "V.LW.MIN",
    "V.MAX",
    "V.MIN",
    "V.RDMAX",
    "V.RDMIN",
    "V.REM",
    "V.SD.MAX",
    "V.SD.MIN",
    "V.SRA",
    "V.SRAI",
    "V.SW.MAX",
    "V.SW.MIN",
}

VECTOR_ALL_MNEMONICS_PREFIX = "V."


def norm_exec_name(mnemonic: str) -> str:
    value = mnemonic.lower().replace(".", "_").replace(" ", "_").replace("-", "_")
    while "__" in value:
        value = value.replace("__", "_")
    return f"exec_{value}"


EXEC_ALIASES = {
    "exec_oriw": "exec_orizw",
    "exec_hl_bstart_call": "exec_bstart_call",
}


PARAM_ALIASES = {
    "acr_id": "ACR-ID",
    "cross_bid": "CROSS-BID",
    "imm5": "uimm5",
    "ssrid": "SSRID",
    "ssr_id12": "SSR_ID",
    "ssr_id24": "SSR_ID",
    "lsr_id12": "LSR_ID",
    "uimm15": "uimm",
    "simm17": "simm",
    "imm32": "imm",
    "SrcD0": "SrcD",
}

SYMBOLIC_VALUES = {
    "RA": "0b01010",
}


BLOCK_TYPE_CODES = {
    "BSTART": "0b0000",
    "BSTART CALL": "0b0000",
    "BSTART.STD": "0b0000",
    "C.BSTART": "0b0000",
    "C.BSTART.STD": "0b0000",
    "HL.BSTART.STD": "0b0000",
    "BSTART.SYS": "0b0001",
    "C.BSTART.SYS": "0b0001",
    "HL.BSTART.SYS": "0b0001",
    "BSTART.FP": "0b0010",
    "C.BSTART.FP": "0b0010",
    "HL.BSTART.FP": "0b0010",
    "BSTART.VPAR": "0b0011",
    "C.BSTART.VPAR": "0b0011",
    "BSTART.VSEQ": "0b0100",
    "C.BSTART.VSEQ": "0b0100",
    "BSTART.MPAR": "0b0101",
    "C.BSTART.MPAR": "0b0101",
    "BSTART.MSEQ": "0b0110",
    "C.BSTART.MSEQ": "0b0110",
    "BSTART.PAR": "0b0111",
    "BSTART.TLOAD": "0b1000",
    "BSTART.TSTORE": "0b1001",
    "BSTART.TMOV": "0b1010",
    "BSTART.CUBE": "0b1011",
    "BSTART.TMA": "0b1100",
    "BSTART.TEPL": "0b1101",
    "BSTART.FIXP": "0b1110",
    "BSTART.TMATMUL": "0b1111",
    "BSTART.TMATMUL.ACC": "0b1111",
    "BSTART.ACCCVT": "0b1111",
}


CONTRACT_KIND_CODES = {
    "BSTART.VPAR": "0b0001",
    "BSTART.VSEQ": "0b0001",
    "BSTART.MPAR": "0b0001",
    "BSTART.MSEQ": "0b0001",
    "C.BSTART.VPAR": "0b0001",
    "C.BSTART.VSEQ": "0b0001",
    "C.BSTART.MPAR": "0b0001",
    "C.BSTART.MSEQ": "0b0001",
    "BSTART.TLOAD": "0b0010",
    "BSTART.TSTORE": "0b0010",
    "BSTART.TMOV": "0b0011",
    "BSTART.TMATMUL": "0b0100",
    "BSTART.TMATMUL.ACC": "0b0100",
    "BSTART.ACCCVT": "0b0101",
    "BSTART.TEPL": "0b0110",
    "BSTART.FIXP": "0b0110",
    "BSTART.TMA": "0b0110",
    "BSTART.CUBE": "0b0110",
    "BSTART.PAR": "0b0110",
}


BRTYPE_TO_XFER = {
    "FALL": "block_xfer_fall()",
    "DIRECT": "block_xfer_direct()",
    "COND": "block_xfer_cond()",
    "CALL": "block_xfer_call()",
    "IND": "block_xfer_ind()",
    "ICALL": "block_xfer_icall()",
    "RET": "block_xfer_ret()",
}


def sanitize(name: str) -> str:
    reserved = {
        "default",
        "else",
        "foreach",
        "function",
        "if",
        "let",
        "match",
        "register",
        "then",
        "type",
        "val",
    }
    out = name.lower()
    out = out.replace("/", "_").replace("-", "_").replace(".", "_").replace("=", "_")
    out = re.sub(r"[^a-z0-9_]+", "_", out)
    out = re.sub(r"_+", "_", out).strip("_")
    if not out:
        out = "field"
    if out[0].isdigit():
        out = f"f_{out}"
    if out in reserved:
        out = f"{out}_field"
    return out


def execute_signatures(text: str) -> dict[str, list[str]]:
    return {
        match.group(1): [
            part.strip().split(":", 1)[0].strip()
            for part in match.group(2).split(",")
            if part.strip()
        ]
        for match in re.finditer(
            r"^function (exec_[A-Za-z0-9_]+)\((.*?)\) -> unit = \{",
            text,
            re.M,
        )
    }


def aggregate_fields(inst: dict) -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for part in inst["encoding"]["parts"]:
        for field in part["fields"]:
            entry = merged.setdefault(
                field["name"],
                {"name": field["name"], "pieces": [], "signed": field.get("signed")},
            )
            for piece in field["pieces"]:
                piece_copy = dict(piece)
                piece_copy["part_index"] = part["index"]
                entry["pieces"].append(piece_copy)
    return merged


def bitwidth_from_field(field: dict) -> int:
    width = 0
    for piece in field["pieces"]:
        if "value_msb" in piece:
            width = max(width, piece["value_msb"] + 1)
        else:
            width = max(width, piece["width"])
    return width


def parse_hexish(value: str | int) -> int:
    if isinstance(value, int):
        return value
    return int(value, 16)


def popcount(hexish: str | int) -> int:
    value = parse_hexish(hexish)
    bit_count = getattr(value, "bit_count", None)
    if bit_count is not None:
        return bit_count()
    return bin(value).count("1")


def piece_expr(piece: dict, width: int) -> str:
    part_index = piece.get("part_index", 0)
    var = f"part{part_index}" if width == 64 else "inst"
    lo = piece["insn_lsb"]
    hi = piece["insn_msb"]
    if lo == hi:
        return f"{var}[{hi}]"
    return f"{var}[{hi}..{lo}]"


def zero_bits(width: int) -> str:
    if width <= 0:
        raise ValueError("zero_bits width must be positive")
    return "0b" + ("0" * width)


def field_expr(field: dict, width: int) -> str:
    pieces = list(field["pieces"])
    if len(pieces) == 1 and "value_msb" not in pieces[0]:
        return piece_expr(pieces[0], width)
    total_width = bitwidth_from_field(field)
    pieces.sort(key=lambda piece: piece.get("value_msb", piece["width"] - 1), reverse=True)
    exprs = []
    expected_hi = total_width - 1
    for piece in pieces:
        piece_hi = piece.get("value_msb", piece["width"] - 1)
        piece_lo = piece.get("value_lsb", 0)
        if expected_hi > piece_hi:
            exprs.append(zero_bits(expected_hi - piece_hi))
        exprs.append(piece_expr(piece, width))
        expected_hi = piece_lo - 1
    if expected_hi >= 0:
        exprs.append(zero_bits(expected_hi + 1))
    return " @ ".join(exprs)


def field_map(inst: dict) -> dict[str, tuple[str, int]]:
    merged = aggregate_fields(inst)
    mapping: dict[str, tuple[str, int]] = {}
    for name, field in merged.items():
        mapping.setdefault(name, (sanitize(name), bitwidth_from_field(field)))
        if "=" in name:
            base = name.split("=", 1)[0]
            mapping.setdefault(base, mapping[name])
    return mapping


def hex_const(value: str | int, width: int) -> str:
    digits = width // 4
    return f"0x{parse_hexish(value):0{digits}x}"


def bit_const(width: int, value: int) -> str:
    return "0b" + format(value, f"0{width}b")


def constraint_expr(inst: dict, field_name: str, op: str, value: str) -> str:
    merged = aggregate_fields(inst)
    field = merged[field_name]
    expr = field_expr(field, inst["length_bits"])
    width = bitwidth_from_field(field)
    if value in SYMBOLIC_VALUES:
        rhs = SYMBOLIC_VALUES[value]
    else:
        rhs = bit_const(width, int(value, 0))
    if op == "!=":
        return f"({expr} != {rhs})"
    if op == ">=":
        return f"(unsigned({expr}) >= {int(value, 0)})"
    raise ValueError(f"unsupported constraint op {op!r} for {inst['mnemonic']}")


def branch_condition(inst: dict) -> str:
    parts = inst["encoding"]["parts"]
    width = inst["length_bits"]
    if width in (16, 32, 48):
        part = parts[0]
        conditions = [f"(inst & {hex_const(part['mask'], width)}) == {hex_const(part['match'], width)}"]
    else:
        conditions = []
        for part in parts:
            conditions.append(
                f"(part{part['index']} & {hex_const(part['mask'], part['width_bits'])}) == {hex_const(part['match'], part['width_bits'])}"
            )
    for part in parts:
        for constraint in part.get("constraints", []):
            conditions.append(
                constraint_expr(inst, constraint["field"], constraint["op"], constraint["value"])
            )
    return " & ".join(conditions)


def decode_vector_type_expr(raw_name: str, mnemonic: str) -> str:
    if mnemonic in VECTOR_CONVERT_MNEMONICS:
        return "0b00001"
    if mnemonic in VECTOR_FP_MNEMONICS:
        return f"regid10_vector_fp_type({raw_name})"
    if mnemonic in VECTOR_SIGNED_INT_MNEMONICS:
        return "0b01001"
    return "0b00001"


def block_xfer_expr(inst: dict, raw_fields: dict[str, tuple[str, int]]) -> str:
    asm = inst["asm"]
    if "BrType" in asm:
        return f"decode_block_brtype({raw_fields['BrType'][0]})"
    for key, expr in BRTYPE_TO_XFER.items():
        if key in asm:
            return expr
    if inst["mnemonic"] == "BSTART":
        if "COND" in asm:
            return "block_xfer_cond()"
        return "block_xfer_direct()"
    if inst["mnemonic"] == "C.BSTART":
        if "COND" in asm:
            return "block_xfer_cond()"
        return "block_xfer_direct()"
    if inst["mnemonic"] in {"BSTART CALL", "HL.BSTART CALL"}:
        return "block_xfer_call()"
    return "block_xfer_fall()"


def block_target_expr(inst: dict, raw_fields: dict[str, tuple[str, int]]) -> str:
    fields = {field["name"] for part in inst["encoding"]["parts"] for field in part["fields"]}
    if "simm12" in fields:
        return f"decode_block_target12({raw_fields['simm12'][0]})"
    if "simm17" in fields:
        return f"decode_block_target17({raw_fields['simm17'][0]})"
    if "simm25" in fields:
        return f"decode_block_target25({raw_fields['simm25'][0]})"
    if "simm" in fields:
        return f"decode_block_target30({raw_fields['simm'][0]})"
    if "BrType" in inst["asm"]:
        return "read_pc_or_tpc()"
    if "RET" in inst["asm"] or "IND" in inst["asm"] or "ICALL" in inst["asm"]:
        return "read_pc_or_tpc()"
    return "read_pc_or_tpc()"


def param_expr(inst: dict, param: str, raw_fields: dict[str, tuple[str, int]]) -> str | None:
    if param == "RegDst" and inst["mnemonic"].startswith("V.RD") and "RegDst" in raw_fields:
        return f"{raw_fields['RegDst'][0]}[4..0]"
    if (
        inst["mnemonic"].startswith("V.")
        and param in {"RegDst", "SrcL", "SrcR"}
        and param in raw_fields
        and raw_fields[param][1] > 5
    ):
        return f"{raw_fields[param][0]}[4..0]"
    if param == "acr_id" and "ACR-ID" in raw_fields:
        return f"sail_zero_extend({raw_fields['ACR-ID'][0]}, 12)"
    if param == "cross_bid" and "CROSS-BID" in raw_fields:
        return f"sail_zero_extend({raw_fields['CROSS-BID'][0]}, 8)"
    if param in raw_fields:
        return raw_fields[param][0]
    alias = PARAM_ALIASES.get(param)
    if alias and alias in raw_fields:
        return raw_fields[alias][0]

    if param in {"SrcL_k", "SrcR_k", "SrcA_k", "SrcD_k", "Dst_k", "RegDst_k", "SrcP_k"}:
        source = {
            "SrcL_k": "SrcL",
            "SrcR_k": "SrcR",
            "SrcA_k": "SrcA",
            "SrcD_k": "SrcD",
            "Dst_k": "RegDst",
            "RegDst_k": "RegDst",
            "SrcP_k": "SrcP" if "SrcP" in raw_fields else "SrcZero",
        }[param]
        return f"decode_vec_reg_selector({raw_fields[source][0]})"

    if param == "Nminus1":
        if "imms" in raw_fields:
            return raw_fields["imms"][0]
        if inst["mnemonic"] == "REV" and "imml" in raw_fields:
            return raw_fields["imml"][0]

    if param == "M":
        if "imml" in raw_fields:
            return raw_fields["imml"][0]
        if "immr" in raw_fields:
            return raw_fields["immr"][0]

    if param == "imm7" and "imm" in raw_fields:
        return raw_fields["imm"][0]

    if param == "neg" and "SrcRType" in raw_fields:
        return f"decode_srcrtype_neg({raw_fields['SrcRType'][0]})"

    if param == "local" and "L" in raw_fields:
        return raw_fields["L"][0]

    if param == "RegDst" and inst["mnemonic"] in {"C.SLLI", "C.SRLI"}:
        return "reg_t()"
    if param == "SrcL" and inst["mnemonic"] in {"C.SLLI", "C.SRLI"}:
        return "reg_t1()"
    if param == "SrcRType" and inst["mnemonic"] == "SETC.TGT":
        return "0b00"
    if param == "SrcD" and "SrcL" in raw_fields:
        return raw_fields["SrcL"][0]

    return None


def prelude_lines(inst: dict, raw_fields: dict[str, tuple[str, int]], width: int) -> list[str]:
    lines: list[str] = []
    mnemonic = inst["mnemonic"]
    asm = inst["asm"]

    if mnemonic == "B.DIM":
        if "LB0" in asm:
            idx = "0b00"
        elif "LB1" in asm:
            idx = "0b01"
        else:
            idx = "0b10"
        reg_src = raw_fields["RegSrc"][0]
        uimm17 = raw_fields["uimm17"][0]
        lines.append(f"decoded_bdim_index_shadow = {idx};")
        lines.append(f"decoded_bdim_value_shadow = read_reg5({reg_src}) + sail_zero_extend({uimm17}, 64);")

    elif mnemonic == "C.B.DIM":
        lines.append(f"decoded_bdim_index_shadow = {raw_fields['LoopNest'][0]}[1..0];")
        lines.append(f"decoded_bdim_value_shadow = read_reg5({raw_fields['RegSrc'][0]});")

    elif mnemonic == "C.B.DIMI":
        lines.append(f"decoded_bdim_index_shadow = {raw_fields['LoopNest'][0]};")
        lines.append(f"decoded_bdim_value_shadow = sail_zero_extend({raw_fields['imm8'][0]}, 64);")

    elif mnemonic == "B.CATR":
        lines.append("decoded_bcatr_raw_shadow = sail_zero_extend(inst, 64);")

    elif mnemonic == "B.DATR":
        lines.append("decoded_bdatr_raw_shadow = sail_zero_extend(inst, 64);")

    elif mnemonic == "B.IOR":
        lines.append(
            "set_decoded_bior("
            f"{raw_fields['RegSrc0'][0]}, "
            f"{raw_fields['RegSrc1'][0]}, "
            f"{raw_fields['RegSrc2'][0]}, "
            f"{raw_fields['RegDst'][0]});"
        )

    if mnemonic.startswith("BSTART") or mnemonic.startswith("C.BSTART") or mnemonic.startswith("HL.BSTART"):
        block_type = BLOCK_TYPE_CODES.get(mnemonic, "0b0000")
        contract_kind = CONTRACT_KIND_CODES.get(mnemonic, "0b0000")
        lines.append(f"decoded_block_target_pc_shadow = {block_target_expr(inst, raw_fields)};")
        lines.append(f"decoded_block_type_shadow = {block_type};")
        lines.append(f"decoded_block_xfer_kind_shadow = {block_xfer_expr(inst, raw_fields)};")
        lines.append(f"decoded_block_contract_kind_shadow = {contract_kind};")

    if mnemonic.startswith(VECTOR_ALL_MNEMONICS_PREFIX):
        srcl_t = "decoded_vec_srcl_type_shadow"
        srcr_t = "decoded_vec_srcr_type_shadow"
        srca_t = "decoded_vec_srca_type_shadow"
        srcp_t = "decoded_vec_srcp_type_shadow"
        dst_t = "decoded_vec_dst_type_shadow"

        srcl = (
            decode_vector_type_expr(raw_fields["SrcL"][0], mnemonic)
            if "SrcL" in raw_fields
            else "0b00001"
        )
        srcr = (
            decode_vector_type_expr(raw_fields["SrcR"][0], mnemonic)
            if "SrcR" in raw_fields
            else "0b00001"
        )
        srca = (
            decode_vector_type_expr(raw_fields["SrcA"][0], mnemonic)
            if "SrcA" in raw_fields
            else "0b00001"
        )
        srcp_name = "SrcP" if "SrcP" in raw_fields else ("SrcZero" if "SrcZero" in raw_fields else None)
        srcp = (
            f"regid10_vector_int_type({raw_fields[srcp_name][0]})"
            if srcp_name is not None
            else "0b00001"
        )
        dst = (
            decode_vector_type_expr(raw_fields["RegDst"][0], mnemonic)
            if "RegDst" in raw_fields
            else "0b00001"
        )
        lines.append(f"{srcl_t} = {srcl};")
        lines.append(f"{srcr_t} = {srcr};")
        lines.append(f"{srca_t} = {srca};")
        lines.append(f"{srcp_t} = {srcp};")
        lines.append(f"{dst_t} = {dst};")
        lines.append(
            "set_decoded_vec_regids("
            f"{raw_fields['SrcL'][0] if 'SrcL' in raw_fields else '0b00_0000_0000'}, "
            f"{raw_fields['SrcR'][0] if 'SrcR' in raw_fields else '0b00_0000_0000'}, "
            f"{raw_fields['SrcA'][0] if 'SrcA' in raw_fields else '0b00_0000_0000'}, "
            f"{raw_fields[srcp_name][0] if srcp_name is not None else '0b00_0000_0000'}, "
            f"{raw_fields['RegDst'][0] if 'RegDst' in raw_fields else '0b00_0000_0000'});"
        )

    return lines


def branch_body(inst: dict, exec_params: dict[str, list[str]]) -> list[str]:
    width = inst["length_bits"]
    raw_field_meta = field_map(inst)
    expr_by_name = {
        name: field_expr(field, width)
        for name, field in aggregate_fields(inst).items()
    }
    lines = [f"// {inst['mnemonic']} | {inst['asm']} | {inst['source']}"]
    for name, (var_name, field_width) in raw_field_meta.items():
        if "=" in name:
            continue
        expr_name = name
        if expr_name not in expr_by_name:
            expr_name = next(
                candidate
                for candidate in expr_by_name
                if candidate.split("=", 1)[0] == name
            )
        lines.append(f"let {var_name} : bits({field_width}) = {expr_by_name[expr_name]};")

    lines.extend(prelude_lines(inst, raw_field_meta, width))

    exec_name = EXEC_ALIASES.get(norm_exec_name(inst["mnemonic"]), norm_exec_name(inst["mnemonic"]))
    params = exec_params.get(exec_name)
    if params is None:
        raise ValueError(f"missing execute function for {inst['mnemonic']} -> {exec_name}")
    args = []
    for param in params:
        expr = param_expr(inst, param, raw_field_meta)
        if expr is None:
            raise ValueError(f"unmapped parameter {param} for {inst['mnemonic']}")
        args.append(expr)
    lines.append(f"{exec_name}({', '.join(args)})" if args else f"{exec_name}()")
    return lines


def render_decode_function(width: int, entries: list[dict], exec_params: dict[str, list[str]]) -> list[str]:
    func_name = WIDTH_FUNCS[width]
    lines = [f"function {func_name}(inst : bits({width})) -> unit = {{"]  # noqa: E231
    if width == 64:
        lines.append("  let part0 : bits(32) = inst[63..32];")
        lines.append("  let part1 : bits(32) = inst[31..0];")
    ordered = sorted(
        entries,
        key=lambda entry: (
            -sum(popcount(part["mask"]) for part in entry["encoding"]["parts"]),
            entry["mnemonic"],
            entry["uid"],
        ),
    )
    for idx, inst in enumerate(ordered):
        prefix = "if" if idx == 0 else "else if"
        lines.append(f"  {prefix} {branch_condition(inst)} then {{")
        for stmt in branch_body(inst, exec_params):
            lines.append(f"    {stmt}")
        lines.append("  }")
    lines.append("  else {")
    lines.append("    trap_illegal_inst(read_pc_or_tpc())")
    lines.append("  }")
    lines.append("}")
    return lines


def render(spec: dict, exec_text: str) -> str:
    exec_params = execute_signatures(exec_text)
    by_width: dict[int, list[dict]] = defaultdict(list)
    for inst in spec["instructions"]:
        by_width[inst["length_bits"]].append(inst)

    lines = [
        "// Generated by tools/isa/gen_sail_decode.py from isa/v0.56/linxisa-v0.56.json.",
        "// Do not edit by hand.",
        "",
        "function decode_srcrtype_neg(srctype : bits(2)) -> bits(1) = {",
        "  if srctype == 0b11 then 0b1 else 0b0",
        "}",
        "",
        "function decode_vec_reg_selector(regid : bits(10)) -> bits(5) = {",
        "  if not_bool(regid10_vector_namespace_ok(regid)) then {",
        "    trap_illegal_inst(read_pc_or_tpc());",
        "    0b00000",
        "  } else {",
        "    let cls : bits(5) = regid10_class(regid);",
        "    let idx : bits(5) = regid10_index(regid);",
        "    if cls == 0b00001 then ri_binding_reg(idx) else regid10_vector_selector(regid)",
        "  }",
        "}",
        "",
        "function decode_block_brtype(brtype : bits(3)) -> block_xfer_kind = {",
        "  if brtype == 0b001 then block_xfer_fall()",
        "  else if brtype == 0b010 then block_xfer_direct()",
        "  else if brtype == 0b011 then block_xfer_cond()",
        "  else if brtype == 0b100 then block_xfer_call()",
        "  else if brtype == 0b101 then block_xfer_ind()",
        "  else if brtype == 0b110 then block_xfer_icall()",
        "  else if brtype == 0b111 then block_xfer_ret()",
        "  else block_xfer_fall()",
        "}",
        "",
        "function decode_block_target12(simm12 : bits(12)) -> bits(64) = {",
        "  read_pc_or_tpc() + sail_shiftleft(sext12_to64(simm12), 1)",
        "}",
        "",
        "function decode_block_target17(simm17 : bits(17)) -> bits(64) = {",
        "  read_pc_or_tpc() + sail_shiftleft(sext17_to64(simm17), 1)",
        "}",
        "",
        "function decode_block_target25(simm25 : bits(25)) -> bits(64) = {",
        "  read_pc_or_tpc() + sail_shiftleft(sext25_to64(simm25), 1)",
        "}",
        "",
        "function decode_block_target30(simm30 : bits(30)) -> bits(64) = {",
        "  read_pc_or_tpc() + sext30_to64(simm30)",
        "}",
        "",
    ]

    for width in (16, 32, 48, 64):
        if by_width.get(width):
            lines.extend(render_decode_function(width, by_width[width], exec_params))
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="isa/v0.56/linxisa-v0.56.json")
    ap.add_argument("--execute", default="isa/sail/model/execute/execute.sail")
    ap.add_argument("--out", default="isa/sail/model/decode/decode.sail")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    execute_text = Path(args.execute).read_text()
    rendered = render(spec, execute_text)
    out_path = Path(args.out)
    if args.check:
        current = out_path.read_text() if out_path.exists() else ""
        if current != rendered:
            raise SystemExit(f"{out_path} is out of date; regenerate with {Path(__file__).name}")
        return 0

    out_path.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
