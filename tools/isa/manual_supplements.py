#!/usr/bin/env python3
"""Map and validate the 22 reviewed LinxISA 0.59.1 Chinese supplements."""

from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping

try:
    from manual_tag import REPO_ROOT, tagged_json
except ModuleNotFoundError:
    from tools.isa.manual_tag import REPO_ROOT, tagged_json

ROOT = REPO_ROOT / "docs/zh/architecture/isa-manual/supplements"
PTO_COMMIT = "a89a53d48f5708328be609fe2e6296ac8bdb4bc2"
MARKER = re.compile(r"^<!-- LINXISA-SUPPLEMENT: (\{.*\}) -->$")
REQUIRED_HEADINGS = (
    "用途",
    "输入与输出",
    "执行结果",
    "示例",
    "合法性与异常",
    "0.59.1 来源",
)
INSTRUCTION_PATHS = {
    "B.ASSEMBLE": "b-assemble.md",
    "B.FPATR": "b-fpatr.md",
    "B.SUBVIEW": "b-subview.md",
    "BSTART.TIMG2COL": "bstart-timg2col.md",
    "FENCE.D": "fence-d.md",
    "FENCE.I": "fence-i.md",
    "SYNC.CORE": "sync-core.md",
}
TILE_PATHS = {
    "TFMA": "tfma.md",
    "TROWARGMAX": "trowargmax.md",
    "TROWARGMIN": "trowargmin.md",
    "TCOLARGMAX": "tcolargmax.md",
    "TCOLARGMIN": "tcolargmin.md",
    "TCI": "tci.md",
    "TTRI": "ttri.md",
    "GMOV": "gmov.md",
    "TPERMUTE": "tpermute.md",
    "TSHUF": "tshuf.md",
    "TPACK": "tpack.md",
    "TUNPACK": "tunpack.md",
    "TGPR2T": "tgpr2t.md",
    "TEXPDIF": "texpdif.md",
    "TLEA": "tlea.md",
}


@lru_cache(maxsize=1)
def _instruction_rows() -> dict[str, dict[str, Any]]:
    wanted = set(INSTRUCTION_PATHS)
    rows = {
        row["mnemonic"]: row
        for row in tagged_json("isa/v0.59/linxisa-v0.59.json")["instructions"]
        if not row.get("pto_scope") and row["mnemonic"] in wanted
    }
    if set(rows) != wanted:
        raise ValueError(
            "supplement instruction set differs from the published catalog"
        )
    return rows


@lru_cache(maxsize=1)
def _tile_rows() -> dict[str, dict[str, Any]]:
    wanted = set(TILE_PATHS)
    rows = {
        row["name"]: row
        for row in tagged_json("isa/v0.59/state/pto_tile_operations.json")["operations"]
        if row["name"] in wanted
    }
    if set(rows) != wanted:
        raise ValueError("supplement Tile set differs from the published catalog")
    return rows


def _tile_identity(row: Mapping[str, Any]) -> str:
    return (
        f"tile:{row['engine']}:{row.get('mode', '-')}:{row['function']}:{row['name']}"
    )


def supplement_mapping() -> dict[str, str]:
    mapping = {
        row["id"]: str(ROOT / INSTRUCTION_PATHS[name])
        for name, row in _instruction_rows().items()
    }
    mapping.update(
        {
            _tile_identity(row): str(ROOT / TILE_PATHS[name])
            for name, row in _tile_rows().items()
        }
    )
    if len(mapping) != 22:
        raise ValueError(f"supplement identity count {len(mapping)} != 22")
    return dict(sorted(mapping.items()))


def instruction_supplement(row: Mapping[str, Any]) -> str | None:
    filename = INSTRUCTION_PATHS.get(str(row.get("mnemonic")))
    return str(ROOT / filename) if filename else None


def tile_supplement(operation: str | Mapping[str, Any]) -> str | None:
    name = operation if isinstance(operation, str) else str(operation.get("name"))
    filename = TILE_PATHS.get(name)
    return str(ROOT / filename) if filename else None


def _metadata(path: Path) -> dict[str, Any]:
    first = path.read_text(encoding="utf-8").splitlines()[0]
    match = MARKER.fullmatch(first)
    if not match:
        raise ValueError("missing supplement metadata marker")
    return json.loads(match.group(1))


def _git_bytes(repo: Path, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(repo), "show", f"{PTO_COMMIT}:{path}"]
    )


