"""Prepare current-edition Chinese prose for the LinxISA golden manual.

This pass is deliberately narrow. It removes known version/editorial
boilerplate while retaining useful explanations, examples, pseudocode,
diagrams and current legality notes.
"""

from __future__ import annotations

import re


_HEADING = re.compile(r"^(#{2,6})\s+(.+?)\s*$", re.MULTILINE)
_SUPPLEMENT_META = re.compile(r"^<!-- LINXISA-SUPPLEMENT: .*?-->\s*", re.DOTALL)
_SUPPLEMENT_BANNER = re.compile(
    r"^>\s*\*\*0\.59\.1 增补\*\*\s*$|"
    r"^本页按 0\.59\.1 发布来源说明当前行为、合法性和异常边界。\s*$",
    re.MULTILINE,
)
_INSTSET_LINK = re.compile(r"\[([^]]+)\]\([^)]*(?:/|^)instset/[^)]*\)", re.IGNORECASE)
_CLASSIFICATION = re.compile(
    r"^(?:\s*(?:[-*+]\s*)?(?:\d+\.\s*)?)?"
    r"(?:本指令|该指令)属于[^\n]*(?:指令集|指令扩展|扩展)[^\n]*$",
    re.MULTILINE,
)
_STALE_BLOCK = re.compile(
    r"旧版|旧模型|旧中文|历史(?:说明|实现|页面|原文)|早期(?:版本|实现)|"
    r"原页|原稿|当时尚未|迁移(?:说明|路径)|兼容拼写|待审|TODO|deprecated|legacy",
    re.IGNORECASE,
)

_CURRENT_WORDING = (
    ("在 0.59.1 中只保留编码和", "仅预留编码和"),
    (
        "处理程序把原始字段与该偏移存入目标的范围记录",
        "指令把原始字段与该偏移存入目标的范围记录",
    ),
    ("因为该处理程序不写自己的 TPC", "随后 TPC 按指令长度前进"),
    (
        "固定位仍在处理程序运行之前完成校验",
        "固定位仍在读取操作数之前完成校验",
    ),
    ("不能从处理程序来源的执行进入", "不能从异常处理入口进入"),
    ("以及处理程序进入", "以及从异常处理入口进入"),
    (
        "无论是指令束中编码的还是注入模型的",
        "无论来自指令束还是平台状态",
    ),
    (
        "该描述符由 SetBundleFixedPointAttributeState 写入；见属性模式模型。",
        "该描述符由 B.FPATR 写入当前指令束的定点属性状态。",
    ),
    ("ASL 注释指出 U8 不是 S8 的同义词。", "U8 与 S8 是两个不同的数据类型编码。"),
    ("FenceData 不触碰内存", "该屏障本身不触碰内存"),
    ("ZeroExtend(uimm11)", "无符号扩展后的 uimm11"),
    (
        "因为处理程序根据行起点以 32 字节为单位推导每个写者的偏移",
        "因为每个写者的偏移按行起点、以 32 字节为单位推导",
    ),
    (
        "BundleTIMG2COLAbortFailedAttempt 中止 Shared 代或回滚 Local 目标",
        "该次尝试会中止 Shared 代或回滚 Local 目标",
    ),
    (
        "GMOVDataTypeLegal 恰好接受 TileCarrierOrPackedBaselineDataTypeSupported 允许的类型：",
        "GMOV 接受的数据类型包括：",
    ),
    ("（TileOperandsLegal_GMOV）", ""),
    (
        "与 atom/red、gather 和 scatter 分派器不同，ExecuteBundleGMOVOperation 没有零掩码提前返回，因此",
        "零掩码不会跳过预检，因此",
    ),
    (
        "StoreConditional 成功所需的 _ReservationValid 状态",
        "SC 成功所需的本地保留有效状态",
    ),
    (
        "在活动 SYS 块体之外的尝试会引发 Fault_BundleControl 并在处理程序之前返回",
        "在活动 SYS 块体之外的尝试会在产生指令效果前引发 Fault_BundleControl",
    ),
)

