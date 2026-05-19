# 0.41 version update

Update date: September 29, 2024

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-0.41](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100519244765)

## Version update background

The next key goal of LinxISA is the integrated computing architecture of NPU and GPU, of which the most important instruction extension is SIMTexecution model. Version 0.41 is used to describe the extended implementation of SIMTexecution model based on block instruction.

Unlike CPUs that process vector data through SIMD (Single Instruction Multiple Data), GPUs usually use SIMT. The advantage of SIMT is that developers do not need to work hard to fit the data into the appropriate vector length, and SIMT allows each thread to have different branches. Purely using SIMD cannot execute conditional jump functions in parallel, because conditional jumps will behave differently in different threads based on different input data. This can only be achieved by using SIMT.

Under the LinxISA framework, we need to integrate the NPU and GPU architectures through a set of instruction sets to meet the new isomorphism requirements. Therefore, we introduce a parallel block engine under the existing framework, which can process N body identical block instruction at the same time to achieve the effect of efficient parallel execution of simple loops. We call this block engine SIMTblock instruction.

The schematic diagram of SIMT block execution model is as follows:

![simt](../figs/isa/version/simt.png)

## General description of version update

1. Added SIMTblock instruction definition
    - Add microinstructions in SIMT blocks and uniformly use **64bit length encoding**
    - Define **CSTK and PredM registers** within the SIMT block.
    - **4 groups of relative index registers** are defined in the SIMT block, named T, U, M, N respectively, and each group contains 8 registers.
2. Add BTEXT instruction to indicate the offset distance from header to body in the separation block
3. Added loop.get and loop.set instructions in scalar block
4. Added read-only register LaneNum in system register, used to store the number of parallel lanes of SIMT block engine
5. Modify the assembly syntax of the load/store instructions of the immediate offset class.
6. Introduce **floating point block** instructions and **in-block microinstructions** definitions

## Change details

### SIMTblock instruction definition

Like the traditional scalar block, SIMTblock instruction also uses the BSTART instruction as the starting instruction of the block, and the necessary block description instructions are added to header to supplement the execution control information.

1. **BSTART.SIMT**

Instruction encoding:

![simt.bstart](../figs/isa/version/bstart.simt.png)

Among them:

- block typeBlockType is encoded as 4b0011 to represent the SIMT block, and the **jump type is fixed as Fall** (encoded as 3b001).
- The current version SIMT block is defined as **detached block** with DCP bit 1.

2. **Add body pointer BTEXT instruction**

In order to expand the coding space, SIMTbody uses 64-bit width microinstructions. If these 64-bit instructions are mixed with 32 or 16-bit instructions in one block, the hardware implementation complexity will be higher and the implementation cycle will be longer.
Therefore, this version defines the SIMT block as a separate block, and the BText instruction for indicating the position of body needs to be added to header. This command is used to encode the offset distance from header to body of SIMTblock instruction.

The instructions are encoded as follows:

![btext-0.41](../figs/isa/version/btext-0.41.png)

3. **SIMT BLOCK architectural state**- **Global Status**
    * R0-R23: The SIMT block uses the same first layer architectural registerR0-R23 as the traditional scalarblock instruction.
- **System Status**
    * **LaneNum**: The SIMT block introduces a read-only system registerLaneNum in the first layer architecture, which is used to store the number of parallel Lanes supported by the current hardware. |
    * **LB0, LB1, LB2**: SIMT block uses LB0, LB1, LB2 3 system register as the upper limit of parallel iteration. |
    * LC0, LC1, LC2: The SIMT block uses LC0, LC1, LC2 3 system register for parallel iteration number control. |
- **Intra-block state**
    * **PredM**: A Predicate Mask register is added to the SIMT block to control whether each lane in the SIMT block engine is valid |
    * **CSTK**: Control Stack register, used to store PC and mask when a branch occurs within the SIMT block |
    * **4 sets of relative index registers**: TR1 to TR8, UR1 to UR8, MR1 to MR8, NR1 to NR8. The **register width of this type is not fixed** and can be 8, 16, 32 or 64 bits, which is determined by the register width expressed by the instruction.

