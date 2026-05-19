# 0.54 version update

Update date: October 24, 2025

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-0.54](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:101014747097)

## 1. Update background

This version 0.54 is mainly used to improve the existing Tile block execution model, update the naming of existing instructions, add specific constraints in details and solve problems in some scenarios.

1. Strengthen the definition and constraints of block type by refining the Tile block classification
2. By adding spill to the S-tile register, the problem of insufficient number of vector registers in some scenarios is solved.
3. Reduce the number of block-private registers by increasing the block-private register number option to solve the resource waste problem caused by too many vector registers in some scenarios.
4. By adding instructions for dual-output Tile registers, the demand for the number of input/outputTiles when integrating Tileop in high-performance scenarios is met.
5. By adding empty Tile register definition implementation, the problem of different index distances of Tile registers in different branches in intensive control flow scenarios is solved.
6. Simplify the implementation of hardware identification of continuous Load/Store by enhancing the definition of address continuous Load/Store.
7. Added a new dimensionality reduction mode switch, and the software can choose whether to optimize the performance of specific scenarios through dimensionality reduction mode.
8. By adjusting the naming of vector instructions, it is easier for software or programmers to distinguish vector instructions.
9. By adding the Load/Store Local or Global flag, it is easier for the hardware to identify memory or Tile register access in advance.
10. By adding the v.psel instruction, the controllability of invalid Lane results is enhanced and the optimization of unilateral branch data merging operations is realized.
11. Solve the problems found in corner scenes by adding instruction constraints.

## 2. Summary of updated content

LinxISA version 0.54 has made the following design adjustments:| Category | Updates | Description |
|-----|--------|---------|
| 1. Tile block design changes | 1.1 Update Tile block classification and definition | Used to refine Tile block classification and strengthen block type definition. |
| | 1.2 Added the option of the number of block-private registers | Reduce the waste of vector register resources in some scenarios. |
| | 1.3 Add private Tile register definition | Tile block can apply for a private Tile Register for register spill within the block. |
| | 1.4 New empty Tile register definition | Used to align the index distance when the compiler allocates registers. |
| | 1.5 New Tile register dual output definition (added TO1) | Meet the demand for the number of input/outputTiles when integrating Tileop in high-performance scenarios. |
| | 1.6 The B.ATTR instruction flag bit is adjusted and merged with the B.ARG instruction | Merge instructions of the same type to streamline the coding space. (Note: Delete the B.ARG instruction) |
| | 1.7 Added dimensionality reduction (DR) mode | to meet the needs of different scenarios. |
| 2. Instruction design expansion | 2.1 vector instruction naming adjustment | Used to distinguish vector operations and scalar operations |
| | 2.2 Strengthen the definition of continuous address load/store | Constrain the base address and offset register of continuous load/store to be the scalar register |
| | 2.3 Load/Store Bridge instruction adds address continuity flag | Used to provide address continuity flag while using bridged memory access instruction |
| | 2.4 Load/Store instructions add identification to distinguish access to local/global | The hardware identifies memory or Tile register access in advance, without waiting for the address to be calculated before making a judgment, thereby improving performance. |
| | 2.5 Added V.PSEL instruction | Used to optimize data merging in unilateral branch scenarios. |
| | 2.6 Add instruction constraints | setret must be placed after BSTART to ensure the performance of the hardware predictor |
| 3. System block definition | 3.1 System block instruction only supports FALL type | Delete BSTART codes corresponding to other jump methods |

## 3. Update details

### 1. Tile block design extension

Tile blocks are a type of block instruction that can access Tile registers. This type of block instruction was introduced to achieve large-scale tensor operations, and by decomposing large operators into Tile-level operations, combined with hardware vectorization/hardening processing and other execution capabilities, it improves the performance of intensive computing tasks such as matrix operations or vector operations.

**1.1 Tile block classification**

In the new version, Tile blocks are divided into the following specific block type according to dimensions such as whether they can access memory, whether there is body and execution mode, so as to provide targeted definitions or constraints for each type of block type.

Tile blocks are classified as follows:| Category/dimension | Whether memory can be accessed | Whether there is body | Whether groups are parallel (whether internal calculations can be parallelized) | Remarks |
|----------|------------|------------|-------------------------------------|---------|
| **Memory Parallel Block (MPAR)** | Can | Yes | Yes | Corresponds to the previous version of MCALL, and Parallel mode |
| **Memory access serial block (MSEQ)** | Can | Yes | No | Corresponds to the previous version of MCALL, and Vector mode |
| **vector Parallel Block (VPAR)** | No | Yes | Yes | Corresponds to the previous version of VCALL, and Parallel mode |
| **vector serial block (VSEQ)** | No | Yes | No | Corresponds to the previous version of VCALL, and Vector mode |
| **Data Movement Block (TMA)** | Yes | No | Yes | Corresponds to TLoad/TStore/TCopy |
| **Matrix Data Block (CUBE)** | No | No | Yes | Corresponds to matrix operations and ACCCVT, etc. |

