# Address calculation class

Address calculation instructions are used to calculate the address of a specified location and PC-relative relative addressing.

| Microinstructions | Assembly format | Description |
| ------ | ----------------------- | -------------------------------------------------- |
| ADDTPC | addtpc simm, ->{t,u,Rd} | This instruction adds TPC to the signed immediate value shifted 12 bits to the left, and the result is written into the destination register |
| SETRET | setret uimm, ->ra | This instruction adds TPC to the unsigned immediate value shifted left by 1 bit, and the result is written to the global ra register |

The encoding format is as follows:

![PC-Arithmetic](../../../figs/bitfield/svg/Introduction_32bit/PC-Arithmetic.svg)