# FPGA Platform Contract (ZYBO Z7-20)

Target board: Xilinx Zynq-7000 based Digilent ZYBO Z7-20.

## Fixed platform defaults

- UART MMIO base: `0x10000000`
- Pass/fail test finisher MMIO register: `0x10009000`

These defaults must remain compatible with existing QEMU-oriented software bring-up paths.

Machine-readable form:

- `docs/bringup/contracts/fpga_platform_contract.json`

## SoC integration baseline

- Core is implemented in PL.
- PL core accesses PS DDR through AXI interconnect/bridge.
- Linux images and staging buffers live in DDR.

## Boot-mode default

- First Linux milestone uses direct kernel boot path.
- U-Boot integration is optional and not required for first pass/fail gate.

## Determinism requirements

- Deterministic reset sequencing between PS and PL.
- Reproducible clocks/constraints for repeated boot tests.
- UART output is the primary acceptance channel for early milestones.
