# Kernel / Linux Checklist

- [x] ID: LINUX-001 Boot initramfs smoke on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/smoke.py`
  Done means: smoke boot reaches expected userspace marker without trap loop.
  Status: ✅ PASS (2026-04-18) - smoke gate remains green in run `2026-04-18-r9-pin-linuxlibc-refresh` (log: `docs/bringup/gates/logs/2026-04-18-r9-pin-linuxlibc-refresh/pin/kernel_smoke.log`).

- [x] ID: LINUX-002 Boot full initramfs scenario on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/full_boot.py`
  Done means: full boot reaches expected completion marker.
  Status: ✅ PASS (2026-07-03 local) - `TIMEOUT=120 SKIP_BUILD=1 QEMU=/tmp/linx-qemu-current-build-20260703-r1/qemu-system-linx64 python3 kernel/linux/tools/linxisa/initramfs/full_boot.py` passes on QEMU `v10.2.0-1004-ga3061b963f3`. The run reaches the initramfs shell, lists `/proc` and `/sys`, probes `/proc/cpuinfo`, `/proc/meminfo`, and `/proc/interrupts`, passes `getdents64_probe` on `/proc` and `/sys`, and completes `sigill`/`sigsegv` tests before `poweroff`.

- [x] ID: LINUX-003 Keep `linxisa_virt_defconfig` compatible with 9p/virtfs SPEC workflows.
  Command: `python3 tools/bringup/check_linx_virt_defconfig_spec.py --report-out docs/bringup/gates/linxisa_virt_defconfig_audit.json`
  Done means: kernel config includes required 9p + virtio-mmio options and still boots.
  Status: ✅ PASS (2026-03-08) - defconfig audit again reports `linxisa_virt_defconfig_spec_compatible` with zero missing/mismatched options (artifact: `docs/bringup/gates/linxisa_virt_defconfig_audit.json`).

- [x] ID: LINUX-004 Boot BusyBox rootfs from virtio-blk and reach userspace `/sbin/init`.
  Command: `ROOTFS_IMG="$(bash tools/bringup/run_linux_busybox_rootfs_build_clean.sh --linux-root $PWD/kernel/linux --worktree $PWD/workloads/generated/busybox-rootfs-clean-rebuild-20260630/src --obj-dir $PWD/workloads/generated/busybox-rootfs-clean-rebuild-20260630/build --out-dir $PWD/workloads/generated/busybox-rootfs-clean-rebuild-20260630/out --llvm-build $PWD/compiler/llvm/build-linxisa-clang)" SKIP_BUILD=1 QEMU=$PWD/emulator/qemu/build-linx/qemu-system-linx64 QEMU_EXTRA_ARGS='-bios none' TIMEOUT=90 python3 kernel/linux/tools/linxisa/busybox_rootfs/boot.py`
  Done means: BusyBox rootfs boots from `/dev/vda`, shell commands run, and poweroff path works.
  Status: ✅ PASS (2026-07-03 local) - `workloads/generated/linux-busybox-latest-qemu-20260703-r1/report.json` records `ok=true` on `/tmp/linx-qemu-current-build-20260703-r1/qemu-system-linx64` (`v10.2.0-1004-ga3061b963f3`) with `kernel/linux/build-linx-fixed/vmlinux` and the current virtio-blk rootfs. The first attempt timed out with no output, but the runner's same-config retry reached the shell, listed `/` and `/sbin`, read `/proc/interrupts` twice, observed `linx-timer` IRQ progress `40 -> 45`, and powered off through `LINX_REBOOT lisc_shutdown`. The earlier `addr=0x10000004` PID1 trap in `workloads/generated/busybox-rootfs-boot-20260630-r1/` came from a stale rootfs image whose BusyBox binary still contained direct UART MMIO loads/stores; the clean rebuilt rootfs binary no longer contains that sequence.

- [ ] ID: LINUX-005 Build pinned `vmlinux` with the propagated LLVM/QEMU workspace state.
  Command: `bash tools/bringup/run_linux_vmlinux_build_clean.sh --linux-root $PWD/kernel/linux --out-dir $PWD/kernel/linux/build-linx-fixed --clang $PWD/compiler/llvm/build-linxisa-clang/bin/clang --gmake /opt/homebrew/bin/gmake --target vmlinux`
  Done means: the pinned kernel tree produces `kernel/linux/build-linx-fixed/vmlinux` without source or link failures.
  Status: ❌ FAIL (2026-05-19 local) - the last canonical proof is still the April 18 run, but current local revalidation has moved well beyond the old `bug.h` inline-asm failure, the first Linx vDSO clean-build failures, and the initial Linx MM/core API drift. The rebuilt kernel now gets through the refreshed VDSO path, the first page-table/uaccess/syscall compatibility fixes, the earlier `fs/nfs` and `fs/lockd` SelectionDAG crashes, and the follow-on `lib/random32.o` crash before stopping on the same backend crash family at `lib/hexdump.o` (`hex_to_bin`) under `-O2`.
