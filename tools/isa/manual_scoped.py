#!/usr/bin/env python3
"""Precise manual fragments for PTO 0.59.1 scoped Scalar and Tile operations."""

from __future__ import annotations
from functools import lru_cache
from html import escape
import json
from pathlib import Path
from typing import Any
from manual_tag import tagged_json
from manual_scoped_zh import ENGINE, SCOPE, role_zh, scoped_summary_zh

ROOT = Path(__file__).resolve().parents[2]
MANUAL_PATH = (
    ROOT / "docs/architecture/isa-manual/reference/data/pto-v0591-tile-manual.json"
)
MANUAL_ZH_PATH = (
    ROOT / "docs/architecture/isa-manual/reference/data/manual-tile-semantics-zh.json"
)
SCOPED_SAIL = "isa/sail/model/execute/scoped_scalar.sail"

SCOPE_TEXT = {
    "Private": "Private GM shareability request",
    "IntraCore": "IntraCore GM shareability request",
    "InterCore": "InterCore GM shareability request",
}


@lru_cache(maxsize=None)
def _load(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _scoped_index() -> dict[str, dict[str, Any]]:
    return {
        r["form_id"]: r
        for r in tagged_json("isa/v0.59/state/pto_scalar_forms.json")["scoped_forms"]
    }


def _base_index() -> dict[str, dict[str, Any]]:
    return {
        r["form_id"]: r
        for r in tagged_json("isa/v0.59/state/pto_scalar_forms.json")["forms"]
    }


def _tile_index() -> dict[str, dict[str, Any]]:
    return {r["mnemonic"]: r for r in _load(str(MANUAL_PATH))["operations"]}


def _tile_zh_index() -> dict[str, dict[str, Any]]:
    return _load(str(MANUAL_ZH_PATH))["operations"]


def _source_row(row: dict[str, Any]) -> dict[str, Any]:
    form_id = row.get("pto_source_form_id") or row.get("form_id")
    try:
        return _scoped_index()[str(form_id)]
    except KeyError as exc:
        raise ValueError(f"unresolved scoped form: {form_id}") from exc


def scoped_summary(row: dict[str, Any], catalog: Any = None) -> str:
    source = _source_row(row)
    return scoped_summary_zh(source, _base_index()[source["base_form_id"]])


def scoped_detail(row: dict[str, Any], catalog: Any = None) -> str:
    source = _source_row(row)
    base = _base_index()[source["base_form_id"]]
    agu = base.get("agu")
    agu_detail = ""
    if isinstance(agu, dict):
        signed = "符号扩展" if agu.get("signed_load") else "零扩展或按完整宽度写回"
        result_rule = (
            f"；load 结果按 {signed} 处理" if "Load" in str(agu.get("action")) else ""
        )
        agu_detail = (
            f"<li>AGU 契约：<code>{escape(str(agu['action']))}</code>，{escape(str(agu['address_kind']))} 地址模式，"
            f"访问 {agu['size_bytes']} 字节，偏移缩放 2^{agu['offset_scale']}，更新模式 "
            f"<code>{escape(str(agu['update_mode']))}</code>{escape(result_rule)}。</li>"
        )
    operands = "".join(
        f"<tr><td><code>{escape(o['field'])}</code></td><td>{escape(role_zh(o['role']))}</td></tr>"
        for o in source["operands"]
    )
    constraints = "".join(
        f"<li><code>{escape(str(item.get('field')))}</code> {escape(str(item.get('operator')))} "
        f"<code>{escape(str(item.get('values', item.get('value', ''))))}</code></li>"
        for item in source.get("constraints", [])
    )
    constraint_section = (
        f"<h3>编码约束</h3><ul>{constraints}</ul>" if constraints else ""
    )
    return (
        '<section class="scoped-contract"><h2>带作用域标量操作</h2>'
        f"<p>{escape(scoped_summary_zh(source, base))}</p><dl>"
        f"<dt>汇编形式</dt><dd><code>{escape(source['asm'])}</code></dd>"
        f"<dt>GM 共享属性</dt><dd><code>{escape(source['scope'])}</code>（编码 {source['scope_code']}，{SCOPE[source['scope']]}）。这是共享请求，不是单独的可见性禁止规则。</dd>"
        f"<dt>语义处理器</dt><dd><code>{escape(source['semantic_handler'])}</code></dd>"
        f"<dt>基础形式</dt><dd><code>{escape(source['base_form_id'])}</code></dd>"
        f"<dt>契约状态</dt><dd><code>{escape(source['status'])}</code></dd></dl>"
        "<h3>生命周期与异常</h3><ul>"
        "<li>外层载体固定为 8 字节。发射前快照源操作数、ACR 身份、源 TPC、地址、共享属性以及 store/atomic 数据。</li>"
        "<li>完成前保持发射上下文。Blocked 表示访问未生效，已捕获请求可重新发射。</li>"
        "<li>只有 Committed 才写目的寄存器或地址回写，并把 TPC 更新为捕获的源 TPC + 8。</li>"
        "<li>对齐或页异常报告第一或第二次访问的实际 fault 地址。PCR 形式以载体起始 TPC 向下对齐到 4 字节后的地址为基址。</li>"
        "<li>Reg5 队列源只快照、不消费。队列目的仅在提交完成后 push；绑定必须精确匹配 core、agent、invocation 和 ACR，请求 pending 时不得替换。</li>"
        f"{agu_detail}"
        f"</ul><h3>外层字段</h3><table><tbody>{operands}</tbody></table>{constraint_section}"
        f"<details><summary>英文规范摘要</summary><p>{escape(source['semantic_summary'])}</p></details>"
        f'<p class="source">来源：<code>{SCOPED_SAIL}</code>；表单 <code>{escape(source["form_id"])}</code>。</p></section>'
    )


def _manual_op(op: dict[str, Any]) -> dict[str, Any]:
    name = str(op.get("name") or op.get("mnemonic"))
    try:
        manual = _tile_index()[name]
    except KeyError as exc:
        raise ValueError(f"unresolved PTO 0.59.1 Tile operation: {name}") from exc
    normative = {
        r["name"]: r
        for r in tagged_json("isa/v0.59/state/pto_tile_operations.json")["operations"]
    }[name]
    for field in (
        "engine",
        "family",
        "function",
        "semantic_handler",
        "legality_handler",
    ):
        if op.get(field) != normative.get(field):
            raise ValueError(f"non-normative Tile record for {name}: {field}")
    return manual


def tile_summary(op: dict[str, Any], catalog: Any = None) -> str:
    _manual_op(op)
    return str(_tile_zh_index()[op["name"]]["roles"]["purpose"]["statements"][0])


def _items(title: str, values: list[str]) -> str:
    if not values:
        return ""
    return (
        f"<h3>{escape(title)}</h3><ul>"
        + "".join(f"<li>{escape(v)}</li>" for v in values)
        + "</ul>"
    )


def tile_detail(op: dict[str, Any], catalog: Any = None) -> str:
    manual = _manual_op(op)
    contract = manual["contract"]
    operands = "".join(
        f"<tr><td><code>{escape(o['field'])}</code></td><td>{escape(role_zh(o['role']))}</td></tr>"
        for o in contract.get("operands", [])
    )
    selector = op.get("selector") or f"Function={op['function']}"
    zh = _tile_zh_index()[op["name"]]
    sections = []
    for role in ("mechanism", "inputs-outputs", "effects", "constraints", "example"):
        value = zh["roles"][role]
        items = "".join(
            f"<li>{escape(statement)}</li>" for statement in value["statements"]
        )
        sections.append(
            f'<section class="tile-zh-{role}"><h3>{escape(value["heading"])}</h3><ul>{items}</ul></section>'
        )
    original_sections = []
    for key, title in (
        ("legality", "Legality"),
        ("defaults", "Defaults"),
        ("state_effects", "State effects"),
        ("memory_effects", "Memory effects"),
        ("ordering", "Ordering"),
        ("exceptions", "Exceptions"),
    ):
        values = contract.get(key, [])
        if values:
            original_sections.append(
                f"<h4>{title}</h4><ul>"
                + "".join(f"<li>{escape(value)}</li>" for value in values)
                + "</ul>"
            )
    return (
        '<section class="tile-contract"><h2>Tile 操作契约</h2>'
        f"<p>{escape(tile_summary(op))}</p><dl><dt>引擎</dt><dd><code>{escape(manual['engine'])}</code>（{ENGINE[manual['engine']]}）</dd>"
        f"<dt>承载指令</dt><dd><code>{escape(op['command_mnemonic'])}</code></dd><dt>选择器</dt><dd><code>{escape(str(selector))}</code></dd>"
        f"<dt>语义处理器</dt><dd><code>{escape(op['semantic_handler'])}</code></dd>"
        f'<dt>ASL 来源</dt><dd><a href="{escape(manual["source_url"])}"><code>{escape(manual["source_path"])}</code></a></dd></dl>'
        f"<h3>操作数</h3><table><tbody>{operands}</tbody></table>"
        + "".join(sections)
        + f"<details><summary>英文规范原文</summary><p>{escape(manual['summary'])}</p>{''.join(original_sections)}</details></section>"
    )


def validate_coverage() -> list[str]:
    errors = []
    scoped = tagged_json("isa/v0.59/state/pto_scalar_forms.json")["scoped_forms"]
    ops = tagged_json("isa/v0.59/state/pto_tile_operations.json")["operations"]
    if len(scoped) != 705:
        errors.append(f"scoped count: {len(scoped)}")
    if len(ops) != 119:
        errors.append(f"Tile count: {len(ops)}")
    for row in scoped:
        try:
            _source_row(row)
        except ValueError as exc:
            errors.append(str(exc))
    for op in ops:
        try:
            _manual_op(op)
        except ValueError as exc:
            errors.append(str(exc))
    return errors
