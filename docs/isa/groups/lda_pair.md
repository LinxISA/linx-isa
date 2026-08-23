# LDA/PAIR

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** LDA/PAIR &nbsp;|&nbsp;
**Forms:** 19 &nbsp;|&nbsp;
**Unique mnemonics:** 19

</div>

Instructions in the **LDA/PAIR** group of the LinxISA v0.58.3 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.LBIP](../instructions/hl_lbip.md) | `hl.lbip [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LBIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 1-byte values. |
| [HL.LBP](../instructions/hl_lbp.md) | `hl.lbp [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LBP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 1-byte values. |
| [HL.LBUIP](../instructions/hl_lbuip.md) | `hl.lbuip [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LBUIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 1-byte values. |
| [HL.LBUP](../instructions/hl_lbup.md) | `hl.lbup [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LBUP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 1-byte values. |
| [HL.LDIP](../instructions/hl_ldip.md) | `hl.ldip [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LDIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 8-byte values. |
| [HL.LDIP.U](../instructions/hl_ldip_u.md) | `hl.ldip.u [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LDIP.U snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 8-byte values. |
| [HL.LDP](../instructions/hl_ldp.md) | `hl.ldp [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LDP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 8-byte values. |
| [HL.LHIP](../instructions/hl_lhip.md) | `hl.lhip [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LHIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LHIP.U](../instructions/hl_lhip_u.md) | `hl.lhip.u [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LHIP.U snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LHP](../instructions/hl_lhp.md) | `hl.lhp [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LHP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LHUIP](../instructions/hl_lhuip.md) | `hl.lhuip [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LHUIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LHUIP.U](../instructions/hl_lhuip_u.md) | `hl.lhuip.u [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LHUIP.U snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LHUP](../instructions/hl_lhup.md) | `hl.lhup [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LHUP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LWIP](../instructions/hl_lwip.md) | `hl.lwip [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LWIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.LWIP.U](../instructions/hl_lwip_u.md) | `hl.lwip.u [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LWIP.U snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.LWP](../instructions/hl_lwp.md) | `hl.lwp [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LWP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.LWUIP](../instructions/hl_lwuip.md) | `hl.lwuip [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LWUIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.LWUIP.U](../instructions/hl_lwuip_u.md) | `hl.lwuip.u [SrcL, simm], ->Dst0, Dst1` | 48 | — | HL.LWUIP.U snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.LWUP](../instructions/hl_lwup.md) | `hl.lwup [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | HL.LWUP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
