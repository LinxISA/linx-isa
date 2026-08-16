# ALU

<div class="insn-header">

<span class="ch-tag ch-tag-12">Ch 12</span>
&nbsp; <strong>ALU — Arithmetic Logic Unit</strong> &nbsp;|&nbsp;
**Group:** ALU &nbsp;|&nbsp;
**Forms:** 107 &nbsp;|&nbsp;
**Unique mnemonics:** 107

</div>

Instructions in the **ALU** group of the LinxISA v0.58.1 catalog.

## Instructions

| Mnemonic | Assembly | Length | Decode | Description |
|----------|----------|--------|--------|-------------|
| [ADD](../instructions/add.md) | `add SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>, ->{t, u, Rd}` | 32 | — | Integer addition. Writes the sum of two registers to the destination. |
| [ADDI](../instructions/addi.md) | `addi SrcL, uimm, ->{t, u, Rd}` | 32 | — | Integer add-immediate. Adds a sign-extended 12-bit immediate to a register. |
| [ADDIW](../instructions/addiw.md) | `addiw SrcL, uimm, ->{t, u, Rd}` | 32 | — | 32-bit word add-immediate. |
| [ADDW](../instructions/addw.md) | `addw SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>, ->{t, u, Rd}` | 32 | — | 32-bit word integer addition. |
| [AND](../instructions/and.md) | `and SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | Bitwise AND of two registers. |
| [ANDI](../instructions/andi.md) | `andi SrcL, simm, ->{t, u, Rd}` | 32 | — | Bitwise AND with an immediate. |
| [ANDIW](../instructions/andiw.md) | `andiw SrcL, simm, ->{t, u, Rd}` | 32 | — | 32-bit word AND-immediate. |
| [ANDW](../instructions/andw.md) | `andw SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | 32-bit word bitwise AND. |
| [BCNT](../instructions/bcnt.md) | `bcnt srcL,  M, N, ->{t, u, Rd}` | 32 | — | Population count. Counts the number of set bits in a register. |
| [BIC](../instructions/bic.md) | `bic SrcL, M, N, ->{t, u, Rd}` | 32 | — | Bit clear / AND-NOT. |
| [BIS](../instructions/bis.md) | `bis SrcL, M, N, ->{t, u, Rd}` | 32 | — | Bit set / OR. |
| [BXS](../instructions/bxs.md) | `bxs SrcL, M, N, ->{t, u, Rd}` | 32 | — | Bit-field extract signed. |
| [BXU](../instructions/bxu.md) | `bxu SrcL, M, N, ->{t, u, Rd}` | 32 | — | Bit-field extract unsigned. |
| [C.ADD](../instructions/c_add.md) | `c.add srcL, srcR, ->t` | 16 | — | [16-bit C.] Integer addition. |
| [C.ADDI](../instructions/c_addi.md) | `c.addi srcL, simm, ->t` | 16 | — | C.ADDI snapshots one complete Reg5 source, sign-extends simm5, adds modulo 2^XLEN, and pushes the result to T. |
| [C.AND](../instructions/c_and.md) | `c.and srcL, srcR, ->t` | 16 | — | [16-bit C.] Bitwise AND. |
| [C.MOVI](../instructions/c_movi.md) | `c.movi simm, ->{t, u, Rd}` | 16 | — | C.MOVI sign-extends its encoded five-bit immediate to XLEN and publishes it through RegDst. |
| [C.MOVR](../instructions/c_movr.md) | `c.movr SrcL, ->{t, u, Rd}` | 16 | — | C.MOVR snapshots a Reg5 source and publishes the complete XLEN value unchanged through RegDst. |
| [C.OR](../instructions/c_or.md) | `c.or srcL, srcR, ->t` | 16 | — | [16-bit C.] Bitwise OR. |
| [C.SETC.TGT](../instructions/c_setc_tgt.md) | `c.setc.tgt srcL` | 16 | — | [16-bit C.] Sets the block-commit condition. |
| [C.SETRET](../instructions/c_setret.md) | `c.setret uimm, ->ra` | 16 | — | Materialize an unsigned halfword-scaled TPC-relative return address in ra and captured return state. |
| [C.SEXT.B](../instructions/c_sext_b.md) | `c.sext.b srcL, ->t` | 16 | — | C.SEXT.B sign-extends SrcL[7:0] to XLEN and pushes the result to T. |
| [C.SEXT.H](../instructions/c_sext_h.md) | `c.sext.h srcL, ->t` | 16 | — | C.SEXT.H sign-extends SrcL[15:0] to XLEN and pushes the result to T. |
| [C.SEXT.W](../instructions/c_sext_w.md) | `c.sext.w srcL, ->t` | 16 | — | C.SEXT.W sign-extends SrcL[31:0] to XLEN and pushes the result to T. |
| [C.SLLI](../instructions/c_slli.md) | `c.slli t#1, uimm, ->t` | 16 | — | C.SLLI snapshots the pre-instruction T#1 value, logically shifts it left by uimm5, and pushes the XLEN result to T. |
| [C.SRLI](../instructions/c_srli.md) | `c.srli t#1, uimm, ->t` | 16 | — | C.SRLI snapshots the pre-instruction T#1 value, logically shifts it right by uimm5, and pushes the XLEN result to T. |
| [C.SUB](../instructions/c_sub.md) | `c.sub srcL, srcR, ->t` | 16 | — | [16-bit C.] Integer subtraction. |
| [C.ZEXT.B](../instructions/c_zext_b.md) | `c.zext.b srcL, ->t` | 16 | — | C.ZEXT.B zero-extends SrcL[7:0] to XLEN and pushes the result to T. |
| [C.ZEXT.H](../instructions/c_zext_h.md) | `c.zext.h srcL, ->t` | 16 | — | C.ZEXT.H zero-extends SrcL[15:0] to XLEN and pushes the result to T. |
| [C.ZEXT.W](../instructions/c_zext_w.md) | `c.zext.w srcL, ->t` | 16 | — | C.ZEXT.W zero-extends SrcL[31:0] to XLEN and pushes the result to T. |
| [CLZ](../instructions/clz.md) | `clz SrcL,  M, N, ->{t, u, Rd}` | 32 | — | Count leading zeros. |
| [CSEL](../instructions/csel.md) | `csel SrcP, SrcL, SrcR<.neg>, ->{t, u, Rd}` | 32 | — | Conditional select. `Dest = (SrcP != 0) ? SrcL : SrcR`. |
| [CTZ](../instructions/ctz.md) | `ctz SrcL,  M, N, ->{t, u, Rd}` | 32 | — | Count trailing zeros. |
| [DIV](../instructions/div.md) | `div SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Signed integer division. |
| [DIVU](../instructions/divu.md) | `divu SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Unsigned integer division. |
| [DIVUW](../instructions/divuw.md) | `divuw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word unsigned integer division. |
| [DIVW](../instructions/divw.md) | `divw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word signed integer division. |
| [HL.ADDI](../instructions/hl_addi.md) | `hl.addi SrcL, uimm, ->{t, u, Rd}` | 48 | — | HL.ADDI applies XLEN addition to SrcL and a zero-extended 24-bit immediate. |
| [HL.ADDIW](../instructions/hl_addiw.md) | `hl.addiw SrcL, uimm, ->{t, u, Rd}` | 48 | — | HL.ADDIW applies word addition to SrcL[31:0] and the low word of a zero-extended 24-bit immediate, then sign-extends the 32-bit result. |
| [HL.ANDI](../instructions/hl_andi.md) | `hl.andi SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.ANDI applies XLEN bitwise conjunction to SrcL and a sign-extended 24-bit immediate. |
| [HL.ANDIW](../instructions/hl_andiw.md) | `hl.andiw SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.ANDIW applies word bitwise conjunction to SrcL[31:0] and the low word of a sign-extended 24-bit immediate, then sign-extends the 32-bit result. |
| [HL.BFI](../instructions/hl_bfi.md) | `hl.bfi SrcL, SrcR, M, N, ->{t, u, Rd}` | 48 | — | [48-bit HL.] Bit-field insert. |
| [HL.CCAT](../instructions/hl_ccat.md) | `hl.ccat SrcL, SrcR, shamt, ->Dst0, Dst1` | 48 | — | HL.CCAT logically right-shifts {SrcL, SrcR}, writes the low 64-bit result to Dst0, then writes the high result to Dst1. |
| [HL.CCATW](../instructions/hl_ccatw.md) | `hl.ccatw SrcL, SrcR, shamt, ->Dst0, Dst1` | 48 | — | HL.CCATW logically right-shifts {SrcL[31:0], SrcR[31:0]}, sign-extends the low then high 32-bit results, and writes them in order. |
| [HL.DIV](../instructions/hl_div.md) | `hl.div SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Signed integer division. |
| [HL.DIVU](../instructions/hl_divu.md) | `hl.divu SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Unsigned integer division. |
| [HL.DIVUW](../instructions/hl_divuw.md) | `hl.divuw SrcL, SrcR, ->Dst0, Dst1` | 48 | — | HL.DIVUW computes a unsigned low-32-bit quotient/remainder pair from source snapshots, then publishes quotient followed by remainder. |
| [HL.DIVW](../instructions/hl_divw.md) | `hl.divw SrcL, SrcR, ->Dst0, Dst1` | 48 | — | HL.DIVW computes a signed low-32-bit quotient/remainder pair from source snapshots, then publishes quotient followed by remainder. |
| [HL.LIS](../instructions/hl_lis.md) | `hl.lis simm, ->{t, u, Rd}` | 48 | — | HL.LIS sign-extends its split encoded 32-bit immediate to XLEN and publishes the result through RegDst. |
| [HL.LIU](../instructions/hl_liu.md) | `hl.liu uimm, ->{t, u, Rd}` | 48 | — | HL.LIU zero-extends its split encoded 32-bit immediate to XLEN and publishes the result through RegDst. |
| [HL.LUI](../instructions/hl_lui.md) | `hl.lui imm, ->{t, u, Rd}` | 48 | — | HL.LUI sign-extends its split encoded 32-bit immediate to XLEN and publishes the result through RegDst. |
| [HL.MADD](../instructions/hl_madd.md) | `hl.madd SrcL, SrcR, SrcD, ->Dst0, Dst1` | 48 | — | HL.MADD computes a signed 128-bit product plus a sign-extended XLEN addend and publishes low then high halves. |
| [HL.MADDW](../instructions/hl_maddw.md) | `hl.maddw SrcL, SrcR, SrcD, ->Dst0, Dst1` | 48 | — | HL.MADDW sign-extends three low-32-bit sources, computes a 128-bit product plus addend, and publishes low then high halves. |
| [HL.MIADD](../instructions/hl_miadd.md) | `hl.miadd SrcL, SrcR, uimm, ->{t, u, Rd}` | 48 | — | HL.MIADD multiplies SrcR by the unsigned 19-bit immediate, adds SrcL modulo 2^PTO_XLEN, and publishes the result. |
| [HL.MISUB](../instructions/hl_misub.md) | `hl.misub SrcL, SrcR, uimm, ->{t, u, Rd}` | 48 | — | HL.MISUB multiplies SrcR by the unsigned 19-bit immediate, subtracts the product from SrcL modulo 2^PTO_XLEN, and publishes the result. |
| [HL.MUL](../instructions/hl_mul.md) | `hl.mul SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Integer multiply. |
| [HL.MULU](../instructions/hl_mulu.md) | `hl.mulu SrcL, SrcR, ->Dst0, Dst1` | 48 | — | HL.MULU computes an unsigned 128-bit scalar product and publishes its low half followed by its high half. |
| [HL.ORI](../instructions/hl_ori.md) | `hl.ori SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.ORI applies XLEN bitwise inclusive-or to SrcL and a sign-extended 24-bit immediate. |
| [HL.ORIW](../instructions/hl_oriw.md) | `hl.oriw SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.ORIW applies word bitwise inclusive-or to SrcL[31:0] and the low word of a sign-extended 24-bit immediate, then sign-extends the 32-bit result. |
| [HL.REM](../instructions/hl_rem.md) | `hl.rem SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Signed integer remainder. |
| [HL.REMU](../instructions/hl_remu.md) | `hl.remu SrcL, SrcR, ->Dst0, Dst1` | 48 | — | [48-bit HL.] Unsigned integer remainder. |
| [HL.REMUW](../instructions/hl_remuw.md) | `hl.remuw SrcL, SrcR, ->Dst0, Dst1` | 48 | — | HL.REMUW computes a unsigned low-32-bit quotient/remainder pair from source snapshots, then publishes quotient followed by remainder. |
| [HL.REMW](../instructions/hl_remw.md) | `hl.remw SrcL, SrcR, ->Dst0, Dst1` | 48 | — | HL.REMW computes a signed low-32-bit quotient/remainder pair from source snapshots, then publishes quotient followed by remainder. |
| [HL.SUBI](../instructions/hl_subi.md) | `hl.subi SrcL, uimm, ->{t, u, Rd}` | 48 | — | HL.SUBI applies XLEN subtraction to SrcL and a zero-extended 24-bit immediate. |
| [HL.SUBIW](../instructions/hl_subiw.md) | `hl.subiw SrcL, uimm, ->{t, u, Rd}` | 48 | — | HL.SUBIW applies word subtraction to SrcL[31:0] and the low word of a zero-extended 24-bit immediate, then sign-extends the 32-bit result. |
| [HL.XORI](../instructions/hl_xori.md) | `hl.xori SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.XORI applies XLEN bitwise exclusive-or to SrcL and a sign-extended 24-bit immediate. |
| [HL.XORIW](../instructions/hl_xoriw.md) | `hl.xoriw SrcL, simm, ->{t, u, Rd}` | 48 | — | HL.XORIW applies word bitwise exclusive-or to SrcL[31:0] and the low word of a sign-extended 24-bit immediate, then sign-extends the 32-bit result. |
| [LUI](../instructions/lui.md) | `lui simm, ->{t, u, Rd}` | 32 | — | Load upper immediate. Materializes a 20-bit constant in the upper bits of the destination. |
| [MADD](../instructions/madd.md) | `madd SrcL, SrcR, SrcD, ->{t, u, Rd}` | 32 | — | Multiply-add: `Dest = SrcD + SrcL * SrcR`. |
| [MADDW](../instructions/maddw.md) | `maddw SrcL, SrcR, SrcD, ->{t, u, Rd}` | 32 | — | 32-bit word multiply-add. |
| [MAX](../instructions/max.md) | `max SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Integer max (signed). |
| [MAXU](../instructions/maxu.md) | `maxu SrcL, SrcR, ->{t, u, Rd}` | 32 | — | MAXU performs an unsigned full-XLEN comparison and publishes the complete bit pattern of the maximum operand. |
| [MIN](../instructions/min.md) | `min SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Integer min (signed). |
| [MINU](../instructions/minu.md) | `minu SrcL, SrcR, ->{t, u, Rd}` | 32 | — | MINU performs an unsigned full-XLEN comparison and publishes the complete bit pattern of the minimum operand. |
| [MUL](../instructions/mul.md) | `mul SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Integer multiply (lower product written to destination). |
| [MULU](../instructions/mulu.md) | `mulu SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Integer multiply (unsigned). |
| [MULUW](../instructions/muluw.md) | `muluw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word integer multiply (unsigned). |
| [MULW](../instructions/mulw.md) | `mulw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word integer multiply. |
| [OR](../instructions/or.md) | `or SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | Bitwise OR of two registers. |
| [ORI](../instructions/ori.md) | `ori SrcL, simm, ->{t, u, Rd}` | 32 | — | Bitwise OR with an immediate. |
| [ORIW](../instructions/oriw.md) | `oriw SrcL, simm, ->{t, u, Rd}` | 32 | — | 32-bit word OR-immediate. |
| [ORW](../instructions/orw.md) | `orw SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | 32-bit word bitwise OR. |
| [REM](../instructions/rem.md) | `rem SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Signed integer remainder. |
| [REMU](../instructions/remu.md) | `remu SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Unsigned integer remainder. |
| [REMUW](../instructions/remuw.md) | `remuw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word unsigned remainder. |
| [REMW](../instructions/remw.md) | `remw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word signed remainder. |
| [REV](../instructions/rev.md) | `rev SrcL,  M, N, ->{t, u, Rd}` | 32 | — | Bit-reversal operation. |
| [SLL](../instructions/sll.md) | `sll SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Logical left shift by the value in SrcR. |
| [SLLI](../instructions/slli.md) | `slli SrcL, shamt, ->{t, u, Rd}` | 32 | — | Logical left shift by an immediate amount. |
| [SLLIW](../instructions/slliw.md) | `slliw SrcL, shamt, ->{t, u, Rd}` | 32 | — | 32-bit word logical left shift (immediate). |
| [SLLW](../instructions/sllw.md) | `sllw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word logical left shift. |
| [SRA](../instructions/sra.md) | `sra SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Arithmetic right shift by the value in SrcR. |
| [SRAI](../instructions/srai.md) | `srai SrcL, shamt, ->{t, u, Rd}` | 32 | — | Arithmetic right shift by an immediate amount. |
| [SRAIW](../instructions/sraiw.md) | `sraiw SrcL, shamt, ->{t, u, Rd}` | 32 | — | 32-bit word arithmetic right shift (immediate). |
| [SRAW](../instructions/sraw.md) | `sraw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word arithmetic right shift. |
| [SRL](../instructions/srl.md) | `srl SrcL, SrcR, ->{t, u, Rd}` | 32 | — | Logical right shift by the value in SrcR. |
| [SRLI](../instructions/srli.md) | `srli SrcL, shamt, ->{t, u, Rd}` | 32 | — | Logical right shift by an immediate amount. |
| [SRLIW](../instructions/srliw.md) | `srliw SrcL, shamt, ->{t, u, Rd}` | 32 | — | 32-bit word logical right shift (immediate). |
| [SRLW](../instructions/srlw.md) | `srlw SrcL, SrcR, ->{t, u, Rd}` | 32 | — | 32-bit word logical right shift. |
| [SUB](../instructions/sub.md) | `sub SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>, ->{t, u, Rd}` | 32 | — | Integer subtraction. |
| [SUBI](../instructions/subi.md) | `subi SrcL, uimm, ->{t, u, Rd}` | 32 | — | SUBI subtracts the zero-extended unsigned 12-bit immediate from the snapshotted XLEN source modulo 2^PTO_XLEN and publishes the result through RegDst. |
| [SUBIW](../instructions/subiw.md) | `subiw SrcL, uimm, ->{t, u, Rd}` | 32 | — | SUBIW subtracts the zero-extended unsigned 12-bit immediate from SrcL[31:0] modulo 2^32, sign-extends the word result to XLEN, and publishes it through RegDst. |
| [SUBW](../instructions/subw.md) | `subw SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>, ->{t, u, Rd}` | 32 | — | 32-bit word integer subtraction. |
| [XOR](../instructions/xor.md) | `xor SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | Bitwise XOR of two registers. |
| [XORI](../instructions/xori.md) | `xori SrcL, simm, ->{t, u, Rd}` | 32 | — | Bitwise XOR with an immediate. |
| [XORIW](../instructions/xoriw.md) | `xoriw SrcL, simm, ->{t, u, Rd}` | 32 | — | 32-bit word XOR-immediate. |
| [XORW](../instructions/xorw.md) | `xorw SrcL, SrcR<{.sw,.uw,.not}><<<shamt>, ->{t, u, Rd}` | 32 | — | 32-bit word bitwise XOR. |

## See Also

- [Instruction reference](../index.md) · [Groups Index](index.md)
- [Chapter 12: ALU — Arithmetic Logic Unit](../index.md)
- [Encoding formats](../encoding.md)
