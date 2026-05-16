# Load Pair

<div class="insn-header">

<span class="ch-tag ch-tag-11">Ch 11</span>
&nbsp; <strong>AGU — Address Generation Unit</strong> &nbsp;|&nbsp;
**Group:** Load Pair &nbsp;|&nbsp;
**Forms:** 19 &nbsp;|&nbsp;
**Unique mnemonics:** 19

</div>

Paired-load instructions that read two consecutive values.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [HL.LBIP](../instructions/hl_lbip.md) | `hl.lbip [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBP](../instructions/hl_lbp.md) | `hl.lbp [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBUIP](../instructions/hl_lbuip.md) | `hl.lbuip [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBUP](../instructions/hl_lbup.md) | `hl.lbup [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDIP](../instructions/hl_ldip.md) | `hl.ldip [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDIP.U](../instructions/hl_ldip_u.md) | `hl.ldip.u [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDP](../instructions/hl_ldp.md) | `hl.ldp [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHIP](../instructions/hl_lhip.md) | `hl.lhip [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHIP.U](../instructions/hl_lhip_u.md) | `hl.lhip.u [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHP](../instructions/hl_lhp.md) | `hl.lhp [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUIP](../instructions/hl_lhuip.md) | `hl.lhuip [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUIP.U](../instructions/hl_lhuip_u.md) | `hl.lhuip.u [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUP](../instructions/hl_lhup.md) | `hl.lhup [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWIP](../instructions/hl_lwip.md) | `hl.lwip [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWIP.U](../instructions/hl_lwip_u.md) | `hl.lwip.u [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWP](../instructions/hl_lwp.md) | `hl.lwp [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUIP](../instructions/hl_lwuip.md) | `hl.lwuip [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUIP.U](../instructions/hl_lwuip_u.md) | `hl.lwuip.u [SrcL, simm], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUP](../instructions/hl_lwup.md) | `hl.lwup [SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>], ->Dst0, Dst1` | 48 | — | [48-bit HL.] Loads a value from memory into a register. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 11: AGU — Address Generation Unit](../index.md)
- [Encoding formats](../encoding.md)
