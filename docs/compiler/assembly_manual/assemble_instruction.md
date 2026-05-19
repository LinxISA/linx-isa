The LinxISA assembly instruction format is specified as follows:

```
Opcode operand0,operand1,... {->destination}
```

- Opcode is the name of the instruction, which is an identifier unique to different instructions.
- Operand is the operation object of the instruction, which can be a register, immediate value, or label
- Opcode and Operand are separated by spaces. Multiple Operands can be separated by ',', such as Opcode operand0, operand1
- Two Opcode instruction identifiers cannot appear in the same instruction.
- ...means there may be 0 or more Operands
- {->destination} means that when there is output, -> needs to be used to indicate the output to the corresponding global or block register. The block register supports dual output, and supports up to 2 block registers.

## Operation object
Operand operation objects have three forms: register, immediate value, and label.

- The naming of registers has been explained in the previous register chapter.
- The writing method of immediate data is the same as other architectures: supports signed/unsigned immediate data, supports decimal (1234)/hexadecimal (0x4d2)/binary (0b100 1101 0010)
- The usage of tags has been explained in the previous tags chapter.

The assembly instructions of header and microinstructions will be introduced below. When reading the assembly instructions below: the {} symbol indicates the use of any string separated by ',' in {}, and <> indicates that the content within <> may not be written by default.

### Expression
In the assembler, immediate and label type operands are treated as an expression. The assembler will convert immediate values ​​and labels into the required numeric values. Therefore, when an assembly instruction or assembly pseudo-instruction requires an integer, we can usually write it as an immediate number and label any of the two operation objects:<br>
1. Directly use an immediate value specified in decimal, hexadecimal (with 0x prefix), or binary (with 0b prefix). (0) <br>
2. Use mathematical and logical expressions consisting of labels and other predefined values. These expressions produce absolute or relative values. The absolute value is position independent and constant. Relative values are specified relative to some linker-defined address that is determined when the binary executable is generated,
For example, the target address of the branch. (1) <br>

(0)
```
BSTART.STD COND, 0x200000     /* 当前ZXTERMZH39QXZ的跳转目标地址为0x200000 */
```

(1)
```
BSTART.STD COND, .LBBO       /* 当前ZXTERMZH39QXZ的跳转目标地址为标签LBBO所指示的地址，在生成二进制执行文件时确定*/ 
```