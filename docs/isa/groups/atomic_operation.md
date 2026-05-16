# Atomic Operation

<div class="insn-header">

<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Group:** Atomic Operation &nbsp;|&nbsp;
**Forms:** 68 &nbsp;|&nbsp;
**Unique mnemonics:** 68

</div>

Atomic read-modify-write operations on memory.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [LD.ADD](../instructions/ld_add.md) | `ld.add<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LD.AND](../instructions/ld_and.md) | `ld.and<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LD.OR](../instructions/ld_or.md) | `ld.or<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LD.SMAX](../instructions/ld_smax.md) | `ld.smax<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LD.SMIN](../instructions/ld_smin.md) | `ld.smin<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LD.UMAX](../instructions/ld_umax.md) | `ld.umax<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LD.UMIN](../instructions/ld_umin.md) | `ld.umin<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LD.XOR](../instructions/ld_xor.md) | `ld.xor<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LR.B](../instructions/lr_b.md) | `lr.b<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LR.D](../instructions/lr_d.md) | `lr.d<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LR.H](../instructions/lr_h.md) | `lr.h<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LR.W](../instructions/lr_w.md) | `lr.w<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LW.ADD](../instructions/lw_add.md) | `lw.add<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LW.AND](../instructions/lw_and.md) | `lw.and<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LW.OR](../instructions/lw_or.md) | `lw.or<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LW.SMAX](../instructions/lw_smax.md) | `lw.smax<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LW.SMIN](../instructions/lw_smin.md) | `lw.smin<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LW.UMAX](../instructions/lw_umax.md) | `lw.umax<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LW.UMIN](../instructions/lw_umin.md) | `lw.umin<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [LW.XOR](../instructions/lw_xor.md) | `lw.xor<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [SC.B](../instructions/sc_b.md) | `sc.b<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> SrcL, [SrcR], {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [SC.D](../instructions/sc_d.md) | `sc.d<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> SrcL, [SrcR], {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [SC.H](../instructions/sc_h.md) | `sc.h<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> SrcL, [SrcR], {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [SC.W](../instructions/sc_w.md) | `sc.w<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> SrcL, [SrcR], {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [SD.ADD](../instructions/sd_add.md) | `sd.add<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SD.AND](../instructions/sd_and.md) | `sd.and<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SD.OR](../instructions/sd_or.md) | `sd.or<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SD.SMAX](../instructions/sd_smax.md) | `sd.smax<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SD.SMIN](../instructions/sd_smin.md) | `sd.smin<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SD.UMAX](../instructions/sd_umax.md) | `sd.umax<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SD.UMIN](../instructions/sd_umin.md) | `sd.umin<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SD.XOR](../instructions/sd_xor.md) | `sd.xor<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SW.ADD](../instructions/sw_add.md) | `sw.add<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SW.AND](../instructions/sw_and.md) | `sw.and<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SW.OR](../instructions/sw_or.md) | `sw.or<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SW.SMAX](../instructions/sw_smax.md) | `sw.smax<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SW.SMIN](../instructions/sw_smin.md) | `sw.smin<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SW.UMAX](../instructions/sw_umax.md) | `sw.umax<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SW.UMIN](../instructions/sw_umin.md) | `sw.umin<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SW.XOR](../instructions/sw_xor.md) | `sw.xor<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | Atomic memory read-modify-write operation. |
| [SWAPB](../instructions/swapb.md) | `swapb<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [SWAPD](../instructions/swapd.md) | `swapd<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [SWAPH](../instructions/swaph.md) | `swaph<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
| [SWAPW](../instructions/swapw.md) | `swapw<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | Atomic memory read-modify-write operation. |
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
