# Version 0.20 update

Update date: 2023-02-01

The following are the specific changes in the instructions in version 0.20:

## 1. Changes in microinstruction structure

Most microinstructions can access both the T register and the SR register. For example:

- **Mode A**: Both sources are registers: add a0 a1.
- **Mode B**: Two sources are SR registers, and one source is T register: add t#1 a0.
- **Mode C**: The two sources are T registers: add t#1 t#2.

!!! note "Note! The following instructions only support T register index"

    MUL/DIV/REM encoding is insufficient and only T register index is supported.  
    Floating point instructions only support T register indexing.

## 2.GET/SET semantic modification

- SET is renamed to SET.G, and global/local GPR is updated at the same time.
- SGET/SSET renamed to GET/SET.
- GET/SET and SET.C/SET.TGT share encoding space 4'b0110/4'b0111.

### 2.1 New MV (Move command)

**MV R1, R2** Move R2 to R1. This instruction is used for register migration in Calling Convention.
**MV.G R1, R2** Move R2 to R1 and broadcast R1. This instruction is used to migrate the value of PHI node in if-else.
The hardware executes this instruction simultaneously as a GET and SET instruction.
The MV instruction serves as the absolute register version of the set instruction **set a0/t#m a1**

### 2.2 Remove ADDSP/ADDSPI instructions

Due to the modified GET/SET semantics, the ADDSP instruction is less necessary.
In addition to affecting the code size, the following two instructions can be used instead of ADD SP t#1, SET.G t#1 SP.
The main reason for removing this instruction is that this instruction is a calculation instruction with side effects. We hope that only SET/MV has side effects, and other instructions cannot modify GPR, which is good for hardware implementation (simplifying intra-block Rename).

### 2.3 Added GETspecial register

- GET TID: Get thread ID
- GET CPUID: Get CPU ID
- GET HDS: Get the size of the current header

## 3. CONST instruction imm is increased from 11bit to 12bit

Original immediate range -1024-1023
Existing immediate range -2048-2047
Reason: 12-bit immediate data is at the same level as RISV's ADDI. In this case

`ADDI rd, rs0, imm(12bit)`

Equivalent to the following:

```c
const imm(12bit)
addi rs0, t#1
```
If there is a SET, then an additional SET is needed.
```c
const imm(12bit)
addi rs0, t#1
set rd, t#1
```

## 4. Added new HYPER Block type

The new version v0.20 indicates whether there is a jump within the block on header
Added new Block attribute b.hyper in parallel with the type of block

## 5. Added TRAP jump type

Tell the hardware that the current header is a TRAP jump type block, and the subsequent hardware is ready to make a system call.
This header is used when the program ends/system call is made.

## 6. LOAD/STORE instruction addressing mode optimization

### Load instruction addressing:

