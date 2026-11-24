# Architecture decision: obsolete two-level execution forms

**Accepted 2026-11-24 for the next LinxISA architecture specification.** Using LinxISA `v0.59.1` as the inventory baseline, classify all 193 forms in groups A–E as `obsolete`. Keep their entire encoding spaces reserved as specified by PTO-SPEC. Future instructions must not reuse them.

| Group | Forms | Count | Decision |
| --- | --- | ---: | --- |
| A | Every mnemonic beginning with `V.`, listed in the appendix | 184 | Obsolete |
| B | `BSTART.MSEQ`, `BSTART.MPAR` | 2 | Obsolete |
| C | `C.BSTART.MSEQ`, `C.BSTART.MPAR` | 2 | Obsolete |
| D | `BSTART.VSEQ`, `BSTART.VPAR`, `C.BSTART.VSEQ`, `C.BSTART.VPAR` | 4 | Obsolete |
| E | `B.TEXT` | 1 | Obsolete |
| F | `HL.BSTART.CALL` | 1 | Retain current definition |
| G | `HL.BSTART.FP` and `HL.BSTART.STD` (four forms each), `HL.BSTART.SYS` (one) | 9 | Retain current definitions |
| H | `L.BSTART.FP` and `L.BSTART.STD` (four forms each), `L.BSTART.SYS` (one) | 9 | Retain current definitions |
| I | `DMA.FREE.L`, `DMA.FREE.S`, `MCOPY.DL`, `MCOPY.DS` | 4 | Encoding reservations only. Execution is unimplemented and must reject before operand reads or architectural effects |

This accounts for all 216 Linx-only forms: 193 obsolete, 19 retained and four encoding-only. The prefix in A includes the two CMD forms `V.QPUSH` and `V.QPOP` as well as the 182 VEC forms. Groups B–E cover the full-size and compressed block entries and their out-of-line body address. The PTO Tile VEC engine, Tile operations such as `TADD`, and the `BSTART.TEPL` carrier have their own definitions. Legacy binary execution policy for A–E remains a separate decision.

## Encoding ownership

The Linx lock selects PTO `v0.59.1.0` at `a89a53d48f5708328be609fe2e6296ac8bdb4bc2`. Group A occupies one reserved 64-bit region: bits 6–0 of the first 32-bit word equal `0x7f`, and the second word is unrestricted. The nine forms in B–E each have a named reservation. These ten reservations cover every matching bit pattern, including values without a Linx mnemonic. Use `(word & mask) == match` for the rows below. [Linx release catalog](../../isa/v0.59/linxisa-v0.59.json) · [PTO source lock](../../isa/v0.59/pto-spec.lock.json) · [PTO reservation table](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/spec/catalog/extension-encoding-reservations.json)

| Mnemonic | Width (bits) | Mask | Match |
| --- | ---: | --- | --- |
| BSTART.MPAR | 32 | `0xf9ffffff` | `0x00001181` |
| BSTART.MSEQ | 32 | `0xf9ffffff` | `0x00009181` |
| C.BSTART.MPAR | 16 | `0xffff` | `0x08c0` |
| C.BSTART.MSEQ | 16 | `0xffff` | `0x48c0` |
| BSTART.VPAR | 32 | `0xf9ffffff` | `0x00021181` |
| BSTART.VSEQ | 32 | `0xf9ffffff` | `0x00029181` |
| C.BSTART.VPAR | 16 | `0xffff` | `0x88c0` |
| C.BSTART.VSEQ | 16 | `0xffff` | `0xc8c0` |
| B.TEXT | 32 | `0x0000007f` | `0x00000003` |

## Appendix: all 184 group A mnemonics

