# vector instruction

## Assembly syntax

The assembly format of the vector instruction is as follows:

```asm
    opcode SrcR1<.T1>, SrcR2<.T2>, ->DstR<.W>
```

Among them, SrcR1 and SrcR2 represent input registers, and DstR represents output register. T1/2 represents the description of data type in the register, and W specifies the bit width of the output register.

Different from the traditional scalar register, the vector register has 4 optional widths. Each instruction needs to express the width of its output register through assembly identifiers B, H, W, D, where:

- **B**: The full name is Byte, indicating an 8-bit register.
- **H**: Full name Half Word, indicating 16-bit register.
- **W**: The full name is Word, indicating a 32-bit register.
- **D**: The full name is Double Word, which means 64-bit register.

For example, the instruction `op t#1.sw, u#2.sw, ->n.w`, where `.sw` and `.w` indicate that the source register t#1, u#2 and the destination register n are all 32-bit wide registers.

Special attention needs to be paid to:

- The **input register and output register bit widths of an instruction are allowed to be different**. If the destination register is wider, it is expanded, if it is narrower, it is truncated.
- Different instructions, when the subsequent instruction indexes the output of the preceding instruction, **The bit width of the source register specified by the subsequent instruction must be consistent with the bit width of the output register of the preceding instruction**. Otherwise, the hardware reports exception.

## Decoding type

vector instructions are encoded by concatenating prefixes and main instructions, and the instruction length is uniformly **64bit**. The lower 32 bits are the prefix instructions and the higher 32 bits are the main instructions.

vector instruction decoding types are as follows:

![instType64](../../../figs/bitfield/svg/Introduction_64bit/instType64.svg)

## Codec description of each domain segment

The vector instruction domain segment mainly includes `输入寄存器域`, `输出寄存器域`, `操作数参数域` and `立即数域`. The following is a detailed description of each domain.

### Input register field

The input register field is the field segment with `Src` in the descriptor, including: `SrcL`, `SrcR`, `SrcD`, `SrcP`, etc.

Without special instructions, the mapping relationship between this field index code and the corresponding register is as follows:| RegSrc | Register name | Register alias | Explanation |
|-------|------|--------|--------|
| 0-3 | VTR1-VTR4 | VT#1-VT#4 | The first to fourth instruction results before the VT result queue |
| 4-7 | Reserve | Reserve | Reserve |
| 8-11 | VUR1-VUR4 | VU#1-VU#4 | The results of the first to fourth instructions before the VU result queue |
| 12-15 | Reserve | Reserve | Reserve |
| 16-19 | VMR1-VMR4 | VM#1-VM#4 | The first to fourth instruction results before the VM result queue |
| 20-23 | Reserve | Reserve | Reserve |
| 24-27 | VNR1-VNR4 | VN#1-VN#4 | The first to fourth instruction results before the VN result queue |
| 28-31 | Reserve | Reserve | Reserve |
| 32-41 | RI0-RI11 | RI0-RI11 | Global register input parameters |
| 42-55 | Reserve | Reserve | Reserve |
| 56-59 | TR1-TR4 | T#1-T#4 | The results of the first to fourth instructions before the T result queue |
| 60-63 | UR1-UR4 | U#1-U#4 | The results of the first to fourth instructions before the U result queue |
| 64 | Lane Counter 0 | LC0 | lane count register 0, innermost iteration variable |
| 65 | Lane Bound 0 | LB0 | lane upper limit register 0, innermost iteration length |
| 66-67 | Reserve | Reserve | Reserve |
| 68 | Lane Counter 1 | LC1 | lane counter register 1, second layer iteration variable |
| 69 | Lane Bound 1 | LB1 | lane upper limit register 1, second layer iteration length |
| 70-71 | Reserve | Reserve | Reserve |
| 72 | Lane Counter 2 | LC2 | lane count register 2, third-level iteration variable |
| 73 | Lane Bound 2 | LB2 | lane upper limit register 2, third layer iteration length |
| 74-79 | Reserve | Reserve | Reserve |
| 80 | TA | TA | The first input Tile register parameter |
| 81 | TB | TB | Second input Tile register formal parameter |
| 82 | TC | TC | The third input Tile register formal parameter || 83 | TD | TD | The fourth input Tile register formal parameter |
| 84 | TE | TE | The fifth input Tile register parameter |
| 85 | TF | TF | The sixth input Tile register parameter |
| 86 | TG | TG | The seventh input Tile register formal parameter |
| 87 | TH | TH | The eighth input Tile register parameter |
| 88 | TO | TO | The first output Tile register parameter |
| 89 | TO1/TS | TO1/TS | Second output Tile register formal parameter |
| 90 | TO2 | TO2 | The third output Tile register formal parameter |
| 91 | TO3 | TO3 | The fourth output Tile register parameter |
| 92 | P | P | Mask register |
| 93-94 | Reserve | Reserve | Reserve |
| 95 | Zero | Zero | Zero register |
| 96 | VTR1.REUSE | VT#1.REUSE | The first instruction result before the VT result queue |
| 97 | VTR2.REUSE | VT#2.REUSE | The second instruction result before the VT result queue |
| 98 | VTR3.REUSE | VT#3.REUSE | The third instruction result before the VT result queue |
| 99 | VTR4.REUSE | VT#4.REUSE | The fourth instruction result before the VT result queue |
| 100-103 | Reserve | Reserve | Reserve |
| 104 | VUR1.REUSE | VU#1.REUSE | The first instruction result before the VU result queue |
| 105 | VUR2.REUSE | VU#2.REUSE | The second instruction result before the VU result queue |
| 106 | VUR3.REUSE | VU#3.REUSE | The third instruction result before the VU result queue |
| 107 | VUR4.REUSE | VU#4.REUSE | The fourth instruction result before the VU result queue |
| 108-111 | Reserve | Reserve | Reserve |
| 112 | VMR1.REUSE | VM#1.REUSE | The first instruction result before the VM result queue |
| 113 | VMR2.REUSE | VM#2.REUSE | The second instruction result before the VM result queue |
| 114 | VMR3.REUSE | VM#3.REUSE | The third instruction result before the VM result queue || 115 | VMR4.REUSE | VM#4.REUSE | The fourth instruction result before the VM result queue |
| 116-119 | Reserve | Reserve | Reserve |
| 120 | VNR1.REUSE | VN#1.REUSE | The first instruction result before the VN result queue |
| 121 | VNR2.REUSE | VN#2.REUSE | The result of the second instruction before the VN result queue |
| 122 | VNR3.REUSE | VN#3.REUSE | The third instruction result before the VN result queue |
| 123 | VNR4.REUSE | VN#4.REUSE | The fourth instruction result before the VN result queue |
| 124-127 | Reserve | Reserve | Reserve |

