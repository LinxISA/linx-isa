# BSTART

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** BSTART &nbsp;|&nbsp;
**Forms:** 20 &nbsp;|&nbsp;
**Unique mnemonics:** 8

</div>

Block split instructions with CALL/RET/commit argument encoding.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [BSTART CALL](../instructions/bstart_call.md) | `BSTART.CALL <br_label>` | 32 | — | Unconditionally transfers to a call block. The instruction preserves `ra`; returning calls require an adjacent `SETRET` or `C.SETRET`. |
| [HL.BSTART CALL](../instructions/hl_bstart_call.md) | `HL.BSTART.CALL <br_label>` | 48 | — | [48-bit HL.] Unconditionally transfers to a call block. The instruction preserves `ra`; returning calls require an adjacent `SETRET` or `C.SETRET`. |
| [HL.BSTART.FP](../instructions/hl_bstart_fp.md) | `HL.BSTART.FP COND, <label>` | 48 | — | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](../instructions/hl_bstart_std.md) | `HL.BSTART.STD CALL, <label>` | 48 | — | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.SYS](../instructions/hl_bstart_sys.md) | `HL.BSTART.SYS FALL<, fixup_label>` | 48 | — | [48-bit HL.] Terminates the current block and begins the next. |
| [L.BSTART.FP](../instructions/l_bstart_fp.md) | `L.BSTART.FP COND, <label>` | 64 | — | Instruction from the BSTART group. |
| [L.BSTART.STD](../instructions/l_bstart_std.md) | `L.BSTART.STD DIRECT, <label>` | 64 | — | Instruction from the BSTART group. |
| [L.BSTART.SYS](../instructions/l_bstart_sys.md) | `L.BSTART.SYS FALL<, fixup_label>` | 64 | — | Instruction from the BSTART group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
