#!/usr/bin/env python3
"""Release-accurate Chinese bodies for the 0.59.1 scalar AMO class."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
SEMANTICS = (
    ROOT / "docs/architecture/isa-manual/reference/data/manual-semantics-zh.json"
)
DIRECT_SOURCES = {
    "SWAPW": ROOT / "docs/zh/isa/inst/misa_s/SWAPW.md",
    "HL.CASW": ROOT / "docs/zh/isa/inst/misa_h/HL.CASW.md",
}
ROLE_ORDER = (
    "purpose",
    "inputs-outputs",
    "mechanism",
    "effects",
    "example",
    "constraints",
)
_EXAMPLE_PREAMBLE = re.compile(
    r"(?:本示例|下面的示例).*?(?:权威来源|不替代规范操作|第二份指令定义)。?"
)


@lru_cache(maxsize=1)
def _semantics() -> dict[str, dict[str, Any]]:
    return json.loads(SEMANTICS.read_text(encoding="utf-8"))["forms"]


def _source_id(row: Mapping[str, Any], source: Mapping[str, Any] | None) -> str:
    return str(
        row.get("pto_source_form_id")
        or (source or {}).get("form_id")
        or row.get("id")
        or ""
    )


def _authored_explanation(mnemonic: str, article: object | None) -> str:
    # These two old pages call the returned word zero-extended.  The 0.59.1
    # owner returns a sign-extended word, so retaining that paragraph would
    # recreate the exact kind of contradiction this manual removes.
    if mnemonic in {"SWAPW", "HL.CASW"}:
        return ""
    if article is None:
        return ""
    sections = []
    for section in getattr(article, "sections", ()):
        heading = str(getattr(section, "heading", "")).rstrip("：:")
        plain = re.sub(r"<[^>]+>", "", heading).strip()
        if plain in {"说明", "简介", "功能说明", "执行模型"}:
            sections.append(
                f"## {heading}\n\n{str(getattr(section, 'markdown', '')).strip()}"
            )
    return "\n\n".join(sections).strip()


def _render_current(record: Mapping[str, Any]) -> str:
    sections = []
    for role in ROLE_ORDER:
        item = record["roles"][role]
        statements = [str(value).strip() for value in item["statements"]]
        if role == "example":
            statements = [
                value
                for value in statements
                if value and not _EXAMPLE_PREAMBLE.fullmatch(value)
            ]
        if statements:
            sections.append(
                "## " + str(item["heading"]) + "\n\n" + "\n\n".join(statements)
            )
    return "\n\n".join(sections).strip()


def _unsupported_dma_free(row: Mapping[str, Any]) -> str:
    mnemonic = str(row["mnemonic"])
    return (
        "## 说明\n\n"
        f"`{mnemonic}` 在 0.59.1 中只保留编码和 `SrcL` 字段。执行语义尚未实现。\n\n"
        "## 执行结果\n\n"
        "实现必须在读取 `SrcL` 或产生任何架构效果之前，以非法指令拒绝该形式。"
        "它不会复制或释放 DMA 资源，不会分配副本，不会发布返回地址或完成状态。\n\n"
        "## 使用约束\n\n"
        "软件不得把这个保留编码当作可执行的 DMA 释放操作。\n"
    )


def atomic_body(
    row: Mapping[str, Any],
    source: Mapping[str, Any] | None = None,
    article: object | None = None,
) -> str | None:
    """Return reviewed Markdown for one base AMO form."""
    if row.get("pto_scope") or row.get("uop_big_kind") != "AMO":
        return None
    mnemonic = str(row.get("mnemonic", ""))
    if mnemonic in DIRECT_SOURCES:
        return DIRECT_SOURCES[mnemonic].read_text(encoding="utf-8")
    if mnemonic in {"DMA.FREE.L", "DMA.FREE.S"}:
        return _unsupported_dma_free(row)
    record = _semantics().get(_source_id(row, source))
    if record is None:
        raise ValueError(f"{mnemonic}: missing 0.59.1 Chinese AMO owner")
    authored = _authored_explanation(mnemonic, article)
    current = _render_current(record)
    return (authored + "\n\n" + current).strip() if authored else current


def validate_atomic_bodies(rows: list[Mapping[str, Any]]) -> list[str]:
    base = [
        row
        for row in rows
        if row.get("uop_big_kind") == "AMO" and not row.get("pto_scope")
    ]
    errors = []
    if len(base) != 61:
        errors.append(f"base AMO count {len(base)} != 61")
    for row in base:
        try:
            body = atomic_body(row)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not body or str(row["mnemonic"]) not in body:
            errors.append(f"{row['mnemonic']}: missing operation-specific Chinese body")
    return errors


__all__ = ["atomic_body", "validate_atomic_bodies"]
