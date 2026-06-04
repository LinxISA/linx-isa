# Load Register Offset

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Load Register Offset &nbsp;|&nbsp;
**Forms:** 15 &nbsp;|&nbsp;
**Unique mnemonics:** 15

</div>

Load instructions with register offsets.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [LB](../instructions/lb.md) | `lb [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->{t, u, Rd}` | 32 | — | Loads a signed 8-bit value from memory. |
| [LBU](../instructions/lbu.md) | `lbu [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->{t, u, Rd}` | 32 | — | Loads a 8-bit value from memory. |
| [LD](../instructions/ld.md) | `ld [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->{t, u, Rd}` | 32 | — | Loads a 64-bit value from memory. |
| [LH](../instructions/lh.md) | `lh [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->{t, u, Rd}` | 32 | — | Loads a signed 16-bit value from memory. |
| [LHU](../instructions/lhu.md) | `lhu [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->{t, u, Rd}` | 32 | — | Loads a 16-bit value from memory. |
| [LW](../instructions/lw.md) | `lw [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->{t, u, Rd}` | 32 | — | Loads a signed 32-bit value from memory. |
| [LWU](../instructions/lwu.md) | `lwu [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->{t, u, Rd}` | 32 | — | Loads a 32-bit value from memory. |
| [PRF](../instructions/prf.md) | `prf [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>]` | 32 | — | Loads a value from memory into a register. |
| [V.LB](../instructions/v_lb.md) | `v.lb<.local> [SrcL, <lc0>, SrcR<<<shamt>], ->Dst` | 64 | — | [64-bit V.] Loads a signed 8-bit value from memory. |

| [V.LBU](../instructions/v_lbu.md) | `v.lbu<.local> [SrcL, <lc0>, SrcR<<<shamt>], ->Dst` | 64 | — | [64-bit V.] Loads a 8-bit value from memory. |

| [V.LD](../instructions/v_ld.md) | `v.ld<.local> [SrcL, <lc0<<3>, SrcR<<<shamt>], ->Dst` | 64 | — | [64-bit V.] Loads a 64-bit value from memory. |

| [V.LH](../instructions/v_lh.md) | `v.lh<.local> [SrcL, <lc0<<1>, SrcR<<<shamt>], ->Dst` | 64 | — | [64-bit V.] Loads a signed 16-bit value from memory. |

| [V.LHU](../instructions/v_lhu.md) | `v.lhu<.local> [SrcL, <lc0<<1>, SrcR<<<shamt>], ->Dst` | 64 | — | [64-bit V.] Loads a 16-bit value from memory. |

| [V.LW](../instructions/v_lw.md) | `v.lw<.local> [SrcL, <lc0<<2>, SrcR<<<shamt>], ->Dst` | 64 | — | [64-bit V.] Loads a signed 32-bit value from memory. |

| [V.LWU](../instructions/v_lwu.md) | `v.lwu<.local> [SrcL, <lc0<<2>, SrcR<<<shamt>], ->Dst` | 64 | — | [64-bit V.] Loads a 32-bit value from memory. |


## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
