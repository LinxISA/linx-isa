#!/usr/bin/env python3
"""Mnemonic-specific index synopses for demonstrably copied functional prose.

The original tagged Chinese articles remain untouched.  This module only
replaces the one-sentence alphabet/class-index synopsis when a shared first
sentence hides or contradicts the operation selected by the mnemonic.
"""

from __future__ import annotations


_SCALAR_BRU = {
    "HL.SETC.LTI": "用有符号小于比较标量寄存器与移位后的 24 位立即数，并把比较结果提交给当前条件指令束。",
    "HL.SETC.ORI": "对标量寄存器与移位后的 24 位立即数作按位或，并在结果非零时向当前条件指令束提交 1；不写寄存器。",
}

def family_index_synopsis(mnemonic: str) -> str:
    """Return a source-verified index override, or an empty string."""
    return _SCALAR_BRU.get(mnemonic, "")


def overridden_mnemonics() -> frozenset[str]:
    return frozenset(_SCALAR_BRU)


__all__ = ["family_index_synopsis", "overridden_mnemonics"]
