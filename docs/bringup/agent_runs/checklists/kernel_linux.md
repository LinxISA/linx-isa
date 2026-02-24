# Kernel / Linux Checklist

- [x] ID: LINUX-001 Boot initramfs smoke on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/smoke.py`
  Done means: smoke boot reaches expected userspace marker without trap loop.
  Status: ✅ PASS (2026-02-23) - timer-on smoke is stable after kernel trap-return fix: `smoke.py` loop recheck is `8/8` pass (summary: `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/kernel_stability_summary.txt`, per-loop logs: `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/smoke_loop_1.log` ... `smoke_loop_8.log`). Diagnostic smokes also pass in the same run (`kernel_ctx_tq_irq_smoke.log`, `kernel_ctx_ri_step_trap_smoke.log`).

- [x] ID: LINUX-002 Boot full initramfs scenario on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/full_boot.py`
  Done means: full boot reaches expected completion marker.
  Status: ✅ PASS (2026-02-23) - timer-on full boot recheck is `6/6` pass after trap-return fix (summary: `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/kernel_stability_summary.txt`, per-loop logs: `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/full_loop_1.log` ... `full_loop_6.log`).

- [ ] ID: LINUX-003 Keep `linxisa_virt_defconfig` compatible with 9p/virtfs SPEC workflows.
  Done means: kernel config includes required 9p + virtio-mmio options and still boots.
  Status: ⚠️ NOT TESTED (2026-02-23)

- [ ] ID: LINUX-004 Boot BusyBox rootfs from virtio-blk and reach userspace `/sbin/init`.
  Command: `python3 kernel/linux/tools/linxisa/busybox_rootfs/boot.py`
  Done means: BusyBox rootfs boots from `/dev/vda`, shell commands run, and poweroff path works.
  Status: ❌ FAIL (2026-02-23) - BusyBox rootfs remains unstable in run `2026-02-23-r6-pin-linux-stability-fix`: userspace marker is missing and failure signature includes `_start -> start_kernel()` re-entry / corrupted hartid output before rootfs handoff completes. Same failure reproduces with timer IRQ disabled (`kernel_busybox_rootfs_timeroff.log`), so this is not only timer-on coupling (logs: `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/kernel_busybox_rootfs.log`, `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/kernel_busybox_rootfs_timeroff.log`, `docs/bringup/gates/logs/2026-02-23-r6-pin-linux-stability-fix/pin/reg_strict_cross_repo.log`).
