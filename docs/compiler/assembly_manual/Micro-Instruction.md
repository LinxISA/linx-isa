# microinstructions
In the architectural definition of LinxISA, block instruction and body are composed of a series of microinstructions to complete specific computing tasks. The assembly instructions of microinstructions may be as shown below.

```
Opcode                                                      
Opcode Operand0 
Opcode Operand0,Operand1
Opcode Operand0,Operand1,Operand2
Opcode Operand0,->{UL_GPR, LL_GPR}
Opcode Operand0,Operand1,->{UL_GPR, LL_GPR}
Opcode Operand0,Operand1,Operand2,->{UL_GPR, LL_GPR}
```

1. Microinstructions may have input and output calculation results during specific calculations. When writing Operand operation objects, the order is first the left source operation object, the right source operation object, and then output. In the following text, Operand0 is the left source operation object, and Operand1 is the right source operation object. <br>
2. The input of the microinstruction may be a register, a label, or an immediate value. If the input is a register, it may be LL_GPR or UL_GPR. It supports using zero to represent a register operand whose value is always 0. For system register, for example, to access ebstatep (architectural state base address register), tp (thread private variable base address register), gp (static global variable base address register), etc., use system registerID for microinstruction access. The specific register operand names can be found in the chapter [Architecture and Registers] (./Architecture_Register.md), and the ID list of system register can be found in the chapter [system register] (../../isa/register/ssr/ssrintro.md). <br>
3. The microinstruction may have no output. If there is output, it can only be a register, which may be output to {UL_GPR, LL_GPR} <br>

   - Adding `->` indicates that the microinstruction has output, which can be output to UL_GPR or LL_GPR <br>
   - Output to the zero register, the instruction execution result has no effect. <br>
   - The default indicates no output. <br>

The following table lists the input and output formats of register operands:| Input register operand | Output register operand |
|--------------------|-----------------------|
| r0 or zero | r0 or zero |
| r1 or sp | r1 or sp |
| r2 or a0 | r2 or a0 |
| r3 or a1 | r3 or a1 |
| r4 or a2 | r4 or a2 |
| r5 or a3 | r5 or a3 |
| r6 or a4 | r6 or a4 |
| r7 or a5 | r7 or a5 |
| r8 or a6 | r8 or a6 |
| r9 or a7 | r9 or a7 |
| r10 or ra | r10 or ra |
| r11 or fp(s0) | r11 or fp(s0) |
| r12 or s1 | r12 or s1 |
| r13 or s2 | r13 or s2 |
| r14 or s3 | r14 or s3 |
| r15 or s4 | r15 or s4 |
| r16 or s5 | r16 or s5 |
| r17 or s6 | r17 or s6 |
| r18 or s7 | r18 or s7 |
| r19 or s8 | r19 or s8 |
| r20 or x0 | r20 or x0 |
| r21 or x1 | r21 or x1 |
| r22 or x2 | r22 or x2 |
| r23 or x3 | r23 or x3 |
| t#1~t#4 | t |
| u#1~u#4 | u |
| LB0~LB2 | LB0~LB2 |
| LC0~LC2 | LC0~LC2 |

**Note**:

For LB0~LB2, LC0~LC2 these system register

- Non-PAR blocks require ssrget/ssrset to access.
- In the PAR block, it can be directly accessed using the private microinstructions of the SIMT block.
- The current version of microinstructions does not support multiple outputs.

## Microinstruction output specifications:

   - The Opcode of the microinstruction determines whether the microinstruction has output
   - The output part of the microinstruction with output cannot be left out by default, otherwise the assembler will report an instruction format error.

## Opcode identification
For the identification of Opcode, first determine the block type where it is located, and then expand the Opcode to distinguish different instructions, floating point instructions of different precisions, and different operations of atomic instructions, etc.- Adding `w`:Opcode{w} after Opcode indicates low 32bit signed extension<br>
- Add `u`:Opcode{u} after Opcode to indicate unsigned operation<br>
- Adding `i`:Opcode{i} after Opcode indicates that the right source operation object is an immediate number<br>
- Add `{.eq, .ne, .lt, .ge, .ltu, .geu, .and, .or}` after Opcode: Opcode{.eq, .ne, .lt, .ge, .ltu, .geu, .and, .or} to indicate the conditions for the judgment to be established. `.eq` means that if they are equal, the judgment will be true. `.ne` means that if they are not equal, the judgment will be true. `.lt` means that if the signed left source is smaller than the signed right source, then the condition will be true. `ge` means that the condition is true if the signed left source is greater than the signed right source. Adding `u` to `.lt` and `.ge` indicates unsigned comparison, `.and` and `.or` respectively indicate logical AND and logical OR, and `i` indicates that the right source operation object is an immediate comparison<br>
- Adding `c.`:c.Opcode in front of Opcode indicates that the instruction is a compressed instruction, and the encoding length is 16 bits
- Floating point precision: Opcode{.fd, .fs, .fh, fb}, `.fd` represents 64bit double precision floating point type, `.fs` represents 32bit single precision floating point type, `.fh` represents the 16-bit half-precision floating point type, and `.fb` represents the 8-bit low-precision floating-point type, which is limited to floating-point instructions<br>
- Atomic operations: Opcode{.aq, .rl, .aqrl}, `.aq` represents Acquire, `.rl` represents Release, `.aqrl` represents AcquireRelease, only atomic instructions<br>

