# FSU

<div class="insn-header">

<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Group:** FSU &nbsp;|&nbsp;
**Forms:** 30 &nbsp;|&nbsp;
**Unique mnemonics:** 30

</div>

Instructions in the **FSU** group of the LinxISA v0.58.3 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [FABS](../instructions/fabs.md) | `fabs.{T} SrcL, ->{t, u, Rd}` | 32 | — | Floating-point absolute value. |
| [FADD](../instructions/fadd.md) | `fadd.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point addition. |
| [FCVT](../instructions/fcvt.md) | `fcvt.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | Floating-point format conversion. |
| [FCVTA](../instructions/fcvta.md) | `fcvta.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | FCVTA converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-away mode. |
| [FCVTM](../instructions/fcvtm.md) | `fcvtm.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | FCVTM converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-down mode. |
| [FCVTN](../instructions/fcvtn.md) | `fcvtn.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | FCVTN converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-nearest mode. |
| [FCVTP](../instructions/fcvtp.md) | `fcvtp.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | FCVTP converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-up mode. |
| [FCVTZ](../instructions/fcvtz.md) | `fcvtz.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | FCVTZ converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-toward-zero mode. |
| [FDIV](../instructions/fdiv.md) | `fdiv.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point division. |
| [FEQ](../instructions/feq.md) | `feq.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point equality comparison. Writes 1 if ordered and equal. |
| [FEQS](../instructions/feqs.md) | `feqs.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | FEQS performs ordered signaling equality and returns canonical XLEN zero or one. |
| [FEXP](../instructions/fexp.md) | `fexp.{T} SrcL, ->{t, u, Rd}` | 32 | — | FEXP applies the active numeric profile exponential operation to the selected FP64 or FP32 carrier. |
| [FGE](../instructions/fge.md) | `fge.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point greater-or-equal comparison (ordered). |
| [FGES](../instructions/fges.md) | `fges.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | FGES performs ordered signaling greater-than-or-equal comparison and returns canonical XLEN zero or one. |
| [FLT](../instructions/flt.md) | `flt.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point less-than comparison (ordered). |
| [FLTS](../instructions/flts.md) | `flts.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | FLTS performs ordered signaling less-than comparison and returns canonical XLEN zero or one. |
| [FMADD](../instructions/fmadd.md) | `fmadd.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}` | 32 | — | FMADD computes one fused SrcL multiplied by SrcR plus SrcA operation through the active numeric profile. |
| [FMAX](../instructions/fmax.md) | `fmax.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point maximum. |
| [FMIN](../instructions/fmin.md) | `fmin.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point minimum. |
| [FMSUB](../instructions/fmsub.md) | `fmsub.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}` | 32 | — | FMSUB computes one fused SrcL multiplied by SrcR minus SrcA operation through the active numeric profile. |
| [FMUL](../instructions/fmul.md) | `fmul.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point multiplication. |
| [FNE](../instructions/fne.md) | `fne.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | FNE performs ordered quiet inequality and returns canonical XLEN zero or one. |
| [FNES](../instructions/fnes.md) | `fnes.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | FNES performs ordered signaling inequality and returns canonical XLEN zero or one. |
| [FNMADD](../instructions/fnmadd.md) | `fnmadd.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}` | 32 | — | FNMADD computes the negation of one fused SrcL multiplied by SrcR plus SrcA operation through the active numeric profile. |
| [FNMSUB](../instructions/fnmsub.md) | `fnmsub.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}` | 32 | — | FNMSUB computes the negation of one fused SrcL multiplied by SrcR minus SrcA operation through the active numeric profile. |
| [FRECIP](../instructions/frecip.md) | `frecip.{T} SrcL, ->{t, u, Rd}` | 32 | — | FRECIP applies the active numeric profile reciprocal operation to the selected FP64 or FP32 carrier. |
| [FSQRT](../instructions/fsqrt.md) | `fsqrt.{T} SrcL, ->{t, u, Rd}` | 32 | — | Floating-point square root. |
| [FSUB](../instructions/fsub.md) | `fsub.{T} SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Floating-point subtraction. |
| [SCVTF](../instructions/scvtf.md) | `scvtf.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | SCVTF converts a signed 64-bit or sign-extended signed 32-bit source to floating carrier code 0 through 14 through the active numeric profile. |
| [UCVTF](../instructions/ucvtf.md) | `ucvtf.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | UCVTF converts an unsigned 64-bit or zero-extended unsigned 32-bit source to floating carrier code 0 through 14 through the active numeric profile. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 13: FSU — Floating-point / SIMD Unit](../index.md)
- [Encoding formats](../encoding.md)
