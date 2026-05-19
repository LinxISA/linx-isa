# GP

The Global Pointer Register is used to store the base address of global variables. The compiler uses this register to address and manage global data.

![GP](../../../figs/bitfield/svg/Sysregs/GP.svg)

You can use this register to place all global variables in a designated memory area to achieve frequent access to shared variables and data structures.

## Remarks

This register is **readable and writable (RW)** and its SSRID is **0x0001**.