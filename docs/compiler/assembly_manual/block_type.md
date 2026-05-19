# Block type directive

```
b{.std, .stdc, .fp, .sys, .stdh, .stdch, .fph, .sysh, .sec}
```

Used to tell the assembler the type of block instruction. The current pseudo-instruction has no operation object. **The default value is B.STD. If there are multiple descriptors of block type, the last descriptor shall prevail**. This type of directive has no operands.

| block instruction Type | Description |
|---------------------|---------------------|
| B.STD | **Standard block instruction Standard Block**, including full scalar operations, encoded as 32bit fixed length. No intra-block jumps.	 |
| B.STDC | **Compressed block instruction Standard Compressed Block**, including some scalar operations. All microinstructions have a maximum of 2 inputs, and the encoding is 16bit fixed length. No intra-block jumps.	|
| B.STDH | **Standard Super block instruction Standard Hyper Block**, in addition to the standard block instruction, also contains jump instructions within the block, allowing control flow within the block.	 |
| B.STDCH | **Compressed Super block instruction Standard Compressed Hyper Block**, in addition to compressing block instruction, it also contains jump instructions within the block, allowing control flow within the block.	 |
| B.FP | **Floating-point block instruction Floating-point Block**, including the most basic floating-point operations, also includes scalar operations that support floating-point calculations. Supports half-precision, single-precision and double-precision floating point operations. No intra-block jumps. |
| B.FPH | **Floating point super block instruction FP Hyper Block**, floating point block instruction contains intra-block jump instructions.	 |
| B.SYS | **System block instruction System Block**, including access to system register and system control and atomic operation instructions. |
| B.SYSH | **System Super block instruction System Hyper Block**, system block instruction also contains intra-block jump instructions.	 |
| B.SEC | **Secure encryption and decryption block instruction Custom Block**, including all security-related encryption and decryption instructions. |