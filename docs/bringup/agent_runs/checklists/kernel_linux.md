# Kernel / Linux Checklist

- [x] ID: LINUX-001 Boot initramfs smoke on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/smoke.py`
  Done means: smoke boot reaches expected userspace marker without trap loop.
  Status: ✅ PASS (2026-02-25) - smoke gate passes in run `2026-02-25-r2-pin-lanefix` (log: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/kernel_smoke.log`).

- [x] ID: LINUX-002 Boot full initramfs scenario on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/full_boot.py`
  Done means: full boot reaches expected completion marker.
  Status: ✅ PASS (2026-02-25) - full boot gate passes in run `2026-02-25-r2-pin-lanefix` (log: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/kernel_full_boot.log`).

- [x] ID: LINUX-003 Keep `linxisa_virt_defconfig` compatible with 9p/virtfs SPEC workflows.
  Command: `python3 tools/bringup/check_linx_virt_defconfig_spec.py --report-out docs/bringup/gates/linxisa_virt_defconfig_audit.json`
  Done means: kernel config includes required 9p + virtio-mmio options and still boots.
  Status: ✅ PASS (2026-02-25) - defconfig audit reports `linxisa_virt_defconfig_spec_compatible` with zero missing/mismatched options (artifact: `docs/bringup/gates/linxisa_virt_defconfig_audit.json`); initramfs and busybox boot gates remain green in run `2026-02-25-r2-pin-lanefix`.

- [x] ID: LINUX-004 Boot BusyBox rootfs from virtio-blk and reach userspace `/sbin/init`.
  Command: `python3 kernel/linux/tools/linxisa/busybox_rootfs/boot.py`
  Done means: BusyBox rootfs boots from `/dev/vda`, shell commands run, and poweroff path works.
  Status: ✅ PASS (2026-02-25) - BusyBox rootfs boot reaches userspace and expected command markers in run `2026-02-25-r2-pin-lanefix` (log: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/kernel_busybox_rootfs.log`).
