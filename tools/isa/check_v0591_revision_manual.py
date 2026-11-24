#!/usr/bin/env python3
"""Independently verify the working and ZIP LinxISA 0.59.1 revision manual."""

from __future__ import annotations

import argparse
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from check_html_reference import Audit, op_page, parse


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "isa/v0.59/linxisa-v0.59.json"
TILES = ROOT / "isa/v0.59/state/pto_tile_operations.json"
SSRS = ROOT / "isa/v0.59/state/pto_system_registers.json"
LINX_FORMS = ROOT / "isa/v0.59/state/linx_extension_forms.json"
RESERVATIONS = ROOT / "isa/v0.59/state/extension_encoding_reservations.json"
MANIFEST = ROOT / "isa/v0.59/release_manifest.json"
LOCK = ROOT / "isa/v0.59/pto-spec.lock.json"
SIGNED_TAG = "v0.59.1"
SIGNED_COMMIT = "d262515b55c727073997c8f4c95261909f2fe8d3"
SIGNED_CATALOG_SHA256 = (
    "490defb827d2aecd5c63fe231467d2a3416e5ce0361b65a65f507d9fab08079c"
)
REMOVED_BLOCK_FORMS = {
    "B.TEXT",
    "BSTART.MPAR",
    "BSTART.MSEQ",
    "BSTART.VPAR",
    "BSTART.VSEQ",
    "C.BSTART.MPAR",
    "C.BSTART.MSEQ",
    "C.BSTART.VPAR",
    "C.BSTART.VSEQ",
}
ENCODING_ONLY_FORMS = {"DMA.FREE.L", "DMA.FREE.S", "MCOPY.DL", "MCOPY.DS"}
SPEC_FILES = {
    "linxisa-v0.59.json": CATALOG,
    "pto_tile_operations.json": TILES,
    "pto_system_registers.json": SSRS,
    "linx_extension_forms.json": LINX_FORMS,
    "extension_encoding_reservations.json": RESERVATIONS,
    "release_manifest.json": MANIFEST,
    "pto-spec.lock.json": LOCK,
}
RESERVATION_SCAN_EXCEPTIONS = {"spec/extension_encoding_reservations.json"}
LEGACY_MODEL_PATTERNS = {
    "VGPR state": re.compile(r"\bVGPR\b|通用向量寄存器", re.IGNORECASE),
    "retired LCFR state": re.compile(r"\bLCFR(?:_EN)?\b"),
    "old Group/Lane model": re.compile(
        r"GroupNumber|LaneNumber|执行组\s*[（(]Group|执行通道\s*[（(]Lane",
        re.IGNORECASE,
    ),
    "old vector queues": re.compile(
        r"4\s*种向量寄存器队列|VT\s*[、,]\s*VU\s*[、,]\s*VM\s*[、,]\s*VN|V[TMUN]R[1-4]",
        re.IGNORECASE,
    ),
    "old lane predicate": re.compile(
        r"Predicate\s+Mask|每一位掩码与\s*Lane\s*一一对应|每个\s*Group\s*最多包含\s*64\s*个\s*lane",
        re.IGNORECASE,
    ),
    "historical Janus state": re.compile(r"Janus\s+Core", re.IGNORECASE),
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git_bytes(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def plain_html(raw: str) -> str:
    raw = re.sub(r"<(?:script|style)\b[^>]*>[\s\S]*?</(?:script|style)>", " ", raw)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def svg_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        chunks = re.findall(
            r"<(?:title|desc|text)\b[^>]*>([\s\S]*?)</(?:title|desc|text)>",
            raw,
            flags=re.IGNORECASE,
        )
        return " ".join(plain_html(chunk) for chunk in chunks)
    return " ".join(
        "".join(node.itertext())
        for node in root.iter()
        if node.tag.rsplit("}", 1)[-1] in {"title", "desc", "text"}
    )


def signed_baseline() -> tuple[dict, set[str], set[str]]:
    commit = (
        git_bytes("rev-list", "-n", "1", f"{SIGNED_TAG}^{{commit}}").decode().strip()
    )
    if commit != SIGNED_COMMIT:
        raise ValueError(f"{SIGNED_TAG} resolves to {commit}, expected {SIGNED_COMMIT}")
    tag = git_bytes("cat-file", "-p", f"refs/tags/{SIGNED_TAG}")
    if b"-----BEGIN SSH SIGNATURE-----" not in tag:
        raise ValueError(f"{SIGNED_TAG} is not an annotated SSH-signed tag")
    raw = git_bytes("show", f"{SIGNED_TAG}:isa/v0.59/linxisa-v0.59.json")
    if sha256(raw).hexdigest() != SIGNED_CATALOG_SHA256:
        raise ValueError("signed v0.59.1 catalog hash differs")
    catalog = json.loads(raw)
    active_ids = {row["id"] for row in load(CATALOG)["instructions"]}
    removed = [row for row in catalog["instructions"] if row["id"] not in active_ids]
    names = {row["mnemonic"] for row in removed}
    if len(removed) != 193 or sum(name.startswith("V.") for name in names) != 184:
        raise ValueError(
            "signed/current catalog difference is not the 193-form hard break"
        )
    if names - {name for name in names if name.startswith("V.")} != REMOVED_BLOCK_FORMS:
        raise ValueError("signed/current catalog difference has unexpected block forms")
    return catalog, {row["id"] for row in removed}, names


def exact_name_pattern(names: set[str]) -> re.Pattern[str]:
    terms = sorted(names, key=lambda value: (-len(value), value))
    return re.compile(
        r"(?<![A-Za-z0-9_.])(?:"
        + "|".join(re.escape(x) for x in terms)
        + r")(?![A-Za-z0-9_.])",
        re.IGNORECASE,
    )


def reader_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".html":
        return plain_html(path.read_text(encoding="utf-8", errors="replace"))
    if suffix == ".svg":
        return svg_text(path)
    raw = path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".md":
        raw = re.sub(r"\]\([^)]*\)", "]", raw)
        raw = re.sub(r"https?://\S+", " ", raw)
    return raw


def json_reader_strings(value: object, key: str = ""):
    if isinstance(value, dict):
        for child_key, child in value.items():
            if child_key == "extension_encoding_reservations":
                continue
            yield from json_reader_strings(child, str(child_key))
    elif isinstance(value, list):
        for child in value:
            yield from json_reader_strings(child, key)
    elif isinstance(value, str):
        if key in {"source_path", "chinese_source", "reader_path", "file", "path"}:
            return
        if value.startswith(("http://", "https://")):
            return
        yield value


def check_identity_and_inventory(site: Path, errors: list[str]) -> tuple[dict, dict]:
    catalog, removed_ids, removed_names = signed_baseline()
    working = load(CATALOG)
    current_ids = {row["id"] for row in working["instructions"]}
    if working.get("version") != "0.59.1" or working.get("instruction_count") != 1306:
        errors.append("catalog: working edition is not version 0.59.1 with 1306 forms")
    status = working.get("release_status", {})
    if status.get("publication_revision") != 1:
        errors.append("catalog: publication revision is not 1")
    if status.get("signed_baseline", {}).get("commit") != SIGNED_COMMIT:
        errors.append("catalog: signed baseline commit differs")
    if current_ids & removed_ids:
        errors.append("catalog: removed forms remain assigned")

    linx = load(LINX_FORMS)
    forms = linx.get("forms", [])
    reserved = {
        row["mnemonic"] for row in forms if "NOT IMPLEMENTED" in row.get("note", "")
    }
    if len(forms) != 23 or reserved != ENCODING_ONLY_FORMS:
        errors.append(
            "linx_extension_forms: expected 19 retained plus 4 encoding-only forms"
        )
    reservations = {
        row["mnemonic"] for row in load(RESERVATIONS).get("reservations", [])
    }
    if not ({"V.*", *REMOVED_BLOCK_FORMS} <= reservations):
        errors.append("reservations: ten removed encoding ranges are incomplete")

    for name, source in SPEC_FILES.items():
        packaged = site / "spec" / name
        if not packaged.is_file():
            errors.append(f"spec/{name}: missing")
        elif packaged.read_bytes() != source.read_bytes():
            errors.append(f"spec/{name}: differs from working specification input")
    tiles = load(TILES)
    ssrs = load(SSRS)
    if len(tiles.get("operations", [])) != 119:
        errors.append("pto_tile_operations: expected 119 operations")
    if len(ssrs.get("registers", [])) != 100:
        errors.append("pto_system_registers: expected 100 registers")

    sources = site / "sources.html"
    if sources.is_file():
        text = plain_html(sources.read_text(encoding="utf-8"))
        for literal in ("v0.59.1", SIGNED_COMMIT, digest(CATALOG)):
            if literal not in text:
                errors.append(f"sources.html: missing edition identity {literal!r}")
    else:
        errors.append("sources.html: missing")
    audit = load(site / "audit.json") if (site / "audit.json").is_file() else {}
    head = git_bytes("rev-parse", "HEAD").decode().strip()
    if audit.get("tag") != SIGNED_TAG or audit.get("commit") != head:
        errors.append("audit.json: tag or working revision commit differs")
    return working, tiles


def check_removed_and_legacy_material(
    site: Path, removed_names: set[str], errors: list[str]
) -> None:
    obsolete = exact_name_pattern(removed_names)
    for path in sorted(site.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
            ".html",
            ".md",
            ".svg",
            ".json",
        }:
            continue
        relative = path.relative_to(site).as_posix()
        if relative in RESERVATION_SCAN_EXCEPTIONS:
            continue
        if path.suffix.lower() == ".json":
            try:
                values = list(
                    json_reader_strings(json.loads(path.read_text(encoding="utf-8")))
                )
            except json.JSONDecodeError as exc:
                errors.append(f"{relative}: invalid JSON: {exc}")
                continue
            texts = values
        else:
            texts = [reader_text(path)]
        for text in texts:
            match = obsolete.search(text)
            if match:
                errors.append(
                    f"{relative}: reader material names removed form {match.group()!r}"
                )
                break
            hits = [
                label
                for label, pattern in LEGACY_MODEL_PATTERNS.items()
                if pattern.search(text)
            ]
            if hits:
                errors.append(f"{relative}: contains {', '.join(hits)}")
                break
        if path.suffix.lower() == ".html" and path.name.startswith("op-v-"):
            errors.append(f"{relative}: removed V.* detail page remains")

    audit_path = site / "architecture-audit.json"
    architecture = load(audit_path) if audit_path.is_file() else {}
    for page, record in architecture.items():
        if page.startswith("arch-ssr-") and str(record.get("status", "")).startswith(
            "historical"
        ):
            errors.append(
                f"architecture-audit.json/{page}: historical SSR page remains packaged"
            )
    for path in sorted(site.glob("arch-ssr-*.html")):
        errors.append(f"{path.name}: historical per-register SSR entry remains")


def require_literals(
    site: Path, page: str, literals: tuple[str, ...], errors: list[str]
) -> None:
    path = site / page
    if not path.is_file():
        errors.append(f"{page}: missing representative page")
        return
    text = reader_text(path)
    for literal in literals:
        if literal not in text:
            errors.append(f"{page}: missing representative contract {literal!r}")


def check_representative_semantics(site: Path, errors: list[str]) -> None:
    require_literals(
        site,
        "op-b-ior.html",
        (
            "选择器编码 24 至 31 保留",
            "读取或改变绑定状态之前",
            "MinIndex",
            "MaxIndex",
            "ExecMaskPresent",
            "两条",
        ),
        errors,
    )
    require_literals(
        site,
        "op-hl-ccat.html",
        ("128 位", "逻辑右移", "低 64 位", "高 64 位", "0 至 127"),
        errors,
    )
    require_literals(
        site,
        "op-hl-bstart-call.html",
        ("本指令承载字的起始地址", "P + 4", "返回地址写入 ra"),
        errors,
    )
    require_literals(
        site,
        "op-l-bstart-fp.html",
        ("FALL", "不会改写 ra", "SETRET"),
        errors,
    )
    require_literals(
        site,
        "tile-mgather.html",
        ("BaseGPR + ByteDisplacement", "字节位移", "MinIndex", "MaxIndex"),
        errors,
    )
    for page in (
        "op-dma-free-l.html",
        "op-dma-free-s.html",
        "op-mcopy-dl.html",
        "op-mcopy-ds.html",
    ):
        require_literals(
            site, page, ("编码保留", "读取操作数", "架构效果之前拒绝"), errors
        )


def check_ssr_projection(site: Path, errors: list[str]) -> None:
    page = site / "arch-ssr.html"
    if not page.is_file():
        errors.append("arch-ssr.html: missing")
        return
    doc = parse(page)
    details = doc.find(tag="section", cls="system-register-detail")
    keys = {node.attrs.get("data-register-detail-key") for node in details}
    if len(details) != 100 or len(keys) != 100:
        errors.append(
            f"arch-ssr.html: expected 100 current register details, found {len(details)}"
        )
    raw = page.read_text(encoding="utf-8")
    if re.search(r'href="arch-ssr-[^"]+\.html', raw):
        errors.append("arch-ssr.html: links to historical per-register pages")


def check_site(site: Path) -> list[str]:
    errors: list[str] = []
    try:
        _baseline, _removed_ids, removed_names = signed_baseline()
        catalog, tiles = check_identity_and_inventory(site, errors)
    except (KeyError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        return [f"release inputs: {exc}"]
    errors.extend(Audit(site, catalog, tiles).run())
    check_removed_and_legacy_material(site, removed_names, errors)
    check_ssr_projection(site, errors)
    check_representative_semantics(site, errors)
    return errors


def zip_members(bundle: Path) -> dict[str, bytes]:
    members: dict[str, bytes] = {}
    with zipfile.ZipFile(bundle) as archive:
        for info in archive.infolist():
            name = posixpath.normpath(unquote(info.filename).replace("\\", "/"))
            if info.is_dir():
                continue
            if name in {"..", "."} or name.startswith("../") or name.startswith("/"):
                raise ValueError(f"unsafe ZIP member {info.filename!r}")
            if name in members:
                raise ValueError(f"duplicate ZIP member {name!r}")
            members[name] = archive.read(info)
    return members


def compare_site_and_zip(site: Path, bundle: Path, errors: list[str]) -> None:
    try:
        members = zip_members(bundle)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        errors.append(f"ZIP: {exc}")
        return
    files = {
        path.relative_to(site).as_posix(): path.read_bytes()
        for path in site.rglob("*")
        if path.is_file()
    }
    if set(files) != set(members):
        errors.append(f"ZIP: inventory differs (site={len(files)}, zip={len(members)})")
    changed = sorted(
        name for name in set(files) & set(members) if files[name] != members[name]
    )
    if changed:
        errors.append(f"ZIP: {len(changed)} files differ, first={changed[0]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--zip", dest="bundle", type=Path, required=True)
    args = parser.parse_args(argv)
    site = args.site.resolve()
    errors = check_site(site)
    compare_site_and_zip(site, args.bundle.resolve(), errors)
    try:
        members = zip_members(args.bundle.resolve())
        with tempfile.TemporaryDirectory(prefix="linx-v0591-manual-zip-") as directory:
            extracted = Path(directory)
            for name, content in members.items():
                target = extracted / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            errors.extend(f"ZIP/{error}" for error in check_site(extracted))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        errors.append(f"ZIP extraction: {exc}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"v0.59.1 revision manual validation failed: {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print("OK: working HTML and ZIP match the 0.59.1 revision specification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
