# BSTART

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** BSTART &nbsp;|&nbsp;
**Forms:** 11 &nbsp;|&nbsp;
**Unique mnemonics:** 5

</div>

Block split instructions with CALL/RET/commit argument encoding.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [BSTART CALL](../instructions/bstart_call.md) | `BSTART.CALL, <br_label>, <rt_label>, -> ra` | 32 | — | Terminates the current block and begins the next. |
| [HL.BSTART CALL](../instructions/hl_bstart_call.md) | `HL.BSTART.CALL, <br_label>, <rt_label>, -> ra` | 48 | — | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.FP](../instructions/hl_bstart_fp.md) | `HL.BSTART.FP COND, <label>` | 48 | — | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](../instructions/hl_bstart_std.md) | `HL.BSTART.STD CALL, <label>` | 48 | — | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.SYS](../instructions/hl_bstart_sys.md) | `HL.BSTART.SYS FALL<, fixup_label>` | 48 | — | [48-bit HL.] Terminates the current block and begins the next. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
