# Integer calculation instructions

Integer calculation instructions include arithmetic operation operations and logical operation operation instructions for integer data of `64位` and `32位`.

This part of the instructions uses two basic instruction formats, namely: B type instructions for register-register operation operations and F type instructions for register-immediate value operation operations.

## 1: 64-bit integer calculation instructions

This part of the instruction is responsible for arithmetic operations and logical operations between two 64-bit operands.

| Microinstructions | Assembly format | Description |
|---------------|--------------|-------------------------------------|
| ADD | add SrcL, SrcR< {.sw,.uw,.neg}><<< shamt>, ->{t,u,Rd} | 64-bit addition |
| SUB | sub SrcL, SrcR<{.sw,.uw,.neg}><<< shamt>, ->{t,u,Rd} | 64-bit subtraction |
| AND | and SrcL, SrcR<{.sw,.uw,.not}><<< shamt>, ->{t,u,Rd} | 64-bit logical AND |
| OR | or SrcL, SrcR<{.sw,.uw,.not}><<< shamt>, ->{t,u,Rd} | 64-bit logical OR |
| XOR |
| SRL | srl SrcL, SrcR, ->{t,u,Rd} | 64-bit logical right shift |
| SRA | sra SrcL, SrcR, ->{t,u,Rd} | 64-bit arithmetic right shift |
| SLL | sll SrcL, SrcR, ->{t,u,Rd} | 64-bit logical left shift |

The encoding format is as follows:

![ArithmeticOperation64bit](../../../figs/bitfield/svg/Introduction_32bit/ArithmeticOperation64bit.svg)

## 2: 64-bit operand-immediate calculation instructions

This part of the instruction undertakes arithmetic operations and logical operations between a 64-bit operand and an immediate value.

| Microinstructions | Assembly format | Description |
|---------------|---------------|----------------------------------------|
| ADDI | addi SrcL, uimm, ->{t,u,Rd} | 64-bit unsigned immediate addition |
| SUBI | subi SrcL, uimm, ->{t,u,Rd} | 64-bit unsigned immediate subtraction |
| ANDI | andi SrcL, simm, ->{t,u,Rd} | 64-bit signed immediate logical AND |
| ORI | ori SrcL, simm, ->{t,u,Rd} | 64-bit signed immediate logical OR |
| XORI | xori SrcL, simm, ->{t,u,Rd} | 64-bit signed immediate logical exclusive OR |
| SRLI | srli SrcL, shamt, ->{t,u,Rd} | 64-bit unsigned immediate logical right shift |
| SRAI | srai SrcL, shamt, ->{t,u,Rd} | 64-bit unsigned immediate arithmetic right shift |
| SLLI | slli SrcL, shamt, ->{t,u,Rd} | 64-bit unsigned immediate logical left shift |

The encoding format is as follows:

![ArithmeticwithimmediateOperation64bits](../../../figs/bitfield/svg/Introduction_32bit/ArithmeticwithimmediateOperation64bits.svg)

## Three: 32-bit integer calculation instructionsThis part of the instructions undertakes arithmetic operations and logical operations between two 32-bit source operands.

| Microinstructions | Assembly format | Description |
|---------------|-----------------------------------------------------|---------------|
| ADDW | addw SrcL, SrcR<{.sw,.uw,.neg}><<< shamt>, ->{t,u,Rd} | 32-bit addition |
| SUBW | subw SrcL, SrcR<{.sw,.uw,.neg}><<< shamt>, ->{t,u,Rd} | 32-bit subtraction |
| ANDW | andw SrcL, SrcR<{.sw,.uw,.not}><<< shamt>, ->{t,u,Rd} | 32-bit logical AND |
| ORW | orw SrcL, SrcR<{.sw,.uw,.not}>, ->{t,u,Rd} | 32-bit logical OR |
| XORW |
| SRLW | srlw SrcL, SrcR, ->{t,u,Rd} | 32-bit logical right shift |
| SRAW | sraw SrcL, SrcR, ->{t,u,Rd} | 32-bit arithmetic right shift |
| SLLW | sllw SrcL, SrcR, ->{t,u,Rd} | 32-bit logical left shift |

The encoding format is as follows:

![ArithmeticOperation32bit](../../../figs/bitfield/svg/Introduction_32bit/ArithmeticOperation32bit.svg)

## Four: 32-bit operand-immediate calculation instructions

This part of the instruction undertakes arithmetic operations and logical operations between a 32-bit source operand and an immediate value.

| Microinstructions | Assembly format | Description |
|---------------|---------------|----------------------------------------|
| ADDIW | addiw SrcL, uimm, ->{t,u,Rd} | 32-bit unsigned immediate addition |
| SUBIW | subiw SrcL, uimm, ->{t,u,Rd} | 32-bit unsigned immediate subtraction |
| ANDIW | andiw SrcL, simm, ->{t,u,Rd} | 32-bit signed immediate logical AND |
| ORIW | oriw SrcL, simm, ->{t,u,Rd} | 32-bit signed immediate logical OR |
| XORIW | xoriw SrcL, simm, ->{t,u,Rd} | 32-bit signed immediate logical exclusive OR |
| SRLIW | srliw SrcL, shamt, ->{t,u,Rd} | 32-bit unsigned immediate logical right shift |
| SRAIW | sraiw SrcL, shamt, ->{t,u,Rd} | 32-bit unsigned immediate arithmetic right shift |
| SLLIW | slliw SrcL, shamt, ->{t,u,Rd} | 32-bit unsigned immediate logical left shift |

The encoding format is as follows:

![ArithmeticwithimmediateOperation32bits](../../../figs/bitfield/svg/Introduction_32bit/ArithmeticwithimmediateOperation32bits.svg)