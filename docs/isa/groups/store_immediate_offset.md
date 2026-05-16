# Store Immediate Offset

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Store Immediate Offset &nbsp;|&nbsp;
**Forms:** 9 &nbsp;|&nbsp;
**Unique mnemonics:** 9

</div>

Store instructions with immediate offsets.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.SDI](../instructions/c_sdi.md) | `c.sdi t#1, [srcL, simm]` | 16 | — | [16-bit C.] Stores a register value to memory. |
| [C.SWI](../instructions/c_swi.md) | `c.swi t#1, [srcL, simm]` | 16 | — | [16-bit C.] Stores a register value to memory. |
| [SBI](../instructions/sbi.md) | `sbi SrcL, [SrcR, simm]` | 32 | — | Stores a register value to memory. |
| [SDI](../instructions/sdi.md) | `sdi SrcL, [SrcR, simm]` | 32 | — | Stores a register value to memory. |
| [SDI.U](../instructions/sdi_u.md) | `sdi.u SrcL, [SrcR, simm]` | 32 | — | Stores a register value to memory. |
| [SHI](../instructions/shi.md) | `shi SrcL, [SrcR, simm]` | 32 | — | Stores a register value to memory. |
| [SHI.U](../instructions/shi_u.md) | `shi.u SrcL, [SrcR, simm]` | 32 | — | Stores a register value to memory. |
| [SWI](../instructions/swi.md) | `swi SrcL, [SrcR, simm]` | 32 | — | Stores a register value to memory. |
| [SWI.U](../instructions/swi_u.md) | `swi.u SrcL, [SrcR, simm]` | 32 | — | Stores a register value to memory. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
