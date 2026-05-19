# SYSCNT

The local timestamp register (System Counter Register) is used to synchronize the timestamps of the large cores. The large cores update them externally, one for each core.

![SYSCNT](../../../figs/bitfield/svg/Sysregs/SYSCNT.svg)

## Remarks

This register is **read-only (RO)** system register customized by the light core, and its SSRID is **0x0810**.