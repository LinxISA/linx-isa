#!/usr/bin/env python3
"""Controlled Chinese terminology for scoped Scalar and Tile manual pages."""

from __future__ import annotations
import re
from typing import Any

try:
    from manual_prose_zh import memory_synopsis
except ModuleNotFoundError:
    from tools.isa.manual_prose_zh import memory_synopsis

SCOPE = {"Private": "私有", "IntraCore": "核内共享", "InterCore": "跨核共享"}
ENGINE = {
    "VEC": "逐元素向量引擎",
    "SFU": "复杂函数引擎",
    "TLSU": "Tile 访存引擎",
    "CUBE": "矩阵运算引擎",
}
ROLE = {
    "destination": "目的 Tile",
    "new Local destination": "新分配的本地目的 Tile",
    "source-left": "左源 Tile",
    "source-right": "右源 Tile",
    "numerator": "分子源 Tile",
    "denominator": "分母源 Tile",
    "dividend": "被除数源 Tile",
    "divisor": "除数源 Tile",
    "value-source": "数值源 Tile",
    "shift-count-source": "移位量源 Tile",
    "effective GM shareability": "实际 GM 共享属性",
    "wrapped instruction length": "内层指令长度编码",
    "EQ, NE, LT, GT, LE, or GE selected by CMode": "由 CMode 选择 EQ、NE、LT、GT、LE 或 GE 比较条件",
    "RowMajor direction or CUBE packed Step2D from RegSrc1": "来自 RegSrc1 的 RowMajor 方向或 CUBE 打包 Step2D",
    "U8 PredicateTile": "U8 谓词 Tile",
    "ValidCol": "有效列数",
    "ValidRow": "有效行数",
    "each PE's absolute peer_tid": "每个 PE 的绝对 peer_tid",
    "limit": "限制值",
    "lower or upper orientation": "上三角或下三角方向",
    "minuend": "被减数",
    "subtrahend": "减数",
    "pack-control": "打包控制",
    "shuffle-control": "重排控制",
    "unpack-control": "解包控制",
    "per-PE GM base": "每个 PE 的 GM 基址",
    "per-PE element width in bits": "每个 PE 的元素位宽",
    "per-PE private-GPR GM base address": "每个 PE 的私有 GPR GM 基地址",
    "physical Col": "物理列数 Col",
    "resolved rounding and saturation": "解析后的舍入与饱和控制",
    "signed diagonal displacement": "有符号对角线位移",
    "six-mode comparison": "六种模式比较",
    "typed sequence start from RowMajor/CUBE RegSrc0": "来自 RowMajor/CUBE RegSrc0 的类型化序列起点",
    "legacy packed Predicate, CUBE PredicateCell, or GPR mask role": "旧式打包 Predicate、CUBE PredicateCell 或 GPR 掩码角色",
    "legacy packed Predicate, CUBE PredicateCell, or first GPR-mask role": "旧式打包 Predicate、CUBE PredicateCell 或第一个 GPR 掩码角色",
    "legacy packed Predicate or CUBE PredicateCell destination; absent for GPR producer": "旧式打包 Predicate 或 CUBE PredicateCell 目的；产生 GPR 结果时不存在",
    "persistent Local row broadcast source; only the selected BroadcastSlot supplies values": "保持的本地行广播源；只有选定的 BroadcastSlot 提供数值",
    "persistent Local row broadcast source; only the selected BroadcastSlot supplies values through the BSTART operation view": "保持的本地行广播源；只有选定的 BroadcastSlot 通过 BSTART 操作视图提供数值",
    "persistent Local row broadcast source interpreted through SrcDataType; only the selected BroadcastSlot supplies values": "按 SrcDataType 解释的保持本地行广播源；只有选定的 BroadcastSlot 提供数值",
    "weight-mode packed StartGPR; inapplicable to ordinary and CUBE forms": "权重模式打包 StartGPR；普通形式和 CUBE 形式不适用",
}


