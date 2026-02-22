# Kernel / Linux Checklist

- [x] ID: LINUX-001 Boot initramfs smoke on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/smoke.py`
  Done means: smoke boot reaches expected userspace marker without trap loop.
  Status: ✅ PASS (2026-02-22) - Smoke boot completes successfully

- [x] ID: LINUX-002 Boot full initramfs scenario on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/full_boot.py`
  Done means: full boot reaches expected completion marker.
  Status: ✅ PASS (2026-02-22) - Full boot completes with all probes passing

- [ ] ID: LINUX-003 Keep `linxisa_virt_defconfig` compatible with 9p/virtfs SPEC workflows.
  Done means: kernel config includes required 9p + virtio-mmio options and still boots.
  Status: ⚠️ NOT TESTED
