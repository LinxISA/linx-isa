"""Short Chinese instruction descriptions for the lookup pages.

Generate regular families from the released form's handler, addressing record
and field definitions. Irregular forms retain their individual translations.
"""

from functools import lru_cache
import re

try:
    from manual_tag import tagged_json
except ModuleNotFoundError:
    from tools.isa.manual_tag import tagged_json


@lru_cache(maxsize=1)
def _scalar_forms():
    return {
        f["form_id"]: f
        for f in tagged_json("isa/v0.59/state/pto_scalar_forms.json")["forms"]
    }


# These substitutions apply to explanatory Chinese sentences only. Whole-word
# matches keep helper names such as ReadTilePayload and vector_lane intact.
_TERMS = {
    "tagged Sail": "发布版 Sail 模型",
    "Tagged Sail": "发布版 Sail 模型",
    "SYS block": "系统块",
    "Standard 块": "标准块",
    "EXEC mask": "执行掩码",
    "scope wrapper": "作用域封装",
    "wrapper": "封装",
    "header": "块头",
    "block": "指令块",
    "body": "块体",
    "lane": "通道",
    "padding": "填充区",
    "payload": "数据",
    "helper": "函数",
    "fault": "异常",
}
_WORD = re.compile(
    r"(?<![a-zA-Z0-9_])("
    + "|".join(re.escape(k) for k in _TERMS)
    + r")(?![a-zA-Z0-9_])"
)


def polish(text):
    text = text.replace("离线 body", "块外指令体").replace(
        "逐活动 lane", "对每个活动通道"
    )
    text = text.replace("发布到 Reg5 目的", "写入 Reg5 指定的目标").replace(
        "之后才到达 RegDst", "再写入 RegDst"
    )
    text = text.replace("目的操作数", "目标操作数").replace("源快照", "源操作数快照")
    text = re.sub(r"(?<![\w])([0-9]+)-bit\b", r"\1 位", text)
    text = _WORD.sub(lambda m: _TERMS[m[0]], text)
    text = re.sub(r"(?<=[一-鿿]) +(?=[一-鿿])", "", text)
    return re.sub(r" {2,}", " ", text).strip()


_MAINTENANCE = {
    "BC.IALL": "指令块缓存全部条目的失效",
    "BC.IVA": "按虚拟地址对指令块缓存执行失效",
    "DC.IALL": "数据缓存全部条目的失效",
    "DC.IVA": "按虚拟地址对数据缓存执行失效",
    "DC.CVA": "按虚拟地址清理数据缓存",
    "DC.CIVA": "按虚拟地址清理数据缓存并执行失效",
    "DC.ISW": "按组、路对数据缓存执行失效",
    "DC.CSW": "按组、路清理数据缓存",
    "DC.CISW": "按组、路清理数据缓存并执行失效",
    "DC.ZVA": "按地址对数据缓存执行清零",
    "IC.IALL": "指令缓存全部条目的失效",
    "IC.IVA": "按虚拟地址对指令缓存执行失效",
    "TLB.IA": "按地址空间标识符（ASID）使 TLB 条目失效",
    "TLB.IALL": "全部 TLB 条目的失效",
    "TLB.IAV": "按 ASID 和虚拟地址使 TLB 条目失效",
    "TLB.IV": "按虚拟地址使 TLB 条目失效",
}
_OPERATION = {
    "ADD": "加法",
    "SUB": "减法",
    "AND": "按位与",
    "OR": "按位或",
    "XOR": "按位异或",
}
_SHIFT = {"SLL": "逻辑左移", "SRL": "逻辑右移", "SRA": "算术右移"}
_ADDRESS = {
    "Register": "寄存器偏移",
    "Immediate": "立即数偏移",
    "Compressed": "压缩立即数偏移",
    "PCRelative": "PC 相对",
}


def memory_synopsis(agu):
    n = agu["size_bytes"]
    action = agu["action"]
    if action == "Prefetch":
        dest = "，并返回有效地址" if agu["prefetch_returns_address"] else ""
        return f"以{_ADDRESS[agu['address_kind']]}寻址，发出预取提示{dest}。"
    verb = "读取" if action.startswith("Load") else "写入"
    values = f"两个相邻的 {n} 字节值" if action.endswith("Pair") else f"一个 {n} 字节值"
    sentence = f"采用{_ADDRESS[agu['address_kind']]}寻址，按小端序{verb}{values}。"
    if action.startswith("Load") and n < 8:
        extension = "符号扩展" if agu["signed_load"] else "零扩展"
        sentence += f"将读取的值{extension}到 XLEN 位。"
    update = {
        "None": "",
        "PreIndex": "先计算新基址，用新地址访问内存。",
        "PostIndex": "本次访问使用原基址，完成后更新基址。",
    }
    return sentence + update[agu["update_mode"]]


def _binary(form):
    name = form["mnemonic"].split(".")[-1]
    word = form["semantic_handler"] == "ScalarBinaryW"
    core = name.removesuffix("W") if word else name
    base = core.removesuffix("I")
    compressed = form["mnemonic"].startswith("C.")
    result = "结果压入 T 队列。" if compressed else "结果写入 RegDst 指定的目标。"
    if word:
        result = "将低 32 位结果符号扩展到 XLEN 位，再写入 RegDst 指定的目标。"
    if base in _SHIFT:
        if core.endswith("I"):
            rhs = "编码中的移位量"
        else:
            rhs = f"SrcR 的低 {5 if word else 6} 位"
        lhs = "T#1" if compressed else ("SrcL 的低 32 位" if word else "SrcL")
        return f"将 {lhs} {_SHIFT[base]}，移位量取自{rhs}。" + result
    if base not in _OPERATION:
        return ""
    lhs = "SrcL 的低 32 位" if word else "SrcL"
    immediate = next(
        (f for f in form["fields"] if f["name"].lower().startswith(("uimm", "simm"))),
        None,
    )
    preparation = ""
    if immediate and core.endswith("I"):
        sign = "符号扩展" if immediate["signedness"] == "signed" else "零扩展"
        right = f"{sign}后的 {immediate['width']} 位立即数"
    elif compressed:
        right = "SrcR"
    else:
        preparation = "先按编码修饰 SrcR，再将其左移 shamt 位。"
        right = "所得的右操作数"
    if base == "ADD":
        operation = f"将 {lhs} 与{right}相加。"
    elif base == "SUB":
        operation = f"从 {lhs} 中减去{right}。"
    else:
        operation = f"将 {lhs} 与{right}作{_OPERATION[base]}运算。"
    return polish(preparation + operation + result)


def scalar_synopsis(row, fallback):
    """Return a concise overview; leave form-specific constraints in detail()."""
    form = _scalar_forms().get(row.get("pto_source_form_id"))
    if not form:
        return polish(fallback)
    m, handler = form["mnemonic"], form["semantic_handler"]
    if handler == "ExecuteMaintenance":
        no_args = "该形式没有显式操作数。" if not form["fields"] else ""
        return (
            f"在系统块内同步完成{_MAINTENANCE[m]}维护。{no_args}"
            if m.endswith("IALL")
            else f"在系统块内同步{_MAINTENANCE[m]}。{no_args}"
        )
    if form.get("agu"):
        return memory_synopsis(form["agu"])
    if handler in ("ScalarBinary", "ScalarBinaryW"):
        sentence = _binary(form)
        if sentence:
            return sentence
    return polish(fallback)
