# STA/PAIR

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** STA/PAIR &nbsp;|&nbsp;
**Forms:** 14 &nbsp;|&nbsp;
**Unique mnemonics:** 14

</div>

Instructions in the **STA/PAIR** group of the LinxISA v0.58.3 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.SBIP](../instructions/hl_sbip.md) | `hl.sbip SrcD, SrcD1, [SrcR, simm]` | 48 | — | HL.SBIP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 1-byte values. |
| [HL.SBP](../instructions/hl_sbp.md) | `hl.sbp SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 48 | — | HL.SBP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 1-byte values. |
| [HL.SDIP](../instructions/hl_sdip.md) | `hl.sdip SrcD, SrcD1, [SrcR, simm]` | 48 | — | HL.SDIP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 8-byte values. |
| [HL.SDIP.U](../instructions/hl_sdip_u.md) | `hl.sdip.u SrcD, SrcD1, [SrcR, simm]` | 48 | — | HL.SDIP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 8-byte values. |
| [HL.SDP](../instructions/hl_sdp.md) | `hl.sdp SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}><<3]` | 48 | — | HL.SDP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 8-byte values. |
| [HL.SDP.U](../instructions/hl_sdp_u.md) | `hl.sdp.u SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 48 | — | HL.SDP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 8-byte values. |
| [HL.SHIP](../instructions/hl_ship.md) | `hl.ship SrcD, SrcD1, [SrcR, simm]` | 48 | — | HL.SHIP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 2-byte values. |
| [HL.SHIP.U](../instructions/hl_ship_u.md) | `hl.ship.u SrcD, SrcD1, [SrcR, simm]` | 48 | — | HL.SHIP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 2-byte values. |
| [HL.SHP](../instructions/hl_shp.md) | `hl.shp SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}><<1]` | 48 | — | HL.SHP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 2-byte values. |
| [HL.SHP.U](../instructions/hl_shp_u.md) | `hl.shp.u SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 48 | — | HL.SHP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 2-byte values. |
| [HL.SWIP](../instructions/hl_swip.md) | `hl.swip SrcD, SrcD1, [SrcR, simm]` | 48 | — | HL.SWIP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 4-byte values. |
| [HL.SWIP.U](../instructions/hl_swip_u.md) | `hl.swip.u SrcD, SrcD1, [SrcR, simm]` | 48 | — | HL.SWIP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 4-byte values. |
| [HL.SWP](../instructions/hl_swp.md) | `hl.swp SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}><<2]` | 48 | — | HL.SWP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 4-byte values. |
| [HL.SWP.U](../instructions/hl_swp_u.md) | `hl.swp.u SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 48 | — | HL.SWP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 4-byte values. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
