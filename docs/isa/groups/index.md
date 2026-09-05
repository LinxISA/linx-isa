# Instruction Groups

Alphabetical list of all 55 instruction groups in the LinxISA v0.58.6 catalog.
See the [chapter index](index.md) for the manual organization.

| Group | Forms | Chapter | Sample mnemonics |
|-------|-------|---------|------------------|
| [SYS](sys.md) | 35 | **Ch 19** — [source](index.md) | `ACRC`, `ACRE`, `ASSERT`, `BC.IALL`, `BC.IVA`, `BSE`, `BWE`, `BWI` +27 |
| [ALU](alu.md) | 107 | **Ch 12** — [source](index.md) | `ADD`, `ADDI`, `ADDIW`, `ADDW`, `AND`, `ANDI`, `ANDIW`, `ANDW` +99 |
| [BRU](bru.md) | 58 | **Ch 16** — [source](index.md) | `ADDTPC`, `C.CMP.EQI`, `C.CMP.NEI`, `C.SETC.EQ`, `C.SETC.NE`, `CMP.AND`, `CMP.ANDI`, `CMP.EQ` +50 |
| [Bundle Range Modifier](bundle_range_modifier.md) | 2 | **Ch 4** — [source](index.md) | `B.ASSEMBLE`, `B.SUBVIEW` |
| [Bundle Control Attribute](bundle_control_attribute.md) | 1 | **Ch 17** — [source](index.md) | `B.CATR` |
| [Bundle Data Attribute](bundle_data_attribute.md) | 1 | **Ch 17** — [source](index.md) | `B.DATR` |
| [Bundle Argument](bundle_argument.md) | 3 | **Ch 4** — [source](index.md) | `B.DIM` |
| [Bundle Fixed-Point PostProcess Attribute](bundle_fixed_point_postprocess_attribute.md) | 1 | **Ch 17** — [source](index.md) | `B.FPATR` |
| [Bundle Hint](bundle_hint.md) | 2 | **Ch 17** — [source](index.md) | `B.HINT` |
| [Bundle Input & Output](bundle_input_output.md) | 7 | **Ch 4** — [source](index.md) | `B.IOR`, `B.IOS`, `B.IOT` |
| [Bundle Offset](bundle_offset.md) | 1 | **Ch 4** — [source](index.md) | `B.TEXT` |
| [Bundle Split](bundle_split.md) | 71 | **Ch 4** — [source](index.md) | `BSTART`, `BSTART.FP`, `BSTART.GMOV`, `BSTART.MGATHER`, `BSTART.MGATHER.ADD`, `BSTART.MGATHER.AND`, `BSTART.MGATHER.CAS`, `BSTART.MGATHER.DEC` +53 |
| [BSTART](bstart.md) | 21 | **Ch 4** — [source](index.md) | `BSTART.CALL`, `BSTART.ICALL`, `HL.BSTART CALL`, `HL.BSTART.FP`, `HL.BSTART.STD`, `HL.BSTART.SYS`, `L.BSTART.FP`, `L.BSTART.STD` +1 |
| [Block Split](block_split.md) | 2 | **Ch 4** — [source](index.md) | `BSTART.VPAR`, `BSTART.VSEQ` |
| [Bundle Dimension](bundle_dimension.md) | 1 | **Ch 4** — [source](index.md) | `C.B.DIMI` |
| [C.BSTART](c_bstart.md) | 7 | **Ch 15** — [source](index.md) | `C.BSTART.FP`, `C.BSTART.MPAR`, `C.BSTART.MSEQ`, `C.BSTART.STD`, `C.BSTART.SYS`, `C.BSTART.VPAR`, `C.BSTART.VSEQ` |
| [LDA/BASE_IMM](lda_base_imm.md) | 9 | **Ch 11** — [source](index.md) | `C.LDI`, `C.LWI`, `LBI`, `LBUI`, `LDI`, `LHI`, `LHUI`, `LWI` +1 |
| [STA/BASE_IMM](sta_base_imm.md) | 9 | **Ch 11** — [source](index.md) | `C.SDI`, `C.SWI`, `SBI`, `SDI`, `SDI.U`, `SHI`, `SHI.U`, `SWI` +1 |
| [AMO](amo.md) | 53 | **Ch 14** — [source](index.md) | `CASB`, `CASD`, `CASH`, `CASW`, `DMA`, `HL.CASB`, `HL.CASD`, `HL.CASH` +45 |
| [FSU](fsu.md) | 30 | **Ch 13** — [source](index.md) | `FABS`, `FADD`, `FCVT`, `FCVTA`, `FCVTM`, `FCVTN`, `FCVTP`, `FCVTZ` +22 |
| [LDA/PC_REL](lda_pc_rel.md) | 7 | **Ch 11** — [source](index.md) | `HL.LB.PCR`, `HL.LBU.PCR`, `HL.LD.PCR`, `HL.LH.PCR`, `HL.LHU.PCR`, `HL.LW.PCR`, `HL.LWU.PCR` |
| [LDA/POST_INDEX](lda_post_index.md) | 19 | **Ch 11** — [source](index.md) | `HL.LB.PO`, `HL.LBI.PO`, `HL.LBU.PO`, `HL.LBUI.PO`, `HL.LD.PO`, `HL.LDI.PO`, `HL.LDI.UPO`, `HL.LH.PO` +11 |
| [LDA/PRE_INDEX](lda_pre_index.md) | 19 | **Ch 11** — [source](index.md) | `HL.LB.PR`, `HL.LBI.PR`, `HL.LBU.PR`, `HL.LBUI.PR`, `HL.LD.PR`, `HL.LDI.PR`, `HL.LDI.UPR`, `HL.LH.PR` +11 |
| [LDA/LONG](lda_long.md) | 12 | **Ch 11** — [source](index.md) | `HL.LBI`, `HL.LBUI`, `HL.LDI`, `HL.LDI.U`, `HL.LHI`, `HL.LHI.U`, `HL.LHUI`, `HL.LHUI.U` +4 |
| [LDA/PAIR](lda_pair.md) | 19 | **Ch 11** — [source](index.md) | `HL.LBIP`, `HL.LBP`, `HL.LBUIP`, `HL.LBUP`, `HL.LDIP`, `HL.LDIP.U`, `HL.LDP`, `HL.LHIP` +11 |
| [LDA](lda.md) | 11 | **Ch 11** — [source](index.md) | `HL.PRF`, `HL.PRF.A`, `HL.PRFI.U`, `HL.PRFI.UA`, `LB.PCR`, `LBU.PCR`, `LD.PCR`, `LH.PCR` +3 |
| [General](general.md) | 3 | **Ch 4** — [source](index.md) | `HL.QMT`, `HL.QPOP`, `HL.QPUSH` |
| [STA/PC_REL](sta_pc_rel.md) | 4 | **Ch 11** — [source](index.md) | `HL.SB.PCR`, `HL.SD.PCR`, `HL.SH.PCR`, `HL.SW.PCR` |
| [STA/POST_INDEX](sta_post_index.md) | 14 | **Ch 11** — [source](index.md) | `HL.SB.PO`, `HL.SBI.PO`, `HL.SD.PO`, `HL.SD.UPO`, `HL.SDI.PO`, `HL.SDI.UPO`, `HL.SH.PO`, `HL.SH.UPO` +6 |
| [STA/PRE_INDEX](sta_pre_index.md) | 14 | **Ch 11** — [source](index.md) | `HL.SB.PR`, `HL.SBI.PR`, `HL.SD.PR`, `HL.SD.UPR`, `HL.SDI.PR`, `HL.SDI.UPR`, `HL.SH.PR`, `HL.SH.UPR` +6 |
| [STA/LONG](sta_long.md) | 7 | **Ch 11** — [source](index.md) | `HL.SBI`, `HL.SDI`, `HL.SDI.U`, `HL.SHI`, `HL.SHI.U`, `HL.SWI`, `HL.SWI.U` |
| [STA/PAIR](sta_pair.md) | 14 | **Ch 11** — [source](index.md) | `HL.SBIP`, `HL.SBP`, `HL.SDIP`, `HL.SDIP.U`, `HL.SDP`, `HL.SDP.U`, `HL.SHIP`, `HL.SHIP.U` +6 |
| [LDA/BASE_REG](lda_base_reg.md) | 8 | **Ch 11** — [source](index.md) | `LB`, `LBU`, `LD`, `LH`, `LHU`, `LW`, `LWU`, `PRF` |
| [LDA/UNSCALED](lda_unscaled.md) | 6 | **Ch 11** — [source](index.md) | `LDI.U`, `LHI.U`, `LHUI.U`, `LWI.U`, `LWUI.U`, `PRFI.U` |
| [STA/BASE_REG](sta_base_reg.md) | 7 | **Ch 11** — [source](index.md) | `SB`, `SD`, `SD.U`, `SH`, `SH.U`, `SW`, `SW.U` |
| [STA](sta.md) | 4 | **Ch 11** — [source](index.md) | `SB.PCR`, `SD.PCR`, `SH.PCR`, `SW.PCR` |
| [Arithmetic Operation](arithmetic_operation.md) | 16 | **Ch 12** — [source](index.md) | `V.ADD`, `V.ADDI`, `V.AND`, `V.ANDI`, `V.OR`, `V.ORI`, `V.SLL`, `V.SLLI` +8 |
| [Bit Manipulation](bit_manipulation.md) | 8 | **Ch 12** — [source](index.md) | `V.BCNT`, `V.BIC`, `V.BIS`, `V.BXS`, `V.BXU`, `V.CLZ`, `V.CTZ`, `V.REV` |
| [Compare Instruction](compare_instruction.md) | 16 | **Ch 16** — [source](index.md) | `V.CMP.AND`, `V.CMP.ANDI`, `V.CMP.EQ`, `V.CMP.EQI`, `V.CMP.GE`, `V.CMP.GEI`, `V.CMP.GEU`, `V.CMP.GEUI` +8 |
| [Three Source Integer](three_source_integer.md) | 2 | **Ch 20** — [source](index.md) | `V.CSEL`, `V.PSEL` |
| [Division](division.md) | 2 | **Ch 20** — [source](index.md) | `V.DIV`, `V.REM` |
| [Floating Point Arithmetic](floating_point_arithmetic.md) | 5 | **Ch 20** — [source](index.md) | `V.FABS`, `V.FCLASS`, `V.FEXP`, `V.FRECIP`, `V.FSQRT` |
| [Three-Source Floating Point](three_source_floating_point.md) | 8 | **Ch 20** — [source](index.md) | `V.FADD`, `V.FDIV`, `V.FMADD`, `V.FMSUB`, `V.FMUL`, `V.FNMADD`, `V.FNMSUB`, `V.FSUB` |
| [Format Convert](format_convert.md) | 4 | **Ch 13** — [source](index.md) | `V.FCVT`, `V.FCVTI`, `V.ICVT`, `V.ICVTF` |
| [Two-Source Floating Point](two_source_floating_point.md) | 12 | **Ch 20** — [source](index.md) | `V.FEQ`, `V.FEQS`, `V.FGE`, `V.FGES`, `V.FLT`, `V.FLTS`, `V.FMAX`, `V.FMIN` +4 |
| [Load Register Offset](load_register_offset.md) | 14 | **Ch 11** — [source](index.md) | `V.LB`, `V.LB.BRG`, `V.LBU`, `V.LBU.BRG`, `V.LD`, `V.LD.BRG`, `V.LH`, `V.LH.BRG` +6 |
| [Load Immediate Offset](load_immediate_offset.md) | 14 | **Ch 11** — [source](index.md) | `V.LBI`, `V.LBI.BRG`, `V.LBUI`, `V.LBUI.BRG`, `V.LDI`, `V.LDI.BRG`, `V.LHI`, `V.LHI.BRG` +6 |
| [Atomic Operation](atomic_operation.md) | 24 | **Ch 14** — [source](index.md) | `V.LD.ADD`, `V.LD.AND`, `V.LD.MAX`, `V.LD.MIN`, `V.LD.OR`, `V.LD.XOR`, `V.LW.ADD`, `V.LW.AND` +16 |
| [Load UnScaled](load_unscaled.md) | 10 | **Ch 11** — [source](index.md) | `V.LDI.U`, `V.LDI.U.BRG`, `V.LHI.U`, `V.LHI.U.BRG`, `V.LHUI.U`, `V.LHUI.U.BRG`, `V.LWI.U`, `V.LWI.U.BRG` +2 |
| [Multi-Cycle ALU](multi_cycle_alu.md) | 2 | **Ch 12** — [source](index.md) | `V.MADD`, `V.MUL` |
| [General Manager](general_manager.md) | 2 | **Ch 9** — [source](index.md) | `V.QPOP`, `V.QPUSH` |
| [Reduce Operation with Register](reduce_operation_with_register.md) | 9 | **Ch 20** — [source](index.md) | `V.RDADD`, `V.RDAND`, `V.RDFADD`, `V.RDFMAX`, `V.RDFMIN`, `V.RDMAX`, `V.RDMIN`, `V.RDOR` +1 |
| [Store Register Offset](store_register_offset.md) | 14 | **Ch 11** — [source](index.md) | `V.SB`, `V.SB.BRG`, `V.SD`, `V.SD.BRG`, `V.SD.U`, `V.SD.U.BRG`, `V.SH`, `V.SH.BRG` +6 |
| [Store Offset](store_offset.md) | 14 | **Ch 11** — [source](index.md) | `V.SBI`, `V.SBI.BRG`, `V.SDI`, `V.SDI.BRG`, `V.SDI.U`, `V.SDI.U.BRG`, `V.SHI`, `V.SHI.BRG` +6 |
| [Shuffle](shuffle.md) | 8 | **Ch 20** — [source](index.md) | `V.SHFL.BFLY`, `V.SHFL.DOWN`, `V.SHFL.IDX`, `V.SHFL.UP`, `V.SHFLI.BFLY`, `V.SHFLI.DOWN`, `V.SHFLI.IDX`, `V.SHFLI.UP` |