Different types of Tile blocks can have different block parameter instructions, which are used to configure the execution parameters of this block. See the following table for details:

| Block parameters | B.ATTR | B.DIM | B.IOT/B.IOTI | B.IOR | B.IOD | B.TEXT | B.HINT |
|-------|--------|-------|-------|------|-------|--------|----------|
| MPAR | Support | Support | Support | Support | Support | Support | Not support |
| MSEQ | Support | Support | Support | Support | Support | Support | Not support |
| VPAR | Supported | Supported | Supported | Supported | Supported | Supported | Not Supported |
| VSEQ | Support | Support | Support | Support | Support | Support | Not support |
| TMA | Support | Support | Support | Support | Support | Not support | Not support |
| CUBE | Support | Support | Support | Not support | Not support | Not support | Not support |

BSTART assembly format:

```asm
BSTART.MPAR <VS8, VS16>
BSTART.MSEQ <VS8, VS16>
BSTART.VPAR <VS8, VS16>
BSTART.VSEQ  <VS8, VS16>
BSTART.TMA TileOp, DataType
BSTART.CUBE TileOP, DataType
```

In terms of encoding, the BlockType field of the Tile block is uniformly encoded as "5b00011", and the BSTART encoding of different types of Tile blocks is as follows:

![bstart.tile](../figs/isa/version/0.54/bstart.tile.png)

For Tile blocks with body, a 16bit BSTART version is also provided.

![c.bstart.tile](../figs/isa/version/0.54/c.bstart.tile.png)

**1.2 Added option for the number of vector registers used**

The current version has body Tile blocks (including MPAR/MSEQ/VPAR/VSEQ). We provide 4 sets of vector registers (vt/vu/vm/vn) within the block, each set of 4. These vector registers will occupy a large amount of physical register resources. And in some scenarios, the Tile block only uses one or two sets of vector registers, causing register resource congestion and affecting the execution efficiency of the Tile block.

Therefore, in the new version, we provide an option for the number of vector registers used for these four Tile blocks. The software can use this option to indicate the number of vector registers used by this block, so that the hardware can reasonably allocate register resources.

This information is expressed on the BSTART instruction of the Tile block, and the assembly format is as follows:
```asm
BSTART.MPAR <VS8, VS16>
BSTART.MSEQ <VS8, VS16>
BSTART.VPAR <VS8, VS16>
BSTART.VSEQ <VS8, VS16>
BSTART.MPAR <VS8, VS16>
BSTART.MSEQ <VS8, VS16>
BSTART.VPAR <VS8, VS16>
BSTART.VSEQ <VS8, VS16>
```Among them, parameters such as "VS" are used to express the number of vector registers used in the block (VS is the abbreviation of Vector Size).

Encoding method:

![c.bstart.tile](../figs/isa/version/0.54/bstart.tile1.png)

This parameter is encoded in the Mode field of the BSTART instruction, and the encoding method is as follows:

| Mode encoding | Meaning | Description |
|----------|-------|------|
| 0 | **VS8** | 2 sets of vector registers are required in the block, 4 in each set (8 in total) |
| 1 | **VS16** | 4 groups of vector registers are required in the block, 4 in each group (16 in total) |
| 2 | VS32 (not supported by the current version) | 4 groups of vector registers are required in the block, 8 in each group (32 in total) |
| 3 | VS64 (not supported by the current version) | 4 groups of vector registers are required in the block, 16 in each group (64 in total) |

Things to note:

- The number of vector registers requested by the software must be greater than or equal to the actual number used, otherwise the hardware will report the illegal parameter exception.
- The 16bit version of C.BSTART.MPAR, etc. does not have a Mode field and uses the full vector register by default.

**1.3 Add private Tile register**

Since the vector parallel block and vector serial block do not allow direct access to the memory space, there is no concept of a thread stack. Therefore, functions that rely on stack space such as function calls and register spills cannot be implemented, which seriously limits the computing power and ease of use of block instruction. To address this problem, we propose the following design extensions:

**1.3.1 Add S register**

Add a type of Tile Register to the first-layer architecture, named S (full name: Stack Tile Register). This register is specially used for Tileblock instruction function call parameter storage or stack space for register spill.

**1.3.2 How to use S register**

- Like other types of Tile registers, Tileblock instruction applies to use the S register through the B.IOT/B.IOTI instruction.
- The difference is that the S register is private to the block instruction that applies for it. The S register is only visible to this block and can be read and written within the block. And this register is released with the submission of block instruction.
- The B.IOT instruction applies for the stack space size used within a Group, and the total space size of the S register requires hardware calculation.
- Note: The total space size of the S register is obtained by multiplying the S register Group capacity by the number of Groups, and **the space size cannot exceed 512KB**.

