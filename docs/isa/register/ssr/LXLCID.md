# LXLCID

The Linx logical core ID register (Linx Logical Core ID Register) stores the unique identification of the current logical core and is used for multi-core scheduling and inter-core communication.

![LXLCID](../../../figs/bitfield/svg/Sysregs/LXLCID.svg)

The compiler can use this register to optimize core-level task scheduling.

## Remarks

This register is **read-only (RO)** and its SSRID is **0x0021**.