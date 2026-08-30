# STA/BASE_IMM

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** STA/BASE_IMM &nbsp;|&nbsp;
**Forms:** 9 &nbsp;|&nbsp;
**Unique mnemonics:** 9

</div>

Instructions in the **STA/BASE_IMM** group of the LinxISA v0.58.5 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.SDI](../instructions/c_sdi.md) | `c.sdi t#1, [srcL, simm]` | 16 | — | C.SDI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [C.SWI](../instructions/c_swi.md) | `c.swi t#1, [srcL, simm]` | 16 | — | C.SWI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [SBI](../instructions/sbi.md) | `sbi SrcL, [SrcR, simm]` | 32 | — | SBI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [SDI](../instructions/sdi.md) | `sdi SrcL, [SrcR, simm]` | 32 | — | SDI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [SDI.U](../instructions/sdi_u.md) | `sdi.u SrcL, [SrcR, simm]` | 32 | — | SDI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [SHI](../instructions/shi.md) | `shi SrcL, [SrcR, simm]` | 32 | — | SHI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [SHI.U](../instructions/shi_u.md) | `shi.u SrcL, [SrcR, simm]` | 32 | — | SHI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [SWI](../instructions/swi.md) | `swi SrcL, [SrcR, simm]` | 32 | — | SWI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [SWI.U](../instructions/swi_u.md) | `swi.u SrcL, [SrcR, simm]` | 32 | — | SWI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
