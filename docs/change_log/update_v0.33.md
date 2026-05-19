# 0.33 version update

Date: November 3, 2023

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-v0.33](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100255827005)

## Change 1: LD/ST adds Scale and Unscale modes

Scaled/Unscaled refers to whether the right source operand SrcR is shifted according to the memory access bit width.

- **Scaled:** Address = SrcL + SrcR << size
- **Unscaled:** Address = SrcL + SrcR

Scaled and Unscaled are applicable to both `Reg+Reg` and `Reg+Imm`.

- **Scaled:** Address = SrcL + imm << size
- **Unscaled:** Address = SrcL + imm

In 0.33, LD uses an additional 1 bit in the Opcode to distinguish between scale and unscale. This 1 bit represents whether to shift.  
The advantage of this change is that the scaled expression range is larger and the data structure is increased from 2MB (12bit) to 16MB (15bit). At the same time, it gives the software more choices in misaligned scenarios.  

Load class instruction (Reg+imm) scaled mode encoding:

![load1-v0.33](../figs/isa/version/load1-v0.33.png)

Load class instruction (Reg+imm) unscaled mode encoding:

![load2-v0.33](../figs/isa/version/load2-v0.33.png)

Load.a class instruction (Reg+imm) scaled mode encoding:

![load3-v0.33](../figs/isa/version/load3-v0.33.png)

Load.a class instruction (Reg+imm) unscaled mode encoding:

![load4-v0.33](../figs/isa/version/load4-v0.33.png)

