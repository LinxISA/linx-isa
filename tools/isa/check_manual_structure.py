#!/usr/bin/env python3
"""Independently validate diagram assets and instruction-class navigation."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from manual_tag import RELEASE_TAG, verified_tag_commit, tagged_bytes, tagged_json


CATALOG_PATH = "isa/v0.59/linxisa-v0.59.json"
CLASS_FILES = {
    "ALU": "class-alu.html",
    "BBD": "class-bbd.html",
    "BRU": "class-bru.html",
    "AGU": "class-lsu.html",
    "AMO": "class-amo.html",
    "CMD": "class-cmd.html",
    "FSU": "class-fsu.html",
    "SYS": "class-sys.html",
    "VEC": "class-vec.html",
}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node"] = field(default_factory=list)
    content: list[object] = field(default_factory=list)

    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def text(self) -> str:
        return re.sub(r"\s+", " ", self.raw_text()).strip()

    def raw_text(self) -> str:
        return "".join(
            item if isinstance(item, str) else item.raw_text() for item in self.content
        )

    def find(self, tag: str | None = None, cls: str | None = None) -> list["Node"]:
        out = []
        if (tag is None or self.tag == tag) and (cls is None or cls in self.classes()):
            out.append(self)
        for child in self.children:
            out.extend(child.find(tag, cls))
        return out


class Parser(HTMLParser):
    VOID = {"br", "hr", "img", "input", "link", "meta"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        self.stack[-1].content.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        self.stack[-1].content.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].content.append(data)


def parse(path: Path) -> Node:
    parser = Parser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.root


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def spelling(row: dict) -> str:
    suffix = {"Private": "PRIVATE", "IntraCore": "INTRA", "InterCore": "INTER"}
    return row["mnemonic"] + (
        "." + suffix[row["pto_scope"]] if row.get("pto_scope") else ""
    )


def op_page(row: dict) -> str:
    return f"op-{slug(spelling(row))}.html"


def expected_class_inventory(catalog: dict) -> dict[str, set[str]]:
    inventory = {filename: set() for filename in CLASS_FILES.values()}
    for row in catalog["instructions"]:
        kind = str(row.get("uop_big_kind", ""))
        if kind not in CLASS_FILES:
            raise ValueError(f"{row['id']}: unknown uop_big_kind {kind!r}")
        inventory[CLASS_FILES[kind]].add(str(row["mnemonic"]))
    return inventory


def class_page_mnemonics(document: Node) -> tuple[list[str], list[str]]:
    lists = document.find(cls="alphabet-list")
    if not lists:
        lists = [
            node
            for section in document.find(tag="section", cls="alphabet")
            for node in section.find(tag="ul", cls="index-list")
        ]
    if not lists:
        return [], ["expected alphabet lists, found none"]
    names = []
    errors = []
    items = [item for listing in lists for item in listing.find(tag="li")]
    for index, item in enumerate(items):
        labels = item.find(cls="mnemonic")
        links = labels[0].find(tag="a") if labels else []
        if len(labels) != 1 or len(links) != 1:
            errors.append(
                f"list row {index} does not have exactly one first mnemonic link"
            )
            continue
        names.append(links[0].text())
    return names, errors


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Audit:
    def __init__(self, site: Path, catalog: dict) -> None:
        self.site = site
        self.catalog = catalog
        self.errors: list[str] = []
        self.docs: dict[str, Node] = {}

    def fail(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def document(self, name: str) -> Node | None:
        if name in self.docs:
            return self.docs[name]
        path = self.site / name
        if not path.is_file():
            self.fail(name, "missing")
            return None
        try:
            self.docs[name] = parse(path)
        except Exception as error:
            self.fail(name, f"HTML parse failed: {error}")
            return None
        return self.docs[name]

    def diagram_audit(self) -> dict | None:
        path = self.site / "diagram-audit.json"
        if not path.is_file():
            self.fail("diagram-audit.json", "missing")
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception as error:
            self.fail("diagram-audit.json", f"invalid JSON: {error}")
            return None
        if value.get("schema") != "linxisa.manual.encoding-diagrams.v1":
            self.fail("diagram-audit.json", "wrong schema")
        if value.get("release_tag") != RELEASE_TAG:
            self.fail("diagram-audit.json", "wrong release tag")
        if value.get("source_commit") != verified_tag_commit():
            self.fail("diagram-audit.json", "wrong release commit")
        if (
            value.get("catalog_sha256")
            != hashlib.sha256(tagged_bytes(CATALOG_PATH)).hexdigest()
        ):
            self.fail("diagram-audit.json", "wrong catalog digest")
        return value

    def check_diagrams(self) -> None:
        audit = self.diagram_audit()
        if audit is None:
            return
        forms = audit.get("forms", {})
        if set(forms) != {row["id"] for row in self.catalog["instructions"]}:
            self.fail("diagram-audit.json", "form inventory differs from catalog")
        figure_count = 0
        assets_seen: set[str] = set()
        for row in self.catalog["instructions"]:
            form_id = row["id"]
            record = forms.get(form_id)
            if not isinstance(record, dict):
                continue
            if (
                record.get("mnemonic") != row["mnemonic"]
                or record.get("asm") != row["asm"]
            ):
                self.fail(form_id, "diagram audit row identity differs")
            parts = record.get("parts", [])
            if len(parts) != len(row["parts"]):
                self.fail(
                    form_id, f"diagram Part count {len(parts)} != {len(row['parts'])}"
                )
                continue
            doc = self.document(op_page(row))
            if doc is None:
                continue
            articles = [
                node
                for node in doc.find(tag="article")
                if node.attrs.get("id") == form_id
            ]
            if len(articles) != 1:
                self.fail(form_id, f"expected one form article, found {len(articles)}")
                continue
            figures = articles[0].find(tag="figure", cls="encoding-diagram")
            if len(figures) != len(parts):
                self.fail(
                    form_id, f"embedded figure count {len(figures)} != {len(parts)}"
                )
                continue
            figure_count += len(figures)
            for index, (part, figure) in enumerate(zip(parts, figures)):
                where = f"{form_id}/part-{index}"
                asset = str(part.get("asset", ""))
                if (
                    part.get("part") != index
                    or part.get("width_bits") != row["parts"][index]["width_bits"]
                ):
                    self.fail(where, "audit Part metadata differs")
                if figure.attrs.get("data-part") != str(index):
                    self.fail(where, "figure data-part differs")
                if figure.attrs.get("data-source") != part.get("source"):
                    self.fail(where, "figure data-source differs")
                images = figure.find(tag="img")
                if len(images) != 1 or images[0].attrs.get("src") != asset:
                    self.fail(where, "embedded img src differs from audit")
                parsed = urlsplit(asset)
                if parsed.scheme or parsed.netloc or parsed.fragment:
                    self.fail(where, f"asset is not a local path: {asset!r}")
                    continue
                target = self.site / unquote(parsed.path)
                if not target.is_file():
                    self.fail(where, f"missing SVG asset {asset!r}")
                    continue
                if asset in assets_seen:
                    self.fail(
                        where, f"SVG asset is reused by multiple Parts: {asset!r}"
                    )
                assets_seen.add(asset)
                if _sha(target) != part.get("svg_sha256"):
                    self.fail(where, "SVG file hash differs from audit")
                if part.get("source") == "tagged-original-wavedrom-svg":
                    source_path = str(part.get("svg_path", ""))
                    if target.read_bytes() != tagged_bytes(source_path):
                        self.fail(
                            where, "original WaveDrom bytes differ from release tag"
                        )
                    json_path = str(part.get("json_path", ""))
                    if hashlib.sha256(tagged_bytes(json_path)).hexdigest() != part.get(
                        "json_sha256"
                    ):
                        self.fail(where, "original WaveDrom JSON hash differs")
                elif part.get("source") == "tagged-catalog-svg-generator":
                    generator = str(part.get("generator_path", ""))
                    if hashlib.sha256(tagged_bytes(generator)).hexdigest() != part.get(
                        "generator_sha256"
                    ):
                        self.fail(where, "fallback SVG generator hash differs")
                else:
                    self.fail(where, f"unknown diagram source {part.get('source')!r}")
        if figure_count != 2398 or len(assets_seen) != 2398:
            self.fail(
                "diagrams", f"figures/assets {figure_count}/{len(assets_seen)} != 2398"
            )
        if audit.get("form_count") != 1499 or audit.get("asset_count") != 2398:
            self.fail("diagram-audit.json", "summary counts differ")

    def check_classes(self) -> None:
        expected = expected_class_inventory(self.catalog)
        seen: set[str] = set()
        for filename in CLASS_FILES.values():
            doc = self.document(filename)
            if doc is None:
                continue
            names, errors = class_page_mnemonics(doc)
            for error in errors:
                self.fail(filename, error)
            if names != sorted(names, key=lambda value: value.casefold()):
                self.fail(filename, "mnemonics are not alphabetically ordered")
            if len(names) != len(set(names)):
                self.fail(filename, "duplicate mnemonic rows")
            if set(names) != expected[filename]:
                missing = sorted(expected[filename] - set(names))
                extra = sorted(set(names) - expected[filename])
                self.fail(
                    filename,
                    f"inventory differs; missing={missing[:5]}, extra={extra[:5]}",
                )
            if seen & set(names):
                self.fail(filename, "mnemonic appears in more than one class")
            seen.update(names)
        if len(seen) != 754:
            self.fail("class inventory", f"unique mnemonic total {len(seen)} != 754")
        home = self.document("index.html")
        if home is not None:
            hrefs = {node.attrs.get("href") for node in home.find(tag="a")}
            missing = sorted(set(CLASS_FILES.values()) - hrefs)
            if missing:
                self.fail("index.html", f"missing class links {missing}")

    def run(self) -> list[str]:
        self.check_diagrams()
        self.check_classes()
        return self.errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True, type=Path)
    args = parser.parse_args(argv)
    catalog = tagged_json(CATALOG_PATH)
    errors = Audit(args.site.resolve(), catalog).run()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"Manual structure validation failed: {len(errors)} error(s)",
            file=sys.stderr,
        )
        return 1
    print("OK: 1,499 forms, 2,398 diagram Parts, 754 mnemonics, 9 classes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
