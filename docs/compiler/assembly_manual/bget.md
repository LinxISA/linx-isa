# Input register directive: **BGET**

```
bget {第一层架构GPR寄存器}*
```

The BGET instruction is used to tell the assembler which UL_GPRs will be read in block instruction. The default value is 0. When block instruction is initialized, the block processor copies the corresponding register in UL_GPR to the R register of its own LL_GPR in the block according to the BGET mask.
The assembler will encode a 16-bit mask in sequence. Each bit in the mask represents a register, 1 means it will be read, and 0 means it will not be read. The default value of mask is 0x0, which means no BGET descriptor is written. When a BGET descriptor is recognized, the assembler will set the corresponding bit in the Mask of the register represented by its parameter list to 1, and only one BGET is allowed to exist at most.
The parameter list accepted by BGET is a register list, separated by ",", and must be one of the UL_GPR registers.