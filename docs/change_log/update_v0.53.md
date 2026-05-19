# 0.53 version update

Update date: August 4, 2025

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-0.53.2](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:101071672597)

## 1. Update background description

With the rapid development of artificial intelligence, especially large-model reasoning scenarios, the demand for computing resources is increasing day by day. AI chip architecture is facing multiple challenges such as computing power density, energy efficiency ratio, and diversified accuracy support. As a block-level instruction set for optimized design of AI chips, LinxISA needs to continue to adapt to emerging computing needs while maintaining efficient programmability.

The update background of this version 0.53 mainly includes the following three aspects:

1. **Increased demand for low-precision computing support for large model inference**: Current mainstream large model inference scenarios (such as LLM, CV model deployment) widely use low-bit precision data formats such as INT4, FP4, and FP6 to significantly compress the model volume and reduce storage bandwidth and power consumption. In order to adapt to this trend, LinxISA needs to expand its expression and operation support for a variety of non-standard low-precision data formats.
2. **Block-level execution model has higher requirements for flexibility and efficiency**: In actual compilation and execution, the instruction model of the original Tile block has problems such as the rigidity of block structure restrictions, high ICache pressure, and difficulty in instruction reuse, making it difficult to support high-density parallel instruction fusion and more complex data flow graph scheduling. Therefore, it is necessary to decouple block execution semantics and structure to improve scheduling freedom and hardware execution efficiency.
3. **AI computing core instruction requirements continue to increase**: As more and more matrix micro-kernels, multi-channel fusion, mixed-precision multiplication and addition, non-linear activation approximation (such as LUT) and other operations appear in large model inference, higher expression ability requirements are put forward for ISA. The instruction set needs to support:
    - Composable matrix operation process (calculation + quantification + writing)
    - Flexible preprocessing (such as Merge, Saturate, Round)
    - Structural parallel operations such as dot product (dot)

## 2. Summary of updated content

Therefore, LinxISA 0.53.0 has made the following directional adjustments in design:

- Introducing new parallel block execution model (multi-block fusion, formal parameter support)
- Extended support for FP4, INT4, and FP6 data formats and matrix operations and conversion instructions
- Streamline uncommonly used complex function instructions (such as sin, cos, log) and focus on high-frequency scenarios
- Optimize the expression of register release information| Category | Matter | Description |
|------|-------|--------|
| **Changes in separated block execution model** | 1. The index global register within the block changes from actual parameters to formal parameters | Reduce the icache footprint pressure of vector PE and enable body merging of multiple blocks |
| **Microinstruction changes within the parallel block** | 1. Data format conversion instruction extension | In order to support applications in a wider range of AI inference and edge computing scenarios |
| | 2. Streamline instructions in parallel blocks | Delete complex operations such as sin, cos, log, etc. |
| | 3. Delete the bf16 and flb type operands of general floating point calculation instructions | Special precision floating point numbers are expressed by specifying opcode |
| | 4. The kill information of the vector register is changed to reuse | In most scenarios, registers are used once, so registers used multiple times are marked with reuse instead |
| **Data block instruction modification** | 1. The kill information of Tile Register is changed to reuse | In most scenarios, registers are used once, so registers used multiple times are marked as reuse instead |
| | 2. The data move instruction adds a relative index barrier | Used to solve the problem of out-of-order execution between COPYIN and COPYOUT being unable to express data dependencies. |
| | 3. Revision of matrix operation instructions | Only output to ACC is allowed |
| | 4. Delete the result matrix operation instructions with transpose | MAMULBT, MAMULBACT and MAMULB.ACCT. |
| | 5. Added ACCCVT instruction | Used for FIXPIPE processing in the process of moving data from ACC register to T/U/M/N register. |
| | 6. Added TCVT instruction | Used to convert the layout and element type of data in the T/U/M/N registers. |
| | 7. B.ARG instruction adds SrcType field | Instruction design to adapt to TCVT |
| | 8. Simplified implementation of TCOPY instruction | Only used for copying from Tile register to Tile register in scenarios without data format conversion |
| | 9. TCOPYIN | Name changed to TLOAD, and support data layout transformation |
| | 10. TCOPYOUT | Name changed to TSTORE and support data layout transformation |
| | 11. B. ARG instruction adds PadValue field | Instruction design adapted to TLOAD |

## 3. Update details

### 1. Change the separated block to formal parameter index global register

