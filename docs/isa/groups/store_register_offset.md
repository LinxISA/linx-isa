# Store Register Offset

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Store Register Offset &nbsp;|&nbsp;
**Forms:** 21 &nbsp;|&nbsp;
**Unique mnemonics:** 21

</div>

Store instructions with register offsets.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [SB](../instructions/sb.md) | `sb SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 32 | — | Stores a register value to memory. |
| [SD](../instructions/sd.md) | `sd SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<3]` | 32 | — | Stores a register value to memory. |
| [SD.U](../instructions/sd_u.md) | `sd.u SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 32 | — | Stores a register value to memory. |
| [SH](../instructions/sh.md) | `sh SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<1]` | 32 | — | Stores a register value to memory. |
| [SH.U](../instructions/sh_u.md) | `sh.u SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 32 | — | Stores a register value to memory. |
| [SW](../instructions/sw.md) | `sw SrcD, [SrcL, SrcR<{.sw,.uw,.neg}><<2]` | 32 | — | Stores a register value to memory. |
| [SW.U](../instructions/sw_u.md) | `sw.u SrcD, [SrcL, SrcR<{.sw,.uw,.neg}>]` | 32 | — | Stores a register value to memory. |
| [V.SB](../instructions/v_sb.md) | `v.sb<.local> SrcD.<T1>, [SrcL, <lc0>, SrcR.<T2><<<shamt>]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SB.BRG](../instructions/v_sb_brg.md) | `v.sb.brg<.local> SrcD.<T1>, [SrcL, <lc0>, SrcR.<T2><<<shamt>]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SD](../instructions/v_sd.md) | `v.sd<.local> SrcD.<T1>, [SrcL, <lc0<<3>, SrcR.<T2><<(3+shamt)]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SD.BRG](../instructions/v_sd_brg.md) | `v.sd.brg<.local> SrcD.<T1>, [SrcL, <lc0<<3>, SrcR.<T2><<(3+shamt)]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SD.U](../instructions/v_sd_u.md) | `v.sd.u<.local> SrcD.<T1>, [SrcL, <lc0<<3>, SrcR.<T2><<<shamt>]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SD.U.BRG](../instructions/v_sd_u_brg.md) | `v.sd.u.brg<.local> SrcD.<T1>, [SrcL, <lc0<<3>, SrcR.<T2><<<shamt>]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SH](../instructions/v_sh.md) | `v.sh<.local> SrcD.<T1>, [SrcL, <lc0<<1>, SrcR.<T2><<(1+shamt)]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SH.BRG](../instructions/v_sh_brg.md) | `v.sh.brg<.local> SrcD.<T1>, [SrcL, <lc0<<1>, SrcR.<T2><<(1+shamt)]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SH.U](../instructions/v_sh_u.md) | `v.sh.u<.local> SrcD.<T1>, [SrcL, <lc0<<1>, SrcR.<T2><<<shamt>]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SH.U.BRG](../instructions/v_sh_u_brg.md) | `v.sh.u.brg<.local> SrcD.<T1>, [SrcL, <lc0<<1>, SrcR.<T2><<<shamt>]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SW](../instructions/v_sw.md) | `v.sw<.local> SrcD.<T1>, [SrcL, <lc0<<2>, SrcR.<T2><<(2+shamt)]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SW.BRG](../instructions/v_sw_brg.md) | `v.sw.brg<.local> SrcD.<T1>, [SrcL, <lc0<<2>, SrcR.<T2><<(2+shamt)]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SW.U](../instructions/v_sw_u.md) | `v.sw.u<.local> SrcD.<T1>, [SrcL, <lc0<<2>, SrcR.<T2><<<shamt>]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SW.U.BRG](../instructions/v_sw_u_brg.md) | `v.sw.u.brg<.local> SrcD.<T1>, [SrcL, <lc0<<2>, SrcR.<T2><<<shamt>]` | 64 | — | [64-bit V.] Stores a register value to memory. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
