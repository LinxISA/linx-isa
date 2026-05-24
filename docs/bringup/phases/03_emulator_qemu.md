# Phase 3: Emulator (QEMU) Bring-up

QEMU implementation source of truth is the submodule:

- `emulator/qemu/`

Linx patch lineage is maintained in the LinxISA QEMU fork history, then pinned here via submodule SHA.

## Basic flow

1. Build the Linx freestanding suite into an aggregate `ET_REL` object, then
   link the firmwareless direct-boot `ET_EXEC` image used by the current
   recovery lane.
2. Run with `qemu-system-linx64 -machine virt -kernel <image>`.
   For the merged Linx64 recovery lane, direct kernel/rootfs runs are
   firmwareless by default and should include `-bios none` unless a specific
   firmware artifact is intentionally under test.
3. Validate output and exit status through AVS suites.

## Test entrypoints

```bash
# Default suites
./avs/qemu/run_tests.sh

# Full suites
./avs/qemu/run_tests.sh --all --timeout 20
```

## Conventions

- Firmwareless direct boot expects the freestanding QEMU suite image to carry
  a concrete entry point and an exported `__end_init_stack` symbol so the Linx
  `virt` machine can seed `sp` before `_start`.
- UART MMIO base: `0x10000000`
- Test finisher MMIO: `0x10009000`
- Finisher low 16 bits select pass/fail/reset (`0x5555` / `0x3333` / `0x7777`);
  the upper 16 bits carry an optional failure code
