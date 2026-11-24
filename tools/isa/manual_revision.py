#!/usr/bin/env python3
"""HTML-manual projection rules for the revised LinxISA 0.59.1 catalog."""

from __future__ import annotations


REMOVED_BLOCK_FORMS = frozenset(
    {
        "B.TEXT",
        "BSTART.MPAR",
        "BSTART.MSEQ",
        "BSTART.VPAR",
        "BSTART.VSEQ",
        "C.BSTART.MPAR",
        "C.BSTART.MSEQ",
        "C.BSTART.VPAR",
        "C.BSTART.VSEQ",
    }
)


def is_removed_form(mnemonic: str) -> bool:
    name = mnemonic.upper()
    return name.startswith("V.") or name in REMOVED_BLOCK_FORMS


__all__ = ["REMOVED_BLOCK_FORMS", "is_removed_form"]
