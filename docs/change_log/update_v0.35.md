# Version 0.35 update

Date: December 11, 2023

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-v0.35](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100261469689)

## General description of version update

1. The main update of this version of the instruction set is the addition of inline block design.
2. The LBREFheader`BTextStartOffset` field is multiplexed into the LCONST field.
3. Encoding adjustment of BLBARblock instruction.
4. Addc, subc, fmadd instruction encoding adjustment.

## Add inline block

The layered design of the Header Body not only causes the expansion of the CodeSize but also hinders further improvement of performance when faced with smaller Blocks. For this reason, in LinxISA-0.35, we refer to CISC instructions. For small blocks, we directly use Header to express the semantics of microinstructions + jumps at the same time. The benefits of this design are: for small pieces of pure data movement, the efficiency of data movement directly in the Header will be higher. For small blocks that are larger than 2 (32bits) instructions and can be encoded into Inline Block, the benefits of CodeSize will be obtained.

### 1.header encoding

The header encoding of inline block instruction is shown below:

![inlineblock-v0.35](../figs/isa/version/inlineblock-0.35.png)

### 2. Introduction to intra-block microinstructions

- Inline block instruction set uses 12bit encoding space.
- Microinstructions are embedded in header. Each header can express up to 4 microinstructions and 1 inter-block jump instruction.
- If the code is less than 4 microinstructions, the inl.nop instruction must be used to occupy the free position.
- In header, bget/bset does not require explicit declaration.
- Microinstructions within the block need to be prefixed with `inl.`.
- Inline blocks can inherit the T register of the previous block.

The inline block microinstruction assembly format and explanation are as follows:| Opcode | Assembly Syntax | Explanation |
|----------|--------------------------------|---------------------|
| INL.CONST | inl.const simm8 | Load the sign-extended 8-bit signed immediate number and write it to the destination T register |
| INL.MOVI | inl.movi simm4, => RegDst | Load 4-bit signed immediate data and write to the destination T register and RegDst register |
| INL.ADDI | inl.addi RegSrc, simm4 | Calculate the value of the register plus the immediate number and write it to the destination T register |
| INL.MOVR | inl.movr RegSrc, => RegDst | Copy the value of the source register to the destination T register and RegDst register |
| INL.LOADI | inl.loadi [t#1, uimm5] | Load the corresponding byte data from the address of the previous instruction result plus the shifted immediate offset and write it to the destination T register |
| INL.MOVT | inl.movt t#l, => RegDst | The results of the previous 1-4 instructions are written to the destination T register and RegDst register |
| INL.LOADR | inl.loadr [RegSrc, t#1] | Load the corresponding byte of data from the left source register plus the address memory of the result of the previous instruction and write it to the destination T register |
| INL.ADD | inl.add RegSrc, t#1, => RegDst | Add the result of the previous instruction to the left source register and write it to the destination T register and RegDst register |
| INL.BINOPI | inl.binopi t#1, simm4 | Two-input short instruction, one register and one immediate input |
| INL.LOADI | inl.loadi [t#1, 0], => RegDst | Load the corresponding byte data from the address memory corresponding to the result of the previous instruction and write it to the destination T register and RegDst register |
| INL.BINOP | inl.binop RegSrc, t#1 | Two-register input short instruction |
| INL.SUB | inl.sub RegSrc, t#1, => RegDst | Subtract the result of the previous instruction from the left source register and write it to the destination T register and RegDst register |
| INL.ALLOP | inl.allop t#1, t#r | Instructions containing most of the two T register inputs |
| INL.MOV2NI | inl.mov2ni simm, => RegDst | Write the immediate number to the Nth power of 2 as the exponent to the destination T register and RegDst register |
| INL.STORE | inl.store t#2, [RegSrc, t#1] | Write the result of the second previous instruction to the memory where the destination address is located |
| INL.LD | inl.ld [RegSrc, t#1], => RegDst | Load 8 bytes of data from the source address and write to the destination T register and RegDst register |

<!-- 
有关内联块的定义详见[内联块介绍](./isa/blockIntro/inline_block.md)
 -->

## Control block instructionLBREFheader to add LCONST domain segment

In order to adapt to the inl.lconst, inl.addbpc and other micro-instructions added in the inline block, the **LCONST** field segment reuses the original **BTextStartOffset** field segment of the LBREFheader. That is, when the LBREF block is followed by an Inline Block, this segment is used to store the 32-bit LCONST long immediate number, which can be indexed by the lconst instruction in the following Inline Block.

![LBREF-0.35](../figs/isa/version/LBREF-0.35.png)

## Instruction encoding modification

### 1. Adjustment of BLBAR instruction encoding in control blockAfter version 0.31 updates the encoding of header, the high 16 bits of headerBInst[63:32] are used to encode the input of block instruction (BGET MASK), and the low 16 bits are used to encode the output of block instruction (BSET MASK). In order to unify the encoding format, the LoadBase0 field segment encoding is changed to the BInst[51:48] position in the upper 16 bits. At the same time, it is renamed RegPtr to avoid misleading. This field segment is used to store the first layer architectural registerID and index the first layer architectural registerR0-R15.

In the initial version definition, block_size in BLBARheader encoding: 2’b00 means prefetching data in 32byte units; 2’b01 means prefetching data in 64byte units. But in fact, hardware prefetching is based on Cacheline (64byte), so the BlockSize field segment in the header encoding is changed to the fixed encoding 2'b01.

Before coding update:

![BLBAR-0.34](../figs/isa/version/BLBAR-0.34.png)

After coding update:

![BLBAR-0.35](../figs/isa/version/BLBAR-0.35.png)

### 2. ADDC, SUBC, FMADD instruction encoding and semantic adjustment

Like the conditional selection instruction csel, addc, subc and fmadd are also three-register input instructions. In order to simplify the compiler implementation, these instructions cancel the restriction of the second source register in the current version (in previous versions, the R/L before the SrcR field in the instruction encoding was fixedly encoded as 0, that is, SrcR can only index the global register R0 and private registers R1-R15). The csel, addc, subc and fmadd instructions now allow all three register inputs to be T registers. The hardware will split the third T register into a Dummy Local GPR mov plus a normal three-input instruction.

For example, a `csel t#l, t#r, t#c` instruction is split into:
```asm
addi t#c, 0, -> r0
csel  t#l, t#r, r0
```
where r0 is a hardware-defined Local R0 register.

Coding before modification:

![ADDC-0.34](../figs/isa/version/ADDC-0.34.png)
![FMADD-0.34](../figs/isa/version/FMADD-0.34.png)

Coding before modification:

![ADDC-0.35](../figs/isa/version/ADDC-0.35.png)
![FMADD-0.35](../figs/isa/version/FMADD-0.35.png)