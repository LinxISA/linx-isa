# All Instructions

Complete alphabetical index of all **740** instruction forms in the LinxISA v0.56 catalog.

Use **Ctrl+F** / **Cmd+F** to search, or click a letter below to jump to it.

[A](#a) | [B](#b) | [C](#c) | [D](#d) | [E](#e) | [F](#f) | [H](#h) | [I](#i) | [J](#j) | [L](#l) | [M](#m) | [O](#o) | [P](#p) | [R](#r) | [S](#s) | [T](#t) | [U](#u) | [V](#v) | [X](#x)

### A

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [ACRC](acrc.md) | [Execution Control](../groups/execution_control.md) | 32 | Architectural control (ring call). Calls an implementation-defined ACR. |
| [ACRE](acre.md) | [Execution Control](../groups/execution_control.md) | 32 | Architectural control (ring entry). Enters an implementation-defined ACR. |
| [ADD](add.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Integer addition. Writes the sum of two registers to the destination. |
| [ADDI](addi.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Integer add-immediate. Adds a sign-extended 12-bit immediate to a register. |
| [ADDIW](addiw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word add-immediate. |
| [ADDTPC](addtpc.md) | [PC-Relative](../groups/pc_relative.md) | 32 | PC-relative addition. Adds an immediate to the current PC/TPC and writes the result. |
| [ADDW](addw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word integer addition. |
| [AND](and.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Bitwise AND of two registers. |
| [ANDI](andi.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Bitwise AND with an immediate. |
| [ANDIW](andiw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word AND-immediate. |
| [ANDW](andw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word bitwise AND. |
| [ASSERT](assert.md) | [Execution Control](../groups/execution_control.md) | 32 | Architectural assertion. Traps if the condition register is zero. |

### B

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [B.ARG](b_arg.md) | [Block Argument](../groups/block_argument.md) | 32 | Instruction from the Block Argument group. |
| [B.ARG](b_arg.md) | [Block Argument](../groups/block_argument.md) | 32 | Instruction from the Block Argument group. |
| [B.ARG](b_arg.md) | [Block Argument](../groups/block_argument.md) | 32 | Instruction from the Block Argument group. |
| [B.ARG](b_arg.md) | [Block Argument](../groups/block_argument.md) | 32 | Instruction from the Block Argument group. |
| [B.ARG](b_arg.md) | [Block Argument](../groups/block_argument.md) | 32 | Instruction from the Block Argument group. |
| [B.ARG](b_arg.md) | [Block Argument](../groups/block_argument.md) | 32 | Instruction from the Block Argument group. |
| [B.CATR](b_catr.md) | [Block Control Attribute](../groups/block_control_attribute.md) | 32 | Instruction from the Block Control Attribute group. |
| [B.DATR](b_datr.md) | [Block Data Attribute](../groups/block_data_attribute.md) | 32 | Instruction from the Block Data Attribute group. |
| [B.DIM](b_dim.md) | [Block Argument](../groups/block_argument.md) | 32 | Instruction from the Block Argument group. |
| [B.DIM](b_dim.md) | [Block Argument](../groups/block_argument.md) | 32 | Instruction from the Block Argument group. |
| [B.DIM](b_dim.md) | [Block Argument](../groups/block_argument.md) | 32 | Instruction from the Block Argument group. |
| [B.EQ](b_eq.md) | [Branch](../groups/branch.md) | 32 | Conditional branch taken when SrcL equals SrcR. |
| [B.GE](b_ge.md) | [Branch](../groups/branch.md) | 32 | Conditional branch taken when SrcL is greater than or equal to SrcR (signed). |
| [B.GEU](b_geu.md) | [Branch](../groups/branch.md) | 32 | Conditional branch taken when SrcL is greater than or equal to SrcR (unsigned). |
| [B.HINT](b_hint.md) | [Block Hint](../groups/block_hint.md) | 32 | Instruction from the Block Hint group. |
| [B.HINT](b_hint.md) | [Block Hint](../groups/block_hint.md) | 32 | Instruction from the Block Hint group. |
| [B.IOD](b_iod.md) | [Block Input & Output](../groups/block_input_output.md) | 32 | Instruction from the Block Input & Output group. |
| [B.IOR](b_ior.md) | [Block Input & Output](../groups/block_input_output.md) | 32 | Instruction from the Block Input & Output group. |
| [B.IOT](b_iot.md) | [Block Input & Output](../groups/block_input_output.md) | 32 | Instruction from the Block Input & Output group. |
| [B.IOT](b_iot.md) | [Block Input & Output](../groups/block_input_output.md) | 32 | Instruction from the Block Input & Output group. |
| [B.IOT](b_iot.md) | [Block Input & Output](../groups/block_input_output.md) | 32 | Instruction from the Block Input & Output group. |
| [B.LT](b_lt.md) | [Branch](../groups/branch.md) | 32 | Conditional branch taken when SrcL is less than SrcR (signed). |
| [B.LTU](b_ltu.md) | [Branch](../groups/branch.md) | 32 | Conditional branch taken when SrcL is less than SrcR (unsigned). |
| [B.NE](b_ne.md) | [Branch](../groups/branch.md) | 32 | Conditional branch taken when SrcL not equal to SrcR. |
| [B.NZ](b_nz.md) | [Branch](../groups/branch.md) | 32 | Conditional PC-relative branch. |
| [B.TEXT](b_text.md) | [Block Offset](../groups/block_offset.md) | 32 | Instruction from the Block Offset group. |
| [B.Z](b_z.md) | [Branch](../groups/branch.md) | 32 | Conditional PC-relative branch. |
| [BC.IALL](bc_iall.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Branch-predictor cache invalidate all entries. |
| [BC.IVA](bc_iva.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Branch-predictor cache invalidate by address. |
| [BCNT](bcnt.md) | [Bit Operation](../groups/bit_operation.md) | 32 | Population count. Counts the number of set bits in a register. |
| [BIC](bic.md) | [Bit Operation](../groups/bit_operation.md) | 32 | Bit clear / AND-NOT. |
| [BIS](bis.md) | [Bit Operation](../groups/bit_operation.md) | 32 | Bit set / OR. |
| [BSE](bse.md) | [Execution Control](../groups/execution_control.md) | 32 | Execution control instruction. |
| [BSTART](bstart.md) | [Block Split](../groups/block_split.md) | 32 | Block split marker. Terminates the current basic block and begins the next. Encodes block type and transition kind. |
| [BSTART](bstart.md) | [Block Split](../groups/block_split.md) | 32 | Block split marker. Terminates the current basic block and begins the next. Encodes block type and transition kind. |
| [BSTART CALL](bstart_call.md) | [BSTART](../groups/bstart.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.ACCCVT](bstart_acccvt.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.CUBE](bstart_cube.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FIXP](bstart_fixp.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.FP](bstart_fp.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.MPAR](bstart_mpar.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.MSEQ](bstart_mseq.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.PAR](bstart_par.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.STD](bstart_std.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.SYS](bstart_sys.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TEPL](bstart_tepl.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TLOAD](bstart_tload.md) | [Block Split](../groups/block_split.md) | 32 | Loads a 64-bit value from memory. |
| [BSTART.TMA](bstart_tma.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TMATMUL](bstart_tmatmul.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TMATMUL.ACC](bstart_tmatmul_acc.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TMOV](bstart_tmov.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.TSTORE](bstart_tstore.md) | [Block Split](../groups/block_split.md) | 32 | Stores a register value to memory. |
| [BSTART.VPAR](bstart_vpar.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTART.VSEQ](bstart_vseq.md) | [Block Split](../groups/block_split.md) | 32 | Terminates the current block and begins the next. |
| [BSTOP](bstop.md) | [Block Split](../groups/block_split.md) | 32 | Block termination marker. Ends the current basic block. |
| [BWE](bwe.md) | [Execution Control](../groups/execution_control.md) | 32 | Execution control instruction. |
| [BWI](bwi.md) | [Execution Control](../groups/execution_control.md) | 32 | Execution control instruction. |
| [BWT](bwt.md) | [Execution Control](../groups/execution_control.md) | 32 | Execution control instruction. |
| [BXS](bxs.md) | [Bit Operation](../groups/bit_operation.md) | 32 | Bit-field extract signed. |
| [BXU](bxu.md) | [Bit Operation](../groups/bit_operation.md) | 32 | Bit-field extract unsigned. |

### C

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [C.ADD](c_add.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 16 | [16-bit C.] Integer addition. |
| [C.ADDI](c_addi.md) | [Arithmetic](../groups/arithmetic.md) | 16 | [16-bit C.] Instruction from the Arithmetic group. |
| [C.AND](c_and.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 16 | [16-bit C.] Bitwise AND. |
| [C.B.DIM](c_b_dim.md) | [Block Dimension](../groups/block_dimension.md) | 16 | [16-bit C.] Instruction from the Block Dimension group. |
| [C.B.DIMI](c_b_dimi.md) | [Block Dimension](../groups/block_dimension.md) | 16 | [16-bit C.] Instruction from the Block Dimension group. |
| [C.BSTART](c_bstart.md) | [Block Split](../groups/block_split.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART](c_bstart.md) | [Block Split](../groups/block_split.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.FP](c_bstart_fp.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.MPAR](c_bstart_mpar.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.MSEQ](c_bstart_mseq.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.STD](c_bstart_std.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.SYS](c_bstart_sys.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.VPAR](c_bstart_vpar.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTART.VSEQ](c_bstart_vseq.md) | [C.BSTART](../groups/c_bstart.md) | 16 | [16-bit C.] Terminates the current block and begins the next. |
| [C.BSTOP](c_bstop.md) | [Block Split](../groups/block_split.md) | 16 | [16-bit C.] Marks the end of the current block. |
| [C.CMP.EQI](c_cmp_eqi.md) | [C.TINST](../groups/c_tinst.md) | 16 | [16-bit C.] Instruction from the C.TINST group. |
| [C.CMP.NEI](c_cmp_nei.md) | [C.TINST](../groups/c_tinst.md) | 16 | [16-bit C.] Instruction from the C.TINST group. |
| [C.EBREAK](c_ebreak.md) | [C.TINST](../groups/c_tinst.md) | 16 | [16-bit C.] Instruction from the C.TINST group. |
| [C.LDI](c_ldi.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 16 | [16-bit C.] Loads a value from memory into a register. |
| [C.LWI](c_lwi.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 16 | [16-bit C.] Loads a value from memory into a register. |
| [C.MOVI](c_movi.md) | [Move](../groups/move.md) | 16 | [16-bit C.] Instruction from the Move group. |
| [C.MOVR](c_movr.md) | [Move](../groups/move.md) | 16 | [16-bit C.] Instruction from the Move group. |
| [C.OR](c_or.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 16 | [16-bit C.] Bitwise OR. |
| [C.SDI](c_sdi.md) | [Store Immediate Offset](../groups/store_immediate_offset.md) | 16 | [16-bit C.] Stores a register value to memory. |
| [C.SETC.EQ](c_setc_eq.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 16 | [16-bit C.] Sets the block-commit condition. |
| [C.SETC.NE](c_setc_ne.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 16 | [16-bit C.] Sets the block-commit condition. |
| [C.SETC.TGT](c_setc_tgt.md) | [C.UNARY](../groups/c_unary.md) | 16 | [16-bit C.] Sets the block-commit condition. |
| [C.SETRET](c_setret.md) | [Move](../groups/move.md) | 16 | [16-bit C.] Instruction from the Move group. |
| [C.SEXT.B](c_sext_b.md) | [C.UNARY](../groups/c_unary.md) | 16 | [16-bit C.] Instruction from the C.UNARY group. |
| [C.SEXT.H](c_sext_h.md) | [C.UNARY](../groups/c_unary.md) | 16 | [16-bit C.] Instruction from the C.UNARY group. |
| [C.SEXT.W](c_sext_w.md) | [C.UNARY](../groups/c_unary.md) | 16 | [16-bit C.] Instruction from the C.UNARY group. |
| [C.SLLI](c_slli.md) | [C.TINST](../groups/c_tinst.md) | 16 | [16-bit C.] Instruction from the C.TINST group. |
| [C.SRLI](c_srli.md) | [C.TINST](../groups/c_tinst.md) | 16 | [16-bit C.] Instruction from the C.TINST group. |
| [C.SSRGET](c_ssrget.md) | [C.TINST](../groups/c_tinst.md) | 16 | [16-bit C.] Instruction from the C.TINST group. |
| [C.SUB](c_sub.md) | [Arithmetic Operation](../groups/arithmetic_operation.md) | 16 | [16-bit C.] Integer subtraction. |
| [C.SWI](c_swi.md) | [Store Immediate Offset](../groups/store_immediate_offset.md) | 16 | [16-bit C.] Stores a register value to memory. |
| [C.ZEXT.B](c_zext_b.md) | [C.UNARY](../groups/c_unary.md) | 16 | [16-bit C.] Instruction from the C.UNARY group. |
| [C.ZEXT.H](c_zext_h.md) | [C.UNARY](../groups/c_unary.md) | 16 | [16-bit C.] Instruction from the C.UNARY group. |
| [C.ZEXT.W](c_zext_w.md) | [C.UNARY](../groups/c_unary.md) | 16 | [16-bit C.] Instruction from the C.UNARY group. |
| [CLZ](clz.md) | [Bit Operation](../groups/bit_operation.md) | 32 | Count leading zeros. |
| [CMP.AND](cmp_and.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Instruction from the Compare Instruction group. |
| [CMP.ANDI](cmp_andi.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Instruction from the Compare Instruction group. |
| [CMP.EQ](cmp_eq.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Compare equal. Sets destination to 1 if operands are equal. |
| [CMP.EQI](cmp_eqi.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Instruction from the Compare Instruction group. |
| [CMP.GE](cmp_ge.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Compare greater-or-equal (signed). |
| [CMP.GEI](cmp_gei.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Instruction from the Compare Instruction group. |
| [CMP.GEU](cmp_geu.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Compare greater-or-equal (unsigned). |
| [CMP.GEUI](cmp_geui.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Instruction from the Compare Instruction group. |
| [CMP.LT](cmp_lt.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Compare less-than (signed). |
| [CMP.LTI](cmp_lti.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Instruction from the Compare Instruction group. |
| [CMP.LTU](cmp_ltu.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Compare less-than (unsigned). |
| [CMP.LTUI](cmp_ltui.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Instruction from the Compare Instruction group. |
| [CMP.NE](cmp_ne.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Compare not-equal. |
| [CMP.NEI](cmp_nei.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Instruction from the Compare Instruction group. |
| [CMP.OR](cmp_or.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Instruction from the Compare Instruction group. |
| [CMP.ORI](cmp_ori.md) | [Compare Instruction](../groups/compare_instruction.md) | 32 | Instruction from the Compare Instruction group. |
| [CSEL](csel.md) | [Compound Operation](../groups/compound_operation.md) | 32 | Conditional select. `Dest = (SrcP != 0) ? SrcL : SrcR`. |
| [CTZ](ctz.md) | [Bit Operation](../groups/bit_operation.md) | 32 | Count trailing zeros. |

### D

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [DC.CISW](dc_cisw.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Data cache clean-and-invalidate by set/way. |
| [DC.CIVA](dc_civa.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |
| [DC.CSW](dc_csw.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |
| [DC.CVA](dc_cva.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |
| [DC.IALL](dc_iall.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |
| [DC.ISW](dc_isw.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Data cache invalidate by set/way. |
| [DC.IVA](dc_iva.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Data cache invalidate by address. |
| [DC.ZVA](dc_zva.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |
| [DIV](div.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | Signed integer division. |
| [DIVU](divu.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | Unsigned integer division. |
| [DIVUW](divuw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | 32-bit word unsigned integer division. |
| [DIVW](divw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | 32-bit word signed integer division. |

### E

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [EBREAK](ebreak.md) | [Execution Control](../groups/execution_control.md) | 32 | Environment break instruction. Traps to the debugging or OS handler. |
| [ERCOV](ercov.md) | [Block Split](../groups/block_split.md) | 32 | Instruction from the Block Split group. |
| [ESAVE](esave.md) | [Block Split](../groups/block_split.md) | 32 | Instruction from the Block Split group. |

### F

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [FABS](fabs.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Floating-point absolute value. |
| [FADD](fadd.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Floating-point addition. |
| [FCVT](fcvt.md) | [Format Convert](../groups/format_convert.md) | 32 | Floating-point format conversion. |
| [FCVTA](fcvta.md) | [Format Convert](../groups/format_convert.md) | 32 | Instruction from the Format Convert group. |
| [FCVTM](fcvtm.md) | [Format Convert](../groups/format_convert.md) | 32 | Instruction from the Format Convert group. |
| [FCVTN](fcvtn.md) | [Format Convert](../groups/format_convert.md) | 32 | Instruction from the Format Convert group. |
| [FCVTP](fcvtp.md) | [Format Convert](../groups/format_convert.md) | 32 | Instruction from the Format Convert group. |
| [FCVTZ](fcvtz.md) | [Format Convert](../groups/format_convert.md) | 32 | Instruction from the Format Convert group. |
| [FDIV](fdiv.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Floating-point division. |
| [FENCE.D](fence_d.md) | [Execution Control](../groups/execution_control.md) | 32 | Data memory ordering fence. |
| [FENCE.I](fence_i.md) | [Execution Control](../groups/execution_control.md) | 32 | Instruction-cache fence. Synchronizes instruction fetch with prior stores. |
| [FENTRY](fentry.md) | [Block Split](../groups/block_split.md) | 32 | Instruction from the Block Split group. |
| [FEQ](feq.md) | [Floating-point Compare](../groups/floating_point_compare.md) | 32 | Floating-point equality comparison. Writes 1 if ordered and equal. |
| [FEQS](feqs.md) | [Floating-point Compare](../groups/floating_point_compare.md) | 32 | Instruction from the Floating-point Compare group. |
| [FEXIT](fexit.md) | [Block Split](../groups/block_split.md) | 32 | Instruction from the Block Split group. |
| [FEXP](fexp.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Instruction from the Floating-point Arithmetic group. |
| [FGE](fge.md) | [Floating-point Compare](../groups/floating_point_compare.md) | 32 | Floating-point greater-or-equal comparison (ordered). |
| [FGES](fges.md) | [Floating-point Compare](../groups/floating_point_compare.md) | 32 | Instruction from the Floating-point Compare group. |
| [FLT](flt.md) | [Floating-point Compare](../groups/floating_point_compare.md) | 32 | Floating-point less-than comparison (ordered). |
| [FLTS](flts.md) | [Floating-point Compare](../groups/floating_point_compare.md) | 32 | Instruction from the Floating-point Compare group. |
| [FMADD](fmadd.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Instruction from the Floating-point Arithmetic group. |
| [FMAX](fmax.md) | [Max-Min](../groups/max_min.md) | 32 | Floating-point maximum. |
| [FMIN](fmin.md) | [Max-Min](../groups/max_min.md) | 32 | Floating-point minimum. |
| [FMSUB](fmsub.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Instruction from the Floating-point Arithmetic group. |
| [FMUL](fmul.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Floating-point multiplication. |
| [FNE](fne.md) | [Floating-point Compare](../groups/floating_point_compare.md) | 32 | Instruction from the Floating-point Compare group. |
| [FNES](fnes.md) | [Floating-point Compare](../groups/floating_point_compare.md) | 32 | Instruction from the Floating-point Compare group. |
| [FNMADD](fnmadd.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Instruction from the Floating-point Arithmetic group. |
| [FNMSUB](fnmsub.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Instruction from the Floating-point Arithmetic group. |
| [FRECIP](frecip.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Instruction from the Floating-point Arithmetic group. |
| [FRET.RA](fret_ra.md) | [Block Split](../groups/block_split.md) | 32 | Instruction from the Block Split group. |
| [FRET.STK](fret_stk.md) | [Block Split](../groups/block_split.md) | 32 | Instruction from the Block Split group. |
| [FSQRT](fsqrt.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Floating-point square root. |
| [FSUB](fsub.md) | [Floating-point Arithmetic](../groups/floating_point_arithmetic.md) | 32 | Floating-point subtraction. |

### H

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [HL.ADDI](hl_addi.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 48 | [48-bit HL.] Instruction from the Arithmetic Operation 64bit group. |
| [HL.ADDIW](hl_addiw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 48 | [48-bit HL.] Instruction from the Arithmetic Operation 32bit group. |
| [HL.ADDTPC](hl_addtpc.md) | [PC-Relative](../groups/pc_relative.md) | 48 | [48-bit HL.] Instruction from the PC-Relative group. |
| [HL.ANDI](hl_andi.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 48 | [48-bit HL.] Instruction from the Arithmetic Operation 64bit group. |
| [HL.ANDIW](hl_andiw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 48 | [48-bit HL.] Instruction from the Arithmetic Operation 32bit group. |
| [HL.BFI](hl_bfi.md) | [RESERVE](../groups/reserve.md) | 48 | [48-bit HL.] Bit-field insert. |
| [HL.BSTART CALL](hl_bstart_call.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.FP](hl_bstart_fp.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.FP](hl_bstart_fp.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.FP](hl_bstart_fp.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.FP](hl_bstart_fp.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](hl_bstart_std.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](hl_bstart_std.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](hl_bstart_std.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.STD](hl_bstart_std.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.BSTART.SYS](hl_bstart_sys.md) | [BSTART](../groups/bstart.md) | 48 | [48-bit HL.] Terminates the current block and begins the next. |
| [HL.CASB](hl_casb.md) | [Atomic](../groups/atomic.md) | 48 | [48-bit HL.] Atomic memory read-modify-write operation. |
| [HL.CASD](hl_casd.md) | [Atomic](../groups/atomic.md) | 48 | [48-bit HL.] Atomic memory read-modify-write operation. |
| [HL.CASH](hl_cash.md) | [Atomic](../groups/atomic.md) | 48 | [48-bit HL.] Atomic memory read-modify-write operation. |
| [HL.CASW](hl_casw.md) | [Atomic](../groups/atomic.md) | 48 | [48-bit HL.] Atomic memory read-modify-write operation. |
| [HL.CCAT](hl_ccat.md) | [Concat](../groups/concat.md) | 48 | [48-bit HL.] Instruction from the Concat group. |
| [HL.CCATW](hl_ccatw.md) | [Concat](../groups/concat.md) | 48 | [48-bit HL.] Instruction from the Concat group. |
| [HL.CMP.ANDI](hl_cmp_andi.md) | [Compare Instruction](../groups/compare_instruction.md) | 48 | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.EQI](hl_cmp_eqi.md) | [Compare Instruction](../groups/compare_instruction.md) | 48 | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.GEI](hl_cmp_gei.md) | [Compare Instruction](../groups/compare_instruction.md) | 48 | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.GEUI](hl_cmp_geui.md) | [Compare Instruction](../groups/compare_instruction.md) | 48 | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.LTI](hl_cmp_lti.md) | [Compare Instruction](../groups/compare_instruction.md) | 48 | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.LTUI](hl_cmp_ltui.md) | [Compare Instruction](../groups/compare_instruction.md) | 48 | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.NEI](hl_cmp_nei.md) | [Compare Instruction](../groups/compare_instruction.md) | 48 | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.CMP.ORI](hl_cmp_ori.md) | [Compare Instruction](../groups/compare_instruction.md) | 48 | [48-bit HL.] Instruction from the Compare Instruction group. |
| [HL.DIV](hl_div.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Signed integer division. |
| [HL.DIVU](hl_divu.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Unsigned integer division. |
| [HL.DIVUW](hl_divuw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.DIVW](hl_divw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.LB.PCR](hl_lb_pcr.md) | [Load PC-Relative](../groups/load_pc_relative.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LB.PO](hl_lb_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LB.PR](hl_lb_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBI](hl_lbi.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBI.PO](hl_lbi_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBI.PR](hl_lbi_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBIP](hl_lbip.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBP](hl_lbp.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBU.PCR](hl_lbu_pcr.md) | [Load PC-Relative](../groups/load_pc_relative.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBU.PO](hl_lbu_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBU.PR](hl_lbu_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBUI](hl_lbui.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBUI.PO](hl_lbui_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBUI.PR](hl_lbui_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBUIP](hl_lbuip.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LBUP](hl_lbup.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LD.PCR](hl_ld_pcr.md) | [Load PC-Relative](../groups/load_pc_relative.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LD.PO](hl_ld_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LD.PR](hl_ld_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDI](hl_ldi.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDI.PO](hl_ldi_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDI.PR](hl_ldi_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDI.U](hl_ldi_u.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDI.UPO](hl_ldi_upo.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDI.UPR](hl_ldi_upr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDIP](hl_ldip.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDIP.U](hl_ldip_u.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LDP](hl_ldp.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LH.PCR](hl_lh_pcr.md) | [Load PC-Relative](../groups/load_pc_relative.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LH.PO](hl_lh_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LH.PR](hl_lh_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHI](hl_lhi.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHI.PO](hl_lhi_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHI.PR](hl_lhi_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHI.U](hl_lhi_u.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHI.UPO](hl_lhi_upo.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHI.UPR](hl_lhi_upr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHIP](hl_lhip.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHIP.U](hl_lhip_u.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHP](hl_lhp.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHU.PCR](hl_lhu_pcr.md) | [Load PC-Relative](../groups/load_pc_relative.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHU.PO](hl_lhu_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHU.PR](hl_lhu_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUI](hl_lhui.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUI.PO](hl_lhui_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUI.PR](hl_lhui_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUI.U](hl_lhui_u.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUI.UPO](hl_lhui_upo.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUI.UPR](hl_lhui_upr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUIP](hl_lhuip.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUIP.U](hl_lhuip_u.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LHUP](hl_lhup.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LIS](hl_lis.md) | [Long Immediate](../groups/long_immediate.md) | 48 | [48-bit HL.] Instruction from the Long Immediate group. |
| [HL.LIU](hl_liu.md) | [Long Immediate](../groups/long_immediate.md) | 48 | [48-bit HL.] Instruction from the Long Immediate group. |
| [HL.LUI](hl_lui.md) | [Immediate](../groups/immediate.md) | 48 | [48-bit HL.] Instruction from the Immediate group. |
| [HL.LW.PCR](hl_lw_pcr.md) | [Load PC-Relative](../groups/load_pc_relative.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LW.PO](hl_lw_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LW.PR](hl_lw_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWI](hl_lwi.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWI.PO](hl_lwi_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWI.PR](hl_lwi_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWI.U](hl_lwi_u.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWI.UPO](hl_lwi_upo.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWI.UPR](hl_lwi_upr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWIP](hl_lwip.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWIP.U](hl_lwip_u.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWP](hl_lwp.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWU.PCR](hl_lwu_pcr.md) | [Load PC-Relative](../groups/load_pc_relative.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWU.PO](hl_lwu_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWU.PR](hl_lwu_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUI](hl_lwui.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUI.PO](hl_lwui_po.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUI.PR](hl_lwui_pr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUI.U](hl_lwui_u.md) | [Load Long Offset](../groups/load_long_offset.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUI.UPO](hl_lwui_upo.md) | [Load Post-Index](../groups/load_post_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUI.UPR](hl_lwui_upr.md) | [Load Pre-Index](../groups/load_pre_index.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUIP](hl_lwuip.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUIP.U](hl_lwuip_u.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.LWUP](hl_lwup.md) | [Load Pair](../groups/load_pair.md) | 48 | [48-bit HL.] Loads a value from memory into a register. |
| [HL.MADD](hl_madd.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.MADDW](hl_maddw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.MIADD](hl_miadd.md) | [RESERVE](../groups/reserve.md) | 48 | [48-bit HL.] Instruction from the RESERVE group. |
| [HL.MISUB](hl_misub.md) | [RESERVE](../groups/reserve.md) | 48 | [48-bit HL.] Instruction from the RESERVE group. |
| [HL.MUL](hl_mul.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Integer multiply. |
| [HL.MULU](hl_mulu.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.ORI](hl_ori.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 48 | [48-bit HL.] Instruction from the Arithmetic Operation 64bit group. |
| [HL.ORIW](hl_oriw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 48 | [48-bit HL.] Instruction from the Arithmetic Operation 32bit group. |
| [HL.PRF](hl_prf.md) | [Prefetch](../groups/prefetch.md) | 48 | [48-bit HL.] Instruction from the Prefetch group. |
| [HL.PRF.A](hl_prf_a.md) | [Prefetch](../groups/prefetch.md) | 48 | [48-bit HL.] Instruction from the Prefetch group. |
| [HL.PRFI.U](hl_prfi_u.md) | [Prefetch](../groups/prefetch.md) | 48 | [48-bit HL.] Instruction from the Prefetch group. |
| [HL.PRFI.UA](hl_prfi_ua.md) | [Prefetch](../groups/prefetch.md) | 48 | [48-bit HL.] Instruction from the Prefetch group. |
| [HL.QMT](hl_qmt.md) | [General](../groups/general.md) | 48 | [48-bit HL.] Instruction from the General group. |
| [HL.QPOP](hl_qpop.md) | [General](../groups/general.md) | 48 | [48-bit HL.] Instruction from the General group. |
| [HL.QPUSH](hl_qpush.md) | [General](../groups/general.md) | 48 | [48-bit HL.] Instruction from the General group. |
| [HL.REM](hl_rem.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Signed integer remainder. |
| [HL.REMU](hl_remu.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Unsigned integer remainder. |
| [HL.REMUW](hl_remuw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.REMW](hl_remw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 48 | [48-bit HL.] Instruction from the Multi-Cycle ALU group. |
| [HL.SB.PCR](hl_sb_pcr.md) | [Store PC-Relative](../groups/store_pc_relative.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SB.PO](hl_sb_po.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SB.PR](hl_sb_pr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SBI](hl_sbi.md) | [Store Long Offset](../groups/store_long_offset.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SBI.PO](hl_sbi_po.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SBI.PR](hl_sbi_pr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SBIP](hl_sbip.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SBP](hl_sbp.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SD.PCR](hl_sd_pcr.md) | [Store PC-Relative](../groups/store_pc_relative.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SD.PO](hl_sd_po.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SD.PR](hl_sd_pr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SD.UPO](hl_sd_upo.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SD.UPR](hl_sd_upr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SDI](hl_sdi.md) | [Store Long Offset](../groups/store_long_offset.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SDI.PO](hl_sdi_po.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SDI.PR](hl_sdi_pr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SDI.U](hl_sdi_u.md) | [Store Long Offset](../groups/store_long_offset.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SDI.UPO](hl_sdi_upo.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SDI.UPR](hl_sdi_upr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SDIP](hl_sdip.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SDIP.U](hl_sdip_u.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SDP](hl_sdp.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SDP.U](hl_sdp_u.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SETC.ANDI](hl_setc_andi.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.EQI](hl_setc_eqi.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.GEI](hl_setc_gei.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.GEUI](hl_setc_geui.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.LTI](hl_setc_lti.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.LTUI](hl_setc_ltui.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.NEI](hl_setc_nei.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETC.ORI](hl_setc_ori.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 48 | [48-bit HL.] Sets the block-commit condition. |
| [HL.SETRET](hl_setret.md) | [PC-Relative](../groups/pc_relative.md) | 48 | [48-bit HL.] Instruction from the PC-Relative group. |
| [HL.SH.PCR](hl_sh_pcr.md) | [Store PC-Relative](../groups/store_pc_relative.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SH.PO](hl_sh_po.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SH.PR](hl_sh_pr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SH.UPO](hl_sh_upo.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SH.UPR](hl_sh_upr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SHI](hl_shi.md) | [Store Long Offset](../groups/store_long_offset.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SHI.PO](hl_shi_po.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SHI.PR](hl_shi_pr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SHI.U](hl_shi_u.md) | [Store Long Offset](../groups/store_long_offset.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SHI.UPO](hl_shi_upo.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SHI.UPR](hl_shi_upr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SHIP](hl_ship.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SHIP.U](hl_ship_u.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SHP](hl_shp.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SHP.U](hl_shp_u.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SSRGET](hl_ssrget.md) | [SSR Access](../groups/ssr_access.md) | 48 | [48-bit HL.] Instruction from the SSR Access group. |
| [HL.SSRSET](hl_ssrset.md) | [SSR Access](../groups/ssr_access.md) | 48 | [48-bit HL.] Instruction from the SSR Access group. |
| [HL.SUBI](hl_subi.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 48 | [48-bit HL.] Instruction from the Arithmetic Operation 64bit group. |
| [HL.SUBIW](hl_subiw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 48 | [48-bit HL.] Instruction from the Arithmetic Operation 32bit group. |
| [HL.SW.PCR](hl_sw_pcr.md) | [Store PC-Relative](../groups/store_pc_relative.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SW.PO](hl_sw_po.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SW.PR](hl_sw_pr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SW.UPO](hl_sw_upo.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SW.UPR](hl_sw_upr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SWI](hl_swi.md) | [Store Long Offset](../groups/store_long_offset.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SWI.PO](hl_swi_po.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SWI.PR](hl_swi_pr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SWI.U](hl_swi_u.md) | [Store Long Offset](../groups/store_long_offset.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SWI.UPO](hl_swi_upo.md) | [Store Post-Index](../groups/store_post_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SWI.UPR](hl_swi_upr.md) | [Store Pre-Index](../groups/store_pre_index.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SWIP](hl_swip.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SWIP.U](hl_swip_u.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SWP](hl_swp.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.SWP.U](hl_swp_u.md) | [Store Pair](../groups/store_pair.md) | 48 | [48-bit HL.] Stores a register value to memory. |
| [HL.XORI](hl_xori.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 48 | [48-bit HL.] Instruction from the Arithmetic Operation 64bit group. |
| [HL.XORIW](hl_xoriw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 48 | [48-bit HL.] Instruction from the Arithmetic Operation 32bit group. |

### I

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [IC.IALL](ic_iall.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |
| [IC.IVA](ic_iva.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |

### J

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [J](j.md) | [Branch](../groups/branch.md) | 32 | Unconditional PC-relative jump to a target label. |
| [JR](jr.md) | [Branch](../groups/branch.md) | 32 | Jump register: PC-relative or register-based jump to the address in a register. |

### L

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [LB](lb.md) | [Load Register Offset](../groups/load_register_offset.md) | 32 | Loads a signed 8-bit value from memory. |
| [LB.PCR](lb_pcr.md) | [Load Symbol](../groups/load_symbol.md) | 32 | Loads a value from memory into a register. |
| [LBI](lbi.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 32 | Loads a value from memory into a register. |
| [LBU](lbu.md) | [Load Register Offset](../groups/load_register_offset.md) | 32 | Loads a 8-bit value from memory. |
| [LBU.PCR](lbu_pcr.md) | [Load Symbol](../groups/load_symbol.md) | 32 | Loads a value from memory into a register. |
| [LBUI](lbui.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 32 | Loads a value from memory into a register. |
| [LD](ld.md) | [Load Register Offset](../groups/load_register_offset.md) | 32 | Loads a 64-bit value from memory. |
| [LD.ADD](ld_add.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LD.AND](ld_and.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LD.OR](ld_or.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LD.PCR](ld_pcr.md) | [Load Symbol](../groups/load_symbol.md) | 32 | Loads a value from memory into a register. |
| [LD.SMAX](ld_smax.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LD.SMIN](ld_smin.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LD.UMAX](ld_umax.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LD.UMIN](ld_umin.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LD.XOR](ld_xor.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LDI](ldi.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 32 | Loads a value from memory into a register. |
| [LDI.U](ldi_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 32 | Loads a value from memory into a register. |
| [LH](lh.md) | [Load Register Offset](../groups/load_register_offset.md) | 32 | Loads a signed 16-bit value from memory. |
| [LH.PCR](lh_pcr.md) | [Load Symbol](../groups/load_symbol.md) | 32 | Loads a value from memory into a register. |
| [LHI](lhi.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 32 | Loads a value from memory into a register. |
| [LHI.U](lhi_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 32 | Loads a value from memory into a register. |
| [LHU](lhu.md) | [Load Register Offset](../groups/load_register_offset.md) | 32 | Loads a 16-bit value from memory. |
| [LHU.PCR](lhu_pcr.md) | [Load Symbol](../groups/load_symbol.md) | 32 | Loads a value from memory into a register. |
| [LHUI](lhui.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 32 | Loads a value from memory into a register. |
| [LHUI.U](lhui_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 32 | Loads a value from memory into a register. |
| [LR.B](lr_b.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LR.D](lr_d.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LR.H](lr_h.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LR.W](lr_w.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LSRGET](lsrget.md) | [SSR Access](../groups/ssr_access.md) | 32 | Instruction from the SSR Access group. |
| [LUI](lui.md) | [Immediate](../groups/immediate.md) | 32 | Load upper immediate. Materializes a 20-bit constant in the upper bits of the destination. |
| [LW](lw.md) | [Load Register Offset](../groups/load_register_offset.md) | 32 | Loads a signed 32-bit value from memory. |
| [LW.ADD](lw_add.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LW.AND](lw_and.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LW.OR](lw_or.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LW.PCR](lw_pcr.md) | [Load Symbol](../groups/load_symbol.md) | 32 | Loads a value from memory into a register. |
| [LW.SMAX](lw_smax.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LW.SMIN](lw_smin.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LW.UMAX](lw_umax.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LW.UMIN](lw_umin.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LW.XOR](lw_xor.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [LWI](lwi.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 32 | Loads a value from memory into a register. |
| [LWI.U](lwi_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 32 | Loads a value from memory into a register. |
| [LWU](lwu.md) | [Load Register Offset](../groups/load_register_offset.md) | 32 | Loads a 32-bit value from memory. |
| [LWU.PCR](lwu_pcr.md) | [Load Symbol](../groups/load_symbol.md) | 32 | Loads a value from memory into a register. |
| [LWUI](lwui.md) | [Load Immediate Offset](../groups/load_immediate_offset.md) | 32 | Loads a value from memory into a register. |
| [LWUI.U](lwui_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 32 | Loads a value from memory into a register. |

### M

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [MADD](madd.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | Multiply-add: `Dest = SrcD + SrcL * SrcR`. |
| [MADDW](maddw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | 32-bit word multiply-add. |
| [MAX](max.md) | [Max-Min](../groups/max_min.md) | 32 | Integer max (signed). |
| [MAXU](maxu.md) | [Max-Min](../groups/max_min.md) | 32 | Instruction from the Max-Min group. |
| [MCOPY](mcopy.md) | [Block Split](../groups/block_split.md) | 32 | Instruction from the Block Split group. |
| [MIN](min.md) | [Max-Min](../groups/max_min.md) | 32 | Integer min (signed). |
| [MINU](minu.md) | [Max-Min](../groups/max_min.md) | 32 | Instruction from the Max-Min group. |
| [MSET](mset.md) | [Block Split](../groups/block_split.md) | 32 | Instruction from the Block Split group. |
| [MUL](mul.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | Integer multiply (lower product written to destination). |
| [MULU](mulu.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | Integer multiply (unsigned). |
| [MULUW](muluw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | 32-bit word integer multiply (unsigned). |
| [MULW](mulw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | 32-bit word integer multiply. |

### O

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [OR](or.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Bitwise OR of two registers. |
| [ORI](ori.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Bitwise OR with an immediate. |
| [ORIW](oriw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word OR-immediate. |
| [ORW](orw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word bitwise OR. |

### P

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [PRF](prf.md) | [Load Register Offset](../groups/load_register_offset.md) | 32 | Loads a value from memory into a register. |
| [PRFI.U](prfi_u.md) | [Load UnScaled](../groups/load_unscaled.md) | 32 | Loads a value from memory into a register. |

### R

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [REM](rem.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | Signed integer remainder. |
| [REMU](remu.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | Unsigned integer remainder. |
| [REMUW](remuw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | 32-bit word unsigned remainder. |
| [REMW](remw.md) | [Multi-Cycle ALU](../groups/multi_cycle_alu.md) | 32 | 32-bit word signed remainder. |
| [REV](rev.md) | [Bit Operation](../groups/bit_operation.md) | 32 | Bit-reversal operation. |

### S

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [SB](sb.md) | [Store Register Offset](../groups/store_register_offset.md) | 32 | Stores a register value to memory. |
| [SB.PCR](sb_pcr.md) | [Store Symbol](../groups/store_symbol.md) | 32 | Stores a register value to memory. |
| [SBI](sbi.md) | [Store Immediate Offset](../groups/store_immediate_offset.md) | 32 | Stores a register value to memory. |
| [SC.B](sc_b.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SC.D](sc_d.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SC.H](sc_h.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SC.W](sc_w.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SCVTF](scvtf.md) | [Format Convert](../groups/format_convert.md) | 32 | Instruction from the Format Convert group. |
| [SD](sd.md) | [Store Register Offset](../groups/store_register_offset.md) | 32 | Stores a register value to memory. |
| [SD.ADD](sd_add.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SD.AND](sd_and.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SD.OR](sd_or.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SD.PCR](sd_pcr.md) | [Store Symbol](../groups/store_symbol.md) | 32 | Stores a register value to memory. |
| [SD.SMAX](sd_smax.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SD.SMIN](sd_smin.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SD.U](sd_u.md) | [Store Register Offset](../groups/store_register_offset.md) | 32 | Stores a register value to memory. |
| [SD.UMAX](sd_umax.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SD.UMIN](sd_umin.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SD.XOR](sd_xor.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SDI](sdi.md) | [Store Immediate Offset](../groups/store_immediate_offset.md) | 32 | Stores a register value to memory. |
| [SDI.U](sdi_u.md) | [Store Immediate Offset](../groups/store_immediate_offset.md) | 32 | Stores a register value to memory. |
| [SETC.AND](setc_and.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.ANDI](setc_andi.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.EQ](setc_eq.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.EQI](setc_eqi.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.GE](setc_ge.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.GEI](setc_gei.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.GEU](setc_geu.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.GEUI](setc_geui.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.LT](setc_lt.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.LTI](setc_lti.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.LTU](setc_ltu.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.LTUI](setc_ltui.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.NE](setc_ne.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.NEI](setc_nei.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.OR](setc_or.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.ORI](setc_ori.md) | [Set Commit Argument](../groups/set_commit_argument.md) | 32 | Sets the block-commit condition. |
| [SETC.TGT](setc_tgt.md) | [SSR Access](../groups/ssr_access.md) | 32 | Sets the block-commit condition. |
| [SETRET](setret.md) | [PC-Relative](../groups/pc_relative.md) | 32 | Materializes a return address (ra) using a PC-relative offset. Used in call headers. |
| [SH](sh.md) | [Store Register Offset](../groups/store_register_offset.md) | 32 | Stores a register value to memory. |
| [SH.PCR](sh_pcr.md) | [Store Symbol](../groups/store_symbol.md) | 32 | Stores a register value to memory. |
| [SH.U](sh_u.md) | [Store Register Offset](../groups/store_register_offset.md) | 32 | Stores a register value to memory. |
| [SHI](shi.md) | [Store Immediate Offset](../groups/store_immediate_offset.md) | 32 | Stores a register value to memory. |
| [SHI.U](shi_u.md) | [Store Immediate Offset](../groups/store_immediate_offset.md) | 32 | Stores a register value to memory. |
| [SLL](sll.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Logical left shift by the value in SrcR. |
| [SLLI](slli.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Logical left shift by an immediate amount. |
| [SLLIW](slliw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word logical left shift (immediate). |
| [SLLW](sllw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word logical left shift. |
| [SRA](sra.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Arithmetic right shift by the value in SrcR. |
| [SRAI](srai.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Arithmetic right shift by an immediate amount. |
| [SRAIW](sraiw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word arithmetic right shift (immediate). |
| [SRAW](sraw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word arithmetic right shift. |
| [SRL](srl.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Logical right shift by the value in SrcR. |
| [SRLI](srli.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Logical right shift by an immediate amount. |
| [SRLIW](srliw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word logical right shift (immediate). |
| [SRLW](srlw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word logical right shift. |
| [SSRGET](ssrget.md) | [SSR Access](../groups/ssr_access.md) | 32 | Instruction from the SSR Access group. |
| [SSRSET](ssrset.md) | [SSR Access](../groups/ssr_access.md) | 32 | Instruction from the SSR Access group. |
| [SSRSWAP](ssrswap.md) | [SSR Access](../groups/ssr_access.md) | 32 | Instruction from the SSR Access group. |
| [SUB](sub.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Integer subtraction. |
| [SUBI](subi.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Instruction from the Arithmetic Operation 64bit group. |
| [SUBIW](subiw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | Instruction from the Arithmetic Operation 32bit group. |
| [SUBW](subw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word integer subtraction. |
| [SW](sw.md) | [Store Register Offset](../groups/store_register_offset.md) | 32 | Stores a register value to memory. |
| [SW.ADD](sw_add.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SW.AND](sw_and.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SW.OR](sw_or.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SW.PCR](sw_pcr.md) | [Store Symbol](../groups/store_symbol.md) | 32 | Stores a register value to memory. |
| [SW.SMAX](sw_smax.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SW.SMIN](sw_smin.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SW.U](sw_u.md) | [Store Register Offset](../groups/store_register_offset.md) | 32 | Stores a register value to memory. |
| [SW.UMAX](sw_umax.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SW.UMIN](sw_umin.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SW.XOR](sw_xor.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SWAPB](swapb.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SWAPD](swapd.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SWAPH](swaph.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SWAPW](swapw.md) | [Atomic Operation](../groups/atomic_operation.md) | 32 | Atomic memory read-modify-write operation. |
| [SWI](swi.md) | [Store Immediate Offset](../groups/store_immediate_offset.md) | 32 | Stores a register value to memory. |
| [SWI.U](swi_u.md) | [Store Immediate Offset](../groups/store_immediate_offset.md) | 32 | Stores a register value to memory. |

### T

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [TLB.IA](tlb_ia.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |
| [TLB.IALL](tlb_iall.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |
| [TLB.IAV](tlb_iav.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |
| [TLB.IV](tlb_iv.md) | [Cache Maintain](../groups/cache_maintain.md) | 32 | Cache maintenance operation. |

### U

| Mnemonic | Group | Bits | Description |
|----------|-------|------|-------------|
| [UCVTF](ucvtf.md) | [Format Convert](../groups/format_convert.md) | 32 | Instruction from the Format Convert group. |

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
| [XB](xb.md) | [Block Split](../groups/block_split.md) | 32 | Instruction from the Block Split group. |
| [XOR](xor.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Bitwise XOR of two registers. |
| [XORI](xori.md) | [Arithmetic Operation 64bit](../groups/arithmetic_operation_64bit.md) | 32 | Bitwise XOR with an immediate. |
| [XORIW](xoriw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word XOR-immediate. |
| [XORW](xorw.md) | [Arithmetic Operation 32bit](../groups/arithmetic_operation_32bit.md) | 32 | 32-bit word bitwise XOR. |
