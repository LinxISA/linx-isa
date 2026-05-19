# 0.36 version update

Update date: December 29, 2023

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-0.36](https://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100298001623)

## General description of version update| Change items | Change content | Reason for change |
|------------|---------------------------------|----------------------------------|
| header encoding | BrTypeExtend: 4bit->3bit; BlockOpcode: 7bit->8bit.  | Reduce decoding complexity.  |
| Standard Block | 1. BrTypeExtend of ECALL jump block: 4'b1011->3'b101;<br>2. BrTypeExtend of ERET jump block: 4'b1100->3'b110.  | header encoding is adjusted uniformly to reduce decoding complexity; reserve space is reserved.  |
| Standard block stdlp | 1. Added new standard block stdlp: BlockType: 3'b001;<br>2. No bitmask (default is all 1), extended field lengths such as BText/BNext Offset;<br>3. Added BranchHint field segment;<br>4. Added Likely BNextOffset to IND and INDCALL blocks for jump prediction.  | 1. Expand the length of fields such as BText/BNext Offset to reduce the number of lbref blocks;<br>2. Add the BranchHint field segment for branch and jump prediction enhancement.  |
| Standard Super Block stdh | BlockType: 3'b001 -> 3'b010.  | To remain consistent with the 6188 implementation version, the BlockType of the stdlp block is set to 3'b001, so the BlockType of the stdh block is adjusted to 3'b010.  |
| Standard floating-point block fp | Floating-point Block | 1. The standard floating-point block supports intra-block jump instructions;<br>2. Delete the floating-point super block fph.  | Standard floating point blocks and floating point super blocks are combined into one block to save coding space.  |
| Inline Block Inline Block | BlockType: 3'b110 -> 3'b101.  | header encoding is adjusted uniformly to reduce decoding complexity.  |
| template blockTemplate Block | 1. BlockType: 3'b111 -> 3'b110;<br>2. Add SrcVld and DstVld domain segments;<br>3. The BLBAR block is adjusted from controlling block type to template block;<br>4. mpush/mpopheader adds MemBitMask and signed imm fields.  | 1. header encoding is adjusted uniformly to reduce decoding complexity. <br>2. The BLBAR block itself is a template instruction, so it is adjusted to template block. <br>3. mpush/mpop is modified to be used for push/pop of discontinuous memory to improve the efficiency of data processing.  |
| Complex CISC blocks | Added 5 new types of CISC blocks: B.MOV, B.ADD, B.LJMP, B.COND, B.CALL | Only used to reserve encoding space.  |
| System Block System Block | 1. header encoding removes the bitmask, which is used for long indexes and long jump offsets;<br>2. Add ECALL blocks and ERET blocks. <br>3. The system block supports intra-block jump instructions and deletes the system super block sysh.  | 1. Same as standard block stdlp<br>2. Add ECALL and ERET: in order to maintain alignment with version 6188 1.0.  || Control Block | 1. The BNextOffset domain range of the LBREF block is reduced to 16 bits;<br>2. Delete the BSBAR block, and the StoreBarrier feature is placed in LBREFheader;<br>3. Remove the BLBAR block and add it to the template block type.  | The StoreBarrier feature is placed on LBREFheader, which can significantly reduce Codesize.  |
| Newly added microinstructions | 1. Added new comparison and jump microinstructions: setc.and and setc.or.  | 1. Statistics show that Specint accounts for 5% and is a hot scene command. Using this compound instruction can effectively reduce Codesize.  |
| Delete instructions | Inline block microinstructions delete inl.lconst/inl.lconstu/inl.addbpc and other instructions.  | The statistics are incorrect. inl.lconst/inl.lconstu/inl.addbpc is a false hotspot instruction, so it is removed. |
| system register | 1. system register adds: CID (physical core ID) and SYSCNT (local timestamp);<br>2. Modify the register ID of system registerBREF to 0x000F;<br>3. Modify the register ID of system registerCYCLE to 0x0C00.   | 1. Product OR requirements;<br>2. The original BREF register ID conflicts with the added CID register ID. <br>3. Keep consistent with the 6188 landing version.  |

## Change details

### 1.header encoding unified adjustment

In version 0.36, the BrTypeExtend field of header encoding is adjusted from the original 4bit to 3bit, and the BlockOpcode field is adjusted from the original 7bit to 8bit.

Version 0.35 header encoding format:

![header-v0.35](../figs/isa/version/header-0.35.png)

Version 0.36 header encoding format:

![header-v0.36](../figs/isa/version/header-0.36.png)

### 2. Standard block std

To adapt to the unified adjustment of header encoding, the BrTypeExtend encoding of ECALL and ERET blocks in the standard block is modified as follows:

ECALL block: **4'b1011** modified to **3'b101**; ERET block: **4'b1100** modified to **3'b110**

Version 0.35 ECALL and ERET block encoding:

![std-v0.35](../figs/isa/version/std-0.35.png)

Version 0.36 ECALL and ERET block encoding:

![std-v0.36](../figs/isa/version/std-0.36.png)

### 3. Add standard block stdlp

Standard block stdlp (Standard Block with Long Pointer): headerbody of the standard block is separated and has no bitmask (the default bitmask is all 1). It is mainly used to jump and identify the range of block instruction.

- Microinstructions within the block use 32bit encoding space.
- The range of BTextStartOffset is extended to **26bit**, the range of BNextOffset is extended to **25bit**, and the range of BEndOffset is extended to **10bit**.
- The LikelyBNextOffset field is added to the two jump type blocks of IND and INDCALL, and the range is extended to 22bit for jump prediction.
- Added the BranchHint field, which is used to jump to information prompts. For specific definitions, see the table below.

![stdlp-v0.36](../figs/isa/version/stdlp-0.36.png)

headerBranchHint field segment description

![branchHint](../figs/isa/version/branchHint.png)

### 4. Standard super block stdhIn order to remain consistent with version 6188-1.0, the BlockType of the stdlp block is set to 3'b001, so the BlockType of the stdh block is adjusted to **3'b010**.

Version 0.35 stdh block encoding:

![stdh-v0.35](../figs/isa/version/stdh-0.35.png)

Version 0.36 stdh block encoding:

![stdh-v0.36](../figs/isa/version/stdh-0.36.png)

### 5. Standard floating point block

In order to save block instruction encoding space, in this version we choose to delete the standard floating point super block fph, leaving the standard floating point block fp. At the same time, it is defined that the standard floating point block supports intra-block jump instructions, that is, in terms of the function of the block engine, the current version of the fp block is equivalent to the previous version of the fph block, but the encoding space of the previous version of the fp block is still used.

Version 0.36 fp block encoding:

![fp-0.36](../figs/isa/version/fp-0.36.png)

### 6. Inline block modification

The BlockType of the inline block block instruction is adjusted from **3'b110** to **3'b101**.

Version 0.36 inline block header encoding:

![inline-0.36](../figs/isa/version/inline-0.36.png)

### 7.template block adjustment

- Unified modification of template block encoding:
    * The BlockType of template blockblock instruction is adjusted from 3'b111 to 3'b110.
    * Unified adjustment to adapt to header encoding: BrTypeExtend field (header[8:5]->header[7:5]) is changed from 4bit to 3bit.
    * Add SrcVld and DstVld field segments to quickly determine dependencies between blocks and reduce hardware decoding complexity.
- FENTRY, FEXIT, FTEXIT block: After adding the encoding space of SrcVld and DstVld, the position conflicts with unsigned imm[18:11] of the immediate high bit, so the position of the immediate high bit is adjusted.
- The jump type of the FTEXIT block is adjusted to the IND (Indirect) type (3’b100 -> 3’b010). This modification is used to improve the accuracy of hardware RAS jump prediction.
- BLBAR block changed from controlling block type to template block:
    * BlockOpcode changed from **4'b0001** to **4'b0010**.
    * After uniformly increasing the coding space of SrcVld and DstVld, the coding positions of fields such as prefetch_count/offset/prefetch Model were adjusted.
    * MPUSH/MPOP adds the MemBitMask field for push and pop of discontinuous memory; adds the Store/Load Offset (i.e. igned imm) field for the offset of address calculation.

Version 0.35 template block encoding:

![memblock-v0.35](../figs/isa/version/memblock-0.35.png)

Version 0.36 template block encoding:

![memblock-v0.36](../figs/isa/version/memblock-0.36.png)

Additional modifications:

#### template blockFEXIT Adjustment

FEXIT modified usage scenario

Scenario 1: The function ends with a function call f.exit+bnext.direct
```c
extern int add(int, int);
int f1(int a, int b) { 
return add(a, b);
}
```
Scenario 2: The function ends with a function pointer call f.exit+bnext.indirect
```c
extern int add(int, int); 
extern int sub(int, int); 
int f2(int a, int b, int cond) {
int (*functionPtr)(int, int);
functionPtr = cond > 0 ? add : sub;
return functionPtr(a, b); 
}
```
FEXIT instruction encoding adjustment

The jump type is changed from Return to Fall, and the BrTypeExtend field encoding is changed to 3’b001.

Original code:

![fexit-0.35](../figs/isa/version/fexit-0.35.png)

Updated coding:
 
![fexit-0.36](../figs/isa/version/fexit-0.36.png)

Modify the microinstruction sequence of FEXIT block expansion

The jump type is changed from the original Return to the Fall type, so there is no need to set CARG.TGT in the block, that is, the setc.tgt instruction expanded in the block is deleted.Take the microinstruction sequence expanded by block instruction f.exit [ra, s0, s1, s2, s3, s4, s5], sp!, 144 as an example:
```asm
addi sp, 144, => sp
ldi [sp, 136], => ra
setc.tgt  t#1 ------->去掉该指令
ldi [sp, 128], => s0
ldi [sp, 120], => s1
ldi [sp, 112], => s2
ldi [sp, 104], => s3
ldi [sp,  96], => s4
ldi [sp,  88], => s5
```

2. Adjustment of template blockFTEXIT

The FTEXIT instruction name is changed to **FRET**, and the assembly identifier is `f.ret`.

FRET(FTEXIT) is adjusted to be used in the scenario of normal return at the end of the function:

Scenario 1: The function ends with ret normally, and there are no sub-functions inside the function, f.ret (RA reads directly)
```c
extern int symbol; 
int f3() { 
return symbol; 
}
```
Scenario 2: The function ends with ret normally, and there are sub-functions inside the function, f.ret (RA loads from the stack)
```c
# include "stdio.h"
extern int symbol; 
int f4(int a, int b) {
printf("Linx\n"); 
return symbol;
}
```

FRET (FTEXIT) encoding adjustment

* The FRET block jump type is changed from IND (indirect) to RETURN, and the BrTypeExtend field encoding is changed to 3’b100.
* The default encoding of the RegRet field segment is 4’b0000 (corresponding to the Ra/R0 register)
* srcvld[1] is modified to be codable: encoding is 1, indicating that the instruction input contains the Ra register; encoding is 0, indicating that the instruction input does not include the Ra register.

![fret-0.35](../figs/isa/version/fret-0.35.png)

Updated coding:
 
![fret-0.36](../figs/isa/version/fret-0.36.png)

3. Modification of assembly syntax

Original assembly format: `f.texit [RegDst0, RegDst1, RegDst2, ..., RegDstn], RegPtr!, RegRet, uimm19`
Modified assembly format: `f.ret [RegDst0, RegDst1, RegDst2, ..., RegDstn], RegPtr!, <Ra>, uimm19`

<Ra> in assembly format: Indicates whether Ra is optional as block instruction input. That is:

`f.ret [RegDst0, RegDst1, RegDst2, ..., RegDstn], RegPtr!, Ra, uimm19` indicates that the instruction input includes the RegPtr and Ra registers, and the return address is obtained by directly reading the Ra register.
`f.ret [RegDst0, RegDst1, RegDst2, ..., RegDstn], RegPtr!, uimm19` means that the instruction input is only the RegPtr register, and the return address is loaded from the stack.

Adjustment of FRET block microinstruction expansion sequence

If header.vld is marked as 1, it means directly reading the Ra register value as the return address. The corresponding microinstruction expansion sequence takes block instruction `f.ret [s0, s1, s2], sp!, ra, 24` as an example:
```asm
setc.tgt ra
addi sp, 24, => sp
ldi [sp, 16], => s0
ldi [sp,  8], => s1
ldi [sp,  0], => s2
```
If the header.vld mark is 0, it means that the instruction input does not contain Ra, and the return address needs to be loaded from the stack (at this time, bsetmask bit[0] needs to be set).
The corresponding microinstruction expansion sequence takes block instruction `f.ret [ra, s0, s1, s2], sp!, 32` as an example:
```asm
addi sp, 32, => sp
ldi [sp, 24], => ra
setc.tgt t#1
ldi [sp, 16], => s0
ldi [sp,  8], => s1
ldi [sp,  0], => s2
```

template block modified encoding

![TEMLP](../figs/isa/version/tempb-0.36.png)

### 8. Added complex CISC blocks

The new CISC block BlockType uses **3'b110** encoding space and shares this space with template block.

![cisc-v0.36](../figs/isa/version/cisc-0.36.png)

### 9. System block modification

1. System block instruction adds two jump type blocks, ECALL and ERET, among which the ECALL block is used to end the program.
2. The system header encoding removes the bitmask and adds long index and long jump offset encoding space.
3. The BranchHint field is added to the system block header, and the definition is the same as described in the previous standard block stdlp.
4. Delete the system super block sysh

Note: The system block does not support inter-block jumps other than the FALL type, but supports intra-block jumps (when accessing system register, spin lock, CMO instructions, if a jump instruction is required, intra-block jumps can be used).

![sys-v0.36](../figs/isa/version/sys-0.36.png)

### 10. Control block encoding adjustment

In order to reduce hardware Load/Store conflicts, version 0.33 adds a BSBAR block in the control block type. In this way, a BSBAR block needs to be added before all blocks containing store instructions. If the jump offset or index offset of the block is not enough, an LBREF block needs to be added before the block to store the additional offset, which causes the code size to expand.Therefore, in version 0.36, we deleted the encoding of BSBARblock instruction, retained its characteristics, and placed the characteristics of BSBAR on LBREFheader. The specific modifications to LBREF are as follows:

1. Added the store_count and SpecType fields of the original BSBARheader (using space Header[15:10] and Header[9:8] respectively)
2. Reduced the space of BNextOffset field from the original 23bit to **16bit**.

Coding before update:

![LBREF-v0.35](../figs/isa/version/LBREF-0.35.png)

Updated coding:

![LBREF-v0.36](../figs/isa/version/LBREF-0.36.png)

### 11. New microinstructions

Add a system block instruction[DC.ZVA](../isa/inst/misa_s/DC.ZVA.md) to clear the cacheline.

### 12. Delete command

Version 0.35 is updated and released with the inline block and the 120+ microinstructions it supports.

However, during subsequent verification, it was found that i**nl.lconst**, **inl.lconstu**, and **inl.addbpc** were false hotspot instructions. At the same time, the hardware's processing of these instructions was relatively complex, so these three instructions were removed from the current version.

### 13.Changes of system register

- In order to meet product OR requirements, add two system register:
    * CID (Physical Core ID) - SSR ID is **0x0030**
    * SYSCNT (local timestamp) - SSR ID is **0x0C01**
- Modify the original register ID:
    * The SSR ID of the original BREF register conflicts with the new CID register. In order to be consistent with the 6188 landing version, the ID of the BREF register is modified to 0x000F.
    * In order to be consistent with the 6188 landing version, modify the ID of the CYCLE register to **0x0C00**.