Example:
```asm
BSTART.VPAR <Row:64, Col:64, FP16>, T#1, U#1, ->T<16KB>, S<8KB>
// 展开形式
BSTART.VPAR FP16
B.DIM zero, 64, ->Row
B.DIM zero, 64, ->Col
B.IOTI T#1, U#1, group=0, ->S<8KB>    # 每个group申请的空间8KB
B.IOTI           group=1, ->T<16KB>
BSTART.VPAR <Row:64, Col:64, FP16>, T#1, U#1, ->T<16KB>, S<8KB>
// 展开形式
BSTART.VPAR FP16
B.DIM zero, 64, ->Row
B.DIM zero, 64, ->Col
B.IOTI T#1, U#1, group=0, ->S<8KB>    # 每个group申请的空间8KB
B.IOTI           group=1, ->T<16KB>
```

**1.3.3 Formal parameter register**

A Tile type formal parameter register TS is added to the block, which is mapped to the S register applied for by header. TS points to the corresponding stack space in the current group.

Register spill example:
```
// Spill
l.sd vt#1.ud, [TS, lc0<<3]
// Reload
l.ld [TS, LC0<<3], ->vt.d
// Spill
l.sd vt#1.ud, [TS, lc0<<3]
// Reload
l.ld [TS, LC0<<3], ->vt.d
```
Note: If an uninitialized TS is read within the block, a random value will be returned.

**1.4 Added empty Tile register definition**

Tileblock instruction allows output to empty Tile registers, which is used to align the index distance when the compiler allocates registers.

**1.4.1 Scenario Example**

Under the relative index register design, after the life cycle of a variable spans the control flow, since different control flow paths may write different times to the hand to which the variable register belongs, there may be multiple index distances when the control flow convergence point uses the variable.
```
if.entry:
     BSTART.VPAR  -> T<1KB>
     BSTART.COND  if.then, if.end
if.then:
     BSTART.MPAR  -> T<2KB>
     BSTART.MPAR  -> T<2KB>
     BSTART DIRECT  if.end 
if.end:
     TSTORE T#?, [a0]          # 将VCALL结果写回内存，此处存在2种索引距离
if.entry:
     BSTART.VPAR  -> T<1KB>
     BSTART.COND  if.then, if.end
if.then:
     BSTART.MPAR  -> T<2KB>
     BSTART.MPAR  -> T<2KB>
     BSTART DIRECT  if.end 
if.end:
     TSTORE T#?, [a0]          # 将VCALL结果写回内存，此处存在2种索引距离
```

In order to solve the above problem, it is necessary to insert some additional instructions to output to the empty Tile in the if.entry code segment to adjust the index distance so that the two index distances at if.end are equal.
```asm
if.entry:
     BSTART.VPAR -> T<1KB>
     BSTART.VPAR -> T<zero>    # 输出至空Tile寄存器  
     BSTART.VPAR -> T<zero>    # 输出至空Tile寄存器  
     BSTART.COND  if.then, if.end
if.then:
     BSTART.MPAR -> T<2KB>
     BSTART.MPAR -> T<2KB>
     BSTART DIRECT  if.end 
if.end:
     TSTORE T#3, [a0]
if.entry:
     BSTART.VPAR -> T<1KB>
     BSTART.VPAR -> T<zero>    # 输出至空Tile寄存器  
     BSTART.VPAR -> T<zero>    # 输出至空Tile寄存器  
     BSTART.COND  if.then, if.end
if.then:
     BSTART.MPAR -> T<2KB>
     BSTART.MPAR -> T<2KB>
     BSTART DIRECT  if.end 
if.end:
     TSTORE T#3, [a0]
```

**1.4.2 Empty Tile register allocation method**If Tileblock instruction needs to apply for an empty Tile register for placeholder, it must use the B.IOT instruction to indicate that the output Tile register space is 0. Information with space 0 is expressed through the zero register.

Example:
```asm
BSTART.VPAR ->T<zero>
BSTART.VPAR ->T<zero>
```
This instruction expands into the following instruction encoding:
```asm
BSTART.VPAR VCALL
B.IOT group=0, ->T<zero>  # 通过zero寄存器表达申请空Tile reg
BSTART.VPAR VCALL
B.IOT group=0, ->T<zero>  # 通过zero寄存器表达申请空Tile reg
```

Encoding method: The RegSrc field is encoded as a zero register.

![biot](../figs/isa/version/0.54/biot.png)

**1.5 B.ATTR and B.ARG instructions are merged**

In order to simplify the instruction coding, the B.ATTR instruction is modified as follows in the new version:

- Delete the hyper flag bit. The current version only supports intra-block jumps in Tile blocks, and there is no need to specify the hyper attribute.
- Delete the relay flag bit. By default, all block instruction do not relay.
- Delete the scall flag bit, which has the same meaning as TRAP.
- TRAP marker bit encoding position adjustment.
- Incorporate the parameters of the B.ARG instruction.
- Added DR flag (dimensionality reduction mode, see section 1.7 for details)

After the relevant parameters of the B.ARG instruction are merged into B.ATTR, delete the B.ARG instruction.

Assembly format:
```asm
B.ATTR {trap, atomic, <aq, rl, aqrl>, far, Layout.{canon, normal}, SrcType, PadValue, DR}
B.ATTR {trap, atomic, <aq, rl, aqrl>, far, Layout.{canon, normal}, SrcType, PadValue, DR}
```

