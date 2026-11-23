#!/usr/bin/env python3
"""Corrected Chinese detail prose for audited v0.59.1 vector forms."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Any, Mapping

try:
    from manual_tag import tagged_bytes
except ModuleNotFoundError:
    from tools.isa.manual_tag import tagged_bytes


ROOT = Path(__file__).resolve().parents[2]
SAIL = ROOT / "docs/architecture/isa-manual/reference/data/manual-linx-sail.json"
SECTION = re.compile(r"^## ([^\n]+)\n[\s\S]*?(?=^## |\Z)", re.MULTILINE)
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]+\)(?:\{[^}]*\})?")

SOURCE_PAGES = frozenset(
    {
        "HL.SETC.LTI",
        "HL.SETC.ORI",
        "V.CMP.AND",
        "V.CMP.ANDI",
        "V.FCVT",
        "V.FCVTI",
        "V.ICVT",
        "V.ICVTF",
        "V.LD.MIN",
        "V.REV",
        "V.SH.BRG",
        "V.SW.BRG",
        "V.SD.BRG",
    }
)
BITFIELD = frozenset({"V.BCNT", "V.BIC", "V.BIS", "V.BXS", "V.BXU", "V.CLZ", "V.CTZ"})
ATOMIC = re.compile(r"^V\.(?:LW|LD|SW|SD)\.(?:ADD|AND|MAX|MIN|OR|XOR)$")


def vector_body(
    row: Mapping[str, Any], source: Mapping[str, Any] | None, article: Any
) -> str | None:
    """Return reviewed Markdown for one vector-family form."""
    del source
    mnemonic = str(row["mnemonic"])
    if mnemonic in SOURCE_PAGES:
        if article is None:
            raise ValueError(f"{mnemonic}: missing Chinese source page")
        return (ROOT / article.source_path).read_text(encoding="utf-8")
    replacement = (
        _brg_body(row)
        or _shuffle_body(mnemonic)
        or _bitfield_body(row)
        or _atomic_body(row)
    )
    if replacement is not None:
        return replacement
    if mnemonic.startswith("V.") and article is not None:
        return _revise_authored_article(row, article)
    return None


def corrected_mnemonics() -> frozenset[str]:
    return SOURCE_PAGES


@lru_cache(maxsize=1)
def _sail() -> Mapping[str, Any]:
    payload = json.loads(SAIL.read_text(encoding="utf-8"))
    if payload.get("schema") != "linxisa.manual.linx-only-sail.v1":
        raise ValueError("unexpected Linx Sail manual schema")
    return payload


def _handler_text(row: Mapping[str, Any]) -> str:
    sail = _sail()
    form = sail["forms"].get(str(row["id"]))
    if form is None:
        raise ValueError(f"{row['id']}: missing published Sail record")
    seen: set[str] = set()
    excerpts: list[str] = []

    def add(name: str) -> None:
        if name in seen:
            return
        seen.add(name)
        handler = sail["handlers"].get(name)
        if handler is None:
            raise ValueError(f"{row['id']}: missing Sail handler {name}")
        excerpt = str(handler["excerpt"])
        excerpts.append(excerpt)
        for nested in re.findall(r"\b(exec_v_[a-z0-9_]+)\s*\(", excerpt):
            add(nested)

    for helper in form["helpers"]:
        add(str(helper))
    return "\n".join(excerpts)


def _execution_note(row: Mapping[str, Any]) -> str:
    mnemonic = str(row["mnemonic"])
    handler = _handler_text(row)
    fields = {
        str(field["name"])
        for part in row["encoding"]["parts"]
        for field in part["fields"]
    }
    if mnemonic == "V.PSEL":
        return (
            "发布 Sail 不读取 P 掩码。每个向量通道读取同一通道的 `SrcP`：其值非零时选择 "
            "`SrcL`，为零时选择 `SrcR`；`neg` 置位时先对 `SrcR` 取二进制补码负值。"
        )
    if mnemonic.startswith("V.RD"):
        empty = {
            "V.RDAND": "没有活动通道时得到该整数类型的全 1 恒等值。",
            "V.RDFMAX": "没有活动通道时写入规范 quiet NaN `0x7fc00000`。",
            "V.RDFMIN": "没有活动通道时写入规范 quiet NaN `0x7fc00000`。",
        }.get(mnemonic, "没有活动通道时写入 0。")
        return (
            "发布 Sail 只把 P 掩码为 1 的通道纳入归约，P 掩码为 0 的通道不参与。"
            "归约结束后只写一次标量目的寄存器。" + empty
        )
    if "RegDst" not in fields:
        return "发布 Sail 仅对 P 掩码为 1 的通道执行操作；其他通道不产生内存、队列或目的寄存器效果。"
    if "undefined_bitvector" in handler:
        return (
            "发布 Sail 对 P 掩码为 1 的通道执行上述运算。P 掩码为 0 的目的通道结果未指定，"
            "软件不能假定它被写成 0 或保留原值。"
        )
    if "var out = read_" in handler:
        return "发布 Sail 对 P 掩码为 1 的通道执行上述运算；P 掩码为 0 的目的通道保持原值。"
    raise ValueError(f"{mnemonic}: unclassified published Sail lane behavior")


def _revise_authored_article(row: Mapping[str, Any], article: Any) -> str:
    markdown = tagged_bytes(article.source_path).decode("utf-8")
    matches = [
        match
        for match in SECTION.finditer(markdown)
        if match.group(1).strip().rstrip("：:") == "执行方式"
    ]
    if len(matches) != 1:
        raise ValueError(f"{row['mnemonic']}: expected one authored execution section")
    match = matches[0]
    figures = IMAGE.findall(match.group(0))
    replacement = "## 执行方式\n\n" + _execution_note(row) + "\n"
    if figures:
        replacement += "\n" + "\n\n".join(figures) + "\n"
    markdown = markdown[: match.start()] + replacement + markdown[match.end() :]

    def current_section(section: re.Match[str]) -> str:
        heading = section.group(1).strip().rstrip("：:")
        if heading == "汇编语法":
            return f"## 汇编语法\n\n```asm\n{row['asm']}\n```\n\n"
        if heading == "汇编符号" or (
            "编码" in heading and ("格式" in heading or "位图" in heading)
        ):
            return ""
        return section.group(0)

    return SECTION.sub(current_section, markdown)


def _bitfield_body(row: Mapping[str, Any]) -> str | None:
    mnemonic = str(row["mnemonic"])
    if mnemonic not in BITFIELD:
        return None
    action = {
        "V.BCNT": "统计该位域中 1 的个数",
        "V.CLZ": "统计该位域从最高位起连续的 0",
        "V.CTZ": "统计该位域从最低位起连续的 0",
        "V.BXU": "把该位域零扩展后写入目的通道",
        "V.BXS": "按该位域最高位做符号扩展后写入目的通道",
        "V.BIC": "把环上选中的位清零，其他位保持不变",
        "V.BIS": "把环上选中的位置一，其他位保持不变",
    }[mnemonic]
    return f"""# {mnemonic}

