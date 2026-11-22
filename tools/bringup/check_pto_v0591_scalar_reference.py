#!/usr/bin/env python3
"""Compare scoped Scalar results from QEMU, linx-model and LinxCoreModel."""

import argparse
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "isa/v0.59/state/pto_scalar_forms.json"
PTO_LOCK = ROOT / "isa/v0.59/pto-spec.lock.json"
RESULT_BASE = 0x10000
STORE_VALUE = 0x555A
U64_MASK = (1 << 64) - 1
FINISHER_ADDRESS = 0x10009000
FINISHER_PASS = 0x5555
PCR_RELOCATIONS = {
    (32, "Load"): ("R_LINX_SCOPED_PCR17_LOAD", 33),
    (32, "Store"): ("R_LINX_SCOPED_PCR17_STORE", 34),
    (48, "Load"): ("R_LINX_SCOPED_HL_PCR29_LOAD", 35),
    (48, "Store"): ("R_LINX_SCOPED_HL_PCR29_STORE", 36),
}


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def file_identity(path):
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def repo_identity(path, timeout):
    repo = invoke(
        ["git", "-C", path, "rev-parse", "--show-toplevel"], timeout=timeout
    ).strip()
    head = invoke(["git", "-C", repo, "rev-parse", "HEAD"], timeout=timeout).strip()
    changes = invoke(["git", "-C", repo, "status", "--porcelain"], timeout=timeout)
    return {"path": repo, "commit": head, "dirty": bool(changes)}


def invoke(argv, *, timeout, input_text=None, env=None, case=None, cwd=None):
    result = subprocess.run(
        argv,
        input=input_text,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )
    if case is not None:
        (case / "stdout.log").write_text(result.stdout, encoding="utf-8")
        (case / "stderr.log").write_text(result.stderr, encoding="utf-8")
        write_json(
            case / "run.json",
            {"command": [str(arg) for arg in argv], "exit": result.returncode},
        )
    if result.returncode:
        raise RuntimeError(f"{argv[0]} exited {result.returncode}\n{result.stderr}")
    return result.stdout


def scoped_cases():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    bases = {row["form_id"]: row for row in catalog["forms"]}
    cases = []
    for row in catalog["scoped_forms"]:
        agu = bases[row["base_form_id"]].get("agu")
        if (
            agu
            and agu["action"] in {"Load", "Store"}
            and agu["address_kind"] in {"Immediate", "PCRelative"}
            and agu["update_mode"] == "None"
        ):
            cases.append((row, agu))
    validate_cases(cases)
    return cases


def validate_cases(cases):
    if len(cases) != 180:
        raise ValueError(
            f"expected 180 scoped immediate/PCR carriers, found {len(cases)}"
        )
    if len({row["form_id"] for row, _ in cases}) != len(cases):
        raise ValueError("scoped carrier form IDs must be unique")
    scopes = {}
    for row, _ in cases:
        scopes.setdefault(row["base_form_id"], set()).add(row["scope_code"])
    if len(scopes) != 60 or any(codes != {0, 1, 2} for codes in scopes.values()):
        raise ValueError("expected 60 base forms with all three scopes")


def pack_carrier(row, register_values, immediate):
    word = position = 0
    for part in row["encoding"]:
        word |= int(part["match"], 0) << position
        position += part["width_bits"]
    for field in row["fields"]:
        name = field["name"]
        if name not in register_values and not name.startswith("simm"):
            continue
        value = register_values.get(name, immediate)
        for piece in field["pieces"]:
            field_bits = (value >> piece["value_lsb"]) & ((1 << piece["width"]) - 1)
            word |= field_bits << piece["instruction_lsb"]
    return word


