# CW

The random status register (CW-Canary Word Register) is mainly used for software to configure random numbers and check the status when pushing and popping the stack.

![CW](../../../figs/bitfield/svg/Sysregs/CW.svg)

Its principle can be briefly summarized as:

In the function stack frame, a canary value is stored between the function context and the local variable stack; when the function returns and pops off the stack, read and check whether the canary value has been overwritten to determine whether the program has a stack overflow.
The compiler stores canary words through global variables to implement **fstack-protector-strong**.

## Specific implementation

- The hardware provides a special register CW (Canary Word Register). When the device is started, the software generates a random number configuration register.
- Read the canary word from CW when opening/unstacking, and perform stack protection related protection.

## Specific requirements

- One register is allocated per hard thread.
-The register width is 64bit.
- Light core can be equipped internally.
- Supports high-frequency reading: the read register does not have a barrier, and a separate read instruction is provided without access through the system block.

## Remarks

This register is **readable and writable (RW)** system register customized by the light core, and its SSRID is **0x0820**.