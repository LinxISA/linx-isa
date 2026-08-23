# Intra-block jump instructions

The jump instruction is used to jump between body instructions. The jump method supports **PC relative jump** and **register relative jump**.

## Command list

The list of jump instructions within the block is as follows:

| Microinstructions | Assembly format | Description |
|---------------|---------------|----------------------------------------|
| JR | jr SrcL, label | Unconditionally jump to the target address of tpc plus offset in the register |
| J | j label | Unconditionally jump to the target address of the current tpc plus offset |

PTO ISA 0.58.3 removes `B.EQ`, `B.NE`, `B.LT`, `B.GE`, `B.LTU`,
`B.GEU`, `B.Z`, and `B.NZ` and reserves their former encodings. Use
`SETC.*` with `BSTART COND` for block-control conditions.

![InnerBlockBranch32bits](../../../figs/bitfield/svg/Introduction_32bit/BranchInstruction.svg)

## Remarks

1. This type of instruction has no destination register and does not occupy the block-private register.
2. When this type of instruction is the last instruction of body, block instruction will submit it immediately after this instruction is submitted, and the jump within the block will not take effect.