## 说明

本指令逐活动通道读取一个 32 位载体。位域宽度由 `Nminus1 + 1` 得到，并钳制到 32 位；起点 `M` 在 32 位环上定位，因此跨过 bit 31 时从 bit 0 继续。随后{action}。

P 掩码为 0 的目的通道结果未指定。本指令不对 64 位值执行循环移位，也没有 64 位位域语义。

## 汇编语法

```asm
{row["asm"]}
```

## 编码格式

![{mnemonic}](../../../figs/bitfield/svg/Instruction_64bit/{mnemonic}.svg)
"""


def _atomic_body(row: Mapping[str, Any]) -> str | None:
    mnemonic = str(row["mnemonic"])
    if not ATOMIC.fullmatch(mnemonic):
        return None
    width_name, bits = (
        ("字", 32) if mnemonic.startswith(("V.LW", "V.SW")) else ("双字", 64)
    )
    load = mnemonic.startswith("V.L")
    op = mnemonic.rsplit(".", 1)[1]
    operation = {
        "ADD": "相加",
        "AND": "按位与",
        "OR": "按位或",
        "XOR": "按位异或",
        "MAX": "按有符号数取较大值",
        "MIN": "按有符号数取较小值",
    }[op]
    result = (
        "每次读到的内存旧值写入相应目的元素。P 掩码为 0 的元素不访问内存，并保持目的元素原值。"
        if load
        else "本形式没有目的寄存器；P 掩码为 0 的元素不访问内存。"
    )
    suffixes = "`aq`、`far` 和 `rl`" if load else "`rl`、`far` 和 `rd`"
    return f"""# {mnemonic}

## 说明

按照 v0.59.1 发布 Sail，`SrcL` 只提供一个内存地址。处理程序按通道递增顺序遍历活动元素；每个活动元素都从同一地址读取 {bits} 位旧值，与该元素的 `SrcR` {operation}，再把结果写回同一地址。多个活动元素会连续更新同一个内存单元，后面的元素看到前面元素写回的值。

{result} 当前发布 Sail 会译码 {suffixes} 位，但处理程序不使用这些位。处理程序以显式的加载和存储描述读改写，没有给出并发观察者之间的原子互斥规则。

## 汇编语法

```asm
{row["asm"]}
```

## 编码格式

![{mnemonic}](../../../figs/bitfield/svg/Instruction_64bit/{mnemonic}.svg)

## 数据宽度