encoding format

![battr](../figs/isa/version/0.54/battr.png)

Among them, the encoding method of the newly added dimensionality reduction mode flag DR is:

| DR | Meaning |
|----|-------|
| 0 | Multidimensional mode |
| 1 | Dimensionality reduction mode |

**1.6 New dimensionality reduction (DR) mode**

In the new version, we provide two ways to expand the three-layer loop of Tileblock instruction.

- Dimension Reduction mode: The three-layer iterations of body are all flattened and unfolded. Every 64 (corresponding to the laneNum of the next Group in the current design) iterations are allocated to a Group for execution until the end of the iteration.
- Multi-Dimension mode (Multi Dimension): Groups are divided into groups based on the number of innermost iterations of body. The two innermost iterations are not allowed to be assigned to the same Group.

The loop expansion of body is implemented as:
```asm
parallel_for（lc2 = 0; lc2 < lb2; lc2++）
    parallel_for（lc1 = 0; lc1 < lb1; lc1++）
        parallel_for（lc0 = 0; lc0 < lb0; lc0++）
              kernel(lane_id);
         end for
    end for
end for
parallel_for（lc2 = 0; lc2 < lb2; lc2++）
    parallel_for（lc1 = 0; lc1 < lb1; lc1++）
        parallel_for（lc0 = 0; lc0 < lb0; lc0++）
              kernel(lane_id);
         end for
    end for
end for
```

The schematic diagram of the dimensionality reduction mode is as follows:

Assuming that the number of innermost loops is 32, the hardware will schedule the two inner loop iterations to be executed in the same group.

![reducedim](../figs/isa/version/0.54/reducedim.png)

The schematic diagram of the multidimensional mode is as follows:

Scenario 1: The upper limit value of the innermost loop (LB0) is less than or equal to 64. The diagram is as follows:

![multidim](../figs/isa/version/0.54/multidim.png)

Scenario 2: The upper limit value of the innermost loop (LB0) is greater than 64. The diagram is as follows:

![multidim1](../figs/isa/version/0.54/multidim1.png)

Under the multidimensional model, it must be ensured:

- The value of LC0 within a Group must be continuous;
- The value of LC1 within a Group must remain unchanged;
- The value of LC2 within a Group must remain unchanged;

Under this model, the calculation formula for the number of Groups split from a Tile block is:
```asm
if (LB0 % 64 > 0) 
    innerNum = LB0 / 64 +1;
else
    innerNum = LB0 / 64;
GroupNumber = LB2 * LB1 * innerNum;
if (LB0 % 64 > 0) 
    innerNum = LB0 / 64 +1;
else
    innerNum = LB0 / 64;
GroupNumber = LB2 * LB1 * innerNum;
```
Multidimensional mode is more suitable for usage scenarios where addresses are continuously loaded/stored, ensuring that lc0 is continuously incremented within a Group.

### 2. Instruction design extension

**2.1 vector instruction assembly renaming**

In the new version, in order to easily distinguish scalar and vector operations, the vector instruction naming in the Tile block is uniformly modified to use "V." as the prefix, and the scalar instruction still uses "L." as the prefix.

