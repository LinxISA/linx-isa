# Execution unit

After the instruction is issued, it will enter the execution unit, which contains three (or more) pipeline levels: register read (RF), data forwarding (BY), and calculation (EX). The calculation can be one or more clock cycles depending on the instruction.

## Data

Within PE, the results of all instructions will be stored in the PE register file. The source operands of all instructions come from the BPC Buffer, block register file and PE register file. Its detailed structure is described in the following chapters:

* [Block Register File](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/bcc/brf/)

* [PE register file](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/backend/pe_rf/)

## Operation

In LinxISA, instructions are divided into three categories: memory access (LSU), calculation (ALU), external communication and PC operation (GSU). We have one or more specific computing units for each type. After the calculation is completed, the result will be sent to the register file in the WriteBack pipeline to be written to the destination register and participate in forwarding.

In this chapter we will divide the calculation into two parts, including:

* [Integer operation](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/backend/exu_int/)

* [Floating point operation](https://openx.huawei.com/mkdocs/project/1410/blockisa-doc/docs/site/docs/backend/exu_fp/)

## Structural block diagram

![AGE_MATRIX1](../figs/uArch/EXU_TOP.png){ width="800" }