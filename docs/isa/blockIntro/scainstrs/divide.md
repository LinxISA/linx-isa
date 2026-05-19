# Division instructions

| Microinstructions | Assembly format | Description |
|--------------|----------------------------|-------------------------------------|
| DIV | div SrcL, SrcR, ->{t,u,Rd} | Signed division of two 64-bit values, the quotient is written to the destination register |
| DIVU | divide SrcL, SrcR, ->{t,u,Rd} | Unsigned division of two 64-bit values, the quotient is written to the destination register |
| DIVW | divw SrcL, SrcR, ->{t,u,Rd} | Signed division of two 32-bit values, the quotient is written to the destination register |
| DIVUW | dividew SrcL, SrcR, ->{t,u,Rd} | Unsigned division of two 32-bit values, the quotient is written to the destination register |
| REM | rem SrcL, SrcR, ->{t,u,Rd} | Signed remainder of two 64-bit values, the remainder is written to the destination register |
| REMU | remu SrcL, SrcR, ->{t,u,Rd} | Unsigned remainder of two 64-bit values, the remainder is written to the destination register |
| REMW | remw SrcL, SrcR, ->{t,u,Rd} | Signed remainder of two 32-bit values, the remainder is written to the destination register |
| REMUW | remuw SrcL, SrcR, ->{t,u,Rd} | Unsigned remainder of two 32-bit values, the remainder is written to the destination register |

The encoding is as follows:

![Multi-CycleALU](../../../figs/bitfield/svg/Introduction_32bit/divisionInstruction.svg)