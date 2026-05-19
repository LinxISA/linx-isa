# Basic extended instruction set

The basic extended instruction set is a supplement to the [Basic Instruction Set] (./baseInstrs.md) and is used to provide extended functions beyond general operations, such as division and remainder operations.

The instruction length of the basic extended instruction set is unified to 32 bits and can be used in different types of block instructionbody.

The command list is as follows:

| Classification | Instructions |
|-----|------|
| **Division operation** | [DIV](../inst/misa_g/DIV.md), [DIVU](../inst/misa_g/DIVU.md), [DIVW](../inst/misa_g/DIVW.md), [DIVUW](../inst/misa_g/DIVUW.md) |
| **Remainder operation** | [REM](../inst/misa_g/REM.md), [REMU](../inst/misa_g/REMU.md), [REMW](../inst/misa_g/REMW.md), [REMUW](../inst/misa_g/REMUW.md) |
| **Conditional Selection** | [CSEL](../inst/misa_g/CSEL.md) |