The command list is as follows:| Original naming | vector command naming | Remarks | Original naming | vector command naming | Remarks |
|--------|----------------|------|--------|-------------|---------|
| L.ADD,L.SUB,L.AND,L.OR,L.XOR<br>L.SRL,L.SRA,L.SLL<br>L.ADDI,L.SUBI,L.ANDI,L.ORI<br>L.XORI,L.SRLI,L.SRAI,L.SLLI | V.ADD,V.SUB,V.AND,V.OR<br>V.XOR,V.SRL,V.SRA,V.SLL<br>V.ADDI,V.SUBI,V.ANDI,V.ORI,<br>V.XORI,V.SRLI,V.SRAI,V.SLLI | vector: vt/vu/vm/vn<br>scalar: t/u, p | L.LW.ADD,L.LW.AND,L.LW.OR<br>L.LW.XOR,L.LW.MAX,L.LW.MIN<br>L.LD.ADD,L.LD.AND,L.LD.OR<br>L.LD.XOR,L.LD.MAX,L.LD.MIN | V.LW.ADD,V.LW.AND,V.LW.OR<br>V.LW.XOR,V.LW.MAX,V.LW.MIN<br>V.LD.ADD,V.LD.AND,V.LD.OR<br>V.LD.XOR,V.LD.MAX,V.LD.MIN | vector: vt/vu/vm/vn<br>scalar: t/u, p |
| L.CMP.EQ,L.CMP.NE,L.CMP.AND<br>L.CMP.ORL.CMP.LT,L.CMP.GE<br>L.CMP.LTU,L.CMP.GEU,L.CMP .EQI<br>L.CMP.NEI,L.CMP.ANDI,L.CMP.ORI<br>L.CMP.LTI,L.CMP.GEI,L.CMP.LTUI<br>L.CMP.GEUI | V.CMP.EQ,V.CMP.NE,V.CMP.AND<br>V.CMP.ORV.CMP.LT,V.CMP.GE<br>V.CMP.LTU,V.CMP.GEU,V.CMP .EQI<br>V.CMP.NEI,V.CMP.ANDI,V.CMP.ORI<br>V.CMP.LTI,V.CMP.GEI,V.CMP.LTUI<br>V.CMP.GEUI | vector: vt/vu/vm/vn,p<br>scalar: t/u<br>When outputting P, it is vector | L.SW.ADD,L.SW.AND,L.SW.OR<br>L.SW.XOR,L.SW.MAX,L.SW.MIN<br>L.SD.ADD,L.SD.AND,L.SD.OR<br>L.SD.XOR,L.SD.MAX,L.SD.MIN | V.SW.ADD,V.SW.AND,V.SW.OR<br>V.SW.XOR,V.SW.MAXV.SW.MIN<br>V.SD.ADD,V.SD.AND,V.SD.OR<br>V.SD.XOR,V.SD.MAX,V.SD.MIN | Any input to the vector register is vector || L.MUL, L.MADD, L.DIV, L.REM | V.MUL, V.MADD, V.DIV, V.REM | vector: vt/vu/vm/vn<br>scalar: t/u, p | L.FADD,L.FSUB,L.FMUL,L.FDIV<br>L.FMADD,L.FMSUB,L.FNMADD<br>L.FNMSUB | vt/vu/vm/vn<br>scalar: t/u, p |
| L.BXS,L.BXU,L.BIC,L.BIS,L.CTZ,L.CLS<br>L.BCNT,L.REV | V.BXS,V.BXU,V.BIC,V.BIS,V.CTZ,V.CLS<br>V.BCNT,V.REV | vector: vt/vu/vm/vn<br>scalar: t/u, p | L.FEQ,L.FNE,L.FLT,L.FGE,L.FEQU<br>L.FNEUL.FLTU,L.FGEU<br>L.MAX,L.MIN,L.FMAX,L.FMIN | V.FEQ,V.FNE,V.FLT,V.FGE,V.FEQU<br>V.FNEUV.FLTU,V.FGEU<br>V.MAX,V.MIN,V.FMAX,V.FMIN | vector: vt/vu/vm/vn<br>scalar: t/u, p |
| L.CSEL | V.CSEL | vector: vt/vu/vm/vn<br>scalar: t/u, p | L.FCVT,L.FCVTI,L.ICVT,L.ICVTF | V.FCVT,V.FCVTI,V.ICVT,V.ICVTF | vector: vt/vu/vm/vn<br>scalar: t/u, p |
| L.LB,L.LH,L.LW,L.LD,L.LBU,L.LHU<br>L.LWU,L.LBI,L.LHI,L.LWI,L.LDI,L.LBUI<br>L.LHUI,L.LWUIL.LHI.U,L.LWI.U,L.LDI.U<br>L.LHUI.U,L.LWUI.U | V.LB,V.LH,V.LW,V.LD,V.LBU,V.LHU<br>V.LWU,V.LBI,V.LHI,V.LWI,V.LDI,V.LBUI<br>V.LHUI,V.LWUIV.LHI.U,V.LWI.U,V.LDI.U<br>V.LHUI.U,V.LWUI.U | vector: vt/vu/vm/vn<br>scalar: t/u, p | L.FABS,L.FSQRT,L.FRECIP,L.FEXP<br>L.FLN,L.FCLASS | vector: vt/vu/vm/vn<br>scalar: t/u, p || L.SB,L.SH,L.SW,L.SD,L.SH.U,L.SW.U<br>L.SD.U,L.SBI,L.SHI,L.SWI,L.SDI,L.SHI.U<br>L.SWI.U,L.SDI.U | V.SB,V.SH,V.SW,V.SD,V.SH.U,V.SW.U<br>V.SD.U,V.SBI,V.SHI,V.SWI,V.SDI,V.SHI.U<br>V.SWI.U,V.SDI.U | Any input to the vector register is vector | L.RDADD,L.RDAND,L.RDOR<br>L.RDXOR,L.RDFADD,L.RDMAX<br>L.RDMIN,L.RDFMAX,L.RDFMIN | V.RDADD,V.RDAND,V.RDOR<br>V.RDXOR,V.RDFADD,V.RDMAX<br>V.RDMIN,V.RDFMAX,V.RDFMIN | Only vector version |
| L.LB.BRG,L.LH.BRG,L.LW.BRG,L.LD.BRG,<br>L.LBU.BRG,L.LHU.BRG,L.LWU.BRG<br>L.LBI.BRG,L.LHI.BRG,L.LWI.BRG<br>L. LDI.BRG,L.LBUI.BRG,L.LHUI.BRG<br>L.LWUI.BRG,L.LHI.U.BRG,L.LWI.U.BRG<br>L.LDI.U.BRG,L.LHUI.U.BRG,L.LWUI.U.BRG | V.LB.BRG,V.LH.BRG,V.LW.BRG,V.LD.BRG,<br>V.LBU.BRG,V.LHU.BRG,V.LWU.BRG<br>V.LBI.BRG,V.LHI.BRG,V.LWI.BRG<br>V. LDI.BRG,V.LBUI.BRG,V.LHUI.BRG<br>V.LWUI.BRG,V.LHI.U.BRG,V.LWI.U.BRG<br>V.LDI.U.BRG,V.LHUI.U.BRG,V.LWUI.U.BRG | Only version vector | L.SHFL.UP,L.SHFL.DOWN<br>L.SHFL.BFLY,L.SHFL.IDX<br>L.SHFLI.UP,L.SHFLI.DOWN<br>L.SHFLI.BFLY,L.SHFLI.IDX | V.SHFL.UP,V.SHFL.DOWN<br>V.SHFL.BFLY,V.SHFL.IDX<br>V.SHFLI.UP,V.SHFLI.DOWN<br>V.SHFLI.BFLY,V.SHFLI.IDX | vector version only |
| L.SB.BRG,L.SH.BRG,L.SW.BRG,L.SD.BRG<br>L.SH.U.BRG,L.SW.U.BRG,L.SD.U,L.SBI.BRG<br>L.SHI.BRG,L.SWI.BRG,L.SDI.BRG<br>L.SHI.U.BRG,L.SWI.U,L.SDI.U.BRG | V.SB.BRG,V.SH.BRG,V.SW.BRG,V.SD.BRG<br>V.SH.U.BRG,V.SW.U.BRG,V.SD.U,V.SBI.BRG<br>V.SHI.BRG,V.SWI.BRG,V.SDI.BRG<br>V.SHI.U.BRG,V.SWI.U,V.SDI.U.BRG | Only vector version | L.QPUSH,L.QPOP | V.QPUSH,V.QPOP | vector: vt/vu/vm/vn<br>scalar: t/u, p |

