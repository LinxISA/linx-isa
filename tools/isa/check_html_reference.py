#!/usr/bin/env python3
"""Independently validate a rendered LinxISA 0.59.1 offline HTML reference."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import sys
from urllib.parse import unquote, urlsplit

from manual_tag import tagged_json, verified_tag_commit

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "isa/v0.59/linxisa-v0.59.json"
TILES = ROOT / "isa/v0.59/state/pto_tile_operations.json"
SEMANTICS = ROOT / "docs/architecture/isa-manual/reference/pto-v0591-semantics.json"
TILE_MANUAL = (
    ROOT / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
)
READER_DATA = ROOT / "docs/architecture/isa-manual/reference/data/manual-reader-zh.json"


@dataclass
class Node:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node"] = field(default_factory=list)
    chunks: list[str] = field(default_factory=list)
    content: list[object] = field(default_factory=list)

    def text(self) -> str:
        raw = "".join(
            item if isinstance(item, str) else item.raw_text() for item in self.content
        )
        return re.sub(r"\s+", " ", raw).strip()

    def raw_text(self) -> str:
        return "".join(
            item if isinstance(item, str) else item.raw_text() for item in self.content
        )

    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    def find(self, *, tag: str | None = None, cls: str | None = None) -> list["Node"]:
        out = []
        if (tag is None or self.tag == tag) and (cls is None or cls in self.classes()):
            out.append(self)
        for child in self.children:
            out.extend(child.find(tag=tag, cls=cls))
        return out


class Parser(HTMLParser):
    VOID = {"meta", "link", "img", "br", "hr", "input"}

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
        self.stack[-1].chunks.append(data)
        self.stack[-1].content.append(data)


def parse(path: Path) -> Node:
    parser = Parser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.root


ENGLISH_SENTENCE = re.compile(
    r"\b[A-Za-z][A-Za-z'’-]*\b(?:[\s,:;()]+\b[A-Za-z][A-Za-z'’-]*\b){4,}"
)
ENGLISH_PROSE_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "before",
    "bitwise",
    "by",
    "conditionally",
    "does",
    "for",
    "from",
    "in",
    "is",
    "it",
    "legacy",
    "matches",
    "memory",
    "not",
    "of",
    "only",
    "or",
    "packed",
    "prior",
    "be",
    "english",
    "here",
    "must",
    "producer",
    "publishes",
    "reported",
    "replaces",
    "selected",
    "sentence",
    "stores",
    "the",
    "this",
    "through",
    "to",
    "unsigned",
    "value",
    "visible",
    "when",
    "while",
    "width",
    "with",
}
ENGLISH_GRAMMAR_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "before",
    "by",
    "does",
    "for",
    "from",
    "in",
    "is",
    "it",
    "not",
    "of",
    "only",
    "or",
    "the",
    "this",
    "through",
    "to",
    "when",
    "while",
    "with",
    "must",
    "be",
}


def default_visible_text(node: Node) -> list[str]:
    """Return default-visible text, excluding code and closed evidence bodies."""
    if node.tag in {"code", "pre", "script", "style"}:
        return []
    if node.tag == "a" and (
        re.search(r"[\[\]{}<>]|->", node.text())
        or any(suffix in node.text() for suffix in (".asl", ".json", ".opc"))
    ):
        return []
    if (
        node.tag == "details"
        and "variant" not in node.classes()
        and "open" not in node.attrs
    ):
        return [
            text
            for child in node.children
            if child.tag == "summary"
            for text in default_visible_text(child)
        ]
    out = [chunk for chunk in node.chunks if chunk.strip()]
    for child in node.children:
        out.extend(default_visible_text(child))
    return out


def english_visible_fragments(node: Node) -> list[str]:
    residuals = []
    for text in default_visible_text(node):
        normalized = re.sub(r"\s+", " ", text).strip()
        prose = False
        for match in ENGLISH_SENTENCE.finditer(normalized):
            words = [
                word.lower()
                for word in re.findall(r"[A-Za-z][A-Za-z'’-]*", match.group())
            ]
            if sum(word in ENGLISH_PROSE_WORDS for word in words) >= 3 and any(
                word in ENGLISH_GRAMMAR_WORDS for word in words
            ):
                prose = True
                break
        if prose:
            residuals.append(normalized)
    return residuals


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def spelling(row: dict) -> str:
    suffix = {"Private": "PRIVATE", "IntraCore": "INTRA", "InterCore": "INTER"}
    return row["mnemonic"] + (
        "." + suffix[row["pto_scope"]] if "pto_scope" in row else ""
    )


def op_page(row: dict) -> str:
    return f"op-{slug(spelling(row))}.html"


def tile_page(name: str) -> str:
    return f"tile-{slug(name)}.html"


def hex_value(value: int, width: int) -> str:
    return f"0x{value:0{(width + 3) // 4}x}"


def grouped_binary(value: str) -> str:
    if len(value) < 8:
        return value
    first = len(value) % 4 or 4
    return " ".join(
        [value[:first], *(value[i : i + 4] for i in range(first, len(value), 4))]
    )


def expected_fields(row: dict, part_index: int) -> list[tuple[str, str]]:
    raw = row["parts"][part_index]
    encoded = row["encoding"]["parts"][part_index]
    pieces = {}
    for fld in encoded.get("fields", []):
        for piece in fld["pieces"]:
            pieces[(int(piece["insn_msb"]), int(piece["insn_lsb"]))] = (
                fld["name"],
                piece,
            )
    mask, match = int(encoded["mask"], 0), int(encoded["match"], 0)
    out = []
    for seg in sorted(raw["segments"], key=lambda item: int(item["msb"]), reverse=True):
        msb, lsb, width = int(seg["msb"]), int(seg["lsb"]), int(seg["width"])
        bit_range = str(msb) if msb == lsb else f"{msb}:{lsb}"
        if "const" in seg:
            label = grouped_binary(f"{int(seg['const']['value']):0{width}b}")
        else:
            name, piece = pieces[(msb, lsb)]
            bits = ((1 << width) - 1) << lsb
            if mask & bits == bits:
                label = (
                    f"{name} = {grouped_binary(f'{(match & bits) >> lsb:0{width}b}')}"
                )
            elif "value_msb" in piece:
                a, b = int(piece["value_msb"]), int(piece["value_lsb"])
                label = f"{name}[{a}]" if a == b else f"{name}[{a}:{b}]"
            else:
                label = name
        out.append((bit_range, label))
    return out


def fixed_bits(row: dict) -> tuple[int, int]:
    mask = match = offset = 0
    for part in row["encoding"]["parts"]:
        mask |= int(part["mask"], 0) << offset
        match |= int(part["match"], 0) << offset
        offset += int(part["width_bits"])
    return mask, match


def expected_operand_rows(row: dict) -> list[dict[str, object]]:
    """Independently derive the complete cross-part operand table."""
    fields: dict[str, dict[str, object]] = {}
    offset = 0
    for part_index, part in enumerate(row["encoding"]["parts"]):
        for field in part.get("fields", []):
            name = str(field["name"])
            record = fields.setdefault(
                name, {"signed": field.get("signed"), "pieces": []}
            )
            if record["signed"] != field.get("signed"):
                raise ValueError(f"{row['id']}: inconsistent signedness for {name}")
            for piece in field["pieces"]:
                local_lsb, local_msb = int(piece["insn_lsb"]), int(piece["insn_msb"])
                value_lsb = piece.get("value_lsb")
                record["pieces"].append(
                    {
                        "part": part_index,
                        "local_lsb": local_lsb,
                        "local_msb": local_msb,
                        "global_lsb": offset + local_lsb,
                        "global_msb": offset + local_msb,
                        "width": int(piece["width"]),
                        "value_lsb": None if value_lsb is None else int(value_lsb),
                        "value_msb": None
                        if value_lsb is None
                        else int(
                            piece.get(
                                "value_msb", int(value_lsb) + int(piece["width"]) - 1
                            )
                        ),
                    }
                )
        offset += int(part["width_bits"])
    out = []
    signed_names = {True: "有符号", False: "无符号", None: "由编码定义"}
    for name, record in fields.items():
        pieces = record["pieces"]
        has_value_map = all(piece["value_lsb"] is not None for piece in pieces)
        if has_value_map:
            value_bits = {
                int(piece["value_lsb"]) + index
                for piece in pieces
                for index in range(int(piece["width"]))
            }
            width = len(value_bits)
        else:
            width = sum(int(piece["width"]) for piece in pieces)
        mappings = []
        for piece in pieces:
            local = (
                str(piece["local_lsb"])
                if piece["local_lsb"] == piece["local_msb"]
                else f"{piece['local_msb']}:{piece['local_lsb']}"
            )
            glob = (
                str(piece["global_lsb"])
                if piece["global_lsb"] == piece["global_msb"]
                else f"{piece['global_msb']}:{piece['global_lsb']}"
            )
            text = f"P{piece['part']}[{local}] / I[{glob}]"
            if piece["value_lsb"] is not None:
                value = (
                    str(piece["value_lsb"])
                    if piece["value_lsb"] == piece["value_msb"]
                    else f"{piece['value_msb']}:{piece['value_lsb']}"
                )
                text += f" → 字段值[{value}]"
            mappings.append(text)
        out.append(
            {
                "field": name,
                "width": width,
                "mapping": ", ".join(mappings),
                "signedness": signed_names.get(record["signed"], str(record["signed"])),
            }
        )
    return out


def actual_operand_rows(table: Node) -> list[dict[str, object]]:
    rows = []
    for tr in table.find(tag="tr"):
        if "data-field" not in tr.attrs:
            continue
        cells = [child for child in tr.children if child.tag == "td"]
        if len(cells) != 4:
            raise ValueError(f"malformed operand row for {tr.attrs.get('data-field')}")
        rows.append(
            {
                "field": tr.attrs["data-field"],
                "width": int(tr.attrs["data-width"]),
                "mapping": cells[2].text(),
                "signedness": tr.attrs["data-signedness"],
            }
        )
    return rows


def tile_predicate(op: dict, row: dict) -> str:
    mask, match = fixed_bits(row)
    if op["family"] == "TEPL":
        part = row["encoding"]["parts"][0]
        for name in ("Mode", "Function"):
            value = int(op[name.lower()])
            field = next(field for field in part["fields"] if field["name"] == name)
            for piece in field["pieces"]:
                width = int(piece["width"])
                bits = (1 << width) - 1
                lsb = int(piece["insn_lsb"])
                value_lsb = int(piece.get("value_lsb", 0))
                mask |= bits << lsb
                match |= ((value >> value_lsb) & bits) << lsb
    width = int(row["length_bits"])
    return f"(word & 0x{mask:0{width // 4}x}) == 0x{match:0{width // 4}x}"


def informative_synopsis(text: str) -> bool:
    return bool(re.search(r"[一-鿿]", text)) and not (
        any(
            fragment in text
            for fragment in (
                "中文增补说明与发布版编码",
                "当前规范汇编：",
                "本地中文站没有",
                "目录形式与来源",
                "无独立说明",
                "<br",
                "{ width=",
                "```",
            )
        )
        or text.startswith(("目录名为 ", "当前汇编为 ", "参见本页", "本页介绍"))
    )


class Audit:
    def __init__(self, out: Path, catalog: dict, tiles: dict) -> None:
        self.out, self.catalog, self.tiles = out, catalog, tiles
        self.errors: list[str] = []
        self.docs: dict[str, Node] = {}
        self.linx_sail = json.loads(
            (READER_DATA.parent / "manual-linx-sail.json").read_text()
        )
        self.semantic_owners = json.loads(SEMANTICS.read_text(encoding="utf-8"))[
            "forms"
        ]
        self.tile_owners = {
            row["mnemonic"]: row
            for row in json.loads(TILE_MANUAL.read_text(encoding="utf-8"))["operations"]
        }
        self.reader_records = json.loads(READER_DATA.read_text(encoding="utf-8"))[
            "records"
        ]
        self.scoped_owners = {
            row["form_id"]: row
            for row in tagged_json("isa/v0.59/state/pto_scalar_forms.json")[
                "scoped_forms"
            ]
        }

    def check_asl_excerpt(
        self, where: str, blocks: list[Node], owner_path: str
    ) -> None:
        if len(blocks) != 1:
            self.fail(where, f"expected one exact ASL excerpt, found {len(blocks)}")
            return
        record = self.reader_records.get(owner_path)
        if not record:
            self.fail(where, f"missing archived reader owner {owner_path}")
            return
        block = blocks[0]
        snippets = [
            code.raw_text()
            for pre in block.find(tag="pre")
            for code in pre.find(tag="code")
        ]
        expected_snippets = [
            str(item["text"]) for item in record.get("operation_blocks", [])
        ]
        if self.catalog.get("version") == "0.59.2":
            expected_snippets = [
                "\n".join(
                    line
                    for line in snippet.split("\n")
                    if not line.lstrip().startswith("//")
                )
                for snippet in expected_snippets
            ]
        if (
            snippets != expected_snippets
            or not snippets
            or not all(value.strip() for value in snippets)
        ):
            self.fail(
                where, "ASL excerpt text differs from archived pinned source blocks"
            )
        expected_base = str(record["normative_asl_url"])
        links = block.find(tag="a")
        expected_links = [
            f"{expected_base}#L{item['line_start']}-L{item['line_end']}"
            for item in record.get("operation_blocks", [])
        ]
        actual_links = [link.attrs.get("href", "") for link in links]
        if actual_links != expected_links:
            self.fail(
                where,
                f"ASL source links differ: {actual_links!r} != {expected_links!r}",
            )

    def fail(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def document(self, name: str) -> Node | None:
        if name in self.docs:
            return self.docs[name]
        path = self.out / name
        if not path.is_file():
            self.fail(name, "missing HTML file")
            return None
        try:
            self.docs[name] = parse(path)
        except Exception as exc:
            self.fail(name, f"HTML parse failed: {exc}")
            return None
        return self.docs[name]

    def check_form(self, row: dict) -> None:
        page = op_page(row)
        doc = self.document(page)
        where = f"{page}#{row['id']}"
        if doc is None:
            return
        matches = [
            n
            for n in doc.find(tag="article", cls="form")
            if n.attrs.get("id") == row["id"]
        ]
        if len(matches) != 1:
            self.fail(where, f"expected one form article, found {len(matches)}")
            return
        article = matches[0]
        specs = article.find(tag="div", cls="form-spec")
        if len(specs) != 1:
            self.fail(where, "expected one tagged encoding record")
            return
        article = specs[0]
        direct_pres = [child for child in article.children if child.tag == "pre"]
        pre_codes = [c.raw_text() for pre in direct_pres for c in pre.find(tag="code")]
        if pre_codes != [row["asm"]]:
            self.fail(where, f"asm differs: {pre_codes!r} != {row['asm']!r}")
        source_id = row.get("pto_base_form_id") or row.get("pto_source_form_id")
        asl_blocks = article.find(tag="details", cls="asl-operation")
        if source_id:
            owner = self.semantic_owners.get(source_id)
            if owner is None:
                self.fail(where, f"unresolved semantic owner {source_id}")
            else:
                self.check_asl_excerpt(where, asl_blocks, str(owner["source_path"]))
        elif asl_blocks:
            self.fail(
                where, "Linx-only form unexpectedly presents PTO ASL as normative"
            )
        if not source_id:
            evidence = self.linx_sail["forms"].get(row["id"])
            model = article.find(tag="details", cls="linx-sail-evidence")
            if evidence is None or len(model) != 1:
                self.fail(where, "missing Linx-only Sail dispatch evidence")
            else:
                snippets = [
                    code.raw_text()
                    for pre in model[0].find(tag="pre")
                    for code in pre.find(tag="code")
                ]
                handlers = self.linx_sail["handlers"]
                expected = [
                    evidence["decode"]["excerpt"],
                    *(handlers[h]["excerpt"] for h in evidence["helpers"]),
                ]
                if (
                    snippets != expected
                    or model[0].attrs.get("data-disposition") != evidence["disposition"]
                ):
                    self.fail(where, "Linx-only Sail path or source text differs")
        if row.get("pto_scope"):
            contracts = article.find(tag="section", cls="scoped-contract")
            if len(contracts) != 1:
                self.fail(
                    where, f"expected one scoped-contract, found {len(contracts)}"
                )
            else:
                pairs = {}
                for dl in contracts[0].find(tag="dl"):
                    children = dl.children
                    for index, child in enumerate(children):
                        if (
                            child.tag == "dt"
                            and index + 1 < len(children)
                            and children[index + 1].tag == "dd"
                        ):
                            pairs[child.text()] = children[index + 1].text()
                expected_keys = {
                    "汇编形式",
                    "GM 共享属性",
                    "语义处理器",
                    "基础形式",
                    "契约状态",
                }
                if set(pairs) != expected_keys:
                    self.fail(where, f"scoped contract keys differ: {set(pairs)!r}")
                owner = self.scoped_owners.get(str(row.get("pto_source_form_id")))
                if owner is None:
                    self.fail(where, "missing exact scoped source owner")
                else:
                    expected_values = {
                        "汇编形式": owner["asm"],
                        "GM 共享属性": owner["scope"],
                        "语义处理器": owner["semantic_handler"],
                        "基础形式": owner["base_form_id"],
                        "契约状态": owner["status"],
                    }
                    for key, value in expected_values.items():
                        if str(value) not in pairs.get(key, ""):
                            self.fail(where, f"{key} omits exact value {value!r}")
        if (
            "NOT IMPLEMENTED" in row.get("note", "")
            and "编码保留" not in article.text()
        ):
            self.fail(
                where, "encoding-only form lacks its reject-before-effects status"
            )
        sources = [
            child
            for child in article.children
            if child.tag == "p" and "source" in child.classes()
        ]
        if (
            len(sources) != 1
            or row["id"] not in sources[0].text()
            or not sources[0].find(tag="a")
        ):
            self.fail(where, "missing source trace with form ID and link")
        elif (
            row.get("pto_source_form_id")
            and row["pto_source_form_id"] not in sources[0].text()
        ):
            self.fail(where, "source trace omits exact PTO form ID")
        elif not row.get("pto_source_form_id"):
            expected_tail = (
                "isa/v0.59.2/linxisa-v0.59.2.json"
                if self.catalog.get("version") == "0.59.2"
                else f"isa/v0.58/{row['source']['file']}#L{row['source']['line']}"
            )
            if expected_tail not in sources[0].find(tag="a")[0].attrs.get("href", ""):
                self.fail(where, f"Linx source trace does not end in {expected_tail}")
        parts = article.find(tag="section", cls="encoding-part")
        expected_parts = row["encoding"]["parts"]
        if len(parts) != len(expected_parts):
            self.fail(
                where, f"encoding part count {len(parts)} != {len(expected_parts)}"
            )
            return
        for index, (node, expected) in enumerate(zip(parts, expected_parts)):
            pwhere = f"{where}/part-{index}"
            if node.attrs.get("data-part") != str(index):
                self.fail(pwhere, "wrong data-part")
            fields = node.find(tag="div", cls="encoding-field")
            actual_fields = []
            for fld in fields:
                ranges = fld.find(tag="span", cls="encoding-bit-range")
                codes = fld.find(tag="code")
                if len(ranges) != 1 or len(codes) != 1:
                    self.fail(pwhere, "malformed field box")
                    continue
                actual_fields.append((ranges[0].text(), codes[0].text()))
            wanted = expected_fields(row, index)
            if actual_fields != wanted:
                self.fail(
                    pwhere, f"field boxes differ: {actual_fields!r} != {wanted!r}"
                )
            exact = node.find(tag="dl", cls="encoding-exact")
            pairs = {}
            if len(exact) == 1:
                for div in exact[0].find(tag="div"):
                    dt, dd = div.find(tag="dt"), div.find(tag="dd")
                    if len(dt) == len(dd) == 1:
                        pairs[dt[0].text()] = dd[0].text()
            width = int(expected["width_bits"])
            wanted_exact = {
                "掩码（Mask）": hex_value(int(expected["mask"], 0), width),
                "匹配值（Match）": hex_value(int(expected["match"], 0), width),
                "位模式（Pattern）": expected["pattern"],
            }
            if pairs != wanted_exact:
                self.fail(
                    pwhere, f"exact encoding differs: {pairs!r} != {wanted_exact!r}"
                )
        operand_tables = article.find(tag="table", cls="encoding-operands")
        wanted_operands = expected_operand_rows(row)
        if bool(operand_tables) != bool(wanted_operands) or len(operand_tables) > 1:
            self.fail(
                where,
                f"operand table count {len(operand_tables)} does not match field presence",
            )
        elif operand_tables:
            try:
                actual_operands = actual_operand_rows(operand_tables[0])
            except (KeyError, TypeError, ValueError) as exc:
                self.fail(where, f"malformed operand table: {exc}")
            else:
                if actual_operands != wanted_operands:
                    self.fail(
                        where,
                        f"operand table differs: {actual_operands!r} != {wanted_operands!r}",
                    )

    def check_audit_json(self) -> None:
        path = self.out / "audit.json"
        if not path.is_file():
            self.fail("audit.json", "missing")
            return
        try:
            audit = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.fail("audit.json", f"invalid JSON: {exc}")
            return
        got = {row["id"]: row for row in audit.get("forms", [])}
        rows = self.catalog["instructions"]
        if len(got) != len(rows):
            self.fail("audit.json", f"form count {len(got)} != {len(rows)}")
        for row in rows:
            record = got.get(row["id"])
            if not record:
                self.fail("audit.json", f"missing {row['id']}")
                continue
            mask, match = fixed_bits(row)
            expected = {
                "asm": row["asm"],
                "bits": row["length_bits"],
                "mask": hex(mask),
                "match": hex(match),
                "page": op_page(row) + "#" + row["id"],
            }
            for key, value in expected.items():
                if record.get(key) != value:
                    self.fail(
                        f"audit.json/{row['id']}",
                        f"{key} {record.get(key)!r} != {value!r}",
                    )
        tile_records = {r["name"]: r for r in audit.get("tile_operations", [])}
        if len(tile_records) != 119:
            self.fail("audit.json", f"Tile count {len(tile_records)} != 119")
        for op in self.tiles["operations"]:
            record = tile_records.get(op["name"])
            wanted = {"page": tile_page(op["name"]), "carrier": op["command_mnemonic"]}
            if record is None:
                self.fail("audit.json", f"missing Tile operation {op['name']}")
            else:
                for key, value in wanted.items():
                    if record.get(key) != value:
                        self.fail(
                            f"audit.json/{op['name']}",
                            f"{key} {record.get(key)!r} != {value!r}",
                        )

    def check_tiles(self) -> None:
        operations = self.tiles["operations"]
        if len(operations) != 119:
            self.fail("tile source", f"operation count {len(operations)} != 119")
        for op in operations:
            page = tile_page(op["name"])
            doc = self.document(page)
            if doc is None:
                continue
            contracts = doc.find(tag="section", cls="tile-contract")
            if len(contracts) != 1:
                self.fail(page, f"expected one tile-contract, found {len(contracts)}")
                continue
            node = contracts[0]
            mains = [main for main in doc.find(tag="div", cls="release-data-body")]
            page_pres = []
            if len(mains) == 1:
                for pre in [child for child in mains[0].children if child.tag == "pre"]:
                    codes = pre.find(tag="code")
                    if len(codes) == 1:
                        page_pres.append(codes[0].raw_text())
            carrier_rows = [
                row
                for row in self.catalog["instructions"]
                if row["mnemonic"] == op["command_mnemonic"] and "pto_scope" not in row
            ]
            if not carrier_rows:
                self.fail(page, f"missing carrier row {op['command_mnemonic']}")
            else:
                owner = self.tile_owners.get(op["name"])
                try:
                    from manual_block_zh import translate_block
                except ImportError:
                    self.fail(page, "missing manual_block_zh translator")
                    translate_block = lambda lines: lines
                expected_pres = [
                    tile_predicate(op, carrier_rows[0]),
                    "\n".join(translate_block(owner.get("block", []))) if owner else "",
                ]
                if (
                    len(page_pres) != 2
                    or page_pres != expected_pres
                    or not all(value.strip() for value in page_pres)
                ):
                    self.fail(
                        page,
                        f"Tile header code blocks differ: {page_pres!r} != {expected_pres!r}",
                    )
                source_blocks = doc.find(tag="details", cls="tile-block-source")
                source_text = [
                    code.raw_text()
                    for detail in source_blocks
                    for pre in detail.find(tag="pre")
                    for code in pre.find(tag="code")
                ]
                expected_source = "\n".join(owner.get("block", [])) if owner else ""
                if len(source_blocks) != 1 or source_text != [expected_source]:
                    self.fail(
                        page, "folded Tile source block differs from exact original"
                    )
            owner = self.tile_owners.get(op["name"])
            if owner:
                self.check_asl_excerpt(
                    page,
                    doc.find(tag="details", cls="asl-operation"),
                    str(owner["source_path"]),
                )
            pairs = {}
            for dl in node.find(tag="dl"):
                children = dl.children
                for i, child in enumerate(children):
                    if (
                        child.tag == "dt"
                        and i + 1 < len(children)
                        and children[i + 1].tag == "dd"
                    ):
                        pairs[child.text()] = children[i + 1].text()
            selector = str(op.get("selector") or f"Function={op['function']}")
            wanted = {
                "引擎": op["engine"],
                "承载指令": op["command_mnemonic"],
                "选择器": selector,
                "语义处理器": op["semantic_handler"],
            }
            for key, value in wanted.items():
                if str(value) not in pairs.get(key, ""):
                    self.fail(page, f"{key} {pairs.get(key)!r} omits {value!r}")
            if not node.find(tag="a") or not pairs.get("ASL 来源"):
                self.fail(page, "missing pinned ASL source")

    def check_indexes(self) -> None:
        # Audit displayed synopsis cells, including class/engine indexes and
        # scoped spellings. A valid link alone does not explain an operation.
        for path in sorted(self.out.glob("*.html")):
            if path.name not in {"tile.html", "mnemonics.html"} and not (
                path.name.startswith("class-") or path.name.startswith("tiles-")
            ):
                continue
            doc = self.document(path.name)
            if doc is None:
                continue
            for row in doc.find(tag="li"):
                if "data-search" not in row.attrs:
                    continue
                columns = [c for c in row.children if c.tag == "span"]
                if len(columns) != 2:
                    self.fail(path.name, "invalid mnemonic index row")
                    continue
                name, synopsis = (column.text() for column in columns)
                if not informative_synopsis(synopsis):
                    self.fail(
                        path.name, f"{name}: missing instruction purpose: {synopsis}"
                    )
        encoding = self.document("encoding.html")
        if encoding is not None:
            indexed = {}
            for tr in [n for n in encoding.find(tag="tr") if "data-search" in n.attrs]:
                links = tr.find(tag="a")
                codes = [n.text() for n in tr.find(tag="code")]
                if len(links) != 1 or len(codes) != 2:
                    self.fail("encoding.html", "malformed encoding row")
                    continue
                indexed[links[0].attrs.get("href", "")] = codes
            if len(indexed) != len(self.catalog["instructions"]):
                self.fail(
                    "encoding.html",
                    f"row count {len(indexed)} != {len(self.catalog['instructions'])}",
                )
            for row in self.catalog["instructions"]:
                href = op_page(row) + "#" + row["id"]
                mask, match = fixed_bits(row)
                width = int(row["length_bits"])
                wanted = [hex_value(match, width), hex_value(mask, width)]
                if indexed.get(href) != wanted:
                    self.fail(
                        "encoding.html",
                        f"{href} values {indexed.get(href)!r} != {wanted!r}",
                    )
        index = self.document("mnemonics.html")
        if index is not None:
            hrefs = {n.attrs.get("href") for n in index.find(tag="a")}
            expected = {op_page(row) for row in self.catalog["instructions"]}
            missing = sorted(expected - hrefs)
            if missing:
                self.fail(
                    "mnemonics.html", f"missing {len(missing)} instruction page links"
                )
        tile_index = self.document("tile.html")
        if tile_index is not None:
            hrefs = {n.attrs.get("href") for n in tile_index.find(tag="a")}
            missing = sorted(
                {tile_page(op["name"]) for op in self.tiles["operations"]} - hrefs
            )
            if missing:
                self.fail("tile.html", f"missing {len(missing)} Tile page links")

    def check_links_and_assets(self) -> None:
        html_files = sorted(self.out.rglob("*.html"))
        for required in (
            "index.html",
            "encoding.html",
            "tile.html",
            "sources.html",
            "manual.css",
            "index-filter.js",
            "audit.json",
        ):
            if not (self.out / required).is_file():
                self.fail(required, "missing offline asset")
        ids_by_file: dict[str, set[str]] = {}
        rendered_forms: list[str] = []
        for path in html_files:
            relative = path.relative_to(self.out).as_posix()
            doc = self.document(relative)
            if doc is None:
                continue
            ids = [n.attrs["id"] for n in doc.find() if "id" in n.attrs]
            duplicates = sorted({value for value in ids if ids.count(value) > 1})
            if duplicates:
                self.fail(relative, f"duplicate IDs: {duplicates}")
            ids_by_file[relative] = set(ids)
            rendered_forms.extend(
                n.attrs.get("id", "") for n in doc.find(tag="article", cls="form")
            )
        expected_forms = {row["id"] for row in self.catalog["instructions"]}
        if (
            len(rendered_forms) != len(expected_forms)
            or set(rendered_forms) != expected_forms
        ):
            self.fail(
                "HTML form inventory",
                f"rendered {len(rendered_forms)} articles / {len(set(rendered_forms))} IDs, expected {len(expected_forms)}",
            )
        for path in html_files:
            relative = path.relative_to(self.out).as_posix()
            doc = self.docs.get(relative)
            if doc is None:
                continue
            authored_text = {
                re.sub(r"\s+", " ", text).strip()
                for node in doc.find(cls="authored-reader")
                for text in default_visible_text(node)
            }
            for residual in english_visible_fragments(doc):
                if residual not in authored_text:
                    self.fail(
                        relative, f"default-visible English sentence: {residual!r}"
                    )
            for anchor in doc.find(tag="a"):
                href = anchor.attrs.get("href", "")
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc:
                    continue
                decoded = unquote(parsed.path)
                target_name = (
                    posixpath.normpath(
                        posixpath.join(posixpath.dirname(relative), decoded)
                    )
                    if decoded
                    else relative
                )
                if target_name == ".." or target_name.startswith("../"):
                    self.fail(relative, f"href escapes offline root {href!r}")
                    continue
                target = self.out / target_name
                if not target.is_file():
                    self.fail(relative, f"broken href {href!r}")
                    continue
                if parsed.fragment and target.suffix == ".html":
                    if target_name not in ids_by_file:
                        doc2 = self.document(target_name)
                        ids_by_file[target_name] = (
                            {n.attrs["id"] for n in doc2.find() if "id" in n.attrs}
                            if doc2
                            else set()
                        )
                    if unquote(parsed.fragment) not in ids_by_file[target_name]:
                        self.fail(relative, f"missing fragment target {href!r}")
            for node in (
                doc.find(tag="img") + doc.find(tag="link") + doc.find(tag="script")
            ):
                ref = node.attrs.get("href") or node.attrs.get("src")
                if not ref:
                    continue
                parsed = urlsplit(ref)
                if parsed.scheme or parsed.netloc:
                    continue
                decoded = unquote(parsed.path)
                target_name = posixpath.normpath(
                    posixpath.join(posixpath.dirname(relative), decoded)
                )
                if (
                    target_name == ".."
                    or target_name.startswith("../")
                    or not (self.out / target_name).is_file()
                ):
                    self.fail(relative, f"missing offline asset {ref!r}")

    def run(self) -> list[str]:
        for row in self.catalog["instructions"]:
            self.check_form(row)
        self.check_audit_json()
        self.check_tiles()
        self.check_indexes()
        self.check_links_and_assets()
        return self.errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site",
        type=Path,
        required=True,
        help="Generated instruction-reference directory",
    )
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--tiles", type=Path)
    args = parser.parse_args(argv)
    catalog = (
        json.loads(args.catalog.read_text(encoding="utf-8"))
        if args.catalog
        else tagged_json(CATALOG.relative_to(ROOT).as_posix())
    )
    tiles = (
        json.loads(args.tiles.read_text(encoding="utf-8"))
        if args.tiles
        else tagged_json(TILES.relative_to(ROOT).as_posix())
    )
    errors = Audit(args.site.resolve(), catalog, tiles).run()
    if not args.catalog and not args.tiles and not errors:
        stamp = json.loads((args.site / "audit.json").read_text())
        if stamp["commit"] != verified_tag_commit():
            errors.append("audit.json: incorrect specification commit")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"HTML reference validation failed: {len(errors)} error(s)", file=sys.stderr
        )
        return 1
    print(
        f"OK: {len(catalog['instructions'])} forms, {len(tiles['operations'])} Tile operations, links and offline assets"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