ROLE.update(
    {
        "Core4 peer-resolved read-old Local source snapshot": "由 Core4 对端选择确定的本地源，读取其旧值快照",
        "Local Tile or absolute Shared S0..S63 source": "本地 Tile，或按绝对编号引用的共享源 S0 至 S63",
        "Local result destination": "保存结果的本地目标",
        "RowMajor or CUBE numeric result destination": "按 RowMajor 或 CUBE 布局存放数值结果的目标",
        "absolute-value source": "用于求绝对值的源操作数",
        "accumulator": "累加源",
        "base-address": "基地址",
        "bias": "偏置",
        "bitwise source": "按位运算的源操作数",
        "byte-displacement indices": "以字节位移表示的索引",
        "column-scale": "列缩放因子",
        "controls": "控制参数",
        "expected": "期望值",
        "fused addend Local source": "融合运算中提供加数的本地源",
        "independent scalar selected by predicate zero": "谓词为 0 时选择的独立标量",
        "indices": "索引",
        "integer shift-count source": "提供移位量的整数源",
        "integer value source": "提供待运算整数的源",
        "left": "左操作数",
        "left comparison source": "比较运算的左源",
        "left factor": "左因子",
        "left multiplicand Local source": "提供左乘数的本地源",
        "left-vector": "左向量",
        "negation source": "用于取相反数的源",
        "new Local DstDataType destination": "新建的本地目标，元素类型为 DstDataType",
        "new Local DstDataType numeric destination": "新建的本地数值目标，元素类型为 DstDataType",
        "new Local S64, S32, S16, U64, U32, or U16 destination": "新建的本地目标，类型可为 S64、S32、S16、U64、U32 或 U16",
        "new Local S64/U64 byte-offset destination": "新建的本地目标，用 S64 或 U64 保存字节偏移量",
        "new Local U32 index destination": "新建的本地目标，用 U32 保存索引",
        "new Local destination or absolute Shared destination": "新建的本地目标，或按绝对编号引用的共享目标",
        "new Local floating destination": "新建的本地浮点目标",
        "new Local numeric destination": "新建的本地数值目标",
        "new Local operation-type numeric destination": "新建的本地数值目标，类型与本次操作相同",
        "new Local same-type numeric destination": "新建的同类型本地数值目标",
        "new Local triangular destination": "新建的本地三角矩阵目标",
        "new Local value destination": "保存结果值的新本地目标",
        "new renamed Local destination": "新分配并重命名的本地目标",
        "new typed and laid-out Local destination": "按指定类型和布局新建的本地目标",
        "new zero-initialized Local value destination": "初始值为零的新本地目标",
        "ordered denominator": "按规定顺序绑定的分母",
        "ordered dividend": "按规定顺序绑定的被除数",
        "ordered divisor": "按规定顺序绑定的除数",
        "ordered left Local numeric source": "按规定顺序绑定的本地左数值源",
        "ordered left Local source": "按规定顺序绑定的本地左源",
        "ordered numerator": "按规定顺序绑定的分子",
        "ordered right Local numeric source": "按规定顺序绑定的本地右数值源",
        "ordered right Local source": "按规定顺序绑定的本地右源",
        "ordinary numeric U8 CUBE destination": "按 CUBE 布局存放普通 U8 数值的目标",
        "ordinary per-PE private-GPR byte row stride or weight-mode packed ShapeGPR": "普通模式取各 PE 私有通用寄存器中的行跨距（字节）；权重模式取打包的 ShapeGPR",
        "per-PE logical row stride in elements": "各 PE 的逻辑行跨距，以元素数计",
        "per-PE private-GPR byte row stride": "各 PE 私有通用寄存器中的行跨距，以字节计",
        "per-participating-PE compare scalar": "各参与 PE 提供的比较标量",
        "per-participating-PE private-GPR scalar": "各参与 PE 从私有通用寄存器提供的标量",
        "persistent Local S16, U16, S32, U32, S64, or U64 row-index source": "持久本地行索引源，类型可为 S16、U16、S32、U32、S64 或 U64",
        "persistent Local S32/U32/S64/U64 element indices": "持久本地元素索引，类型为 S32、U32、S64 或 U64",
        "persistent Local SrcOperationType minuend": "持久本地被减数，类型为 SrcOperationType",
        "persistent Local SrcOperationType subtrahend": "持久本地减数，类型为 SrcOperationType",
        "persistent Local column broadcast source interpreted through SrcDataType; only row zero supplies values": "按 SrcDataType 解释的持久本地列广播源，仅第 0 行提供数据",
        "persistent Local column broadcast source; only row zero supplies values": "持久本地列广播源，仅第 0 行提供数据",
        "persistent Local column broadcast source; only row zero supplies values through the BSTART operation view": "持久本地列广播源，仅第 0 行按 BSTART 指定的操作类型提供数据",
        "persistent Local floating source": "持久本地浮点源",
        "persistent Local full-shape numeric source": "具有完整形状的持久本地数值源",
        "persistent Local numeric source": "持久本地数值源",
        "persistent Local source": "持久本地源",
        "persistent Local value source": "提供数据的持久本地源",
        "rectifier source": "整流运算的源操作数",
        "replacement": "替换值",
        "right": "右操作数",
        "right comparison source": "比较运算的右源",
        "right factor": "右因子",
        "right multiplicand Local source": "提供右乘数的本地源",
        "right-matrix": "右矩阵",
        "row-scale": "行缩放因子",
        "selected Local destination fragments": "选中的本地目标片段",
        "source": "源操作数",
        "source data": "源数据",
        "source selected by predicate one": "谓词为 1 时选择的源",
        "source selected by predicate zero": "谓词为 0 时选择的源",
        "source0": "源操作数 0",
        "source1": "源操作数 1",
        "value": "数值",
        "ordered source-only GPR0": "按顺序绑定的只读源寄存器 GPR0",
        "ordered source-only GPR1": "按顺序绑定的只读源寄存器 GPR1",
        "ordered source-only GPR2": "按顺序绑定的只读源寄存器 GPR2",
        "ordered source-only GPR3": "按顺序绑定的只读源寄存器 GPR3",
    }
)


