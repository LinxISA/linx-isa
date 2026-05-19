# Load retain and conditional store instructions

## Why introduce conditional storage and load retention instructions?

Conditional store and load retention are also a type of atomic instructions. Ordinary AMO atomic instructions require that the entire read, calculation, and write back must be atomic, that is, between read and write back, the memory address cannot be accessed by other processes, and the bus is usually locked, so that multi-core systems can be supported. However, because the bus will be locked, other cores will not be able to access the bus. When there are many cores and frequent lock grabbing, the bus will be locked for a long time. Therefore, a new mutually exclusive type of memory access instruction is introduced, namely the LR (load reserved)/SC (store conditional) instruction.

The LR/SC instructions are a pair of instructions used in pairs. They introduce conditions and retention mechanisms in load and store operations to lock the memory address between reading and writing back, thus avoiding the situation where the bus is locked for a long time. This ensures the atomicity of the operation while allowing other cores to access other memory addresses during the operation.

| Microinstructions | Assembly format | Description |
|----------|-------------------------------------------------------------|--------------------------------------------------|
| LR.B | lr.b<{.aq,.rl,.aqrl}> [SrcL], {->t, ->u, =>Rd\} | Load bytes and write them to the destination register with sign extension, and mark the memory |
| LR.H | lr.h<{.aq,.rl,.aqrl}> [SrcL], {->t, ->u, =>Rd\} | Load the halfword and write it to the destination register with sign extension, and mark the memory |
| LR.W | lr.w<{.aq,.rl,.aqrl}> [SrcL], {->t, ->u, =>Rd\} | Load the word and write it to the destination register with sign extension, and mark the memory |
| LR.D | lr.d<{.aq,.rl,.aqrl}> [SrcL], {->t, ->u, =>Rd\} | Load the double word and write it to the destination register with sign extension, and mark the memory |
| SC.B | sc.b<{.aq,.rl,.aqrl}> SrcL, [SrcR], {->t, ->u, =>Rd\} | Write the lowest byte of the left source register to the memory corresponding to the address in the right source register. Successfully write 0 to the destination register, otherwise write non-0 |
| SC.H | sc.h<{.aq,.rl,.aqrl}> SrcL, [SrcR], {->t, ->u, =>Rd\} | Write the lowest half-word of the left source register to the memory corresponding to the address in the right source register. Successfully write 0 to the destination register, otherwise write non-0 |
| SC.W | sc.w<{.aq,.rl,.aqrl}> SrcL, [SrcR], {->t, ->u, =>Rd\} | Write the lowest word of the left source register to the memory corresponding to the address in the right source register. Successfully write 0 to the destination register, otherwise write non-0 |
| SC.D | sc.d<{.aq,.rl,.aqrl}> SrcL, [SrcR], {->t, ->u, =>Rd\} | Write the double word of the left source register to the memory corresponding to the address in the right source register. Successfully write 0 to the destination register, otherwise write non-0 |

![StoreConditional](../../../figs/bitfield/svg/Introduction_32bit/StoreConditional.svg)

LR/SC type instructions support the release of consistent memory models, and each instruction is followed by an optional suffix of ".aq" and ".rl". "aq" is the abbreviation of "acquire", and "rl" is the abbreviation of "release".
The LR/SC instructions use these two suffixes to add additional memory order restrictions. The specific definition is as follows:| Acquire | Release | Meaning |
|---------------|---------------|----------------------------------------|
| 0 | 0 | No order restrictions |
| 0 | 1 | The results of all instructions accessing storage in the block instruction that precede this instruction must be observed before the instruction is executed |
| 1 | 0 | All instructions that access storage after the block instruction where this instruction is located must wait until the execution of this instruction is completed before starting to execute |
| 1 | 1 | The results of all instructions that access storage before the instruction is located in block instruction must be observed before the instruction is executed. All instructions that access storage after the instruction is located in block instruction must wait until the execution of the instruction is completed before starting execution |