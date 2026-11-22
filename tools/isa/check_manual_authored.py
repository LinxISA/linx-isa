#!/usr/bin/env python3
"""Verify embedded human-authored Chinese articles against the reviewed tag."""

from __future__ import annotations

import argparse
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from manual_authored import authored_for, authored_tile
from manual_markdown import render_article
from manual_tag import tagged_bytes, tagged_json

START = "<!-- authored:start -->"
END = "<!-- authored:end -->"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def spelling(row: dict[str, Any]) -> str:
    suffix = {"Private": "PRIVATE", "IntraCore": "INTRA", "InterCore": "INTER"}
    return row["mnemonic"] + (
        "." + suffix[row["pto_scope"]] if row.get("pto_scope") else ""
    )


def op_page(row: dict[str, Any]) -> str:
    return f"op-{slug(spelling(row))}.html"


def tile_page(name: str) -> str:
    return f"tile-{slug(name)}.html"


def extract_authored(page: str) -> tuple[str, str]:
    if page.count(START) != 1 or page.count(END) != 1:
        raise ValueError("expected exactly one authored:start/end pair")
    match = re.search(
        r'<section class="authored-reader" data-source-path="([^"]+)">.*?'
        + re.escape(START)
        + r"(.*?)"
        + re.escape(END)
        + r"</section>",
        page,
        flags=re.DOTALL,
    )
    if match is None:
        raise ValueError("authored markers do not wrap one authored-reader section")
    return match.group(1), match.group(2)


def _normalize_local_targets(html: str) -> str:
    def replace(match: re.Match[str]) -> str:
        name, value = match.group(1), match.group(2)
        if re.match(r"^(?:https?|mailto):", value):
            return match.group(0)
        return f' {name}="__OFFLINE_TARGET__"'

    return re.sub(r' (href|src)="([^"]*)"', replace, html)


