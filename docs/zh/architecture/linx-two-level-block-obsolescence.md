# 架构决策：废弃 Linx 两级执行扩展的 193 个编码形式

**已采纳 · 2026-11-24 · 适用于 LinxISA v0.59.1 修订稿。** 以 LinxISA `v0.59.1` 的发布目录为基线，从有效指令集合删除 A–E 共 193 个形式。这些形式占用的编码按 PTO-SPEC 继续预留，禁止重新分配。

## 裁决范围

| 组 | 发布目录中的形式 | 数量 | 架构状态 |
| --- | --- | ---: | --- |
| A | 全部以 `V.` 开头的助记符，逐条见附录 | 184 | 删除，编码预留 |
| B | `BSTART.MSEQ`、`BSTART.MPAR` | 2 | 删除，编码预留 |
| C | `C.BSTART.MSEQ`、`C.BSTART.MPAR` | 2 | 删除，编码预留 |
| D | `BSTART.VSEQ`、`BSTART.VPAR`、`C.BSTART.VSEQ`、`C.BSTART.VPAR` | 4 | 删除，编码预留 |
| E | `B.TEXT` | 1 | 删除，编码预留 |
| F | `HL.BSTART.CALL` | 1 | 沿用现行定义 |
| G | `HL.BSTART.FP`、`HL.BSTART.STD` 各 4 个形式，`HL.BSTART.SYS` 1 个形式 | 9 | 沿用现行定义 |
| H | `L.BSTART.FP`、`L.BSTART.STD` 各 4 个形式，`L.BSTART.SYS` 1 个形式 | 9 | 沿用现行定义 |
| I | `DMA.FREE.L`、`DMA.FREE.S`、`MCOPY.DL`、`MCOPY.DS` | 4 | 仅预留编码，不实现 |

A–E 一并覆盖旧向量块体指令、顺序和并行分离块的普通与压缩入口，以及指定块外地址的 `B.TEXT`。A 按助记符前缀选取，包含 VEC 类的 182 条，以及归入 CMD 类的 `V.QPUSH`、`V.QPOP`。PTO 的 Tile VEC 引擎、`TADD` 等 Tile 操作和承载它们的 `BSTART.TEPL` 有各自的发布定义。

F–H 共 19 个形式继续采用 Linx 定义。I 组的 4 个形式只占用码位，执行须在读取操作数或产生架构效果前拒绝。三类合计覆盖 216 个 Linx 独有形式（193 + 19 + 4）。本次采用硬断开策略：落入这十个预留范围的机器字必须在读取操作数或产生架构效果之前被拒绝，包括 V.* 预留区内从未分配给助记符的机器字。

## 编码归属

LinxISA `v0.59.1` 锁定 PTO 发布标签 `v0.59.1.0`（提交 `a89a53d48f5708328be609fe2e6296ac8bdb4bc2`）。A 组的 184 个 64 位形式均落在同一条 `V.*` 预留记录内；B–E 的 9 个形式各有一条具名预留记录。因此 193 个形式对应 **10 条 PTO 预留记录**。预留覆盖整个匹配范围，包括尚无 Linx 助记符的取值。仓库来源为 `isa/v0.59/linxisa-v0.59.json` 和 `isa/v0.59/pto-spec.lock.json`。[PTO 原始编码预留表](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/spec/catalog/extension-encoding-reservations.json)

| 助记符 | 位宽 | Mask | Match |
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

按 `(指令字 & Mask) == Match` 识别各行。V.* 的 64 位区域仅检查第一段的低 7 位，第二段全部位都在该预留区内。

## 附录：A 组 184 个形式

按发布目录的 group 展示，匹配条件为助记符以 `V.` 开头。19 个组共 184 条。目录中的 CMD 类也纳入匹配。

