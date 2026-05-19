# VERSION

The Linx logical core version register (Linx Core Version Register) indicates the hardware version number of the current core, which can help the software identify the processor function version and thus select an appropriate optimization strategy.

![VERSION](../../../figs/bitfield/svg/Sysregs/VERSION.svg)

**Major**: Describes the major version number. When the core design or architecture of the hardware changes significantly, the major version number will increase.

**Minor**: Describes the minor version number. When the hardware has functional improvements or additions, but does not affect the compatibility of existing functions, the minor version number will increase.

**Release**: Describes the revision number, which is incremented when bug fixes or other non-functional changes are made to the hardware.

## Remarks

This register is **read-only (RO)** and its SSRID is **0x0023**.