1. The original load/store encoding becomes scaled by default, and unscaled load and store are added in the new opcode space. Therefore, only new codes are added and the original codes remain unchanged.
2. Since there are few usage scenarios for SrcL-SrcR calculation addresses, the original ScaledLoad (Opcode = 7'b001_00X0) and ScaledStore (Opcode = 7'b001_01X0), that is, when Reg+Reg addressing is performed, the right source register no longer supports the inversion operation (.neg), and the low word interception signed/unsigned extension implementation (.sw and .uw) is retained.
3. The execution semantics of the original ScaledLoad (Opcode = 7'b001_00X1) and ScaledStore (Opcode = 7'b001_01X1), that is, Reg+Imm addressing, have changed: the immediate data is shifted according to the memory access bit width.
4. The encoding format of the original prf/prf.a instruction (Opcode = 7'b001_00X1) is removed, that is, the Reg+Imm format, and the corresponding execution semantics are implemented in the prf.ui/prf.uia instruction (Opcode = 7'b001_10X1).
5. The highest 3 bits in the encoding of the prf/prf.a instruction (Opcode = 7'b001_00X0) are defined as the `model` field, which is used to implement cache level settings for prefetch purposes.

Before update:

![prefetch-v0.32](../figs/isa/version/prefetch-v0.32.png)

After update:

![prefetch-v0.33](../figs/isa/version/prefetch-v0.33.png)

prefetch Model: 000: L1 Cache; 001: L2 Cache; 010: L3 Cache;

After adding unscaled mode, the comparison of immediate data shifts between scaled and unscaled load/store instructions is as follows:| Scaled Load | Scaled | Unscaled Load | Unscaled |
|-------------|-------------|------------|------------|
| lh | SrcL+simm<<1 | lh.ui | SrcL+simm |
| lw | SrcL+simm<<2 | lw.ui | SrcL+simm |
| ld | SrcL+simm<<3 | ld.ui | SrcL+simm |
| lhu | SrcL+simm<<1 | lhu.ui | SrcL+simm |
| lwu | SrcL+simm<<2 | lwu.ui | SrcL+simm |
| lh.a | SrcL+simm<<1 | lhu.uia | SrcL+simm |
| lw.a | SrcL+simm<<2 | lw.uia | SrcL+simm |
| ld.a | SrcL+simm<<3 | ld.uia | SrcL+simm |
| lhu.a | SrcL+simm<<1 | lhu.uia | SrcL+simm |
| lwu.a | SrcL+simm<<2 | lwu.uia | SrcL+simm |

| Scaled Store | Scaled | Unscaled Store | Unscaled |
|-------------|-------------|------------|------------|
| sh | SrcL+SrcR<<1 | sh.ur | SrcL+SrcR |
| sw | SrcL+SrcR<<2 | sw.ur | SrcL+SrcR |
| sd | SrcL+SrcR<<3 | sd.ur | SrcL+SrcR |
| sh.a | SrcL+SrcR<<1 | sh.ura | SrcL+SrcR |
| sw.a | SrcL+SrcR<<2 | sw.ura | SrcL+SrcR |
| sd.a | SrcL+SrcR<<3 | sd.ura | SrcL+SrcR |
| sh | SrcL+simm<<1 | sh.ui | SrcL+simm |
| sw | SrcL+simm<<2 | sw.ui | SrcL+simm |
| sd | SrcL+simm<<3 | sd.ui | SrcL+simm |
| sh.a | SrcL+simm<<1 | sh.uia | SrcL+simm |
| sw.a | SrcL+simm<<2 | sw.uia | SrcL+simm |
| sd.a | SrcL+simm<<3 | sd.uia | SrcL+simm |

Modify the assembly format of scaled mode load/store instructions,| Microinstructions | Assembly before update | Assembly after update |
|---------------|---------------|--------------------------------------------------------------------------------------------------|
| LH | lh \[SrcL, simm<<1\]<, {=>, ->}RegDst> | lh \[SrcL, simm\]<, {=>, ->}RegDst> |
| LW | lw \[SrcL, simm<<2\]<, {=>, ->}RegDst> | lw \[SrcL, simm\]<, {=>, ->}RegDst> |
| LD | ld \[SrcL, simm<<3\]<, {=>, ->}RegDst> | ld \[SrcL, simm\]<, {=>, ->}RegDst> |
| LBU | lbu \[SrcL, simm<<1\]<, {=>, ->}RegDst> | lbu \[SrcL, simm\]<, {=>, ->}RegDst> |
| LHU | lhu \[SrcL, simm<<2\]<, {=>, ->}RegDst> | lhu \[SrcL, simm\]<, {=>, ->}RegDst> |
| LWU | lwu \[SrcL, simm<<3\]<, {=>, ->}RegDst> | lwu \[SrcL, simm\]<, {=>, ->}RegDst> |
| LH.A | lh.a \[SrcL, simm<<1\]<, {=>, ->}RegDst> | lh.a \[SrcL, simm\]<, {=>, ->}RegDst> |
| LW.A | lw.a \[SrcL, simm<<2\]<, {=>, ->}RegDst> | lw.a \[SrcL, simm\]<, {=>, ->}RegDst> |
| LD.A | ld.a \[SrcL, simm<<3\]<, {=>, ->}RegDst> | ld.a \[SrcL, simm\]<, {=>, ->}RegDst> |
| LHU.A | lhu.a \[SrcL, simm<<1\]<, {=>, ->}RegDst> | lhu.a \[SrcL, simm\]<, {=>, ->}RegDst> |
| LWU.A | lwu.a \[SrcL, simm<<2\]<, {=>, ->}RegDst> | lhu.a \[SrcL, simm\]<, {=>, ->}RegDst> || Microinstructions | Assembly before update | Assembly after update |
|---------------|---------------------|--------------------------------------------------------------------------------|
| SH | sh SrcD, \[SrcL, SrcR<{.sw,.uw}><<1\] | sh SrcD, \[SrcL, SrcR<{.sw,.uw}>\] |
| SW | sw SrcD, \[SrcL, SrcR<{.sw,.uw}><<2\] | sw SrcD, \[SrcL, SrcR<{.sw,.uw}>\] |
| SD | sd SrcD, \[SrcL, SrcR<{.sw,.uw}><<3\] | sd SrcD, \[SrcL, SrcR<{.sw,.uw}>\] |
| SH.A | sh.a SrcD, \[SrcL, SrcR<{.sw,.uw}><<1\]<, {=>, ->}RegDst> | sh.a SrcD, \[SrcL, SrcR<{.sw,.uw}>\]<, {=>, ->}RegDst> |
| SW.A | sw.a SrcD, \[SrcL, SrcR<{.sw,.uw}><<2\]<, {=>, ->}RegDst> | sw.a SrcD, \[SrcL, SrcR<{.sw,.uw}>\]<, {=>, ->}RegDst> |
| SD.A | sd.a SrcD, \[SrcL, SrcR<{.sw,.uw}><<3\]<, {=>, ->}RegDst> | sd.a SrcD, \[SrcL, SrcR<{.sw,.uw}>\]<, {=>, ->}RegDst> || Microinstructions | Assembly before update | Assembly after update |
|---------------|---------------------|--------------------------------------------------------------------------------|
| SH | sh SrcL, [SrcR, simm<<1] | sh SrcL, [SrcR, simm] |
| SW | sw SrcL, [SrcR, simm<<2] | sw SrcL, [SrcR, simm] |
| SD | sd SrcL, [SrcR, simm<<3] | sd SrcL, [SrcR, simm] |
| SH.A | sh.a SrcL, [SrcR, simm<<1]<, {=>, ->}RegDst> | sh.a SrcL, [SrcR, simm]<, {=>, ->}RegDst> |
| SW.A | sw.a SrcL, [SrcR, simm<<2]<, {=>, ->}RegDst> | sw.a SrcL, [SrcR, simm]<, {=>, ->}RegDst> |
| SD.A | sd.a SrcL, [SrcR, simm<<3]<, {=>, ->}RegDst> | sd.a SrcL, [SrcR, simm]<, {=>, ->}RegDst> |

!!! note "note"
    The above are only modifications to the assembly format of the instructions, and the instruction semantics have not changed.

## Control block type to add BLB and BSBblock instruction

The purpose of adding BLB instructions is to improve memory access efficiency, and adding BSB instructions can reduce Load/Store conflicts.

For detailed introduction, you can view the implementation of each instruction.

- **BLBAR**: Memory load speculation barrier (Block Load Speculation Barrier).
- **BSBAR**: Memory write speculation barrier (Block Store Speculation Barrier).

!!! note "note"
   When a block instruction has memory to write a store, BSBblock instruction must be added. Without the block instruction, it means that there is no memory write in the current block.

## JR adds immediate data - multiplexes BCOND encoding

The JR instruction execution semantics and encoding have changed. For the updated instruction implementation and encoding, please see [JR](../isa/inst/misa_g/JR.md).

This change to the JR instruction is an optimization scenario for intra-block jumps. If you need to jump to the location of a symbol and the j instruction encoding is insufficient, you only need one addtpc and jr to complete it.

```
jmp_label:
   ......
   
addtpc %top_20bit(jmp_label)
jr t#1, %bottom_12bit(jmp_label)
```

Before updating, you need to use three instructions to complete:
```
jmp_label:
   ......
   
addtpc %top_20bit(jmp_label)
addi t#1, %bottom_12bit(jmp_label)
jr t#1
```

## Added ADDBPCN instruction and ADDBPCF instruction

Under CALLBLOCK, obtaining the BPC of the current or next header is a frequently used command. However, due to encoding restrictions, Next Block PC does not want to occupy the immediate field segment. Therefore, we added the ADDBPCF instruction. (Note: The lowest bit of Opcode of instructions using immediate data must be 1). Adding this instruction can speed up the access speed of CALL block.

- ADDBPCF: Add Block PC Fall Through, import the delayed BPC of the current block into the T register or RegDst register.

Under PGO and performance Debug, we need to obtain the PC value predicted by the current jump prediction. Achieve the effect of Branch Record.- ADDBPCN: Add Block PC Next, import the predicted next BPC of the current block into the T register or RegDst register.

After adding the ADDBPCN and ADDBPCF instructions, the opcode of the original ADDBPC instruction was adjusted:

Before modification:

![ADDBPC-v0.32](../figs/isa/version/ADDBPC-v0.32.png)

After modification:

![ADDBPC-v0.33](../figs/isa/version/ADDBPC-v0.33.png)

Due to encoding conflicts, `opcode` of the three instructions ADDBPC, ADDBPCN, and ADDBPCF has been readjusted.

Corrected encoding:

![ADDBPC-v0.33-1](../figs/isa/version/ADDBPC-v0.33-1.png)

## ADD/ADDW encoding adjustment

1. In order to avoid conflicts with all-0 encoding (illegal instructions), the add instruction encoding is adjusted: the high 3 bits of the instruction encoding (func field) are changed from 3’b000 to 3’b001.

![ADD-v0.33](../figs/isa/version/ADD-v0.33.png)

2. In order to adapt to the modification of the add instruction, the same adjustment is made to the addw encoding.

![ADDW-v0.33](../figs/isa/version/ADDW-v0.33.png)