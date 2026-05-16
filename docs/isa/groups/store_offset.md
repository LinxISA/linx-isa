# Store Offset

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Store Offset &nbsp;|&nbsp;
**Forms:** 14 &nbsp;|&nbsp;
**Unique mnemonics:** 14

</div>

Store instructions with register offsets.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [V.SBI](../instructions/v_sbi.md) | `v.sbi<.local> SrcL, [SrcR, <lc0>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SBI.BRG](../instructions/v_sbi_brg.md) | `v.sbi.brg<.local> SrcL, [SrcR, <lc0>,  simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SDI](../instructions/v_sdi.md) | `v.sdi<.local> SrcL, [SrcR, <lc0<3>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SDI.BRG](../instructions/v_sdi_brg.md) | `v.sdi.brg<.local> SrcL, [SrcR, <lc0<<3>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SDI.U](../instructions/v_sdi_u.md) | `v.sdi.u<.local> SrcL, [SrcR, <lc0<<3>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SDI.U.BRG](../instructions/v_sdi_u_brg.md) | `v.sdi.u.brg<.local> SrcL, [SrcR, <lc0<<3>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SHI](../instructions/v_shi.md) | `v.shi<.local> SrcL, [SrcR, <lc0<<1>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SHI.BRG](../instructions/v_shi_brg.md) | `v.shi.brg<.local> SrcL, [SrcR, <lc0<<1>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SHI.U](../instructions/v_shi_u.md) | `v.shi.u<.local> SrcL, [SrcR, <lc0<<1>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SHI.U.BRG](../instructions/v_shi_u_brg.md) | `v.shi.u.brg<.local> SrcL, [SrcR, <lc0<<1>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SWI](../instructions/v_swi.md) | `v.swi<.local> SrcL, [SrcR, <lc0<<2>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SWI.BRG](../instructions/v_swi_brg.md) | `v.swi.brg<.local> SrcL, [SrcR, <lc0<<2>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SWI.U](../instructions/v_swi_u.md) | `v.swi.u<.local> SrcL, [SrcR, <lc0<<2>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |
| [V.SWI.U.BRG](../instructions/v_swi_u_brg.md) | `v.swi.u.brg<.local> SrcL, [SrcR, <lc0<<2>, simm]` | 64 | — | [64-bit V.] Stores a register value to memory. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