The implementation logic for body is the same, but the separate blocks of global registers used are different. If the global register used in body can be made into a formal parameter, then this body can be multiplexed by multiple block instruction, and then the header of multiple block instruction can be called by passing different actual parameters. This method can enable body merging of multiple blocks, effectively reducing PE's icache fetch pressure. Therefore, in the new version, we propose a definition of global registers indexed through formal parameters within the block.Example of detached blocks defined in previous versions:
```asm
BSTART.PAR MCALL .L1_body <Row:64, Col:32> [a1, a2, s0], ->T<256B>
BSTART.PAR MCALL .L2_body <Row:32, Col:32> [a3, a4, a5], ->T<128B>
...
.L1_body:
    l.madd    lc0.uh, a1.uh, lc1.uh,   ->vu.w
    l.lw      [a2.sd, vu#1.sw<<2],     ->vt.w
    l.madd    lc1.uh, s0.uh, lc0.uh,   ->vu.w
    l.sw      vt#1.sw, [to.ud, vu#1.sw<<2]
    bstop
.L2_body:
    l.madd    lc0.uh, a3.uh, lc1.uh,   ->vu.w
    l.lw      [a4.sd, vu#1.sw<<2],     ->vt.w
    l.madd    lc1.uh, a5.uh, lc0.uh,   ->vu.w
    l.sw      vt#1.sw, [to.ud, vu#1.sw<<2]
bstop
```
In previous versions, even if the body execution logic of the two blocks was the same, because the global registers used by the instructions were different, two body still needed to be defined, occupying two memory spaces.

New version of detached block example:
```asm
BSTART.PAR MCALL .L1_body <Row:64, Col:32> [a1, a2, s0], ->T<256B>
BSTART.PAR MCALL .L1_body <Row:32, Col:32> [a3, a4, a5], ->T<128B>
...
.L1_body:
    l.madd    lc0.uh, ri0.uh, lc1.uh, ->vu.w      // ri0映射到ZXTERMZH32QXZ第1个输入GPR
    l.lw      [ri1.sd, vu#1.sw<<2],   ->vt.w      // ri1映射到ZXTERMZH32QXZ第2个输入GPR
    l.madd    lc1.uh, ri2.uh, lc0.uh, ->vu.w      // ri2映射到ZXTERMZH32QXZ第3个输入GPR
    l.sw      vt#1.sw, [to.ud, vu#1.sw<<2]
    bstop
```

In the new version, we require the use of formal parameters in the separated block body to index global registers, such as "ri0, ri1, ri2" in the above code. In this way, the two MCALL blocks above can use the same body, and flexibly specify which GPRs to enter as needed.

- When the first MCALL is executed, ri0 is mapped to a1, ri1 is mapped to a2, and ri2 is mapped to s0.
- When the second MCALL is executed, ri0 is mapped to a3, ri1 is mapped to a4, and ri2 is mapped to a5.

Through this implementation method, the original two body can be merged into one to reduce the PE icache fetch pressure.

In the new version, we have defined 16 formal parameter registers, including 12 inputs and 4 outputs:

- The 12 input registers are named RI0-RI11. (RI – Register Input)
- The 4 output registers are named RO0-RO3 respectively. (RO – Register Output)

Example:
```asm
  BSTART.PAR MCALL .L1_body <Row:64, Col:32> [a1, a2, a1], ->T<256B>                  ；允许输入GPR重复
  BSTART.PAR MCALL .L3_body <Row:64, Col:32> [a1, a2, a1], ->T<256B> [s0, s0, s1]    ；不允许输出GPR重复
```
The register index encoding is modified as follows:

![formal-reg](../figs/isa/version/0.53/formal-reg.png){ width="800" }

At the same time, in order to adapt to the above modifications, the index coding of the zero register by the instructions in the parallel block has also been updated. The coding modification is as follows:
 
![zero-reg](../figs/isa/version/0.53/zero.png){ width="800" }

### 2. Modification of data format conversion instructions

In order to support the application of LinxISA in a wider range of AI inference and edge computing scenarios, especially the ability to deploy large models in resource-constrained environments, version 0.53 has systematically enhanced data format support and conversion instructions as well as its special decoding method.

2.1 Supported formats

In the previous version, LinxISA already supported the following mainstream data formats:

