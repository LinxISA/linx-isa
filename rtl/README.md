# RTL (LinxCore)

This directory hosts the **LinxCore RTL implementation** for LinxISA.

## Overview

- **Submodule**: [LinxISA/LinxCore](https://github.com/LinxISA/LinxCore)
- **Purpose**: RTL implementation for FPGA/ASIC targets
- **ISA Contract**: Must match architected semantics in the canonical ISA catalog

## Key References

| Topic | Path |
|-------|------|
| ISA specification | `isa/v0.57/linxisa-v0.57.json` |
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

RTL behavior MUST match the architected semantics in the canonical ISA catalog
and manual, independent of microarchitectural implementation details.

## ISA Version Policy

This RTL targets the current active LinxISA profile. The canonical ISA
specification lives at `isa/v0.57/linxisa-v0.57.json`. When the ISA profile
is upgraded, update the reference above. See `docs/project/isa-upgrade-guide.md`
for the upgrade procedure.
