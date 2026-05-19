# CYCLE

The core-level timestamp register (Cycle Counter Register) is a register used to record and track time. The count update starts after the core is powered on.

![CYCLE](../../../figs/bitfield/svg/Sysregs/CYCLE.svg)

Supports hardware read access that triggers cycle counting within the core, and supports the core program instruction ssrget to read this register.

## Application

Core-level timestamp registers are typically synchronized to the computer's clock and have high-frequency oscillators to ensure accuracy.

Using core-level timestamp registers, time intervals between multiple events can be recorded and measured, which is useful for performance analysis, debugging, and optimization.

In addition, core-level timestamp registers can be used for time synchronization and timestamp calibration to ensure time consistency between different computers or devices.

In summary, the core-level timestamp register is a high-precision hardware device used to record and measure the time of event occurrence, providing valuable performance analysis and time synchronization functions.

## Remarks

This register is **read-only (RO)** and its SSRID is **0x0011**.