| Format name | Format description |
|---------|-------------|
| FP64 | 64bit double precision floating point (e11m52) |
| FP32 | 32bit single precision floating point number (e8m23) |
| FP16 | 16bit half-precision floating point number (e5m10) |
| FP8 | 8bit low-precision floating-point number (e4m3) |
| BF16 | 16bit half-precision floating point number (e8m7) |
| FP8 | 8bit low-precision floating-point number (e5m2) |
| S64/32/16/8 | 64/32/16/8 bit signed integer |
| U64/32/16/8 | 64/32/16/8bit unsigned integer |

However, as inference models become increasingly larger, there is an increasingly urgent need to further compress model storage and reduce bandwidth pressure. To this end, the new version adds the following content:

| Format name | Bit width | Structure | Description |
|---------|-------|-----|-----------|
| TF32 | 32b | e8m10 | High-speed training format |
| HF32 | 32b | e8m11 | High dynamic range format |
| HiF8 | 8b | vendor-specific low-precision data format | Specific model compression optimization |
| SF8 | 8b | e8m0 | Dynamic range encoding, sparse representation |
| FP6 | 6b | e3m2 / e2m3 | Extremely compressed floating point numbers |
| FP4 | 4b | e2m1 / e1m2 | Super low-precision floating-point number |
| HiF4 | 4b | vendor-specific low-precision data format | Specific model compression optimization |
| S/U4 | 4b | Signed/unsigned integer | Commonly used for edge reasoning |For non-standard data formats, no special calculation instructions are provided. You can use the conversion command (Convert) to convert the non-standard data format into a standard format, perform calculations, and then convert it back to the original format.

2.3 Data format conversion instruction type

Linx supports the following four types of format conversion instructions, all of which support low-precision formats:

- FCVT: floating point to floating point: `l.fcvt.{st2dt} SrcL.<T>, ->Dst.<W>`
- FCVTI: floating point to integer: `l.fcvti.{st2dt} SrcL.<T>, ->Dst.<W>`
- ICVTF: integer to floating point: `l.icvtf.{st2dt} SrcL.<T>, ->Dst.<W>`
- ICVT: integer to integer: `l.icvt.{st2dt} SrcL.<T>, ->Dst.<W>`

Assembly example:
```asm
    l.fcvt.f162f32 vt#1.fh, ->vt.w
    l.fcvti.f322s8 vt#2.fs, ->vt.b
    l.icvtf.s162f8 vu#3.sh, ->vt.b
    l.icvt.s322s4 vu#4.sw, ->vt.b
```

2.4 Instruction encoding update

- The SrcType and DstType fields have been expanded in the instruction encoding to support all new formats.
- The function fields of L.ICVT and L.ICVTF have been updated.

The instructions are encoded as follows:
 
![cvt](../figs/isa/version/0.53/cvt.png){ width="800" }

2.5 Conversion example

| Operation target | Assembly example |
|----------|-------------|
| FP32 → FP8 | `l.fcvt.f322f8 vt#1.fs, ->vt.b` |
| FP8 → S8 | `l.fcvti.f82s8 vt#2.fb, ->vt.b` |
| S8 → FP16 | `l.icvtf.s82f16 vt#3.sb, ->vt.h` |
| S32 → S4 | `l.icvt.s322s4 vt#4.sw, ->vt.b` |

### 3. Remove variant floating point calculations

The current version deletes variant floating point calculations, including BF16, FP8 (E5M3) and other formats.

![removebf16](../figs/isa/version/0.53/removebf16.png){ width="800" }

This version does not support floating point calculations in variant data formats, but provides the Convert instruction. Convert variant data format to standard data format for calculation.

### 4. Streamlining instructions in parallel blocks

After upgrading to version 0.5, the parallel block supports instruction mixing of different lengths. Address calculation and system register access operations can use the 32bit version, so the 64bit version is removed. On the other hand, the hardware implementation of operation instructions such as sine, cosine and logarithm is more difficult and can be implemented through other instruction combinations, so it is deleted.

The list of deletion instructions is as follows:

| Classification | Instructions |
|--------------------|------------------|
| Long immediate load/address calculation | l.addtpc, l.lui |
| system register access | l.ssrget, l.ssrset |
| Complex calculation class | l.fsin, l.fcos, l.flogb |

The delete command is encoded as follows:
 
![const](../figs/isa/version/0.53/const.png){ width="800" }

![ssrget](../figs/isa/version/0.53/ssrget.png){ width="800" }

![fsin](../figs/isa/version/0.53/fsin.png){ width="800" }

### 5. Change the kill information in the vector register to reuse information

In the previous version, in order to improve register usage efficiency, the software can actively add ".kill" information to the vector register in the parallel block to indicate that the register is used for the last time and can be released after use.

