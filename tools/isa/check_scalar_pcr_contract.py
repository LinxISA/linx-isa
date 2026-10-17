#!/usr/bin/env python3
"""Check Sail PCR wiring against the authenticated PTO scalar catalog.

This is a source-contract check, not memory-execution conformance. Run the
pinned Sail directed gate as well to test the address helper's arithmetic.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from pto_scalar_proposal import apply_proposal


ROOT = Path(__file__).resolve().parents[2]


def pcr_forms(root: Path) -> list[dict]:
    profile = root / "isa/v0.58"
    catalog = json.loads((profile / "state/pto_scalar_forms.json").read_text())
    apply_proposal(profile, catalog)
    return [form for form in catalog["forms"]
            if form.get("agu", {}).get("address_kind") == "PCRelative"]


def function_parts(source: str, name: str) -> tuple[str, str]:
    matches = re.findall(
        rf"^function {re.escape(name)}\((.*?)\)\s*->[^\n]+?=\s*\{{\n(.*?)^\}}",
        source, re.MULTILINE | re.DOTALL,
    )
    if len(matches) != 1:
        raise ValueError(f"expected one auditable Sail function {name}")
    return matches[0]


def check_wiring(forms: list[dict], execution: str, decoder: str) -> list[str]:
    errors: list[str] = []
    expected = {"exec_" + form["mnemonic"].lower().replace(".", "_")
                for form in forms}
    actual = {name for name in re.findall(r"^function (exec_\w+_pcr)\(",
                                         execution, re.MULTILINE)
              if not name.startswith("exec_v_")}
    if actual != expected:
        errors.append(f"PCR function inventory mismatch: missing={sorted(expected - actual)}, "
                      f"extra={sorted(actual - expected)}")

    for helper, width in (("ea_pcr17", 17), ("hl_ea_pcr", 29)):
        try:
            params, body = function_parts(execution, helper)
            immediate = re.findall(rf"(\w+)\s*:\s*bits\({width}\)", params)
            if len(immediate) != 1:
                raise ValueError(f"{helper}: expected one signed {width}-bit immediate")
            required = (f"scalar_pcr_address(read_pc_or_tpc(),"
                        f"sext{width}_to64({immediate[0]}),scale)")
            if re.sub(r"\s+", "", body) != required:
                errors.append(f"{helper}: must preserve the current-PC adapter and signed {width}-bit offset")
        except ValueError as exc:
            errors.append(str(exc))

    for form in forms:
        name = form["mnemonic"]
        function = "exec_" + name.lower().replace(".", "_")
        agu = form["agu"]
        if agu["action"] not in {"Load", "Store"}:
            errors.append(f"{name}: unsupported PCR memory action {agu['action']}")
            continue
        signed_fields = [field for field in form["fields"]
                         if field.get("signedness") == "signed"]
        if len(signed_fields) != 1:
            errors.append(f"{name}: expected one signed catalog displacement")
            continue
        width = signed_fields[0]["width"]
        helper = {17: "ea_pcr17", 29: "hl_ea_pcr"}.get(width)
        if helper is None:
            errors.append(f"{name}: unsupported PCR displacement width {width}")
            continue
        try:
            params, body = function_parts(execution, function)
            registers = re.findall(r"(\w+)\s*:\s*bits\(5\)", params)
            immediate = re.findall(rf"(\w+)\s*:\s*bits\({width}\)", params)
            if len(immediate) != 1 or len(registers) != 1:
                raise ValueError(f"{name}: Sail operand widths differ from catalog")
            register = registers[0]
            load = agu["action"] == "Load"
            data_field = "RegDst" if load else "SrcL"
            if not any(field["name"] == data_field and field["width"] == 5
                       for field in form["fields"]):
                raise ValueError(f"{name}: missing catalog data operand {data_field}")
            calls = re.findall(rf"\b{function}\(([^\n]*)\)", decoder)
            expected_call = f"{data_field.lower()},{signed_fields[0]['name'].lower()}"
            if [re.sub(r"\s+", "", call) for call in calls] != [expected_call]:
                errors.append(f"{name}: decoded data/displacement binding differs from catalog")
            guard = ("scalar_gpr_or_discard_destination_supported" if load
                     else "scalar_gpr_source_supported")
            prefix = (rf"\s*if\s+not_bool\({guard}\({register}\)\)\s+then\s+"
                      r"trap_illegal_inst\(read_pc_or_tpc\(\)\)\s+else\s*\{")
            if not re.match(prefix, body):
                errors.append(f"{name}: unsupported queue operands must reject before effects")
            call = rf"let\s+ea\s*=\s*{helper}\({immediate[0]},\s*{agu['offset_scale']}\);"
            if not re.search(call, body):
                errors.append(f"{name}: PCR helper/scale differs from catalog")
            bits = agu["size_bytes"] * 8
            memory_op = (("read_mem8" if load else "write_mem8") if bits == 8
                         else f"mem_{'load' if load else 'store'}{bits}_le")
            accesses = re.findall(r"\b(read_mem8|write_mem8|mem_load\d+_le|mem_store\d+_le)\(", body)
            if accesses != [memory_op] or not re.search(rf"\b{memory_op}\(ea\b", body):
                errors.append(f"{name}: memory action/width/address differs from catalog")
            writes = re.findall(r"\b(write_regdst|write_reg5|write_scalar_gpr_or_discard)\(", body)
            if load:
                value = re.search(rf"let\s+(\w+)\s*:\s*bits\({bits}\)\s*=\s*{memory_op}\(ea\);", body)
                if value is None:
                    errors.append(f"{name}: loaded value is not captured at catalog width")
                    continue
                expression = value[1]
                if bits < 64:
                    expression = f"{'s' if agu['signed_load'] else 'z'}ext{bits}_from{bits}({expression})"
                if writes != ["write_scalar_gpr_or_discard"] or not re.search(
                    rf"write_scalar_gpr_or_discard\({register},\s*{re.escape(expression)}\)", body
                ):
                    errors.append(f"{name}: loaded value/extension/destination publication differs from catalog")
            else:
                truncation = "" if bits == 64 else rf"\[{bits - 1}\.\.0\]"
                value = re.search(rf"let\s+(\w+)\s*:\s*bits\({bits}\)\s*=\s*read_reg5\({register}\){truncation};", body)
                if value is None or writes or not re.search(
                    rf"{memory_op}\(ea,\s*{value[1]}\)", body
                ):
                    errors.append(f"{name}: store source/truncation/payload differs from catalog")
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        forms = pcr_forms(args.root)
        errors = check_wiring(
            forms,
            (args.root / "isa/sail/model/execute/execute.sail").read_text(),
            (args.root / "isa/sail/model/decode/decode.sail").read_text(),
        )
    except (ValueError, KeyError) as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(errors))
        return 1
    print(f"OK: {len(forms)} scalar PCR Sail GPR/discard bindings match PTO golden; "
          "execute the Sail directed gate for arithmetic proof")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
