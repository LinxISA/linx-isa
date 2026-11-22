"""Chinese annotations for the block compositions in the 0.59.1 Tile catalog.

Assembly mnemonics and symbolic operand names keep their published spelling.
The page also carries the source template for direct comparison.
"""

# Whole notes are translated as units. This preserves the scope of conditions
# such as the separate RowMajor and CUBE rules for LB1 and LB2.
NOTES = {
    "optional": "可选",
    "exactly one": "必须出现一次",
    "GPR form only": "仅用于通用寄存器形式",
    "CellReg form only": "仅用于 CellReg 形式",
    "U8 GPR form only": "仅用于 U8 通用寄存器形式",
    "optional, default 1": "可选，省略时取 1",
    "optional, default ValidCol": "可选，省略时取 ValidCol",
    "optional; BType defaults to AType": "可选；省略时 BType 取 AType",
    "optional; omission selects 0 and lower": "可选；省略时对角线取 0，方向为下三角",
    "optional; omission selects 0 and ascending": "可选；省略时起始值为 0，方向为递增",
    "optional, default 1; TGEMV permits only M=1": "可选，省略时取 1；TGEMV 只允许 M=1",
    "RowMajor optional, default 1; when present must equal 1; CUBE required positive": "行主序下可省略，取值须为 1；CUBE 布局下必须给出正值",
    "RowMajor optional, default ValidCol; CUBE optional; omitted aligns ValidCol to the cell-column quantum": "行主序下可省略，默认取 ValidCol；CUBE 布局下省略时，按单元列粒度对齐 ValidCol",
    "optional; cooperative mask 1111": "可选；协作模式的掩码为 1111",
}
LINES = {
    "# Local destination": "# 目标位于本地 Tile 寄存器",
    "# Shared destination": "# 目标位于共享 Tile 寄存器",
    "B.DATR RowMajor all-zero (optional), or explicit CUBE_M32/CUBE_M16 tuple": "B.DATR  行主序参数全为 0（可省略），或显式指定 CUBE_M32/CUBE_M16 参数组",
    "B.DATR all-zero (optional)": "B.DATR  所有字段取 0（可省略）",
    "B.DIM LB0 M or cooperative group_M (optional, default 1)": "B.DIM LB0  取 M，协作模式下取 group_M（可选，省略时取 1）",
    "B.IOR predicate-GPR destination (GPR form only)": "B.IOR  指定接收谓词结果的通用寄存器（仅用于 GPR 形式）",
    "B.IOR predicate-GPR source (GPR form only)": "B.IOR  指定提供谓词的通用寄存器（仅用于 GPR 形式）",
    "B.IOR predicate-GPR source and optional scalar-false source": "B.IOR  指定提供谓词的通用寄存器，可另给谓词为假时使用的标量源",
    "B.IOR scalar-compare source and optional predicate-GPR destination": "B.IOR  指定用于比较的标量源，可另给接收谓词结果的通用寄存器",
    "B.IOS complete right or both matrix operand groups (optional; cooperative mask 1111)": "B.IOS  绑定完整的右矩阵操作数组，或同时绑定左右两组（可选；协作掩码为 1111）",
    "B.IOT D matching A's CUBE_M16/M32 layout with a distinct encoded destination index, optional RowMaxOut, optional GroupMaxOut destinations": "B.IOT  D 使用与 A 相同的 CUBE_M16/M32 布局，目标编码索引须不同；可另设 RowMaxOut 和 GroupMaxOut",
    "B.IOT D matching A's CUBE_M16/M32 layout, optional RowMaxOut, optional GroupMaxOut destinations": "B.IOT  D 使用与 A 相同的 CUBE_M16/M32 布局；可另设 RowMaxOut 和 GroupMaxOut",
    "B.IOT/B.IOR postprocess operands selected by B.FPATR": "B.IOT/B.IOR  绑定由 B.FPATR 选择的后处理操作数",
    "BSTOP or the next BSTART completion boundary": "以 BSTOP 或下一个 BSTART 作为本块的完成边界",
    "CUBE: exactly one B.IOR StartGPR, Step2DGPR, zero, ->zero": "CUBE 布局必须有一条 B.IOR StartGPR, Step2DGPR, zero, ->zero",
    "RowMajor: B.IOR Start, Direction (optional; omission selects 0 and ascending)": "行主序：B.IOR Start, Direction（可选，省略时从 0 开始递增）",
    "Local: BSTART.TSTORE DataType; optional B.DATR Layout; optional B.DIM; optional B.IOR; one source B.IOT; BSTOP": "本地源：BSTART.TSTORE DataType → B.DATR Layout（可选）→ B.DIM（可选）→ B.IOR（可选）→ 一条源绑定 B.IOT → BSTOP",
    "Shared: BSTART.TSTORE DataType; optional B.DATR/B.DIM/B.IOR; one source B.IOS with any nonzero consumer PE_MASK; optional B.SUBVIEW; BSTOP": "共享源：BSTART.TSTORE DataType → B.DATR/B.DIM/B.IOR（可选）→ 一条源绑定 B.IOS（消费方 PE_MASK 可取任意非零值）→ B.SUBVIEW（可选）→ BSTOP",
    "one terminating destination B.IOT": "以一条绑定目标寄存器的 B.IOT 结束",
    "optional B.DATR Layout": "B.DATR Layout（可选）",
    "optional B.IOR RegSrc0=base, RegSrc1=row_stride_bytes": "B.IOR RegSrc0=base, RegSrc1=row_stride_bytes（可选）",
    "replace B.IOT with one destination B.IOS": "改用一条 B.IOS 绑定目标寄存器",
}
MATRIX_SOURCES = {
    "A CUBE_M16/M32 primary": "A 主操作数（CUBE_M16/M32）",
    "B CUBE_N8 primary": "B 主操作数（CUBE_N8）",
    "C CUBE_M16/M32 accumulator matching A with encoded selector distinct from DstTile": "累加源 C（CUBE_M16/M32，布局与 A 匹配，编码选择器须与 DstTile 不同）",
    "CUBE_N8 1xN Bias": "偏置（1×N，CUBE_N8）",
    "optional A scale": "A 缩放因子（可选）",
    "optional B scale": "B 缩放因子（可选）",
    "optional U8 CScale CUBE_M32 [M,1]": "CScale（可选，U8，CUBE_M32 布局，形状为 [M,1]）",
}


def translate_line(line: str) -> str:
    if line in LINES:
        return LINES[line]
    matrix = "B.IOT ordered Local mathematical sources: "
    if line.startswith(matrix):
        # The comma inside the shape [M,1] is part of the shape, not a separator.
        names = line.removeprefix(matrix).split(", ")
        return "B.IOT  依次绑定本地源：" + "、".join(MATRIX_SOURCES[n] for n in names)
    for suffix, translation in (
        (
            " OR GPR predicate form without PredicateCell",
            "；通用寄存器谓词形式省略 PredicateCell",
        ),
        (" OR no destination", "，也可省略目标"),
    ):
        if line.endswith(suffix):
            return line.removesuffix(suffix) + translation
    if line.endswith(")"):
        operands, note = line[:-1].rsplit(" (", 1)
        return operands + "（" + NOTES[note] + "）"
    return line


def translate_block(lines: list[str]) -> list[str]:
    return [translate_line(line) for line in lines]
