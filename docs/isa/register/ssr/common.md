## General system register

The universal system register is accessible to all ACRs. These SSRs are divided into 4 categories:

- Running registers: These registers can be considered as infrequently used GPR, using the space in the 0x0000-0x000f range.
- Clock registers: These registers are used to record the global timestamp of the processor, using the space in the 0x0010-0x001f range.
- Static configuration registers: These registers are mainly used to read global information. Use space in the range 0x0020-0x002f.
- Loop control registers, these registers are used for execution control of parallel blocks or LOOPblock instruction, using the space in the 0x0050-0x005f range.

## Run register

| SSR ID | Abbreviation | Name | Name |
|----------|----------|---------------|------------------|
| 0x0000 | [TP](./TP.md) | Thread Pointer Register | Thread base address register |
| 0x0001 | [GP](./GP.md) | Global Pointer Register | Global Base Address Register |

## Clock register

| SSR ID | Abbreviation | Name | Name |
|----------|----------|---------------|------------------|
| 0x0010 | [TIME](./TIME.md) | Timer Counter Register | Timer Counter Register |
| 0x0011 | [CYCLE](./CYCLE.md) | Cycle Counter Register | Core-level timestamp |

## Static configuration register

| SSR ID | Abbreviation | Name | Name |
|----------|----------|---------------|------------------|
| 0x0020 | [CSTATE](./CSTATE.md) | Common State Register | Common State Register |
| 0x0021 | [LXLCID](./LXLCID.md) | Linx Logical Core ID Register | Linx logical core ID register |
| 0x0022 | [VENDOR](./VENDOR.md) | Vendor ID Register | Vendor ID Register |
| 0x0023 | [VERSION](./VERSION.md) | Linx Core Version Register | Linx logic core version register |
| 0x0024 | [LCFR](./LCFR.md) | Linx Core Features Register | Linx Core Features Register |
| 0x0025 | [LCFR_EN](./LCFR_EN.md) | Linx Core Feature Enable Register | Linx core feature enable register |

## Dynamic configuration register| SSR ID | Abbreviation | Name | Name |
|----------|----------|---------------|------------------|
| 0x0050 | [BLOCKNUM](./BLOCKNUM.md) | Block Number Register | Total number of logical cores register |
| 0x0051 | [BLOCKID](./BLOCKID.md) | Block ID Register | Logic core ID register |