def build_case(output, symbolic_pcr=False):
    cases = scoped_cases()
    length = len(cases) * 8
    header = [
        ".text",
        ".p2align 2",
        ".globl cross_model_result, cross_model_result_size, _start",
        f".set cross_model_result_size, {length}",
        "cross_model_result:",
    ]
    cells = [
        ((0x8877665544332281 + i * 0x102030405060709) & U64_MASK)
        for i in range(len(cases))
    ]
    for i, value in enumerate(cells):
        if symbolic_pcr:
            header.append(f".Lcell{i}:")
        header.append(f".8byte 0x{value:016x}")
    header += [
        "_start:",
        "C.BSTART",
        f"hl.liu {RESULT_BASE}, ->a0",
        f"hl.liu {STORE_VALUE}, ->a2",
    ]

    # C.BSTART plus two HL.LIU instructions precede the first carrier.
    pc = length + 2 + 6 + 6
    instructions = []
    segments = []
    pcr_relocations = []
    golden = bytearray()
    for i, ((row, agu), initial) in enumerate(zip(cases, cells, strict=True)):
        offset = 8 * i
        load = agu["action"] == "Load"
        displacement = (
            offset - (pc & ~3) if agu["address_kind"] == "PCRelative" else offset
        )
        scale = 1 << agu["offset_scale"]
        if displacement % scale:
            raise ValueError(f"nonrepresentable target for {row['form_id']}")
        regs = {"RegDst": 3, "SrcL": 2 if load else 4, "SrcR": 2, "SrcD": 4}
        if symbolic_pcr and agu["address_kind"] == "PCRelative":
            mnemonic = row["asm"].split(" ", 1)[0]
            target = f"[.Lcell{i}]"
            operands = f"{target}, ->a1" if load else f"a2, {target}"
            instructions.append(f"{mnemonic} {operands}")
            name, number = PCR_RELOCATIONS[row["inner_length_bits"], agu["action"]]
            pcr_relocations.append((pc, name, number))
        else:
            word = pack_carrier(row, regs, displacement // scale)
            instructions.append(f".8byte 0x{word:016x}")
        pc += 8
        bits = agu["size_bytes"] * 8
        mask = (1 << bits) - 1
        if load:
            instructions.append(f"sdi a1, [a0, {offset}]")
            pc += 4
            value = initial & mask
            if agu["signed_load"] and value & (1 << (bits - 1)):
                value -= 1 << bits
            value &= U64_MASK
        else:
            value = (initial & ~mask) | (STORE_VALUE & mask)
        golden.extend(value.to_bytes(8, "little"))
        segments.append(
            {"form_id": row["form_id"], "offset": offset, "size": 8, "type": "u64le"}
        )

    end = [
        "C.BSTOP",
        "C.BSTART",
        "hl.liu 21845, ->a0",
        "hl.liu 268472320, ->t",
        "swi a0, [t#1, 0]",
        "C.BSTOP",
    ]
    source = output / "scoped_scalar.s"
    source.write_text("\n".join(header + instructions + end) + "\n", encoding="utf-8")
    (output / "golden.bin").write_bytes(golden)
    return source, bytes(golden), segments, pcr_relocations


def check_pcr_relocations(readobj, obj, expected, timeout):
    output = invoke(
        [readobj, "--elf-output-style=JSON", "--expand-relocs", "--relocations", obj],
        timeout=timeout,
    )
    actual = []
    for section in json.loads(output)[0]["Relocations"]:
        for entry in section["Relocs"]:
            rel = entry["Relocation"]
            name = rel["Type"]["Name"]
            if name.startswith("R_LINX_SCOPED_"):
                actual.append((rel["Offset"], name, rel["Type"]["Value"]))
    if sorted(actual) != expected:
        raise ValueError("scoped PCR relocations differ in type or carrier-start offset")


def read_elf_contract(readobj, elf, timeout):
    notes = invoke([readobj, "--string-dump=.note.pto.isa", elf], timeout=timeout)
    lock = json.loads(PTO_LOCK.read_text(encoding="utf-8"))
    descriptor = {
        key: lock[key]
        for key in ("encoding_abi", "encoding_projection_sha256", "release")
    }
    if notes.count(json.dumps(descriptor, separators=(",", ":"))) != 1:
        raise ValueError("ELF must have the locked PTO 0.59.1 identity")
    symbols = invoke([readobj, "--symbols", elf], timeout=timeout)
    names = ("cross_model_result", "cross_model_result_size")
    result = []
    for name in names:
        matches = re.findall(
            rf"\bName: {name} \([^\n]*\)\n\s+Value: (0x[0-9a-fA-F]+)", symbols
        )
        if len(matches) != 1:
            raise ValueError(f"ELF must define {name} exactly once")
        result.append(int(matches[0], 16))
    return tuple(result)


def qemu_preflight(qemu, elf, timeout, env):
    qmp = [
        {"execute": "qmp_capabilities"},
        {"execute": "qom-list", "arguments": {"path": "/machine"}},
        {"execute": "quit"},
    ]
    output = invoke(
        [
            qemu,
            "-display",
            "none",
            "-serial",
            "none",
            "-monitor",
            "none",
            "-machine",
            "virt",
            "-smp",
            "1",
            "-bios",
            "none",
            "-kernel",
            elf,
            "-S",
            "-qmp",
            "stdio",
        ],
        timeout=timeout,
        input_text="\n".join(map(json.dumps, qmp)) + "\n",
        env=env,
    )
    properties = set()
    for line in output.splitlines():
        result = json.loads(line).get("return")
        if isinstance(result, list):
            properties.update(item["name"] for item in result)
    required = {"cross-model-dump", "cross-model-address", "cross-model-size"}
    if not required <= properties:
        raise ValueError(
            f"QEMU is missing machine properties: {sorted(required - properties)}"
        )


def compare(expected, actual, segments):
    if len(actual) != len(expected):
        return {
            "pass": False,
            "expected_size": len(expected),
            "actual_size": len(actual),
        }
    for row in segments:
        start = row["offset"]
        expected_value = expected[start : start + 8]
        actual_value = actual[start : start + 8]
        if actual_value != expected_value:
            return {
                "pass": False,
                **row,
                "expected": expected_value.hex(),
                "actual": actual_value.hex(),
            }
    return {"pass": True, "bytes": len(expected)}


def require_pass_finisher(trace):
    last = {}
    with trace.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                last = json.loads(line)
    expected = {
        "trap_valid": 0,
        "mem_valid": 1,
        "mem_is_store": 1,
        "mem_addr": FINISHER_ADDRESS,
        "mem_size": 4,
        "mem_wdata": FINISHER_PASS,
    }
    if any(last.get(key) != value for key, value in expected.items()):
        raise ValueError(f"{trace.parent.name} did not retire the pass finisher")


def run_linxcore_model(tool, elf, address, size, case, timeout):
    case.mkdir()
    result = case / "result.bin"
    stdout = invoke(
        [
            tool,
            "-f",
            elf,
            "--result_address",
            str(address),
            "--result_size",
            str(size),
            "--result_file",
            result,
        ],
        timeout=timeout,
        case=case,
        cwd=case,
    )
    if (
        "linx_test_finisher write addr=0x10009000 val=0x5555 pass"
        not in stdout.splitlines()
    ):
        raise ValueError(f"{case.name} did not report the pass finisher")
    data = result.read_bytes()
    if len(data) != size:
        raise ValueError(
            f"{case.name} exported {len(data)} result bytes, expected {size}"
        )
    return data


def compare_models(results, golden, segments):
    comparisons = {
        f"{model}_to_golden": compare(golden, data, segments)
        for model, data in results.items()
    }
    for (left, lhs), (right, rhs) in combinations(results.items(), 2):
        comparisons[f"{left}_to_{right}"] = compare(lhs, rhs, segments)
    return comparisons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llvm-bin", required=True, type=Path)
    parser.add_argument("--qemu", required=True, type=Path)
    parser.add_argument("--linx-model", required=True, type=Path)
    parser.add_argument("--gfrun", type=Path)
    parser.add_argument("--gfsim", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", default=30, type=int)
    parser.add_argument("--symbolic-pcr", action="store_true",
                        help="assemble PCR targets with the scoped relocation ABI")
    args = parser.parse_args()
    llvm_bin = args.llvm_bin.resolve()
    tools = {name: llvm_bin / name for name in ("llvm-mc", "ld.lld", "llvm-readobj")}
    tools.update({"qemu": args.qemu.resolve(), "linx-model": args.linx_model.resolve()})
    core_models = {
        name: path.resolve()
        for name, path in (("gfrun", args.gfrun), ("gfsim", args.gfsim))
        if path is not None
    }
    tools.update(core_models)
    output = args.output.resolve()
    output.mkdir(parents=True)
    source, golden, segments, pcr_relocations = build_case(output, args.symbolic_pcr)
    obj, elf = output / "scoped_scalar.o", output / "scoped_scalar.elf"
    invoke(
        [
            tools["llvm-mc"],
            "-triple=linx64",
            "-mattr=+pto-v0591-scoped",
            "-filetype=obj",
            source,
            "-o",
            obj,
        ],
        timeout=args.timeout,
    )
    if args.symbolic_pcr:
        check_pcr_relocations(tools["llvm-readobj"], obj, pcr_relocations, args.timeout)
    invoke(
        [
            tools["ld.lld"],
            "-m",
            "elf64linx",
            "--linx-pto-v0591-scoped",
            f"--section-start=.text={RESULT_BASE:#x}",
            obj,
            "-o",
            elf,
        ],
        timeout=args.timeout,
    )
    address, size = read_elf_contract(tools["llvm-readobj"], elf, args.timeout)
    if (address, size) != (RESULT_BASE, len(golden)):
        raise ValueError(f"unexpected result range in ELF: {address:#x}, {size}")
    manifest = output / "resolved_manifest.json"
    write_json(manifest, {"address": address, "size": size, "segments": segments})
    artifacts = {
        **tools,
        "object": obj,
        "elf": elf,
        "manifest": manifest,
        "catalog": CATALOG,
        "pto_lock": PTO_LOCK,
    }
    identities = {name: file_identity(path) for name, path in artifacts.items()}
    sources = {
        "linx-isa": ROOT,
        "llvm": llvm_bin,
        "qemu": tools["qemu"].parent,
        "linx-model": tools["linx-model"].parent,
    }
    sources.update({name: path.parent for name, path in core_models.items()})
    repositories = {
        name: repo_identity(path, args.timeout) for name, path in sources.items()
    }
    write_json(
        output / "provenance.json",
        {
            "schema_version": 1,
            "artifacts": identities,
            "repositories": repositories,
            "selected_models": ["qemu", "linx-model", *core_models],
            "pe_count": 1,
            "linxisa_encoding_version": "v0.59-candidate",
            "pto_isa_version": "0.59.1",
            "model_profile": "single-PE scoped immediate/PCR reference",
            "symbolic_pcr_relocations": len(pcr_relocations),
        },
    )

    env = {
        key: value for key, value in os.environ.items() if not key.startswith("LINX_")
    }
    env.update({"LINX_QEMU_SCOPED_SCALAR_RUNTIME": "1", "LINX_VIRT_TEST_FINISHER": "1"})
    qemu_preflight(tools["qemu"], elf, args.timeout, env)
    qemu_case, model_case = output / "qemu", output / "linx-model"
    qemu_case.mkdir()
    model_case.mkdir()
    qemu_trace = qemu_case / "commits.jsonl"
    model_trace = model_case / "commits.jsonl"
    qemu_result = str(qemu_case / "result.bin").replace(",", ",,")
    machine = f"virt,cross-model-dump={qemu_result},cross-model-address={address},cross-model-size={size}"
    invoke(
        [
            tools["qemu"],
            "-nographic",
            "-monitor",
            "none",
            "-machine",
            machine,
            "-smp",
            "1",
            "-bios",
            "none",
            "-kernel",
            elf,
        ],
        timeout=args.timeout,
        env={**env, "LINX_COMMIT_TRACE": str(qemu_trace)},
        case=qemu_case,
    )
    invoke(
        [
            tools["linx-model"],
            "--bin",
            elf,
            "--engine",
            "ref",
            "--enable-pto-v0591-scoped",
            "--emit-minst-trace",
            model_trace,
            "--result-address",
            str(address),
            "--result-size",
            str(size),
            "--result-dump",
            model_case / "result.bin",
        ],
        timeout=args.timeout,
        case=model_case,
    )
    require_pass_finisher(qemu_trace)
    require_pass_finisher(model_trace)
    results = {
        "qemu": (qemu_case / "result.bin").read_bytes(),
        "linx_model": (model_case / "result.bin").read_bytes(),
    }
    failures = {}
    for name, tool in core_models.items():
        try:
            results[name] = run_linxcore_model(
                tool, elf, address, size, output / name, args.timeout
            )
        except (OSError, RuntimeError, subprocess.TimeoutExpired, ValueError) as error:
            failures[f"{name}_to_golden"] = {"pass": False, "error": str(error)}
    result = {
        "elf_sha256": identities["elf"]["sha256"],
        "carriers": len(segments),
        **compare_models(results, golden, segments),
        **failures,
    }
    if any(
        file_identity(path) != identities[name] for name, path in artifacts.items()
    ) or any(
        repo_identity(path, args.timeout) != repositories[name]
        for name, path in sources.items()
    ):
        raise ValueError("validation inputs changed while the models ran")
    write_json(output / "compare.json", result)
    for name, comparison in result.items():
        if isinstance(comparison, dict) and not comparison["pass"]:
            raise SystemExit(f"{name}: {comparison}")
    print(
        f"PASS: {len(segments)} scoped Scalar carriers, {size} bytes across "
        f"{len(results)} models"
    )


if __name__ == "__main__":
    main()