Note: The SSRID of LB and LC class system register has been adjusted in this version.

4. **SIMT intra-block microinstructions**

On the one hand, due to the introduction of more private registers in the SIMT block, all optional registers cannot be encoded in 5-bit space in the 32-bit space; on the other hand, the microinstructions in the SIMT block need to indicate the width information of the source and destination registers, and the types of instruction operands have been expanded. For these reasons, an instruction within the SIMT block cannot be encoded using 32bit.

Therefore, in the current version, **microinstructions within the SIMT block uniformly use 64bit encoding length**. This 64-bit long instruction is defined as "the lower bit of a 32-bit standard instruction spliced ​​into a 32-bit instruction LIEXT for expansion." The 32-bit standard instruction can be an instruction in the public coding space or a SIMTblock-private microinstruction.

The Liext (full name: Long Instruction Extend) instruction is used to splice with subsequent basic instructions to form a 64-bit long instruction. The different field segments of this instruction serve as extension bits of the corresponding fields of the base instruction.

The instructions are encoded as follows:

![liext-0.41](../figs/isa/version/liext-0.41.png)

Among them:

- **dest-ext**: This field is used as the extension bit of the instruction's destination register field RegDst.
- **func-ext**: This field is used as the extension bit of the func field in the instruction encoding.
- **Src0-ext**: This field is used as an extension to the first source register field of the instruction.
- **Src1-ext**: This field is used as an extension to the second source register field of the instruction.
- **Src2-ext**: This field is used as an extension to the third source register field of the instruction.

- **Floating point multi-operation instructions**| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| FADD | fadd SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Floating point addition |
| FSUB | fsub SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Floating point subtraction |
| FMUL | fmul SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Floating point multiplication |
| FDIV | fdiv SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Floating point division |
| FMADD | fmadd SrcL.{T}, SrcR.{T}, SrcA.{T}, ->{t,u,m,n}.{w} | Floating point multiply and add |
| FMSUB | fmsub SrcL.{T}, SrcR.{T}, SrcA.{T}, ->{t,u,m,n}.{w} | Floating point multiplication and subtraction |
| FNMADD | fnmadd SrcL.{T}, SrcR.{T}, SrcA.{T}, ->{t,u,m,n}.{w} | Floating point multiplication and addition, negative |
| FNMSUB | fnmsub SrcL.{T}, SrcR.{T}, SrcA.{T}, ->{t,u,m,n}.{w} | Floating point multiplication and subtraction, negative |

- **Floating point unary operation instructions**

| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| FABS | fabs SrcL.{T}, ->{t,u,m,n}.{w} | Absolute value |
| FSQRT | fsqrt SrcL.{T}, ->{t,u,m,n}.{w} | Square root |
| FEXP | fexp SrcL.{T}, ->{t,u,m,n}.{w} | Exponent value with base e |
| FLOG | flog SrcL.{T}, ->{t,u,m,n}.{w} | Base 2 logarithmic value |
| FSIN | fsin SrcL.{T}, ->{t,u,m,n}.{w} | Sine value |
| FCOS | fcos SrcL.{T}, ->{t,u,m,n}.{w} | Cosine value |
| FRECIP | frecip SrcL.{T}, ->{t,u,m,n}.{w} | Find the reciprocal |

- **Floating point type judgment instruction**

| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| FCLASS | fclass SrcL.{T}, ->{t,u,m,n}.{w} | Floating point type judgment |

