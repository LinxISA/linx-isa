# Kernel / Linux Checklist

- [x] ID: LINUX-001 Boot initramfs smoke on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/smoke.py`
  Done means: smoke boot reaches expected userspace marker without trap loop.
  Status: ✅ PASS (2026-04-18) - smoke gate remains green in run `2026-04-18-r9-pin-linuxlibc-refresh` (log: `docs/bringup/gates/logs/2026-04-18-r9-pin-linuxlibc-refresh/pin/kernel_smoke.log`).

- [x] ID: LINUX-002 Boot full initramfs scenario on Linx QEMU.
  Command: `python3 kernel/linux/tools/linxisa/initramfs/full_boot.py`
  Done means: full boot reaches expected completion marker.
  Status: ✅ PASS (2026-04-18) - full initramfs boot remains green in run `2026-04-18-r9-pin-linuxlibc-refresh` (log: `docs/bringup/gates/logs/2026-04-18-r9-pin-linuxlibc-refresh/pin/kernel_full_boot.log`).

- [x] ID: LINUX-003 Keep `linxisa_virt_defconfig` compatible with 9p/virtfs SPEC workflows.
  Command: `python3 tools/bringup/check_linx_virt_defconfig_spec.py --report-out docs/bringup/gates/linxisa_virt_defconfig_audit.json`
  Done means: kernel config includes required 9p + virtio-mmio options and still boots.
  Status: ✅ PASS (2026-03-08) - defconfig audit again reports `linxisa_virt_defconfig_spec_compatible` with zero missing/mismatched options (artifact: `docs/bringup/gates/linxisa_virt_defconfig_audit.json`).

- [ ] ID: LINUX-004 Boot BusyBox rootfs from virtio-blk and reach userspace `/sbin/init`.
  Command: `QEMU="$(bash tools/bringup/run_qemu_build_clean.sh --qemu-root $PWD/emulator/qemu --out-dir /tmp/linx-qemu-clean-build --target qemu-system-linx64)" python3 kernel/linux/tools/linxisa/busybox_rootfs/boot.py`
  Done means: BusyBox rootfs boots from `/dev/vda`, shell commands run, and poweroff path works.
  Status: ❌ FAIL (2026-04-18) - the Python 3.9 wrapper crash is fixed, and the pin lane can now build a clean pinned QEMU artifact via `run_qemu_build_clean.sh`, but BusyBox rootfs still reproduces a kernel `E_BLOCK` after `Run /sbin/init as init process` even against that clean QEMU. The current verbose failure lands in `__submit_bio` at `pc=0x1cb034` on `FRET.STK [ra ~ s4], sp!, 128` with `cause=0x101` and `ra=0`, which keeps the live regression narrowed to Linux runtime/call-return handling rather than the wrapper or a dirty emulator tree.

- [x] ID: LINUX-005 Build pinned `vmlinux` with the propagated LLVM/QEMU workspace state.
  Command: `bash tools/bringup/run_linux_vmlinux_build_clean.sh --linux-root $PWD/kernel/linux --out-dir $PWD/kernel/linux/build-linx-fixed --clang $PWD/compiler/llvm/build-linxisa-clang/bin/clang --gmake /opt/homebrew/bin/gmake --target vmlinux`
  Done means: the pinned kernel tree produces `kernel/linux/build-linx-fixed/vmlinux` without source or link failures.
  Status: ✅ PASS (2026-04-18) - the clean-build helper reproduces `vmlinux` successfully on the current workspace by temporarily stashing source-tree generated state before invoking `gmake`; this gate is no longer blocked by Kbuild source-tree hygiene.