- **Mode A**: Link + Imm (signed 5bit) Assembly format: ld [t#1, 8]
```c
LB：ADDR = Link + Imm
LH：ADDR = Link + Imm<<1
LW：ADDR = Link + Imm<<2
LD：ADDR = Link + Imm<<3
LBU：ADDR = Link + Imm
LHU：ADDR = Link + Imm<<1
LWU：ADDR = Link + Imm<<2
```
Note: The range of immediate data is -16 to 16

- **Mode B**: Register + Imm (signed 4bit) Assembly format: ld [a0, 8]
```c
LB：ADDR = Register + Imm
LH：ADDR = Register + Imm<<1
LW：ADDR = Register + Imm<<2
LD：ADDR = Register + Imm<<3
LBU：ADDR = Register + Imm
LHU：ADDR = Register + Imm<<1
LWU：ADDR = Register + Imm<<2
```
Note: The range of immediate data is -8 to 8

- **Mode C**: SP + Imm (signed 8bit) Assembly format: ld [sp, 8]
```c
LB：ADDR = SP + Imm
LH：ADDR = SP + Imm<<1
LW：ADDR = SP + Imm<<2
LD：ADDR = SP + Imm<<3
LBU：ADDR = SP + Imm
LHU：ADDR = SP + Imm<<1
LWU：ADDR = SP + Imm<<2
```
Note: The range of immediate data is -128 to 128- **Mode D**: IP + Imm (unsigned 8bit) Assembly format: ld [ip, 8]
```c
LW：ADDR = TPC_END + Imm<<2
LD：ADDR = TPC_END + Imm<<3
LWU：ADDR = TPC_END + Imm<<2
```
Note: This instruction is used to access the long immediate number placed after body. Can also be used for PC-relative loads. The immediate range is 0 to 256.

Using the above addressing modes, most load scenarios can be efficiently covered, such as pointer addressing:
```
ld [a0]
ld [t#1, 8]
```
### Store instruction addressing

Due to the 16-bit encoding limitation, the Store needs to index additional data, so it cannot have complex addressing modes.

- **Mode E**: [Link0 + Imm (unsigned 3bit)] = link1 Assembly format: sd [t#1, 8], t#2

SB: [ADDR = Link0]=DATA=Link1 Note: store byte does not have immediate encoding, write ADDR back to T register
SH: [ADDR = Link0]=DATA=Link1 Note: store half word does not have immediate encoding, write ADDR back to T register
SW: [ADDR = Link0 + Imm<<2]=DATA=Link1, the immediate data only has 3 bit space, takes the value 0/4/8/12/16/20/24/28, and writes ADDR back to the T register
SD: [ADDR = Link0 + Imm<<3]=DATA=Link1, the immediate data only has 3 bit space, takes the value 0/8/16/24/32/40/48/56, and writes ADDR back to the T register
Example: If you want to encode array[i] = a0+a1
```c
add a0, a1
ag.uxtw array, i
sd [t#1], t#2
```

- **Mode F**: [Link + Imm (unsigned 2bit)] = register assembly format: sd [t#1, 8], a0

SB: [ADDR = Link0]=DATA=Reg Note: store byte does not have immediate encoding, write ADDR back to T register
SH: [ADDR = Link0]=DATA=Reg Note: store half word does not have immediate encoding, write ADDR back to T register
SW: [ADDR = Link0 + Imm<<2]=DATA=Reg, the immediate data only has 2 bit space, takes the value 0/4/8/12, and writes ADDR back to the T register
SD: [ADDR = Link0 + Imm<<3]=DATA=Reg, the immediate data only has 2 bit space, takes the value 0/8/16/24, and writes ADDR back to the T register
Example: If you implement a store quart instruction
```c
sd [a4], a0
sd [t#1, 4], a1
sd [t#1, 4], a2
sd [t#1, 4], a3
```

- **Mode G**: [Register + Imm (unsigned 2bit)] = link assembly format: sd [a0, 8], t#1

SB: [ADDR = Register]=DATA=Link Note: store byte does not have immediate encoding.
SH: [ADDR = Register]=DATA=Link Note: store half word does not have immediate encoding.
SW: [ADDR = Register + Imm<<2]=DATA=Link, the immediate data only has 3 bit space, takes the value 0/4/8/12/, and writes ADDR back to the T register
SD: [ADDR = Register + Imm<<3]=DATA=Link, the immediate data only has 3 bit space, takes the value 0/8/16/24/, and writes ADDR back to the T register
Example: Another implementation method of store quard instruction
```c
ld [s0]
sd [a0], t#1
sd [a0, 8], t#2
sd [a0, 16], t#3
sd [a0, 24], t#4
```
If the immediate number is too long, or is not within 0/4/8/12, then you have to use the following method:
```c
const imm
ag.td a0, t#1
sd [t#1], a1
```
- **Mode H**: [Register + Imm (unsigned 1bit)] = link assembly format: sd [a0, 8], a1SB: [ADDR = Register]=DATA=Register Note: store byte does not have immediate encoding, write ADDR back to T register
SH: [ADDR = Register]=DATA=Register Note: store half word does not have immediate encoding, write ADDR back to T register
SW: [ADDR = Register + Imm<<2]=DATA=Register, the immediate data only has 1 bit space, takes the value 0/4, and writes ADDR back to the T register
SD: [ADDR = Register + Imm<<3]=DATA=Register, the immediate data only has 1 bit space, takes the value 0/8, and writes ADDR back to the T register
Example: An implementation method of the store pair instruction
```c
sd [a0], a1
sd [a0,8], a2
```
The two register codes already occupy 8 bits, and the Opcode is 7 bits, so there is no coding space for immediate data.

Why can't it be made like this? :
```
const offset
sd [a0, t#1], a2
```
Because this instruction becomes a 3-operand instruction, it violates the principle of simplifying hardware.

How to solve the problem of insufficient register encoding? ->Use AG-address gen command
```
const offset
ag.td a0, t#1
sd [t#1], a2
```

## AG instruction addressing

In order to solve the problem of significant insufficient Store encoding space in pure 16-bit encoding space, we introduced the AG:address generation instruction.

AG was originally called LEA:load effective address. In order to avoid duplication with x86, it was changed to AG.  
The AG instruction is specially used for complex addressing modes and can be used together with the Load/Store instructions, but it is mainly used for stores.  
Due to insufficient coding space of the Store, additional instructions had to be introduced to generate the store address.  
AG is mainly used for the access mode array[i] = b.  
The AG command formula is as follows:

`R0 + convert(R1) << scale`

Convert refers to a transformation function, which has the following three types:

1. If the R1 type is unsigned int, then zero extend first, and shift left by 2/3
2. If the R1 type is signed int, then sign extend first and shift left by 2/3
3. If the R1 type is long int, then shift left by 1/2/3

As an opcode extension of AG, convert has the following modes:

- AG.TW: Equivalent to R0 + R1<<2 Assembly format: ag.tw a0, a1
- AG.TD: Equivalent to R0 + R1<<3 Assembly format: ag.td a0, a1
- AG.UXTW: Equivalent to R0 + ((unsigned int)R1)<<2 Assembly format: ag.uxtw a0, a1
- AG.SXTW: Equivalent to R0 + ((signed int)R1)<<2 Assembly format: ag.sxtw a0, a1
- AG.UXTD: Equivalent to R0 + ((unsigned int)R1)<<3 Assembly format: ag.uxtd a0, a1
- AG.SXTD: Equivalent to R0 + ((signed int)R1)<<3 Assembly format: ag.sxtd a0, a1

The AG instruction supports three index modes, single and mixed, for Link and Register.

### LD/ST directive

For assembly readability, we need to introduce the ld/st pseudo-instruction, which can be split into the AG+LD/ST microinstruction sequence at the back end.

load directive format:

`ld [(reg0/t#m), (reg1/t#n), imm, {TW/TD/UXTW/SXTW/UXTD/SXTD}]`
For example, when reading array[i].field, i is int, array is 64bit, and field offset is 24, it can be written as the following pseudo-instruction

`ld [a0, a1, 24, uxtd]`
It will expand into the following instructions:
```c
ag.uxtw a0, a1
ld [t#1, 24]
```
store directive format:

`sd [(reg0/t#m), (reg1/t#n), imm, {TW/TD/UXTW/SXTW/UXTD/SXTD}], (reg2/t#k)`
For example, to assign a value to array[i].field = x, it can be written as the following pseudo-instruction`sw [a0, a1, 24, sxtw], a3`
It will expand into the following instructions:
```c
ag.sxtw a0, a1
addi t#1, 24
sw [t#1], a3
```
Among them, ag.sxtw can be replaced by the following instructions:
```c
getw a1
slli t#1, 2
add a2, t#1
addi t#1, 24
sw [t#1], a3
```

# LinxISA0.21 update introduction

LinxISA v0.21 mainly solves the problems we encountered in v0.20 compilation and model joint debugging implementation. The main changes are:

1. Fine-tuning the coding field of some instructions with the goal of further reducing the Code Size.
2. Some immediate instructions can only index the results of previous instructions, increasing the coding space for immediate instructions.
3. Reconstructed the encoding of Store instructions. The encoding and decoding of v0.20 is too complicated.
4. Added SET Imm command.
5. Refer to RISCV and complete the Zba/Zbb/Zbc/Zbd extension.

The following are the specific changes to the directive:

## 1. Added Local Zero register

The Local GPR of BISA v0.21 defines a total of 17 registers, **Zero** and **R0-R15**. But there is no Zero register definition in Global GPR.

!!! note "note"
    The Local RA register has not been removed and can only be read by GET instructions and written by SET instructions.

The parsing of R0 in GET/SET in microinstructions is different:

GET Rx in the microinstruction can index R0-R15, where x==0 represents the index R0 (Local RA) register.  
In microinstructions, SET R0, R0 represents SET Zero, RA. The same goes for SET.G/SET.GL.  
SET Rx, Ry in the microinstruction. Rx can index Zero, R1-R15, Ry can index R0, R1-R15.  
R0 in the remaining microinstructions all represent Zero registers.

The above directly indexed registers become Zero registers.

## 2. Index preorder instruction results

We found that most instructions use T#1 much more frequently than other T#2-T#8. For ADDI t#l, imm instructions, there are no non-t#1 scenarios.

Therefore, we give up the encoding of the Link field segment to the immediate value. Under V0.21, the following instructions can only use t#1:

ADDI,SUBI,ANDI,ORI,XORI,SRLI,SRAI,SLLI - addi t#1, imm where t#1 is not encoded.

!!! info "LOAD/STORE command"
    Due to insufficient original coding space, the Store instruction needs to be reconstructed using this design.

## 3.REG+IMM immediate encoding reconstruction

Due to the introduction of the Zero register, the ADDI class immediate data Imm does not need to express Imm with a value of 0, so Imm 0 is given the encoding of a larger value number.

The original command ADDI R0, 0 can be used as GET. BISA V0.21 needs to be changed to ADD R0, zero.
The original code of the original instruction ADDI R0, 0 needs to be parsed into ADDI R0, 16.

!!! note "note"

    The immediate encoding +1 of SRL/SRA/SLL will be uniformly changed to the following mapping in 0.21:
    The mapping of immediate encoding becomes one-to-one correspondence, and for immediate 0, it is decoded into a larger overflow value.

This immediate mapping applies to:

ADDI,SUBI,ANDI,ORI,XORI,SRLI,SRAI,SLLI
ADDIW,SUBIW,ANDIW,ORIW,XORIW,SRLIW,SRAIW,SLLIW
CMP.EQI,CMP.NEI,CMP.LTI,CMP.LTUI,CMP.GEI,CMP.GEUI
SETC.EQI,SETC.NEI,SETC.LTI,SETC.LTUI,SETC.GEI,SETC.GEUI

Immediate values of Load/Store type instructions are not applicable.

## 4. Complete the AG command

The AG instruction version 0.21 completes all possibilities and can be unified into the following form, with a total of 2x2x3x4=48 expression forms.
The reason for the completion instruction: Shift 1 operations will be used more frequently (half-precision) in AI programs in the future.

`AG {LREG/TREG}, {LREG,TREG}, {DW, SW, UW} << {0,1,2,3}`

Improvements in assembly writing:

In order to avoid conflicts with ARM patents, the name UXTW will be attacked, so we redesigned the assembly writing method```c
    ag a0, a1, uw        /* 代表计算a0 + ((unsigned int)a1) */
    ag a0, a1, uw << 1   /* 代表计算a0 + ((unsigned int)a1)<<1 */
    ag a0, t#1, sw << 2  /* 代表计算a0 + ((signed int)t#1)<<2 */
    ag t#2, t#1 << 3     /* 代表计算t#2 + (t#1<<3) */
```

## 5. New growth instruction encoding

In order to solve the problem of insufficient 16bit instruction encoding, BISA v0.21 introduced long instruction encoding. The principle of long instruction encoding is similar to CONCATheader.

- Long instruction encoding fixedly occupies 1/16 of the encoding space.
- The long instruction occupies the position of a T register, and the encoding length is 32 bits.
- Long instructions only appear in **auxiliary block AUX**, **system block SYS**, **floating point block FP**, and do not appear in standard blocks.


The encoding of the following instructions is transferred to the long instruction space, and relative indexing/absolute indexing/mixed indexing is also supported.

- `mul a0, a1`, `mul a0, t#1`, `mul t#1, a1`, `mul t#1, t#2`, `mulh, mulhu, mulhsu, mulw `
- `div a0, a1`, `div a0, t#1`, `div t#1, a1`, `div t#1, t#2`, `divu, divuw`
- `rem a0, a1`, `remu a0, t#1`, `remuw t#1, a1`, `remw t#1, t#2`, `remu, remuw`
- `bxu a0, imml-u6, immr-u6`, `bxu t#1, imml-u6, immr-u6`
- `bxs a0, imml-u6, immr-u6`, `bxs t#1, imml-u6, immr-u6`

## 6. Added three-operand instruction

In order to reduce hardware complexity, the third operand of the three-operand instruction must be the T register.
BISA v0.21 adds two three-operand instructions in the auxiliary block:
- **SELECT**：select t#c, a0/t#1, a1/t#2
Among them, t#c indexes the condition

- **BFM**: bfm t#c, a0/t#1, a1/t#2 - The original BAM+BMG instructions are merged.  
Among them, t#c indexes the bitfield mask.

The value of a1 and Mask are covered to get value -- BMG
Overwrite value onto a0 and write to T register - BAM

## 7. Reconstructed floating point encoding

In the SPEC2006 FP example, floating point multiplication/floating point are hot instructions and need to be assigned two encoding formats: absolute/relative.

Allocating absolute/relative encoding space to all floating point instructions has exceeded the 16bit encoding space.

Therefore, in 0.21, we only give 16 bits of space for floating point multiplication, addition and floating point conversion.

FADD.H, FADD.S, FADD.D represent half-precision, single-precision and full-precision floating point addition respectively.

FMUL.H, FMUL.S, FMUL.D represent half-precision, single-precision and full-precision floating point multiplication respectively

The hardware will combine the following combinations of instructions into multiply-accumulate instructions:
```
FADD.D R0, R1
FMUL.D t#1, R3
```

The FGET instruction supports mutual conversion of five formats: **64bit Integer**, **32bit signed/unsigned**, **half precision**, **single precision**, and **double precision**.
A total of 24 mode conversions.- FGET.L.H: 64-bit long integer to 16-bit half float
- FGET.L.S: 64-bit long integer to 32-bit single float
- FGET.L.D: 64-bit long integer to 64-bit double
- FGET.W.H: 32-bit signed integer to 16-bit half float
- FGET.W.S: 32-bit signed integer to 32-bit single float
- FGET.W.D: 32-bit signed integer to 64-bit double
- FGET.WU.H: 32-bit unsigned integer to 16-bit half float
- FGET.WU.S: 32-bit unsigned integer to 32-bit single float
- FGET.WU.D: 32-bit unsigned integer to 64-bit double
- FGET.H.L: 16-bit half float to 64-bit long integer
- FGET.H.W: 16-bit half float to 32-bit signed integer
- FGET.H.WU: 16-bit half float to 32-bit unsigned integer
- FGET.H.S: 16-bit half float to 32-bit single float
- FGET.H.D: 16-bit half float to 64-bit double
- FGET.S.L: 32-bit single float to 64-bit long integer
- FGET.S.W: 32-bit single float to 32-bit signed integer
- FGET.S.WU: 32-bit single float to 32-bit unsigned integer
- FGET.S.H: 32-bit single float to 16-bit half float
- FGET.S.D: 32-bit single float to 64-bit double
- FGET.D.L: 64-bit double to 64-bit long integer
- FGET.D.W: 64-bit double to 32-bit signed integer
- FGET.D.WU: 64-bit double to 32-bit unsigned integer
- FGET.D.H: 64-bit double to 16-bit half float
- FGET.D.S: 64-bit double to 32-bit single float

## 7. All remaining system blocks and floating point block instruction are moved to the long immediate space