#!/usr/bin/env python3
"""Independently validate the reader-visible LinxISA v0.59.2 HTML manual.

The expected form inventory is read from the signed v0.59.2 tag.  This checker
does not import the HTML generator.  It reuses the older reference checker's
DOM and encoding validators only after removing the 193 obsolete forms from a
copy of the signed catalog.
"""

from __future__ import annotations

import argparse
import copy
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from check_html_reference import Audit, op_page, parse, spelling, tile_page


ROOT = Path(__file__).resolve().parents[2]
RELEASE_TAG = "v0.59.2"
REVIEWED_TAG_OBJECT = "230c730b73ff4d22441411b52640458428279fd2"
REVIEWED_COMMIT = "830fbdb53bccec889414b5673ffba31b0a08606d"
CATALOG_PATH = "isa/v0.59.2/linxisa-v0.59.2.json"
TILES_PATH = "isa/v0.59/state/pto_tile_operations.json"
SYSTEM_REGISTERS_PATH = "isa/v0.59/state/pto_system_registers.json"
READABLE_SUFFIXES = {".html", ".md", ".txt", ".adoc"}
STATUS_STATES = {"retained", "reserved-unimplemented"}
OBSOLETE_BLOCK_ALIASES = {"MSEQ", "MPAR", "VSEQ", "VPAR"}
LEGACY_EXAMPLE_MNEMONICS = {"B.EQ"}
RETIRED_PAGES = {
    "arch-core-state.html",
    "arch-execution-mode.html",
    "arch-predicate.html",
    "arch-ssr-lcfr-en.html",
    "arch-ssr-lcfr.html",
    "arch-vgpr.html",
}
RETIRED_ASSET_SUFFIXES = {
    "docs--zh--figs--intro--group.png",
    "docs--zh--figs--isa--arch--pred.png",
    "docs--zh--figs--bitfield--svg--Sysregs--LCFR.svg",
    "docs--zh--figs--bitfield--svg--Sysregs--LCFR_EN.svg",
}
LEGACY_MODEL_PATTERNS = {
    "old Group/Lane execution model": re.compile(
        r"执行组\s*[（(]Group[）)]|执行通道\s*[（(]Lane[）)]|GroupNumber|LaneNumber",
        re.IGNORECASE,
    ),
    "old vector register queues": re.compile(
        r"4\s*种向量寄存器队列|VT\s*[、,]\s*VU\s*[、,]\s*VM\s*[、,]\s*VN|V[TMUN]R[1-4]",
        re.IGNORECASE,
    ),
    "old lane predicate register": re.compile(
        r"Predicate\s+Mask|每一位掩码与\s*Lane\s*一一对应|每个\s*Group\s*最多包含\s*64\s*个\s*lane",
        re.IGNORECASE,
    ),
    "retired LCFR state": re.compile(r"\bLCFR(?:_EN)?\b"),
    "historical Janus core state": re.compile(r"Janus\s+Core"),
}


def _git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def release_inputs() -> tuple[dict, dict]:
    """Return the catalog and Tile inventory from the exact signed release."""
    tag_object_id = _git("rev-parse", f"refs/tags/{RELEASE_TAG}").decode().strip()
    if tag_object_id != REVIEWED_TAG_OBJECT:
        raise ValueError(
            f"{RELEASE_TAG} tag object is {tag_object_id}, expected {REVIEWED_TAG_OBJECT}"
        )
    commit = _git("rev-list", "-n", "1", f"{RELEASE_TAG}^{{commit}}").decode().strip()
    if commit != REVIEWED_COMMIT:
        raise ValueError(
            f"{RELEASE_TAG} resolves to {commit or '<missing>'}, expected {REVIEWED_COMMIT}"
        )
    tag_object = _git("cat-file", "-p", f"refs/tags/{RELEASE_TAG}").decode(
        "utf-8", errors="replace"
    )
    if "-----BEGIN SSH SIGNATURE-----" not in tag_object:
        raise ValueError(f"{RELEASE_TAG} is not an annotated SSH-signed tag")
    catalog = json.loads(_git("show", f"{RELEASE_TAG}:{CATALOG_PATH}"))
    tiles = json.loads(_git("show", f"{RELEASE_TAG}:{TILES_PATH}"))
    return catalog, tiles


def inventories(catalog: dict) -> tuple[list[dict], list[dict]]:
    rows = catalog.get("instructions", [])
    obsolete = [
        row
        for row in rows
        if row.get("architecture_status", {}).get("state") == "obsolete"
    ]
    active = [row for row in rows if row not in obsolete]
    if len(rows) != 1499 or len(obsolete) != 193 or len(active) != 1306:
        raise ValueError(
            f"wrong signed inventory: all={len(rows)}, obsolete={len(obsolete)}, active={len(active)}"
        )
    if sum(row["mnemonic"].startswith("V.") for row in obsolete) != 184:
        raise ValueError(
            "signed catalog does not contain exactly 184 obsolete V.* forms"
        )
    return active, obsolete


