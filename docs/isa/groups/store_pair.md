# Store Pair

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Store Pair &nbsp;|&nbsp;
**Forms:** 14 &nbsp;|&nbsp;
**Unique mnemonics:** 14

</div>

Paired-store instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.SBIP](../instructions/hl_sbip.md) | `hl.sbip SrcD, SrcD1, [SrcR, simm]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SBP](../instructions/hl_sbp.md) | `hl.sbp SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SDIP](../instructions/hl_sdip.md) | `hl.sdip SrcD, SrcD1, [SrcR, simm]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SDIP.U](../instructions/hl_sdip_u.md) | `hl.sdip.u SrcD, SrcD1, [SrcR, simm]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SDP](../instructions/hl_sdp.md) | `hl.sdp SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}><<3]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SDP.U](../instructions/hl_sdp_u.md) | `hl.sdp.u SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SHIP](../instructions/hl_ship.md) | `hl.ship SrcD, SrcD1, [SrcR, simm]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SHIP.U](../instructions/hl_ship_u.md) | `hl.ship.u SrcD, SrcD1, [SrcR, simm]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SHP](../instructions/hl_shp.md) | `hl.shp SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}><<1]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SHP.U](../instructions/hl_shp_u.md) | `hl.shp.u SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SWIP](../instructions/hl_swip.md) | `hl.swip SrcD, SrcD1, [SrcR, simm]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SWIP.U](../instructions/hl_swip_u.md) | `hl.swip.u SrcD, SrcD1, [SrcR, simm]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SWP](../instructions/hl_swp.md) | `hl.swp SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}><<2]` | 48 | — | [48-bit HL.] Stores a register value to memory. |
| [HL.SWP.U](../instructions/hl_swp_u.md) | `hl.swp.u SrcD, SrcD1, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 48 | — | [48-bit HL.] Stores a register value to memory. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
