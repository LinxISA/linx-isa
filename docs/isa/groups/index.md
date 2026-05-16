# Instruction Groups

Alphabetical list of all 66 instruction groups in the LinxISA v0.56 catalog.
See the [chapter index](index.md) for the manual organization.

| Group | Forms | Chapter | Sample mnemonics |
|-------|-------|---------|------------------|
| [Execution Control](execution_control.md) | 10 | **Ch 19** — [source](index.md) | `ACRC`, `ACRE`, `ASSERT`, `BSE`, `BWE`, `BWI`, `BWT`, `EBREAK` +2 |
| [Arithmetic Operation 64bit](arithmetic_operation_64bit.md) | 21 | **Ch 12** — [source](index.md) | `ADD`, `ADDI`, `AND`, `ANDI`, `HL.ADDI`, `HL.ANDI`, `HL.ORI`, `HL.SUBI` +13 |
| [Arithmetic Operation 32bit](arithmetic_operation_32bit.md) | 21 | **Ch 12** — [source](index.md) | `ADDIW`, `ADDW`, `ANDIW`, `ANDW`, `HL.ADDIW`, `HL.ANDIW`, `HL.ORIW`, `HL.SUBIW` +13 |
| [PC-Relative](pc_relative.md) | 4 | **Ch 16** — [source](index.md) | `ADDTPC`, `HL.ADDTPC`, `HL.SETRET`, `SETRET` |
| [Block Argument](block_argument.md) | 9 | **Ch 4** — [source](index.md) | `B.ARG`, `B.DIM` |
| [Block Control Attribute](block_control_attribute.md) | 1 | **Ch 17** — [source](index.md) | `B.CATR` |
| [Block Data Attribute](block_data_attribute.md) | 1 | **Ch 17** — [source](index.md) | `B.DATR` |
| [Branch](branch.md) | 10 | **Ch 16** — [source](index.md) | `B.EQ`, `B.GE`, `B.GEU`, `B.LT`, `B.LTU`, `B.NE`, `B.NZ`, `B.Z` +2 |
| [Block Hint](block_hint.md) | 2 | **Ch 17** — [source](index.md) | `B.HINT` |
| [Block Input & Output](block_input_output.md) | 5 | **Ch 4** — [source](index.md) | `B.IOD`, `B.IOR`, `B.IOT` |
| [Block Offset](block_offset.md) | 1 | **Ch 4** — [source](index.md) | `B.TEXT` |
| [Cache Maintain](cache_maintain.md) | 16 | **Ch 19** — [source](index.md) | `BC.IALL`, `BC.IVA`, `DC.CISW`, `DC.CIVA`, `DC.CSW`, `DC.CVA`, `DC.IALL`, `DC.ISW` +8 |
| [Bit Operation](bit_operation.md) | 8 | **Ch 12** — [source](index.md) | `BCNT`, `BIC`, `BIS`, `BXS`, `BXU`, `CLZ`, `CTZ`, `REV` |
| [Block Split](block_split.md) | 45 | **Ch 4** — [source](index.md) | `BSTART`, `BSTART.ACCCVT`, `BSTART.CUBE`, `BSTART.FIXP`, `BSTART.FP`, `BSTART.MPAR`, `BSTART.MSEQ`, `BSTART.PAR` +23 |
| [BSTART](bstart.md) | 11 | **Ch 4** — [source](index.md) | `BSTART CALL`, `HL.BSTART CALL`, `HL.BSTART.FP`, `HL.BSTART.STD`, `HL.BSTART.SYS` |
| [Arithmetic Operation](arithmetic_operation.md) | 20 | **Ch 12** — [source](index.md) | `C.ADD`, `C.AND`, `C.OR`, `C.SUB`, `V.ADD`, `V.ADDI`, `V.AND`, `V.ANDI` +12 |
| [Arithmetic](arithmetic.md) | 1 | **Ch 12** — [source](index.md) | `C.ADDI` |
| [Block Dimension](block_dimension.md) | 2 | **Ch 4** — [source](index.md) | `C.B.DIM`, `C.B.DIMI` |
| [C.BSTART](c_bstart.md) | 7 | **Ch 15** — [source](index.md) | `C.BSTART.FP`, `C.BSTART.MPAR`, `C.BSTART.MSEQ`, `C.BSTART.STD`, `C.BSTART.SYS`, `C.BSTART.VPAR`, `C.BSTART.VSEQ` |
| [C.TINST](c_tinst.md) | 6 | **Ch 19** — [source](index.md) | `C.CMP.EQI`, `C.CMP.NEI`, `C.EBREAK`, `C.SLLI`, `C.SRLI`, `C.SSRGET` |
| [Load Immediate Offset](load_immediate_offset.md) | 23 | **Ch 11** — [source](index.md) | `C.LDI`, `C.LWI`, `LBI`, `LBUI`, `LDI`, `LHI`, `LHUI`, `LWI` +15 |
| [Move](move.md) | 3 | **Ch 12** — [source](index.md) | `C.MOVI`, `C.MOVR`, `C.SETRET` |
| [Store Immediate Offset](store_immediate_offset.md) | 9 | **Ch 11** — [source](index.md) | `C.SDI`, `C.SWI`, `SBI`, `SDI`, `SDI.U`, `SHI`, `SHI.U`, `SWI` +1 |
| [Set Commit Argument](set_commit_argument.md) | 26 | **Ch 16** — [source](index.md) | `C.SETC.EQ`, `C.SETC.NE`, `HL.SETC.ANDI`, `HL.SETC.EQI`, `HL.SETC.GEI`, `HL.SETC.GEUI`, `HL.SETC.LTI`, `HL.SETC.LTUI` +18 |
| [C.UNARY](c_unary.md) | 7 | **Ch 12** — [source](index.md) | `C.SETC.TGT`, `C.SEXT.B`, `C.SEXT.H`, `C.SEXT.W`, `C.ZEXT.B`, `C.ZEXT.H`, `C.ZEXT.W` |
| [Compare Instruction](compare_instruction.md) | 40 | **Ch 16** — [source](index.md) | `CMP.AND`, `CMP.ANDI`, `CMP.EQ`, `CMP.EQI`, `CMP.GE`, `CMP.GEI`, `CMP.GEU`, `CMP.GEUI` +32 |
| [Compound Operation](compound_operation.md) | 1 | **Ch 12** — [source](index.md) | `CSEL` |
| [Multi-Cycle ALU](multi_cycle_alu.md) | 28 | **Ch 12** — [source](index.md) | `DIV`, `DIVU`, `DIVUW`, `DIVW`, `HL.DIV`, `HL.DIVU`, `HL.DIVUW`, `HL.DIVW` +20 |
| [Floating-point Arithmetic](floating_point_arithmetic.md) | 12 | **Ch 13** — [source](index.md) | `FABS`, `FADD`, `FDIV`, `FEXP`, `FMADD`, `FMSUB`, `FMUL`, `FNMADD` +4 |
| [Format Convert](format_convert.md) | 12 | **Ch 13** — [source](index.md) | `FCVT`, `FCVTA`, `FCVTM`, `FCVTN`, `FCVTP`, `FCVTZ`, `SCVTF`, `UCVTF` +4 |
| [Floating-point Compare](floating_point_compare.md) | 8 | **Ch 13** — [source](index.md) | `FEQ`, `FEQS`, `FGE`, `FGES`, `FLT`, `FLTS`, `FNE`, `FNES` |
| [Max-Min](max_min.md) | 6 | **Ch 16** — [source](index.md) | `FMAX`, `FMIN`, `MAX`, `MAXU`, `MIN`, `MINU` |
| [RESERVE](reserve.md) | 3 | **Ch 18** — [source](index.md) | `HL.BFI`, `HL.MIADD`, `HL.MISUB` |
| [Atomic](atomic.md) | 4 | **Ch 14** — [source](index.md) | `HL.CASB`, `HL.CASD`, `HL.CASH`, `HL.CASW` |
| [Concat](concat.md) | 2 | **Ch 18** — [source](index.md) | `HL.CCAT`, `HL.CCATW` |
| [Load PC-Relative](load_pc_relative.md) | 7 | **Ch 11** — [source](index.md) | `HL.LB.PCR`, `HL.LBU.PCR`, `HL.LD.PCR`, `HL.LH.PCR`, `HL.LHU.PCR`, `HL.LW.PCR`, `HL.LWU.PCR` |
| [Load Post-Index](load_post_index.md) | 19 | **Ch 11** — [source](index.md) | `HL.LB.PO`, `HL.LBI.PO`, `HL.LBU.PO`, `HL.LBUI.PO`, `HL.LD.PO`, `HL.LDI.PO`, `HL.LDI.UPO`, `HL.LH.PO` +11 |
| [Load Pre-Index](load_pre_index.md) | 19 | **Ch 11** — [source](index.md) | `HL.LB.PR`, `HL.LBI.PR`, `HL.LBU.PR`, `HL.LBUI.PR`, `HL.LD.PR`, `HL.LDI.PR`, `HL.LDI.UPR`, `HL.LH.PR` +11 |
| [Load Long Offset](load_long_offset.md) | 12 | **Ch 11** — [source](index.md) | `HL.LBI`, `HL.LBUI`, `HL.LDI`, `HL.LDI.U`, `HL.LHI`, `HL.LHI.U`, `HL.LHUI`, `HL.LHUI.U` +4 |
| [Load Pair](load_pair.md) | 19 | **Ch 11** — [source](index.md) | `HL.LBIP`, `HL.LBP`, `HL.LBUIP`, `HL.LBUP`, `HL.LDIP`, `HL.LDIP.U`, `HL.LDP`, `HL.LHIP` +11 |
| [Long Immediate](long_immediate.md) | 2 | **Ch 12** — [source](index.md) | `HL.LIS`, `HL.LIU` |
| [Immediate](immediate.md) | 2 | **Ch 12** — [source](index.md) | `HL.LUI`, `LUI` |
| [Prefetch](prefetch.md) | 4 | **Ch 11** — [source](index.md) | `HL.PRF`, `HL.PRF.A`, `HL.PRFI.U`, `HL.PRFI.UA` |
| [General](general.md) | 3 | **Ch 4** — [source](index.md) | `HL.QMT`, `HL.QPOP`, `HL.QPUSH` |
| [Store PC-Relative](store_pc_relative.md) | 4 | **Ch 11** — [source](index.md) | `HL.SB.PCR`, `HL.SD.PCR`, `HL.SH.PCR`, `HL.SW.PCR` |
| [Store Post-Index](store_post_index.md) | 14 | **Ch 11** — [source](index.md) | `HL.SB.PO`, `HL.SBI.PO`, `HL.SD.PO`, `HL.SD.UPO`, `HL.SDI.PO`, `HL.SDI.UPO`, `HL.SH.PO`, `HL.SH.UPO` +6 |
| [Store Pre-Index](store_pre_index.md) | 14 | **Ch 11** — [source](index.md) | `HL.SB.PR`, `HL.SBI.PR`, `HL.SD.PR`, `HL.SD.UPR`, `HL.SDI.PR`, `HL.SDI.UPR`, `HL.SH.PR`, `HL.SH.UPR` +6 |
| [Store Long Offset](store_long_offset.md) | 7 | **Ch 11** — [source](index.md) | `HL.SBI`, `HL.SDI`, `HL.SDI.U`, `HL.SHI`, `HL.SHI.U`, `HL.SWI`, `HL.SWI.U` |
| [Store Pair](store_pair.md) | 14 | **Ch 11** — [source](index.md) | `HL.SBIP`, `HL.SBP`, `HL.SDIP`, `HL.SDIP.U`, `HL.SDP`, `HL.SDP.U`, `HL.SHIP`, `HL.SHIP.U` +6 |
| [SSR Access](ssr_access.md) | 7 | **Ch 19** — [source](index.md) | `HL.SSRGET`, `HL.SSRSET`, `LSRGET`, `SETC.TGT`, `SSRGET`, `SSRSET`, `SSRSWAP` |
| [Load Register Offset](load_register_offset.md) | 22 | **Ch 11** — [source](index.md) | `LB`, `LBU`, `LD`, `LH`, `LHU`, `LW`, `LWU`, `PRF` +14 |
| [Load Symbol](load_symbol.md) | 7 | **Ch 11** — [source](index.md) | `LB.PCR`, `LBU.PCR`, `LD.PCR`, `LH.PCR`, `LHU.PCR`, `LW.PCR`, `LWU.PCR` |
| [Atomic Operation](atomic_operation.md) | 68 | **Ch 14** — [source](index.md) | `LD.ADD`, `LD.AND`, `LD.OR`, `LD.SMAX`, `LD.SMIN`, `LD.UMAX`, `LD.UMIN`, `LD.XOR` +60 |
| [Load UnScaled](load_unscaled.md) | 16 | **Ch 11** — [source](index.md) | `LDI.U`, `LHI.U`, `LHUI.U`, `LWI.U`, `LWUI.U`, `PRFI.U`, `V.LDI.U`, `V.LDI.U.BRG` +8 |
| [Store Register Offset](store_register_offset.md) | 21 | **Ch 11** — [source](index.md) | `SB`, `SD`, `SD.U`, `SH`, `SH.U`, `SW`, `SW.U`, `V.SB` +13 |
| [Store Symbol](store_symbol.md) | 4 | **Ch 11** — [source](index.md) | `SB.PCR`, `SD.PCR`, `SH.PCR`, `SW.PCR` |
| [Bit Manipulation](bit_manipulation.md) | 8 | **Ch 12** — [source](index.md) | `V.BCNT`, `V.BIC`, `V.BIS`, `V.BXS`, `V.BXU`, `V.CLZ`, `V.CTZ`, `V.REV` |
| [Three Source Integer](three_source_integer.md) | 2 | **Ch 20** — [source](index.md) | `V.CSEL`, `V.PSEL` |
| [Division](division.md) | 2 | **Ch 20** — [source](index.md) | `V.DIV`, `V.REM` |
| [Floating Point Arithmetic](floating_point_arithmetic.md) | 5 | **Ch 20** — [source](index.md) | `V.FABS`, `V.FCLASS`, `V.FEXP`, `V.FRECIP`, `V.FSQRT` |
| [Three-Source Floating Point](three_source_floating_point.md) | 8 | **Ch 20** — [source](index.md) | `V.FADD`, `V.FDIV`, `V.FMADD`, `V.FMSUB`, `V.FMUL`, `V.FNMADD`, `V.FNMSUB`, `V.FSUB` |
| [Two-Source Floating Point](two_source_floating_point.md) | 12 | **Ch 20** — [source](index.md) | `V.FEQ`, `V.FEQS`, `V.FGE`, `V.FGES`, `V.FLT`, `V.FLTS`, `V.FMAX`, `V.FMIN` +4 |
| [General Manager](general_manager.md) | 2 | **Ch 9** — [source](index.md) | `V.QPOP`, `V.QPUSH` |
| [Reduce Operation with Register](reduce_operation_with_register.md) | 9 | **Ch 20** — [source](index.md) | `V.RDADD`, `V.RDAND`, `V.RDFADD`, `V.RDFMAX`, `V.RDFMIN`, `V.RDMAX`, `V.RDMIN`, `V.RDOR` +1 |
| [Store Offset](store_offset.md) | 14 | **Ch 11** — [source](index.md) | `V.SBI`, `V.SBI.BRG`, `V.SDI`, `V.SDI.BRG`, `V.SDI.U`, `V.SDI.U.BRG`, `V.SHI`, `V.SHI.BRG` +6 |
| [Shuffle](shuffle.md) | 8 | **Ch 20** — [source](index.md) | `V.SHFL.BFLY`, `V.SHFL.DOWN`, `V.SHFL.IDX`, `V.SHFL.UP`, `V.SHFLI.BFLY`, `V.SHFLI.DOWN`, `V.SHFLI.IDX`, `V.SHFLI.UP` |
