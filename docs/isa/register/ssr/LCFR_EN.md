# LCFR_EN

Linx core feature enable register (Linx Core Feature Enable Register)<br>
This register enables or disables processor-specific features such as parallel blocks, floating point operations, etc., and the compiler generates compatible code based on the setting of this register. It is read and write (RW), but for each specific bit, only a specific ACR can write to it. Modifying the corresponding bits of an ACR that does not have write permission will have no effect.

![LCFR_EN](../../../figs/bitfield/svg/Sysregs/LCFR_EN.svg)

The definitions of all fields are the same as those defined in the [LCFR](../../../isa/register/ssr/LCFR.md) register

## Remarks

The SSRID of this register is **0x0025**.