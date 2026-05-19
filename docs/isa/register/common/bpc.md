# BPC

## Description

The block instruction pointer register (**Block Program Counter**, referred to as **BPC**) has a bit width of 64 bits.

BPC is the address used to indicate the block instruction header (Block Header) currently being executed. When each block instruction is executed, the processor will read and update `BPC` to track the position of the current block instruction. After block instruction is submitted, `BPC` will be updated to the starting address of the next block instruction to ensure that the program is executed according to the correct control flow.

## Initial value

After the machine is powered on or restarted, this register is initialized to 64'h0.

## Access properties

This register is read-only (RO).