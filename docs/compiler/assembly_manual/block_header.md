header contains the attributes of the current block instruction (block instruction type, jump type, input, output, microinstruction storage address and other information). The final header information is expressed through the accumulation of one or more pieces of header instruction information. Different header assembly instructions convey different block instruction information. Programmers use the corresponding header instruction according to code requirements. For the general form of header instruction, it must start with the **BSTART** command and cooperate with other header instruction to express a complete header. The currently supported header instruction and its meaning are shown in the table below. The template block instruction is defined in LinxISA, which does not explicitly include microinstructions. The specific microinstruction form is determined by the hardware implementation. For detailed template block instruction, see [template block instruction set](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/isa/blockIntro/temp_block/intro/):<br>

| header directive | Operand | Description |
|----------------------------------|--------------------------------------------------------|--------------------------------|
| BSTART.<Btype> <BrType>, <label> | block type, jump type and expression | block instruction start |
| BSTOP | NULL | block instructionEND |
| B.CATR | {TRAP, ATOMIC, <.AQ,.RL,.AQRL>, FAR} | Block attributes |
| B.TEXT | Expression | Indicates the starting position of the body instruction |
| B.NEXT | Expression | Indicates the position of the next header |


**Note**:

- From the perspective of reading experience, it is recommended that **header instruction is uppercase and body is lowercase**. The assembler allows headerbody instructions to be lowercase.

- **The assembly pseudo-instruction sequence that makes up header starts with BSTART. If the next BSTART is encountered, it indicates the start of the next block**. The assembler encodes header instruction line by line and does not check the correctness of the header assembly sequence.

- The assembly instructions of header and microinstructions will be introduced below. When reading the assembly instructions below: the syntax type is expression, which means that the operation object can be written in the form of an immediate number or a label. The {} symbol means using any string separated by ',' in {}, and <> means that the content within <> can be left blank by default.The assembly instruction format requirements of header are described in detail below. If the input assembly format requirements of the assembler are not met, the assembler will give an error prompt and terminate the assembly process.