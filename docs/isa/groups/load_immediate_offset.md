# Load Immediate Offset

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Load Immediate Offset &nbsp;|&nbsp;
**Forms:** 23 &nbsp;|&nbsp;
**Unique mnemonics:** 23

</div>

Load instructions with immediate offsets.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [C.LDI](../instructions/c_ldi.md) | `c.ldi [srcL, simm], ->t` | 16 | — | [16-bit C.] Loads a value from memory into a register. |
| [C.LWI](../instructions/c_lwi.md) | `c.lwi [srcL, simm], ->t` | 16 | — | [16-bit C.] Loads a value from memory into a register. |
| [LBI](../instructions/lbi.md) | `lbi [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [LBUI](../instructions/lbui.md) | `lbui [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [LDI](../instructions/ldi.md) | `ldi [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [LHI](../instructions/lhi.md) | `lhi [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [LHUI](../instructions/lhui.md) | `lhui [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [LWI](../instructions/lwi.md) | `lwi [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [LWUI](../instructions/lwui.md) | `lwui [SrcL, simm], ->{t, u, Rd}` | 32 | — | Loads a value from memory into a register. |
| [V.LBI](../instructions/v_lbi.md) | `v.lbi<.local> [SrcL, <lc0>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LBI.BRG](../instructions/v_lbi_brg.md) | `v.lbi.brg<.local> [SrcL, <lc0>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LBUI](../instructions/v_lbui.md) | `v.lbui<.local> [SrcL, <lc0>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LBUI.BRG](../instructions/v_lbui_brg.md) | `v.lbui.brg<.local> [SrcL, <lc0>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LDI](../instructions/v_ldi.md) | `v.ldi<.local> [SrcL, <lc0<<3>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LDI.BRG](../instructions/v_ldi_brg.md) | `v.ldi.brg<.local> [SrcL, <lc0<<3>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LHI](../instructions/v_lhi.md) | `v.lhi<.local> [SrcL, <lc0<<1>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LHI.BRG](../instructions/v_lhi_brg.md) | `v.lhi.brg<.local> [SrcL, <lc0<<1>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LHUI](../instructions/v_lhui.md) | `v.lhui<.local> [SrcL, <lc0<<1>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LHUI.BRG](../instructions/v_lhui_brg.md) | `v.lhui.brg<.local> [SrcL, <lc0<<1>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LWI](../instructions/v_lwi.md) | `v.lwi<.local> [SrcL, <lc0<<2>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LWI.BRG](../instructions/v_lwi_brg.md) | `v.lwi.brg<.local> [SrcL, <lc0<<2>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LWUI](../instructions/v_lwui.md) | `v.lwui<.local> [SrcL, <lc0<<2>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |
| [V.LWUI.BRG](../instructions/v_lwui_brg.md) | `v.lwui.brg<.local> [SrcL, <lc0<<2>, simm], ->Dst` | 64 | — | [64-bit V.] Loads a value from memory into a register. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
