"""Correct Chinese detail bodies for scalar pages whose older article conflicts.

The ordinary manual path keeps the tagged, human-authored Chinese article when
it agrees with the 0.59.1 contract.  This module handles the smaller set where
that article has a known semantic or operand conflict.  Its prose comes from
the reviewed Chinese semantic record bound to the same published PTO form.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Any, Mapping

try:
    from manual_prose_zh import polish
except ModuleNotFoundError:
    from tools.isa.manual_prose_zh import polish


ROOT = Path(__file__).resolve().parents[2]
SEMANTICS = (
    ROOT / "docs/architecture/isa-manual/reference/data/manual-semantics-zh.json"
)
ROLE_ORDER = (
    ("purpose", "说明"),
    ("mechanism", "工作方式"),
    ("inputs-outputs", "操作数与结果"),
    ("effects", "架构效果"),
    ("constraints", "使用约束"),
    ("example", "示例"),
)
CURRENT_FAMILIES = {"AGU", "BRU", "SYS"}
CURRENT_COMMANDS = {
    "B.DATR",
    "B.IOS",
    "B.IOT",
    "BSTART",
    "BSTART.FP",
    "BSTART.STD",
    "BSTART.SYS",
}
NON_TILE_STARTS = {
    "BSTART",
    "BSTART.FP",
    "BSTART.ICALL",
    "BSTART.STD",
    "BSTART.SYS",
}


@lru_cache(maxsize=1)
def _records() -> Mapping[str, Mapping[str, Any]]:
    payload = json.loads(SEMANTICS.read_text(encoding="utf-8"))
    if payload.get("schema") != "linxisa.manual.semantics-zh.v1":
        raise ValueError("unexpected Chinese scalar semantics schema")
    return payload["forms"]


def _source_id(row: Mapping[str, Any], source: Mapping[str, Any] | None) -> str:
    if source and source.get("form_id"):
        return str(source["form_id"])
    value = row.get("pto_base_form_id") or row.get("pto_source_form_id")
    return str(value or "")


def _keep(statement: str) -> bool:
    """Drop provenance boilerplate while retaining architectural content."""
    return not (
        "只用于说明" in statement
        or "只说明如何使用本页" in statement
        or "本示例说明如何" in statement
        or "只演示" in statement
        or "不替代规范" in statement
        or "ASL" in statement
        or "规范汇编" in statement
        or "在寄存器偏移形式中同名意味着" in statement
        or "位移量为 0" in statement
        or "当前所有者" in statement
        or "当前 ASL" in statement
        or "目录记录" in statement
        or "处理程序" in statement
        or "派发代码" in statement
        or "模型状态" in statement
        or "模型中存在" in statement
        or "契约返回" in statement
        or "MaintenanceUsesOperand" in statement
        or "MaintenanceAccessPermitted" in statement
        or "Handler " in statement
        or "NormalizeScalar" in statement
        or "ScalarAGU" in statement
        or "记录的读者" in statement
        or "建模缓存" in statement
        or re.search(r"[A-Za-z]+(?:Returns|Requires|Uses|Handler)[A-Za-z]*", statement)
    )


def _humanize(statement: str) -> str:
    statement = statement.replace("契约规定其", "执行时，")
    statement = statement.replace("保留其历史含义", "表示该源可在后续块中继续复用")
    statement = statement.replace("hand T", "目标 T")
    statement = re.sub(r"Maintenance_[A-Z0-9_]+", "该维护操作", statement)
    return polish(statement)


def _precise_operation(source: Mapping[str, Any] | None) -> str:
    if not source or not source.get("agu"):
        return ""
    agu = source["agu"]
    if agu["address_kind"] != "Immediate" or not str(agu["action"]).startswith("Store"):
        return ""
    scale = int(agu["offset_scale"])
    displacement = (
        "符号扩展后的立即数直接作为字节位移，不缩放"
        if scale == 0
        else f"符号扩展后的立即数乘以 {1 << scale}，得到字节位移"
    )
    update = {
        "None": "有效地址是 SrcR 与该字节位移之和；本形式不回写基址。",
        "PreIndex": "先把 SrcR 与该字节位移相加；所得新基址既作为有效地址，也在存储成功后写入 RegDst。",
        "PostIndex": "本次存储使用原 SrcR 作为有效地址；存储成功后，再把 SrcR 与该字节位移之和写入 RegDst。",
    }[agu["update_mode"]]
    action = (
        f"从 SrcD 取低 {agu['size_bytes']} 字节，按小端序写入有效地址。"
        if agu["action"] == "Store"
        else f"从 SrcD、SrcD1 依次取低 {agu['size_bytes']} 字节，按小端序写入有效地址及其后一个单元。"
    )
    return f"{displacement}。{update}\n\n{action}"


def _render(record: Mapping[str, Any], source: Mapping[str, Any] | None) -> str:
    asm = str((source or {}).get("asm") or record["mnemonic"])
    encodings = (source or {}).get("encoding", ())
    matches = "、".join(str(item["match"]) for item in encodings)
    identity = f"；固定匹配值为 {matches}" if matches else ""
    sections: list[str] = [f"## 汇编写法\n\n`{asm}`{identity}。"]
    roles = record["roles"]
    for role, heading in ROLE_ORDER:
        precise = _precise_operation(source) if role == "mechanism" else ""
        if role == "mechanism" and precise:
            statements = []
        else:
            statements = [
                _humanize(str(value))
                for value in roles[role]["statements"]
                if _keep(str(value))
            ]
        if role == "mechanism":
            if precise:
                statements.insert(0, precise)
        if not statements:
            continue
        sections.append(f"## {heading}\n\n" + "\n\n".join(statements))
    return "\n\n".join(sections)


def _special_bstart(row: Mapping[str, Any]) -> str | None:
    mnemonic = str(row["mnemonic"])
    asm = str(row["asm"])
    if mnemonic == "HL.BSTART CALL":
        return (
            f"## 汇编写法\n\n`{asm}`。\n\n"
            "## 说明\n\n这条 48 位融合调用指令结束当前块、开始新的标准块，并同时计算调用目标和返回地址。"
            "两个标签各自拥有独立的重定位项。\n\n"
            "## 地址计算\n\n设 P 为本指令承载字的起始地址。调用目标为 "
            "P + (SignExtend(simm25) << 1)，返回地址为 "
            "(P + 4) + (ZeroExtend(uimm5) << 1)。返回地址写入 ra。"
        )
    if mnemonic in {"L.BSTART.FP", "L.BSTART.STD"} and " CALL" in asm:
        kind = "浮点" if mnemonic.endswith(".FP") else "标准"
        return (
            f"## 汇编写法\n\n`{asm}`。\n\n"
            f"## 说明\n\n这条 64 位指令结束当前块，以 CALL 转移开始新的{kind}块。\n\n"
            "## 返回地址\n\n该形式不会改写 ra。需要返回的调用必须在此前执行 SETRET 或 "
            "C.SETRET，并显式给出返回标签。"
        )
    return None


def _linx_bstart(row: Mapping[str, Any]) -> str | None:
    mnemonic = str(row["mnemonic"])
    if "BSTART" not in mnemonic or row.get("pto_source_form_id"):
        return None
    asm = str(row["asm"])
    if ".FP" in mnemonic:
        kind = "浮点"
    elif ".SYS" in mnemonic:
        kind = "系统"
    else:
        kind = "标准"
    transfer = next(
        (
            name
            for name in ("FALL", "DIRECT", "COND", "CALL", "IND", "RET")
            if name in asm
        ),
        "固定",
    )
    fields = sorted(
        {
            str(field["name"])
            for part in row.get("encoding", {}).get("parts", [])
            for field in part.get("fields", [])
        }
    )
    field_text = (
        "编码字段为 " + "、".join(fields) + "。"
        if fields
        else "该形式没有可变编码字段。"
    )
    note = str(row.get("note", ""))
    note_text = ""
    if "preserves ra" in note:
        note_text = "该 CALL 形式不改写 ra；需要返回时必须预先用 SETRET 或 C.SETRET 设置返回标签。"
    return (
        f"## 汇编写法\n\n`{asm}`。\n\n"
        f"## 说明\n\n这条 {row['length_bits']} 位块边界指令结束当前块，建立新的{kind}块描述符。"
        f"本 form 明确选择 {transfer} 转移。\n\n"
        f"## 编码操作数\n\n{field_text}\n\n"
        "## 架构效果\n\n成功执行后，后续指令按新块描述符解释。"
        + ("\n\n" + note_text if note_text else "")
    )


def scalar_body(
    row: Mapping[str, Any],
    source: Mapping[str, Any] | None,
    article: Any | None,
) -> str | None:
    """Return an accurate replacement body for one conflicting scalar page.

    ``None`` deliberately means that the caller should retain its authored
    Chinese body.  Vector and Tile material is owned by their dedicated review
    paths and is never rewritten here.
    """
    mnemonic = str(row["mnemonic"])
    manual = _special_bstart(row)
    if manual is not None:
        return manual
    manual = _linx_bstart(row)
    if manual is not None:
        return manual
    family = str((source or {}).get("semantic_family", ""))
    command_is_owned = family == "CMD" and (
        not mnemonic.startswith("BSTART.") or mnemonic in NON_TILE_STARTS
    )
    if not (
        article is not None
        and (
            article.classification == "conflicting-current"
            or family in CURRENT_FAMILIES
            or command_is_owned
            or mnemonic in CURRENT_COMMANDS
        )
    ):
        return None
    form_id = _source_id(row, source)
    record = _records().get(form_id)
    if record is None:
        raise ValueError(f"{mnemonic}: no reviewed Chinese semantics for {form_id}")
    if record["mnemonic"] != mnemonic:
        raise ValueError(
            f"{mnemonic}: Chinese semantics record names {record['mnemonic']}"
        )
    return _render(record, source)


__all__ = ["scalar_body"]
