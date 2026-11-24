"""Prepare the instruction reader from the tagged article and its released forms."""

from __future__ import annotations

import posixpath
import re
from functools import lru_cache

from manual_detail_atomic import atomic_body
from manual_detail_scalar import scalar_body
from manual_detail_tile import tile_body, tile_command_body
from manual_editorial import edit_article
from manual_authored import authored_for
from manual_tag import REPO_ROOT, tagged_json
from manual_reader import _plain_markdown

# The edited Chinese source is also the input for the standalone HTML.
REVISED_ALU = {
    "ADD",
    "ADDW",
    "AND",
    "ANDW",
    "BCNT",
    "BIC",
    "BIS",
    "BXS",
    "BXU",
    "C.SETC.TGT",
    "CLZ",
    "CSEL",
    "CTZ",
    "HL.BFI",
    "HL.SETC.LTI",
    "HL.SETC.ORI",
    "HL.CCAT",
    "HL.CCATW",
    "HL.MADD",
    "HL.MADDW",
    "HL.MUL",
    "HL.MULU",
    "MULUW",
    "OR",
    "ORW",
    "REV",
    "SUB",
    "SUBW",
    "XOR",
    "XORW",
} | {
    prefix + op + suffix
    for prefix in ("", "HL.")
    for op in ("DIV", "REM")
    for suffix in ("", "U", "W", "UW")
}
SCOPE_NAMES = {"Private": "私有", "IntraCore": "核内共享", "InterCore": "跨核共享"}
SECTION = re.compile(r"^## ([^\n]+)\n[\s\S]*?(?=^## |\Z)", re.MULTILINE)
ASSEMBLY = re.compile(r"```[^\n]*\n([\s\S]*?)\n\s*```")
IMAGE = re.compile(r"!\[[^\]]*\]\(([^) ]+)")


@lru_cache(maxsize=1)
def source_forms():
    result = {}
    for path in ("pto_scalar_forms", "pto_command_forms"):
        doc = tagged_json(f"isa/v0.59/state/{path}.json")
        for form in doc["forms"] + doc.get("scoped_forms", []):
            result[form["form_id"]] = form
    return result


def _syntax(rows):
    return "\n".join(dict.fromkeys(row["asm"] for row in rows))


def _current_sections(markdown, rows, path, parts):
    """Keep matching syntax and WaveDrom figures; the form record supplies other diagrams."""
    syntax = _syntax(rows)
    svg = [p.get("svg_path") for p in parts]

    def replace(match):
        heading, section = match[1].strip().rstrip("：:"), match[0]
        if heading == "汇编语法":
            asm = ASSEMBLY.search(section)
            if asm and asm[1].strip() == syntax and len(rows) == 1:
                return section
            return f"## 汇编语法\n\n```asm\n{syntax}\n```\n\n"
        if "编码" in heading and ("格式" in heading or "位图" in heading):
            figures = [
                posixpath.normpath(posixpath.join(posixpath.dirname(path), url))
                for url in IMAGE.findall(section)
            ]
            if len(rows) != 1 or not figures or figures != svg:
                return ""
        return section

    return SECTION.sub(replace, markdown)


def _base_revision(base, article):
    """Resolve reviewed semantics against one specific base encoding."""
    if not article:
        return None
    source = source_forms().get(base.get("pto_source_form_id"), {})
    if base["mnemonic"] in REVISED_ALU or base["uop_big_kind"] == "FSU":
        return (REPO_ROOT / article.source_path).read_text(encoding="utf-8")
    revised = (
        tile_command_body(base, source, article)
        or atomic_body(base, source, article)
        or scalar_body(base, source, article)
    )
    if not revised and article.classification == "conflicting-current":
        raise ValueError(f"{base['mnemonic']}: missing reviewed instruction text")
    return revised


def instruction_body(rows, base_rows, article, parts):
    if not article:
        return None
    row = rows[0]
    groups = {}
    for variant in rows:
        base = (
            base_rows[variant["pto_base_form_id"]]
            if variant.get("pto_scope")
            else variant
        )
        text = _base_revision(base, authored_for(base))
        groups.setdefault(text, []).append(variant["asm"])
    if len(groups) == 1:
        revised = next(iter(groups))
    else:
        sections = []
        for text, spellings in groups.items():
            if not text:
                raise ValueError(
                    f"{row['mnemonic']}: only some encoding forms have a reviewed body"
                )
            sections.append(
                "## 汇编形式\n\n```asm\n"
                + "\n".join(spellings)
                + "\n```\n\n"
                + text.strip()
            )
        revised = "\n\n".join(sections)
    if scope := row.get("pto_scope"):
        # Assembly examples and the old base diagrams use a different carrier.
        # The full base article remains reachable through the related-form link.
        semantics = revised
        if semantics:
            semantics = SECTION.sub(
                lambda match: (
                    ""
                    if any(word in match[1] for word in ("汇编", "编码", "索引模式"))
                    or (
                        ("示例" in match[1] or "例子" in match[1])
                        and base["mnemonic"].lower() in match[0].lower()
                    )
                    else match[0]
                ),
                re.sub(r"^# [^\n]*\n", "", semantics),
            )
        if not semantics:
            intro = next(
                (s.markdown for s in article.sections if s.heading == "说明"),
                article.intro,
            )
            if not intro:
                raise ValueError(f"{row['id']}: missing base description")
            semantics = "## 说明\n\n" + intro
        return (
            "## 访存作用域\n\n本指令采用 64 位编码，访存请求使用"
            + SCOPE_NAMES[scope]
            + "属性。\n\n```asm\n"
            + _syntax(rows)
            + "\n```\n\n"
            + semantics.strip()
        )
    if revised:
        return _current_sections(revised, rows, article.source_path, parts).strip()
    original = edit_article(article.source_path)[0]
    current = _current_sections(original, rows, article.source_path, parts)
    return current if current != original else None


def revised_intro(markdown):
    """Use a revised operation paragraph when the previous index text was superseded."""
    if not markdown:
        return ""
    for match in SECTION.finditer(markdown):
        if match[1].strip() not in {"说明", "用途", "功能说明"}:
            continue
        body = match[0].split("\n", 1)[1].strip()
        paragraph = body.split("\n\n", 1)[0]
        if "```" in paragraph or "![" in paragraph:
            return ""
        plain = _plain_markdown(paragraph).strip()
        gloss = re.match(
            r"^[^()（）]{1,90}[（(][A-Za-z][A-Za-z ,/+:._’'–-]+[）)]\s*(.+)$", plain
        )
        if gloss and re.search(r"[一-鿿]", gloss[1]):
            plain = gloss[1]
        if re.search(r"(?:[A-Za-z]+ ){4,}[A-Za-z]+", plain):
            return ""

        return plain if len(plain) <= 130 else plain.split("。")[0] + "。"
    return ""


def operation_body(op, article):
    if article and op["name"].startswith(("TMATMUL", "TGEMV")):
        return (REPO_ROOT / article.source_path).read_text(encoding="utf-8")
    return tile_body(op, article) if article else None