- **Floating Point Comparison Instructions**| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| FEQ | feq.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Equality comparison (silent comparison) |
| FNE | fne.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Unequal comparison (silent comparison) |
| FLT | flt.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Less than comparison (silent comparison) |
| FGE | fge.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Greater than or equal to comparison (silent comparison) |
| FEQS | feqs.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Equality comparison (sending comparison) |
| FNES | fnes.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Unequal comparison (sending comparison) |
| FLTS | flts.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Less than comparison (sending comparison) |
| FGES | fges.srcT SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Greater than or equal to comparison (sending comparison) |

- **Floating point conditional jump instructions**

| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| B.FEQ | b.feq.srcT SrcL.{T}, SrcR.{T}, label | Equality jump, otherwise execute sequentially |
| B.FNE | b.fne.srcT SrcL.{T}, SrcR.{T}, label | Jump if not equal, otherwise execute sequentially |
| B.FLT | b.flt.srcT SrcL.{T}, SrcR.{T}, label | If less than jump, otherwise execute sequentially |
| B.FGE | b.fge.srcT SrcL.{T}, SrcR.{T}, label | If greater than or equal to, jump, otherwise execute sequentially |

- **data type conversion instruction**

The data type conversion instruction is used to support conversion operations between floating point data formats and from floating point to integer data formats. The instructions are defined in the following table:

| Instructions | Assembly Syntax | Description |
|------|-----------|---------|
| FCVT | fcvt SrcL.{srcT}, ->{t,u,m,n}.{w}.{dstT} | Format conversion between floating point data |
| FCVTI | fcvti SrcL.{srcT}, ->{t,u,m,n}.{w}.{dstT} | Floating point to integer format conversion |
| ICVT | icvt SrcL.{srcT}, ->{t,u,m,n}.{w}.{dstT} | Format conversion between integer data |
| ICVTF | icvtf SrcL.{srcT}, ->{t,u,m,n}.{w}.{dstT} | Integer to floating point format conversion |

- **Maximum and Minimum Value Instructions**| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| MAX | max SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | signed integer maximum value |
| MAXU | maxu SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | unsigned integer maximum value |
| FMAX | fmax SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | Maximum floating point value |
| MIN | min SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | signed integer minimum value |
| MINU | minu SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | unsigned integer minimum value |
| FMIN | fmin SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | Minimum floating point number |

- **scalar operation instructions**

| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| DIV | div SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | Integer signed division |
| DIVU | divide SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | Integer unsigned division |
| REM | rem SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | Integer signed remainder |
| REMU | remu SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | Integer unsigned remainder |

- **Conditional selection instructions**

| Instructions | Assembly Syntax | Instruction Definition
|------|-----------|---------|
| CSEL | CSEL SrcP.{T}, SrcL.{T}, SrcR{T}, ->{t,u,m,n}.{w} | Conditional selection instructions |

- **bit-bit operation instructions**

| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| REV16 | rev16 SrcL.{T}, ->{t,u,m,n}.{w} | Big-endian conversion within every 16 bits |
| REV32 | rev32 SrcL.{T}, ->{t,u,m,n}.{w} | Big-endian conversion within every 32 bits |
| REV64 | rev64 SrcL.{T}, ->{t,u,m,n}.{w} | Big-endian conversion within 64bit |
| CTZ | ctz SrcL.{T}, ->{t,u,m,n}.{w} | The effective bits are from low to high, counting the number of 0s before the first 1 |
| CLZ | clz SrcL.{T}, ->{t,u,m,n}.{w} | The effective bits are from high to low, counting the number of 0s before the first 1 |

- **Memory application and release instructions**

| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| ALLOC | alloc size, ->{t,u,m,n}.{W} | Apply to allocate memory space of a specified size |
| FREE | free SrcL.d, size | Release the memory space where the address in the source register is located |

- **Reduce instruction**