The new version is modified to specify that the register will still be used by adding ".reuse" information and is not allowed to be released temporarily. For the last used register, specify that the register can be released after use by not adding ".reuse".

For example:
```asm
    l.add vt#1.sw, vt#2.reuse.sw, ->vt.w     # 本指令提交后，不允许硬件释放掉vt#2寄存器。
    l.ldi [vu#4.ud, 8],           ->vt.d      # 本指令提交后，允许硬件释放掉vu#4寄存器。
```

Things to note:- All instructions that support reading the vector register support actively releasing the vector register read by this instruction.
- When it is uncertain whether subsequent instructions use this register, the reuse flag needs to be added.
- The scalar register does not need to be marked with reuse information.
- After the vector register is released, if there is a subsequent instruction to read the register, the hardware should generate exception. That is, only the last used register can be actively released.

### 6.The kill information of Tile Register is changed to reuse information.

In order to improve the utilization of Tile Register, the previous version provided the definition of actively releasing the Tile registers read by this block for the parallel block instruction, that is, adding kill information to the registers that are no longer used.

In this version, we modified it to use ".reuse" information to specify which registers will still be used and do not allow hardware release. The assembly format is as follows:
```asm
分离块：TileOP body_label, <LB0:Arg0, LB1:Arg1, LB2:Arg2> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, [BGetList], ->DstTileType<TileSize>, [BSetList]
ZXTERMZH36QXZ：TileOP <Row:Arg0, Col:Arg1, Dep:Arg2, DataType> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, [BGetList], ->DstTileType<TileSize>, [BSetList]
```
Example:
```
  TADD     <Row: 64, Col: 64, FP16> T#7.reuse, T#2, ->T<32KB>     ; 本指令提交后T#2允许释放，T#7不允许。
  TCOPYOUT <Row: 64, Col: 64, FP32> U#4.reuse, [a0]                ; 本指令提交后，U#4不允许释放
```
The information about whether the Tile Register is retained (reuse) is encoded in the B.IOT or B.IOTI instructions. The updated definitions of these two instructions are as follows:

Assembly format:
```asm
  B.IOT  [SrcTile0<.reuse>, SrcTile1<.reuse>], group={0,1}, ->DstTile<RegSrc>    # 通过寄存器RegSrc设置输出Tile的大小
  B.IOTI [SrcTile0<.reuse>, SrcTile1<.reuse>], group={0,1}, ->DstTile<Size>      # 通过立即数Size设置输出Tile的大小
```

Encoding format:

![biot](../figs/isa/version/0.53/biot.png){ width="800" }

The instruction encoding method is modified as follows:

- The S0K flag is modified to S0R (Reuse Source0): This flag is used to indicate whether SrcTile0 will be retained after this instruction is submitted. When coded as 1, it means that it is retained and no release is allowed; when coded as 0, it is allowed to be released.
- The S1K flag is modified to S1R (Reuse Source1): This flag is used to indicate whether SrcTile1 will be retained after this instruction is submitted. When coded as 1, it means that it is retained and no release is allowed; when coded as 0, it is allowed to be released.
- The DT bit and the DstTile field are jointly encoded to form a 3-bit output register field.

| DT:DstTile | Encoding | Explanation |
|-------------|---------|----------|
| 3b000 | Output to T register queue |
| 3b001 | Output to U register queue |
| 3b010 | Output to M register queue |
| 3b011 | Output to N register queue |
| 3b100 | Output to ACC register queue |
| 3b101 – 3b110 | Reserved |
| 3b111 | Invalid output |

### 7. block instruction increases relative index barrier

In the previous design, if data movement instructions such as TCOPYIN and TCOPYOUT read and write the same memory space, but use different global registers to transfer the first memory address, the hardware implementation cannot determine the dependency relationship between the two instructions in advance. At this time, if they are executed out of order, execution errors will occur. For example:

```asm
  TADD T#1, U#1, ->T<8KB>
  TCOPYOUT  T#1, [a2]             ;将tile寄存器内的数据搬移到a2指定的地址内存中
  TCOPYIN   [a1]，->T<4KB>        ;将a1指定的地址内存中的数据搬移到tile寄存器中
  ...
```

If the same first memory address is stored in a2 and a1, TCOPYIN should wait for TCOPYOUT to complete before executing.

Therefore, in the new version, we add a barrier mechanism to indicate the dependencies between data movement instructions. Specifically, D (dependency) information is added to the instruction.

