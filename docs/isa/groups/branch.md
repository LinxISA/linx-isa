# Branch

<div class="insn-header">

<span class="ch-tag ch-tag-16">Ch 16</span>
&nbsp; <strong>BRU — Branch and Compare</strong> &nbsp;|&nbsp;
**Group:** Branch &nbsp;|&nbsp;
**Forms:** 10 &nbsp;|&nbsp;
**Unique mnemonics:** 10

</div>

Conditional PC-relative branch instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [B.EQ](../instructions/b_eq.md) | `b.eq SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL equals SrcR. |
| [B.GE](../instructions/b_ge.md) | `b.ge SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL is greater than or equal to SrcR (signed). |
| [B.GEU](../instructions/b_geu.md) | `b.geu SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL is greater than or equal to SrcR (unsigned). |
| [B.LT](../instructions/b_lt.md) | `b.lt SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL is less than SrcR (signed). |
| [B.LTU](../instructions/b_ltu.md) | `b.ltu SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL is less than SrcR (unsigned). |
| [B.NE](../instructions/b_ne.md) | `b.ne SrcL, SrcR, label` | 32 | — | Conditional branch taken when SrcL not equal to SrcR. |
| [B.NZ](../instructions/b_nz.md) | `b.nz label` | 32 | — | Conditional PC-relative branch. |
| [B.Z](../instructions/b_z.md) | `b.z label` | 32 | — | Conditional PC-relative branch. |
| [J](../instructions/j.md) | `j label` | 32 | — | Unconditional PC-relative jump to a target label. |
| [JR](../instructions/jr.md) | `jr SrcL, label` | 32 | — | Jump register: PC-relative or register-based jump to the address in a register. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 16: BRU — Branch and Compare](../index.md)
- [Encoding formats](../encoding.md)
