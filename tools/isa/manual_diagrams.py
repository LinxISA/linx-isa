#!/usr/bin/env python3
"""Deterministic, tag-bound SVG diagrams for every LinxISA 0.59.1 form."""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
import hashlib
from html import escape
import json
from pathlib import PurePosixPath
import re
import subprocess
from typing import Any
import xml.etree.ElementTree as ET

from gen_encoding_svg import _build_parts, _svg_for_parts
from manual_tag import (
    REVIEWED_COMMIT,
    RELEASE_TAG,
    REPO_ROOT,
    tagged_bytes,
    tagged_json,
)


CATALOG_PATH = "isa/v0.59/linxisa-v0.59.json"
LEGACY_JSON_ROOT = "docs/figs/bitfield/json"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _base_field(token: str) -> str:
    return re.sub(r"\[[^]]+\]$", "", token)


def _catalog_segments(
    row: dict[str, Any], part_index: int
) -> list[tuple[str, str | int]]:
    bits = []
    part = row["parts"][part_index]
    for segment in sorted(part["segments"], key=lambda item: int(item["lsb"])):
        width = int(segment["width"])
        if "const" in segment:
            value = int(segment["const"]["value"])
            bits.extend(("constant", (value >> index) & 1) for index in range(width))
        else:
            bits.extend(
                ("field", _base_field(str(segment["token"]))) for _ in range(width)
            )
    return bits


def _json_instruction(items: object, mnemonic: str) -> list[dict[str, Any]] | None:
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        return None
    headers = [
        (index, str(item.get("####", "")))
        for index, item in enumerate(items)
        if "####" in item
    ]
    if headers:
        starts = [index for index, name in headers if name == mnemonic]
        if len(starts) != 1:
            return None
        start = starts[0] + 1
    else:
        start = 0
    result = []
    for item in items[start:]:
        if "####" in item or (item.get("name") == "" and result):
            break
        if "bits" not in item or "name" not in item:
            continue
        result.append(item)
    return result or None


def _legacy_segments(data: bytes, mnemonic: str) -> list[tuple[str, str | int]] | None:
    try:
        items = _json_instruction(json.loads(data.decode("utf-8")), mnemonic)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if items is None:
        return None
    bits = []
    for item in items:
        width = item.get("bits")
        name = item.get("name")
        if not isinstance(width, int) or width <= 0:
            return None
        if isinstance(name, int):
            if name < 0 or name >= 1 << width:
                return None
            bits.extend(("constant", (name >> index) & 1) for index in range(width))
        elif isinstance(name, str) and name:
            bits.extend(("field", name) for _ in range(width))
        else:
            return None
    return bits


def _legacy_padding(data: bytes, mnemonic: str) -> int:
    try:
        decoded = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return 0
    if not isinstance(decoded, list):
        return 0
    headers = [
        i
        for i, item in enumerate(decoded)
        if isinstance(item, dict) and item.get("####") == mnemonic
    ]
    start = headers[0] + 1 if len(headers) == 1 else 0
    seen = False
    for item in decoded[start:]:
        if not isinstance(item, dict):
            continue
        if "####" in item:
            return 0
        if item.get("name") == "" and seen:
            bits = item.get("bits")
            return int(bits) if isinstance(bits, int) and bits >= 0 else 0
        if "bits" in item and "name" in item:
            seen = True
    return 0