Example:
```asm
# ZXTERMZH45QXZ指令
l.add t#1, u#1, ->t
l.add t#1, p, ->p
l.ld [TS, offset], ->u
l.ld [TS, offset], ->p
l.sd t#1, [TO, offset]
l.sd p#1, [TO, offset]
# ZXTERMZH43QXZ指令：
v.add vt#1.uh, vu#1.uh, ->vt.h
v.add t#1, vu#1.uh, ->vt.h
v.sw vt#1.uw, [TO, lc0<<2]
v.ld [TA, lc0<<3], ->vt.d
```

**2.2 Strengthen the definition of continuous Load/Store**In version 0.52.1, in order to simplify the hardware address calculation process and perform address access efficiently. The instruction set provides a Load/Store instruction with continuous addresses. The address of this type of instruction is calculated from three parts: "base address register", "LC0 register offset" and "offset register or immediate offset".

We expect that the "base address register" and "offset register or immediate offset" are invariants, and LC0 is a variable that increases sequentially following lane expansion. In this way, the continuity of memory access addresses within the group is achieved.

The assembly format of some of the instructions:
```asm
v.lw  [srcL.<T>, lc0<<2, srcR.<T>], ->dst.w
v.lwi [srcL.<T>, lc0<<2, imm], ->dst.w
v.sw  srcD.uw, [srcL.<T>, lc0<<2, srcR.<T>]
v.swi srcD.uw, [srcL.<T>, lc0<<2, imm]
v.lw  [srcL.<T>, lc0<<2, srcR.<T>], ->dst.w
v.lwi [srcL.<T>, lc0<<2, imm], ->dst.w
v.sw  srcD.uw, [srcL.<T>, lc0<<2, srcR.<T>]
v.swi srcD.uw, [srcL.<T>, lc0<<2, imm]
```

**2.2.1 Instruction constraints**

In order to ensure the continuity of memory access addresses within a group, on the one hand, the architecture design is required to be divided into groups according to the definition in Section 1.3 above. On the other hand, it is also necessary to add constraints on the use of "base address register SrcL" and "offset register SrcR" for such memory access instructions:

- The base address register of memory access instructions with consecutive addresses must be the scalar register or the Tile register, otherwise an illegal instruction exception will be reported.
- The offset register of memory access instructions with consecutive addresses must be the scalar register, otherwise an illegal instruction exception will be reported.
- If the value of the offset register is calculated from LC1/LC2, then this type of instruction should be ensured to be used in multi-dimensional mode to ensure that LC1 and LC2 remain unchanged within a Group.

Example:
```asm
v.lw  [ri0, lc0<<2, t#1], ->vt.w
v.lwi [TA, lc0<<2, 8],    ->vu.w
v.sw vt#1.uw, [TO, lc0<<2, ri1]
v.swi vu#1.uw, [ri2, lc0<<2, 8]
v.lw  [ri0, lc0<<2, t#1], ->vt.w
v.lwi [TA, lc0<<2, 8],    ->vu.w
v.sw vt#1.uw, [TO, lc0<<2, ri1]
v.swi vu#1.uw, [ri2, lc0<<2, 8]
```

