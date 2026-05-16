# Format Convert

<div class="insn-header">

<span class="ch-tag ch-tag-13">Ch 13</span>
&nbsp; <strong>FSU — Floating-point / SIMD Unit</strong> &nbsp;|&nbsp;
**Group:** Format Convert &nbsp;|&nbsp;
**Forms:** 12 &nbsp;|&nbsp;
**Unique mnemonics:** 12

</div>

Floating-point and integer format conversion instructions.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [FCVT](../instructions/fcvt.md) | `fcvt.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | Floating-point format conversion. |
| [FCVTA](../instructions/fcvta.md) | `fcvta.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | Instruction from the Format Convert group. |
| [FCVTM](../instructions/fcvtm.md) | `fcvtm.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | Instruction from the Format Convert group. |
| [FCVTN](../instructions/fcvtn.md) | `fcvtn.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | Instruction from the Format Convert group. |
| [FCVTP](../instructions/fcvtp.md) | `fcvtp.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | Instruction from the Format Convert group. |
| [FCVTZ](../instructions/fcvtz.md) | `fcvtz.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | Instruction from the Format Convert group. |
| [SCVTF](../instructions/scvtf.md) | `scvtf.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | Instruction from the Format Convert group. |
| [UCVTF](../instructions/ucvtf.md) | `ucvtf.{srcT2dstT} SrcL, ->{t, u, Rd}` | 32 | — | Instruction from the Format Convert group. |
| [V.FCVT](../instructions/v_fcvt.md) | `v.fcvt.{st2dt} SrcL, ->Dst` | 64 | — | [64-bit V.] Instruction from the Format Convert group. |
| [V.FCVTI](../instructions/v_fcvti.md) | `v.fcvti.{st2dt} SrcL, ->Dst` | 64 | — | [64-bit V.] Instruction from the Format Convert group. |
| [V.ICVT](../instructions/v_icvt.md) | `v.icvt.{st2dt} SrcL, ->Dst` | 64 | — | [64-bit V.] Instruction from the Format Convert group. |
| [V.ICVTF](../instructions/v_icvtf.md) | `v.icvtf.{st2dt} SrcL, ->Dst` | 64 | — | [64-bit V.] Instruction from the Format Convert group. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 13: FSU — Floating-point / SIMD Unit](../index.md)
- [Encoding formats](../encoding.md)
