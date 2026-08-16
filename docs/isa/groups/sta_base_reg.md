# STA/BASE_REG

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** STA/BASE_REG &nbsp;|&nbsp;
**Forms:** 7 &nbsp;|&nbsp;
**Unique mnemonics:** 7

</div>

Instructions in the **STA/BASE_REG** group of the LinxISA v0.58.1 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [SB](../instructions/sb.md) | `sb SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 32 | — | SB snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [SD](../instructions/sd.md) | `sd SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<3]` | 32 | — | SD snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [SD.U](../instructions/sd_u.md) | `sd.u SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 32 | — | SD.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [SH](../instructions/sh.md) | `sh SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<1]` | 32 | — | SH snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [SH.U](../instructions/sh_u.md) | `sh.u SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 32 | — | SH.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [SW](../instructions/sw.md) | `sw SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<2]` | 32 | — | SW snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [SW.U](../instructions/sw_u.md) | `sw.u SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 32 | — | SW.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
