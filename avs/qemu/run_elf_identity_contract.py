#!/usr/bin/env python3
"""Exercise QEMU's fail-closed PTO ISA ELF identity loader contract."""

from __future__ import annotations

import argparse
import os
import struct
import subprocess
import tempfile
from pathlib import Path


IDENTITY = (
    b'{"encoding_abi":"pto-isa-0.58.1-mode-function-v1",'
    b'"encoding_projection_sha256":'
    b'"89b872d6eaf0252200bc9349d49b9346e2a69d894cdcc2dcd0fd71911c1e0b8c",'
    b'"release":"0.58.1"}'
)
OLD_IDENTITY = IDENTITY.replace(b'"release":"0.58.1"', b'"release":"0.58.0"')


def _align4(value: int) -> int:
    return (value + 3) & ~3


def _note(descriptor: bytes, *, namesz: int = 4) -> bytes:
    data = struct.pack("<III", namesz, len(descriptor), 1) + b"PTO\0"
    data += b"\0" * (_align4(namesz) - 4)
    data += descriptor + b"\0" * (_align4(len(descriptor)) - len(descriptor))
    return data


def _section_table(data: bytearray) -> tuple[int, int, int, bool]:
    if data[:4] != b"\x7fELF" or data[5] != 1:
        raise ValueError("fixture must be a little-endian ELF")
    if data[4] == 2:
        return struct.unpack_from("<Q", data, 40)[0], struct.unpack_from("<H", data, 58)[0], struct.unpack_from("<H", data, 60)[0], True
    if data[4] == 1:
        return struct.unpack_from("<I", data, 32)[0], struct.unpack_from("<H", data, 46)[0], struct.unpack_from("<H", data, 48)[0], False
    raise ValueError("unsupported ELF class")


def make_fixture(source: Path, destination: Path, kind: str) -> None:
    data = bytearray(source.read_bytes())
    shoff, shentsize, shnum, is64 = _section_table(data)
    note_header = None
    for index in range(shnum):
        header = shoff + index * shentsize
        if struct.unpack_from("<I", data, header + 4)[0] == 7:
            note_header = header
            break
    if note_header is None:
        raise ValueError("source ELF has no SHT_NOTE identity section")
    if is64:
        offset = struct.unpack_from("<Q", data, note_header + 24)[0]
        size_field, size_fmt = note_header + 32, "<Q"
    else:
        offset = struct.unpack_from("<I", data, note_header + 16)[0]
        size_field, size_fmt = note_header + 20, "<I"

    if kind == "missing":
        struct.pack_into("<I", data, note_header + 4, 1)
    else:
        payloads = {
            "canonical": _note(IDENTITY),
            "duplicate-identical": _note(IDENTITY) + _note(IDENTITY),
            "old": _note(OLD_IDENTITY),
            "malformed": _note(IDENTITY, namesz=3),
            "trailing-nul": _note(IDENTITY + b"\0"),
            "duplicate-conflicting": _note(IDENTITY) + _note(OLD_IDENTITY),
            "mixed": _note(OLD_IDENTITY) + _note(IDENTITY),
        }
        if kind not in payloads:
            raise ValueError(f"unknown fixture kind: {kind}")
        payload = payloads[kind]
        if offset + len(payload) > shoff:
            raise ValueError("ELF has insufficient non-loadable space for duplicate note fixture")
        data[offset : offset + len(payload)] = payload
        struct.pack_into(size_fmt, data, size_field, len(payload))
    destination.write_bytes(data)


def _run(qemu: Path, elf: Path) -> subprocess.CompletedProcess[bytes]:
    env = dict(os.environ)
    env["LINX_VIRT_TEST_FINISHER"] = "1"
    return subprocess.run(
        [str(qemu), "-machine", "virt", "-bios", "none", "-kernel", str(elf),
         "-nographic", "-monitor", "none"],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qemu", required=True, type=Path)
    parser.add_argument("--elf", required=True, type=Path)
    args = parser.parse_args()
    accepted = {"canonical", "duplicate-identical"}
    rejected = {"missing", "old", "malformed", "trailing-nul", "duplicate-conflicting", "mixed"}
    with tempfile.TemporaryDirectory(prefix="linx-elf-identity-") as tmp:
        tmpdir = Path(tmp)
        for kind in sorted(accepted | rejected):
            fixture = tmpdir / f"{kind}.elf"
            make_fixture(args.elf, fixture, kind)
            completed = _run(args.qemu, fixture)
            if kind in accepted:
                if completed.returncode != 0 or not completed.stdout:
                    print(f"error: accepted fixture {kind} did not enter the guest")
                    return 1
            elif completed.returncode == 0 or completed.stdout:
                print(f"error: rejected fixture {kind} reached guest execution")
                return 1
    print("ok: canonical and duplicate-identical identities accepted; all six negative identities rejected before guest entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
