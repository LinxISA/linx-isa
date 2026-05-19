# 0.34 version update

Date: December 6, 2023

For the path to the web version of the instruction encoding design document, please see [LinxISA Encoding-v0.34](http://dbox.huawei.com/detaildocs?oid=VR%3Awt.doc.WTDocument%3A100258403959)

## General description of version update

1. Added implementation of 13 floating point instructions.
2. Updates to load/store instructions: (1) Split of address offset shift type (scaled) load/store instructions; (2) Address offset non-shift type (unscaled) load/store instruction assembly name modification (3) Add an empty store instruction.
3. Some instruction encoding adjustments: (1) System instruction encoding adjustment; (2) Arithmetic operation shift instruction encoding adjustment; (3) Partial template block instruction encoding adjustment; (4) Conditional selection instruction CSEL encoding adjustment
4. Some instruction assembly format modifications: (1) l1/l2/l3 Cache identifiers are added to the prefetch instruction assembly format; (2) the destination register is removed from the template block instructionB.MCOPY and B.MSET assembly formats
5. The CARG register removes the BSET/BGET/MSG field segments and changes it to a 64bit register.

## Modification 1: Add floating point instruction implementation

**Floating point calculation class**

| Microinstructions | Assembly format | Description |
|--------------|-------------------------------------------------|----------------|
| fadd | fadd{.d,.s,.h} SrcL, SrcR<, {=>, ->}RegDst> | Floating point addition |
| fsub | fsub{.d,.s,.h} SrcL, SrcR<, {=>, ->}RegDst> | Floating point subtraction |
| fmul | fmul{.d,.s,.h} SrcL, SrcR<, {=>, ->}RegDst> | Floating point multiplication |
| fmadd | fmadd{.d,.s,.h} SrcL, RSR, t#c<, {=>, ->}RegDst> | Floating point multiply and add |
| fdiv | fdiv{.d,.s,.h} SrcL, SrcR<, {=>, ->}RegDst> | Floating point division |
| fabs | fabs{.d,.s,.h} SrcL<, {=>, ->}RegDst> | Floating point absolute value |
| fsqrt | fsqrt{.d,.s,.h} SrcL<, {=>, ->}RegDst> | Floating point square root |

**Floating point conversion class**

| Microinstructions | Assembly format | Description |
|----------|----------------------------------|--------------|
| fcvt | fcvt.dstT SrcL.srcT<, {=>, ->}RegDst> | Floating point conversion |

**Floating point comparison class**| Microinstructions | Assembly format | Description |
|--------------|------------------|---------------------------------|
| feq | feq{.d,.s,.h} srcL, srcR<, {=>, ->}RegDst> | Floating point equality comparison |
| fle | fle{.d,.s,.h} srcL, srcR<, {=>, ->}RegDst> | Floating point less than or equal to comparison |
| flt | flt{.d,.s,.h} srcL, srcR<, {=>, ->}RegDst> | Floating point less than comparison |

**Maximum value class**

| Microinstructions | Assembly format | Description |
|--------------|------------------|---------------------------------|
| fmax | fmax{.d,.s,.h} srcL, srcR<, {=>, ->}RegDst> | Floating point maximum value |
| fmin | fmin{.d,.s,.h} srcL, srcR<, {=>, ->}RegDst> | Floating point minimum value |

## Modification 2, Load/Store command changes

1. The load/store instructions of the addressing offset shift class (scaled mode) are split into two instructions according to the two encoding formats `Reg + Reg` and `Reg + Imm`.

- `Reg + Reg` encoding format: keep the original command name unchanged.
- `Reg + Imm` encoding format: Add "**I**" to the original instruction name to indicate that the instruction is a load/store instruction using immediate offset, adding an instruction. For example: `LB -> LBI`, `SD -> SDI`, `LW.A -> LWI.A`, `SD.A -> SDI.A`

**Modification of Load command**| Original instruction name | Split instruction name | Assembly example | Explanation |
|-----------|---------------|---------------------|-----------------------------------------------------------------------------|
| LB | LB<br>LBI | lb [a1, a2 << shamt]<br>lbi [a1, imm] | The memory access address is a1 + (a2 << shamt), no fixed shift<br>The memory access address is a1 + imm, no shift by default |
| LH | LH<br>LHI | lh [a1, a2 << shamt]<br>lhi [a1, imm] | The access address is a1 + (a2 << shamt), no fixed shift<br>The access address is a1 + (imm << 1), the default left shift is 1 bit |
| LW | LW<br>LWI | lw [a1, a2 << shamt]<br>lwi [a1, imm] | The access address is a1 + (a2 << shamt), no fixed shift<br>The access address is a1 + (imm << 2), the default left shift is 2 bits |
| LD | LD<br>LDI | ld [a1, a2 << shamt]<br>ldi [a1, imm] | The access address is a1 + (a2 << shamt), no fixed shift<br>The access address is a1 + (imm << 3), the default left shift is 3 bits |
| LBU | LBU<br>LBUI | lbu [a1, a2 << shamt]<br>lbui [a1, imm] | The access address is a1 + (a2 << shamt), no fixed shift<br>The access address is a1 + imm, no shift by default |
| LHU | LHU<br>LHUI | lhu [a1, a2 << shamt]<br>lhui [a1, imm] | The access address is a1 + (a2 << shamt), no fixed shift<br>The access address is a1 + (imm << 1), the default left shift is 1 bit |
| LWU | LWU<br>LWUI | lwu [a1, a2 << shamt]<br>lwui [a1, imm] | The access address is a1 + (a2 << shamt), no fixed shift<br>The access address is a1 + (imm << 2), the default left shift is 2 bits |
| LB.A | LB.A<br>LBI.A | lb.a [a1, a2 << shamt]<br>lbi.a [a1, imm] | The memory access address is a1 + (a2 << shamt), no fixed shift<br>The memory access address is a1 + imm, no shift by default |
| LH.A | LH.A<br>LHI.A | lh.a [a1, a2 << shamt]<br>lhi.a [a1, imm] | The access address is a1 + (a2 << shamt), no fixed shift<br>The access address is a1 + (imm << 1), the default left shift is 1 bit |
| LW.A | LW.A<br>LWI.A | lw.a [a1, a2 << shamt]<br>lwi.a [a1, imm] | The access address is a1 + (a2 << shamt), no fixed shift<br>The access address is a1 + (imm << 2), the default left shift is 2 bits || LD.A | LD.A<br>LDI.A | ld.a [a1, a2 << shamt]<br>ldi.a [a1, imm] | Access address is a1 + (a2 << shamt), no fixed shift<br>Access address is a1 + (imm << 3), default left shift is 3 bits |
| LBU.A | LBU.A<br>LBUI.A | lbu.a [a1, a2 << shamt]<br>lbui.a [a1, imm] | The memory access address is a1 + (a2 << shamt), no fixed shift<br>The memory access address is a1 + imm, no shift by default |
| LHU.A | LHU.A<br>LHUI.A | lhu.a [a1, a2 << shamt]<br>lhui.a [a1, imm] | The access address is a1 + (a2 << shamt), no fixed shift<br>The access address is a1 + (imm << 1), the default left shift is 1 bit |
| LWU.A | LWU.A<br>LWUI.A | lwu.a [a1, a2 << shamt]<br>lwui.a [a1, imm] | The access address is a1 + (a2 << shamt), no fixed shift<br>The access address is a1 + (imm << 2), the default left shift is 2 bits |

**Modification of Store directive**| Original instruction name | Split instruction name | Assembly example | Explanation |
|-----------|---------------|---------------------|-----------------------------------------------------------------------------|
| SB | SB<br>SBI | sb a0, [a1, a2]<br>sbi a0, [a1, imm] | The access address is a1 + a2, not shifted by default<br>The access address is a1 + imm, not shifted by default |
| SH | SH<br>SHI | sh a0, [a1, a2]<br>shi a0, [a1, imm] | The memory access address is a1 + (a2 << 1), the default left shift is 1 bit<br> The memory access address is a1 + (imm << 1), the default left shift is 1 bit |
| SW | SW<br>SWI | sw a0, [a1, a2]<br>swi a0, [a1, imm] | The memory access address is a1 + (a2 << 2), the default left shift is 2 bits<br> The memory access address is a1 + (imm << 2), the default left shift is 2 bits |
| SD | SD<br>SDI | sd a0, [a1, a2]<br>sdi a0, [a1, imm] | The memory access address is a1 + (a2 << 3), the default left shift is 3 bits<br> The memory access address is a1 + (imm << 3), the default left shift is 3 bits |
| SB.A | SB.A<br>SBI.A | sb.a a0, [a1, a2]<br>sbi.a a0, [a1, imm] | The memory access address is a1 + a2, not shifted by default<br>The memory access address is a1 + imm, not shifted by default |
| SH.A | SH.A<br>SHI.A | sh.a a0, [a1, a2]<br>shi.a a0, [a1, imm] | The access address is a1 + (a2 << 1), the default left shift is 1 bit<br> The access address is a1 + (imm << 1), the default left shift is 1 bit |
| SW.A | SW.A<br>SWI.A | sw.a a0, [a1, a2]<br>swi.a a0, [a1, imm] | The memory access address is a1 + (a2 << 2), the default left shift is 2 bits<br> The memory access address is a1 + (imm << 2), the default left shift is 2 bits |
| SD.A | SD.A<br>SDI.A | sd.a a0, [a1, a2]<br>sdi.a a0, [a1, imm] | The memory access address is a1 + (a2 << 3), the default left shift is 3 bits<br>The memory access address is a1 + (imm << 3), the default left shift is 3 bits |

2. In order to unify the naming format, modify the load/store instruction name of the addressing offset non-shift class (unscaled mode).

**Modification of Load command**| Original instruction name | Modified name | Assembly example | Explanation |
|----------|-------------|------------------------|---------------------------------------------|
| LH.UI | LHI.U | lhi.u [a1, imm] | The access address is a1 + imm, no default shift is performed |
| LW.UI | LWI.U | lwi.u [a1, imm] | The access address is a1 + imm, no default shift is performed |
| LD.UI | LDI.U | ldi.u [a1, imm] | The access address is a1 + imm, no default shift is performed |
| LHU.UI | LHUI.U | lhui.u [a1, imm] | The access address is a1 + imm, no default shift is performed |
| LWU.UI | LWUI.U | lwui.u [a1, imm] | The access address is a1 + imm, no default shift is performed |
| PRF.UI | PRFI.U | prfi.u.l1 [a1, imm] | The access address is a1 + imm, no default shift is performed |
| LB.UIA | LBI.UA | lbi.ua [a1, imm] | The access address is a1 + imm, no default shift is performed |
| LH.UIA | LHI.UA | lhi.ua [a1, imm] | The access address is a1 + imm, no default shift is performed |
| LW.UIA | LWI.UA | lwi.ua [a1, imm] | The access address is a1 + imm, no default shift is performed |
| LD.UIA | LDI.UA | ldi.ua [a1, imm] | The access address is a1 + imm, no default shift is performed |
| LHU.UIA | LHUI.UA | lhui.ua [a1, imm] | The access address is a1 + imm, no default shift is performed |
| LWU.UIA | LWUI.UA | lwui.ua [a1, imm] | The access address is a1 + imm, no default shift is performed |
| PRF.UIA | PRFI.UA | prfi.ua.l1 [a1, imm] | The access address is a1 + imm, no default shift is performed |

**Modification of Store directive**| Original instruction name | Modified name | Assembly example | Explanation |
|----------|-------------|------------------------|---------------------------------------------|
| SH.UR | SH.U | sh.u a0, [a1, a2] | The access address is a1 + a2, no default shift is performed |
| SW.UR | SW.U | sw.u a0, [a1, a2] | The access address is a1 + a2, no default shift is performed |
| SD.UR | SD.U | sd.u a0, [a1, a2] | The access address is a1 + a2, no default shift is performed |
| SH.URA | SH.UA | sh.ua a0, [a1, a2] | The access address is a1 + a2, no default shift is performed |
| SW.URA | SW.UA | sw.ua a0, [a1, a2] | The access address is a1 + a2, no default shift is performed |
| SD.URA | SD.UA | sd.ua a0, [a1, a2] | The access address is a1 + a2, no default shift is performed |
| SH.UI | SHI.U | shi.u a0, [a1, imm] | The access address is a1 + imm, no default shift is performed |
| SW.UI | SWI.U | swi.u a0, [a1, imm] | The access address is a1 + imm, no default shift is performed |
| SD.UI | SDI.U | sdi.u a0, [a1, imm] | The access address is a1 + imm, no default shift is performed |
| SH.UIA | SHI.UA | shi.ua a0, [a1, imm] | The access address is a1 + imm, no default shift is performed |
| SW.UIA | SWI.UA | swi.ua a0, [a1, imm] | The access address is a1 + imm, no default shift is performed |
| SD.UIA | SDI.UA | sdi.ua a0, [a1, imm] | The access address is a1 + imm, no default shift is performed |

3. Add a store instruction SNOP (Store NOP)

This store instruction **does not write memory** and only occupies Store Buffer Entry (used with BSBAR memory write barrier block instruction).

The instructions are encoded as follows:

![SN](../figs/isa/version/SN.png)

## Modification 3. Instruction encoding adjustment

### System block instruction encoding adjustment

In order to facilitate hardware decoding implementation and standardize the encoding and decoding format, we hope that the lowest bit of the **Opcode** field segment in the instruction encoding using immediate data is **1**. Therefore, the encoding of system instructions including SSRGET, SSRSET, SSRCRLT (and its expansion instructions) has been adjusted.

Specifically: change the Opcode from the original `7'b100_0000` to `7'b100_0001`.

Updated encoding:

![sysinst-v0.34](../figs/isa/version/sysinst-v0.34.png)

### Shift instruction encoding adjustment

In order to improve the standardization of the instruction encoding and decoding format, firstly, the high-order bits of the shift instructions are divided into more clear geographical segments. At the same time, the func fields (encoded 12-14 bits) of the SRA{I,W,IW} instructions and the SRL{I,W,IW} instructions use the same encoding, and are distinguished in the high-order func fields. This can reserve space for adding shift instructions in future versions. The func field (encoded 12-14bit) of the SLL{I,W,IW} instruction has been modified accordingly.

Coding before modification:

![shift-v0.33](../figs/isa/version/shift-0.33.png)

Modified encoding:

![shift-v0.34](../figs/isa/version/shift-0.34.png)### Template block instruction encoding adjustment

In the current version, saving the status of B.MCOPY and B.MSET when they are interrupted during execution can be implemented using the exception block, so these two instructions do not require the encoding of the output register. Therefore, the RegDst0-RegDst2 field segments in the B.MCOPY and B.MSET instruction codes are deleted and replaced with the placeholder value 4’b0000.

Coding before modification:

![memblock-v0.33](../figs/isa/version/memblock-0.33.png)

Modified encoding:

![memblock-v0.34](../figs/isa/version/memblock-0.34.png)

In the previous version, the immediate value of template block was encoded as 15 bits (the lower three bits were 0). However, when the instruction was implemented, the 15-bit immediate value could not be expressed in a microinstruction, so the implementation of template block was modified. When the effective bits of the immediate data exceed 12 bits, a combination of three instructions is used to splice the long immediate data in header. Since the modified implementation can handle more than 12-bit immediate numbers, it is better to expand the range of immediate numbers at the same time and encode all 16-31 bits encoded by block instruction as immediate numbers. In this way, 19-bit immediate numbers can be expressed, and the stack space available for instructions is larger. Therefore, adjustments are made to the immediate field segments of the three block instruction codes: template blockfentry, fexit, and ftexit.

Coding before modification:

![temlblock-v0.33](../figs/isa/version/temlblock-0.33.png)

Modified encoding:

![temlblock-v0.34](../figs/isa/version/temlblock-0.34.png)

After the block instruction encoding is modified, the immediate number in header can express a 19-bit immediate number (the lower three bits default to 0). When the effective digits of the immediate data expressed by header exceed 12 bits, a combination of multiple instructions is used to splice the long immediate data expressed by header. The following uses the F.ENTRY instruction as an example to illustrate this modification:

- Execution method before modification:
```c
subi RegPtr, imm, => RegPtr

sd RegSrc0, [RegPtr, -8]
sd RegSrc1, [RegPtr, -16]
sd RegSrc2, [RegPtr, -24]
...
sd RegSrcn, [RegPtr, -8*m]
```
- Modified execution method:
```c
if uimm19[18:12] != 0:
    lui {13'b0 + uimm19[18:12]}
    addi t#1, uimm19[11:0]
    sub RegPtr, t#1, => RegPtr
else:
    subi RegPtr, uimm19[11:0], => RegPtr

sd RegSrc0, [RegPtr, -8]
sd RegSrc1, [RegPtr, -16]
sd RegSrc2, [RegPtr, -24]
...
sd RegSrcn, [RegPtr, -8*m]
```

### Control block instruction encoding adjustment

#### BLBARblock instruction encoding adjustment

In the encoding format of BLBARheader, the high 16 bits of BInst[63:32] are used to encode the input of block instruction, and the low 16 bits are used to encode the output of block instruction. In order to unify the encoding format, the LoadBase0 field segment encoding is changed to the BInst[51:48] position and renamed `RegPtr`. This field segment is used to store the first layer architectural registerID and index the first layer architectural registerR0-R15.

At the same time, the prefetch size of this instruction is based on one Cacheline (64byte), so the BlockSize field segment in the original header encoding is changed to the fixed encoding **2'b01**.

Before coding update:

![BLBAR-0.33](../figs/isa/version/BLBAR-0.33.png)

After coding update:

![BLBAR-0.34](../figs/isa/version/BLBAR-0.34.png)

#### BSBARblock instruction encoding adjustment

Before coding update:

![BSBAR-0.33](../figs/isa/version/BSBAR-0.33.png)

After coding update:

![BSBAR-0.34](../figs/isa/version/BSBAR-0.34.png)

!!! note "note"

    In order to eliminate the BSBAR blocks before the store instruction: BSBAR 0 format blocks and reduce the occupation of hardware BROB, this instruction prohibits store_count from being 0.

### CSEL/ADDC/SUBC instruction encoding adjustmentThe CSEL/ADDC/SUBC instructions are three-input instructions. In order to simplify the hardware read port design, in the previous version, at the instruction design level, the third source register was limited to the T register, the second source register was limited to the Local GPR, and the first source register was not limited. This achieves the purpose of having at most two T register inputs or at most two Local Reg register inputs at the same time.

In the current version, at the instruction encoding level, the restriction that the second source register is fixed to Local GPR is cancelled, that is, the second source register can be either a T register or a Local GPR.

Previous version encoding:

![bitmap-0.33](../figs/isa/version/bitmap-0.33.png)

Current version encoding:

![bitmap-0.34](../figs/isa/version/bitmap-0.34.png)

## Modification 4. Modification of assembly format

1. Modification of microinstruction assembly format

In the previous version, the model field was added to the encoding format of the prefetch instructions prf and prf.a to indicate which level of cache the instruction prefetched, but the assembly format was not modified. In order for assembly programmers to clearly indicate the cache level of instruction prefetching, the suffix ".l1/.l2/.l3" is added to the assembly names of the prf and prf.a instructions. The prfi.u and prfi.ua instructions are prefetched to the L1 Cache by default. To unify the format, the suffix ".l1" is added to the assembly names of these two instructions. The modified assembly format is as follows:

| Instructions | Original assembly format | Modified assembly format |
|------|------------------------------------------------|------------------------------------------------|
| prf | prf [SrcL, srcR<{.sw,.uw}><<<shamt>] | prf{.l1,.l2,.l3} [SrcL, SrcR<{.sw,.uw}><<<shamt>] |
| prf.a | prf [SrcL, SrcR<{.sw,.uw}><<<shamt>]<, {=>, ->}RegDst> | prf.a{.l1,.l2,.l3} [SrcL, SrcR<{.sw,.uw}><<<shamt>]<, {=>, ->}RegDst> |
| prfi.u | prfi.u [SrcL, simm] | prfi.u.l1 [SrcL, simm] |
| prfi.ua | prfi.ua [SrcL, simm]<, {=>, ->}RegDst> | prfi.ua.l1 [SrcL, simm]<, {=>, ->}RegDst> |

2.block instruction assembly format modification

As mentioned above, the RegDst0-RegDst2 fields are deleted in the encoding of template blockB.MCOPY and B.MSET instructions, so the expressions of RegDst0-RegDst2 are also deleted in the assembly format.

After B.MCOPY modification:
```
    b.mcopy [RegSrc0, RegSrc1, RegSrc2]
```
After B.MSET modification:
```
    b.mset [RegSrc0, RegSrc1, RegSrc2]
```

## Modification 5, CARGsystem register modification

1. The CARG register deletes the MSG/BGET/BSET field segment.
2. The setc.msg instruction needs to be replaced by the alias instruction [BSE] (../isa/inst/misa_s/BSE.md).
3. The current version uses the B.EXCEPTIONexception block to save the BGET/BSET status within the block.
4. Messages sent within the block are saved in the message buffer register.

Previous version register field segment:

![CARG-v0.33](../figs/isa/version/CARG-0.33.png)

Current version register field segment:

![CARG-v0.34](../figs/isa/version/CARG-0.34.png)