def role_zh(role: str) -> str:
    return ROLE[role]


def scoped_summary_zh(source: dict[str, Any], base: dict[str, Any]) -> str:
    name = source["mnemonic"]
    handler = source["semantic_handler"]
    if base.get("agu"):
        operation = memory_synopsis(base["agu"])
    else:
        atom = name.removeprefix("HL.")
        width_letter = (
            atom[-1]
            if handler != "AtomicReadModifyWrite" or atom.startswith("SWAP")
            else atom[1]
        )
        width = {"B": 8, "H": 16, "W": 32, "D": 64}[width_letter]
        if handler == "LoadReserved":
            operation = f"读取 {width} 位内存值并建立保留。"
        elif handler == "StoreConditional":
            operation = f"在保留条件成立时写入 {width} 位内存值。"
        elif handler == "CompareAndSwap":
            operation = f"比较 {width} 位内存值与期望值，相等时原子地写入替换值。"
        elif atom.startswith("SWAP"):
            operation = f"原子交换寄存器与内存中的 {width} 位值。"
        else:
            what = {
                "ADD": "加法",
                "SUB": "减法",
                "AND": "按位与",
                "OR": "按位或",
                "XOR": "按位异或",
                "SMAX": "有符号最大值",
                "SMIN": "有符号最小值",
                "UMAX": "无符号最大值",
                "UMIN": "无符号最小值",
            }
            operation = f"对 {width} 位内存值执行原子{what[atom.split('.')[1]]}操作。"
    return f"{name} 的访存请求采用{SCOPE[source['scope']]}属性。{operation}"
