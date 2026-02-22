# Kernel

This directory hosts the **Linux kernel port** for LinxISA.

## Overview

- **Submodule**: [LinxISA/linux](https://github.com/LinxISA/linux)
- **Purpose**: Linux kernel with LinxISA architecture support

## Key References

| Topic | Path |
|-------|------|
| ISA specification | `isa/v0.3/linxisa-v0.3.json` |
| Linux bring-up scripts | `kernel/linux/tools/linxisa/initramfs/` |
| Linux bring-up phase | `docs/bringup/phases/06_linux_on_janus.md` |

## Validation

### Linux Boot Tests

```bash
# Smoke test
python3 kernel/linux/tools/linxisa/initramfs/smoke.py

# Full boot
python3 kernel/linux/tools/linxisa/initramfs/full_boot.py

# Virtio test
python3 kernel/linux/tools/linxisa/initramfs/virtio.py
```

### Configuration

The kernel uses `linxisa_virt_defconfig` for QEMU virtualization:

```bash
# Build kernel
cd kernel/linux
make linxisa_virt_defconfig
make
```

## Development Notes

- Linux bring-up requires `LINX_DISABLE_TIMER_IRQ=1` to avoid timer IRQ issues in QEMU
- 9p/virtfs support is required for SPEC workflow integration
