# Kernel / Linux Checklist

- [x] ID: LINUX-001 Boot initramfs smoke on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/smoke.py`
  Done means: smoke boot reaches expected userspace marker without trap loop.
  Status: ✅ PASS (2026-02-23) - timer-on smoke passes in run `2026-02-23-r3-pin-qemu-llvm-linux-fix` (log: `docs/bringup/gates/logs/2026-02-23-r3-pin-qemu-llvm-linux-fix/pin/kernel_smoke.log`). Diagnostics now split: `ctx_ri_step_trap_smoke.py` passes, `ctx_tq_irq_smoke.py` still fails with `irq0_delta=0` (logs: `kernel_ctx_ri_step_trap_smoke.log`, `kernel_ctx_tq_irq_smoke.log`).

- [x] ID: LINUX-002 Boot full initramfs scenario on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/full_boot.py`
  Done means: full boot reaches expected completion marker.
  Status: ✅ PASS (2026-02-23) - timer-on full boot passes in run `2026-02-23-r3-pin-qemu-llvm-linux-fix` (log: `docs/bringup/gates/logs/2026-02-23-r3-pin-qemu-llvm-linux-fix/pin/kernel_full_boot.log`).

- [ ] ID: LINUX-003 Keep `linxisa_virt_defconfig` compatible with 9p/virtfs SPEC workflows.
  Done means: kernel config includes required 9p + virtio-mmio options and still boots.
  Status: ⚠️ NOT TESTED (2026-02-23)

- [ ] ID: LINUX-004 Boot BusyBox rootfs from virtio-blk and reach userspace `/sbin/init`.
  Command: `python3 kernel/linux/tools/linxisa/busybox_rootfs/boot.py`
  Done means: BusyBox rootfs boots from `/dev/vda`, shell commands run, and poweroff path works.
  Status: ⚠️ BLOCKED (2026-02-23) - Python typing compatibility is fixed, but host dependency still blocks closure: `busybox_rootfs/build_rootfs.sh` fails with `mkfs.ext4/mke2fs not found` (log: `docs/bringup/gates/logs/2026-02-23-r3-pin-qemu-llvm-linux-fix/pin/kernel_busybox_rootfs.log`).