```asm
  MCALL label, <LB0:Arg0, LB1:Arg1, LB2:Arg2> SrcTile0, SrcTile1, SrcTile2, [BGetList], DepSrc, ->DstTileType<TileSize>, [BSetList], DepDst
```

Among them:

- DepSrc expresses dependence on pre-order instructions, and can specify dependence on instructions with a pre-order D index distance of 1 to 8. For example, D#1 means that it must wait for the latest instruction written to D to be submitted before execution.
- DepDst expresses the barrier to subsequent instructions, which is expressed as D in actual assembly.

At the same time, a new instruction B.IOD (Block Input and Output Dependency) needs to be added to encode dependency information.

Assembly format: `B.IOD DepSrc, ->DepDst`

Instruction encoding:

![biod](../figs/isa/version/0.53/biod.png){ width="800" }

The DepSrc and DepDst fields are encoded as shown in the following dependency table:| input/output encoding | DepSrc | DepDst |
|-------------|---------|----------|
| 5'b00000 | No dependencies | No output |
| 5'b00001 | D#1 | D |
| 5'b00010 | D#2 | reserve |
| 5'b00011 | D#3 | reserve |
| 5'b00100 | D#4 | reserve |
| 5'b00101 | D#5 | reserve |
| 5'b00110 | D#6 | reserve |
| 5'b00111 | D#7 | reserve |
| 5'b01000 | D#8 | reserve |
| others | reserve | reserve |

template blockTCOPYIN and TCOPYOUT can be expressed as:

```asm
TCOPYIN  <Row:Arg0, Col:Arg1, Dep:Arg2, DataType>, [RegSrc],  DepSrc,          -> DstTileType<TileSize>, DepDst
TCOPYOUT <Row:Arg0, Col:Arg1, Dep:Arg2, DataType>, SrcTile, [RegSrc], DepSrc, -> DstDep
```

Example:
```asm
TCOPYOUT t#1, [a2], ->d            ; I0
TCOPYIN [a3]，d#1,  ->T            ; I1, 等待I0提交后执行
TCOPYOUT t#1, [a4], ->d            ; I2
TCOPYIN [a5]，d#2,  ->T            ; I3, 等待I0提交后执行
TCOPYIN [a1]，d#1,  ->T, d         ; I4, 等待I2提交后执行
TCOPYOUT t#1, [a0], d#1            ; I5, 等待I4提交后执行
```

- Submit means that Tcopyout writes all the data to memory.
- TCopyout writes to memory in order, and the hardware memory model ensures that TCopyout will not execute out of order. Therefore, TCopyin D#1 relies on the pre-order Copyout, which means that execution starts after all copyouts in the pre-order copyin are written to the memory and submitted (Note: written to SCB).

### 8. Supplementary definition of matrix operation instructions

8.1 Revisions to existing matrix operation instructions

- In order to simplify hardware implementation, in the new version, the results of matrix operation instructions are only allowed to be output to the ACC register, and are not supported to be directly written to Tile registers such as T/U/M/N.
- The data format in ACC is **fixed to FP32 or INT32**, and the storage fractal format is **Large N Small Z**, **The size of Small Z is 1024Byte**.
- To ensure design uniformity, matrix operation instructions no longer support storage transposition of the result matrix. Then add an ACCCVT instruction to export data from the ACC register to T/U/M/N, etc., while supporting FixPipe processing.

After the above modifications, the original MAMULB, MAMULBAC, and MAMULB.ACC instructions are retained, and the three instructions MAMULBT, MAMULBACT, and MAMULB.ACCT** that transpose the result matrix are deleted.

| Opcode | Function | TileOP | Description |
|---------|----------|-----------|----------|
| **2-CUBE** | 0 | MAMULB | Matrix multiplication: A matrix multiplies B matrix, and the result matrix is written to the ACC register |
| | 1 | MAMULBAC | Matrix multiplication and addition: A matrix multiplies B matrix, adds C matrix, and the result matrix is written to the ACC register |
| | 2 | MAMULB.ACC | Matrix multiplication and accumulation: A matrix multiplies B matrix, adds ACC matrix, and the result matrix is written to the ACC register |

1) MAMULB

Assembly format: `MAMULB <M:Arg0, N:Arg1, K:Arg2, DataType> SrcTile0<.reuse>, SrcTile1<.reuse>, ->ACC<TileSize>`
This template block is split into the following instructions for encoding:
```asm
    BSTART.PAR MAMULB, DataType
    B.DIM  reg, imm,   ->M
    B.DIM  reg, imm,   ->N
    B.DIM  reg, imm,   ->K
    B.IOT  [SrcTile0<.reuse>, SrcTile1<.reuse>], group=0, ->ACC<TileSize>
```

