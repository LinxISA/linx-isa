#!/usr/bin/env python3
"""Reject historical prose and stale artifacts from the v0.59.2 golden manual.

This is intentionally independent of the HTML generator.  It first runs the
signed-release inventory/encoding validator, then inspects the finished files
that a reader can open or download.  Exact PTO source identity is allowed on
the source page.  Historical explanations, comparison copy and old generated
assets are not.
"""

from __future__ import annotations

import argparse
from html import unescape
import json
from pathlib import Path
import posixpath
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from check_html_reference import parse
from check_manual_detail_semantics import (
    _check_bstart_examples,
    _check_ccat,
    _check_modifier_tables,
    _check_scalar_fp,
    _check_scalar_results,
    _check_scopes,
    _check_tile_accumulators,
)
from check_v0592_html import check_site as check_v0592_site


READABLE_SUFFIXES = {".html", ".md", ".txt", ".adoc"}
ASSET_ROOTS = {"article-source", "support", "support-assets", "figures", "diagrams"}
FORBIDDEN_FILES = {
    "reader-quality-review.md",
    "arm64-reference-organization.md",
}
FORBIDDEN_PAGE_CLASSES = {
    "historical-article",
    "edition-difference",
    "supplement-reader",
}
FORBIDDEN_ARCH_STATUS = {
    "historical-conflict",
    "historical-register-note",
    "implementation-only",
    "contextual-original",
}
FORBIDDEN_PROSE = {
    "历史说明": re.compile(r"历史(?:说明|中文|原文|实现|页面|资料|版本|模型|语境)"),
    "旧版或旧模型": re.compile(
        r"旧(?:版|中文|模型|路径|式|页面|原文|约束|行为|编码|拼写|名称|说明|实现|教程)"
    ),
    "早期实现": re.compile(r"早期(?:版本|实现|页面|模型|设计|\s*Janus)"),
    "原页对照": re.compile(
        r"(?:查看|保留|沿用|下方)原(?:文|页|图)|中文站原(?:文|页|稿)|原作者"
    ),
    "版本对照": re.compile(
        r"版本差异|对照(?:中文站|原页|旧版)|兼容旧机器字|兼容执行路径"
    ),
    "增补标记": re.compile(r"(?:0\.59\.1\s*)?增补|supplement", re.IGNORECASE),
    "obsolete 说明": re.compile(r"\bobsolete\b|已移除|废弃指令", re.IGNORECASE),
    "历史英文": re.compile(
        r"\b(?:historical|legacy)\s+(?:article|page|model|version|encoding|behavior|behaviour|instruction)s?\b",
        re.IGNORECASE,
    ),
    "旧规范版本": re.compile(r"(?<![0-9.])v?0\.(?:5[0-8])(?:\.\d+)*(?![0-9.])"),
    "旧规范路径": re.compile(r"(?:^|[/\"'])isa/v0\.58(?:[/\"'#]|$)"),
    "归档或未发布说明": re.compile(r"归档\s*v|当前未发布|尚未发布的\s*v"),
    "旧资料导航": re.compile(r"系统寄存器原文|中文站各寄存器说明|实现模型补充"),
    "非规范实现材料": re.compile(r"实现背景材料|不得据此增加\s*ISA\s*承诺"),
}
SOURCE_FACTS = (
    re.compile(r"\bv0\.59\.1\.0\b"),
    re.compile(r"\b0\.59\.1\b"),
    re.compile(r"pto-isa-0\.59\.1-mode-function-v1"),
)


def _plain_html(value: str) -> str:
    value = re.sub(r"<(?:script|style)\b[^>]*>[\s\S]*?</(?:script|style)>", " ", value)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", unescape(value)).strip()


def _svg_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        parts = re.findall(
            r"<(?:title|desc|text)\b[^>]*>([\s\S]*?)</(?:title|desc|text)>",
            raw,
            flags=re.IGNORECASE,
        )
        return " ".join(_plain_html(part) for part in parts)
    return " ".join(
        "".join(node.itertext())
        for node in root.iter()
        if node.tag.rsplit("}", 1)[-1] in {"title", "desc", "text"}
    )


def _reader_text(path: Path) -> str:
    if path.suffix.lower() == ".html":
        return _plain_html(path.read_text(encoding="utf-8", errors="replace"))
    if path.suffix.lower() == ".svg":
        return _svg_text(path)
    return path.read_text(encoding="utf-8", errors="replace")