| 目录分组 | 数量 | 助记符 |
| --- | ---: | --- |
| Arithmetic Operation | 16 | `V.ADD`、`V.ADDI`、`V.AND`、`V.ANDI`、`V.OR`、`V.ORI`、`V.SLL`、`V.SLLI`、`V.SRA`、`V.SRAI`、`V.SRL`、`V.SRLI`、`V.SUB`、`V.SUBI`、`V.XOR`、`V.XORI` |
| Atomic Operation | 24 | `V.LD.ADD`、`V.LD.AND`、`V.LD.MAX`、`V.LD.MIN`、`V.LD.OR`、`V.LD.XOR`、`V.LW.ADD`、`V.LW.AND`、`V.LW.MAX`、`V.LW.MIN`、`V.LW.OR`、`V.LW.XOR`、`V.SD.ADD`、`V.SD.AND`、`V.SD.MAX`、`V.SD.MIN`、`V.SD.OR`、`V.SD.XOR`、`V.SW.ADD`、`V.SW.AND`、`V.SW.MAX`、`V.SW.MIN`、`V.SW.OR`、`V.SW.XOR` |
| Bit Manipulation | 8 | `V.BCNT`、`V.BIC`、`V.BIS`、`V.BXS`、`V.BXU`、`V.CLZ`、`V.CTZ`、`V.REV` |
| Compare Instruction | 16 | `V.CMP.AND`、`V.CMP.ANDI`、`V.CMP.EQ`、`V.CMP.EQI`、`V.CMP.GE`、`V.CMP.GEI`、`V.CMP.GEU`、`V.CMP.GEUI`、`V.CMP.LT`、`V.CMP.LTI`、`V.CMP.LTU`、`V.CMP.LTUI`、`V.CMP.NE`、`V.CMP.NEI`、`V.CMP.OR`、`V.CMP.ORI` |
| Division | 2 | `V.DIV`、`V.REM` |
| Floating Point Arithmetic | 5 | `V.FABS`、`V.FCLASS`、`V.FEXP`、`V.FRECIP`、`V.FSQRT` |
| Format Convert | 4 | `V.FCVT`、`V.FCVTI`、`V.ICVT`、`V.ICVTF` |
| General Manager | 2 | `V.QPOP`、`V.QPUSH` |
| Load Immediate Offset | 14 | `V.LBI`、`V.LBI.BRG`、`V.LBUI`、`V.LBUI.BRG`、`V.LDI`、`V.LDI.BRG`、`V.LHI`、`V.LHI.BRG`、`V.LHUI`、`V.LHUI.BRG`、`V.LWI`、`V.LWI.BRG`、`V.LWUI`、`V.LWUI.BRG` |
| Load Register Offset | 14 | `V.LB`、`V.LB.BRG`、`V.LBU`、`V.LBU.BRG`、`V.LD`、`V.LD.BRG`、`V.LH`、`V.LH.BRG`、`V.LHU`、`V.LHU.BRG`、`V.LW`、`V.LW.BRG`、`V.LWU`、`V.LWU.BRG` |
| Load UnScaled | 10 | `V.LDI.U`、`V.LDI.U.BRG`、`V.LHI.U`、`V.LHI.U.BRG`、`V.LHUI.U`、`V.LHUI.U.BRG`、`V.LWI.U`、`V.LWI.U.BRG`、`V.LWUI.U`、`V.LWUI.U.BRG` |
| Multi-Cycle ALU | 2 | `V.MADD`、`V.MUL` |
| Reduce Operation with Register | 9 | `V.RDADD`、`V.RDAND`、`V.RDFADD`、`V.RDFMAX`、`V.RDFMIN`、`V.RDMAX`、`V.RDMIN`、`V.RDOR`、`V.RDXOR` |
| Shuffle | 8 | `V.SHFL.BFLY`、`V.SHFL.DOWN`、`V.SHFL.IDX`、`V.SHFL.UP`、`V.SHFLI.BFLY`、`V.SHFLI.DOWN`、`V.SHFLI.IDX`、`V.SHFLI.UP` |
| Store Offset | 14 | `V.SBI`、`V.SBI.BRG`、`V.SDI`、`V.SDI.BRG`、`V.SDI.U`、`V.SDI.U.BRG`、`V.SHI`、`V.SHI.BRG`、`V.SHI.U`、`V.SHI.U.BRG`、`V.SWI`、`V.SWI.BRG`、`V.SWI.U`、`V.SWI.U.BRG` |
| Store Register Offset | 14 | `V.SB`、`V.SB.BRG`、`V.SD`、`V.SD.BRG`、`V.SD.U`、`V.SD.U.BRG`、`V.SH`、`V.SH.BRG`、`V.SH.U`、`V.SH.U.BRG`、`V.SW`、`V.SW.BRG`、`V.SW.U`、`V.SW.U.BRG` |
| Three Source Integer | 2 | `V.CSEL`、`V.PSEL` |
| Three-Source Floating Point | 8 | `V.FADD`、`V.FDIV`、`V.FMADD`、`V.FMSUB`、`V.FMUL`、`V.FNMADD`、`V.FNMSUB`、`V.FSUB` |
| Two-Source Floating Point | 12 | `V.FEQ`、`V.FEQS`、`V.FGE`、`V.FGES`、`V.FLT`、`V.FLTS`、`V.FMAX`、`V.FMIN`、`V.FNE`、`V.FNES`、`V.MAX`、`V.MIN` |