The Reduce instruction is used to summarize the processing results in all Lanes of the hardware and output them to the global register Rd.| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| RDADDU | rdaddu SrcL_v.{T}, =>Rd | Perform an unsigned addition operation on the values of SrcL_v in all lanes, and write the result to the global register Rd |
| RDADDS | rdadds SrcL_v.{T}, =>Rd | Perform signed addition operation on the values of SrcL_v in all lanes, and write the result to the global register Rd |
| RDAND | rdand SrcL_v.{T}, =>Rd | Bitwise AND the values of SrcL_v in all lanes, and the result is written to the global register Rd |
| RDOR | rdor SrcL_v.{T}, =>Rd | Perform bitwise OR on the values of SrcL_v in all lanes, and write the result to the global register Rd |
| RDXOR | rdxor SrcL_v.{T}, =>Rd | Perform bitwise XOR on the values of SrcL_v in all lanes, and write the result to the global register Rd |
| RDFADD | rdfadd SrcL_v.{T}, =>Rd | Add the floating point numbers in SrcL_v in all lanes, and write the result to the global register Rd |

- **Maximum/Minimum Value Comparison Instructions**

| Instructions | Assembly syntax | Instruction definition |
|------|-----------|---------|
| RDMAXU | rdmaxu SrcL_v.{T}, =>Rd | **Unsigned** Compare the values of SrcL.<T> in all lanes and write the maximum value to the global register Rd. |
| RDMAXS | rdmaxs SrcL_v.{T}, =>Rd | **Signed** Compare the values of SrcL.<T> in all lanes and write the maximum value to the global register Rd. |
| RDMINU | rdminu SrcL_v.{T}, =>Rd | **Unsigned** Compare the values of SrcL.<T> in all lanes and write the minimum value to the global register Rd. |
| RDMINS | rdmins SrcL_v.{T}, =>Rd | **Signed** Compare the values of SrcL.<T> in all lanes and write the minimum value to the global register Rd. |
| RDFMAX | Rdfmax SrcL_v.{T}, =>Rd | Compare the floating point numbers in SrcL.<T> in all lanes and write the maximum value to the global register Rd. |
| RDFMIN | Rdfmin SrcL_v.{T}, =>Rd | Compare the floating point numbers in SrcL.<T> in all lanes and write the minimum value to the global register Rd. |

- **PC.PUSH/POP command**

The pc.push and pc.pop instructions are used to save and restore the PC and mask of the re-convergence point when there is a fork in the execution path in different lanes within the SIMT block.

| Instructions | Assembly Syntax | Description |
|------|-----------|---------|
| PC.PUSH | pc.push label | Push the address obtained by adding the offset to the instruction PC and the mask of the current lane into the Control Stack register. |
| PC.POP | pc.pop | Pop the PC and mask from the Control Stack register and jump to the corresponding address and set the mask register. |

- **QPUSH/QPOP command**

| Instructions | Assembly Syntax | Description |
|------|-----------|---------|
| QPUSH | qpush SrcL.{T}, SrcR.{T}, ->{t,u,m,n}.{w} | Push the data in SrcR to the GQM queue specified by SrcL. If the writing is successful, 0 will be output, otherwise 1 will be output to the destination register. |
| QPOP | qpop SrcL.{T}, ->{t,u,m,n}.{w} | Read the data of a specific width in the GQM queue specified by SrcL, and write the result to the destination register. |In addition to SIMT private instructions, some instructions in the public encoding space will be used in the SIMT block, and they are also encoded by splicing a LIEXT instruction before the original 32-bit encoding. The list of common instructions used within the current version of SIMT blocks is as follows:

- **Arithmetic Operation Instructions**

| Command List |
|----------|
| ADD, SUB, AND, OR, XOR, SRL, SRA, SLL |
| ADDI, SUBI, ANDI, ORI, XORI, SRLI, SRAI, SLLI |

- **Comparison Command**

| Command |
|------|
| CMP.EQ, CMP.NE, CMP.AND, CMP.OR, CMP.LT, CMP.GE, CMP.LTU, CMP.GEU |
| CMP.EQI, CMP.NEI, CMP.ANDI, CMP.ORI, CMP.LTI, CMP.GEI, CMP.LTUI, CMP.GEUI |

