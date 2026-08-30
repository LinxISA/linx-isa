# All Instructions

Complete alphabetical index of all **754** instruction forms in the LinxISA v0.58.5 catalog.

Use **Ctrl+F** / **Cmd+F** to search, or click a letter below to jump to it.

[A](#a) | [B](#b) | [C](#c) | [D](#d) | [E](#e) | [F](#f) | [H](#h) | [I](#i) | [J](#j) | [L](#l) | [M](#m) | [O](#o) | [P](#p) | [R](#r) | [S](#s) | [T](#t) | [U](#u) | [V](#v) | [X](#x)

### A

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [ACRC](acrc.md) | [SYS](../groups/sys.md) | 32 | Architectural control (ring call). Calls an implementation-defined ACR. |
| [ACRE](acre.md) | [SYS](../groups/sys.md) | 32 | Architectural control (ring entry). Enters an implementation-defined ACR. |
| [ADD](add.md) | [ALU](../groups/alu.md) | 32 | Integer addition. Writes the sum of two registers to the destination. |
| [ADDI](addi.md) | [ALU](../groups/alu.md) | 32 | Integer add-immediate. Adds a sign-extended 12-bit immediate to a register. |
| [ADDIW](addiw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word add-immediate. |
| [ADDTPC](addtpc.md) | [BRU](../groups/bru.md) | 32 | PC-relative addition. Adds an immediate to the current PC/TPC and writes the result. |
| [ADDW](addw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word integer addition. |
| [AND](and.md) | [ALU](../groups/alu.md) | 32 | Bitwise AND of two registers. |
| [ANDI](andi.md) | [ALU](../groups/alu.md) | 32 | Bitwise AND with an immediate. |
| [ANDIW](andiw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word AND-immediate. |
| [ANDW](andw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word bitwise AND. |
| [ASSERT](assert.md) | [SYS](../groups/sys.md) | 32 | Architectural assertion. Traps if the condition register is zero. |

### B

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [B.ASSEMBLE](b_assemble.md) | [Bundle Range Modifier](../groups/bundle_range_modifier.md) | 32 | Decodes one destination-range assemble modifier and retains its XLEN-wrapped derived offset in the immediately preceding binder group. |
| [B.CATR](b_catr.md) | [Bundle Control Attribute](../groups/bundle_control_attribute.md) | 32 | Defines one optional block control record for post-commit trap, transactional visibility, acquire/release ordering, remote execution, and dimension-reduction mode. |
| [B.DATR](b_datr.md) | [Bundle Data Attribute](../groups/bundle_data_attribute.md) | 32 | Latches the optional per-block tile layout, data type, padding, comparison, rounding, saturation, and canonicalization attributes. |
| [B.DIM](b_dim.md) | [Bundle Argument](../groups/bundle_argument.md) | 32 | Writes zero-extend((GPR[RegSrc] + uimm17)[15:0]) to the selected bundle-local LB register exactly once. |
| [B.DIM](b_dim.md) | [Bundle Argument](../groups/bundle_argument.md) | 32 | Writes zero-extend((GPR[RegSrc] + uimm17)[15:0]) to the selected bundle-local LB register exactly once. |
| [B.DIM](b_dim.md) | [Bundle Argument](../groups/bundle_argument.md) | 32 | Writes zero-extend((GPR[RegSrc] + uimm17)[15:0]) to the selected bundle-local LB register exactly once. |
| [B.FPATR](b_fpatr.md) | [Bundle Fixed-Point PostProcess Attribute](../groups/bundle_fixed_point_postprocess_attribute.md) | 32 | Latches complete-bundle matrix post-processing mode, reduction enables, and fixed-point descriptor controls. |
| [B.HINT](b_hint.md) | [Bundle Hint](../groups/bundle_hint.md) | 32 | Records one optional per-block branch, temperature, prefetch-size, or trace-boundary hint without changing functional results. |
| [B.HINT](b_hint.md) | [Bundle Hint](../groups/bundle_hint.md) | 32 | Records one optional per-block branch, temperature, prefetch-size, or trace-boundary hint without changing functional results. |
| [B.IOR](b_ior.md) | [Bundle Input & Output](../groups/bundle_input_output.md) | 32 | Bind up to three absolute GPR inputs and one absolute GPR output; TLOAD/TSTORE use source zero as GM base and source one as byte row stride. |
| [B.IOS](b_ios.md) | [Bundle Input & Output](../groups/bundle_input_output.md) | 32 | Binds one ordered absolute Core-private Shared register S0..S63 as a source or destination with a common four-PE participation mode decoded to a fixed mask. |
| [B.IOT](b_iot.md) | [Bundle Input & Output](../groups/bundle_input_output.md) | 32 | Binds an ordered Local Tile source/destination sequence with one common four-PE participation mode decoded to a fixed mask; L terminates only that sequence and never releases a source. |
| [B.IOT](b_iot.md) | [Bundle Input & Output](../groups/bundle_input_output.md) | 32 | Binds an ordered Local Tile source/destination sequence with one common four-PE participation mode decoded to a fixed mask; L terminates only that sequence and never releases a source. |
| [B.IOT](b_iot.md) | [Bundle Input & Output](../groups/bundle_input_output.md) | 32 | Binds an ordered Local Tile source/destination sequence with one common four-PE participation mode decoded to a fixed mask; L terminates only that sequence and never releases a source. |
| [B.IOT](b_iot.md) | [Bundle Input & Output](../groups/bundle_input_output.md) | 32 | Binds an ordered Local Tile source/destination sequence with one common four-PE participation mode decoded to a fixed mask; L terminates only that sequence and never releases a source. |
| [B.IOT](b_iot.md) | [Bundle Input & Output](../groups/bundle_input_output.md) | 32 | Binds an ordered Local Tile source/destination sequence with one common four-PE participation mode decoded to a fixed mask; L terminates only that sequence and never releases a source. |
| [B.SUBVIEW](b_subview.md) | [Bundle Range Modifier](../groups/bundle_range_modifier.md) | 32 | Decodes one source-range subview modifier and retains its XLEN-wrapped derived offset in the immediately preceding binder group. |
| [B.TEXT](b_text.md) | [Bundle Offset](../groups/bundle_offset.md) | 32 | Sets the out-of-line body entry address for a decoupled bundle. |
| [BC.IALL](bc_iall.md) | [SYS](../groups/sys.md) | 32 | Branch-predictor cache invalidate all entries. |
| [BC.IVA](bc_iva.md) | [SYS](../groups/sys.md) | 32 | Branch-predictor cache invalidate by address. |
| [BCNT](bcnt.md) | [ALU](../groups/alu.md) | 32 | Population count. Counts the number of set bits in a register. |
| [BIC](bic.md) | [ALU](../groups/alu.md) | 32 | Bit clear / AND-NOT. |
| [BIS](bis.md) | [ALU](../groups/alu.md) | 32 | Bit set / OR. |
| [BSE](bse.md) | [SYS](../groups/sys.md) | 32 | BSE publishes the SendEvent nonblocking execution-control request. |
| [BSTART](bstart.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Block split marker. Terminates the current basic block and begins the next. Encodes block type and transition kind. |
| [BSTART](bstart.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Block split marker. Terminates the current basic block and begins the next. Encodes block type and transition kind. |
| [BSTART.CALL](bstart_call.md) | [BSTART](../groups/bstart.md) | 32 | Atomic fused call with independent call-target and return-target fields; transfers to the call block and writes `ra`. This exact aggregate is distinct from the generic bare-call form, which preserves `ra` and requires an adjacent `SETRET` or `C.SETRET`. |
| [BSTART.FP](bstart_fp.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.GMOV](bstart_gmov.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.ICALL](bstart_icall.md) | [BSTART](../groups/bstart.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.MGATHER](bstart_mgather.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.MGATHER.CAS](bstart_mgather_cas.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.MGATHER.MASK](bstart_mgather_mask.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.MPAR](bstart_mpar.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.MSCATTER](bstart_mscatter.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.MSCATTER.MASK](bstart_mscatter_mask.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.MSEQ](bstart_mseq.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.SYS](bstart_sys.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TEPL](bstart_tepl.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TGEMV](bstart_tgemv.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TGEMV.ACC](bstart_tgemv_acc.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TGEMV.BIAS](bstart_tgemv_bias.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TGEMVMX](bstart_tgemvmx.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TGEMVMX.ACC](bstart_tgemvmx_acc.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TGEMVMX.BIAS](bstart_tgemvmx_bias.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TLOAD](bstart_tload.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Loads a 64-bit value from memory. |
| [BSTART.TMATMUL](bstart_tmatmul.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TMATMUL.ACC](bstart_tmatmul_acc.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TMATMUL.BIAS](bstart_tmatmul_bias.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TMATMULMX](bstart_tmatmulmx.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TMATMULMX.ACC](bstart_tmatmulmx_acc.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TMATMULMX.BIAS](bstart_tmatmulmx_bias.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TMOV](bstart_tmov.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TPREFETCH](bstart_tprefetch.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TSTORE](bstart_tstore.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Stores a register value to memory. |
| [BSTART.VPAR](bstart_vpar.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.VSEQ](bstart_vseq.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTOP](bstop.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Block termination marker. Ends the current basic block. |
| [BWE](bwe.md) | [SYS](../groups/sys.md) | 32 | BWE publishes the WaitEvent nonblocking execution-control request. |
| [BWI](bwi.md) | [SYS](../groups/sys.md) | 32 | BWI publishes the WaitInterrupt nonblocking execution-control request. |
| [BWT](bwt.md) | [SYS](../groups/sys.md) | 32 | BWT publishes the WaitTimeout nonblocking execution-control request. |
| [BXS](bxs.md) | [ALU](../groups/alu.md) | 32 | Bit-field extract signed. |
| [BXU](bxu.md) | [ALU](../groups/alu.md) | 32 | Bit-field extract unsigned. |

### C

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [C.ADD](c_add.md) | [ALU](../groups/alu.md) | 16 | [16-bit C.] Integer addition. |
| [C.ADDI](c_addi.md) | [ALU](../groups/alu.md) | 16 | C.ADDI snapshots one complete Reg5 source, sign-extends simm5, adds modulo 2^XLEN, and pushes the result to T. |
| [C.AND](c_and.md) | [ALU](../groups/alu.md) | 16 | [16-bit C.] Bitwise AND. |
| [C.B.DIMI](c_b_dimi.md) | [Bundle Dimension](../groups/bundle_dimension.md) | 16 | Zero-extends imm8 and writes one selected bundle-local LB exactly once. |
| [C.BSTART](c_bstart.md) | [Bundle Split](../groups/bundle_split.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART](c_bstart.md) | [Bundle Split](../groups/bundle_split.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.FP](c_bstart_fp.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.MPAR](c_bstart_mpar.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.MSEQ](c_bstart_mseq.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.STD](c_bstart_std.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.SYS](c_bstart_sys.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.VPAR](c_bstart_vpar.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.VSEQ](c_bstart_vseq.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTOP](c_bstop.md) | [Bundle Split](../groups/bundle_split.md) | 16 | [16-bit C.] Marks the end of the current block. |
| [C.CMP.EQI](c_cmp_eqi.md) | [BRU](../groups/bru.md) | 16 | C.CMP.EQI - Compare scalar operands and write the encoded boolean result. |
| [C.CMP.NEI](c_cmp_nei.md) | [BRU](../groups/bru.md) | 16 | C.CMP.NEI - Compare scalar operands and write the encoded boolean result. |
| [C.EBREAK](c_ebreak.md) | [SYS](../groups/sys.md) | 16 | C.EBREAK raises software-breakpoint trap 50 with its 5-bit immediate as cause. |
| [C.LDI](c_ldi.md) | [LDA/BASE_IMM](../groups/lda_base_imm.md) | 16 | C.LDI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [C.LWI](c_lwi.md) | [LDA/BASE_IMM](../groups/lda_base_imm.md) | 16 | C.LWI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [C.MOVI](c_movi.md) | [ALU](../groups/alu.md) | 16 | C.MOVI sign-extends its encoded five-bit immediate to XLEN and publishes it through RegDst. |
| [C.MOVR](c_movr.md) | [ALU](../groups/alu.md) | 16 | C.MOVR snapshots a Reg5 source and publishes the complete XLEN value unchanged through RegDst. |
| [C.OR](c_or.md) | [ALU](../groups/alu.md) | 16 | [16-bit C.] Bitwise OR. |
| [C.SDI](c_sdi.md) | [STA/BASE_IMM](../groups/sta_base_imm.md) | 16 | C.SDI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [C.SETC.EQ](c_setc_eq.md) | [BRU](../groups/bru.md) | 16 | [16-bit C.] Sets the block-commit condition. |
| [C.SETC.NE](c_setc_ne.md) | [BRU](../groups/bru.md) | 16 | [16-bit C.] Sets the block-commit condition. |
| [C.SETC.TGT](c_setc_tgt.md) | [ALU](../groups/alu.md) | 16 | [16-bit C.] Sets the block-commit condition. |
| [C.SETRET](c_setret.md) | [ALU](../groups/alu.md) | 16 | Materialize an unsigned halfword-scaled TPC-relative return address in ra and captured return state. |
| [C.SEXT.B](c_sext_b.md) | [ALU](../groups/alu.md) | 16 | C.SEXT.B sign-extends SrcL[7:0] to XLEN and pushes the result to T. |
| [C.SEXT.H](c_sext_h.md) | [ALU](../groups/alu.md) | 16 | C.SEXT.H sign-extends SrcL[15:0] to XLEN and pushes the result to T. |
| [C.SEXT.W](c_sext_w.md) | [ALU](../groups/alu.md) | 16 | C.SEXT.W sign-extends SrcL[31:0] to XLEN and pushes the result to T. |
| [C.SLLI](c_slli.md) | [ALU](../groups/alu.md) | 16 | C.SLLI snapshots the pre-instruction T#1 value, logically shifts it left by uimm5, and pushes the XLEN result to T. |
| [C.SRLI](c_srli.md) | [ALU](../groups/alu.md) | 16 | C.SRLI snapshots the pre-instruction T#1 value, logically shifts it right by uimm5, and pushes the XLEN result to T. |
| [C.SSRGET](c_ssrget.md) | [SYS](../groups/sys.md) | 16 | C.SSRGET reads the complete encoded system-register address. |
| [C.SUB](c_sub.md) | [ALU](../groups/alu.md) | 16 | [16-bit C.] Integer subtraction. |
| [C.SWI](c_swi.md) | [STA/BASE_IMM](../groups/sta_base_imm.md) | 16 | C.SWI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [C.ZEXT.B](c_zext_b.md) | [ALU](../groups/alu.md) | 16 | C.ZEXT.B zero-extends SrcL[7:0] to XLEN and pushes the result to T. |
| [C.ZEXT.H](c_zext_h.md) | [ALU](../groups/alu.md) | 16 | C.ZEXT.H zero-extends SrcL[15:0] to XLEN and pushes the result to T. |
| [C.ZEXT.W](c_zext_w.md) | [ALU](../groups/alu.md) | 16 | C.ZEXT.W zero-extends SrcL[31:0] to XLEN and pushes the result to T. |
| [CASB](casb.md) | [AMO](../groups/amo.md) | 32 | CASB atomically compares and conditionally replaces one byte, then publishes the prior value. |
| [CASD](casd.md) | [AMO](../groups/amo.md) | 32 | CASD atomically compares and conditionally replaces one doubleword, then publishes the prior value. |
| [CASH](cash.md) | [AMO](../groups/amo.md) | 32 | CASH atomically compares and conditionally replaces one halfword, then publishes the prior value. |
| [CASW](casw.md) | [AMO](../groups/amo.md) | 32 | CASW atomically compares and conditionally replaces one word, then publishes the prior value. |
| [CLZ](clz.md) | [ALU](../groups/alu.md) | 32 | Count leading zeros. |
| [CMP.AND](cmp_and.md) | [BRU](../groups/bru.md) | 32 | CMP.AND - Combine scalar comparison results with the encoded logical operation. |
| [CMP.ANDI](cmp_andi.md) | [BRU](../groups/bru.md) | 32 | CMP.ANDI - Combine scalar comparison results with the encoded logical operation. |
| [CMP.EQ](cmp_eq.md) | [BRU](../groups/bru.md) | 32 | Compare equal. Sets destination to 1 if operands are equal. |
| [CMP.EQI](cmp_eqi.md) | [BRU](../groups/bru.md) | 32 | CMP.EQI - Compare scalar operands and write the encoded boolean result. |
| [CMP.GE](cmp_ge.md) | [BRU](../groups/bru.md) | 32 | Compare greater-or-equal (signed). |
| [CMP.GEI](cmp_gei.md) | [BRU](../groups/bru.md) | 32 | CMP.GEI - Compare scalar operands and write the encoded boolean result. |
| [CMP.GEU](cmp_geu.md) | [BRU](../groups/bru.md) | 32 | Compare greater-or-equal (unsigned). |
| [CMP.GEUI](cmp_geui.md) | [BRU](../groups/bru.md) | 32 | CMP.GEUI - Compare scalar operands and write the encoded boolean result. |
| [CMP.LT](cmp_lt.md) | [BRU](../groups/bru.md) | 32 | Compare less-than (signed). |
| [CMP.LTI](cmp_lti.md) | [BRU](../groups/bru.md) | 32 | CMP.LTI - Compare scalar operands and write the encoded boolean result. |
| [CMP.LTU](cmp_ltu.md) | [BRU](../groups/bru.md) | 32 | Compare less-than (unsigned). |
| [CMP.LTUI](cmp_ltui.md) | [BRU](../groups/bru.md) | 32 | CMP.LTUI - Compare scalar operands and write the encoded boolean result. |
| [CMP.NE](cmp_ne.md) | [BRU](../groups/bru.md) | 32 | Compare not-equal. |
| [CMP.NEI](cmp_nei.md) | [BRU](../groups/bru.md) | 32 | CMP.NEI - Compare scalar operands and write the encoded boolean result. |
| [CMP.OR](cmp_or.md) | [BRU](../groups/bru.md) | 32 | CMP.OR - Combine scalar comparison results with the encoded logical operation. |
| [CMP.ORI](cmp_ori.md) | [BRU](../groups/bru.md) | 32 | CMP.ORI - Combine scalar comparison results with the encoded logical operation. |
| [CSEL](csel.md) | [ALU](../groups/alu.md) | 32 | Conditional select. `Dest = (SrcP != 0) ? SrcL : SrcR`. |
| [CTZ](ctz.md) | [ALU](../groups/alu.md) | 32 | Count trailing zeros. |

### D

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [DC.CISW](dc_cisw.md) | [SYS](../groups/sys.md) | 32 | Data cache clean-and-invalidate by set/way. |
| [DC.CIVA](dc_civa.md) | [SYS](../groups/sys.md) | 32 | DC.CIVA completes the data-cache clean-and-invalidate scope token maintenance operation synchronously. |
| [DC.CSW](dc_csw.md) | [SYS](../groups/sys.md) | 32 | DC.CSW completes the data-cache clean-by-set/way scope token maintenance operation synchronously. |
| [DC.CVA](dc_cva.md) | [SYS](../groups/sys.md) | 32 | DC.CVA completes the data-cache clean-by-address scope token maintenance operation synchronously. |
| [DC.IALL](dc_iall.md) | [SYS](../groups/sys.md) | 32 | DC.IALL completes the data-cache all-entry scope maintenance operation synchronously. |
| [DC.ISW](dc_isw.md) | [SYS](../groups/sys.md) | 32 | Data cache invalidate by set/way. |
| [DC.IVA](dc_iva.md) | [SYS](../groups/sys.md) | 32 | Data cache invalidate by address. |
| [DC.ZVA](dc_zva.md) | [SYS](../groups/sys.md) | 32 | DC.ZVA completes the data-cache zero-by-address scope token maintenance operation synchronously. |
| [DIV](div.md) | [ALU](../groups/alu.md) | 32 | Signed integer division. |
| [DIVU](divu.md) | [ALU](../groups/alu.md) | 32 | Unsigned integer division. |
| [DIVUW](divuw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word unsigned integer division. |
| [DIVW](divw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word signed integer division. |
| [DMA](dma.md) | [AMO](../groups/amo.md) | 32 | DMA performs an exact 64-byte copy, validates both ranges before effects, snapshots the source so overlap has memmove semantics, and guarantees that any fault leaves memory unchanged for precise full reissue. |

### E

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [EBREAK](ebreak.md) | [SYS](../groups/sys.md) | 32 | Environment break instruction. Traps to the debugging or OS handler. |
| [ERCOV](ercov.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Inventories an extension-owned execution-context recovery family rejected by PTO before operand interpretation or effects. |
| [ESAVE](esave.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Inventories an extension-owned execution-context save family rejected by PTO before operand interpretation or effects. |

### F

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [FABS](fabs.md) | [FSU](../groups/fsu.md) | 32 | Floating-point absolute value. |
| [FADD](fadd.md) | [FSU](../groups/fsu.md) | 32 | Floating-point addition. |
| [FCVT](fcvt.md) | [FSU](../groups/fsu.md) | 32 | Floating-point format conversion. |
| [FCVTA](fcvta.md) | [FSU](../groups/fsu.md) | 32 | FCVTA converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-to-nearest, ties-away mode. |
| [FCVTM](fcvtm.md) | [FSU](../groups/fsu.md) | 32 | FCVTM converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-down mode. |
| [FCVTN](fcvtn.md) | [FSU](../groups/fsu.md) | 32 | FCVTN converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-nearest mode. |
| [FCVTP](fcvtp.md) | [FSU](../groups/fsu.md) | 32 | FCVTP converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-up mode. |
| [FCVTZ](fcvtz.md) | [FSU](../groups/fsu.md) | 32 | FCVTZ converts a selected FP64 or FP32 carrier to integer carrier code 0 through 14 with fixed round-toward-zero mode. |
| [FDIV](fdiv.md) | [FSU](../groups/fsu.md) | 32 | Floating-point division. |
| [FENCE.D](fence_d.md) | [SYS](../groups/sys.md) | 32 | Data memory ordering fence. |
| [FENCE.I](fence_i.md) | [SYS](../groups/sys.md) | 32 | Instruction-cache fence. Synchronizes instruction fetch with prior stores. |
| [FENTRY](fentry.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Creates a restartable stack frame by snapshotting and storing one inclusive callee-save register-ring range. |
| [FEQ](feq.md) | [FSU](../groups/fsu.md) | 32 | Floating-point equality comparison. Writes 1 if ordered and equal. |
| [FEQS](feqs.md) | [FSU](../groups/fsu.md) | 32 | FEQS performs ordered signaling equality and returns canonical XLEN zero or one. |
| [FEXIT](fexit.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Destroys a restartable stack frame and restores one inclusive callee-save register-ring range. |
| [FEXP](fexp.md) | [FSU](../groups/fsu.md) | 32 | FEXP applies the active numeric profile exponential operation to the selected FP64 or FP32 carrier. |
| [FGE](fge.md) | [FSU](../groups/fsu.md) | 32 | Floating-point greater-or-equal comparison (ordered). |
| [FGES](fges.md) | [FSU](../groups/fsu.md) | 32 | FGES performs ordered signaling greater-than-or-equal comparison and returns canonical XLEN zero or one. |
| [FLT](flt.md) | [FSU](../groups/fsu.md) | 32 | Floating-point less-than comparison (ordered). |
| [FLTS](flts.md) | [FSU](../groups/fsu.md) | 32 | FLTS performs ordered signaling less-than comparison and returns canonical XLEN zero or one. |
| [FMADD](fmadd.md) | [FSU](../groups/fsu.md) | 32 | FMADD computes one fused SrcL multiplied by SrcR plus SrcA operation through the active numeric profile. |
| [FMAX](fmax.md) | [FSU](../groups/fsu.md) | 32 | Floating-point maximum. |
| [FMIN](fmin.md) | [FSU](../groups/fsu.md) | 32 | Floating-point minimum. |
| [FMSUB](fmsub.md) | [FSU](../groups/fsu.md) | 32 | FMSUB computes one fused SrcL multiplied by SrcR minus SrcA operation through the active numeric profile. |
| [FMUL](fmul.md) | [FSU](../groups/fsu.md) | 32 | Floating-point multiplication. |
| [FNE](fne.md) | [FSU](../groups/fsu.md) | 32 | FNE performs ordered quiet inequality and returns canonical XLEN zero or one. |
| [FNES](fnes.md) | [FSU](../groups/fsu.md) | 32 | FNES performs ordered signaling inequality and returns canonical XLEN zero or one. |
| [FNMADD](fnmadd.md) | [FSU](../groups/fsu.md) | 32 | FNMADD computes the negation of one fused SrcL multiplied by SrcR plus SrcA operation through the active numeric profile. |
| [FNMSUB](fnmsub.md) | [FSU](../groups/fsu.md) | 32 | FNMSUB computes the negation of one fused SrcL multiplied by SrcR minus SrcA operation through the active numeric profile. |
| [FRECIP](frecip.md) | [FSU](../groups/fsu.md) | 32 | FRECIP applies the active numeric profile reciprocal operation to the selected FP64 or FP32 carrier. |
| [FRET.RA](fret_ra.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Restores a restartable stack frame and returns through the pre-restore architectural return address. |
| [FRET.STK](fret_stk.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Restores a restartable stack frame whose first stack slot supplies the validated return target. |
| [FSQRT](fsqrt.md) | [FSU](../groups/fsu.md) | 32 | Floating-point square root. |
| [FSUB](fsub.md) | [FSU](../groups/fsu.md) | 32 | Floating-point subtraction. |

### H

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [HL.ADDI](hl_addi.md) | [ALU](../groups/alu.md) | 48 | HL.ADDI applies XLEN addition to SrcL and a zero-extended 24-bit immediate. |
| [HL.ADDIW](hl_addiw.md) | [ALU](../groups/alu.md) | 48 | HL.ADDIW applies word addition to SrcL[31:0] and the low word of a zero-extended 24-bit immediate, then sign-extends the 32-bit result. |
| [HL.ADDTPC](hl_addtpc.md) | [BRU](../groups/bru.md) | 48 | HL.ADDTPC - Add a signed 4 KiB page displacement to the current TPC. |
| [HL.ANDI](hl_andi.md) | [ALU](../groups/alu.md) | 48 | HL.ANDI applies XLEN bitwise conjunction to SrcL and a sign-extended 24-bit immediate. |
| [HL.ANDIW](hl_andiw.md) | [ALU](../groups/alu.md) | 48 | HL.ANDIW applies word bitwise conjunction to SrcL[31:0] and the low word of a sign-extended 24-bit immediate, then sign-extends the 32-bit result. |
| [HL.BFI](hl_bfi.md) | [ALU](../groups/alu.md) | 48 | [48-bit HL.] Bit-field insert. |
| [HL.BSTART CALL](hl_bstart_call.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Atomic fused call with independent call-target and return-target fields; transfers to the call block and writes `ra`. This exact aggregate is distinct from the generic bare-call form, which preserves `ra` and requires an adjacent `SETRET` or `C.SETRET`. |
| [HL.BSTART.FP](hl_bstart_fp.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.FP](hl_bstart_fp.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.FP](hl_bstart_fp.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.FP](hl_bstart_fp.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](hl_bstart_std.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](hl_bstart_std.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](hl_bstart_std.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](hl_bstart_std.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.SYS](hl_bstart_sys.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.CASB](hl_casb.md) | [AMO](../groups/amo.md) | 48 | HL.CASB atomically compares and conditionally replaces one byte, then publishes the prior value. |
| [HL.CASD](hl_casd.md) | [AMO](../groups/amo.md) | 48 | HL.CASD atomically compares and conditionally replaces one doubleword, then publishes the prior value. |
| [HL.CASH](hl_cash.md) | [AMO](../groups/amo.md) | 48 | HL.CASH atomically compares and conditionally replaces one halfword, then publishes the prior value. |
| [HL.CASW](hl_casw.md) | [AMO](../groups/amo.md) | 48 | HL.CASW atomically compares and conditionally replaces one word, then publishes the prior value. |
| [HL.CCAT](hl_ccat.md) | [ALU](../groups/alu.md) | 48 | HL.CCAT logically right-shifts {SrcL, SrcR}, writes the low 64-bit result to Dst0, then writes the high result to Dst1. |
| [HL.CCATW](hl_ccatw.md) | [ALU](../groups/alu.md) | 48 | HL.CCATW logically right-shifts {SrcL[31:0], SrcR[31:0]}, sign-extends the low then high 32-bit results, and writes them in order. |
| [HL.CMP.ANDI](hl_cmp_andi.md) | [BRU](../groups/bru.md) | 48 | HL.CMP.ANDI - Combine scalar comparison results with the encoded logical operation. |
| [HL.CMP.EQI](hl_cmp_eqi.md) | [BRU](../groups/bru.md) | 48 | HL.CMP.EQI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.GEI](hl_cmp_gei.md) | [BRU](../groups/bru.md) | 48 | HL.CMP.GEI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.GEUI](hl_cmp_geui.md) | [BRU](../groups/bru.md) | 48 | HL.CMP.GEUI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.LTI](hl_cmp_lti.md) | [BRU](../groups/bru.md) | 48 | HL.CMP.LTI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.LTUI](hl_cmp_ltui.md) | [BRU](../groups/bru.md) | 48 | HL.CMP.LTUI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.NEI](hl_cmp_nei.md) | [BRU](../groups/bru.md) | 48 | HL.CMP.NEI - Compare scalar operands and write the encoded boolean result. |
| [HL.CMP.ORI](hl_cmp_ori.md) | [BRU](../groups/bru.md) | 48 | HL.CMP.ORI - Combine scalar comparison results with the encoded logical operation. |
| [HL.DIV](hl_div.md) | [ALU](../groups/alu.md) | 48 | [48-bit HL.] Signed integer division. |
| [HL.DIVU](hl_divu.md) | [ALU](../groups/alu.md) | 48 | [48-bit HL.] Unsigned integer division. |
| [HL.DIVUW](hl_divuw.md) | [ALU](../groups/alu.md) | 48 | HL.DIVUW computes a unsigned low-32-bit quotient/remainder pair from source snapshots, then publishes quotient followed by remainder. |
| [HL.DIVW](hl_divw.md) | [ALU](../groups/alu.md) | 48 | HL.DIVW computes a signed low-32-bit quotient/remainder pair from source snapshots, then publishes quotient followed by remainder. |
| [HL.LB.PCR](hl_lb_pcr.md) | [LDA/PC_REL](../groups/lda_pc_rel.md) | 48 | HL.LB.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LB.PO](hl_lb_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LB.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LB.PR](hl_lb_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LB.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBI](hl_lbi.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LBI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBI.PO](hl_lbi_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LBI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBI.PR](hl_lbi_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LBI.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBIP](hl_lbip.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LBIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 1-byte values. |
| [HL.LBP](hl_lbp.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LBP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 1-byte values. |
| [HL.LBU.PCR](hl_lbu_pcr.md) | [LDA/PC_REL](../groups/lda_pc_rel.md) | 48 | HL.LBU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBU.PO](hl_lbu_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LBU.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBU.PR](hl_lbu_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LBU.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBUI](hl_lbui.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LBUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBUI.PO](hl_lbui_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LBUI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBUI.PR](hl_lbui_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LBUI.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [HL.LBUIP](hl_lbuip.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LBUIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 1-byte values. |
| [HL.LBUP](hl_lbup.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LBUP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 1-byte values. |
| [HL.LD.PCR](hl_ld_pcr.md) | [LDA/PC_REL](../groups/lda_pc_rel.md) | 48 | HL.LD.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LD.PO](hl_ld_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LD.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LD.PR](hl_ld_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LD.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LDI](hl_ldi.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LDI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LDI.PO](hl_ldi_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LDI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LDI.PR](hl_ldi_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LDI.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LDI.U](hl_ldi_u.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LDI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LDI.UPO](hl_ldi_upo.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LDI.UPO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LDI.UPR](hl_ldi_upr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LDI.UPR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [HL.LDIP](hl_ldip.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LDIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 8-byte values. |
| [HL.LDIP.U](hl_ldip_u.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LDIP.U snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 8-byte values. |
| [HL.LDP](hl_ldp.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LDP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 8-byte values. |
| [HL.LH.PCR](hl_lh_pcr.md) | [LDA/PC_REL](../groups/lda_pc_rel.md) | 48 | HL.LH.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LH.PO](hl_lh_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LH.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LH.PR](hl_lh_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LH.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHI](hl_lhi.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LHI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHI.PO](hl_lhi_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LHI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHI.PR](hl_lhi_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LHI.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHI.U](hl_lhi_u.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LHI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHI.UPO](hl_lhi_upo.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LHI.UPO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHI.UPR](hl_lhi_upr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LHI.UPR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHIP](hl_lhip.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LHIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LHIP.U](hl_lhip_u.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LHIP.U snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LHP](hl_lhp.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LHP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LHU.PCR](hl_lhu_pcr.md) | [LDA/PC_REL](../groups/lda_pc_rel.md) | 48 | HL.LHU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHU.PO](hl_lhu_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LHU.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHU.PR](hl_lhu_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LHU.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUI](hl_lhui.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LHUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUI.PO](hl_lhui_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LHUI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUI.PR](hl_lhui_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LHUI.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUI.U](hl_lhui_u.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LHUI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUI.UPO](hl_lhui_upo.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LHUI.UPO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUI.UPR](hl_lhui_upr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LHUI.UPR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [HL.LHUIP](hl_lhuip.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LHUIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LHUIP.U](hl_lhuip_u.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LHUIP.U snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LHUP](hl_lhup.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LHUP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 2-byte values. |
| [HL.LIS](hl_lis.md) | [ALU](../groups/alu.md) | 48 | HL.LIS sign-extends its split encoded 32-bit immediate to XLEN and publishes the result through RegDst. |
| [HL.LIU](hl_liu.md) | [ALU](../groups/alu.md) | 48 | HL.LIU zero-extends its split encoded 32-bit immediate to XLEN and publishes the result through RegDst. |
| [HL.LUI](hl_lui.md) | [ALU](../groups/alu.md) | 48 | HL.LUI places its split 32-bit immediate in result bits 63:32 and clears result bits 31:0. |
| [HL.LW.PCR](hl_lw_pcr.md) | [LDA/PC_REL](../groups/lda_pc_rel.md) | 48 | HL.LW.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LW.PO](hl_lw_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LW.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LW.PR](hl_lw_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LW.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWI](hl_lwi.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LWI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWI.PO](hl_lwi_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LWI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWI.PR](hl_lwi_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LWI.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWI.U](hl_lwi_u.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LWI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWI.UPO](hl_lwi_upo.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LWI.UPO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWI.UPR](hl_lwi_upr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LWI.UPR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWIP](hl_lwip.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LWIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.LWIP.U](hl_lwip_u.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LWIP.U snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.LWP](hl_lwp.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LWP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.LWU.PCR](hl_lwu_pcr.md) | [LDA/PC_REL](../groups/lda_pc_rel.md) | 48 | HL.LWU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWU.PO](hl_lwu_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LWU.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWU.PR](hl_lwu_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LWU.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUI](hl_lwui.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LWUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUI.PO](hl_lwui_po.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LWUI.PO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUI.PR](hl_lwui_pr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LWUI.PR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUI.U](hl_lwui_u.md) | [LDA/LONG](../groups/lda_long.md) | 48 | HL.LWUI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUI.UPO](hl_lwui_upo.md) | [LDA/POST_INDEX](../groups/lda_post_index.md) | 48 | HL.LWUI.UPO snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUI.UPR](hl_lwui_upr.md) | [LDA/PRE_INDEX](../groups/lda_pre_index.md) | 48 | HL.LWUI.UPR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [HL.LWUIP](hl_lwuip.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LWUIP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.LWUIP.U](hl_lwuip_u.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LWUIP.U snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.LWUP](hl_lwup.md) | [LDA/PAIR](../groups/lda_pair.md) | 48 | HL.LWUP snapshots its scalar sources, forms its encoded address, and loads two adjacent aligned little-endian 4-byte values. |
| [HL.MADD](hl_madd.md) | [ALU](../groups/alu.md) | 48 | HL.MADD computes a signed 128-bit product plus a sign-extended XLEN addend and publishes low then high halves. |
| [HL.MADDW](hl_maddw.md) | [ALU](../groups/alu.md) | 48 | HL.MADDW computes a signed 64-bit word multiply-add result and publishes its sign-extended low and high 32-bit halves. |
| [HL.MIADD](hl_miadd.md) | [ALU](../groups/alu.md) | 48 | HL.MIADD multiplies SrcR by the unsigned 19-bit immediate, adds SrcL modulo 2^PTO_XLEN, and publishes the result. |
| [HL.MISUB](hl_misub.md) | [ALU](../groups/alu.md) | 48 | HL.MISUB multiplies SrcR by the unsigned 19-bit immediate, subtracts the product from SrcL modulo 2^PTO_XLEN, and publishes the result. |
| [HL.MUL](hl_mul.md) | [ALU](../groups/alu.md) | 48 | [48-bit HL.] Integer multiply. |
| [HL.MULU](hl_mulu.md) | [ALU](../groups/alu.md) | 48 | HL.MULU computes an unsigned 128-bit scalar product and publishes its low half followed by its high half. |
| [HL.ORI](hl_ori.md) | [ALU](../groups/alu.md) | 48 | HL.ORI applies XLEN bitwise inclusive-or to SrcL and a sign-extended 24-bit immediate. |
| [HL.ORIW](hl_oriw.md) | [ALU](../groups/alu.md) | 48 | HL.ORIW applies word bitwise inclusive-or to SrcL[31:0] and the low word of a sign-extended 24-bit immediate, then sign-extends the 32-bit result. |
| [HL.PRF](hl_prf.md) | [LDA](../groups/lda.md) | 48 | HL.PRF snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint with no destination effect. |
| [HL.PRF.A](hl_prf_a.md) | [LDA](../groups/lda.md) | 48 | HL.PRF.A snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint and publishes the effective address. |
| [HL.PRFI.U](hl_prfi_u.md) | [LDA](../groups/lda.md) | 48 | HL.PRFI.U snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint with no destination effect. |
| [HL.PRFI.UA](hl_prfi_ua.md) | [LDA](../groups/lda.md) | 48 | HL.PRFI.UA snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint and publishes the effective address. |
| [HL.QMT](hl_qmt.md) | [General](../groups/general.md) | 48 | Queries, initializes, notifies, suspends, or restores one General Queue Management queue. |
| [HL.QPOP](hl_qpop.md) | [General](../groups/general.md) | 48 | Atomically pops one 64-bit head entry from a General Queue Management queue. |
| [HL.QPUSH](hl_qpush.md) | [General](../groups/general.md) | 48 | Atomically pushes one 64-bit entry at the tail or head of a General Queue Management queue. |
| [HL.REM](hl_rem.md) | [ALU](../groups/alu.md) | 48 | [48-bit HL.] Signed integer remainder. |
| [HL.REMU](hl_remu.md) | [ALU](../groups/alu.md) | 48 | [48-bit HL.] Unsigned integer remainder. |
| [HL.REMUW](hl_remuw.md) | [ALU](../groups/alu.md) | 48 | HL.REMUW computes an unsigned low-32-bit remainder/quotient pair from source snapshots, then publishes remainder followed by quotient. |
| [HL.REMW](hl_remw.md) | [ALU](../groups/alu.md) | 48 | HL.REMW computes a signed low-32-bit remainder/quotient pair from source snapshots, then publishes remainder followed by quotient. |
| [HL.SB.PCR](hl_sb_pcr.md) | [STA/PC_REL](../groups/sta_pc_rel.md) | 48 | HL.SB.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SB.PO](hl_sb_po.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SB.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SB.PR](hl_sb_pr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SB.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SBI](hl_sbi.md) | [STA/LONG](../groups/sta_long.md) | 48 | HL.SBI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SBI.PO](hl_sbi_po.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SBI.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SBI.PR](hl_sbi_pr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SBI.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [HL.SBIP](hl_sbip.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SBIP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 1-byte values. |
| [HL.SBP](hl_sbp.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SBP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 1-byte values. |
| [HL.SD.PCR](hl_sd_pcr.md) | [STA/PC_REL](../groups/sta_pc_rel.md) | 48 | HL.SD.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SD.PO](hl_sd_po.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SD.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SD.PR](hl_sd_pr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SD.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SD.UPO](hl_sd_upo.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SD.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SD.UPR](hl_sd_upr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SD.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI](hl_sdi.md) | [STA/LONG](../groups/sta_long.md) | 48 | HL.SDI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI.PO](hl_sdi_po.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SDI.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI.PR](hl_sdi_pr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SDI.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI.U](hl_sdi_u.md) | [STA/LONG](../groups/sta_long.md) | 48 | HL.SDI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI.UPO](hl_sdi_upo.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SDI.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDI.UPR](hl_sdi_upr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SDI.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [HL.SDIP](hl_sdip.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SDIP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 8-byte values. |
| [HL.SDIP.U](hl_sdip_u.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SDIP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 8-byte values. |
| [HL.SDP](hl_sdp.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SDP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 8-byte values. |
| [HL.SDP.U](hl_sdp_u.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SDP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 8-byte values. |
| [HL.SETC.ANDI](hl_setc_andi.md) | [BRU](../groups/bru.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.EQI](hl_setc_eqi.md) | [BRU](../groups/bru.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.GEI](hl_setc_gei.md) | [BRU](../groups/bru.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.GEUI](hl_setc_geui.md) | [BRU](../groups/bru.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.LTI](hl_setc_lti.md) | [BRU](../groups/bru.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.LTUI](hl_setc_ltui.md) | [BRU](../groups/bru.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.NEI](hl_setc_nei.md) | [BRU](../groups/bru.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.ORI](hl_setc_ori.md) | [BRU](../groups/bru.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETRET](hl_setret.md) | [BRU](../groups/bru.md) | 48 | HL.SETRET - Write the architectural return address. |
| [HL.SH.PCR](hl_sh_pcr.md) | [STA/PC_REL](../groups/sta_pc_rel.md) | 48 | HL.SH.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SH.PO](hl_sh_po.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SH.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SH.PR](hl_sh_pr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SH.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SH.UPO](hl_sh_upo.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SH.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SH.UPR](hl_sh_upr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SH.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI](hl_shi.md) | [STA/LONG](../groups/sta_long.md) | 48 | HL.SHI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI.PO](hl_shi_po.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SHI.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI.PR](hl_shi_pr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SHI.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI.U](hl_shi_u.md) | [STA/LONG](../groups/sta_long.md) | 48 | HL.SHI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI.UPO](hl_shi_upo.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SHI.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHI.UPR](hl_shi_upr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SHI.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [HL.SHIP](hl_ship.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SHIP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 2-byte values. |
| [HL.SHIP.U](hl_ship_u.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SHIP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 2-byte values. |
| [HL.SHP](hl_shp.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SHP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 2-byte values. |
| [HL.SHP.U](hl_shp_u.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SHP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 2-byte values. |
| [HL.SSRGET](hl_ssrget.md) | [SYS](../groups/sys.md) | 48 | HL.SSRGET reads the complete encoded system-register address. |
| [HL.SSRSET](hl_ssrset.md) | [SYS](../groups/sys.md) | 48 | HL.SSRSET writes the complete encoded system-register address. |
| [HL.SUBI](hl_subi.md) | [ALU](../groups/alu.md) | 48 | HL.SUBI applies XLEN subtraction to SrcL and a zero-extended 24-bit immediate. |
| [HL.SUBIW](hl_subiw.md) | [ALU](../groups/alu.md) | 48 | HL.SUBIW applies word subtraction to SrcL[31:0] and the low word of a zero-extended 24-bit immediate, then sign-extends the 32-bit result. |
| [HL.SW.PCR](hl_sw_pcr.md) | [STA/PC_REL](../groups/sta_pc_rel.md) | 48 | HL.SW.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SW.PO](hl_sw_po.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SW.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SW.PR](hl_sw_pr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SW.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SW.UPO](hl_sw_upo.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SW.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SW.UPR](hl_sw_upr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SW.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI](hl_swi.md) | [STA/LONG](../groups/sta_long.md) | 48 | HL.SWI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI.PO](hl_swi_po.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SWI.PO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI.PR](hl_swi_pr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SWI.PR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI.U](hl_swi_u.md) | [STA/LONG](../groups/sta_long.md) | 48 | HL.SWI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI.UPO](hl_swi_upo.md) | [STA/POST_INDEX](../groups/sta_post_index.md) | 48 | HL.SWI.UPO snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWI.UPR](hl_swi_upr.md) | [STA/PRE_INDEX](../groups/sta_pre_index.md) | 48 | HL.SWI.UPR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [HL.SWIP](hl_swip.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SWIP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 4-byte values. |
| [HL.SWIP.U](hl_swip_u.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SWIP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 4-byte values. |
| [HL.SWP](hl_swp.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SWP snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 4-byte values. |
| [HL.SWP.U](hl_swp_u.md) | [STA/PAIR](../groups/sta_pair.md) | 48 | HL.SWP.U snapshots its scalar sources, forms its encoded address, and stores two adjacent aligned little-endian 4-byte values. |
| [HL.XORI](hl_xori.md) | [ALU](../groups/alu.md) | 48 | HL.XORI applies XLEN bitwise exclusive-or to SrcL and a sign-extended 24-bit immediate. |
| [HL.XORIW](hl_xoriw.md) | [ALU](../groups/alu.md) | 48 | HL.XORIW applies word bitwise exclusive-or to SrcL[31:0] and the low word of a sign-extended 24-bit immediate, then sign-extends the 32-bit result. |

### I

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [IC.IALL](ic_iall.md) | [SYS](../groups/sys.md) | 32 | IC.IALL completes the instruction-cache all-entry scope maintenance operation synchronously. |
| [IC.IVA](ic_iva.md) | [SYS](../groups/sys.md) | 32 | IC.IVA completes the instruction-cache virtual-address scope token maintenance operation synchronously. |

### J

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [J](j.md) | [BRU](../groups/bru.md) | 32 | Unconditional PC-relative jump to a target label. |
| [JR](jr.md) | [BRU](../groups/bru.md) | 32 | Jump register: PC-relative or register-based jump to the address in a register. |

### L

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [L.BSTART.FP](l_bstart_fp.md) | [BSTART](../groups/bstart.md) | 64 | Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind. |
| [L.BSTART.FP](l_bstart_fp.md) | [BSTART](../groups/bstart.md) | 64 | Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind. |
| [L.BSTART.FP](l_bstart_fp.md) | [BSTART](../groups/bstart.md) | 64 | Bare L.BSTART.FP CALL preserves ra. A returning call must be preceded by SETRET or C.SETRET with an explicit return label. |
| [L.BSTART.FP](l_bstart_fp.md) | [BSTART](../groups/bstart.md) | 64 | Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind. |
| [L.BSTART.STD](l_bstart_std.md) | [BSTART](../groups/bstart.md) | 64 | Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind. |
| [L.BSTART.STD](l_bstart_std.md) | [BSTART](../groups/bstart.md) | 64 | Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind. |
| [L.BSTART.STD](l_bstart_std.md) | [BSTART](../groups/bstart.md) | 64 | Bare L.BSTART.STD CALL preserves ra. A returning call must be preceded by SETRET or C.SETRET with an explicit return label. |
| [L.BSTART.STD](l_bstart_std.md) | [BSTART](../groups/bstart.md) | 64 | Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind. |
| [L.BSTART.SYS](l_bstart_sys.md) | [BSTART](../groups/bstart.md) | 64 | Closes the current bundle, initializes the next bundle descriptor, and selects its transfer and execution kind. |
| [L.BSTOP](l_bstop.md) | [Bundle Split](../groups/bundle_split.md) | 64 | Commits the current bundle and transfers to its selected continuation. |
| [LB](lb.md) | [LDA/BASE_REG](../groups/lda_base_reg.md) | 32 | LB snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LB.PCR](lb_pcr.md) | [LDA](../groups/lda.md) | 32 | LB.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LBI](lbi.md) | [LDA/BASE_IMM](../groups/lda_base_imm.md) | 32 | LBI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LBU](lbu.md) | [LDA/BASE_REG](../groups/lda_base_reg.md) | 32 | LBU snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LBU.PCR](lbu_pcr.md) | [LDA](../groups/lda.md) | 32 | LBU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LBUI](lbui.md) | [LDA/BASE_IMM](../groups/lda_base_imm.md) | 32 | LBUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 1-byte value. |
| [LD](ld.md) | [LDA/BASE_REG](../groups/lda_base_reg.md) | 32 | LD snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [LD.ADD](ld_add.md) | [AMO](../groups/amo.md) | 32 | LD.ADD atomically stores the width-sized modular sum and publishes the prior memory value. |
| [LD.AND](ld_and.md) | [AMO](../groups/amo.md) | 32 | LD.AND atomically stores the width-sized bitwise AND and publishes the prior memory value. |
| [LD.OR](ld_or.md) | [AMO](../groups/amo.md) | 32 | LD.OR atomically stores the width-sized bitwise OR and publishes the prior memory value. |
| [LD.PCR](ld_pcr.md) | [LDA](../groups/lda.md) | 32 | LD.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [LD.SMAX](ld_smax.md) | [AMO](../groups/amo.md) | 32 | LD.SMAX atomically stores the width-sized signed maximum and publishes the prior memory value. |
| [LD.SMIN](ld_smin.md) | [AMO](../groups/amo.md) | 32 | LD.SMIN atomically stores the width-sized signed minimum and publishes the prior memory value. |
| [LD.UMAX](ld_umax.md) | [AMO](../groups/amo.md) | 32 | LD.UMAX atomically stores the width-sized unsigned maximum and publishes the prior memory value. |
| [LD.UMIN](ld_umin.md) | [AMO](../groups/amo.md) | 32 | LD.UMIN atomically stores the width-sized unsigned minimum and publishes the prior memory value. |
| [LD.XOR](ld_xor.md) | [AMO](../groups/amo.md) | 32 | LD.XOR atomically stores the width-sized bitwise XOR and publishes the prior memory value. |
| [LDI](ldi.md) | [LDA/BASE_IMM](../groups/lda_base_imm.md) | 32 | LDI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [LDI.U](ldi_u.md) | [LDA/UNSCALED](../groups/lda_unscaled.md) | 32 | LDI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 8-byte value. |
| [LH](lh.md) | [LDA/BASE_REG](../groups/lda_base_reg.md) | 32 | LH snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LH.PCR](lh_pcr.md) | [LDA](../groups/lda.md) | 32 | LH.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LHI](lhi.md) | [LDA/BASE_IMM](../groups/lda_base_imm.md) | 32 | LHI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LHI.U](lhi_u.md) | [LDA/UNSCALED](../groups/lda_unscaled.md) | 32 | LHI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LHU](lhu.md) | [LDA/BASE_REG](../groups/lda_base_reg.md) | 32 | LHU snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LHU.PCR](lhu_pcr.md) | [LDA](../groups/lda.md) | 32 | LHU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LHUI](lhui.md) | [LDA/BASE_IMM](../groups/lda_base_imm.md) | 32 | LHUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LHUI.U](lhui_u.md) | [LDA/UNSCALED](../groups/lda_unscaled.md) | 32 | LHUI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 2-byte value. |
| [LR.B](lr_b.md) | [AMO](../groups/amo.md) | 32 | LR.B loads one byte, establishes a 64-byte-line reservation, and publishes the prior value. |
| [LR.D](lr_d.md) | [AMO](../groups/amo.md) | 32 | LR.D loads one doubleword, establishes a 64-byte-line reservation, and publishes the prior value. |
| [LR.H](lr_h.md) | [AMO](../groups/amo.md) | 32 | LR.H loads one halfword, establishes a 64-byte-line reservation, and publishes the prior value. |
| [LR.W](lr_w.md) | [AMO](../groups/amo.md) | 32 | LR.W loads one word, establishes a 64-byte-line reservation, and publishes the prior value. |
| [LSRGET](lsrget.md) | [SYS](../groups/sys.md) | 32 | LSRGET reads one assigned word from the active block BARG view. |
| [LUI](lui.md) | [ALU](../groups/alu.md) | 32 | Load upper immediate. Materializes a 20-bit constant in the upper bits of the destination. |
| [LW](lw.md) | [LDA/BASE_REG](../groups/lda_base_reg.md) | 32 | LW snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LW.ADD](lw_add.md) | [AMO](../groups/amo.md) | 32 | LW.ADD atomically stores the modular 32-bit sum and publishes the prior memory value. |
| [LW.AND](lw_and.md) | [AMO](../groups/amo.md) | 32 | LW.AND atomically stores the width-sized bitwise AND and publishes the prior memory value. |
| [LW.OR](lw_or.md) | [AMO](../groups/amo.md) | 32 | LW.OR atomically stores the width-sized bitwise OR and publishes the prior memory value. |
| [LW.PCR](lw_pcr.md) | [LDA](../groups/lda.md) | 32 | LW.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LW.SMAX](lw_smax.md) | [AMO](../groups/amo.md) | 32 | LW.SMAX atomically stores the width-sized signed maximum and publishes the prior memory value. |
| [LW.SMIN](lw_smin.md) | [AMO](../groups/amo.md) | 32 | LW.SMIN atomically stores the width-sized signed minimum and publishes the prior memory value. |
| [LW.UMAX](lw_umax.md) | [AMO](../groups/amo.md) | 32 | LW.UMAX atomically stores the width-sized unsigned maximum and publishes the prior memory value. |
| [LW.UMIN](lw_umin.md) | [AMO](../groups/amo.md) | 32 | LW.UMIN atomically stores the width-sized unsigned minimum and publishes the prior memory value. |
| [LW.XOR](lw_xor.md) | [AMO](../groups/amo.md) | 32 | LW.XOR atomically stores the width-sized bitwise XOR and publishes the prior memory value. |
| [LWI](lwi.md) | [LDA/BASE_IMM](../groups/lda_base_imm.md) | 32 | LWI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LWI.U](lwi_u.md) | [LDA/UNSCALED](../groups/lda_unscaled.md) | 32 | LWI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LWU](lwu.md) | [LDA/BASE_REG](../groups/lda_base_reg.md) | 32 | LWU snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LWU.PCR](lwu_pcr.md) | [LDA](../groups/lda.md) | 32 | LWU.PCR snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LWUI](lwui.md) | [LDA/BASE_IMM](../groups/lda_base_imm.md) | 32 | LWUI snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |
| [LWUI.U](lwui_u.md) | [LDA/UNSCALED](../groups/lda_unscaled.md) | 32 | LWUI.U snapshots its scalar sources, forms its encoded address, and loads one aligned little-endian 4-byte value. |

### M

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [MADD](madd.md) | [ALU](../groups/alu.md) | 32 | Multiply-add: `Dest = SrcD + SrcL * SrcR`. |
| [MADDW](maddw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word multiply-add. |
| [MAX](max.md) | [ALU](../groups/alu.md) | 32 | Integer max (signed). |
| [MAXU](maxu.md) | [ALU](../groups/alu.md) | 32 | MAXU performs an unsigned full-XLEN comparison and publishes the complete bit pattern of the maximum operand. |
| [MCOPY](mcopy.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Copies a non-overlapping byte range in restartable forward memory steps. |
| [MIN](min.md) | [ALU](../groups/alu.md) | 32 | Integer min (signed). |
| [MINU](minu.md) | [ALU](../groups/alu.md) | 32 | MINU performs an unsigned full-XLEN comparison and publishes the complete bit pattern of the minimum operand. |
| [MSET](mset.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Fills zero through 63 bytes with the low byte of an absolute GPR after complete access preflight. |
| [MUL](mul.md) | [ALU](../groups/alu.md) | 32 | Integer multiply (lower product written to destination). |
| [MULU](mulu.md) | [ALU](../groups/alu.md) | 32 | Integer multiply (unsigned). |
| [MULUW](muluw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word integer multiply (unsigned). |
| [MULW](mulw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word integer multiply. |

### O

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [OR](or.md) | [ALU](../groups/alu.md) | 32 | Bitwise OR of two registers. |
| [ORI](ori.md) | [ALU](../groups/alu.md) | 32 | Bitwise OR with an immediate. |
| [ORIW](oriw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word OR-immediate. |
| [ORW](orw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word bitwise OR. |

### P

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [PRF](prf.md) | [LDA/BASE_REG](../groups/lda_base_reg.md) | 32 | PRF snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint with no destination effect. |
| [PRFI.U](prfi_u.md) | [LDA/UNSCALED](../groups/lda_unscaled.md) | 32 | PRFI.U snapshots its scalar sources, forms its encoded address, and issues a non-binding 1-byte-granularity prefetch hint with no destination effect. |

### R

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [REM](rem.md) | [ALU](../groups/alu.md) | 32 | Signed integer remainder. |
| [REMU](remu.md) | [ALU](../groups/alu.md) | 32 | Unsigned integer remainder. |
| [REMUW](remuw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word unsigned remainder. |
| [REMW](remw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word signed remainder. |
| [REV](rev.md) | [ALU](../groups/alu.md) | 32 | Bit-reversal operation. |

### S

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [SB](sb.md) | [STA/BASE_REG](../groups/sta_base_reg.md) | 32 | SB snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [SB.PCR](sb_pcr.md) | [STA](../groups/sta.md) | 32 | SB.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [SBI](sbi.md) | [STA/BASE_IMM](../groups/sta_base_imm.md) | 32 | SBI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 1-byte value. |
| [SC.B](sc_b.md) | [AMO](../groups/amo.md) | 32 | SC.B conditionally stores one byte when the local 64-byte-line reservation matches. |
| [SC.D](sc_d.md) | [AMO](../groups/amo.md) | 32 | SC.D conditionally stores one doubleword when the local 64-byte-line reservation matches. |
| [SC.H](sc_h.md) | [AMO](../groups/amo.md) | 32 | SC.H conditionally stores one halfword when the local 64-byte-line reservation matches. |
| [SC.W](sc_w.md) | [AMO](../groups/amo.md) | 32 | SC.W conditionally stores one word when the local 64-byte-line reservation matches. |
| [SCVTF](scvtf.md) | [FSU](../groups/fsu.md) | 32 | SCVTF converts a signed 64-bit or sign-extended signed 32-bit source to floating carrier code 0 through 14 through the active numeric profile. |
| [SD](sd.md) | [STA/BASE_REG](../groups/sta_base_reg.md) | 32 | SD snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [SD.ADD](sd_add.md) | [AMO](../groups/amo.md) | 32 | SD.ADD atomically replaces the aligned 64-bit memory value with its modular sum with SrcR; it does not publish the old value. |
| [SD.AND](sd_and.md) | [AMO](../groups/amo.md) | 32 | SD.AND atomically replaces the aligned 64-bit memory value with its bitwise AND with SrcR; it does not publish the old value. |
| [SD.OR](sd_or.md) | [AMO](../groups/amo.md) | 32 | SD.OR atomically replaces the aligned 64-bit memory value with its bitwise OR with SrcR; it does not publish the old value. |
| [SD.PCR](sd_pcr.md) | [STA](../groups/sta.md) | 32 | SD.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [SD.SMAX](sd_smax.md) | [AMO](../groups/amo.md) | 32 | SD.SMAX atomically replaces the aligned 64-bit memory value with its signed maximum with SrcR; it does not publish the old value. |
| [SD.SMIN](sd_smin.md) | [AMO](../groups/amo.md) | 32 | SD.SMIN atomically replaces the aligned 64-bit memory value with its signed minimum with SrcR; it does not publish the old value. |
| [SD.U](sd_u.md) | [STA/BASE_REG](../groups/sta_base_reg.md) | 32 | SD.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [SD.UMAX](sd_umax.md) | [AMO](../groups/amo.md) | 32 | SD.UMAX atomically replaces the aligned 64-bit memory value with its unsigned maximum with SrcR; it does not publish the old value. |
| [SD.UMIN](sd_umin.md) | [AMO](../groups/amo.md) | 32 | SD.UMIN atomically replaces the aligned 64-bit memory value with its unsigned minimum with SrcR; it does not publish the old value. |
| [SD.XOR](sd_xor.md) | [AMO](../groups/amo.md) | 32 | SD.XOR atomically replaces the aligned 64-bit memory value with its bitwise XOR with SrcR; it does not publish the old value. |
| [SDI](sdi.md) | [STA/BASE_IMM](../groups/sta_base_imm.md) | 32 | SDI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [SDI.U](sdi_u.md) | [STA/BASE_IMM](../groups/sta_base_imm.md) | 32 | SDI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 8-byte value. |
| [SETC.AND](setc_and.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.ANDI](setc_andi.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.EQ](setc_eq.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.EQI](setc_eqi.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.GE](setc_ge.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.GEI](setc_gei.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.GEU](setc_geu.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.GEUI](setc_geui.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.LT](setc_lt.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.LTI](setc_lti.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.LTU](setc_ltu.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.LTUI](setc_ltui.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.NE](setc_ne.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.NEI](setc_nei.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.OR](setc_or.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.ORI](setc_ori.md) | [BRU](../groups/bru.md) | 32 | Sets the block-commit condition. |
| [SETC.TGT](setc_tgt.md) | [SYS](../groups/sys.md) | 32 | Sets the block-commit condition. |
| [SETRET](setret.md) | [BRU](../groups/bru.md) | 32 | Materializes a return address (ra) using a PC-relative offset. Used in call headers. |
| [SH](sh.md) | [STA/BASE_REG](../groups/sta_base_reg.md) | 32 | SH snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [SH.PCR](sh_pcr.md) | [STA](../groups/sta.md) | 32 | SH.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [SH.U](sh_u.md) | [STA/BASE_REG](../groups/sta_base_reg.md) | 32 | SH.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [SHI](shi.md) | [STA/BASE_IMM](../groups/sta_base_imm.md) | 32 | SHI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [SHI.U](shi_u.md) | [STA/BASE_IMM](../groups/sta_base_imm.md) | 32 | SHI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 2-byte value. |
| [SLL](sll.md) | [ALU](../groups/alu.md) | 32 | Logical left shift by the value in SrcR. |
| [SLLI](slli.md) | [ALU](../groups/alu.md) | 32 | Logical left shift by an immediate amount. |
| [SLLIW](slliw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word logical left shift (immediate). |
| [SLLW](sllw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word logical left shift. |
| [SRA](sra.md) | [ALU](../groups/alu.md) | 32 | Arithmetic right shift by the value in SrcR. |
| [SRAI](srai.md) | [ALU](../groups/alu.md) | 32 | Arithmetic right shift by an immediate amount. |
| [SRAIW](sraiw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word arithmetic right shift (immediate). |
| [SRAW](sraw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word arithmetic right shift. |
| [SRL](srl.md) | [ALU](../groups/alu.md) | 32 | Logical right shift by the value in SrcR. |
| [SRLI](srli.md) | [ALU](../groups/alu.md) | 32 | Logical right shift by an immediate amount. |
| [SRLIW](srliw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word logical right shift (immediate). |
| [SRLW](srlw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word logical right shift. |
| [SSRGET](ssrget.md) | [SYS](../groups/sys.md) | 32 | SSRGET reads the complete encoded system-register address. |
| [SSRSET](ssrset.md) | [SYS](../groups/sys.md) | 32 | SSRSET writes the complete encoded system-register address. |
| [SSRSWAP](ssrswap.md) | [SYS](../groups/sys.md) | 32 | SSRSWAP atomically swaps the complete encoded system-register address. |
| [SUB](sub.md) | [ALU](../groups/alu.md) | 32 | Integer subtraction. |
| [SUBI](subi.md) | [ALU](../groups/alu.md) | 32 | SUBI subtracts the zero-extended unsigned 12-bit immediate from the snapshotted XLEN source modulo 2^PTO_XLEN and publishes the result through RegDst. |
| [SUBIW](subiw.md) | [ALU](../groups/alu.md) | 32 | SUBIW subtracts the zero-extended unsigned 12-bit immediate from SrcL[31:0] modulo 2^32, sign-extends the word result to XLEN, and publishes it through RegDst. |
| [SUBW](subw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word integer subtraction. |
| [SW](sw.md) | [STA/BASE_REG](../groups/sta_base_reg.md) | 32 | SW snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [SW.ADD](sw_add.md) | [AMO](../groups/amo.md) | 32 | SW.ADD atomically replaces the aligned 32-bit memory value with its modular sum with SrcR; it does not publish the old value. |
| [SW.AND](sw_and.md) | [AMO](../groups/amo.md) | 32 | SW.AND atomically replaces the aligned 32-bit memory value with its bitwise AND with SrcR; it does not publish the old value. |
| [SW.OR](sw_or.md) | [AMO](../groups/amo.md) | 32 | SW.OR atomically replaces the aligned 32-bit memory value with its bitwise OR with SrcR; it does not publish the old value. |
| [SW.PCR](sw_pcr.md) | [STA](../groups/sta.md) | 32 | SW.PCR snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [SW.SMAX](sw_smax.md) | [AMO](../groups/amo.md) | 32 | SW.SMAX atomically replaces the aligned 32-bit memory value with its signed maximum with SrcR; it does not publish the old value. |
| [SW.SMIN](sw_smin.md) | [AMO](../groups/amo.md) | 32 | SW.SMIN atomically replaces the aligned 32-bit memory value with its signed minimum with SrcR; it does not publish the old value. |
| [SW.U](sw_u.md) | [STA/BASE_REG](../groups/sta_base_reg.md) | 32 | SW.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [SW.UMAX](sw_umax.md) | [AMO](../groups/amo.md) | 32 | SW.UMAX atomically replaces the aligned 32-bit memory value with its unsigned maximum with SrcR; it does not publish the old value. |
| [SW.UMIN](sw_umin.md) | [AMO](../groups/amo.md) | 32 | SW.UMIN atomically replaces the aligned 32-bit memory value with its unsigned minimum with SrcR; it does not publish the old value. |
| [SW.XOR](sw_xor.md) | [AMO](../groups/amo.md) | 32 | SW.XOR atomically replaces the aligned 32-bit memory value with its bitwise XOR with SrcR; it does not publish the old value. |
| [SWAPB](swapb.md) | [AMO](../groups/amo.md) | 32 | SWAPB atomically replaces one byte and publishes the prior value. |
| [SWAPD](swapd.md) | [AMO](../groups/amo.md) | 32 | SWAPD atomically replaces one doubleword and publishes the prior value. |
| [SWAPH](swaph.md) | [AMO](../groups/amo.md) | 32 | SWAPH atomically replaces one halfword and publishes the prior value. |
| [SWAPW](swapw.md) | [AMO](../groups/amo.md) | 32 | SWAPW atomically replaces one word and publishes the prior value. |
| [SWI](swi.md) | [STA/BASE_IMM](../groups/sta_base_imm.md) | 32 | SWI snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |
| [SWI.U](swi_u.md) | [STA/BASE_IMM](../groups/sta_base_imm.md) | 32 | SWI.U snapshots its scalar sources, forms its encoded address, and stores one aligned little-endian 4-byte value. |

### T

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [TLB.IA](tlb_ia.md) | [SYS](../groups/sys.md) | 32 | TLB.IA completes the 16-bit ASID token in bits 15:0 maintenance operation synchronously. |
| [TLB.IALL](tlb_iall.md) | [SYS](../groups/sys.md) | 32 | TLB.IALL completes the all translation entries maintenance operation synchronously. |
| [TLB.IAV](tlb_iav.md) | [SYS](../groups/sys.md) | 32 | TLB.IAV completes the canonical 48-bit virtual address with ASID scope maintenance operation synchronously. |
| [TLB.IV](tlb_iv.md) | [SYS](../groups/sys.md) | 32 | TLB.IV completes the canonical 48-bit virtual address maintenance operation synchronously. |

### U

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [UCVTF](ucvtf.md) | [FSU](../groups/fsu.md) | 32 | UCVTF converts an unsigned 64-bit or zero-extended unsigned 32-bit source to floating carrier code 0 through 14 through the active numeric profile. |

### V

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [V.ADD](v_add.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Integer addition. |
| [V.ADDI](v_addi.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.AND](v_and.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Bitwise AND. |
| [V.ANDI](v_andi.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.BCNT](v_bcnt.md) | [Bit Manipulation](../groups/bit_manipulation.md) | 64 | [64-bit V.] Population count. |
| [V.BIC](v_bic.md) | [Bit Manipulation](../groups/bit_manipulation.md) | 64 | [64-bit V.] Bit clear. |
| [V.BIS](v_bis.md) | [Bit Manipulation](../groups/bit_manipulation.md) | 64 | [64-bit V.] Bit set. |
| [V.BXS](v_bxs.md) | [Bit Manipulation](../groups/bit_manipulation.md) | 64 | [64-bit V.] Bit-field extract signed. |
| [V.BXU](v_bxu.md) | [Bit Manipulation](../groups/bit_manipulation.md) | 64 | [64-bit V.] Bit-field extract unsigned. |
| [V.CLZ](v_clz.md) | [Bit Manipulation](../groups/bit_manipulation.md) | 64 | [64-bit V.] Count leading zeros. |
| [V.CMP.AND](v_cmp_and.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.ANDI](v_cmp_andi.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.EQ](v_cmp_eq.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.EQI](v_cmp_eqi.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.GE](v_cmp_ge.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.GEI](v_cmp_gei.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.GEU](v_cmp_geu.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.GEUI](v_cmp_geui.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.LT](v_cmp_lt.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.LTI](v_cmp_lti.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.LTU](v_cmp_ltu.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.LTUI](v_cmp_ltui.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.NE](v_cmp_ne.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.NEI](v_cmp_nei.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.OR](v_cmp_or.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CMP.ORI](v_cmp_ori.md) | [Compare Instruction](../groups/compare_instruction.md) | 64 | [64-bit V.] Instruction from the Compare Instruction group. |
| [V.CSEL](v_csel.md) | [Three Source Integer](../groups/three_source_integer.md) | 64 | [64-bit V.] Conditional select. |
| [V.CTZ](v_ctz.md) | [Bit Manipulation](../groups/bit_manipulation.md) | 64 | [64-bit V.] Count trailing zeros. |
| [V.DIV](v_div.md) | [Division](../groups/division.md) | 64 | [64-bit V.] Signed integer division. |
| [V.FABS](v_fabs.md) | [Floating Point Arithmetic](../groups/floating_point_arithmetic.md) | 64 | [64-bit V.] Instruction from the Floating Point Arithmetic group. |
| [V.FADD](v_fadd.md) | [Three-Source Floating Point](../groups/three_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Three-Source Floating Point group. |
| [V.FCLASS](v_fclass.md) | [Floating Point Arithmetic](../groups/floating_point_arithmetic.md) | 64 | [64-bit V.] Instruction from the Floating Point Arithmetic group. |
| [V.FCVT](v_fcvt.md) | [Format Convert](../groups/format_convert.md) | 64 | [64-bit V.] Instruction from the Format Convert group. |
| [V.FCVTI](v_fcvti.md) | [Format Convert](../groups/format_convert.md) | 64 | [64-bit V.] Instruction from the Format Convert group. |
| [V.FDIV](v_fdiv.md) | [Three-Source Floating Point](../groups/three_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Three-Source Floating Point group. |
| [V.FEQ](v_feq.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.FEQS](v_feqs.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.FEXP](v_fexp.md) | [Floating Point Arithmetic](../groups/floating_point_arithmetic.md) | 64 | [64-bit V.] Instruction from the Floating Point Arithmetic group. |
| [V.FGE](v_fge.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.FGES](v_fges.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.FLT](v_flt.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.FLTS](v_flts.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.FMADD](v_fmadd.md) | [Three-Source Floating Point](../groups/three_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Three-Source Floating Point group. |
| [V.FMAX](v_fmax.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.FMIN](v_fmin.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.FMSUB](v_fmsub.md) | [Three-Source Floating Point](../groups/three_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Three-Source Floating Point group. |
| [V.FMUL](v_fmul.md) | [Three-Source Floating Point](../groups/three_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Three-Source Floating Point group. |
| [V.FNE](v_fne.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.FNES](v_fnes.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.FNMADD](v_fnmadd.md) | [Three-Source Floating Point](../groups/three_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Three-Source Floating Point group. |
| [V.FNMSUB](v_fnmsub.md) | [Three-Source Floating Point](../groups/three_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Three-Source Floating Point group. |
| [V.FRECIP](v_frecip.md) | [Floating Point Arithmetic](../groups/floating_point_arithmetic.md) | 64 | [64-bit V.] Instruction from the Floating Point Arithmetic group. |
| [V.FSQRT](v_fsqrt.md) | [Floating Point Arithmetic](../groups/floating_point_arithmetic.md) | 64 | [64-bit V.] Instruction from the Floating Point Arithmetic group. |
| [V.FSUB](v_fsub.md) | [Three-Source Floating Point](../groups/three_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Three-Source Floating Point group. |
| [V.ICVT](v_icvt.md) | [Format Convert](../groups/format_convert.md) | 64 | [64-bit V.] Instruction from the Format Convert group. |
| [V.ICVTF](v_icvtf.md) | [Format Convert](../groups/format_convert.md) | 64 | [64-bit V.] Instruction from the Format Convert group. |
| [V.LB](v_lb.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a signed 8-bit value from memory. |
| [V.LB.BRG](v_lb_brg.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LBI](v_lbi.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LBI.BRG](v_lbi_brg.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LBU](v_lbu.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a 8-bit value from memory. |
| [V.LBU.BRG](v_lbu_brg.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LBUI](v_lbui.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LBUI.BRG](v_lbui_brg.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LD](v_ld.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a 64-bit value from memory. |
| [V.LD.ADD](v_ld_add.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LD.AND](v_ld_and.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LD.BRG](v_ld_brg.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LD.MAX](v_ld_max.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LD.MIN](v_ld_min.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LD.OR](v_ld_or.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LD.XOR](v_ld_xor.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LDI](v_ldi.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LDI.BRG](v_ldi_brg.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LDI.U](v_ldi_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LDI.U.BRG](v_ldi_u_brg.md) | [Load UnScaled](../groups/load_unscaled.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LH](v_lh.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a signed 16-bit value from memory. |
| [V.LH.BRG](v_lh_brg.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LHI](v_lhi.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LHI.BRG](v_lhi_brg.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LHI.U](v_lhi_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LHI.U.BRG](v_lhi_u_brg.md) | [Load UnScaled](../groups/load_unscaled.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LHU](v_lhu.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a 16-bit value from memory. |
| [V.LHU.BRG](v_lhu_brg.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LHUI](v_lhui.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LHUI.BRG](v_lhui_brg.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LHUI.U](v_lhui_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LHUI.U.BRG](v_lhui_u_brg.md) | [Load UnScaled](../groups/load_unscaled.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LW](v_lw.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a signed 32-bit value from memory. |
| [V.LW.ADD](v_lw_add.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.AND](v_lw_and.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.BRG](v_lw_brg.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LW.MAX](v_lw_max.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.MIN](v_lw_min.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.OR](v_lw_or.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LW.XOR](v_lw_xor.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.LWI](v_lwi.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LWI.BRG](v_lwi_brg.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LWI.U](v_lwi_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LWI.U.BRG](v_lwi_u_brg.md) | [Load UnScaled](../groups/load_unscaled.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LWU](v_lwu.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a 32-bit value from memory. |
| [V.LWU.BRG](v_lwu_brg.md) | [Load Register Offset](../groups/load_register_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LWUI](v_lwui.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LWUI.BRG](v_lwui_brg.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LWUI.U](v_lwui_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.LWUI.U.BRG](v_lwui_u_brg.md) | [Load UnScaled](../groups/load_unscaled.md) | 64 | [64-bit V.] Loads a value from memory into a register. |
| [V.MADD](v_madd.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 64 | [64-bit V.] Instruction from the Multi-Cycle ALU group. |
| [V.MAX](v_max.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.MIN](v_min.md) | [Two-Source Floating Point](../groups/two_source_floating_point.md) | 64 | [64-bit V.] Instruction from the Two-Source Floating Point group. |
| [V.MUL](v_mul.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 64 | [64-bit V.] Integer multiply. |
| [V.OR](v_or.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Bitwise OR. |
| [V.ORI](v_ori.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.PSEL](v_psel.md) | [Three Source Integer](../groups/three_source_integer.md) | 64 | [64-bit V.] Instruction from the Three Source Integer group. |
| [V.QPOP](v_qpop.md) | [General Manager](../groups/general_manager.md) | 64 | [64-bit V.] Instruction from the General Manager group. |
| [V.QPUSH](v_qpush.md) | [General Manager](../groups/general_manager.md) | 64 | [64-bit V.] Instruction from the General Manager group. |
| [V.RDADD](v_rdadd.md) | [Reduce Operation with Register](../groups/reduce_operation_with_register.md) | 64 | [64-bit V.] Instruction from the Reduce Operation with Register group. |
| [V.RDAND](v_rdand.md) | [Reduce Operation with Register](../groups/reduce_operation_with_register.md) | 64 | [64-bit V.] Instruction from the Reduce Operation with Register group. |
| [V.RDFADD](v_rdfadd.md) | [Reduce Operation with Register](../groups/reduce_operation_with_register.md) | 64 | [64-bit V.] Instruction from the Reduce Operation with Register group. |
| [V.RDFMAX](v_rdfmax.md) | [Reduce Operation with Register](../groups/reduce_operation_with_register.md) | 64 | [64-bit V.] Instruction from the Reduce Operation with Register group. |
| [V.RDFMIN](v_rdfmin.md) | [Reduce Operation with Register](../groups/reduce_operation_with_register.md) | 64 | [64-bit V.] Instruction from the Reduce Operation with Register group. |
| [V.RDMAX](v_rdmax.md) | [Reduce Operation with Register](../groups/reduce_operation_with_register.md) | 64 | [64-bit V.] Instruction from the Reduce Operation with Register group. |
| [V.RDMIN](v_rdmin.md) | [Reduce Operation with Register](../groups/reduce_operation_with_register.md) | 64 | [64-bit V.] Instruction from the Reduce Operation with Register group. |
| [V.RDOR](v_rdor.md) | [Reduce Operation with Register](../groups/reduce_operation_with_register.md) | 64 | [64-bit V.] Instruction from the Reduce Operation with Register group. |
| [V.RDXOR](v_rdxor.md) | [Reduce Operation with Register](../groups/reduce_operation_with_register.md) | 64 | [64-bit V.] Instruction from the Reduce Operation with Register group. |
| [V.REM](v_rem.md) | [Division](../groups/division.md) | 64 | [64-bit V.] Signed integer remainder. |
| [V.REV](v_rev.md) | [Bit Manipulation](../groups/bit_manipulation.md) | 64 | [64-bit V.] Bit-reversal. |
| [V.SB](v_sb.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SB.BRG](v_sb_brg.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SBI](v_sbi.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SBI.BRG](v_sbi_brg.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SD](v_sd.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SD.ADD](v_sd_add.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.AND](v_sd_and.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.BRG](v_sd_brg.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SD.MAX](v_sd_max.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.MIN](v_sd_min.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.OR](v_sd_or.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SD.U](v_sd_u.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SD.U.BRG](v_sd_u_brg.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SD.XOR](v_sd_xor.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SDI](v_sdi.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SDI.BRG](v_sdi_brg.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SDI.U](v_sdi_u.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SDI.U.BRG](v_sdi_u_brg.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SH](v_sh.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SH.BRG](v_sh_brg.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SH.U](v_sh_u.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SH.U.BRG](v_sh_u_brg.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SHFL.BFLY](v_shfl_bfly.md) | [Shuffle](../groups/shuffle.md) | 64 | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFL.DOWN](v_shfl_down.md) | [Shuffle](../groups/shuffle.md) | 64 | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFL.IDX](v_shfl_idx.md) | [Shuffle](../groups/shuffle.md) | 64 | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFL.UP](v_shfl_up.md) | [Shuffle](../groups/shuffle.md) | 64 | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFLI.BFLY](v_shfli_bfly.md) | [Shuffle](../groups/shuffle.md) | 64 | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFLI.DOWN](v_shfli_down.md) | [Shuffle](../groups/shuffle.md) | 64 | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFLI.IDX](v_shfli_idx.md) | [Shuffle](../groups/shuffle.md) | 64 | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHFLI.UP](v_shfli_up.md) | [Shuffle](../groups/shuffle.md) | 64 | [64-bit V.] Instruction from the Shuffle group. |
| [V.SHI](v_shi.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SHI.BRG](v_shi_brg.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SHI.U](v_shi_u.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SHI.U.BRG](v_shi_u_brg.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SLL](v_sll.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Logical left shift. |
| [V.SLLI](v_slli.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.SRA](v_sra.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Arithmetic right shift. |
| [V.SRAI](v_srai.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.SRL](v_srl.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Logical right shift. |
| [V.SRLI](v_srli.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.SUB](v_sub.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Integer subtraction. |
| [V.SUBI](v_subi.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Instruction from the Arithmetic Operation group. |
| [V.SW](v_sw.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SW.ADD](v_sw_add.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.AND](v_sw_and.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.BRG](v_sw_brg.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SW.MAX](v_sw_max.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.MIN](v_sw_min.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.OR](v_sw_or.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SW.U](v_sw_u.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SW.U.BRG](v_sw_u_brg.md) | [Store Register Offset](../groups/store_register_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SW.XOR](v_sw_xor.md) | [Atomic Operation](../groups/atomic_operation.md) | 64 | [64-bit V.] Atomic memory read-modify-write operation. |
| [V.SWI](v_swi.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SWI.BRG](v_swi_brg.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SWI.U](v_swi_u.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.SWI.U.BRG](v_swi_u_brg.md) | [Store Offset](../groups/store_offset.md) | 64 | [64-bit V.] Stores a register value to memory. |
| [V.XOR](v_xor.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Bitwise XOR. |
| [V.XORI](v_xori.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 64 | [64-bit V.] Instruction from the Arithmetic Operation group. |

### X

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [XB](xb.md) | [Bundle Split](../groups/bundle_split.md) | 32 | Inventories an extension-owned cross-block transfer encoding that PTO rejects before field interpretation or architectural effects. |
| [XOR](xor.md) | [ALU](../groups/alu.md) | 32 | Bitwise XOR of two registers. |
| [XORI](xori.md) | [ALU](../groups/alu.md) | 32 | Bitwise XOR with an immediate. |
| [XORIW](xoriw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word XOR-immediate. |
| [XORW](xorw.md) | [ALU](../groups/alu.md) | 32 | 32-bit word bitwise XOR. |