_BIOR_CURRENT = """# B.IOR

## 说明

`B.IOR` 把绝对 GPR 选择器绑定到当前指令束。每条记录最多携带三个输入和一个输出；具体操作决定消费哪些槽位及其角色。执行 `B.IOR` 只登记选择器，所选操作在提交时读取输入并发布输出。

## 汇编语法

```asm
B.IOR [<gpr>[, <gpr>[, <gpr>]]][, -><gpr>][, ExecMaskPresent]
```

## 选择器

`RegSrc0`、`RegSrc1`、`RegSrc2` 与 `RegDst` 只接受绝对 GPR 选择器 0 至 23。编码 0 表示架构零寄存器，不表示省略字段。编码 24 至 31 保留，并在改变任何绑定状态之前引发 `Fault_IllegalInstruction`；T/U 相对队列选择器不适用于 `B.IOR`。

省略整条 `B.IOR` 时，操作使用自身定义的默认值。已经编码的零选择器仍是实际的 GPR0。例如 TLOAD/TSTORE 省略 `B.IOR` 会采用基址零和由列数、数据类型推导的紧密行跨距；显式 `RegSrc1=zero` 则把行跨距设为零。

## 索引 TLSU 范围

MGATHER、MSCATTER 及其掩码和原子形式必须显式提供 `B.IOR`。第一条记录的 `RegSrc0` 是无符号 GM 基地址，`RegDst` 为 zero。

- 第一条记录未设置 `ExecMaskPresent` 且 `(RegSrc1, RegSrc2)=(zero, zero)` 时，不声明范围描述符。
- 其他合法的 `RegSrc1`、`RegSrc2` 选择器分别读取完整的 S64 `MinIndex` 和 `MaxIndex`，表示相对基址的有符号字节位移上下界。
- 同时使用范围描述符和 GPR 执行掩码时，第一条记录写 Base/Min/Max 且不设置标志；紧接的第二条记录提供一至两个掩码字，只有最后一条记录设置 `ExecMaskPresent`。
- 第一条记录直接设置 `ExecMaskPresent` 时，保留单记录 Base 加 GPR 掩码的定义，不把 `RegSrc1`、`RegSrc2` 解释为范围。

对参与执行的当前 PE，`MinIndex > MaxIndex` 会在该请求的索引访存和目标 Tile 效果之前引发 `Fault_TileLegality`。已经提交的其他 PE 效果不回滚。

## 其他多记录形式

普通操作至多使用一条 `B.IOR`。TGPR2T、TIMG2COL 以及允许 GPR 执行掩码的 Local CUBE 形式可使用紧邻的第二条记录。第二条记录只能携带源；输出只允许出现在第一条记录。`ExecMaskPresent` 只能位于实际携带 GPR 执行掩码的最后一条记录上。

## 示例

只提供索引基址、不声明范围：

```asm
B.IOR a0, zero, zero, ->zero
```

提供索引范围：

```asm
B.IOR a0, a1, a2, ->zero
```

其中 a0 是 BaseGPR，a1、a2 分别保存 S64 MinIndex、MaxIndex。

范围描述符与两字 GPR 执行掩码同时使用：

```asm
B.IOR a0, a1, a2, ->zero
B.IOR a3, a4, zero, ->zero, ExecMaskPresent
```

多余、错位、不连续或操作 schema 不消费的记录和非零字段会在操作效果之前引发块控制或 Tile 合法性故障。
"""

_BIOR_CONSTRAINTS = (
    "RegSrc0、RegSrc1、RegSrc2 与 RegDst 只接受绝对 GPR 选择器 0 至 23；编码 24 至 31 在改变绑定状态之前引发 Fault_IllegalInstruction。",
    "B.IOR 只能出现在 BSTART 之后、块体开始之前。多余、错位、不连续或 schema 不消费的记录和非零字段会在操作效果之前引发 Fault_BundleControl 或 Fault_TileLegality。",
    "ExecMaskPresent 只允许在实际携带 GPR ExecutionMask 的最后一条连续记录上置位；此前记录、无掩码形式和谓词 Tile 掩码形式必须清零。",
    "索引 TLSU 的第一条 B.IOR 以 RegSrc0 绑定 BaseGPR。未携带单记录 GPR 掩码时，RegSrc1 与 RegSrc2 同为 zero 表示不声明范围；其他合法选择器分别绑定完整的 S64 MinIndex 与 MaxIndex。",
    "范围描述符与 GPR ExecutionMask 同时使用时，第一条记录绑定 Base/Min/Max 且标志为零，紧接的第二条记录携带掩码字并在最后一条记录设置 ExecMaskPresent；RegDst 为 zero。",
    "参与执行的当前 PE 若 MinIndex 大于 MaxIndex，会在该请求的索引访存和目标 Tile 效果之前引发 Fault_TileLegality；其他 PE 已提交的效果不回滚。",
)