def validate_supplements(pto_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    reference = json.loads(
        (
            REPO_ROOT
            / "docs/architecture/isa-manual/reference/pto-v0591-semantics.json"
        ).read_text(encoding="utf-8")
    )["forms"]
    tile_manual = {
        row["mnemonic"]: row
        for row in json.loads(
            (
                REPO_ROOT
                / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
            ).read_text(encoding="utf-8")
        )["operations"]
    }
    reader = json.loads(
        (
            REPO_ROOT
            / "docs/architecture/isa-manual/reference/data/manual-reader-zh.json"
        ).read_text(encoding="utf-8")
    )["records"]
    if pto_root is not None:
        pto_root = pto_root.resolve()
        try:
            head = subprocess.check_output(
                ["git", "-C", str(pto_root), "rev-parse", "HEAD"], text=True
            ).strip()
        except (OSError, subprocess.CalledProcessError) as exc:
            return [f"PTO source checkout is unavailable: {exc}"]
        if head != PTO_COMMIT:
            errors.append(f"PTO source HEAD {head} != {PTO_COMMIT}")
    expected_files = set(INSTRUCTION_PATHS.values()) | set(TILE_PATHS.values())
    actual_files = {path.name for path in ROOT.glob("*.md")}
    if actual_files != expected_files:
        errors.append(
            f"supplement file set differs: missing={sorted(expected_files - actual_files)} extra={sorted(actual_files - expected_files)}"
        )
    for name, filename in {**INSTRUCTION_PATHS, **TILE_PATHS}.items():
        path = ROOT / filename
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        try:
            meta = _metadata(path)
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{filename}: {exc}")
            continue
        if (
            meta.get("schema") != "linxisa.manual-supplement.v1"
            or meta.get("version") != "0.59.1"
        ):
            errors.append(f"{filename}: schema/version differs")
        if meta.get("name") != name or meta.get("pto_source_commit") != PTO_COMMIT:
            errors.append(f"{filename}: name or PTO commit differs")
        reader_record = reader.get(str(meta.get("pto_source_path")), {})
        if meta.get("reader_source_path") != reader_record.get("reader_path"):
            errors.append(f"{filename}: pinned Chinese reader path differs")
        if (
            re.fullmatch(r"[0-9a-f]{64}", str(meta.get("reader_source_sha256", "")))
            is None
        ):
            errors.append(f"{filename}: pinned Chinese reader SHA-256 missing")
        if (
            re.fullmatch(r"[0-9a-f]{64}", str(meta.get("pto_source_sha256", "")))
            is None
        ):
            errors.append(f"{filename}: pinned PTO source SHA-256 missing")
        if (
            re.fullmatch(r"[0-9a-f]{64}", str(meta.get("pto_instruction_sha256", "")))
            is None
        ):
            errors.append(f"{filename}: PTO instruction fingerprint missing")
        headings = tuple(re.findall(r"^## (.+)$", text, flags=re.MULTILINE))
        if headings != REQUIRED_HEADINGS:
            errors.append(f"{filename}: heading order differs: {headings}")
        if "> **0.59.1 增补**" not in text or not re.search(r"[\u4e00-\u9fff]", text):
            errors.append(f"{filename}: supplement label or Chinese prose missing")
        if "DOC-BEGIN" in text or "readonly func" in text or "pure func" in text:
            errors.append(f"{filename}: raw ASL prose leaked into supplement")
        if name in INSTRUCTION_PATHS:
            row = _instruction_rows()[name]
            owner = reference.get(str(row.get("pto_source_form_id")), {})
            expected = (row["id"], row["asm"], owner.get("source_path"))
        else:
            row = _tile_rows()[name]
            owner = tile_manual[name]
            expected = (
                _tile_identity(row),
                row["command_mnemonic"],
                owner.get("source_path"),
            )
            selector = row.get("selector") or f"Function={row['function']}"
            if str(selector) not in text:
                errors.append(f"{filename}: current selector missing")
        if (
            meta.get("identity") != expected[0]
            or expected[1] not in text
            or meta.get("pto_source_path") != expected[2]
        ):
            errors.append(f"{filename}: current identity/syntax/source differs")
        if pto_root is not None:
            try:
                reader_bytes = _git_bytes(pto_root, str(meta["reader_source_path"]))
                asl_bytes = _git_bytes(pto_root, str(meta["pto_source_path"]))
                first = asl_bytes.splitlines()[0].decode("utf-8")
                instruction = json.loads(first.split(": ", 1)[1])
                fingerprint = sha256(
                    json.dumps(
                        instruction, sort_keys=True, separators=(",", ":")
                    ).encode("utf-8")
                ).hexdigest()
                records = instruction.get("catalog_records", [])
                source_identity_ok = (
                    any(
                        record.get("form_id") == row.get("pto_source_form_id")
                        for record in records
                    )
                    if name in INSTRUCTION_PATHS
                    else any(record.get("name") == name for record in records)
                )
                if sha256(reader_bytes).hexdigest() != meta["reader_source_sha256"]:
                    errors.append(f"{filename}: Chinese reader source digest differs")
                if sha256(asl_bytes).hexdigest() != meta["pto_source_sha256"]:
                    errors.append(f"{filename}: PTO ASL source digest differs")
                if fingerprint != meta["pto_instruction_sha256"]:
                    errors.append(f"{filename}: PTO instruction fingerprint differs")
                if not source_identity_ok:
                    errors.append(
                        f"{filename}: PTO source does not own the expected form/Tile identity"
                    )
            except (
                KeyError,
                ValueError,
                subprocess.CalledProcessError,
                UnicodeDecodeError,
            ) as exc:
                errors.append(
                    f"{filename}: strict PTO source verification failed: {exc}"
                )
        if not re.search(r"^## 示例\n\n(?=\S)", text, flags=re.MULTILINE):
            errors.append(f"{filename}: reviewed example missing")
    if len(supplement_mapping()) != 22:
        errors.append("supplement mapping is not exactly 22 identities")
    return errors


__all__ = [
    "INSTRUCTION_PATHS",
    "TILE_PATHS",
    "instruction_supplement",
    "supplement_mapping",
    "tile_supplement",
    "validate_supplements",
]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify the 22 release-specific reader supplements"
    )
    parser.add_argument("--pto-root", type=Path, required=True)
    args = parser.parse_args()
    problems = validate_supplements(args.pto_root.resolve())
    if problems:
        raise SystemExit("\n".join(problems))
    print(
        "OK: all 22 supplements refer to the pinned source identities and matching file digests"
    )
