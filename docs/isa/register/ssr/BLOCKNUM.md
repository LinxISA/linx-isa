# BLOCKNUM

Total number of logical cores register (Block Number)

This SSR is configured by the system controller before the kernel starts and is not expected to be modified while the kernel is running. If modifications are made while the kernel is running, consistency cannot be guaranteed.

## Bit width

The register width is 16bit.

## Reset value

This register is reset to 16'h0 after the machine is powered on.

## Remarks

This register is **read-only (RO)** system register, and its SSRID is **0x0050**.