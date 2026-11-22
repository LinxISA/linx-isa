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
    if not form or not reference:
        return ()
    details = [
        f"规范语义处理器：{form['semantic_handler']}。",
        f"PTO semantic family/group：{form['semantic_family']} / {form['semantic_group']}。",
    ]
    agu = form.get("agu")
    if isinstance(agu, dict):
        action = agu.get("action")
        kind = agu.get("address_kind")
        scale = agu.get("offset_scale")
        update = agu.get("update_mode")
        size = agu.get("size_bytes")
        details.append(
            f"AGU 契约：{action}，{kind} 地址，访问宽度 {size} byte，偏移缩放 2^{scale}，更新模式 {update}。"
        )
        if action in {"Load", "LoadPair"}:
            signed = "有符号扩展" if agu.get("signed_load") else "零扩展或完整宽度写回"
            details.append(
                f"加载结果采用{signed}；Pair 形式访问两个相邻元素。"
                if action == "LoadPair"
                else f"加载结果采用{signed}。"
            )
        if update == "PreIndex":
            details.append(
                "PreIndex 先形成更新后的有效地址，再访问该地址，并按 Syntax 写回地址结果。"
            )
        elif update == "PostIndex":
            details.append(
                "PostIndex 使用更新前基址访问，再形成并按 Syntax 写回更新后的地址。"
            )
    operands = reference.get("operands") or []
    if operands:
        details.append(
            "操作数："
            + "；".join(f"{item['field']} = {item['role']}" for item in operands)
            + "。"
        )
    for label, key in (
        ("状态结果", "state_effects"),
        ("内存效果", "memory_effects"),
        ("顺序", "ordering"),
        ("异常与 fault 边界", "exceptions"),
        ("合法性", "legality"),
    ):
        values = [
            str(value)
            for value in reference.get(key, [])
            if str(value) and str(value) != "none"
        ]
        if values:
            details.append(f"{label}：" + "；".join(values))
    return tuple(details)


def _pto_short_zh(inst: Mapping[str, Any], exact: str) -> str:
    form = _pto_forms().get(_clean(inst.get("pto_source_form_id"))) or {}
    mnemonic = _clean(inst.get("mnemonic"))
    agu = form.get("agu")
    if isinstance(agu, dict):
        actions = {
            "Load": "加载",
            "LoadPair": "相邻双元素加载",
            "Store": "存储",
            "StorePair": "相邻双元素存储",
            "Prefetch": "预取",
        }
        action = actions.get(str(agu.get("action")), str(agu.get("action")))
        return f"{mnemonic}：{action} {agu.get('size_bytes')} byte 数据，地址模式 {agu.get('address_kind')}/{agu.get('update_mode')}。{exact}"
    handler = str(form.get("semantic_handler", ""))
    labels = (
        ("Atomic", "原子读改写"),
        ("Compare", "比较并产生结果"),
        ("Floating", "浮点运算"),
        ("ScalarBinary", "标量二元运算"),
        ("Multiply", "乘法或乘加"),
        ("Divide", "除法"),
        ("Remainder", "余数运算"),
        ("SystemRegister", "系统寄存器访问"),
        ("Bundle", "block 描述符更新"),
        ("SetCommit", "提交条件更新"),
        ("Jump", "控制流转移"),
        ("Fence", "内存或取指顺序约束"),
        ("Maintenance", "系统维护操作"),
        ("Move", "标量值传送"),
    )
    label = next(
        (text for token, text in labels if token in handler), "规范标量或 block 操作"
    )
    return f"{mnemonic}：{label}。{exact}"


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


