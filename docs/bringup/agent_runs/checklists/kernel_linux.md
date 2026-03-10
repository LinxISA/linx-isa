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
  Status: ✅ PASS (2026-03-08) - defconfig audit again reports `linxisa_virt_defconfig_spec_compatible` with zero missing/mismatched options (artifact: `docs/bringup/gates/linxisa_virt_defconfig_audit.json`).

- [x] ID: LINUX-004 Boot BusyBox rootfs from virtio-blk and reach userspace `/sbin/init`.
  Command: `python3 kernel/linux/tools/linxisa/busybox_rootfs/boot.py`
  Done means: BusyBox rootfs boots from `/dev/vda`, shell commands run, and poweroff path works.
  Status: ✅ PASS (2026-02-25) - BusyBox rootfs boot reaches userspace and expected command markers in run `2026-02-25-r2-pin-lanefix` (log: `docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/kernel_busybox_rootfs.log`).

- [x] ID: LINUX-005 Build pinned `vmlinux` with the propagated LLVM/QEMU workspace state.
  Command: `env PATH=$PWD/compiler/llvm/build-linxisa-clang/bin:$PATH /opt/homebrew/bin/gmake -C kernel/linux ARCH=linx LLVM=$PWD/compiler/llvm/build-linxisa-clang/bin/ 'CC=$PWD/compiler/llvm/build-linxisa-clang/bin/clang --target=linx64-unknown-linux-gnu -fintegrated-as' HOSTCC=/usr/bin/clang HOSTCXX=/usr/bin/clang++ O=$PWD/kernel/linux/build-linx-fixed vmlinux -j$(sysctl -n hw.ncpu 2>/dev/null || nproc)`
  Done means: the pinned kernel tree produces `kernel/linux/build-linx-fixed/vmlinux` without source or link failures.
  Status: ✅ PASS (2026-03-08) - pinned Linux `49785e788762` builds `kernel/linux/build-linx-fixed/vmlinux`; source-tree cleanliness was preserved by temporarily moving the stale in-tree generated include directories out of the way before the out-of-tree build.
