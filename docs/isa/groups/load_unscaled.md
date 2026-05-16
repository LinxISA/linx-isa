# Load UnScaled

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Load UnScaled &nbsp;|&nbsp;
**Forms:** 16 &nbsp;|&nbsp;
**Unique mnemonics:** 16

</div>

Load instructions with unscaled immediate offsets.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [LDI.U](../instructions/ldi_u.md) | `ldi.u [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [LHI.U](../instructions/lhi_u.md) | `lhi.u [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [LHUI.U](../instructions/lhui_u.md) | `lhui.u [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [LWI.U](../instructions/lwi_u.md) | `lwi.u [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [LWUI.U](../instructions/lwui_u.md) | `lwui.u [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [PRFI.U](../instructions/prfi_u.md) | `prfi.u [SrcL, simm]` | 32 | — | Loads a value from memory into a register. |
| [V.LDI.U](../instructions/v_ldi_u.md) | `v.ldi.u<.local> [SrcL, <lc0<<3>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LDI.U.BRG](../instructions/v_ldi_u_brg.md) | `v.ldi.u.brg<.local> [SrcL, <lc0<<3>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LHI.U](../instructions/v_lhi_u.md) | `v.lhi.u<.local> [SrcL, <lc0<<1>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LHI.U.BRG](../instructions/v_lhi_u_brg.md) | `v.lhi.u.brg<.local> [SrcL, <lc0<<1>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LHUI.U](../instructions/v_lhui_u.md) | `v.lhui.u<.local> [SrcL, <lc0<<1>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LHUI.U.BRG](../instructions/v_lhui_u_brg.md) | `v.lhui.u.brg<.local> [SrcL, <lc0<<1>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LWI.U](../instructions/v_lwi_u.md) | `v.lwi.u<.local> [SrcL, <lc0<<2>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LWI.U.BRG](../instructions/v_lwi_u_brg.md) | `v.lwi.u.brg<.local> [SrcL, <lc0<<2>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LWUI.U](../instructions/v_lwui_u.md) | `v.lwui.u<.local> [SrcL, <lc0<<2>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LWUI.U.BRG](../instructions/v_lwui_u_brg.md) | `v.lwui.u.brg<.local> [SrcL, <lc0<<2>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