### <span id="locationA">operand parameter field</span>

The microinstructions in the 64bit decoding format need to specify the width of the data type output register of the input data. The parameter fields used are as follows:

- **s/t width**: This field segment is located in the high three bits of Src/RegDst and is used to represent data type in the source/destination register, that is, how to parse the data in the input/output register. This field is valid for all parallel block input/output registers. The details are as follows:

| s/t width | Assembly mark | Explanation |
|-----------|-----------|--------------------------------|
| **Floating point instructions (input) t width** | | |
| 000 | fd | The operand is 64-bit double-precision floating point data |
| 001 | fs | The operand is 32-bit single-precision floating point data |
| 010 | fh | The operand is 16-bit half-precision floating point data |
| 011 | fb | The operand is 8bitlow-precision floating-point type data |
| 100 | reserve | reserved code |
| 101 | reserve | reserved code |
| 110 | reserve | reserved code |
| 111 | reserve | reserved code |
| **Integer command (input) s width** | | |
| 000 | ud | The operand is 64-bit unsigned integer data |
| 001 | uw | The operand is 32-bit unsigned integer data |
| 010 | uh | The operand is 16-bit unsigned integer data |
| 011 | ub | The operand is 8-bit unsigned integer data |
| 100 | sd | The operand is 64-bit signed integer data |
| 101 | sw | The operand is 32-bit signed integer data |
| 110 | sh | The operand is 16-bit signed integer data |
| 111 | sb | The operand is 8-bit signed integer data |

### <span id="locationB">Output register field</span>

The output register field is a field segment marked with descriptor `RegDst`. The index encoding is as follows:| RegDst | Register name | Register alias | Explanation |
|----------|----------|------------|-------|
| 0 | VT | VT | Push to VT queue |
| 1 | VU | VU | Push to VU queue |
| 2 | VM | VM | Push to VM queue |
| 3 | VN | VN | Push to VN queue |
| 4~31 | reserve | reserve | reserve |
| 32~35 | RO0~RO3 | Global register output parameters |
| 36~61 | reserve | reserve | reserve |
| 62 | U | U | Push to U queue |
| 63 | T | T | Push to T queue |
| 64~91 | reserve | reserve | reserve |
| 92 | P | P | Mask register |
| others | Reserve | Reserve | Reserve |

Output register bit width encoding:

| width | Assembly mark | Explanation |
|-----------|-----------|-----------|
| 00 | d | The operand is 64-bit integer data |
| 10 | w | The operand is 32-bit integer data |
| 10 | h | The operand is 16-bit integer data |
| 11 | b | The operand is 8-bit integer data |

## Notes

- The **input register and output register bit widths of the same vector instruction are allowed to be different**. If the destination register is wider, it is expanded, if it is narrower, it is truncated.
- Different instructions, when the subsequent instruction indexes the output of the preceding instruction, **The bit width of the source register specified by the subsequent instruction must be consistent with the bit width of the output register of the preceding instruction**. Otherwise, the hardware reports exception.