_INDEXED_BIOR = (
    "B.IOR 必须显式提供 RegSrc0 作为 BaseGPR。RegDst 为 zero。"
    "未携带单记录 GPR 执行掩码时，RegSrc1、RegSrc2 同为 zero 表示不声明范围；"
    "其他合法选择器分别绑定完整的 S64 MinIndex 和 MaxIndex。"
    "范围描述符与 GPR 执行掩码同时使用时，第一条记录绑定 Base/Min/Max 且不设置标志，"
    "紧接的第二条记录携带掩码字，并只在最后一条记录设置 ExecMaskPresent。"
)

_STALE_INDEXED_BIOR = re.compile(
    r"(?:B\.IOR\s*是必需的[^。；\n]*[，；]\s*)?"
    r"(?:且[^。；\n]*[，；]\s*)?"
    r"RegSrc1[、,，]\s*RegSrc2[^。；\n]{0,80}RegDst[^。；\n]{0,40}(?:为|编码为|保持为|必须为|均为)零[。；]?"
)


def _sections(markdown: str) -> list[tuple[str, str, str]]:
    matches = list(_HEADING.finditer(markdown))
    if not matches:
        return [("", "", markdown)]
    result = [("", "", markdown[: matches[0].start()])]
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        result.append((match.group(1), match.group(2), markdown[match.start() : end]))
    return result


def _drop_stale_paragraphs(value: str) -> str:
    blocks = re.split(r"(\n\s*\n)", value)
    kept: list[str] = []
    for block in blocks:
        if not block.strip() or re.fullmatch(r"\n\s*\n", block):
            kept.append(block)
            continue
        if _CLASSIFICATION.search(block) or _STALE_BLOCK.search(block):
            continue
        kept.append(block)
    return "".join(kept)


def _remove_empty_sections(markdown: str) -> str:
    kept: list[str] = []
    for marks, heading, section in _sections(markdown):
        if not marks:
            if section.strip():
                kept.append(section.strip())
            continue
        body = section.split("\n", 1)[1] if "\n" in section else ""
        if body.strip():
            kept.append(f"{marks} {heading}\n{body.strip()}")
    return "\n\n".join(kept).strip() + "\n"


def _supplement(markdown: str) -> str:
    markdown = _SUPPLEMENT_META.sub("", markdown)
    markdown = _SUPPLEMENT_BANNER.sub("", markdown)
    sections = []
    for marks, heading, section in _sections(markdown):
        if marks and re.fullmatch(r"0\.59\.1\s+来源", heading.strip()):
            continue
        sections.append(section)
    return "\n\n".join(part.strip() for part in sections if part.strip()) + "\n"


def golden_markdown(path: str, markdown: str) -> str:
    """Return current architectural prose without migration/editorial residue."""
    normalized = path.replace("\\", "/")
    if normalized.endswith("/B.IOR.md"):
        return _BIOR_CURRENT
    if "/supplements/" in path.replace("\\", "/"):
        markdown = _supplement(markdown)
    for before, after in _CURRENT_WORDING:
        markdown = markdown.replace(before, after)
    markdown = _INSTSET_LINK.sub(r"\1", markdown)
    if re.search(r"(?:M|S)GATHER|MSCATTER", normalized + "\n" + markdown, re.I):
        markdown = _STALE_INDEXED_BIOR.sub(_INDEXED_BIOR, markdown)
    markdown = _drop_stale_paragraphs(markdown)
    return _remove_empty_sections(markdown)


def golden_constraints(
    mnemonic: str, statements: list[str] | tuple[str, ...]
) -> tuple[str, ...]:
    """Return current constraint prose for generated definition panels."""
    if mnemonic == "B.IOR":
        return _BIOR_CONSTRAINTS
    if mnemonic.startswith(
        ("MGATHER", "MSCATTER", "BSTART.MGATHER", "BSTART.MSCATTER")
    ):
        kept = tuple(
            statement
            for statement in statements
            if not _STALE_INDEXED_BIOR.search(statement)
        )
        if not any(
            "MinIndex" in statement and "MaxIndex" in statement for statement in kept
        ):
            kept += (_INDEXED_BIOR,)
        return kept
    return tuple(statements)


__all__ = ["golden_constraints", "golden_markdown"]