| Catalog group | Count | Mnemonics |
| --- | ---: | --- |
| Arithmetic Operation | 16 | `V.ADD`, `V.ADDI`, `V.AND`, `V.ANDI`, `V.OR`, `V.ORI`, `V.SLL`, `V.SLLI`, `V.SRA`, `V.SRAI`, `V.SRL`, `V.SRLI`, `V.SUB`, `V.SUBI`, `V.XOR`, `V.XORI` |
| Atomic Operation | 24 | `V.LD.ADD`, `V.LD.AND`, `V.LD.MAX`, `V.LD.MIN`, `V.LD.OR`, `V.LD.XOR`, `V.LW.ADD`, `V.LW.AND`, `V.LW.MAX`, `V.LW.MIN`, `V.LW.OR`, `V.LW.XOR`, `V.SD.ADD`, `V.SD.AND`, `V.SD.MAX`, `V.SD.MIN`, `V.SD.OR`, `V.SD.XOR`, `V.SW.ADD`, `V.SW.AND`, `V.SW.MAX`, `V.SW.MIN`, `V.SW.OR`, `V.SW.XOR` |
| Bit Manipulation | 8 | `V.BCNT`, `V.BIC`, `V.BIS`, `V.BXS`, `V.BXU`, `V.CLZ`, `V.CTZ`, `V.REV` |
| Compare Instruction | 16 | `V.CMP.AND`, `V.CMP.ANDI`, `V.CMP.EQ`, `V.CMP.EQI`, `V.CMP.GE`, `V.CMP.GEI`, `V.CMP.GEU`, `V.CMP.GEUI`, `V.CMP.LT`, `V.CMP.LTI`, `V.CMP.LTU`, `V.CMP.LTUI`, `V.CMP.NE`, `V.CMP.NEI`, `V.CMP.OR`, `V.CMP.ORI` |
| Division | 2 | `V.DIV`, `V.REM` |
| Floating Point Arithmetic | 5 | `V.FABS`, `V.FCLASS`, `V.FEXP`, `V.FRECIP`, `V.FSQRT` |
| Format Convert | 4 | `V.FCVT`, `V.FCVTI`, `V.ICVT`, `V.ICVTF` |
| General Manager | 2 | `V.QPOP`, `V.QPUSH` |
| Load Immediate Offset | 14 | `V.LBI`, `V.LBI.BRG`, `V.LBUI`, `V.LBUI.BRG`, `V.LDI`, `V.LDI.BRG`, `V.LHI`, `V.LHI.BRG`, `V.LHUI`, `V.LHUI.BRG`, `V.LWI`, `V.LWI.BRG`, `V.LWUI`, `V.LWUI.BRG` |
| Load Register Offset | 14 | `V.LB`, `V.LB.BRG`, `V.LBU`, `V.LBU.BRG`, `V.LD`, `V.LD.BRG`, `V.LH`, `V.LH.BRG`, `V.LHU`, `V.LHU.BRG`, `V.LW`, `V.LW.BRG`, `V.LWU`, `V.LWU.BRG` |
| Load UnScaled | 10 | `V.LDI.U`, `V.LDI.U.BRG`, `V.LHI.U`, `V.LHI.U.BRG`, `V.LHUI.U`, `V.LHUI.U.BRG`, `V.LWI.U`, `V.LWI.U.BRG`, `V.LWUI.U`, `V.LWUI.U.BRG` |
| Multi-Cycle ALU | 2 | `V.MADD`, `V.MUL` |
| Reduce Operation with Register | 9 | `V.RDADD`, `V.RDAND`, `V.RDFADD`, `V.RDFMAX`, `V.RDFMIN`, `V.RDMAX`, `V.RDMIN`, `V.RDOR`, `V.RDXOR` |
| Shuffle | 8 | `V.SHFL.BFLY`, `V.SHFL.DOWN`, `V.SHFL.IDX`, `V.SHFL.UP`, `V.SHFLI.BFLY`, `V.SHFLI.DOWN`, `V.SHFLI.IDX`, `V.SHFLI.UP` |
| Store Offset | 14 | `V.SBI`, `V.SBI.BRG`, `V.SDI`, `V.SDI.BRG`, `V.SDI.U`, `V.SDI.U.BRG`, `V.SHI`, `V.SHI.BRG`, `V.SHI.U`, `V.SHI.U.BRG`, `V.SWI`, `V.SWI.BRG`, `V.SWI.U`, `V.SWI.U.BRG` |
| Store Register Offset | 14 | `V.SB`, `V.SB.BRG`, `V.SD`, `V.SD.BRG`, `V.SD.U`, `V.SD.U.BRG`, `V.SH`, `V.SH.BRG`, `V.SH.U`, `V.SH.U.BRG`, `V.SW`, `V.SW.BRG`, `V.SW.U`, `V.SW.U.BRG` |
| Three Source Integer | 2 | `V.CSEL`, `V.PSEL` |
| Three-Source Floating Point | 8 | `V.FADD`, `V.FDIV`, `V.FMADD`, `V.FMSUB`, `V.FMUL`, `V.FNMADD`, `V.FNMSUB`, `V.FSUB` |
| Two-Source Floating Point | 12 | `V.FEQ`, `V.FEQS`, `V.FGE`, `V.FGES`, `V.FLT`, `V.FLTS`, `V.FMAX`, `V.FMIN`, `V.FNE`, `V.FNES`, `V.MAX`, `V.MIN` |