The diagram is as follows:

![](../figs/isa/version/0.54/continuels.png)

**2.2.2 Instruction encoding**

This version has no changes to the encoding of Load/Store instructions with consecutive addresses. The 12th bit of the memory access instruction is the flag bit for continuous address. When the code is 1, the software should ensure that the addresses in each group must be continuous, otherwise the addresses are allowed to be discontinuous.

![](../figs/isa/version/0.54/vload.png)

**2.3 Load/Store bridge command adds a mark with consecutive addresses**

In order to meet the needs of software using Load/Store bridge operations at the same time and providing Load/Store with consecutive addresses, the new version adds a continuous address mark to the Load/Store bridge instruction. Reduce the overhead of hardware address calculations with this flag.

**2.3.1 Assembly format**

Like ordinary Load/Store instructions, Load/Store bridge instructions with consecutive addresses pass a fixed LC0 input as part of the addressing offset in assembly.|Instructions | Assembly format |
|------|--------|
| V.LB.BRG | `v.lb.brg<.local> [SrcL<.ud>, <lc0>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LH.BRG | `v.lh.brg<.local> [SrcL<.ud>, <lc0<<1>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LW.BRG | `v.lw.brg<.local> [SrcL<.ud>, <lc0<<2>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LD.BRG | `v.ld.brg<.local> [SrcL<.ud>, <lc0<<3>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LBU.BRG | `v.lbu.brg<.local> [SrcL<.ud>, <lc0>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LHU.BRG | `v.lhu.brg<.local> [SrcL<.ud>, <lc0<<1>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LWU.BRG | `v.lwu.brg<.local> [SrcL<.ud>, <lc0<<2>, SrcR.<T><<<shamt>], ->Dst.<W>` |
| V.LBI.BRG | `v.lbi.brg<.local> [SrcL<.ud>, <lc0>, simm], ->Dst.<W>` |
| V.LHI.BRG | `v.lhi.brg<.local> [SrcL<.ud>, <lc0<<1>, simm], ->Dst.<W>` |
| V.LWI.BRG | `v.lwi.brg<.local> [SrcL<.ud>, <lc0<<2>, simm], ->Dst.<W>` |
| V.LDI.BRG | `v.ldi.brg<.local> [SrcL<.ud>, <lc0<<3>, simm], ->Dst.<W>` |
| V.LBUI.BRG | `v.lbui.brg<.local> [SrcL<.ud>, <lc0>, simm], ->Dst.<W>` |
| V.LHUI.BRG | `v.lhui.brg<.local> [SrcL<.ud>, <lc0<<1>, simm], ->Dst.<W>` |
| V.LWUI.BRG | `v.lwui.brg<.local> [SrcL<.ud>, <lc0<<2>, simm], ->Dst.<W>` |
| V.LHI.UBRG | `v.lhi.ubrg<.local> [SrcL<.ud>, <lc0<<1>, simm], ->Dst.<W>` |
| V.LWI.UBRG | `v.lwi.ubrg<.local> [SrcL<.ud>, <lc0<<2>, simm], ->Dst.<W>` |
| V.LDI.UBRG | `v.ldi.ubrg<.local> [SrcL<.ud>, <lc0<<3>, simm], ->Dst.<W>` |
| V.LHUI.UBRG | `v.lhui.ubrg<.local> [SrcL<.ud>, <lc0<<1>, simm], ->Dst.<W>` |
| V.LWUI.UBRG | `v.lwui.ubrg<.local> [SrcL<.ud>, <lc0<<2>, simm], ->Dst.<W>` |
| V.SB.BRG | `v.sb.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0>, SrcR.<T>]` |
| V.SH.BRG | `v.sh.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<1>, SrcR.<T><<1]` |
| V.SW.BRG | `v.sw.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<2>, SrcR.<T><<2]` |
| V.SD.BRG | `v.sd.brg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<3>, SrcR.<T><<3]` |
| V.SH.UBRG | `v.sh.ubrg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<1>, SrcR.<T>]` |
| V.SW.UBRG | `v.sw.ubrg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<2>, SrcR.<T>]` |
| V.SD.UBRG | `v.sd.ubrg<.local> SrcD.<T>, [SrcL<.ud>, <lc0<<3>, SrcR.<T>]` |
| V.SBI.BRG | `v.sbi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0>, simm]` |
| V.SHI.BRG | `v.shi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<1>, simm]` |
| V.SWI.BRG | `v.swi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<2>, simm]` |
| V.SDI.BRG | `v.sdi.brg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<3>, simm]` |
| V.SHI.UBRG | `v.shi.ubrg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<1>, simm]` |
| V.SWI.UBRG | `v.swi.ubrg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<2>, simm]` |
| V.SDI.UBRG | `v.sdi.ubrg<.local> SrcL.<T>, [SrcR<.ud>, <lc0<<3>, simm]` |

When using Load/Store bridge instructions with consecutive addresses, you must also ensure that the requirements for continuous Load/Store instructions in 2.2 are met.

**2.3.2 Instruction encoding**

Like ordinary Load/Store instructions, the Load/Store bridge instruction uses the "C" flag bit to indicate whether the addresses are continuous.

![vloadbrg](../figs/isa/version/0.54/vloadbrg.png)

Please see the ISA Encoding Excel document for full instruction encoding.

**2.4 Distinguish between Local/Global access**

In order for the hardware to identify Tile Reg or Global Memory access in advance, there is no need to wait for the address to be calculated before making a judgment, thereby improving performance. In version 0.54, the Load/Store command adds a logo that expresses the Tile Reg access.

The specific modifications are as follows:

- The address is the Load/Store instruction of Tile Register, and the ".local" suffix is added to the assembly.
- The address is the Load/Store instruction of Global Memory, and no additional suffix is ​​added in the assembly. (Default access to shared memory)

Assembly syntax:
```asm
v.loadop<.local>  [baseReg, offset], ->dstReg
v.storeop<.local> dataReg, [baseReg, offset]
v.loadop<.local>  [baseReg, offset], ->dstReg
v.storeop<.local> dataReg, [baseReg, offset]
```
Among them, ".local" is an optional suffix, and the software chooses whether to add the suffix based on whether the access address is a Tile Register.

Note: Software/programmers should ensure that the addresses accessed by instructions are classified correctly. If the address is wrong, the hardware reports exception.In the instruction encoding, a 1bit **L (local)** flag is added. The code is 1 when accessing the Tile Register, otherwise the code is 0. The encoding is as follows:

![localload](../figs/isa/version/0.54/localload.png)

![localstore](../figs/isa/version/0.54/localstore.png)

Only part of the load/store instruction encoding is pasted here. Please see the ISA Encoding Excel document for the full content.

**2.5 Add V.PSEL instruction**

In vector calculations, some lanes may be marked as invalid due to mask control, boundary crossing, or branch masking. How to handle the output values ​​​​of these invalid channels is of great significance for controlling numerical correctness, storage consistency, and subsequent calculation behavior.

In order to enhance the ability to control calculation results, a new Predication Mode (pmode) definition is added to Tileblock instruction, which is used to specify how to handle calculation results of invalid channels. Two pmode mode definitions:

- merging mode: The result of the invalid channel will remain as the original value of the input register, which is suitable for situations where you want to retain the original data without causing mutations.
- zeroing mode: The result of an invalid channel is forced to be written as 0, suitable for scenarios where old values ​​need to be cleared or output initialized.

This mechanism allows developers to clearly control how instructions handle invalid channels based on specific application requirements, avoiding reliance on default behaviors and improving code controllability and portability.

Under the current definition, the instruction calculation result in the invalid lane of the Tile block defaults to the clear mode, that is, the destination register is filled with 0. Therefore, the new version implements the merge mode by adding an L.PSEL instruction. The directive is defined as follows:

**2.5.1 Instruction definition**

Instruction semantics: According to each bit mask in register SrcP, select the value of the left source register or the right source register to be written to the destination register. A mask of 1 selects the left source register SrcL; a mask of 0 selects the right source register SrcR.

Assembly syntax:
```asm
v.psel SrcP, SrcL.<T>, SrcR.<T><.neg>, ->Dst.<W>
v.psel SrcP, SrcL.<T>, SrcR.<T><.neg>, ->Dst.<W>
```

- SrcP can be the P register or the scalar register (each bit in the scalar register is read as a lane condition mask).
- SrcR supports the optional ".neg" parameter, which is used to add one to the bitwise negation of the SrcR operand.

The instructions are encoded as follows:

![psel](../figs/isa/version/0.54/psel.png)

**2.6 Add instruction constraints**

The setret instruction is used in the CAL block or ICALL block to record the return address to the ra register. In the previous design, this instruction could be placed anywhere in body, and the return address was calculated by adding offset to the current TPC.

However, the following problems were found during the implementation of the microarchitecture:

- setret triggers the call_ret prediction address to be pushed into the predictor when the IFU is retrieved.
- If setret is not the first microinstruction in the block, and nuke_flush occurs before the setret instruction, it will cause the call_ret prediction address to be pushed into the predictor repeatedly, and eventually the call_ret prediction function will fail.

![setret](../figs/isa/version/0.54/setret.png)

Therefore, the new version adds the following constraints: **In block instruction of CALL or ICALL type, the setret or c.setret instruction must be placed after BSTART**. Otherwise, the hardware triggers the illegal instruction exception.

**3. System block changes**

In the new version, system block instruction only supports the FALL extension type inter-block jump method, so the codes corresponding to other jump types are deleted. Conditional jumps or function calls in the program can be implemented through the integer scalar block or the floating point scalar block.

32bit encoding:

![sysblock-32](../figs/isa/version/0.54/sysblock-32.png)

48t encoding:

![sysblock-32](../figs/isa/version/0.54/sysblock-48.png)

64bit encoding:

![sysblock-32](../figs/isa/version/0.54/sysblock-64.png)