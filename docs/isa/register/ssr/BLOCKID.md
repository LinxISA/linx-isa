# BLOCKID

The logical core ID register (Block ID) is used to uniquely identify different modules (Blocks) in the system during system debugging (System Debug) or tracing (Trace).

This SSR is configured by the system controller before the kernel starts, and it is not recommended to modify it while the kernel is running. If modifications are made while the kernel is running, consistency is not guaranteed.

## Bit width

The register width is 16bit.

## Reset value

This register is reset to 16'h0 after the machine is powered on.

## Remarks

This register is **read-only (RO)** system register, and its SSRID is **0x0051**.