def _svg_matches_json(svg: bytes, data: bytes, mnemonic: str) -> bool:
    """Verify WaveDrom text boundaries, labels and fixed bits against JSON."""
    try:
        root = ET.fromstring(svg)
        decoded = json.loads(data.decode("utf-8"))
    except (ET.ParseError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    items = _json_instruction(decoded, mnemonic)
    if items is None:
        return False
    padding = _legacy_padding(data, mnemonic)
    text = [value.strip() for value in root.itertext() if value.strip()]
    numeric = [value for value in text if re.fullmatch(r"\d+", value)]
    boundaries = []
    cursor = 0
    for item in items:
        width = int(item["bits"])
        boundaries.extend((cursor, cursor + width - 1))
        cursor += width
    if padding:
        boundaries.extend((cursor, cursor + padding - 1))
    expected_boundaries = [str(value) for value in sorted(set(boundaries))]
    observed_boundaries = []
    for value in numeric:
        if observed_boundaries and int(value) <= int(observed_boundaries[-1]):
            break
        observed_boundaries.append(value)
    if observed_boundaries != expected_boundaries:
        return False
    expected_labels = {
        str(item.get("attr") or item["name"])
        for item in items
        if isinstance(item.get("attr") or item.get("name"), str)
        and str(item.get("attr") or item.get("name"))
    }
    if not expected_labels.issubset(set(text)):
        return False
    expected_fixed_bits = [
        str((int(item["name"]) >> index) & 1)
        for item in items
        if isinstance(item["name"], int)
        for index in range(int(item["bits"]))
    ]
    remaining_numeric = numeric[len(observed_boundaries) :]
    observed_fixed_bits = [value for value in remaining_numeric if value in {"0", "1"}]
    return observed_fixed_bits == expected_fixed_bits


@lru_cache(maxsize=1)
def _legacy_json_paths() -> dict[str, list[str]]:
    output = subprocess.check_output(
        [
            "git",
            "ls-tree",
            "-r",
            "--name-only",
            REVIEWED_COMMIT,
            "--",
            LEGACY_JSON_ROOT,
        ],
        cwd=REPO_ROOT,
        text=True,
    )
    paths: dict[str, list[str]] = defaultdict(list)
    for path in output.splitlines():
        if path.endswith(".json"):
            paths[PurePosixPath(path).stem].append(path)
    return dict(paths)


def _legacy_asset(row: dict[str, Any]) -> dict[str, Any] | None:
    if len(row.get("parts", [])) != 1:
        return None
    mnemonic = str(row["mnemonic"])
    wanted = _catalog_segments(row, 0)
    matches = []
    for json_path in _legacy_json_paths().get(mnemonic, []):
        json_bytes = tagged_bytes(json_path)
        if _legacy_segments(json_bytes, mnemonic) != wanted:
            continue
        suffix = json_path.removeprefix(f"{LEGACY_JSON_ROOT}/")
        svg_path = "docs/zh/figs/bitfield/svg/" + suffix.removesuffix(".json") + ".svg"
        try:
            svg = tagged_bytes(svg_path)
        except subprocess.CalledProcessError:
            continue
        if b"<svg" not in svg:
            continue
        try:
            ET.fromstring(svg)
        except ET.ParseError:
            # A few archived WaveDrom files carry literal characters after
            # </svg>. Preserve exact originals only when they are valid SVG.
            continue
        if not _svg_matches_json(svg, json_bytes, mnemonic):
            continue
        matches.append((json_path, json_bytes, svg_path, svg))
    if not matches:
        return None
    # Several historical folders may contain byte-identical mirrors. Reuse
    # only when the exact rendered SVG is unambiguous.
    if len({_sha(match[3]) for match in matches}) != 1:
        return None
    json_path, json_bytes, svg_path, svg = sorted(matches, key=lambda item: item[0])[0]
    return {
        "source": "tagged-original-wavedrom-svg",
        "json_path": json_path,
        "json_sha256": _sha(json_bytes),
        "svg_path": svg_path,
        "svg_sha256": _sha(svg),
        "padded_blank_bits": _legacy_padding(json_bytes, mnemonic),
        "svg": svg,
    }


def _tagged_catalog_rows() -> dict[str, dict[str, Any]]:
    return {str(row["id"]): row for row in tagged_json(CATALOG_PATH)["instructions"]}


def _validate_row(row: dict[str, Any], tagged: dict[str, Any]) -> None:
    for key in ("id", "mnemonic", "asm", "length_bits", "parts", "encoding"):
        if row.get(key) != tagged.get(key):
            raise ValueError(
                f"{row.get('id')}: {key} differs from reviewed release tag"
            )


def _generated_part(row: dict[str, Any], part_index: int) -> bytes:
    parts = _build_parts(row)
    part = parts[part_index]
    title = f"{row['mnemonic']} · Part {part_index}"
    svg = _svg_for_parts(title, [part], part.width_bits)
    # The shared generator's English note is presentation-only. Localize the
    # note without changing geometry, fields, constants or bit positions.
    svg = svg.replace(
        f">{part.width_bits}-bit encoding</text>",
        f">{part.width_bits} 位编码</text>",
    )
    return svg.encode("utf-8")


def make_diagrams(
    catalog: dict[str, Any],
    *,
    selected_rows=None,
    release_tag=RELEASE_TAG,
    source_commit=REVIEWED_COMMIT,
    catalog_path=CATALOG_PATH,
    catalog_sha256=None,
) -> tuple[dict[str, str], dict[str, bytes], dict[str, Any]]:
    """Return per-form HTML, offline SVG assets, and a tag-bound audit."""
    tagged_rows = _tagged_catalog_rows()
    rows = list(catalog.get("instructions", []))
    if {str(row.get("id")) for row in rows} != set(tagged_rows):
        raise ValueError("catalog form inventory differs from reviewed release tag")
    html: dict[str, str] = {}
    assets: dict[str, bytes] = {}
    form_audit: dict[str, Any] = {}
    source_counts: Counter[str] = Counter()
    if selected_rows is not None:
        rows = selected_rows
    catalog_sha256 = catalog_sha256 or _sha(tagged_bytes(CATALOG_PATH))
    for row in rows:
        form_id = str(row["id"])
        _validate_row(row, tagged_rows[form_id])
        figures = []
        part_audit = []
        original = _legacy_asset(row)
        for part_index, part in enumerate(row["parts"]):
            relative = f"diagrams/{form_id}-part{part_index}.svg"
            if part_index == 0 and original is not None:
                data = original["svg"]
                record = {key: value for key, value in original.items() if key != "svg"}
            else:
                data = _generated_part(row, part_index)
                record = {
                    "source": "tagged-catalog-svg-generator",
                    "generator_path": "tools/isa/gen_encoding_svg.py",
                    "generator_sha256": _sha(
                        tagged_bytes("tools/isa/gen_encoding_svg.py")
                    ),
                    "catalog_path": catalog_path,
                    "catalog_sha256": catalog_sha256,
                    "svg_sha256": _sha(data),
                }
            if relative in assets:
                raise ValueError(f"diagram asset collision: {relative}")
            assets[relative] = data
            source_counts[str(record["source"])] += 1
            record.update(
                {
                    "part": part_index,
                    "width_bits": int(part["width_bits"]),
                    "asset": relative,
                }
            )
            part_audit.append(record)
            figures.append(
                '<figure class="encoding-diagram" '
                f'data-part="{part_index}" data-source="{escape(str(record["source"]), quote=True)}">'
                f'<img src="{escape(relative, quote=True)}" '
                f'alt="{escape(str(row["mnemonic"]))} 第 {part_index} 段编码位图">'
                f"<figcaption>第 {part_index} 段（Part {part_index}），{int(part['width_bits'])} 位。"
                f"来源：LinxISA {release_tag} 固定快照。"
                + (
                    f"原图上半部留白，指令实际为 {int(part['width_bits'])} 位。"
                    if int(record.get("padded_blank_bits", 0))
                    else ""
                )
                + "</figcaption></figure>"
            )
        html[form_id] = (
            f'<div class="encoding-diagrams" data-form-id="{escape(form_id, quote=True)}">'
            + "".join(figures)
            + "</div>"
        )
        form_audit[form_id] = {
            "mnemonic": row["mnemonic"],
            "asm": row["asm"],
            "parts": part_audit,
        }
    audit = {
        "schema": "linxisa.manual.encoding-diagrams.v1",
        "release_tag": release_tag,
        "source_commit": source_commit,
        "catalog_path": catalog_path,
        "catalog_sha256": catalog_sha256,
        "form_count": len(form_audit),
        "asset_count": len(assets),
        "source_counts": dict(sorted(source_counts.items())),
        "forms": form_audit,
    }
    return html, assets, audit


__all__ = ["make_diagrams"]