def _active_catalog(catalog: dict, active: list[dict]) -> dict:
    result = copy.deepcopy(catalog)
    result["instructions"] = copy.deepcopy(active)
    result["instruction_count"] = len(active)
    return result


def _load_json(path: Path, errors: list[str]) -> dict:
    if not path.is_file():
        errors.append(f"{path.name}: missing")
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: invalid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.name}: expected a JSON object")
        return {}
    return value


def _exact_token_pattern(names: set[str]) -> re.Pattern[str]:
    ordered = sorted(names, key=lambda value: (-len(value), value))
    return re.compile(
        r"(?<![A-Za-z0-9_.])(?:"
        + "|".join(re.escape(name) for name in ordered)
        + r")(?![A-Za-z0-9_.])",
        flags=re.IGNORECASE,
    )


def _plain_html(value: str) -> str:
    value = re.sub(r"<(?:script|style)\b[^>]*>[\s\S]*?</(?:script|style)>", " ", value)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def _check_no_obsolete_reader_material(
    site: Path, obsolete: list[dict], errors: list[str]
) -> None:
    names = (
        {spelling(row) for row in obsolete}
        | OBSOLETE_BLOCK_ALIASES
        | LEGACY_EXAMPLE_MNEMONICS
    )
    pattern = _exact_token_pattern(names)
    obsolete_pages = {op_page(row) for row in obsolete}
    for name in sorted(obsolete_pages):
        if (site / name).exists():
            errors.append(f"{name}: obsolete instruction page remains in the package")

    for path in sorted(site.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(site).as_posix()
        path_label = unquote(relative)
        if path.suffix:
            path_label = path_label[: -len(path.suffix)]
        name_match = pattern.search(path_label)
        if name_match:
            errors.append(
                f"{relative}: packaged filename names obsolete mnemonic {name_match.group()!r}"
            )
        if path.suffix.lower() == ".svg":
            try:
                root = ET.fromstring(path.read_bytes())
            except ET.ParseError:
                # Some reviewed WaveDrom assets contain concatenated SVG roots.
                # The structure checker validates the exact bytes.  Here only
                # extract reader-visible labels and deliberately ignore paths,
                # numeric coordinates and embedded generation metadata.
                raw_svg = path.read_text(encoding="utf-8", errors="replace")
                visible = " ".join(
                    _plain_html(match.group(1))
                    for match in re.finditer(
                        r"<(?:title|desc|text)\b[^>]*>([\s\S]*?)</(?:title|desc|text)>",
                        raw_svg,
                        flags=re.IGNORECASE,
                    )
                )
            else:
                visible = " ".join(
                    "".join(node.itertext())
                    for node in root.iter()
                    if node.tag.rsplit("}", 1)[-1] in {"title", "desc", "text"}
                )
            match = pattern.search(visible)
            if match:
                errors.append(
                    f"{relative}: SVG label still describes obsolete mnemonic {match.group()!r}"
                )
            continue
        if path.suffix.lower() not in READABLE_SUFFIXES:
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix.lower() == ".html" and "LinxISA 0.59.2" not in raw:
            errors.append(f"{relative}: page does not identify the v0.59.2 manual")
        text = _plain_html(raw) if path.suffix.lower() == ".html" else raw
        match = pattern.search(text)
        if match:
            errors.append(
                f"{relative}: reader material still describes obsolete mnemonic {match.group()!r}"
            )
        if path.suffix.lower() != ".html":
            continue
        doc = parse(path)
        for anchor in doc.find(tag="a"):
            href = anchor.attrs.get("href", "")
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            decoded = unquote(parsed.path)
            target = posixpath.normpath(
                posixpath.join(posixpath.dirname(relative), decoded)
            )
            if target in obsolete_pages:
                errors.append(
                    f"{relative}: links to obsolete instruction page {href!r}"
                )


def _legacy_model_hits(text: str) -> list[str]:
    return [
        label
        for label, pattern in LEGACY_MODEL_PATTERNS.items()
        if pattern.search(text)
    ]


def _check_retired_execution_model(site: Path, errors: list[str]) -> None:
    for filename in sorted(RETIRED_PAGES):
        if (site / filename).exists():
            errors.append(
                f"{filename}: retired execution-model page remains in package"
            )
    for path in sorted(site.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(site).as_posix()
        if any(relative.endswith(suffix) for suffix in RETIRED_ASSET_SUFFIXES):
            errors.append(
                f"{relative}: retired execution-model figure remains in package"
            )
        if path.suffix.lower() not in READABLE_SUFFIXES:
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        text = _plain_html(raw) if path.suffix.lower() == ".html" else raw
        for label in _legacy_model_hits(text):
            errors.append(f"{relative}: contains {label}")


def _check_current_system_state(site: Path, errors: list[str]) -> None:
    path = site / "arch-ssr.html"
    if not path.is_file():
        errors.append("arch-ssr.html: missing current system-register table")
        return
    source = json.loads(_git("show", f"{RELEASE_TAG}:{SYSTEM_REGISTERS_PATH}"))
    wanted = {
        f"{row['scope']}:{row['name']}:{row.get('address', row.get('low_index'))}"
        for row in source["registers"]
    }
    doc = parse(path)
    actual = {
        node.attrs["data-register-key"]
        for node in doc.find()
        if "data-register-key" in node.attrs
    }
    if len(actual) != 100 or actual != wanted:
        errors.append(
            f"arch-ssr.html: current register rows differ ({len(actual)} != 100)"
        )
    if not any(key.split(":")[1] == "CORE_STATE" for key in actual):
        errors.append("arch-ssr.html: current CORE_STATE definition is missing")
    for filename in ("tile-mgather-mask.html", "tile-mscatter-mask.html"):
        target = site / filename
        if not target.is_file() or "掩码" not in _plain_html(
            target.read_text(encoding="utf-8", errors="replace")
        ):
            errors.append(f"{filename}: current predicated Tile operation is missing")


def _check_status_pages(site: Path, active: list[dict], errors: list[str]) -> None:
    grouped: dict[str, list[dict]] = {}
    for row in active:
        state = row.get("architecture_status", {}).get("state")
        if state in STATUS_STATES:
            grouped.setdefault(op_page(row), []).append(row)
    expected_counts = {"retained": 19, "reserved-unimplemented": 4}
    actual_counts = {
        state: sum(
            row.get("architecture_status", {}).get("state") == state for row in active
        )
        for state in expected_counts
    }
    if actual_counts != expected_counts:
        errors.append(
            f"signed active extension status counts differ: {actual_counts!r}"
        )
    for filename, rows in grouped.items():
        path = site / filename
        if not path.is_file():
            errors.append(f"{filename}: missing status-bearing instruction page")
            continue
        doc = parse(path)
        nodes = doc.find(tag="section", cls="architecture-status")
        wanted_states = {row["architecture_status"]["state"] for row in rows}
        actual_states = {node.attrs.get("data-state") for node in nodes}
        if not wanted_states <= actual_states:
            errors.append(
                f"{filename}: architecture status sections {actual_states!r} omit {wanted_states!r}"
            )
        if "reserved-unimplemented" in wanted_states:
            text = " ".join(node.text() for node in nodes)
            for phrase in ("仅预留编码", "读取操作数", "架构效果", "拒绝"):
                if phrase not in text:
                    errors.append(
                        f"{filename}: reserved-unimplemented notice omits {phrase!r}"
                    )


def _detail_record_has_removed_form(
    filename: str,
    record: dict,
    *,
    tile_pages: set[str],
    active_ids: set[str],
    obsolete_ids: set[str],
) -> bool:
    """Tile audit rows name an operation; instruction rows name form IDs."""
    if filename in tile_pages:
        return False
    ids = set(record.get("forms", []))
    return bool(ids & obsolete_ids or not ids <= active_ids)


def _check_audits_and_assets(
    site: Path,
    catalog: dict,
    active: list[dict],
    obsolete: list[dict],
    errors: list[str],
) -> None:
    active_ids = {row["id"] for row in active}
    obsolete_ids = {row["id"] for row in obsolete}
    active_pages = {op_page(row) for row in active}
    audit = _load_json(site / "audit.json", errors)
    if audit.get("tag") != RELEASE_TAG or audit.get("commit") != REVIEWED_COMMIT:
        errors.append("audit.json: wrong v0.59.2 release identity")
    records = audit.get("forms", [])
    audit_ids = {row.get("id") for row in records if isinstance(row, dict)}
    if audit_ids != active_ids or len(records) != len(active_ids):
        errors.append(
            f"audit.json: form inventory differs: {len(audit_ids)} IDs, expected {len(active_ids)}"
        )
    source_rows = {row["id"]: row for row in active}
    for record in records:
        if not isinstance(record, dict) or record.get("id") not in source_rows:
            continue
        row = source_rows[record["id"]]
        wanted = row.get("architecture_status")
        if record.get("architecture_status") != wanted:
            errors.append(
                f"audit.json/{row['id']}: architecture_status differs from signed catalog"
            )

    detail = _load_json(site / "detail-audit.json", errors)
    tile_pages = {
        tile_page(operation["name"])
        for operation in json.loads(_git("show", f"{RELEASE_TAG}:{TILES_PATH}"))[
            "operations"
        ]
    }
    expected_detail_pages = active_pages | tile_pages
    if set(detail) != expected_detail_pages:
        errors.append(
            f"detail-audit.json: page inventory {len(detail)} != {len(expected_detail_pages)}"
        )
    for filename, record in detail.items():
        if not isinstance(record, dict):
            errors.append(f"detail-audit.json/{filename}: malformed record")
            continue
        if _detail_record_has_removed_form(
            filename,
            record,
            tile_pages=tile_pages,
            active_ids=active_ids,
            obsolete_ids=obsolete_ids,
        ):
            errors.append(f"detail-audit.json/{filename}: contains removed form IDs")

    for filename in ("authored-audit.json", "editorial-audit.json"):
        document = _load_json(site / filename, errors)
        pages = document.get("pages", document)
        if not isinstance(pages, dict):
            errors.append(f"{filename}: malformed page inventory")
            continue
        leftovers = sorted(set(pages) & {op_page(row) for row in obsolete})
        if leftovers:
            errors.append(
                f"{filename}: contains {len(leftovers)} obsolete instruction pages"
            )

    diagrams = _load_json(site / "diagram-audit.json", errors)
    diagram_rows = diagrams.get("forms", {})
    if (
        diagrams.get("release_tag") != RELEASE_TAG
        or diagrams.get("source_commit") != REVIEWED_COMMIT
    ):
        errors.append("diagram-audit.json: wrong v0.59.2 release identity")
    signed_catalog = _git("show", f"{RELEASE_TAG}:{CATALOG_PATH}")
    if diagrams.get("catalog_sha256") != sha256(signed_catalog).hexdigest():
        errors.append("diagram-audit.json: wrong signed catalog digest")
    if set(diagram_rows) != active_ids:
        errors.append(
            f"diagram-audit.json: form inventory {len(diagram_rows)} != {len(active_ids)}"
        )
    wanted_assets = set()
    for identity, record in diagram_rows.items():
        for part in record.get("parts", []):
            asset = part.get("asset")
            if not asset:
                errors.append(f"diagram-audit.json/{identity}: missing diagram asset")
                continue
            wanted_assets.add(asset)
            target = site / asset
            if not target.is_file():
                errors.append(f"diagram-audit.json/{identity}: missing {asset}")
            elif sha256(target.read_bytes()).hexdigest() != part.get("svg_sha256"):
                errors.append(
                    f"diagram-audit.json/{identity}: SVG digest differs for {asset}"
                )
    actual_assets = {
        path.relative_to(site).as_posix() for path in (site / "diagrams").glob("*.svg")
    }
    if actual_assets != wanted_assets:
        errors.append(
            f"diagrams/: asset inventory {len(actual_assets)} != {len(wanted_assets)}"
        )
    if diagrams.get("form_count") != len(active_ids) or diagrams.get(
        "asset_count"
    ) != len(wanted_assets):
        errors.append("diagram-audit.json: summary counts differ from active assets")

    spec_dir = site / "spec"
    projections = []
    if spec_dir.is_dir():
        for path in spec_dir.glob("*.json"):
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict) and isinstance(value.get("instructions"), list):
                projections.append((path, value))
    if len(projections) != 1:
        errors.append(
            f"spec/: expected one current instruction projection, found {len(projections)}"
        )
    else:
        path, projection = projections[0]
        ids = {row.get("id") for row in projection["instructions"]}
        if (
            projection.get("version") != "0.59.2"
            or projection.get("source_commit") != REVIEWED_COMMIT
            or projection.get("source_catalog_sha256")
            != sha256(signed_catalog).hexdigest()
            or projection.get("instruction_count") != len(active_ids)
            or ids != active_ids
        ):
            errors.append(
                f"{path.relative_to(site)}: current projection does not contain exactly 1,306 active forms"
            )


def check_site(site: Path) -> list[str]:
    errors: list[str] = []
    try:
        catalog, tiles = release_inputs()
        active, obsolete = inventories(catalog)
    except (
        OSError,
        subprocess.CalledProcessError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        return [f"release authority unavailable: {exc}"]

    shared = Audit(site, _active_catalog(catalog, active), tiles).run()
    errors.extend(f"shared-reference/{error}" for error in shared)
    _check_no_obsolete_reader_material(site, obsolete, errors)
    _check_retired_execution_model(site, errors)
    _check_current_system_state(site, errors)
    _check_status_pages(site, active, errors)
    _check_audits_and_assets(site, catalog, active, obsolete, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True, type=Path)
    args = parser.parse_args(argv)
    errors = check_site(args.site.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"v0.59.2 HTML validation failed: {len(errors)} error(s)", file=sys.stderr
        )
        return 1
    print("OK: 1,306 active forms, 193 obsolete forms removed, 119 Tile operations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
