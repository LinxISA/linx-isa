# RTL (LinxCore)

This directory hosts the **LinxCore RTL implementation** for LinxISA v0.3.

## Overview

- **Submodule**: [LinxISA/LinxCore](https://github.com/LinxISA/LinxCore)
- **Purpose**: RTL implementation for FPGA/ASIC targets
- **ISA Contract**: Must match architected semantics in v0.3 catalog

## Key References

| Topic | Path |
|-------|------|
| ISA specification | `isa/v0.3/linxisa-v0.3.json` |
| ISA manual | `docs/architecture/isa-manual/` |
| RTL bring-up phase | `docs/bringup/phases/04_rtl.md` |
| Trace contract | `docs/bringup/contracts/trace_schema.md` |
| Co-sim tests | `rtl/LinxCore/tests/` |

## Validation

Run RTL co-simulation:

```bash
bash rtl/LinxCore/tests/test_cosim_smoke.sh
```

## Alignment Rule

RTL behavior MUST match the architected semantics in the v0.3 catalog and manual, independent of microarchitectural implementation details.
