# 0.42 version update

Update date: September 30, 2024
Corresponding to the instruction level definition version on DBOX [LinxISA Encoding-0.42] (https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100727107943)

## General description of version update

This version update mainly covers instruction naming conventions, optimization of long jump offsets, instruction dual or multi-output encoding methods, etc.

| Change items | Change content | Reason for change |
|------------|---------------------------------|----------------------------------|
|system register|Supplement system registerCW,TR1,TR2|Supplement system register that was missing after upgrading to version 0.4x|
|Instruction changes|**block instruction**:<br> 1. Adjust the instruction naming<br> 2. Modify the implementation of long jump<br> 3. SIMTblock instruction supports serial execution mode<br>**Microinstruction**:<br> 1. Instruction multi-output expression and encoding<br> 2. Supplement the output register bit width identifier of the reduce instruction in the SIMT block<br> 3. Implemented by merging pc.push and conditional jump instructions<br> 4. Modify the expression of instruction encoding immediate field<br> 5. Add b.cond instruction<br> 6. Jump offset of J/JR instruction<br> 7. Add atomic instructions in SIMT block<br> 8. Modify instructions in SIMT block|**block instruction**：<br> 1. In order to clearly distinguish header instruction from microinstructions and to distinguish the block start instruction in header from other description instructions<br> 2. The BNextOffset field of the BSTART instruction may not be enough to encode the actual jump offset<br> 3. Provide corresponding software interfaces for different scenarios in the program loop to facilitate software designers to flexibly write programs<br>**Microinstructions**:<br> 1. Dual/multi-output instructions that need to be introduced later in LinxISA<br> 3. Avoid adding redundant registers<br> 5. Supplement the instruction definitions in the block to ensure functional completeness<br> 2&4&6. Continuously optimize the instruction set |


## Change details

### 1. system register

Added system register**CW**, **TR1**, **TR2**, these are the missing system register after upgrading to version 0.4x.

### 2. Instruction changes

**block instruction**

In LinxISA, in order to clearly distinguish header instruction from microinstructions and to distinguish block start instructions from other description instructions in header, this version has made the following standardized adjustments to the instruction naming:

- header instruction is expressed in uppercase letters; microinstructions are expressed in lowercase letters. <br>
- In addition to the block start instruction in header instruction, other header description instructions use "B." as a prefix to facilitate the distinction between block start instructions and other block description instructions in the assembler. <br>
- Compression instructions with a coding width of 16 bits are named with "C." as the prefix.

#### Adjustment 1: Naming convention for header instruction

Generally speaking, except for BSTART in header instruction of inline blocks and detached blocks, other description instructions are uniformly prefixed with B.. The specific modifications are as follows:

![v0.42BlockHeaderName](../figs/isa/version/v0.42BlockHeaderName.png)

#### Adjustment 2: Template block instruction naming modification

In order to cooperate with the adjustment of the header instruction naming, the naming of the template block instruction has been modified simultaneously, as follows:![v0.42templateName](../figs/isa/version/v0.42templateName.png)

#### Adjustment 3: Naming modification of compression instructions

All 16-bit compression instructions are uniformly prefixed with "C.", and the related instructions are as follows:

![v0.42comInsName](../figs/isa/version/v0.42comInsName.png)

#### Adjustment 4: Modify the implementation of long jump

Version 0.42 introduces the BSTART + B.NEXT encoding combination solution to solve the problem that the BNextOffset field of the BSTART instruction may not be enough to encode the actual required jump offset. The specific instructions are as follows:

Among them:

- BSTART is used to encode the low-order part of the jump offset, and B.NEXT is used to encode the high-order part. <br>
- Only the BSTART instruction with Opcode 4b0000 can be used in combination with B.NEXT. The B.NEXT instruction is invalid when placed in other header.
- The B.NEXT code immediately follows the BSTART instruction. <br>
- EX: extend flag, setting it to 0 means that the jump offset in BSTART is complete (FF), setting it to 1 means it is incomplete (HF), and you need to wait for the subsequent B.NEXT instruction to form a complete jump distance.

BSTART coding structure

![v0.42bstartEncode](../figs/isa/version/v0.42bstartEncode.png)

B.NEXT coding structure, BnextOffset[41:17] is used to encode the high-order part of the jump distance, and can be combined with BSTART to express the 42-bit jump distance.

![v0.42B.NEXT](../figs/isa/version/v0.42B.NEXT.png)

