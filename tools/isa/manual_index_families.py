#!/usr/bin/env python3
"""Mnemonic-specific index synopses for demonstrably copied functional prose.

The original tagged Chinese articles remain untouched.  This module only
replaces the one-sentence alphabet/class-index synopsis when a shared first
sentence hides or contradicts the operation selected by the mnemonic.
"""

from __future__ import annotations


_SHUFFLE = {
    "V.SHFL.BFLY": "用 SrcP 掩码与当前通道 ID 异或确定源通道，并把该通道的 SrcL 数据搬到当前通道。",
    "V.SHFL.DOWN": "在 SrcR 指定的 通道重排范围内，用 SrcP 偏移量加到当前通道 ID 以确定源通道。",
    "V.SHFL.IDX": "在 SrcR 指定的 通道重排范围内，用 SrcP 索引值确定源通道并搬移 SrcL 数据。",
    "V.SHFL.UP": "在 SrcR 指定的 通道重排范围内，从当前通道 ID 减去 SrcP 偏移量以确定源通道。",
    "V.SHFLI.BFLY": "用立即数掩码与当前通道 ID 异或确定源通道，并把该通道的 SrcL 数据搬到当前通道。",
    "V.SHFLI.DOWN": "在 SrcR 指定的 通道重排范围内，用立即数偏移量加到当前通道 ID 以确定源通道。",
    "V.SHFLI.IDX": "在 SrcR 指定的 通道重排范围内，用立即数索引值确定源通道并搬移 SrcL 数据。",
    "V.SHFLI.UP": "在 SrcR 指定的 通道重排范围内，从当前通道 ID 减去立即数偏移量以确定源通道。",
}

_SCALAR_BRU = {
    "HL.SETC.LTI": "用有符号小于比较标量寄存器与移位后的 24 位立即数，并把比较结果提交给当前条件指令束。",
    "HL.SETC.ORI": "对标量寄存器与移位后的 24 位立即数作按位或，并在结果非零时向当前条件指令束提交 1；不写寄存器。",
}

_ATOMIC = {
    "V.LD.MIN": "逐活动通道执行 64 位 原子有符号最小值读改写，并把加载的原值写入目的寄存器。",
}

_BRG = frozenset(
    {
        "V.LB.BRG",
        "V.LBI.BRG",
        "V.LBU.BRG",
        "V.LBUI.BRG",
        "V.LD.BRG",
        "V.LDI.BRG",
        "V.LDI.U.BRG",
        "V.LH.BRG",
        "V.LHI.BRG",
        "V.LHI.U.BRG",
        "V.LHU.BRG",
        "V.LHUI.BRG",
        "V.LHUI.U.BRG",
        "V.LW.BRG",
        "V.LWI.BRG",
        "V.LWI.U.BRG",
        "V.LWU.BRG",
        "V.LWUI.BRG",
        "V.LWUI.U.BRG",
        "V.SB.BRG",
        "V.SBI.BRG",
        "V.SD.BRG",
        "V.SD.U.BRG",
        "V.SDI.BRG",
        "V.SDI.U.BRG",
        "V.SH.BRG",
        "V.SH.U.BRG",
        "V.SHI.BRG",
        "V.SHI.U.BRG",
        "V.SW.BRG",
        "V.SW.U.BRG",
        "V.SWI.BRG",
        "V.SWI.U.BRG",
    }
)

_MEMORY = {
    "LB": (8, "有符号"),
    "LBU": (8, "无符号"),
    "LH": (16, "有符号"),
    "LHU": (16, "无符号"),
    "LW": (32, "有符号"),
    "LWU": (32, "无符号"),
    "LD": (64, ""),
    "SB": (8, ""),
    "SH": (16, ""),
    "SW": (32, ""),
    "SD": (64, ""),
}


def _brg_synopsis(mnemonic: str) -> str:
    body = mnemonic.removeprefix("V.").removesuffix(".BRG")
    unscaled = body.endswith(".U")
    body = body.removesuffix(".U")
    immediate = body.endswith("I")
    root = body[:-1] if immediate else body
    width, signedness = _MEMORY[root]
    qualifier = f"{signedness} {width} 位" if signedness else f" {width} 位"
    if root.startswith("L"):
        if immediate:
            text = f"按 v0.59.1 Sail 阶段模型，从一个有效地址加载{qualifier}数据并广播到活动通道"
        else:
            text = f"按 v0.59.1 Sail 阶段模型，用第 0 通道的索引形成单一地址，加载{qualifier}数据并广播到活动通道"
    elif immediate:
        text = f"按 v0.59.1 Sail 阶段模型，让各活动通道依次向同一有效地址存储{qualifier}数据"
    else:
        text = f"按 v0.59.1 Sail 阶段模型，用第 0 通道的索引形成单一地址，并用第 0 通道的数据存储{qualifier}数据"
    if unscaled:
        text += "；.U 当前复用对应的缩放处理"
    return text + "；BRG 的最终芯片契约尚未冻结。"


def family_index_synopsis(mnemonic: str) -> str:
    """Return a source-verified index override, or an empty string."""
    if mnemonic in _BRG:
        return _brg_synopsis(mnemonic)
    return (
        _SCALAR_BRU.get(mnemonic) or _SHUFFLE.get(mnemonic) or _ATOMIC.get(mnemonic, "")
    )


def overridden_mnemonics() -> frozenset[str]:
    return _BRG | frozenset(_SCALAR_BRU) | frozenset(_SHUFFLE) | frozenset(_ATOMIC)


__all__ = ["family_index_synopsis", "overridden_mnemonics"]