2) MAMULBAC

Assembly format: `MAMULBAC <M:Arg0, N:Arg1, K:Arg2, DataType> SrcTile0<.reuse>, SrcTile1<.reuse>, SrcTile2<.reuse>, ->ACC<TileSize>`
This template block is split into the following instructions for encoding:
```asm
    BSTART.PAR MAMULBAC, DataType
    B.DIM  reg, imm,   ->M
    B.DIM  reg, imm,   ->N
    B.DIM  reg, imm,   ->K
    B.IOT  [SrcTile0<.reuse>, SrcTile1<.reuse>], group=0, ->ACC<TileSize>
    B.IOT  [SrcTile2<.reuse>], group=1
```
3) MAMULB.ACC

Assembly format: `MAMULB.ACC <M:Arg0, N:Arg1, K:Arg2, DataType> SrcTile0<.reuse>, SrcTile1<.reuse>, ACC#1, ->ACC<TileSize>`
This template block is split into the following instructions for encoding:
```asm
    BSTART.PAR MAMULB.ACC, DataType
    B.DIM  reg, imm,   ->M
    B.DIM  reg, imm,   ->N
    B.DIM  reg, imm,   ->K
    B.IOT  [SrcTile0<.reuse>, SrcTile1<.reuse>], group=0, ->ACC<TileSize>
```

8.2 Matrix operations support low-precision data formats

In this version, the instruction set reserves 3 pieces of data block instruction (TileOp) for matrix multiplication or multiplication and accumulation, and supports the following data formats:

Therefore, in the new version, we have added more low-precision data type data support for matrix operation instructions, including INT4 and FP4.

Example: `MAMULB <M:128, N:32, K:64, S4> T#1, U#1, ->ACC<64KB>`This matrix multiplication instruction is split into the following instructions for encoding:
```asm
    BSTART.PAR MAMULB, S4
    B.DIM  zero, 128,   ->M
    B.DIM  zero, 32,    ->N
    B.DIM  zero, 64,    ->K
    B.IOTI  [T#1, U#1], ->T<64KB>
```
The element data type is encoded through the DataType field of the BSTART.PAR instruction, so the new version has adjusted the encoding method of this field. The modified definition is as follows:

![bstart.par](../figs/isa/version/0.53/bstart.par.png){ width="800" }

| Encoding | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| DataType | FP64 | FP32 | TF32 | HF32 | FP16 | BF16 | HiF8 | e4m3 | e5m2 | e3m2 | e2m3 | e2m1 | e1m2 | e8m0 | HiF4 | reserve |
| Coding | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 |
| DataType | S64 | S32 | S16 | S8 | S4 | reserve | reserve | reserve | U64 | U32 | U16 | U8 | U4 | reserve | reserve | reserve |

8.3 Storage format of CUBE input

In the hardware implementation based on LinxISA, the input of the CUBE operation unit supports the following storage layout. Before the software performs matrix operations, it should ensure that the input must be arranged according to the following layout, otherwise the execution result will be unknown.

- Matrix A: adopts a storage layout of large N and small z.
- Matrix B: adopts a storage layout of large Z and small n.
- Matrix C: adopts a storage layout of large Z and small z.

The input diagram is as follows:

![layout](../figs/isa/version/0.53/layout.png){ width="900" }

Among them, both matrix A and matrix C must be stored in a layout of **large N and small z**, and matrix B is stored in a layout of **large Z and small n**.

Assume that S0 and K0 are the number of bytes and the number of elements of the K-dimensional fractal size respectively. Different hardware implementations have different sizes of S0 (S0 uses 32Byte by default, corresponding to a fractal size of 512Byte). Then:

- The fractal matrix size of matrix A is `16 x K0`.
- The fractal matrix size of matrix B is `K0 x 16`.
- The fractal matrix size of matrix C is `16 x 16`.

K0 can be calculated by the following formula: `K0 = S0 / sizeof(DataType)`; # DataType represents the element data type

When the input is arranged according to the above storage layout, the default output format is large N and small z. If you want to change the storage layout of the result matrix to another format for subsequent instruction operations, you can use the TCVT instruction to change the storage layout and write the data to the T, U, M, and N registers.

### 9.ACCCVT data movement and accompanying processing support