B.NEXT supports 16-bit compressed version B.NEXT.C, which can be combined to express 29-bit jump distance.

![v0.42B.NEXT16](../figs/isa/version/v0.42B.NEXT16.png)

#### Tweak 5: SIMTblock instruction supports serial execution mode

**Execution Mode**

For the different dependencies between each iteration of the loop, the instruction set provides the definition of three SIMT block execution modes.

- BSTART.LOOP: Complete serial execution between all lanes. It is suitable for scenarios where there are memory access dependencies between iterations of a loop. <br>
- BSTART.VECT: Different lanes in the same group can be executed in parallel, but different groups need to be executed serially. It is suitable for scenarios where there are memory access dependencies between some iterations in the loop. <br>
- BSTART.SIMT: Parallel execution can be performed between different lanes in the same group, and parallel execution is also supported between different groups. Suitable for scenarios where there are no dependencies between all iterations in the loop.

The schematic diagram of each execution mode is as follows:

![v0.42ExcuteModeDiagram](../figs/isa/version/v0.42ExcuteModeDiagram.png)

**Command definition**

The BSTART definition of SIMTblock instruction is as follows:

Assembly syntax:

```asm
C.BSTART.<LOOP, VECT, SIMT>
BSTART.<LOOP, VECT, SIMT>
```

SIMTblock instruction defaults to FALL type jump.

Encoding format:

![v0.42bstart](../figs/isa/version/v0.42bstart.png)

Compared with the previous version, the Parallel Mode field for encoding execution mode has been added. Among them:

- 0: for encoding LOOP mode<br>
- 1: for encoding VECT mode<br>
- 2: For encoding SIMT mode<br>
- Other encodings are reserved.

Note:

The current version does not currently support the LOOP block implementation released in the V0.41 version. The corresponding encoding is temporarily deleted from the instruction set. The original LOOP block is encoded as follows:

![v0.42loop](../figs/isa/version/v0.42loop.png)

---

**Microinstructions**

#### Tweak 6: Directive multiple outputs and expressions

In view of the dual/multi-output instructions that need to be introduced in LinxISA in the future, we first determined its encoding method in the current version and accordingly adjusted the assembly expression of output to the global register UL_GPR.

Single output:

```asm
add SrcL，SrcR, ->t；   #输出至T队列
add SrcL，SrcR, ->u；   #输出至U队列
add SrcL，SrcR, ->Rx；  #输出至UL_GPR
```

Multiple outputs:

```asm
mulh SrcL, SrcR, ->tx2；        #输出到连续2个T队列
ld [SrcL, SrcR<<3], ->tx4；     #输出到连续4个T队列0
```

The input/output codec of the microinstruction register in the scalar block is as follows:

![v0.42in&outAsm](../figs/isa/version/v0.42in&outAsm.png)

Note:- Multi-output is only allowed for specific Opcodes. The output register (RegDst) field encoding of other single-output instructions is undefined, and the model or hardware execution results are not known. <br>
- Since the speed pointer attributes of T and U clock hands are different, one instruction is not supported to output to both T and U. <br>
- The UL_GPR written in the block is modified to be marked by "->", and the instruction in the block reads the register value to the updated value. <br>
- Retain the original restriction: "Each UL_GPR can only be written once in the same block."

#### Adjustment 7: reduce instruction

Supplement the output register bit width identifier of the reduce instruction in the SIMT block.

#### Adjustment 8: pc.push and conditional jump instructions

The pc.push instruction in the SIMT block is used to push the convergence point (reconverge) PC and thread mask onto the stack when the program execution flow diverges. However, to determine whether divergence occurs during program execution, you need to wait for the result of the subsequent conditional jump instruction, so you need to add a register to temporarily save the PC of the convergence point.

In order to avoid increasing this register, it was decided to merge the pc.push and conditional jump instructions into one instruction in the current version. The specific modifications are as follows:

**Modification 1: Remove pc.push instruction**

**Modification 2: Update conditional jump instruction semantics**

Based on the semantics of scalar, the execution process of conditional jump instructions in the modified SIMT block is as follows:

- There is a diverge (the result of whether the effective lane jump in the current group is inconsistent): Store the reconvergence information and the diverge information of one side branch into the ControlStack register, and update the mask and PC of the other side branch to the current state for execution.
- There is no diverge: no effect on the ControlStack register. And execute according to ordinary conditional jump instructions.

Among them:

- The mask of the current group is recorded as cur_mask.
- Among the two branches, if the mask of the branch chosen to be executed first is recorded as cal_mask, it will be stored in save_mask=cur_mask &(~cal_mask) of the ControlStack register.
- The condition for judging the existence of diverge is: ((cur_mask & cal_mask) != cur_mask) && ((cur_mask & ~cal_mask) != cur_mask)

Assembly syntax:

![v0.42pcpushasm1](../figs/isa/version/v0.42pcpushasm1.png)

Among them:<br>
The calculation of the re-convergence point PC is: rpc = tpc + rc_offset<<3<br>
The calculation of the jump target address is: br_pc = tpc + br_offset<<3

#### Adjustment 9: Add a b.cond instruction

In order to avoid insufficient offset encoding space for conditional jump instructions in extreme scenarios, a B.COND instruction is added<br>

Assembly syntax:

```asm
b.cond SrcP.<T>, SrcL.<T>, SrcR.<T>
```
Among them: the value of SrcP is used as the judgment condition; SrcL is used to store the jump target address; SrcR is used to store the re-convergence point PC.

Instruction semantics:<br>
Determine the SrcP values in all valid lanes under the current group: if all are 0 or all 1, it means there is no diverge. <br>
**No diverge**: If all are 0, the execution will be postponed, if all are 1, the execution will be jumped. <br>
**Diverge exists**: First push the re-convergence point PC and the mask of the current Group in SrcR to the CSTK register, and then push the branch PC and branch mask on one side. And update the mask and PC of the other side branch to the current state for execution.

Encoding format:

![v0.42b.cond](../figs/isa/version/v0.42b.cond.png)

This instruction needs to be used in conjunction with CMP instructions, see the assembly example below:

```asm
addtpc %hi(rc_label),    ->t
addi t#1, %lo(rc_label), ->t        // 得到重汇聚点PC
addtpc %hi(br_label),    ->t
addi t#1, %lo(br_label), ->t        // 得到跳转目标PC
cmp.eq a0, t#1,          ->t
b.cond t#1, t#2, t#4
```

#### Adjustment 10: Jump offset of J/JR instructions

The jump offset of the J/JR instruction is modified to be encoded in 8-byte units.

![v0.42jr](../figs/isa/version/v0.42jr.png)The execution semantics of the JR instruction in the SIMT block are: jump to tpc=SrcL+simm15<< 3

![v0.42j](../figs/isa/version/v0.42j.png)

The execution semantics of the J instruction in the SIMT block are: jump to tpc += simm25<<3

#### Adjustment 11: Add atomic instructions in SIMT block

The following atomic instructions are added to the SIMT block to implement atomic operations and store reduce operations.

![v0.42automaticasm](../figs/isa/version/v0.42automaticasm.png)

- The Load.op class instruction adds an optional attribute ".ne" based on the definition of scalar, indicating that the instruction implements non-atomic operations. Atomic operations are implemented by default. <br>
- The Store.op class instruction is based on the definition of scalar, with the optional suffix ".rd" added, indicating that the instruction has the same address in SrcL in all lanes and performs store reduce operations. Atomic operations are implemented by default.

#### Adjustment 12: Modification of instructions in SIMT block

**Supplement the assembly identification and encoding of sd and ud**

- For data type conversion instructions, it is necessary to distinguish whether there are signs during the conversion process of 64-bit integer data and floating-point data;<br>
- Multiplication and division instructions need to distinguish whether they are signed or not when operating on 64-bit wide integer data.

Therefore, the 64-bit source operands of SIMTblock instruction are uniformly modified to be represented by the suffix ".sd" or ".ud", and the encoding of 64-bit signed and unsigned integer data is supplemented.

![v0.42integerasm](../figs/isa/version/v0.42integerasm.png)

**Command adjustment**

The data type, bit width, and presence or absence of signs operated by instructions in the SIMT block can be represented by the suffix of the operand, so instructions with sign information in some OPs are merged. <br>
These include: Reduce instructions and multiplication and division instructions

![v0.42reduce1](../figs/isa/version/v0.42reduce1.png)

At the same time, the reduce instruction encoding was modified. The modified encoding is as follows:

![v0.42reduce2](../figs/isa/version/v0.42reduce2.png)

The instruction encoding retains the original mul, div, and rem encoding.

**Add lbstop encoding**

Added the end instruction encoding in SIMTbody and named it lbstop to avoid ambiguity when the assembler generates binary files or model decoding.

![v0.42lbstop](../figs/isa/version/v0.42lbstop.png)