本指令固定处理一个{width_name}（{bits} 位）。发布 Sail 已明确这一宽度，不使用旧页“位宽不满足时结果不可知”的兜底说法。
"""


def _brg_body(row: Mapping[str, Any]) -> str | None:
    mnemonic = str(row["mnemonic"])
    if not (mnemonic.startswith("V.") and mnemonic.endswith(".BRG")):
        return None
    operation = mnemonic.split(".")[1]
    immediate = operation.endswith("I")
    load = operation.startswith("L")
    unsigned_load = operation in {"LBU", "LBUI", "LHU", "LHUI", "LWU", "LWUI"}
    width_letter = (
        operation.removeprefix("L" if load else "S").removesuffix("I").removesuffix("U")
    )
    width, width_name, scale = {
        "B": (8, "字节", 0),
        "H": (16, "半字", 1),
        "W": (32, "字", 2),
        "D": (64, "双字", 3),
    }[width_letter]
    if immediate:
        offset = "符号扩展后的 24 位立即数"
        offset_note = "发布 Sail 直接把立即数作为字节偏移；带 `.U` 与不带 `.U` 的立即数 BRG 都没有再次按元素宽度缩放。"
    else:
        offset = "索引向量 lane 0 的 32 位值左移 `shamt` 位"
        offset_note = ""
    base = "SrcR" if immediate and not load else "SrcL"
    address = f"`{base}`（标量基址） + (`LC0` × {width // 8}) + {offset}"
    if load:
        if width in {8, 16}:
            extension = "读取值先做零扩展" if unsigned_load else "读取值先做符号扩展"
        elif width == 32:
            extension = "读取的 32 位原样写入"
        else:
            extension = "读取的 64 位值由相邻两个 32 位通道承载"
        inactive = (
            "结果未指定" if "undefined_bitvector" in _handler_text(row) else "保持原值"
        )
        effect = f"从该地址读取一个{width_name}。{extension}，再广播到活动目的元素；非活动目的元素{inactive}。"
    elif immediate:
        data = f"低 {width} 位" if width < 64 else "一对 32 位通道组成的 64 位值"
        effect = f"按通道递增顺序把每个活动元素的{data}依次写到同一地址；多个活动元素会连续覆盖，非活动元素不写内存。"
    else:
        data = (
            f"lane 0 的低 {width} 位" if width < 64 else "lane 1、lane 0 拼成的 64 位值"
        )
        effect = f"把源数据向量 {data} 写到该地址；只使用索引 lane 0 和第一项数据，而且不读取 P 掩码。"
    gap = ""
    if not immediate and ".U.BRG" not in mnemonic and width > 8 and not load:
        gap = f"\n\n## 0.59.1 内部不一致\n\n目录汇编写 `SrcR << ({scale} + shamt)`，发布 Sail 只做 `SrcR << shamt`。0.59.1 未在两者之间裁决，不能把该差异当作已确定的硬件要求。"
    return (
        f"# {mnemonic}\n\n## 说明\n\n按照 v0.59.1 发布 Sail，本指令以 {address} 形成地址。"
        "`.local` 会被译码，但当前处理程序不使用它，也没有据此切换地址空间。"
        f"{offset_note}{effect}发布 Sail 没有旧页所述的桥接表读写。\n\n"
        f"## 汇编语法\n\n```asm\n{row['asm']}\n```\n\n"
        f"## 编码格式\n\n![{mnemonic}](../../../figs/bitfield/svg/Instruction_64bit/{mnemonic}.svg)\n"
        + gap
    )


def _shuffle_body(mnemonic: str) -> str | None:
    if not mnemonic.startswith("V.SHFL"):
        return None
    immediate = mnemonic.startswith("V.SHFLI.")
    kind = mnemonic.rsplit(".", 1)[1]
    value = "14 位无符号立即数" if immediate else "同一通道的 `SrcP` 值"
    if kind == "BFLY":
        operation = f"每个活动通道取 {value}，对当前通道数取模后与当前通道 ID 异或。结果越出当前组时读取本通道。"
        figure = "shfl.bfly.png"
    else:
        selector = {
            "DOWN": f"把 {value} 对范围取模后加到当前通道 ID",
            "UP": f"把 {value} 对范围取模后从当前通道 ID 减去",
            "IDX": f"把 {value} 对范围取模后加到当前分段起点",
        }[kind]
        operation = (
            "每个活动通道从同一通道的 `SrcR` 读取范围，范围为 0 时使用当前组通道数；"
            + selector
            + "。结果越过分段边界时读取本通道。"
        )
        figure = f"shfl.{kind.lower()}.png"
    return f"# {mnemonic}\n\n## 说明\n\n{operation}源通道的 `SrcL` 写入当前目的通道；P 掩码为 0 的结果未指定。\n\n![{mnemonic}](../../../figs/isa/inst/{figure})\n"


__all__ = ["corrected_mnemonics", "vector_body"]
