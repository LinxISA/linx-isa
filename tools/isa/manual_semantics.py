#!/usr/bin/env python3
"""Source-backed instruction prose for the generated HTML reference.

The catalog ``note`` is the primary per-form semantic summary.  A small number
of Linx-only vector forms intentionally have no note.  This module describes
those forms from their mnemonic, assembly template, group, and the tagged
v0.59.1 Sail model.  It deliberately does not invent pseudocode for
fields whose interpretation is selected by another architectural profile.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from html import escape
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

try:
    from manual_tag import tagged_json
except ModuleNotFoundError:  # package-style unittest import
    from tools.isa.manual_tag import tagged_json
try:
    from manual_prose_zh import polish, scalar_synopsis
except ModuleNotFoundError:  # package-style unittest import
    from tools.isa.manual_prose_zh import polish, scalar_synopsis


@dataclass(frozen=True)
class SemanticDescription:
    """Structured prose consumed by index and instruction-page renderers."""

    short: str
    description: str
    details: tuple[str, ...]
    provenance: tuple[str, ...]
    confidence: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_VECTOR_INTEGER = {
    "ADD": "逐活动 lane 做整数加法",
    "ADDI": "逐活动 lane 做整数立即数加法",
    "SUB": "逐活动 lane 做整数减法",
    "SUBI": "逐活动 lane 做整数立即数减法",
    "AND": "逐活动 lane 做按位与",
    "ANDI": "逐活动 lane 与立即数做按位与",
    "OR": "逐活动 lane 做按位或",
    "ORI": "逐活动 lane 与立即数做按位或",
    "XOR": "逐活动 lane 做按位异或",
    "XORI": "逐活动 lane 与立即数做按位异或",
    "SLL": "逐活动 lane 做逻辑左移",
    "SLLI": "逐活动 lane 做立即数逻辑左移",
    "SRL": "逐活动 lane 做逻辑右移",
    "SRLI": "逐活动 lane 做立即数逻辑右移",
    "SRA": "逐活动 lane 做算术右移",
    "SRAI": "逐活动 lane 做立即数算术右移",
    "MUL": "逐活动 lane 做无符号整数乘法并保留目的类型可表示的低位",
    "MADD": "逐活动 lane 做无符号整数乘加并保留目的类型可表示的低位",
    "DIV": "逐活动 lane 做有符号整数除法",
    "REM": "逐活动 lane 计算有符号整数余数",
}

_VECTOR_BITS = {
    "BCNT": "统计所选位域中的置位数",
    "BIC": "清除所选位域",
    "BIS": "设置所选位域",
    "BXS": "有符号提取所选位域",
    "BXU": "无符号提取所选位域",
    "CLZ": "统计所选位域的前导零",
    "CTZ": "统计所选位域的尾随零",
    "REV": "对每个 32-bit lane 执行完整 bswap32（当前 Sail 忽略位域参数）",
}

_FP = {
    "FABS": "逐活动 lane 取浮点绝对值",
    "FADD": "逐活动 lane 做浮点加法",
    "FCLASS": "逐活动 lane 对浮点值分类",
    "FDIV": "逐活动 lane 做浮点除法",
    "FEXP": "逐活动 lane 计算浮点指数函数",
    "FMADD": "逐活动 lane 做融合浮点乘加",
    "FMSUB": "逐活动 lane 做融合浮点乘减",
    "FMUL": "逐活动 lane 做浮点乘法",
    "FNMADD": "逐活动 lane 做融合负乘加",
    "FNMSUB": "逐活动 lane 做融合负乘减",
    "FRECIP": "逐活动 lane 计算浮点倒数",
    "FSQRT": "逐活动 lane 计算浮点平方根",
    "FSUB": "逐活动 lane 做浮点减法",
    "FMAX": "逐活动 lane 选择浮点最大值",
    "FMIN": "逐活动 lane 选择浮点最小值",
    "MAX": "逐活动 lane 按有符号整数顺序选择最大值",
    "MIN": "逐活动 lane 按有符号整数顺序选择最小值",
}

_COMPARE = {
    "EQ": "相等",
    "EQI": "与立即数相等",
    "NE": "不相等",
    "NEI": "与立即数不相等",
    "LT": "有符号小于",
    "LTI": "有符号小于立即数",
    "GE": "有符号大于等于",
    "GEI": "有符号大于等于立即数",
    "LTU": "无符号小于",
    "LTUI": "无符号小于立即数",
    "GEU": "无符号大于等于",
    "GEUI": "无符号大于等于立即数",
    "AND": "左右操作数分别判非零后做布尔 AND",
    "ANDI": "左操作数与有符号立即数分别判非零后做布尔 AND",
    "OR": "左右操作数分别判非零后做布尔 OR",
    "ORI": "左操作数与有符号立即数分别判非零后做布尔 OR",
}

_TAGGED_SAIL = "https://github.com/LinxISA/linx-isa/blob/d262515b55c727073997c8f4c95261909f2fe8d3/isa/sail/model/execute/execute.sail"


def _logical_compare_result(operation: str, left: int, right: int) -> int:
    """Independent executable oracle for V.CMP logical forms."""
    lhs, rhs = left != 0, right != 0
    if operation in {"AND", "ANDI"}:
        return int(lhs and rhs)
    if operation in {"OR", "ORI"}:
        return int(lhs or rhs)
    raise ValueError(f"not a V.CMP logical operation: {operation}")


_FP_COMPARE = {
    "FEQ": "浮点相等比较",
    "FEQS": "S 形式浮点相等比较",
    "FNE": "浮点不等比较",
    "FNES": "S 形式浮点不等比较",
    "FLT": "浮点小于比较",
    "FLTS": "S 形式浮点小于比较",
    "FGE": "浮点大于等于比较",
    "FGES": "S 形式浮点大于等于比较",
}


def _clean(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _catalog_source(inst: Mapping[str, Any], profile: str) -> str:
    src = inst.get("source") or {}
    path = _clean(src.get("file"))
    line = src.get("line")
    suffix = f":{line}" if line is not None else ""
    return (
        f"isa/{profile}/{path}{suffix}"
        if path
        else f"isa/{profile}/linxisa-{profile}.json"
    )


@lru_cache(maxsize=1)
def _pto_forms() -> dict[str, Mapping[str, Any]]:
    forms: dict[str, Mapping[str, Any]] = {}
    for name in ("pto_scalar_forms.json", "pto_command_forms.json"):
        payload = tagged_json(f"isa/v0.59/state/{name}")
        forms.update({str(form["form_id"]): form for form in payload["forms"]})
    return forms


@lru_cache(maxsize=1)
def _pto_reference() -> dict[str, Mapping[str, Any]]:
    path = (
        Path(__file__).resolve().parents[2]
        / "docs/architecture/isa-manual/reference/pto-v0591-semantics.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))["forms"]


@lru_cache(maxsize=1)
def _pto_chinese() -> dict[str, Mapping[str, Any]]:
    path = (
        Path(__file__).resolve().parents[2]
        / "docs/architecture/isa-manual/reference/data/manual-semantics-zh.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))["forms"]


def _pto_source_link(inst: Mapping[str, Any]) -> str | None:
    record = _pto_reference().get(_clean(inst.get("pto_source_form_id")))
    if not record:
        return None
    return (
        "https://github.com/PTO-ISA/pto-spec/blob/"
        f"{record['source_commit']}/{record['source_path']}"
    )


def _pto_form_details(inst: Mapping[str, Any]) -> tuple[str, ...]:
    form_id = _clean(inst.get("pto_source_form_id"))
    form = _pto_forms().get(form_id)
    reference = _pto_reference().get(form_id)
    chinese = _pto_chinese().get(form_id)
    if not form or not reference or not chinese:
        return ()
    if inst.get("mnemonic") == "DC.IALL":
        return (
            polish("操作数：无显式操作数；唯一合法机器字为 0x0010602b。"),
            polish(
                "执行结果：记录 Maintenance_DC_IALL，将数据缓存维护计数加一，成功后 TPC 前进 4 字节。"
            ),
            polish(
                "约束与异常：仅可在 SYS block 内执行；合法执行不做普通访存，也没有指令自身的算术或数据访问异常；在其他 block 中执行会触发 Fault_BundleControl。"
            ),
        )
    roles = chinese["roles"]
    groups = (
        ("机制", roles["mechanism"]["statements"][2:]),
        ("操作数", roles["inputs-outputs"]["statements"]),
        ("执行结果", roles["effects"]["statements"]),
        ("约束与异常", roles["constraints"]["statements"]),
    )
    return tuple(
        polish(
            f"{heading}："
            + " ".join(_natural_chinese(str(item)) for item in statements)
        )
        for heading, statements in groups
        if statements
    )


def _pto_short_zh(inst: Mapping[str, Any], exact: str) -> str:
    chinese = _pto_chinese().get(_clean(inst.get("pto_source_form_id")))
    if chinese:
        fallback = _natural_chinese(
            _concise_chinese(str(chinese["roles"]["purpose"]["statements"][0]))
        )
        return scalar_synopsis(inst, fallback)
    return polish(exact)


def _pto_description_zh(inst: Mapping[str, Any], fallback: str) -> str:
    if inst.get("mnemonic") == "DC.IALL":
        return "该指令不读取标量源寄存器。维护完成后，才更新维护记录和 TPC。"
    chinese = _pto_chinese().get(_clean(inst.get("pto_source_form_id")))
    if not chinese:
        return fallback
    statements = chinese["roles"]["mechanism"]["statements"]
    return polish(_natural_chinese(" ".join(str(item) for item in statements[:2])))


def _natural_chinese(text: str) -> str:
    replacements = {
        "并通过 Reg5 目标发布和": "并把结果写入 Reg5 选择的目标",
        "通过 Reg5 目标发布结果": "把结果写入 Reg5 选择的目标",
        "发布出的字": "写入的结果",
        "RegDst 发布结果": "RegDst 写入结果",
        "和发布或丢弃": "结果写入或丢弃",
        "发布为 0x": "写入为 0x",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text).strip()


def _first_chinese_sentence(text: str) -> str:
    match = re.match(r"^.*?[。！？](?:[”’])?", text)
    return match.group(0) if match else text


def _concise_chinese(text: str) -> str:
    sentences = [
        item.strip()
        for item in re.findall(r".*?(?:[。！？](?:[”’])?|$)", text)
        if item.strip()
    ]
    selected: list[str] = []
    for sentence in sentences:
        if "其记录的摘要为" in sentence or sentence.startswith("设计要点："):
            continue
        if selected:
            first = selected[0]
            needs_second = len(first) < 30 or "是一条独立的" in first
            if (
                not needs_second
                or len(selected) >= 2
                or len("".join(selected)) + len(sentence) > 180
            ):
                break
        selected.append(sentence)
    return "".join(selected) or _first_chinese_sentence(text)


def _memory_width(root: str) -> tuple[int, bool] | None:
    base = root.rstrip("I")
    table = {
        "LB": (8, True),
        "LBU": (8, False),
        "LH": (16, True),
        "LHU": (16, False),
        "LW": (32, True),
        "LWU": (32, False),
        "LD": (64, False),
        "SB": (8, False),
        "SH": (16, False),
        "SW": (32, False),
        "SD": (64, False),
    }
    return table.get(base)


def _linx_note_zh(inst: Mapping[str, Any], exact: str) -> str:
    mnemonic = _clean(inst.get("mnemonic"))
    asm = _clean(inst.get("asm"))
    if mnemonic == "B.TEXT":
        return polish("B.TEXT 为解耦 block 设置离线 body 的入口地址。")
    if mnemonic in {"DMA.FREE.L", "DMA.FREE.S", "MCOPY.DL", "MCOPY.DS"}:
        return polish(
            f"{mnemonic} 仅保留编码，尚未实现；执行时必须在读取操作数或产生任何架构效果之前拒绝。"
        )
    if mnemonic == "HL.BSTART CALL":
        return polish(
            "HL.BSTART.CALL 原子地完成调用：目标为 P + (SignExtend(simm25) << 1)，ra 为 (P + 4) + (ZeroExtend(uimm5) << 1)；两个标签分别编码、分别重定位。"
        )
    if mnemonic in {"BSTART.MPAR", "BSTART.MSEQ"}:
        mode = "并行" if mnemonic.endswith("MPAR") else "顺序"
        return polish(
            f"{mnemonic} 结束当前 block，并以所选 VS8/VS16 宽度开始新的{mode} SIMT block。"
        )
    if mnemonic in {"BSTART.VPAR", "BSTART.VSEQ"}:
        mode = "并行" if mnemonic.endswith("VPAR") else "顺序"
        return polish(
            f"{mnemonic} 开始新的{mode} SIMT block；解耦形式必须由 B.TEXT 提供 body 入口。"
        )
    if "BSTART" in mnemonic:
        block_kind = (
            "浮点块"
            if ".FP" in mnemonic
            else "系统块"
            if ".SYS" in mnemonic
            else "标准块"
        )
        start = f"结束当前块，并初始化后继{block_kind}的描述符。"
        if " FALL" in asm:
            return start + "默认顺序转移。"
        if " DIRECT" in asm:
            return start + "直接转移到目标标签。"
        if " COND" in asm:
            return start + "按块条件选择是否转移到目标标签。"
        if " CALL" in asm:
            call = "以标签给出的地址为调用目标。"
            if mnemonic.startswith("L."):
                call += "本形式保持 ra 不变；如需返回，须先用 SETRET 或 C.SETRET 指定返回标签。"
            return start + call
        return start

    return polish(exact)


def _describe_vector(inst: Mapping[str, Any], profile: str) -> SemanticDescription:
    mnemonic = _clean(inst.get("mnemonic")).upper()
    group = _clean(inst.get("group"))
    parts = mnemonic.split(".")
    core = parts[1] if len(parts) > 1 else mnemonic
    suffixes = parts[2:]
    details = [
        "该形式采用 64 位 Linx 向量编码。普通逐 lane 运算由 64 位执行掩码 p 隐式控制。",
        "对于 v0.59.1 Sail 中由两个 32 位 lane 承载的 64 位元素，逻辑元素 i 使用谓词位 2*i；不能把一个谓词位简单对应到所有元素宽度。",
        "操作数名称、可选修饰符与目的操作数以本页汇编语法和编码图为准。",
    ]
    issue_urls: list[str] = []
    evidence_urls: list[str] = []

    if core == "CMP" and suffixes:
        operation = suffixes[0]
        cond = _COMPARE.get(operation, operation)
        short = f"逐活动 lane 判断{cond}并产生比较结果"
        if operation in {"AND", "ANDI", "OR", "ORI"}:
            example = _logical_compare_result(operation, 1, 2)
            details.append(
                f"v0.59.1 Sail 先把两个输入分别转换为非零布尔值，再做逻辑 {operation.rstrip('I')}，并写 0 或 1；判别例 (1, 2) 的结果是 {example}，不是按位运算结果。"
            )
            if operation.endswith("I"):
                details.append(
                    "立即数先从 simm12 符号扩展到 32 bit；布尔化后只有零与非零有区别。"
                )
            evidence_urls.append(_TAGGED_SAIL + "#L3899-L3964")
    elif core in _FP_COMPARE:
        short = f"逐活动 lane 做{_FP_COMPARE[core]}并写入布尔结果"
    elif core in _VECTOR_INTEGER:
        short = _VECTOR_INTEGER[core]
    elif core in _VECTOR_BITS:
        short = f"逐活动 lane {_VECTOR_BITS[core]}"
        if core == "REV":
            details.append(
                "v0.59.1 Sail 对每个 32 位 lane 做完整字节序反转；该模型忽略 immr/imml，因此位域选择语义仍需架构确认。"
            )
    elif core in _FP:
        short = _FP[core]
    elif core in {"FCVT", "FCVTI", "ICVT", "ICVTF"}:
        labels = {
            "FCVT": "转换浮点格式",
            "FCVTI": "将浮点值转换为整数",
            "ICVT": "转换整数格式",
            "ICVTF": "将整数值转换为浮点格式",
        }
        short = f"逐活动 lane {labels[core]}"
        details.append("源类型和目的类型由 st2dt 类型限定符选择。")
        details.append(
            "不受 v0.59.1 Sail 类型判定支持的 SrcType/DstType 组合触发 ILLEGAL_INST；不得把阶段模型中的零值或承载打包方式推广为额外架构格式。"
        )
    elif core in {"CSEL", "PSEL"}:
        short = "逐 lane 根据条件源选择左操作数或右操作数"
        if core == "PSEL":
            details[0] = (
                "v0.59.1 Sail 的 V.PSEL 遍历配置的 lane 数，但不读取执行掩码 p；每个 lane 根据 SrcP 是否非零选择 SrcL 或可选取负后的 SrcR。"
            )
            evidence_urls.append(_TAGGED_SAIL + "#L3966-L3986")
    elif core.startswith("RD"):
        op = core[2:]
        names = {
            "ADD": "加法",
            "AND": "按位与",
            "OR": "按位或",
            "XOR": "按位异或",
            "MAX": "有符号最大值",
            "MIN": "有符号最小值",
            "FADD": "浮点加法",
            "FMAX": "浮点最大值",
            "FMIN": "浮点最小值",
        }
        short = f"将活动 lane 按{names.get(op, op)}归约到寄存器目的操作数"
        details[0] = "该形式是跨活动 lane 的归约操作，不是独立的逐-lane 写回。"
    elif core.startswith("SHFL"):
        mode = suffixes[0] if suffixes else ""
        modes = {"BFLY": "蝶形", "DOWN": "向下", "UP": "向上", "IDX": "索引"}
        short = f"按{modes.get(mode, mode)}模式在 lane 之间重排数据"
    elif core in {"QPOP", "QPUSH"}:
        short = "从队列取出向量数据" if core == "QPOP" else "向队列写入向量数据"
    elif group.startswith("Load") or group.startswith("Store"):
        is_load = core.startswith("L")
        width_signed = _memory_width(core)
        width = width_signed[0] if width_signed else None
        sign = width_signed[1] if width_signed else False
        bridge = "BRG" in suffixes
        unscaled = "U" in suffixes or "UnScaled" in group
        kind = "加载" if is_load else "存储"
        qual = (
            "有符号"
            if sign and is_load
            else "无符号"
            if is_load and width and width < 64
            else ""
        )
        immediate = "simm" in _clean(inst.get("asm"))
        short = (
            f"编码为向量立即数地址{kind}{qual}{width or ''}-bit 数据"
            if immediate
            else f"逐活动 lane {kind}{qual}{width or ''}-bit 数据"
        )
        if bridge:
            details.append(
                "对寄存器索引 .BRG 形式，v0.59.1 Sail 使用 lane 0 的索引形成单一地址；加载值广播到活动 lane，存储使用 lane 0 数据。"
                "立即数 .BRG 形式当前复用对应的阶段处理函数；这不构成额外的芯片顺序契约。"
            )
        if immediate:
            details.append(
                "v0.59.1 Sail 的立即数加载从一个有效地址读取并广播；立即数存储让每个活动 lane 依次写同一地址。"
                "该行为属于阶段模型，不能据此推导跨 lane 的最终写入或故障原子性芯片契约。"
            )
        if unscaled:
            details.append(
                ".U 标记选择非缩放编码形式；当前 Sail 对部分 .U 处理函数直接复用缩放形式的阶段处理函数，实际缩放契约尚未冻结。"
            )
        details.append(
            "C/L、local/BRG 组合及 halfword alignment 尚未冻结，不能把当前模型行为当作芯片契约。"
        )
        issue_urls.append("https://github.com/LinxISA/linx-isa/issues/141")
    elif group == "Atomic Operation" and core in {"LD", "LW", "SD", "SW"}:
        op = suffixes[0] if suffixes else ""
        width = 64 if core.endswith("D") else 32
        names = {
            "ADD": "加法",
            "AND": "按位与",
            "OR": "按位或",
            "XOR": "按位异或",
            "MAX": "有符号最大值",
            "MIN": "有符号最小值",
        }
        returning = core.startswith("L")
        short = f"逐活动 lane 做 {width}-bit 原子{names.get(op, op)}读改写"
        details.append(
            "该 load 型形式返回修改前的内存值。"
            if returning
            else "该 store 型形式只更新内存，不返回原值。"
        )
        details.append("跨 lane 串行次序、内存顺序、非活动 lane 和故障原子性尚未冻结。")
        if op in {"MAX", "MIN"}:
            details.append(
                "v0.59.1 Sail 按有符号整数顺序选择 MAX/MIN；最终芯片 lane 次序仍受 issue #149 约束。"
            )
            evidence_urls.append(_TAGGED_SAIL + "#L4852-L5258")
        issue_urls.append("https://github.com/LinxISA/linx-isa/issues/149")
    else:
        short = f"执行 {mnemonic} 所定义的向量操作"

    asm = _clean(inst.get("asm"))
    if "uimm" in asm:
        details.append("汇编语法使用 uimm，立即数按无符号值解释。")
    if "simm" in asm:
        details.append("汇编语法使用 simm，立即数按有符号值解释。")
    if core in {"SLL", "SRL", "SRA", "SLLI", "SRLI", "SRAI"}:
        details.append(
            "v0.59.1 Sail 将移位量对 SrcL 的有效整数位宽取模；寄存器形式从 SrcR 的类型化数值取得移位量，立即数形式使用无符号 shamt。"
        )
        evidence_urls.append(_TAGGED_SAIL + "#L5266-L5388")
    if core in {"MUL", "MADD"}:
        details.append(
            "v0.59.1 Sail 把类型化输入转换为无符号整数后计算乘积或乘加，再按 DstType 打包结果。"
        )
        evidence_urls.append(_TAGGED_SAIL + "#L4360-L4415")

    if core in {"QPOP", "QPUSH"}:
        details.append(
            "队列状态机、空/满结果、并发与故障 ABI 尚未冻结；内存环形队列仅是阶段模型的近似实现。"
        )
        issue_urls.append("https://github.com/LinxISA/linx-isa/issues/150")
    if core.startswith("SHFL"):
        details.append("非活动 lane、尾部 lane、源快照和指令锁步执行策略尚未冻结。")
        issue_urls.append("https://github.com/LinxISA/linx-isa/issues/151")

    return SemanticDescription(
        short=polish(short),
        description=polish(short + "。"),
        details=tuple(polish(item) for item in details),
        provenance=tuple((_catalog_source(inst, profile), *evidence_urls, *issue_urls)),
        confidence="derived-from-normative-fields",
    )


def describe_form(
    inst: Mapping[str, Any], profile: str = "v0.58"
) -> SemanticDescription:
    """Describe one catalog form without weakening the catalog's exact prose.

    ``confidence`` is ``catalog-semantic-summary`` when the compiled catalog
    supplies a note.  The fallback is reserved for the 186 Linx-only vector
    forms and two compressed vector-block starts that lack notes in both
    profiles.
    """

    profile = profile if profile.startswith("v") else f"v{profile}"
    note = _clean(inst.get("note"))
    if note:
        first = re.split(r"(?<=[.!?])\s+", note, maxsplit=1)[0]
        is_v059 = profile == "v0.59"
        source_link = _pto_source_link(inst) if is_v059 else None
        provenance = [_catalog_source(inst, profile)]
        if is_v059 and inst.get("pto_source_form_id"):
            provenance.append(
                "docs/architecture/isa-manual/reference/pto-v0591-semantics.json"
            )
        if source_link:
            provenance.append(source_link)
        chinese_summary = (
            _pto_short_zh(inst, first)
            if is_v059 and inst.get("pto_source_form_id")
            else _linx_note_zh(inst, first)
            if is_v059
            else first
        )
        return SemanticDescription(
            short=chinese_summary,
            description=(
                _pto_description_zh(inst, chinese_summary)
                if is_v059 and inst.get("pto_source_form_id")
                else chinese_summary
                if is_v059
                else note
            ),
            details=_pto_form_details(inst) if is_v059 else (),
            provenance=tuple(dict.fromkeys(provenance)),
            confidence="catalog-semantic-summary",
        )

    mnemonic = _clean(inst.get("mnemonic")).upper()
    if mnemonic == "C.BSTART.VPAR":
        return SemanticDescription(
            short=polish("结束当前 block，并以 VPAR 类型开始下一个 block"),
            description=polish(
                "结束当前 block，并以 VPAR 类型按顺序落点开始下一个 block。"
            ),
            details=(
                polish(
                    "该形式使用 16 位压缩编码。FALL 是汇编形式名称；编码中没有独立的 FALL 物理字段。"
                ),
            ),
            provenance=(_catalog_source(inst, profile),),
            confidence="derived-from-normative-fields",
        )
    if mnemonic == "C.BSTART.VSEQ":
        return SemanticDescription(
            short=polish("结束当前 block，并以 VSEQ 类型开始下一个 block"),
            description=polish(
                "结束当前 block，并以 VSEQ 类型按顺序落点开始下一个 block。"
            ),
            details=(
                polish(
                    "该形式使用 16 位压缩编码。FALL 是汇编形式名称；编码中没有独立的 FALL 物理字段。"
                ),
            ),
            provenance=(_catalog_source(inst, profile),),
            confidence="derived-from-normative-fields",
        )
    if mnemonic.startswith("V."):
        return _describe_vector(inst, profile)
    return SemanticDescription(
        short=f"{mnemonic} instruction",
        description="当前 catalog 未提供可逐字引用的语义摘要。请以 Syntax、Encoding 和所列规范来源为准。",
        details=(),
        provenance=(_catalog_source(inst, profile),),
        confidence="catalog-metadata-only",
    )


def describe_mnemonic(
    forms: Iterable[Mapping[str, Any]], profile: str = "v0.58"
) -> SemanticDescription:
    """Combine same-mnemonic forms while retaining form-specific differences."""

    descriptions = [describe_form(form, profile) for form in forms]
    if not descriptions:
        raise ValueError("describe_mnemonic requires at least one form")
    first = descriptions[0]
    details = list(first.details)
    for item in descriptions[1:]:
        if item.description != first.description and item.description not in details:
            details.append(item.description)
        for detail in item.details:
            if detail not in details:
                details.append(detail)
    provenance = tuple(dict.fromkeys(p for d in descriptions for p in d.provenance))
    confidence = (
        first.confidence
        if all(d.confidence == first.confidence for d in descriptions)
        else "mixed-source-backed"
    )
    return SemanticDescription(
        first.short, first.description, tuple(details), provenance, confidence
    )


def validate_catalog_coverage(repo_root: Path, profile: str) -> list[str]:
    """Return form IDs that only receive the metadata-only safety fallback."""

    import json

    profile = profile if profile.startswith("v") else f"v{profile}"
    version = profile[1:]
    catalog_path = repo_root / "isa" / profile / f"linxisa-{profile}.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    return [
        str(inst.get("id") or inst.get("uid") or inst.get("mnemonic"))
        for inst in catalog["instructions"]
        if describe_form(inst, profile).confidence == "catalog-metadata-only"
    ]


def _profile_from_catalog(catalog: Mapping[str, Any]) -> str:
    version = _clean(catalog.get("version"))
    if version.startswith("0.59"):
        return "v0.59"
    return "v0.58"


def summary(row: Mapping[str, Any], catalog: Mapping[str, Any]) -> str:
    """Return the concise index explanation for one catalog row."""

    return describe_form(row, _profile_from_catalog(catalog)).short


def detail(
    row: Mapping[str, Any],
    catalog: Mapping[str, Any],
    *,
    show_repeated_summary: bool = True,
) -> str:
    """Return safe HTML for the semantic section of one instruction form."""

    semantic = describe_form(row, _profile_from_catalog(catalog))
    blocks = []
    if show_repeated_summary or semantic.description.rstrip(
        "。"
    ) != semantic.short.rstrip("。"):
        blocks.append(
            f'<p class="semantic-description">{escape(semantic.description)}</p>'
        )

    if semantic.details:
        section_names = {"机制", "操作数", "执行结果", "约束与异常"}
        split_details = [item.split("：", 1) for item in semantic.details]
        if split_details and all(
            len(parts) == 2 and parts[0] in section_names for parts in split_details
        ):
            sections = "".join(
                f'<section class="semantic-section"><h4>{escape(heading)}</h4><p>{escape(body)}</p></section>'
                for heading, body in split_details
            )
            blocks.append(f'<div class="semantic-details">{sections}</div>')
        else:
            items = "".join(f"<li>{escape(item)}</li>" for item in semantic.details)
            blocks.append(f'<ul class="semantic-details">{items}</ul>')
    links = [source for source in semantic.provenance if source.startswith("https://")]
    if links:
        anchors = " · ".join(
            f'<a href="{escape(link, quote=True)}">规范来源</a>' for link in links
        )
        blocks.append(f'<p class="semantic-sources">{anchors}</p>')
    return "".join(blocks)
