# Floating-point Compare

<div class="insn-header">

<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Group:** Floating-point Compare &nbsp;|&nbsp;
**Forms:** 8 &nbsp;|&nbsp;
**Unique mnemonics:** 8

</div>

Floating-point comparison instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [FEQ](../instructions/feq.md) | `feq.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point equality comparison. Writes 1 if ordered and equal. |
| [FEQS](../instructions/feqs.md) | `feqs.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Instruction from the Floating-point Compare group. |
| [FGE](../instructions/fge.md) | `fge.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point greater-or-equal comparison (ordered). |
| [FGES](../instructions/fges.md) | `fges.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Instruction from the Floating-point Compare group. |
| [FLT](../instructions/flt.md) | `flt.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point less-than comparison (ordered). |
| [FLTS](../instructions/flts.md) | `flts.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Instruction from the Floating-point Compare group. |
| [FNE](../instructions/fne.md) | `fne.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Instruction from the Floating-point Compare group. |
| [FNES](../instructions/fnes.md) | `fnes.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Instruction from the Floating-point Compare group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 13: FSU — Floating-point / SIMD Unit](../index.md)
- [Encoding formats](../encoding.md)
