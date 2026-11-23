#!/usr/bin/env python3
"""Current Chinese detail prose for every published PTO 0.59.1 Tile operation.

The old Linx Tile pages remain valuable as explanations and diagrams, but they
predate the locked PTO contract in several places.  This module renders the
reviewed Chinese PTO owner text directly, so a detail page never needs to show
an old operation body next to a contradictory release note.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Any, Mapping

try:
    from manual_supplements import TILE_PATHS
    from manual_tag import tagged_json
except ModuleNotFoundError:
    from tools.isa.manual_supplements import TILE_PATHS
    from tools.isa.manual_tag import tagged_json


ROOT = Path(__file__).resolve().parents[2]
SEMANTICS = (
    ROOT / "docs/architecture/isa-manual/reference/data/manual-tile-semantics-zh.json"
)
DIRECT_SOURCES = {
    "MGATHER": ROOT / "docs/zh/isa/header/tileblock/MGATHER.md",
    "MSCATTER": ROOT / "docs/zh/isa/header/tileblock/MSCATTER.md",
}

ROLE_ORDER = (
    "purpose",
    "inputs-outputs",
    "mechanism",
    "effects",
    "example",
    "constraints",
)

# These sentences describe the provenance of the generated reader rather than
# the instruction.  Omitting them makes the page read like a chip-development
# manual while retaining the checked example that follows.
_EXAMPLE_PREAMBLE = re.compile(
    r"(?:本示例|下面的示例|生成的\s+\S+\s+示例|这是非规范契约模式草图)"
    r".*?(?:不替代规范操作|不是第二份指令定义|下方 owner 定义的 legality 和状态合同|不声称可以直接汇编)。?"
)

_ROW_REDUCTIONS = {
    "TROWSUM",
    "TROWMAX",
    "TROWMIN",
    "TROWPROD",
    "TROWARGMAX",
    "TROWARGMIN",
}
_COLUMN_REDUCTIONS = {
    "TCOLSUM",
    "TCOLMAX",
    "TCOLMIN",
    "TCOLPROD",
    "TCOLARGMAX",
    "TCOLARGMIN",
}


@lru_cache(maxsize=1)
def _operations() -> dict[str, dict[str, Any]]:
    rows = tagged_json("isa/v0.59/state/pto_tile_operations.json")["operations"]
    return {str(row["name"]): row for row in rows}


@lru_cache(maxsize=1)
def _semantics() -> dict[str, dict[str, Any]]:
    document = json.loads(SEMANTICS.read_text(encoding="utf-8"))
    if document.get("source_commit") != "a89a53d48f5708328be609fe2e6296ac8bdb4bc2":
        raise ValueError("Tile Chinese semantics are not pinned to PTO 0.59.1")
    return document["operations"]


@lru_cache(maxsize=1)
def _operation_by_command() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for operation in _operations().values():
        command = str(operation["command_mnemonic"])
        if command == "BSTART.TEPL":
            continue
        if command in result:
            raise ValueError(
                f"typed Tile command selects more than one operation: {command}"
            )
        result[command] = operation
    return result


def _operation_name(value: str | Mapping[str, Any]) -> str:
    return value if isinstance(value, str) else str(value.get("name", ""))


def _statements(name: str, role: str) -> tuple[str, ...]:
    section = _semantics()[name]["roles"][role]
    statements = tuple(str(statement).strip() for statement in section["statements"])
    if role == "example":
        statements = tuple(
            statement
            for statement in statements
            if statement and not _EXAMPLE_PREAMBLE.fullmatch(statement)
        )
    return statements


def _corrected_statement(name: str, statement: str) -> str:
    """Remove example dimensions that leaked into four generic arg-reduce pages."""
    if name in _ROW_REDUCTIONS:
        statement = statement.replace(
            "逻辑形状为 7 个有效行乘一个有效列",
            "逻辑形状为 ValidRow 个有效行乘一个有效列",
        ).replace(
            "7 x 1 有效区域之外",
            "ValidRow x 1 有效区域之外",
        )
    if name in _COLUMN_REDUCTIONS:
        statement = statement.replace(
            "逻辑形状为 一个有效行乘 60 个有效列",
            "逻辑形状为一个有效行乘 ValidCol 个有效列",
        ).replace(
            "1 x 60 有效区域之外",
            "1 x ValidCol 有效区域之外",
        )
    return statement


def _render_roles(name: str, roles: tuple[str, ...]) -> str:
    record = _semantics()[name]
    sections = []
    for role in roles:
        section = record["roles"][role]
        statements = [
            _corrected_statement(name, statement)
            for statement in _statements(name, role)
        ]
        if statements:
            sections.append(
                "## " + str(section["heading"]) + "\n\n" + "\n\n".join(statements)
            )
    return "\n\n".join(sections).strip() + "\n"


def _normalized_title(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def _authored_explanation(name: str, article: object | None) -> str:
    """Keep explanatory prose and figures only from the exact operation page."""
    if article is None or _normalized_title(
        str(getattr(article, "title", ""))
    ) != _normalized_title(name):
        return ""
    sections = []
    for section in getattr(article, "sections", ()):
        heading = str(getattr(section, "heading", "")).rstrip("：:")
        plain_heading = re.sub(r"<[^>]+>", "", heading).strip()
        if plain_heading in {"说明", "简介", "功能说明", "执行模型"}:
            prefix = ""
            if name == "MGATHER" and plain_heading == "执行模型":
                prefix = (
                    "> 下面的伪代码描述普通非打包类型的逻辑坐标。CUBE 布局仍按布局映射寻址；"
                    "四位打包类型由一个索引字节承载两个相邻逻辑元素。精确边界见后文。\n\n"
                )
            sections.append(
                f"## {heading}\n\n{prefix}{str(getattr(section, 'markdown', '')).strip()}"
            )
    return "\n\n".join(sections).strip()


def tile_body(
    operation: str | Mapping[str, Any], article: object | None = None
) -> str | None:
    """Return current Chinese Markdown for one published Tile operation.

    Existing 0.59.1 supplements remain their own source files.  Every older
    Linx article is replaced because a filename match is insufficient proof
    that it implements the locked PTO operation, and several old family pages
    are shared by semantically distinct atomic forms.
    """
    name = _operation_name(operation)
    if name not in _operations() or name not in _semantics():
        return None
    if name in TILE_PATHS:
        return None
    if name in DIRECT_SOURCES:
        return DIRECT_SOURCES[name].read_text(encoding="utf-8")
    # Historical CUBE pages use queue and accumulator language that does not
    # match the released operand contract.  A dedicated CUBE review owns any
    # prose reuse for those pages.
    authored = (
        ""
        if str(_operations()[name].get("engine")) == "CUBE"
        else _authored_explanation(name, article)
    )
    if not authored:
        return _render_roles(name, ROLE_ORDER)
    current = _render_roles(
        name, ("inputs-outputs", "mechanism", "effects", "example", "constraints")
    )
    return authored + "\n\n" + current


def tile_command_body(
    row: Mapping[str, Any],
    source: Mapping[str, Any] | None = None,
    article: object | None = None,
) -> str | None:
    """Return current prose for a standalone typed BSTART Tile command."""
    del article
    mnemonic = str(row.get("mnemonic", ""))
    operation = _operation_by_command().get(mnemonic)
    if operation is None:
        return None
    if source is not None and str(source.get("mnemonic", mnemonic)) != mnemonic:
        raise ValueError(f"{mnemonic}: command source has a different mnemonic")
    name = str(operation["name"])
    purpose = "\n\n".join(
        _corrected_statement(name, statement)
        for statement in _statements(name, "purpose")
    )
    inputs = "\n".join(
        "- " + _corrected_statement(name, statement)
        for statement in _statements(name, "inputs-outputs")
    )
    constraints = "\n".join(
        "- " + _corrected_statement(name, statement)
        for statement in _statements(name, "constraints")
    )
    return (
        "## 说明\n\n"
        f"`{mnemonic}` 选择 Tile 操作 `{name}`。实际效果在完整指令束提交时发生。\n\n"
        f"{purpose}\n\n"
        "## 块内操作数\n\n"
        f"{inputs}\n\n"
        "## 合法性与异常\n\n"
        f"{constraints}\n"
    )


def validate_tile_bodies() -> list[str]:
    errors = []
    operation_names = set(_operations())
    semantic_names = set(_semantics())
    if operation_names != semantic_names:
        errors.append(
            "Tile operation/Chinese semantic inventories differ: "
            f"operations={len(operation_names)}, semantics={len(semantic_names)}"
        )
    if len(operation_names) != 119:
        errors.append(f"published Tile operation count {len(operation_names)} != 119")
    for name, operation in _operations().items():
        body = tile_body(operation)
        if name in TILE_PATHS:
            path = (
                ROOT / "docs/zh/architecture/isa-manual/supplements" / TILE_PATHS[name]
            )
            if body is not None or not path.is_file():
                errors.append(f"{name}: 0.59.1 supplement was not preserved")
            continue
        if not body or name not in body or not re.search(r"[一-鿿]", body):
            errors.append(f"{name}: missing operation-specific Chinese body")
        if body and _EXAMPLE_PREAMBLE.search(body):
            errors.append(f"{name}: reader provenance leaked into the detail body")
    for command, operation in _operation_by_command().items():
        body = tile_command_body({"mnemonic": command})
        if not body or command not in body or str(operation["name"]) not in body:
            errors.append(f"{command}: missing typed command body")
    return errors


__all__ = ["tile_body", "tile_command_body", "validate_tile_bodies"]