def history_hits(relative: str, text: str) -> list[str]:
    """Return reader-facing historical markers, with one narrow provenance exception."""
    checked = text
    if relative == "sources.html":
        for pattern in SOURCE_FACTS:
            checked = pattern.sub("CURRENT_UPSTREAM_IDENTITY", checked)
    hits = [
        label for label, pattern in FORBIDDEN_PROSE.items() if pattern.search(checked)
    ]
    if relative != "sources.html" and re.search(
        r"(?<![0-9.])v?0\.59\.1(?:\.0)?(?![0-9.])", checked
    ):
        hits.append("旧手册版本")
    return hits


def _json_strings(value: object, path: str = ""):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _json_strings(item, f"{path}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _json_strings(item, f"{path}/{index}")
    elif isinstance(value, str):
        yield path, value


def _check_reader_material(site: Path, errors: list[str]) -> None:
    for path in sorted(site.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(site).as_posix()
        if relative in FORBIDDEN_FILES:
            errors.append(
                f"{relative}: review or supplement artifact is not golden manual content"
            )
        if path.suffix.lower() in READABLE_SUFFIXES | {".svg"}:
            for label in history_hits(relative, _reader_text(path)):
                errors.append(f"{relative}: contains {label}")
        if path.suffix.lower() != ".html":
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        for css_class in FORBIDDEN_PAGE_CLASSES:
            if re.search(rf'class="[^"]*\b{re.escape(css_class)}\b', raw):
                errors.append(
                    f"{relative}: contains forbidden reader section {css_class!r}"
                )
        if re.search(r'class="[^"]*\bversion-context\b', raw):
            contexts = re.findall(
                r'<[^>]+class="[^"]*\bversion-context\b[^"]*"[^>]*>([\s\S]*?)</[^>]+>',
                raw,
            )
            for context in contexts:
                if history_hits(relative, _plain_html(context)):
                    errors.append(f"{relative}: version context is a migration note")
                    break
        if "/isa/v0.58/" in raw or "blob/v0.58/" in raw:
            errors.append(f"{relative}: links to a superseded v0.58 source")


def _check_audit_prose(site: Path, errors: list[str]) -> None:
    architecture_path = site / "architecture-audit.json"
    if not architecture_path.is_file():
        errors.append("architecture-audit.json: missing")
        return
    architecture = json.loads(architecture_path.read_text(encoding="utf-8"))
    for page, record in architecture.items():
        status = str(record.get("status", ""))
        source = str(record.get("source_path", ""))
        if status in FORBIDDEN_ARCH_STATUS or status.startswith("historical"):
            errors.append(
                f"architecture-audit.json/{page}: non-current status {status!r}"
            )
        if status == "implementation-only" or "/isa/model/" in source:
            errors.append(
                f"architecture-audit.json/{page}: implementation tutorial is not golden ISA text"
            )
        if "/isa/register/ssr/" in source and status != "current-system-register":
            errors.append(
                f"architecture-audit.json/{page}: old SSR article is still authoritative"
            )

    for path in sorted(site.glob("*.json")):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for location, value in _json_strings(document):
            if path.name == "architecture-audit.json" and location.endswith("/status"):
                continue
            # Version, ABI and commit strings are machine provenance.  Prose is not.
            if value in {
                "0.59.1",
                "v0.59.1",
                "v0.59.1.0",
                "pto-isa-0.59.1-mode-function-v1",
            } or re.fullmatch(r"[0-9a-f]{40,64}", value):
                continue
            if location.endswith(("/source_path", "/chinese_source")):
                # This is exact source provenance.  The reader-facing label and
                # manuscript still go through the no-history prose scan.
                continue
            for label in history_hits(path.name, value):
                errors.append(f"{path.name}{location}: contains {label}")


def _check_ssr(site: Path, errors: list[str]) -> None:
    page = site / "arch-ssr.html"
    if not page.is_file():
        errors.append("arch-ssr.html: missing")
        return
    raw = page.read_text(encoding="utf-8")
    if re.search(r"旧中文|历史说明|旧中文页", raw):
        errors.append("arch-ssr.html: still offers historical register descriptions")
    if re.search(r'href="arch-ssr-[^"]+\.html', raw):
        errors.append("arch-ssr.html: still links to old per-register pages")
    for path in site.glob("arch-ssr-*.html"):
        audit = json.loads((site / "architecture-audit.json").read_text())
        record = audit.get(path.name, {})
        if path.name == "arch-ssr-overview.html":
            if record.get("origin") != "v0.59.2-machine-projection":
                errors.append(
                    "arch-ssr-overview.html: overview is not a current machine projection"
                )
            continue
        if record.get("status") != "current-system-register":
            errors.append(
                f"{path.name}: per-register page is not generated from the current catalog"
            )


def _check_instruction_semantics(site: Path, errors: list[str]) -> None:
    for check in (
        _check_modifier_tables,
        _check_scalar_results,
        _check_ccat,
        _check_scalar_fp,
        _check_bstart_examples,
        _check_tile_accumulators,
        _check_scopes,
    ):
        try:
            check(site, errors)
        except (FileNotFoundError, ValueError) as exc:
            errors.append(f"{check.__name__}: {exc}")


def _check_b_ior_contract(site: Path, errors: list[str]) -> None:
    path = site / "op-b-ior.html"
    if not path.is_file():
        errors.append("op-b-ior.html: missing")
        return
    text = _plain_html(path.read_text(encoding="utf-8"))
    required = {
        "reserved selectors": ("24", "31", "Fault_IllegalInstruction"),
        "indexed bounds": ("RegSrc1", "RegSrc2", "MinIndex", "MaxIndex", "S64"),
        "descriptor absence": ("RegSrc1", "RegSrc2", "范围描述符"),
        "descriptor plus mask": ("第二条", "ExecMaskPresent"),
    }
    for label, literals in required.items():
        missing = [literal for literal in literals if literal not in text]
        if missing:
            errors.append(f"op-b-ior.html: {label} omits {missing!r}")
    if not (
        re.search(r"24\s*(?:至|\.\.)\s*31", text)
        and "Fault_IllegalInstruction" in text
        and re.search(r"(?:读取|绑定|效果).{0,100}(?:前|之前)", text)
    ):
        errors.append(
            "op-b-ior.html: reserved selectors are not rejected before binding effects"
        )
    if not re.search(
        r"RegSrc1\s*[,，、]\s*RegSrc2.{0,100}(?:zero|0).{0,50}(?:zero|0).{0,100}(?:不声明|不提供|省略|没有).{0,30}范围描述符",
        text,
        flags=re.IGNORECASE,
    ):
        errors.append("op-b-ior.html: zero selector pair does not omit the descriptor")
    if not re.search(
        r"第二条.{0,180}ExecMaskPresent|ExecMaskPresent.{0,180}(?:最后|最终)",
        text,
    ):
        errors.append("op-b-ior.html: final execution-mask record is unclear")
    stale = {
        "stores reserved selectors": r"记录仍会保存这些编码",
        "defers selector rejection": r"只有在操作特定检查.{0,100}(?:故障|拒绝)",
        "forbids every indexed descriptor": r"带索引.{0,100}RegSrc1[、,， ]+RegSrc2.{0,50}(?:全为|必须为)零",
    }
    for label, pattern in stale.items():
        if re.search(pattern, text):
            errors.append(f"op-b-ior.html: {label}")


def _local_targets(site: Path) -> set[str]:
    targets: set[str] = set()
    for page in site.rglob("*.html"):
        relative = page.relative_to(site).as_posix()
        doc = parse(page)
        for node in doc.find():
            raw = node.attrs.get("href") or node.attrs.get("src")
            if not raw:
                continue
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc:
                continue
            target = posixpath.normpath(
                posixpath.join(posixpath.dirname(relative), unquote(parsed.path))
            )
            if target and not target.startswith("../"):
                targets.add(target)
    for path in site.glob("*.json"):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for _, value in _json_strings(document):
            if any(
                value == root or value.startswith(root + "/") for root in ASSET_ROOTS
            ):
                targets.add(value)
    return targets


def _check_orphans(site: Path, errors: list[str]) -> None:
    targets = _local_targets(site)
    for root in ASSET_ROOTS:
        folder = site / root
        if not folder.is_dir():
            continue
        for path in folder.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(site).as_posix()
            if relative not in targets:
                errors.append(f"{relative}: orphaned packaged artifact")


def check_site(site: Path) -> list[str]:
    site = site.resolve()
    errors = [f"v0.59.2/{error}" for error in check_v0592_site(site)]
    _check_reader_material(site, errors)
    _check_audit_prose(site, errors)
    _check_ssr(site, errors)
    _check_instruction_semantics(site, errors)
    _check_b_ior_contract(site, errors)
    _check_orphans(site, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True, type=Path)
    args = parser.parse_args(argv)
    errors = check_site(args.site)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"golden HTML validation failed: {len(errors)} error(s)")
        return 1
    print("OK: golden v0.59.2 manual contains only current architecture definitions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
