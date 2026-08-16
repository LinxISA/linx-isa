# BSTART

<div class="insn-header">

<span class="ch-tag ch-tag-04">Ch 04</span>
&nbsp; <strong>Block ISA — Block-structured Control Flow</strong> &nbsp;|&nbsp;
**Group:** BSTART &nbsp;|&nbsp;
**Forms:** 21 &nbsp;|&nbsp;
**Unique mnemonics:** 9

</div>

Block split instructions with CALL/RET/commit argument encoding.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [BSTART.CALL](../instructions/bstart_call.md) | `BSTART.CALL <br_label>, <rt_label>, ->ra` | 32 | — | Atomic fused call with independent call-target and return-target fields; transfers to the call block and writes `ra`. This exact aggregate is distinct from the generic bare-call form, which preserves `ra` and requires an adjacent `SETRET` or `C.SETRET`. |
| [BSTART.ICALL](../instructions/bstart_icall.md) | `BSTART.ICALL <rt_label>, ->ra` | 32 | — | Terminates the current block and begins the next. |
| [HL.BSTART CALL](../instructions/hl_bstart_call.md) | `HL.BSTART.CALL <br_label>, <rt_label>, ->ra` | 48 | — | [48-bit HL.] Atomic fused call with independent call-target and return-target fields; transfers to the call block and writes `ra`. This exact aggregate is distinct from the generic bare-call form, which preserves `ra` and requires an adjacent `SETRET` or `C.SETRET`. |
| [HL.BSTART.FP](../instructions/hl_bstart_fp.md) | `HL.BSTART.FP FALL<, fixup_label>` | 48 | — | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](../instructions/hl_bstart_std.md) | `HL.BSTART.STD FALL<, fixup_label>` | 48 | — | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.SYS](../instructions/hl_bstart_sys.md) | `HL.BSTART.SYS FALL<, fixup_label>` | 48 | — | [48-bit HL.] Terminates the current block and begins the next. |
| [L.BSTART.FP](../instructions/l_bstart_fp.md) | `L.BSTART.FP DIRECT, <label>` | 64 | — | Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind. |
| [L.BSTART.STD](../instructions/l_bstart_std.md) | `L.BSTART.STD COND, <label>` | 64 | — | Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind. |
| [L.BSTART.SYS](../instructions/l_bstart_sys.md) | `L.BSTART.SYS FALL<, fixup_label>` | 64 | — | Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 4: Block ISA — Block-structured Control Flow](../index.md)
- [Encoding formats](../encoding.md)
