# Output to register directive: **BSET**

```
bset {第一层架构GPR寄存器}*
```

The BSET instruction is used to tell the assembler which UL_GPR will be modified in block instruction. The default value is 0. When block instruction is submitted, the block processor copies the R register in LL_GPR in the block to the corresponding register of UL_GPR according to the BSET mask.
The assembler will encode a 16-bit mask in sequence. Each bit in the mask represents a register. 1 means it will be modified, and 0 means it will not be modified. The default value of mask is 0x0, that is, the BGET descriptor is not written. When a BSET descriptor is recognized, the assembler will set the corresponding bit in the Mask of the register represented by its parameter list to 1, and only one BSET is allowed to exist at most.
The parameter list accepted by BSET is a register list, separated by ",", which must be one of the first-level architectural stateGPR registers. Please refer to the previous chapter for the first-level architectural stateGPR.