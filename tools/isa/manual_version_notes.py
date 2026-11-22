"""Edition differences verified against the 0.59.1 indexed Tile contracts."""

from html import escape

# The base authored MGATHER/MSCATTER drawings illustrate an ordinary unmasked
# transfer. Every variant retains that article, and gets its own selector note.
_ATOMIC = {
    "CAS": "比较并交换",
    "EXCH": "交换",
    "MAX": "取最大值",
    "MIN": "取最小值",
    "ADD": "加法",
    "INC": "递增",
    "DEC": "递减",
    "AND": "按位与",
    "OR": "按位或",
    "XOR": "按位异或",
    "POPC": "计数",
}


def indexed_transfer_note(op, owners):
    name = op["name"]
    family, _, suffix = name.partition("_")
    if family not in {"MGATHER", "MSCATTER"}:
        return ""
    owner = owners[name]
    contract = owner["contract"]
    facts = []
    if suffix == "MASK":
        facts.append(
            f"{name} 按掩码选择参与访问的元素。下方《{family}》原页的循环没有掩码步骤。"
        )
    elif suffix:
        action = _ATOMIC[suffix]
        facts.append(
            f"{name} 对索引选出的内存位置执行原子{action}操作。《{family}》原页的普通搬运循环只解释寻址，不能代替本形式的原子操作。"
        )
    # Bind differences to actual source facts; do not spread an operation's
    # preflight or fault-atomicity contract to neighboring selectors.
    operands = " ".join(
        str(v)
        for k in ("operands", "defaults", "legality")
        for v in contract.get(k, [])
    )
    if "S32/U32/S64/U64" in operands or "S32, U32, S64, or U64" in operands:
        facts.append(
            "本版索引元素为 S32、U32、S64 或 U64，表示字节位移。原文列出的 u16 不适用于本版索引。"
        )
    if name == "MGATHER":
        facts.extend(
            [
                "地址等于 BaseGPR 加上该元素的字节位移，不再按传输元素大小缩放。B.IOR 的 RegSrc0 提供 BaseGPR，其余字段为零。",
                "普通传输的有效形状与 IndexTile 匹配。四位打包传输每次读取一个字节，数据的有效列数须为索引有效列数的两倍。允许 ROWMAJOR、CUBE_M16 和 CUBE_M32 布局。",
                "若提供范围描述符，MinIndex 和 MaxIndex 是有符号的相对字节界限。MinIndex 大于 MaxIndex 时，本次请求在产生索引访存或写入目标 Tile 之前引发 Fault_TileLegality；已提交的其他 PE 效果保留。每项起始地址在界内、整个地址区间不回绕，由软件保证。",
                "在产生第一个架构效果之前，先完成所有有效地址的预检。",
            ]
        )
    if not facts:
        return ""
    return (
        '<aside class="edition-difference"><h2>0.59.1 版本差异</h2><ul>'
        + "".join("<li>" + escape(f) + "</li>" for f in facts)
        + '</ul><p><a href="'
        + escape(owner["source_url"], quote=True)
        + '">核对本操作的发布定义</a></p></aside>'
    )


def release_constraints(source, *, base=False):
    roles = source.get("roles", {})
    statements = roles.get("constraints", {}).get("statements", [])
    if not statements:
        return ""
    label = "基础形式的约束与异常" if base else "约束与异常"
    return (
        '<details class="fault-reference"><summary>'
        + label
        + "（PTO 中文参考）</summary><ul>"
        + "".join("<li>" + escape(v) + "</li>" for v in statements)
        + "</ul></details>"
    )
