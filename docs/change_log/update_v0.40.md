# Version 0.40 update

Update date: June 5, 2024

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-0.40](https://dbox.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:100421282855)

Problems to be solved by LinxISA V0.40:

1. V0.3X architecture scalability problem: fixed-length 64bitheader cannot expand registers and other description information.
2. V0.3X instruction encoding problem: headerbody does not share a set of encoding, causing the hardware and compiler implementation complexity to be too high.
3. V0.3X codesize problem: The instruction expansion caused by header is too large, about 50% compared to ARM.

## General description of version update

- **architectural state/ABI changes**

| Change content | Reason |
|----------------------------------|----------------------------------|
| 1. The first layer architectural registerUL_GPR is increased to 24 | Optimize the register allocation algorithm, reduce the Spill overhead of block instruction, and improve performance. |
| 2. Deleting LL_GPR in the second layer architectural register | LL_GPR will significantly increase the complexity of hardware renaming.  |
| 3. The T register index distance in the second layer architectural register is reduced to 4 | T#5-T#8 has a low usage rate and takes up hardware ROB space.  |
| 4. Add U relative index register in the second layer architectural register, the index distance is 1-4 | Enable long-distance relative index, greatly reducing the number of copy instructions.  |
| 5. Modify the register mapping relationship: R1 maps to SP, R2 to R9 maps to A0 to A7, R10 maps to RA | Adapt to the new version of fentry, fexit, fret and other template block designs. |

- **block instruction form**

Added architecture definitions for integrated blocks and separate blocks. An integrated block can significantly eliminate header overhead, and small blocks can reduce the information redundancy of header.

Note: Version 0.40 only supports one block definition

- **header encoding reconstruction**

The header encoding is completely reconstructed and split into header composed of multiple 16bit and 32bit instruction descriptors. By splitting the 64-bit fixed-length header into multiple header instruction combinations, the amount of program code can be effectively reduced and the expansion capability of header can be enhanced.

| header instruction | List |
|--------|----------|
| Added 16bitheader instruction | C.BSTART of general block, C.BSTART, C.LBREF, C.BSTOP of hotspot scalar block |
| Added 32bitheader instruction | BSTART of general block, BSTART, LBREF, BATTR, BSTOP of hotspot scalar block |
| Template instructions changed to 32bit encoding | MCOPY, MSET, FENTRY, FEXIT, FRET.RA, FRET.STK (MPUSH, MPOP, BLBAR are not supported in the current version) |

- **DELETED block instruction**

Remove Inline Block and BSBAR blocks. Inline instruction design is not efficient enough. In most scenarios, there are only 1-2 microinstructions in the Inline block.

- **Microinstructions**

The microinstruction coding is completely reconstructed, the definition of existing instructions remains unchanged, and all coding is adjusted. The microinstruction coding space is shared with the header coding space, which is conducive to disassembly and hardware decoder implementation, making the execution environment safer.

After upgrading to version 0.4, the microinstruction encoding method is adjusted as follows:1. Since headerbody is coded together, the lower 7-bit Opcode field of the original 32-bit instruction is adjusted.
2. After deleting LL_GPR, the input/output register field is changed to 5bit unified encoding.
3. Extend the shamt domain of instructions such as add to support a wider range of offsets.
4. Registerless output instructions do not occupy the T register slot, reducing register allocation.
5. Cancel the restriction of three-input instructions. For specific three-input instructions, one of the inputs is no longer required to be fixed to the T register in the block.
6. The M and N parameters of the bit field insertion instruction bfi are changed to be encoded with byte granularity.
7. The SrcRType field is added to the cmp and setc instructions to extend the instruction implementation.
8. Due to the limitation of encoding format, the floating point instruction FCVT is split into multiple instructions.
9. Following the ABI changes, the encoding method of the instruction input/output register has been adjusted.

The list of microinstructions added or deleted in the current version is as follows:

| Command List | Reason |
|--------|----------|
| **New 32bit instruction** | |
| 1. addpc <br>2. cmp.and, cmp.or, cmp.andi, cmp.ori<br>3. setc.and, setc.or, setc.andi, setc.ori, setc.tgt<br>4. bic, bis, ccatw<br>5. madd, maddw<br>6. tc.iva, tc.iall<br>7. lr.b, lr.h, sc.b, sc.h, swapb, swaph | 1. Based on the codesize analysis of the compiler and model team, new instructions are used to reduce the amount of program code. <br>2. tc.iva, tc.iall are the operating system OS kernel development requirements. |
| **New 16bit instruction** | |
| 1 movr, movi<br>2. c.add, c.sub, c.and, c.or<br>3. c.addi, c.slli, c.srli<br>4. c.setc.eq, c.setc.ne<br>5. c.lwi, c.ldi, c.swi, c.sdi<br>6. c.cmp.eqi, c.cmp.nei<br>7. sext.b, sext.h, sext.w, zext.b, zext.h, zext.w<br>8. c.ssrget, c.addpc, c.addtpc | Add 16bit length C extension instructions to reduce Codesize and improve performance. |
| **Name Adjustment Command** | |
| 1. The name of the concat instruction is changed to ccat<br>2. The name of the rev instruction is changed to rev64 | Standardized instruction naming |
| **The current version does not implement the command** | |
| 1. mulh, mulhu<br>2. load.a, load.ua classes<br>3. addc, subc<br>4. casw, casd<br>5. gqm class and Cache maintenance instructions in the system block | The current version does not support dual output instructions, and system instructions such as gqm will be determined in later versions |
| **Removed microinstructions** | |
| 1. addbpcf, addbpcn <br>2. setc.trap, setc.msg <br>3. ssrcrlt <br>4. tlbget, tlbset, tlbi | Based on the architectural changes in version 0.40, some instructions are no longer used and therefore deleted. |

## Change details

### 1. architectural state changes

The first layer architectural registerUL_GPR is increased to 24: R0 to R23. The dynamic instruction number benefit brought by increasing the number of GPRs in the SPEC test program is as shown in the figure below:

![spec](../figs/isa/version/spec.png)

As can be seen from the above figure, adding 8 GPRs can effectively reduce the number of dynamic instructions in the SPEC test program, and using two sets of relative index registers within the block brings greater benefits.Second layer architectural register modification:

1. Delete LL_GPR of block-private;
2. The number of relative index T registers is reduced to 4, and each instruction can index the results of the previous 4 instructions output to the T queue;
3. Add 4 relative index U registers. Each instruction can index the results of the previous 4 instructions output to the U queue.

| Register name | Register alias | Explanation |
|-----------|-----------|--------|
| TR1 | T#1 | The first instruction result output to the T queue in the previous sequence |
| TR2 | T#2 | The result of the second previous instruction output to the T queue |
| TR3 | T#3 | The result of the third previous instruction output to the T queue |
| TR4 | T#4 | The result of the fourth previous instruction output to the T queue |
| UR1 | U#1 | The first instruction result output to the U queue in the previous sequence |
| UR2 | U#2 | The result of the second previous instruction output to the U queue |
| UR3 | U#3 | The third instruction result output to the U queue in the previous sequence |
| UR4 | U#4 | The result of the fourth previous instruction output to the U queue |

The T register and the U register are indexed independently. The example is as follows:

```asm
ldi [a0, 0], ->t         # inst0，指令结果写到T队列
ldi [a1, 0], ->t         # inst1，指令结果写到T队列
ldi [a0, 8], ->u         # inst3，指令结果写到U队列
ldi [a1, 8], ->u         # inst4，指令结果写到U队列
addi  t#2, t#1, ->t      # 索引inst0和inst1的指令结果
sd t#1，[a2, 0]          # 指令无寄存器输出
addi u#2 u#1, ->u        # 索引inst3和inst4的指令结果
sd u#1，[a2, 8]          # 指令无寄存器输出
```
Assembly example of instruction output:

- Instruction without register output: `Opcode SrcL, SrcR`
- Instructions are output to the T queue: `Opcode SrcL, SrcR, ->t`
- Instructions are output to the U queue: `Opcode SrcL, SrcR, ->u`
- The command is output to the first layer architectural register: `Opcode SrcL, SrcR, =>a0`

### 2. Change of instruction encoding space

The instruction encoding space and characteristics are as follows:

headerbody unified encoding, the encoding length uses 16bit and 32bit.

![Coding space](../figs/isa/arch/encoding.png)

Symbol description:

- Size: Instruction word length, 0: 16bit instruction; 1: 32bit instruction.
- L/Layer: Instruction level, 0: header instruction coding space; 1-3: Microinstruction coding space
- Opcode: instruction operation code

The combination space distribution is as follows:

- Size=0: 16bit instruction
    - layer=0 : 16bitheader instruction
    - layer=1 : 16bitbody microinstruction
- Size=1: 32bit instruction
    - layer=0 : 32bitheader instruction
    - layer=1-3: 32bitbody microinstructions

### 3. header instruction changes

The header encoding is completely reconstructed, introducing the concept and design of variable-length header, and splitting it into multiple header combinations of 16bit and 32bit instruction descriptors.

The so-called variable length header encoding, in layman's terms, means splitting the entire information description field contained in header, and then combining some of the field segments into multiple block description instructions, which can be 16 bits long or 32 bits long. Therefore, in the new version, a header instruction is composed of multiple 16 or 32bit block descriptor instructions. The total encoding length of header is not fixed and is called variable length header.

For an integrated block, the **header description instruction must precede the body instruction**. Decoding to the body instruction indicates the end of the current header description instruction.

1. **New BSTART instruction**

BSTART instruction semantics: Submit the previous block instruction and open the current block. BSTART is an instruction that must exist in block instructionheader and is also the first instruction in block instruction.The current version is designed with two BSTART instructions. One supports the full range of block type and jump type instructions for general scenarios. The other is an instruction mainly used for offset class jumps and block type defaults to the scalar block, also known as the hot scalar block.

16bit BSTART：

![v0.40bstart16](../figs/isa/version/v0.40bstart16.png)

32bit BSTART：

![v0.40bstart32](../figs/isa/version/v0.40bstart32.png)

- BlockType field: used to encode block type.
- DCP bit: integrated block and separated block flag bit: 0 represents an integrated block, 1 represents a separated block (the current version is fixedly coded as 0)
- BrType field: used for encoding jump type: **0 is invalid encoding**.
- PayLoad: When the jump mode is offset type jump, this field is used to encode the jump distance; other jump types are temporarily reserved. 

2. Added BATTR instruction

The BATTR block is used to describe the attribute information of a block. The encoding is as follows:

![v0.40battr](../figs/isa/version/v0.40battr.png)

- T: Block submission trap flag T-trap, set to 1: indicates that the current block instruction will generate a trap after submission.
- R: block instruction relay flag R-relay, set to 1: the private register of the current block is inherited to the next block instruction, otherwise it is not inherited.
- F: exception normal processing flag F-fixup, some exception low privilege level processing.
- H: Super block mark H-hyper, set to 1: indicates that jump instructions within the block are supported; otherwise, it is not supported.
- atom: Atomic block flag bit, indicating that the current block is an atomic block.
- far: Send the current block to multi-core remote execution.
- aq/rl: identifies the fence attribute between block instruction.

3. Added LBREF instruction

The LBREF block is only used to express jump offsets between blocks. This instruction has two encoding formats, 16bit and 32bit.

![lbref-0.40](../figs/isa/version/lbref-0.40.png)

Jump offset reference instruction LBREF. The BNextOffset field in its encoding is used to splice with the BNextOffset in the subsequent BSTART/C.BSTART instructions to form a complete BNextOffset field.

LBREF instruction description:

- In storage logic, the lbref instruction of a block always precedes the bstart instruction.
- If a block contains the lbref instruction, the hardware will use lbref as the starting instruction of the block.
- 16bit and 32bit bstart and lbref instructions can be freely combined, for example: `c.lbref + c.bstart`, `c.lbref + bstart`, `lbref + c.bstart`, `lbref + bstart`.

4. Added BSTOP instruction

The lowest bit is 0 or 1, and the remaining bit codes are all 0, which is an invalid instruction. It is also used as a BSTOP instruction and can be used to submit the current block instruction.

![bstop](../figs/isa/version/bstop-0.40.png)

5. Added template block

The design of template block is introduced to reduce CodeSize and improve performance. The template block instruction is defined as a block start instruction, which is used to submit the previous block instruction and open the current block. The Opcode for each template block acts as a special "BSTART", template blockheader describes the input/output of block instruction, and other implementation requirements.

![v0.40templateblock](../figs/isa/version/v0.40templateblock.png)

Instruction design description:

- **MCOPY/MSET instruction**: Input instructions for three registers. The three inputs are transmitted using the first layer architectural registerRegSrc0, RegSrc1 and RegSrc2 respectively, where:| Memory copy instruction MCOPY | Memory assignment instruction MSET |
|------------------|------------------------|
| RegSrc0: used to transfer the destination memory address | RegSrc0: used to transfer the destination memory address |
| RegSrc1: used to pass the source memory address | RegSrc1: used to pass the source data |
| RegSrc2: used to pass the number of bytes copied | RegSrc2: used to pass the number of bytes assigned |

- **FENTRY instruction**: This instruction is used to open the stack at function entry, **implying the input/output information of the stack pointer register sp**.
- **FEXIT, FRET.RA, FRET.STK instructions**: These three instructions are used for the stack operation at function exit, and also **imply the input/output information of the stack pointer register sp**.

The stack space size is encoded in unsigned immediate unsigned imm[14:3], in units of 8 Byte. The register information pushed onto the stack is expressed through SrcBegin and SrcEnd. SrcBegin and SrcEnd represent a continuous register in the first-level registers R0-R23. For example, if R2, R3, R4, R5, and R6 are pushed onto the stack, SrcBegin will be encoded as R2 and SrcEnd will be encoded as R6.

The three stack stack instructions correspond to different scenarios of function exit, specifically:

- The FEXIT instruction is used in scenarios where the function ends with a function call (including function pointer call), and the jump type defaults to Fall. <br>
- The FRET.RA instruction is used in scenarios where the function returns normally and there are no sub-functions inside the function. The return address is obtained by directly reading the Ra register. The default jump type is Return. <br>
- The FRET.STK instruction is used in scenarios where the function returns normally and there are sub-functions inside the function. The return address needs to be loaded from the stack, and the jump type defaults to Return.

The assembly format is as follows:

| Template instructions | Assembly format | Default jump method | Notes |
|-----------|-----------|-----------|-----------|
| MCOPY | b.mcopy [RegSrc0, RegSrc1, RegSrc2] | Defer Fall Through | Source and destination addresses do not overlap |
| MSET | b.mset [RegSrc0, RegSrc1, RegSrc2] | Defer Fall Through | None |
| FENTRY | f.entry [RegSrc0 ~ RegSrcn], sp!, uimm | Defer Fall Through | Imply sp register as input and output |
| FEXIT | f.exit [RegDst0 ~ RegDstn], sp!, uimm | Defer Fall Through | Implicit sp register as input and output |
| FRET.RA | f.ret.ra [RegDst0 ~ RegDstn], sp!, uimm | Return | Implies sp register as input and output |
| FRET.STK | f.ret.stk [RegDst0 ~ RegDstn], sp!, uimm | Return | Implies sp register as input and output |

6. Delete block instruction

Remove Inline Block and BSBAR blocks. <br>

Inline instruction design is not efficient enough. In most scenarios, there are only 1-2 microinstructions in the Inline block. Therefore, delete the original Inline design and change the block structure form into an integrated block (dynamic Inline block)

### 4. Microinstruction changes

Based on the codesize analysis summary led by the compiler team and the analysis data of the model team, the following instructions are added to reduce the codesize gap with other architectures.

1. Add movr/movi command

The command encoding is as follows:<br>

![v0.40movr&movi](../figs/isa/version/v0.40movr&movi.png)Movr: Register movement, moves the source register value to the destination register, SrcL and RegDst can be repeated.
Movi: Move immediate data, move immediate data in the range [-16,15] to registers R1-R23 or T/U queue.

2. Add C.ADDPC instruction

The c.addpc instruction is used to record the return address in a CALL type block. c.addpc is the alias instruction of movi. The instruction encoding is as follows:<br>

![v0.40c.adddpc](../figs/isa/version/v0.40c.adddpc.png)

The output of the c.addpc instruction is fixed to the RA register, and the immediate value field is used as a signed immediate value.

3. Add cmp and setc instructions

Added cmp.{and, or, andi, ori} and setc.{and, or, andi, ori} commands<br>

![v0.40cmp&setc-1](../figs/isa/version/v0.40cmp&setc-1.png)

cmp.and: RegDst = SrcL & SrcR<br>
cmp.or: RegDst = SrcL | SrcR<br>

![v0.40cmp&setc-2](../figs/isa/version/v0.40cmp&setc-2.png)

cmp.andi: RegDst = SrcL & simm12<br>
cmp.ori: RegDst = SrcL | simm12<br>

![v0.40cmp&setc-3](../figs/isa/version/v0.40cmp&setc-3.png)

setc.and: setc.flag = SrcL & SrcR<br>
setc.or: setc.flag = SrcL | SrcR<br>

![v0.40cmp&setc-4](../figs/isa/version/v0.40cmp&setc-4.png)

cmp.andi: setc.flag = SrcL & simm<br>
cmp.ori:setc.flag = SrcL | simm<br>

4. Add BIC/BIS instructions

In a large number of scenarios, we need to clear the lower 3 bits, lower 4 bits or lower 5 bits of the data. The original method is to use left shift and then right shift (or a combination of multiple instructions). After adding the BIC instruction, it can be implemented with one instruction.

![v0.40bic&bis](../figs/isa/version/v0.40bic&bis.png)

The following are the comparison results provided by the compiler team in the summary of comparative analysis between LinxISA and ARM codesize:<br>

![v0.40bic&bisCause](../figs/isa/version/v0.40bic&bisCause.png)

5. Add MADD/MADDW instructions and MIADD/MISUB instructions

Added multiply-accumulate instructions MADD/MADDW and multiply-add-multiply-subtract instructions with immediate values. <br>

![v0.40madd&maddw](../figs/isa/version/v0.40madd&maddw.png)

| Command | Operation |
|---------|----------------|
| MADD | RegDst = SrcD+SrcL*SrcR |
| MADDW | RegDst = SignExtend((SrcD+SrcL*SrcR)[31:0]) |
| MIADD | RegDst = SrcL + SrcR * uimm |
| MISUB | RegDst = SrcL - SrcR * uimm |

The following are the comparison results provided by the compiler team in the analysis summary of LinxISA and ARM codesize:<br>

![v0.40madd&maddwCause](../figs/isa/version/v0.40madd&maddwCause.png)

6. Add CCATW command

![v0.40ccatw](../figs/isa/version/v0.40ccatw.png)

Semantics: The lower 32 bits of the two source registers are concatenated and circularly shifted. The lower 32 bits and upper 32 bits of the result are sign-extended and written to RegDst and T respectively.

7. Add TC.IVA/TC.IALL instructions

This instruction is added to meet the operating system OS kernel development needs, and is coded as follows:

![v0.40tc.iva&tc.iall](../figs/isa/version/v0.40tc.iva&tc.iall.png)TC.IVA instruction semantics: Invalidate the cache line copy where the memory address SrcL is located from the Translation Cache. <br>
TC.IALL instruction semantics: Invalidate the cache line copy contained in the Translation Cache.

8. Add LR/SC/SWAP instructions

Added LR/SC/SWAP instructions to operate in bytes and halfwords.<br>

![v0.40lr&sc&swap](../figs/isa/version/v0.40lr&sc&swap.png)

| ATOMIC_SIZE | LR class instructions | SC class instructions | SWAP class instructions |
|---|---|---|---|
| 0 | LR.B | SC.B | SWAPB |
| 1 | LR.H | SC.H | SWAPH |
| 2 | LR.W | SC.W | SWAPW |
| 3 | LR.D | SC.D | SWAPD |

9. Add setc.tgt and addpc instructions

Add the encoding of setc.tgt and addpc instructions in the 32bit public instruction space. <br>

![v0.40addtpc&addpc](../figs/isa/version/v0.40addtpc&addpc.png)

addpc is an alias instruction of addtpc, the RegDst field is fixedly encoded as RA, and only the upper 12 bits of the immediate data field are valid.

![v0.40setc.tgt32](../figs/isa/version/v0.40setc.tgt32.png)

The SrcR field of the setc.tgt instruction is encoded as all zeros.

10. Add C extension instructions

According to the instruction usage popularity, the following 16-bit microinstructions are added to reduce the Codesize and improve performance in some scenarios. <br>
16bit microinstructions are basic instructions and can be used in any block type and body.

![v0.40Cinstruction](../figs/isa/version/v0.40Cinstruction.png)

Among the above instructions, special attention needs to be paid to the C.SSRGET instruction, whose SSRID requires an independent set of encoding. The encoding and decoding mapping relationship is as follows:<br>

![v0.40c.ssrget-ssrid](../figs/isa/version/v0.40c.ssrget-ssrid.png)

Currently, only the commonly used TP, GP, and CP register codes have been added, and other spaces are temporarily reserved.

---

### Instruction encoding adjustment

**Adjustment 1: Adjustment of the lower 7-bit Opcode field of the original instruction**

The lower 7 bits of the current version of the instruction encoding contain three types of information:<br>

**MInst[0]**: Instruction length field Size, Size=0 indicates a 16-bit length instruction; Size=1 indicates a 32-bit length instruction. <br>
**MInst[2:1]**: Instruction level field Layer, Layer=0b01 and 0b10 belong to the public instruction encoding space; Layer=0b11 belongs to the private instruction encoding space (private space for each block type). <br>
**MInst[6:3]**: Instruction opcode Opcode.

**Adjustment 2: Input/output register field adjustment**

The R/L and Src fields in previous versions are merged and 5bit is coded together. Merge the G/L and RegDst fields in previous versions, and use 5 bits to code together. <br>
Version 0.3x:<br>

![v0.40in&outreg-1](../figs/isa/version/v0.40in&outreg-1.png)

0.4x version:

![v0.40in&outreg-2](../figs/isa/version/v0.40in&outreg-2.png)

**Adjustment 3: Extend shamt domain**

For add/sub/and/or/xor/load type instructions, extend the shamt field to 5 bits to meet the needs of large structs in programming languages and address offset shifts exceeding 3 bits.

![v0.40shamt](../figs/isa/version/v0.40shamt.png)

**Adjustment 4: No register output instructions**

Registerless output instructions do not occupy the T register slot:<br>

setc class, intra-block jump class, ssrset, ssrwr, store does not update address class, prf class, execution control class (trap, bwe, etc.), Cache management class instructions do not occupy T register slot. <br>

**Adjustment 5: Three-input cancellation restriction**Three-register input instructions such as CSEL have no limit on the input register, which can be up to 3 GPR or 3 T REG or 3 S REG.

![v0.40csel](../figs/isa/version/v0.40csel.png)

**Tweak 6: SSRGET/SSRSET instructions within scalar block**

In order to unify the encoding format and reduce the decoder complexity, adjust the SSR-ID of the SSRGET/SSRSET instructions in the scalar block to 12bit. <br>
At the same time, in order to adapt to the adjustment of the addpc command, the opcode field of the ssrget/ssrset command is modified: 4b1100 -> 4b1111

![v0.40SSRGET&SSRSET](../figs/isa/version/v0.40SSRGET&SSRSET.png)

**Tweak 7: SSRGET/SSRSET instructions within system blocks**

The names of the SSRGET/SSRSET instructions in the system block are modified: SSRGET is changed to SSRRD; SSRSET is changed to SSRWR.

![v0.40SSRRD&SSRWR](../figs/isa/version/v0.40SSRRD&SSRWR.png)

#### Adjustment 8: CONCAT directive

CONCAT name changed to CCAT. <br>

![v0.40ccat](../figs/isa/version/v0.40ccat.png)

#### Adjustment 9: BFI command

BFI changes to Byte as the granularity. <br>

The original instruction encoding is relatively special and requires a separate hardware decoding implementation, which increases the decoding complexity. Therefore, modify its granularity to BYTE, and the modification will make the processing of strings very efficient. <br>
Modify the instruction semantics as follows: intercept the lower N bytes from the right source register, replace the Mth to M+N-1th bytes of the left source register, and write the result to the destination register.

![v0.40bfi](../figs/isa/version/v0.40bfi.png)

**Tweak 10: SETC.TGT directive**

SETC.TGT is added to the 16bit compressed instruction space. <br>

![v0.40setc.tgt](../figs/isa/version/v0.40setc.tgt.png)

**Adjustment 11: CMP/SETC class instructions**

CMP/SETC class instructions add SrcRType field. <br>

The encoding is as follows:

![v0.40cmp&setc](../figs/isa/version/v0.40cmp&setc.png)

The setc.{and, or} and cmp.{and, or} instructions are not completely consistent with the SrcRType parameters of other instructions, as follows:

| SrcRType | setc.and, setc.or, cmp.and, cmp.or | Other setc, cmp instructions |
|----------|----------------------------------------|-------------------|
| 0 | No format conversion | No format conversion |
| 1 | Intercept the lower 32 bits of the SrcR register with sign extension (.sw) | Intercept the lower 32 bits of the SrcR register with sign extension (.sw) |
| 2 | Intercept the lower 32-bit unsigned extension of the SrcR register (.uw) | Intercept the lower 32-bit unsigned extension of the SrcR register (.uw) |
| 3 | Invert SrcR register bit (.not) | Invalid encoding (N/A) |

**Adjustment 12: Some SETC instructions**

The immediate offset of SETC class instructions with immediate data needs to be left shifted by shamt bits. The specific encoding is as follows:<br>

![v0.40setc](../figs/isa/version/v0.40setc.png)

The immediate value in the assembly syntax of the setc class instruction does not express shifting. The compiler will perform shift encoding based on the given immediate value. The specific compilation is as follows:

![v0.40setcasm](../figs/isa/version/v0.40setcasm.png)

**Adjustment 13: Division/Remainder Instructions**

Division instruction DIV class: Modify the quotient of the division result and write it to the destination register. <br>
Remainder instruction REM class: Modify the remainder of the division result and write it to the destination register.

**Tweak 14: Floating point instruction FCVT split**

In order to unify the decoding format and reduce the complexity of hardware decoding, an FCVT instruction from the previous version was split. The results are as follows:<br>

![v0.40fvt-1](../figs/isa/version/v0.40fcvt-1.png)SrcType of FCVT.H/ FCVT.S/ FCVT.D instruction: 0: uw; 1: sw; 2: sl; 3: ul<br>

FCVT.UW/ FCVT.SW/ FCVT.UL/ FCVT.SL instruction SrcType: 0: n/a; 1: h; 2: s; 3: d

![v0.40fvt-2](../figs/isa/version/v0.40fcvt-2.png)

SrcType of FCVT.H/ FCVT.S/ FCVT.D instruction: 0: n/a; 1: h; 2: s; 3: d

**Tweak 15: Command input/output encoding**

After upgrading to version 0.40, the microinstruction input/output field encoding method is as follows:

| Encoding | Input register field | Output register field |
|------|-------------|-----------------|
| 0 | R0 | Invalid output |
| 1-23 | R1-R23 | R1-R23 |
| 24-27 | T#1-T#4 | reserve reserve |
| 28-29 | U#1-U#2 | reserve reserve |
| 30 | U#3 | Uqueue |
| 31 | U#4 | T queue |

![v0.40src&dstasm.png](../figs/isa/version/v0.40src&dstasm.png)

**Adjustment 16: Delete some instructions**

Based on the architectural changes in version 0.40, the following instructions are no longer used and therefore deleted:

**addbpcf**, **addbpcn**, **setc.trap**, **setc.msg**, **ssrcrlt**, **tlbget**, **tlbset**, **tlbi**