def _describe_vector(inst: Mapping[str, Any], profile: str) -> SemanticDescription:
    mnemonic = _clean(inst.get("mnemonic")).upper()
    group = _clean(inst.get("group"))
    parts = mnemonic.split(".")
    core = parts[1] if len(parts) > 1 else mnemonic
    suffixes = parts[2:]
    details = [
        "该形式属于 64-bit Linx vector encoding。普通逐-lane 运算由 64-bit EXEC mask p 隐式谓词化。",
        "对当前 Sail 中的 packed 64-bit 元素，逻辑元素 i 使用 predicate bit 2*i；不能把 mask bit 与所有元素宽度简单一一对应。",
        "操作数命名、可选修饰符与目的操作数以本页 Syntax 和 Encoding 为准。",
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
                f"Tagged Sail 先把两个输入分别转换为非零布尔值，再做逻辑 {operation.rstrip('I')}，并写 0 或 1；判别例 (1, 2) 的结果是 {example}，不是按位运算结果。"
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
                "当前 checked-in Sail 对每个 32-bit lane 做 bswap32；immr/imml 在该模型中被忽略，因此位域选择语义仍需架构确认。"
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
            "不受 checked-in Sail type predicates 支持的 SrcType/DstType 组合触发 ILLEGAL_INST；不得把 staged-model 的零值或 carrier packing 推广为额外架构格式。"
        )
    elif core in {"CSEL", "PSEL"}:
        short = "逐 lane 根据条件源选择左操作数或右操作数"
        if core == "PSEL":
            details[0] = (
                "当前 tagged Sail 的 V.PSEL 遍历配置的 lane 数，但不读取 EXEC mask p；每个 lane 根据 SrcP 是否非零选择 SrcL 或可选取负后的 SrcR。"
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
                "对寄存器索引 .BRG 形式，当前 checked-in Sail 使用 lane 0 的索引形成单一地址；加载值广播到活动 lane，存储使用 lane 0 数据。"
                "立即数 .BRG 形式当前复用对应立即数 staged handler；这不是额外的芯片 ordering 契约。"
            )
        if immediate:
            details.append(
                "当前 checked-in Sail 的立即数 load 从一个有效地址读取并广播；立即数 store 让每个活动 lane 依次写同一地址。"
                "该行为属于 staged model，不能推导跨 lane 的最终写入或 fault atomicity 芯片契约。"
            )
        if unscaled:
            details.append(
                ".U 标记选择 unscaled 编码形式；当前 Sail 对部分 .U handler 直接复用 scaled staged handler，实际缩放契约尚未冻结。"
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
        details.append(
            "跨 lane 序列化、ordering、inactive lane 和 fault atomicity 尚未冻结。"
        )
        if op in {"MAX", "MIN"}:
            details.append(
                "当前 tagged Sail 按有符号整数顺序选择 MAX/MIN；最终芯片 lane ordering 仍受 issue #149 约束。"
            )
            evidence_urls.append(_TAGGED_SAIL + "#L4852-L5258")
        issue_urls.append("https://github.com/LinxISA/linx-isa/issues/149")
    else:
        short = f"执行 {mnemonic} 所定义的向量操作"

    asm = _clean(inst.get("asm"))
    if "uimm" in asm:
        details.append("Syntax 使用 uimm，立即数按无符号值解释。")
    if "simm" in asm:
        details.append("Syntax 使用 simm，立即数按有符号值解释。")
    if core in {"SLL", "SRL", "SRA", "SLLI", "SRLI", "SRAI"}:
        details.append(
            "Tagged Sail 将 shift amount 对 SrcL 的有效整数位宽取模；寄存器形式从 SrcR 的类型化数值取得 shift amount，立即数形式使用无符号 shamt。"
        )
        evidence_urls.append(_TAGGED_SAIL + "#L5266-L5388")
    if core in {"MUL", "MADD"}:
        details.append(
            "当前 tagged Sail 把类型化输入转换为无符号整数后计算乘积或乘加，再按 DstType 打包结果。"
        )
        evidence_urls.append(_TAGGED_SAIL + "#L4360-L4415")

    if core in {"QPOP", "QPUSH"}:
        details.append(
            "队列状态机、empty/full 结果、并发与 fault ABI 尚未冻结；memory-ring 仅是 staged model approximation。"
        )
        issue_urls.append("https://github.com/LinxISA/linx-isa/issues/150")
    if core.startswith("SHFL"):
        details.append(
            "inactive/tail lane policy、source snapshot 和 instruction-lockstep 执行尚未冻结。"
        )
        issue_urls.append("https://github.com/LinxISA/linx-isa/issues/151")

    return SemanticDescription(
        short=short,
        description=short + "。",
        details=tuple(details),
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
        return SemanticDescription(
            short=_pto_short_zh(inst, first)
            if is_v059 and inst.get("pto_source_form_id")
            else first,
            description=note,
            details=_pto_form_details(inst) if is_v059 else (),
            provenance=tuple(dict.fromkeys(provenance)),
            confidence="catalog-semantic-summary",
        )

    mnemonic = _clean(inst.get("mnemonic")).upper()
    if mnemonic == "C.BSTART.VPAR":
        return SemanticDescription(
            short="结束当前 block，并以 VPAR 类型开始下一个 block",
            description="结束当前 block，并以 VPAR 类型开始下一个 fall-through block。",
            details=(
                "该形式使用 16-bit compressed encoding。FALL 是 assembly 形式名称；编码中没有独立的 FALL 物理字段。",
            ),
            provenance=(_catalog_source(inst, profile),),
            confidence="derived-from-normative-fields",
        )
    if mnemonic == "C.BSTART.VSEQ":
        return SemanticDescription(
            short="结束当前 block，并以 VSEQ 类型开始下一个 block",
            description="结束当前 block，并以 VSEQ 类型开始下一个 fall-through block。",
            details=(
                "该形式使用 16-bit compressed encoding。FALL 是 assembly 形式名称；编码中没有独立的 FALL 物理字段。",
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


def detail(row: Mapping[str, Any], catalog: Mapping[str, Any]) -> str:
    """Return safe HTML for the semantic section of one instruction form."""

    semantic = describe_form(row, _profile_from_catalog(catalog))
    blocks = [f'<p class="semantic-description">{escape(semantic.description)}</p>']
    if semantic.details:
        items = "".join(f"<li>{escape(item)}</li>" for item in semantic.details)
        blocks.append(f'<ul class="semantic-details">{items}</ul>')
    links = [source for source in semantic.provenance if source.startswith("https://")]
    if links:
        anchors = " · ".join(
            f'<a href="{escape(link, quote=True)}">规范来源</a>' for link in links
        )
        blocks.append(f'<p class="semantic-sources">{anchors}</p>')
    return "".join(blocks)