- **Bit operation instructions**

| Command |
|------|
| BXS, BXU, BIC, BIS |

- **Multiplication Instructions**

| Command |
|------|
| MUL, MULU, MADD |

- **Intra-block jump instructions**

| Command |
|------|
| JR, J |
| B.EQ, B.NE, B.LT, B.GE, B.LTU, B.GEU |

- **system register access command**

| Command |
|------|
| SSRGET, SSRSET |

- **Memory loading load command**

| Command |
|------|
|LB, LH, LW, LD,LBU,LHU, LWU, LBI, LHI, LWI, LDI |
| LBUI, LHUI, LWUI, LHI.U, LWI.U, LDI.U, LHUI.U, LWUI.U |

- **Memory write Store command**

| Command |
|------|
| SB, SH, SW, SD, SH.U, SW.U, SD.U |
| SBI, SHI, SWI, SDI, SHI.U, SWI.U, SDI.U |

- **Long immediate and PC relative addressing instructions**

| Command |
|------|
| ADDTPC, LUI |

## Add microinstructions

In this version, the following microinstructions are added to the basic instruction set to set the loop register.

| Instructions | Assembly Syntax | Description |
|------|-----------|------|
| LOOP.GET | loop.get LoopReg, ->{t,u,m,n}.{w} | Read the loop register value to the block-private register |
| LOOP.SET | loop.set SrcL, uimm, => LoopReg | Set the result of register SrcL plus immediate uimm to the loop register |

![loopgetset-0.41](../figs/isa/version/loopgetset-0.41.png)

## Load/store instruction modification

In order to distinguish the immediate address offset scaled and unscaled addressing modes of the load/store-imm instruction, this version makes the following modifications to this type of instruction:

