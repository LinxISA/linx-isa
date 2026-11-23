#!/usr/bin/env python3
"""Short, operation-specific Chinese notes for Tile and typed BSTART indexes."""

from __future__ import annotations
from functools import lru_cache
import json, re
from pathlib import Path
from typing import Any, Mapping

try:
    from manual_tag import tagged_json
except ModuleNotFoundError:
    from tools.isa.manual_tag import tagged_json

ROOT = Path(__file__).resolve().parents[2]
ZH_PATH = (
    ROOT / "docs/architecture/isa-manual/reference/data/manual-tile-semantics-zh.json"
)

_ATOMIC = {
    "EXCH": "原子交换",
    "MAX": "原子最大值",
    "MIN": "原子最小值",
    "ADD": "原子加法",
    "INC": "原子受限自增",
    "DEC": "原子受限自减",
    "AND": "原子按位与",
    "OR": "原子按位或",
    "XOR": "原子按位异或",
}


@lru_cache(maxsize=1)
def _owners() -> dict[str, dict[str, Any]]:
    return json.loads(ZH_PATH.read_text(encoding="utf-8"))["operations"]


@lru_cache(maxsize=1)
def _operations() -> dict[str, dict[str, Any]]:
    return {
        row["name"]: row
        for row in tagged_json("isa/v0.59/state/pto_tile_operations.json")["operations"]
    }


def _name(value: str | Mapping[str, Any]) -> str:
    return (
        value
        if isinstance(value, str)
        else str(value.get("name") or value.get("mnemonic"))
    )


def tile_index_note(value: str | Mapping[str, Any]) -> str:
    name = _name(value)
    if name not in _operations() or name not in _owners():
        raise ValueError(f"unknown PTO 0.59.1 Tile operation: {name}")
    if name == "MGATHER":
        return "MGATHER：将各有效索引的字节位移加到基址，从相应内存地址读取数据，写入本地目标 Tile。"
    if name == "MGATHER_MASK":
        return "MGATHER_MASK：仅在谓词为 1 的索引位置读取数据；谓词为 0 的位置不生成地址，也不触发访存异常。"
    if name == "MGATHER_CAS":
        return "MGATHER_CAS：对各有效索引指定的内存位置执行比较交换，并将观察到的旧值写入本地目标 Tile。"
    if name.startswith("MGATHER_"):
        op = name.removeprefix("MGATHER_")
        return f"{name}：在各有效索引指定的内存位置执行{_ATOMIC[op]}，将旧值写入本地目标 Tile。"
    if name == "MSCATTER":
        return (
            "MSCATTER：按索引给出的字节位移把活动源元素写入 GM；不分配或发布目的 Tile。"
        )
    if name == "MSCATTER_MASK":
        return "MSCATTER_MASK：仅写入谓词为 1 的索引位置；谓词为 0 的位置不生成地址或内存事件。"
    if name == "MSCATTER_POPC":
        return "MSCATTER_POPC：每个活动索引对对应 GM U32 字执行一次原子加一；不读取 ValueTile，也不返回结果。"
    if name.startswith("MSCATTER_"):
        op = name.removeprefix("MSCATTER_")
        return f"{name}：在各有效索引指定的内存位置执行{_ATOMIC[op]}，不返回旧值，也不发布目的 Tile。"
    purpose = str(_owners()[name]["roles"]["purpose"]["statements"][0])
    first = re.split(r"(?<=。)", purpose, maxsplit=1)[0].strip()
    return first or purpose


def command_index_notes() -> dict[str, str]:
    result = {}
    for name, operation in _operations().items():
        command = str(operation["command_mnemonic"])
        if command != "BSTART.TEPL":
            result[command] = tile_index_note(name)
    return dict(sorted(result.items()))


def validate_tile_index_notes() -> list[str]:
    errors = []
    notes = {name: tile_index_note(name) for name in _operations()}
    if len(notes) != 119:
        errors.append(f"Tile note count {len(notes)} != 119")
    for name, note in notes.items():
        if name not in note or not re.search(r"[\u4e00-\u9fff]", note):
            errors.append(f"{name}: note is not operation-specific Chinese")
    return errors


__all__ = ["tile_index_note", "command_index_notes", "validate_tile_index_notes"]
