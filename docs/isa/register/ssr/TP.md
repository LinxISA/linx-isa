# TP

Thread Pointer Register (TP), referred to as TP, is used to store the data base address of the current thread. The compiler uses this register to perform local data access in multi-threaded programs.

![TP](../../../figs/bitfield/svg/Sysregs/TP.svg)

In a multi-threaded application, each thread may have its own set of private variables. These private variables will be stored in a specific memory space, and the address of this memory space is stored in TP.

## Remarks

This register is a 64-bit **readable and writable (RW)** system register, and its SSRID is **0x0000**