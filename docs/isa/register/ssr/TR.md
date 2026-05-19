# TR

The thread private register (Thread Register) contains two SSRs, TR1 and TR2, which are system register customized for light-core user mode, and each thread has an independent one.

**TR1**

![TR1](../../../figs/bitfield/svg/Sysregs/TR1.svg)

**TR2**

![TR2](../../../figs/bitfield/svg/Sysregs/TR2.svg)

## Remarks

This register is **readable and writable (RW)** system register customized by the light core, where the SSRID of the TR1 register is **0x0800** and the SSRID of the TR2 register is **0x0801**.