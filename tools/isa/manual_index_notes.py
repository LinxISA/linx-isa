#!/usr/bin/env python3
"""Purpose-first Chinese synopses for mnemonic-index entries with weak source intros."""

from __future__ import annotations

from typing import Mapping, Any


INDEX_NOTES: dict[str, str] = {
    "B.DATR": "为当前块登记 Tile 布局、数据类型、填充值以及舍入、饱和、规范化和执行掩码控制。",
    "B.IOR": "按顺序绑定至多三个 GPR 输入和一个 GPR 输出，并可声明最后一项包含 GPR 执行掩码。",
    "B.IOS": "把绝对编号的 Core 内 Shared Tile 寄存器绑定为源或目的，并用四 PE 掩码限定参与者。",
    "B.IOT": "把相对编号的 Local Tile 源和重命名目的按序绑定到当前块，可选择复用源或标记其最后一次使用。",
    "BC.IALL": "同步失效块头缓存中的全部条目；0.59.1 形式没有显式操作数。",
    "BSE": "未启用 MSGB 时发送 SendEvent 请求；启用 MSGB 时原子受理暂存的消息。",
    "BSTART": "提交此前块后启动标准块，并建立直接或条件 PC 相对后继。",
    "BSTART.FP": "提交此前块并启动浮点块，选择顺序、直接、条件、间接、调用或返回后继。",
    "BSTART.GMOV": "启动 GMOV 块，按参与掩码把同一核内对端 PE 的本地 Tile 分片复制到所选目标。",
    "BSTART.ICALL": "启动间接调用块，把旧块的间接目标写入新块后继，同时把独立的返回地址写入 ra。",
    "BSTART.MPAR": "启动并行 MPAR 块，并选择块内向量寄存器档位 VS8 或 VS16。",
    "BSTART.MSEQ": "启动顺序 MSEQ 块，并选择块内向量寄存器档位 VS8 或 VS16。",
    "BSTART.STD": "提交此前块并启动标准标量块，选择顺序、直接、条件、间接、调用或返回后继。",
    "BSTART.SYS": "提交此前块并启动顺序执行的系统块。",
    "BSTART.TEPL": "用 Mode 和 Function 选择 VEC 或 SFU 的 Tile 操作，用 DataType 指定元素类型。",
    "BSTART.VPAR": "启动并行 SIMT 向量块，并选择块内向量寄存器档位 VS8 或 VS16。",
    "BSTART.VSEQ": "启动顺序 SIMT 向量块，并选择块内向量寄存器档位 VS8 或 VS16。",
    "BSTOP": "提交当前块，并跳转到块头选定的后继地址。",
    "C.BSTART": "以 16 位压缩编码启动标准块，并建立直接或条件 PC 相对后继。",
    "C.BSTART.FP": "以 16 位压缩编码启动浮点块，后继仅可为顺序、间接或返回。",
    "C.BSTART.MPAR": "以 16 位压缩编码启动顺序后继的并行 MPAR 块。",
    "C.BSTART.MSEQ": "以 16 位压缩编码启动顺序后继的 MSEQ 块。",
    "C.BSTART.STD": "以 16 位压缩编码启动标准标量块，后继仅可为顺序、间接或返回。",
    "C.BSTART.SYS": "以 16 位压缩编码启动固定顺序后继的系统块。",
    "C.BSTART.VPAR": "以 16 位压缩编码启动固定顺序后继的并行 SIMT 向量块。",
    "C.BSTART.VSEQ": "以 16 位压缩编码启动固定顺序后继的顺序 SIMT 向量块。",
    "C.BSTOP": "以 16 位压缩编码提交当前块，并跳转到块头选定的后继地址。",
    "DMA.FREE.L": "仅保留 DMA.FREE.L 的编码与操作数字段；0.59.1 尚未实现，执行必须在读取操作数或产生状态效果前拒绝。",
    "DMA.FREE.S": "仅保留 DMA.FREE.S 的编码与操作数字段；0.59.1 尚未实现，执行必须在读取操作数或产生状态效果前拒绝。",
    "HL.BSTART CALL": "以两个独立 PC 相对位移分别建立调用目标和返回地址，并原子地启动调用块、写入 ra。",
    "HL.BSTART.FP": "以 48 位块头启动浮点块，可携带较长的直接、条件或调用目标以及顺序后继修正地址。",
    "HL.BSTART.STD": "以 48 位块头启动标准标量块，可携带较长的直接、条件或调用目标以及顺序后继修正地址。",
    "HL.BSTART.SYS": "以 48 位块头启动顺序系统块，并可携带后继修正地址。",
    "HL.CCAT": "将 SrcL、SrcR 分别作为高、低半部拼成 128 位值，逻辑右移 shamt 位；低 64 位先写 Dst0，高 64 位再写 Dst1。",
    "HL.CCATW": "取 SrcL 和 SrcR 的低 32 位，分别作为高、低半部拼成 64 位值，再逻辑右移 shamt 位。结果的低、高 32 位分别符号扩展，依次写入 Dst0、Dst1。",
    "IC.IALL": "同步失效指令缓存中的全部条目；0.59.1 形式没有显式操作数。",
    "L.BSTART.FP": "以 64 位块头启动浮点块并携带长距离后继；CALL 本身不写 ra，返回地址须由 SETRET 预先设置。",
    "L.BSTART.STD": "以 64 位块头启动标准标量块并携带长距离后继；CALL 本身不写 ra，返回地址须由 SETRET 预先设置。",
    "L.BSTART.SYS": "以 64 位块头启动顺序系统块，并可携带长距离后继修正地址。",
    "L.BSTOP": "以 64 位编码提交当前块，并跳转到块头选定的后继地址。",
    "MCOPY.DL": "仅保留 MCOPY.DL 的编码与操作数字段；0.59.1 尚未实现，执行必须在读取地址寄存器或产生状态效果前拒绝。",
    "MCOPY.DS": "仅保留 MCOPY.DS 的编码与操作数字段；0.59.1 尚未实现，执行必须在读取地址寄存器或产生状态效果前拒绝。",
    "PRF": "由两个标量源和移位量形成地址，发出不绑定结果、无目的写回的预取提示。",
    "PRFI.U": "由标量基址和有符号立即数形成地址，发出不绑定结果、无目的写回的预取提示。",
    "TLB.IA": "按 SrcL 低 16 位给出的 ASID，同步失效该地址空间的 TLB 条目。",
    "TLB.IALL": "同步失效全部 TLB 条目。",
    "TLB.IAV": "按 SrcL 中的规范 48 位虚拟地址和 ASID，同步失效对应的 TLB 条目。",
    "TLB.IV": "按 SrcL 中的规范 48 位虚拟地址，同步失效对应的 TLB 条目。",
    "V.FCVT": "逐活动通道把源浮点值从 st 类型转换为 dt 浮点类型，并写入向量目的。",
    "V.FCVTI": "逐活动通道把 st 浮点值转换为 dt 整数类型，并写入向量目的。",
    "V.ICVT": "逐活动通道把源整数从 st 整数类型转换为 dt 整数类型，并写入向量目的。",
    "V.ICVTF": "逐活动通道把 st 整数值转换为 dt 浮点类型，并写入向量目的。",
    "XB": "登记扩展自有的跨块传送编码；PTO 0.59.1 在解释字段或产生任何架构效果前拒绝执行。",
}


def index_note(row_or_mnemonic: str | Mapping[str, Any]) -> str | None:
    """Return the reviewed index synopsis for a catalog row or mnemonic."""

    if isinstance(row_or_mnemonic, str):
        mnemonic = row_or_mnemonic
    else:
        mnemonic = str(row_or_mnemonic.get("mnemonic", ""))
    return INDEX_NOTES.get(mnemonic)


def covered_mnemonics() -> tuple[str, ...]:
    """Return stable inventory used by generator and audit tests."""

    return tuple(sorted(INDEX_NOTES))