In order to enhance LinxISA's support for operations such as data conversion and activation/quantization in the post-processing path, version 0.53 adds the ACCCVT instruction (AccTile Convert). This instruction is used to move the result of matrix multiplication calculation from the ACC register to an external Tile register (such as T/U/M/N), and integrates quantization, activation, element-by-element operations and other on-path processing capabilities in the moving process.

9.1 Hardware path and execution mechanism

The original intention of the ACCCVT instruction is to solve the performance bottleneck problem of "the matrix multiplication result still needs to perform a series of format conversion and processing before being written to the Tile Register".In the Linx architecture, the calculation results of the matrix multiplication unit CUBE Core are first written to the internal accumulation register ACC. On the transportation path from ACC to Tile Register, a programmable fixed function processing pipeline (FixPipe) is specially set up, that is, the accompanying processing path.

FixPipe is a micro-pipeline composed of multiple tightly coupled hardware modules connected in series, supporting the following path-dependent computing capabilities:

* Activation function unit (ReLU, ClipReLU)
* Quantization module (supports INT4/INT8, fixed-point scale/zp)
* Element-level calculation unit (Add, Mul, etc.)
* Sparse data filtering and compression unit
* Output bit mask control unit

These modules are enabled on demand by the `ACCCVT` instruction through the `B.ARG` encoding. During the process of data output from the ACC to the Tile register, the corresponding format/structure/precision conversion is directly completed, with extremely high throughput.
 
9.2 ACCCVT command

Instruction format:
```
ACCCVT.{Layout.{canon, normal}} <Row:Arg0, Col:Arg1, DstType> ACC, ->DstTileType<TileSize>
```

- Layout: Instructs the storage format conversion operation during data migration. The current version supports NORM, NZ2ND, NZ2DN, etc.
- DstType: data type representing the element in the Tile after format conversion.
- DstTileType: used to indicate the destination register, optional T/U/M/N, etc.

The opcode for this instruction is defined as follows:

| Opcode | Function | TileOP | Description |
|--------|----------|---------|--------|
| 2-CUBE | 8 | ACCCVT | Move data from ACC register to external T, U, M, N registers. Supports transformation operations during data movement. |

The ACCCVT instruction only supports ACC input and does not support T/U/M/N register input.

```asm
    BSTART.PAR ACCCVT, DstType    # 隐含包含ACC输入
    B.ARG  Layout.{canon, normal}
    B.DIM  reg, imm,   ->ROW
    B.DIM  reg, imm,   ->COL
    B.IOT  [], group=0, ->{T, U, M, N}<TileSize>
```

Operation configuration: Set the functional mode of ACCCVT through the B.ARG instruction to avoid using SSR register configuration and improve code clarity and instruction set consistency.

Assembly format: `B.ARG Layout.{canon, normal}`

- canon(canonicalize): Convert the fractal of the matrix input into ACC into the standard left matrix format (the fractal capacity of the standard left matrix is 512 bytes, which is a Z fractal), and merge or split the original fractals of ACC based on different data formats.
- normal: Do not transform the original fractal of the matrix in the input ACC.

The schematic diagram of canon operation is as follows:

![fixpipe](../figs/isa/version/0.53/fixpipe.png){ width="700" }

Example: `矩阵Q x (矩阵K^T) x 矩阵V `
```asm
COPYIN [a0], ->T<4KB>                                    # 矩阵Q（row major）
COPYIN [a1], ->T<4KB>                                    # 矩阵K (column major)
COPYIN [a2], ->T<4KB>                                    # 矩阵V (row major)
MAMULB <M:32, N:32, K:32, FP32> T#3, T#2, ->ACC<4KB>
ACCCVT.NORM.canon <Row:32, Col:32, FP32> ACC, ->T<4KB>  # 将ACC矩阵标准化，并写入T寄存器。
MAMULB <M:32, N:32, K:32, FP32> T#1, T#2, ->ACC<4KB>
ACCCVT.NZ2ND.normal <Row:32, Col:32, FP32> ACC, ->T<4KB> # 将ACC矩阵转换为ND格式，并写入T寄存器。
COPYOUT T#1, [a4] 
```

### 10.TCVT conversion operation

10.1 Instruction format:
```
TCVT.{Layout}, SrcType, <Row:Arg0, Col:Arg1, DstType> SrcTile.<reuse>, ->DstTileType<TileSize>
```
- Layout: Instructs the storage format conversion operation during data migration.
- SrcType: Indicates data type of the element in the input Tile.
- DstType: Indicates the data type of the elements in the Tile output after format conversion.
- SrcTile: Input Tile register, ACC register is not allowed.
- DstTileType: output Tile register, ACC register is not allowed.