class _ArticleFacts(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[str] = []
        self.code: list[str] = []
        self.images: list[dict[str, str]] = []
        self.admonitions: list[tuple[str, str]] = []
        self._capture: str | None = None
        self._buffer: list[str] = []
        self._admonition_class = ""

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag in {"h2", "h3", "h4", "h5", "h6", "code"}:
            self._capture = tag
            self._buffer = []
        if tag == "img":
            self.images.append(values)
        if tag == "div" and "admonition" in values.get("class", "").split():
            self._admonition_class = values.get("class", "")
            self._capture = "admonition"
            self._buffer = []

    def handle_endtag(self, tag):
        if self._capture == tag:
            text = "".join(self._buffer).strip()
            if tag.startswith("h"):
                self.headings.append(text.replace("¶", "").strip())
            elif tag == "code":
                self.code.append(text)
            self._capture = None
            self._buffer = []
        elif self._capture == "admonition" and tag == "div":
            self.admonitions.append(
                (self._admonition_class, "".join(self._buffer).strip())
            )
            self._capture = None
            self._buffer = []
            self._admonition_class = ""

    def handle_data(self, data):
        if self._capture:
            self._buffer.append(data)


def _load_audit(site: Path) -> dict[str, dict[str, Any]]:
    path = site / "authored-audit.json"
    if not path.is_file():
        raise ValueError("missing authored-audit.json")
    value = json.loads(path.read_text(encoding="utf-8"))
    if "pages" in value:
        value = value["pages"]
    if not isinstance(value, dict):
        raise ValueError("authored audit must be a filename mapping")
    return value


def _expected_pages(catalog: dict[str, Any], tiles: dict[str, Any]) -> dict[str, Any]:
    base_by_mnemonic: dict[str, list[dict[str, Any]]] = {}
    for row in catalog["instructions"]:
        if not row.get("pto_scope"):
            base_by_mnemonic.setdefault(row["mnemonic"], []).append(row)
    expected = {}
    for row in catalog["instructions"]:
        base = row
        if row.get("pto_scope"):
            candidates = base_by_mnemonic.get(row["mnemonic"], [])
            base = next(
                (
                    candidate
                    for candidate in candidates
                    if candidate.get("pto_source_form_id")
                    == row.get("pto_base_form_id")
                ),
                candidates[0] if candidates else row,
            )
        article = authored_for(base)
        if article:
            expected.setdefault(op_page(row), article)
    for op in tiles["operations"]:
        article = authored_tile(op["name"])
        if article:
            expected.setdefault(tile_page(op["name"]), article)
    return expected


def check_site(site: Path) -> list[str]:
    errors: list[str] = []
    catalog = tagged_json("isa/v0.59/linxisa-v0.59.json")
    tiles = tagged_json("isa/v0.59/state/pto_tile_operations.json")
    expected = _expected_pages(catalog, tiles)
    try:
        audit = _load_audit(site)
    except ValueError as exc:
        return [str(exc)]
    routes: dict[str, str] = {}
    for filename in sorted(audit):
        record = audit[filename]
        source = str(record.get("source_path", ""))
        if source:
            routes.setdefault(source, filename)
    if set(audit) != set(expected):
        missing = sorted(set(expected) - set(audit))
        extra = sorted(set(audit) - set(expected))
        if missing:
            errors.append(f"authored audit missing {len(missing)} pages: {missing[:8]}")
        if extra:
            errors.append(
                f"authored audit has {len(extra)} unexpected pages: {extra[:8]}"
            )
    for filename, article in expected.items():
        where = filename
        record = audit.get(filename)
        if not isinstance(record, dict):
            continue
        page_path = site / filename
        if not page_path.is_file():
            errors.append(f"{where}: missing page")
            continue
        source_bytes = tagged_bytes(article.source_path)
        if record.get("source_path") != article.source_path:
            errors.append(f"{where}: source path differs")
        if record.get("source_sha256") != sha256(source_bytes).hexdigest():
            errors.append(f"{where}: source SHA-256 differs")
        source_asset = site / str(record.get("source_asset", ""))
        if not source_asset.is_file() or source_asset.read_bytes() != source_bytes:
            errors.append(f"{where}: offline authored source asset differs from tag")
        if record.get("classification") != article.classification:
            errors.append(f"{where}: classification differs")
        try:
            embedded_path, embedded = extract_authored(
                page_path.read_text(encoding="utf-8")
            )
        except ValueError as exc:
            errors.append(f"{where}: {exc}")
            continue
        if embedded_path != article.source_path:
            errors.append(f"{where}: data-source-path differs")
        if (
            record.get("rendered_sha256")
            != sha256(embedded.encode("utf-8")).hexdigest()
        ):
            errors.append(f"{where}: rendered SHA-256 differs")
        rendered = render_article(
            article.source_path,
            current_page=filename,
            document_routes=routes,
        ).html
        if _normalize_local_targets(embedded) != _normalize_local_targets(rendered):
            errors.append(f"{where}: embedded article differs from tag re-render")
    # Deep regression for the complete first authored instruction article.
    filename = "op-c-movr.html"
    if filename in expected and (site / filename).is_file():
        try:
            page_text = (site / filename).read_text(encoding="utf-8")
            _, fragment = extract_authored(page_text)
            first_screen = page_text[: page_text.index(START)]
            if (
                'class="intro"' in first_screen
                or "semantic-description" in first_screen
            ):
                errors.append(
                    f"{filename}: generated synopsis appears before original article"
                )
            facts = _ArticleFacts()
            facts.feed(fragment)
            wanted_headings = [
                "说明",
                "汇编语法",
                "汇编符号",
                "编码格式",
                "执行方式",
                "汇编索引模式",
                "备注",
            ]
            if facts.headings[: len(wanted_headings)] != wanted_headings:
                errors.append(f"{filename}: original heading order incomplete")
            example_blocks = [
                [
                    line
                    for line in block.splitlines()
                    if line.strip().startswith("c.movr ")
                ]
                for block in facts.code
            ]
            examples = sum(len(lines) for lines in example_blocks if len(lines) > 1)
            if examples != 9:
                errors.append(
                    f"{filename}: expected 9 c.movr examples, found {examples}"
                )
            if not any(
                image.get("alt") == "c.movr" and image.get("src", "").endswith(".svg")
                for image in facts.images
            ):
                errors.append(f"{filename}: original c.movr SVG is missing")
            if not any(
                "info" in classes.split() and "注意" in text
                for classes, text in facts.admonitions
            ):
                errors.append(f"{filename}: accessible 注意 admonition is missing")
        except ValueError as exc:
            errors.append(f"{filename}: {exc}")
    # MGATHER is a Tile operation, distinct from the BSTART.MGATHER command.
    # Validate the original data-flow explanation, parameter table and source
    # program in addition to the generic byte-level article comparison.
    name = "tile-mgather.html"
    if name in expected and (site / name).is_file():
        page = (site / name).read_text(encoding="utf-8")
        source_html = page.split(START, 1)[-1].split(END, 1)[0]
        from html import unescape

        plain = unescape(re.sub(r"<[^>]+>", "", source_html))
        for literal in (
            "基于间接寻址",
            "执行模型",
            "offset_t offset = src[i][j];",
            "dst[i][j] = Memory[base + offset];",
            "dst[i][j] = PadValue;",
        ):
            if literal not in plain:
                errors.append(f"{name}: missing original MGATHER content {literal!r}")
        if "<table" not in source_html or not (
            0 <= page.find(START) < page.find('class="release-data"')
        ):
            errors.append(
                f"{name}: authored table and original reader must precede release details"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True)
    args = parser.parse_args(argv)
    errors = check_site(args.site.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"authored article validation failed: {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print("OK: embedded authored Chinese articles match the reviewed tag")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