- Added constraints on immediate offset in load/store instruction assembly of scaled and unscaled classes.
- Modify the expression form of immediate offset in instruction encoding to: simm12 or simm7. Among them, "simm" represents a signed immediate offset, and the following number represents the number of bits.| load command | assembly syntax | remarks |
|------|-----------|----------|
| LBI | lbi [SrcL, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm12 is encoded as simm |
| LHI | lhi [SrcL, simm], {->t, ->u, =>Rd} | simm must be a multiple of 2, simm12 is encoded as simm/2 |
| LWI | lwi [SrcL, simm], {->t, ->u, =>Rd} | simm must be a multiple of 4, simm12 is encoded as simm/4 |
| LDI | ldi [SrcL, simm], {->t, ->u, =>Rd} | simm must be a multiple of 8, simm12 is encoded as simm/8 |
| LBUI | lbui [SrcL, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm12 is encoded as simm |
| LHUI | lhui [SrcL, simm], {->t, ->u, =>Rd} | simm must be a multiple of 2, simm12 is encoded as simm/2 |
| LWUI | lwui [SrcL, simm], {->t, ->u, =>Rd} | simm must be a multiple of 4, simm12 is encoded as simm/4 |
| LHI.U | lhi.u [SrcL, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm12 is encoded as simm |
| LWI.U | lwi.u [SrcL, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm12 is encoded as simm |
| LDI.U | ldi.u [SrcL, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm12 is encoded as simm |
| LHUI.U | lhui.u [SrcL, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm12 is encoded as simm |
| LWUI.U | lwui.u [SrcL, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm12 is encoded as simm |

The memory access address of the above load instruction is: `address = SrcL + simm`.

The instructions are encoded as follows:

![load-0.41](../figs/isa/version/load-0.41.png)

| store command | Assembly syntax | Remarks |
|------|-----------|----------|
| SBI | sbi SrcL, [SrcR, simm] | simm is a multiple of 1, simm12 is encoded as simm |
| SHI | shi SrcL, [SrcR, simm] | simm must be a multiple of 2, simm12 is encoded as simm/2 |
| SWI | swi SrcL, [SrcR, simm] | simm must be a multiple of 4, simm12 is encoded as simm/4 |
| SDI | sdi SrcL, [SrcR, simm] | simm must be a multiple of 8, simm12 is encoded as simm/8 |
| SHI.U | shi.u SrcL, [SrcR, simm] | simm is a multiple of 1, simm12 is encoded as simm |
| SWI.U | swi.u SrcL, [SrcR, simm] | simm is a multiple of 1, simm12 is encoded as simm |
| SDI.U | sdi.u SrcL, [SrcR, simm] | simm is a multiple of 1, simm12 is encoded as simm |

The instructions are encoded as follows:

![store-0.41](../figs/isa/version/store-0.41.png)| store command | Assembly syntax | Remarks |
|------|-----------|----------|
| SBI.A | sbi.a SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm7 is encoded as simm |
| SHI.A | shi.a SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm must be a multiple of 2, simm7 is encoded as simm/2 |
| SWI.A | swi.a SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm must be a multiple of 4, simm7 is encoded as simm/4 |
| SDI.A | sdi.a SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm must be a multiple of 8, simm7 is encoded as simm/8 |
| SHI.UA | shi.ua SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm7 is encoded as simm |
| SWI.UA | swi.ua SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm7 is encoded as simm |
| SDI.UA | sdi.ua SrcL, [SrcR, simm], {->t, ->u, =>Rd} | simm is a multiple of 1, simm7 is encoded as simm |

The instructions are encoded as follows:

![store1-0.41](../figs/isa/version/store1-0.41.png)

The memory access address of the above store instruction is: `address = Srcr + simm`.

## Introducing floating point blocks and floating point instructions

In order to further optimize the amount of program code and reduce the expansion of Codesize, this version incorporates the design of the floating point block and adds related floating point instructions.

The characteristics of the floating point block are as follows:

- The starting instruction of the floating point block is BSTART, which also supports 32-bit and compressed version encoding.
- The floating point block does not support the split block form and is identified by ".fp" in assembly.
- The definition of registers within the floating point block is the same as that of the scalar block: **4 T + 4 U registers**.

BSTART.fp encoding (32bit)

![fp-0.41](../figs/isa/version/fp-0.41.png)

C.BSTART.fp encoding (16bit)

![c.fp-0.41](../figs/isa/version/c.fp-0.41.png)

Floating point block instruction centrally defines the following instructions.

- Division remainder instruction
- Bit manipulation instructions
- Maximum and minimum instructions
- Conditional selection instructions
- Floating point instructions
- data type conversion instructions

Among them:

Floating point instructions support 4 types of floating point data type: 8bitlow-precision floating-point number, 16bit half-precision floating point number, 32bit single-precision floating point number and 64bit double-precision floating point number.

The assembly format of floating point instructions is (taking fadd as an example): `fadd.{T} SrcL, SrcR, {->t, ->u, =>Rd}`

- **{T}**: refers to the operand type of the floating point instruction, encoded in the "SrcType" field, the encoding method is shown in the following table:

![fadd-0.41](../figs/isa/version/fadd-0.41.png)

| SrcType | Assembly flag | Explanation |
|------|-----------|----------|
| 00 | fd | The operand is 64-bit double-precision floating point data |
| 01 | fs | The operand is 32-bit single-precision floating point data |
| 10 | fh | The operand is 16-bit half-precision floating point data |
| 11 | fb | The operand is 8bitlow-precision floating-point type data |

The assembly format of the data format conversion instruction cvt is: `cvt.srcT2dstT SrcL, {->t, ->u, =>Rd}`

- srcT represents the input data format, encoded in the "SrcType" field.
- dstT represents the converted data format, encoded in the "DstType" field.

The instructions are encoded as follows:![fpcvt-0.41](../figs/isa/version/fpcvt-0.41.png)