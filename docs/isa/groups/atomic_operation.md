# Atomic Operation

<div class="insn-header">

<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Group:** Atomic Operation &nbsp;|&nbsp;
**Forms:** 24 &nbsp;|&nbsp;
**Unique mnemonics:** 24

</div>

Atomic read-modify-write operations on memory.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [V.LD.ADD](../instructions/v_ld_add.md) | `v.ld.add<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LD.AND](../instructions/v_ld_and.md) | `v.ld.and<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LD.MAX](../instructions/v_ld_max.md) | `v.ld.max<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LD.MIN](../instructions/v_ld_min.md) | `v.ld.min<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LD.OR](../instructions/v_ld_or.md) | `v.ld.or<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LD.XOR](../instructions/v_ld_xor.md) | `v.ld.xor<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.ADD](../instructions/v_lw_add.md) | `v.lw.add<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.AND](../instructions/v_lw_and.md) | `v.lw.and<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.MAX](../instructions/v_lw_max.md) | `v.lw.max<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.MIN](../instructions/v_lw_min.md) | `v.lw.min<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.OR](../instructions/v_lw_or.md) | `v.lw.or<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.XOR](../instructions/v_lw_xor.md) | `v.lw.xor<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->Dst` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.ADD](../instructions/v_sd_add.md) | `v.sd.add<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.AND](../instructions/v_sd_and.md) | `v.sd.and<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.MAX](../instructions/v_sd_max.md) | `v.sd.max<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.MIN](../instructions/v_sd_min.md) | `v.sd.min<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.OR](../instructions/v_sd_or.md) | `v.sd.or<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.XOR](../instructions/v_sd_xor.md) | `v.sd.xor<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.ADD](../instructions/v_sw_add.md) | `v.sw.add<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.AND](../instructions/v_sw_and.md) | `v.sw.and<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.MAX](../instructions/v_sw_max.md) | `v.sw.max<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.MIN](../instructions/v_sw_min.md) | `v.sw.min<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.OR](../instructions/v_sw_or.md) | `v.sw.or<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.XOR](../instructions/v_sw_xor.md) | `v.sw.xor<.{rl, f, rd, rlf, rdf, rlrd, rlrdf}> [SrcL], SrcR` | 64 | — | [64-bit V.] Atomic memory read-modify-write operation. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 14: AMO — Atomic Memory Operations](../index.md)
- [Encoding formats](../encoding.md)