The TCVT instruction is split into the following instructions for encoding:
```asm
BSTART.PAR TCVT, DstType
B.ARG  Layout, SrcType
B.DIM  reg, imm,   ->ROW
B.DIM  reg, imm,   ->COL
B.IOT  [SrcTile.<reuse>], group=0, ->{T, U, M, N}<TileSize>
```

10.2 B.ARG modification

In order to adapt to the instruction function of TCVT, the B.ARG instruction adds a SrcType field (encoding method is as follows), which is used to specify the data format of the elements in the input Tile.

![barg](../figs/isa/version/0.53/barg.png){ width="700" }

The SrcType field is encoded as follows:| Encoding | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SrcType | FP64 | FP32 | TF32 | HF32 | FP16 | BF16 | HiF8 | e4m3 | e5m2 | e3m2 | e2m3 | e2m1 | e1m2 | e8m0 | HiF4 | reserve |
| Coding | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 |
| SrcType | S64 | S32 | S16 | S8 | S4 | reserve | reserve | reserve | U64 | U32 | U16 | U8 | U4 | reserve | reserve | invalid |

### 11.TCOPY modification

After the update, the TCOPY instruction is used to copy data from Tile register to Tile register in unformatted conversion scenarios.

11.1 Assembly format

```asm
TCOPY SrcTile.<reuse>, ->DstTileType<TileSize>
```

The template block is split into the following instructions for encoding:
```asm
BSTART.PAR TCOPY
B.IOT [SrcTile.<reuse>], group=0, -> DstTileType<TileSize>  #如果通过立即数指定输出大小，需使用B.IOTI指令
```

### 12.TCOPYIN modification

In order to align with the definition of the PTO instruction set, the TCOPYIN instruction naming was changed to **TLOAD** in version 0.53.2. The TLOAD instruction is used to copy data from memory to the Tile register. During the copy process, it supports modifying the storage layout of the data.

In the current version, the TLOAD instruction only supports loading of one to two dimensions of data in memory.

12.1 Assembly format

```asm
TLOAD.Layout <LB0:ColValid, LB1:RowValid, LB2:Col, DataType, PadValue>, [RegSrc0, RegSrc1], DepSrc, -> DstTileType<TileSize>, DepDst
```
The template block is split into the following instructions for encoding:
```asm
BSTART.PAR TLOAD, DataType
B.ARG  Layout, PadValue
B.DIM  reg, imm, ->LB0      # ColValid
B.DIM  reg, imm, ->LB1      # RowValid
B.DIM  reg, imm, ->LB2      # Col
B.IOT  group=0, ->DstTileType<TileSize>  #如果通过立即数指定输出大小，需使用B.IOTI指令
B.IOR  RegSrc0, RegSrc1
B.IOD  DepSrc, ->DepDst
```

12.2 B.ARG instruction modification

In order to adapt to the design of TLOAD, the new version of the B.ARG instruction adds the PadValue parameter. This parameter is encoded as follows:

| PadValue encoding | Description |
|-------------|-------|
| 0 | Zero |
| 1 | Max |
| 2 | Min |
| 3 | Null |
| others | reserved |

The modified B.ARG instruction encoding is as follows:

![barg1](../figs/isa/version/0.53/barg1.png){ width="700" }

### 13.TCOPYOUT modification

In order to align with the definition of the PTO instruction set, the TCOPYOUT instruction naming is changed to **TSTORE** in version 0.53.2.

The TSTORE instruction is used to copy data from the Tile register to the memory. During the copy process, it supports modifying the storage layout of the data to facilitate flexible application in different scenarios.

13.1 Assembly format

```asm
TSTORE.Layout <LB0:ColValid, LB1:RowValid, LB2:Col, DataType>, SrcTile, [RegSrc0, RegSrc1], DepSrc, -> DepDst
```

The template block is split into the following instructions for encoding:
```asm
BSTART.PAR TSTORE, DataType
B.ARG  Layout
B.DIM  reg, imm,   ->LB0    # ColValid
B.DIM  reg, imm,   ->LB1    # RowValid
B.DIM  reg, imm,   ->LB2    # Col
B.IOT  SrcTile, group=0
B.IOR RegSrc0, RegSrc1
B.IOD DepSrc, ->DepDst
```