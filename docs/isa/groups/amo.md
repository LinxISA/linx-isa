# AMO

<div class="insn-header">

<span class="ch-tag ch-tag-14">Ch 14</span>
&nbsp; <strong>AMO — Atomic Memory Operations</strong> &nbsp;|&nbsp;
**Group:** AMO &nbsp;|&nbsp;
**Forms:** 53 &nbsp;|&nbsp;
**Unique mnemonics:** 53

</div>

Instructions in the **AMO** group of the LinxISA v0.58.6 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [CASB](../instructions/casb.md) | `casb<.{aq, rl, aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 32 | — | CASB atomically compares and conditionally replaces one byte, then publishes the prior value. |
| [CASD](../instructions/casd.md) | `casd<.{aq, rl, aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 32 | — | CASD atomically compares and conditionally replaces one doubleword, then publishes the prior value. |
| [CASH](../instructions/cash.md) | `cash<.{aq, rl, aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 32 | — | CASH atomically compares and conditionally replaces one halfword, then publishes the prior value. |
| [CASW](../instructions/casw.md) | `casw<.{aq, rl, aqrl}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 32 | — | CASW atomically compares and conditionally replaces one word, then publishes the prior value. |
| [DMA](../instructions/dma.md) | `dma [SrcL], SrcR` | 32 | — | DMA performs an exact 64-byte copy, validates both ranges before effects, snapshots the source so overlap has memmove semantics, and guarantees that any fault leaves memory unchanged for precise full reissue. |
| [HL.CASB](../instructions/hl_casb.md) | `hl.casb<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 48 | — | HL.CASB atomically compares and conditionally replaces one byte, then publishes the prior value. |
| [HL.CASD](../instructions/hl_casd.md) | `hl.casd<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 48 | — | HL.CASD atomically compares and conditionally replaces one doubleword, then publishes the prior value. |
| [HL.CASH](../instructions/hl_cash.md) | `hl.cash<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 48 | — | HL.CASH atomically compares and conditionally replaces one halfword, then publishes the prior value. |
| [HL.CASW](../instructions/hl_casw.md) | `hl.casw<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, SrcD, ->{t, u, Rd}` | 48 | — | HL.CASW atomically compares and conditionally replaces one word, then publishes the prior value. |
| [LD.ADD](../instructions/ld_add.md) | `ld.add<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LD.ADD atomically stores the width-sized modular sum and publishes the prior memory value. |
| [LD.AND](../instructions/ld_and.md) | `ld.and<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LD.AND atomically stores the width-sized bitwise AND and publishes the prior memory value. |
| [LD.OR](../instructions/ld_or.md) | `ld.or<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LD.OR atomically stores the width-sized bitwise OR and publishes the prior memory value. |
| [LD.SMAX](../instructions/ld_smax.md) | `ld.smax<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LD.SMAX atomically stores the width-sized signed maximum and publishes the prior memory value. |
| [LD.SMIN](../instructions/ld_smin.md) | `ld.smin<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LD.SMIN atomically stores the width-sized signed minimum and publishes the prior memory value. |
| [LD.UMAX](../instructions/ld_umax.md) | `ld.umax<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LD.UMAX atomically stores the width-sized unsigned maximum and publishes the prior memory value. |
| [LD.UMIN](../instructions/ld_umin.md) | `ld.umin<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LD.UMIN atomically stores the width-sized unsigned minimum and publishes the prior memory value. |
| [LD.XOR](../instructions/ld_xor.md) | `ld.xor<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LD.XOR atomically stores the width-sized bitwise XOR and publishes the prior memory value. |
| [LR.B](../instructions/lr_b.md) | `lr.b<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], {->t, ->u, ->Rd}` | 32 | — | LR.B loads one byte, establishes a 64-byte-line reservation, and publishes the prior value. |
| [LR.D](../instructions/lr_d.md) | `lr.d<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], {->t, ->u, ->Rd}` | 32 | — | LR.D loads one doubleword, establishes a 64-byte-line reservation, and publishes the prior value. |
| [LR.H](../instructions/lr_h.md) | `lr.h<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], {->t, ->u, ->Rd}` | 32 | — | LR.H loads one halfword, establishes a 64-byte-line reservation, and publishes the prior value. |
| [LR.W](../instructions/lr_w.md) | `lr.w<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], {->t, ->u, ->Rd}` | 32 | — | LR.W loads one word, establishes a 64-byte-line reservation, and publishes the prior value. |
| [LW.ADD](../instructions/lw_add.md) | `lw.add<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LW.ADD atomically stores the modular 32-bit sum and publishes the prior memory value. |
| [LW.AND](../instructions/lw_and.md) | `lw.and<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LW.AND atomically stores the width-sized bitwise AND and publishes the prior memory value. |
| [LW.OR](../instructions/lw_or.md) | `lw.or<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LW.OR atomically stores the width-sized bitwise OR and publishes the prior memory value. |
| [LW.SMAX](../instructions/lw_smax.md) | `lw.smax<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LW.SMAX atomically stores the width-sized signed maximum and publishes the prior memory value. |
| [LW.SMIN](../instructions/lw_smin.md) | `lw.smin<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LW.SMIN atomically stores the width-sized signed minimum and publishes the prior memory value. |
| [LW.UMAX](../instructions/lw_umax.md) | `lw.umax<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LW.UMAX atomically stores the width-sized unsigned maximum and publishes the prior memory value. |
| [LW.UMIN](../instructions/lw_umin.md) | `lw.umin<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LW.UMIN atomically stores the width-sized unsigned minimum and publishes the prior memory value. |
| [LW.XOR](../instructions/lw_xor.md) | `lw.xor<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | LW.XOR atomically stores the width-sized bitwise XOR and publishes the prior memory value. |
| [SC.B](../instructions/sc_b.md) | `sc.b<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> SrcL, [SrcR], {->t, ->u, ->Rd}` | 32 | — | SC.B conditionally stores one byte when the local 64-byte-line reservation matches. |
| [SC.D](../instructions/sc_d.md) | `sc.d<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> SrcL, [SrcR], {->t, ->u, ->Rd}` | 32 | — | SC.D conditionally stores one doubleword when the local 64-byte-line reservation matches. |
| [SC.H](../instructions/sc_h.md) | `sc.h<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> SrcL, [SrcR], {->t, ->u, ->Rd}` | 32 | — | SC.H conditionally stores one halfword when the local 64-byte-line reservation matches. |
| [SC.W](../instructions/sc_w.md) | `sc.w<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> SrcL, [SrcR], {->t, ->u, ->Rd}` | 32 | — | SC.W conditionally stores one word when the local 64-byte-line reservation matches. |
| [SD.ADD](../instructions/sd_add.md) | `sd.add<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SD.ADD atomically replaces the aligned 64-bit memory value with its modular sum with SrcR; it does not publish the old value. |
| [SD.AND](../instructions/sd_and.md) | `sd.and<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SD.AND atomically replaces the aligned 64-bit memory value with its bitwise AND with SrcR; it does not publish the old value. |
| [SD.OR](../instructions/sd_or.md) | `sd.or<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SD.OR atomically replaces the aligned 64-bit memory value with its bitwise OR with SrcR; it does not publish the old value. |
| [SD.SMAX](../instructions/sd_smax.md) | `sd.smax<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SD.SMAX atomically replaces the aligned 64-bit memory value with its signed maximum with SrcR; it does not publish the old value. |
| [SD.SMIN](../instructions/sd_smin.md) | `sd.smin<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SD.SMIN atomically replaces the aligned 64-bit memory value with its signed minimum with SrcR; it does not publish the old value. |
| [SD.UMAX](../instructions/sd_umax.md) | `sd.umax<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SD.UMAX atomically replaces the aligned 64-bit memory value with its unsigned maximum with SrcR; it does not publish the old value. |
| [SD.UMIN](../instructions/sd_umin.md) | `sd.umin<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SD.UMIN atomically replaces the aligned 64-bit memory value with its unsigned minimum with SrcR; it does not publish the old value. |
| [SD.XOR](../instructions/sd_xor.md) | `sd.xor<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SD.XOR atomically replaces the aligned 64-bit memory value with its bitwise XOR with SrcR; it does not publish the old value. |
| [SW.ADD](../instructions/sw_add.md) | `sw.add<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SW.ADD atomically replaces the aligned 32-bit memory value with its modular sum with SrcR; it does not publish the old value. |
| [SW.AND](../instructions/sw_and.md) | `sw.and<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SW.AND atomically replaces the aligned 32-bit memory value with its bitwise AND with SrcR; it does not publish the old value. |
| [SW.OR](../instructions/sw_or.md) | `sw.or<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SW.OR atomically replaces the aligned 32-bit memory value with its bitwise OR with SrcR; it does not publish the old value. |
| [SW.SMAX](../instructions/sw_smax.md) | `sw.smax<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SW.SMAX atomically replaces the aligned 32-bit memory value with its signed maximum with SrcR; it does not publish the old value. |
| [SW.SMIN](../instructions/sw_smin.md) | `sw.smin<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SW.SMIN atomically replaces the aligned 32-bit memory value with its signed minimum with SrcR; it does not publish the old value. |
| [SW.UMAX](../instructions/sw_umax.md) | `sw.umax<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SW.UMAX atomically replaces the aligned 32-bit memory value with its unsigned maximum with SrcR; it does not publish the old value. |
| [SW.UMIN](../instructions/sw_umin.md) | `sw.umin<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SW.UMIN atomically replaces the aligned 32-bit memory value with its unsigned minimum with SrcR; it does not publish the old value. |
| [SW.XOR](../instructions/sw_xor.md) | `sw.xor<.{rl, f, rlf}> [SrcL], SrcR` | 32 | — | SW.XOR atomically replaces the aligned 32-bit memory value with its bitwise XOR with SrcR; it does not publish the old value. |
| [SWAPB](../instructions/swapb.md) | `swapb<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | SWAPB atomically replaces one byte and publishes the prior value. |
| [SWAPD](../instructions/swapd.md) | `swapd<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | SWAPD atomically replaces one doubleword and publishes the prior value. |
| [SWAPH](../instructions/swaph.md) | `swaph<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | SWAPH atomically replaces one halfword and publishes the prior value. |
| [SWAPW](../instructions/swapw.md) | `swapw<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, {->t, ->u, ->Rd}` | 32 | — | SWAPW atomically replaces one word and publishes the prior value. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 14: AMO — Atomic Memory Operations](../index.md)
- [Encoding formats](../encoding.md)