## Operand operation
Supports operations such as Operand's shifting, address calculation, address fetching, arithmetic operations, logical operations, etc.

- When the type of Operand is a register, the following operations are supported:<br>
    - Arithmetic operation `Operand{.sw, .uw, .neg}` can only be performed on registers. `sw` means intercepting the lower 32 bits of the operand and doing signed extension. `uw` means intercepting the lower 32 bits of the operand and doing unsigned extension. `neg` means inverting the operand and adding 1. <br>
    - The logical operation `Operand{.sw, .uw, .not}` can only be performed on the register. `.not` means inverting the operand. <br>
    - Shift operation: `Operand1<<shamt`, shift Operand1 to the left by shamt bits. <br>- When the Operand is an immediate value and a label, it can support constant value and immediate value acquisition operations. It is limited to integer calculation instructions, memory access instructions, and constant instructions: <br>
    - Use absolute values: `%hi(表达式)` means to get the high 20 bits of the expression calculation result, `%lo(表达式)` means to get the low 12 bits of the expression calculation result. <br>
    - Use relative TPC values: `%tpcrel_hi(symbol)` means to get the symbol address relative to the high 20 bits of the current TPC, `%got_tpcrel_hi(symbol)` means to get the symbol address in the GOT table relative to the high 20 bits of the current TPC, `%tpcrel_lo(label)` needs to get the high symbol address relative to the low 12 bits of the label address. <br>
    - Use the value relative to the Thread Pointer: `%tprel_hi` means to obtain the high 20 bits of the TLS variable relative to the Thead Pointer register, and `%tprel_lo` means to obtain the low 12 bits of the TLS variable relative to the Thead Pointer register. <br>
    - Use the value relative to the Global Pointer: `%gprel_hi` means to obtain the high 20 bits of the global variable relative to the Global Pointer register, and `gprel_lo` means to obtain the low 12 bits of the global variable relative to the Global Pointer register.

- Address calculation operation: `[Operand0]` or `[Operand0,Operand1]`, address calculation can only be performed on registers or immediate numbers Operand. Operand0 is a register and Operand1 can be a register or immediate number. For details, see memory access instructions <br>

Multiple operations can be performed on the same Operand, such as `[Operand1, Operand2.sw<<shamt]` <br>

## Operand extension design of register type
The register type Operand is designed to add a bit width indication. The purpose is to give hardware prompts to improve the utilization of register resources in the SIMT block. How to use it:

- Output operand identification: Operand{.b, .h, .w, .d}, `.b, .h, .w, .d` indicates that the register operand width is 8bit, 16bit, 32bit, 64bit respectively. This extension design can be used in conjunction with other basic operations of Operand, such as shifting, which are determined according to specific instructions.
- Input operand identifier: Operand{.fd, .fs, .fh, .fb, .bf, .flb, .d, .uw, .uh, .ub, .sw, .sh, .sb}, where `.fd, .fs, .fh, .fb, .bf, .flb` is used to indicate the floating point type of the register operand type and the corresponding bit width, and `.d, .uw, .uh, .ub, .sw, .sh, .sb` is used to indicate that the register operand is an integer type and the corresponding bit width.


## Use of body microinstructions
body microinstructions are divided into two categories: public microinstructions and private microinstructions. Normally, the body microinstructions of block instruction are composed of public microinstructions and some private microinstructions.

- Public microinstructions: Indicates that all types of block instruction can be used. For specific microinstructions, please refer to the chapter [Basic Instruction Set] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/instset/baseInstrs/)
- Private microinstructions: Indicates that only the corresponding type of block instruction can be used. For specific microinstructions, please refer to [scalarblock instruction Set] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/std_block/intro/), [System ZXTERM ZH32QXZ set] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/sys_block/intro/), [Floating point block instruction set] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/fp_block/intro/), [Parallel block instruction set] (https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/simt_block/intro/).
- The body microinstructions of the parallel block are all composed of private microinstructions.