# 内核/Linux 清单

- [x] ID：LINUX-001 灵犀 QEMU 上启动 initramfs 冒烟。
  命令：`python3 kernel/linux/tools/linxisa/initramfs/smoke.py`
  完成意味着：烟雾引导到达预期的用户空间标记，没有陷阱循环。
  状态：✅ 通过 (2026-04-18) - 运行 `2026-04-18-r9-pin-linuxlibc-refresh` 时烟门保持绿色（日志：`docs/bringup/gates/logs/2026-04-18-r9-pin-linuxlibc-refresh/pin/kernel_smoke.log`）。

- [x] ID：LINUX-002 在 灵犀 QEMU 上启动完整的 initramfs 场景。
  命令：`python3 kernel/linux/tools/linxisa/initramfs/full_boot.py`
  完成意味着：完全启动达到预期完成标记。
  状态： ✅ 通过 (2026-04-18) - 完整的 initramfs 启动在运行 `2026-04-18-r9-pin-linuxlibc-refresh` 中保持绿色（日志：`docs/bringup/gates/logs/2026-04-18-r9-pin-linuxlibc-refresh/pin/kernel_full_boot.log`）。

- [x] ID：LINUX-003 保持 `linxisa_virt_defconfig` 与 9p/virtfs SPEC 工作流程兼容。
  命令：`python3 tools/bringup/check_linx_virt_defconfig_spec.py --report-out docs/bringup/gates/linxisa_virt_defconfig_audit.json`
  完成意味着：内核配置包含所需的 9p + virtio-mmio 选项并且仍然可以启动。
  状态： ✅ 通过 (2026-03-08) - defconfig 审核再次报告 `linxisa_virt_defconfig_spec_compatible`，其中缺少/不匹配的选项为零（工件：`docs/bringup/gates/linxisa_virt_defconfig_audit.json`）。- [ ] ID：LINUX-004 从 virtio-blk 启动 BusyBox rootfs 并到达用户空间 `/sbin/init`。
  命令：`QEMU="$(bash tools/bringup/run_qemu_build_clean.sh --qemu-root $PWD/emulator/qemu --out-dir /tmp/linx-qemu-clean-build --target qemu-system-linx64)" QEMU_EXTRA_ARGS='-bios none' python3 kernel/linux/tools/linxisa/busybox_rootfs/boot.py`
  完成意味着：BusyBox rootfs 从 `/dev/vda` 启动，shell 命令运行，并且断电路径有效。
  状态：❌ 失败（2026 年 5 月 19 日本地）- 下一个操作不匹配现已明确：合并的 灵犀64 QEMU 恢复通道必须启动无固件 (`-bios none`) 才能直接运行内核/rootfs。 `boot.py` 在本地对齐，旧的 `arch/linx/include/asm/bug.h` 指令故障已修复，本地重建后续操作还清除了立即的 SMP/VDSO 源冲突、第一个 灵犀 MM/核心 API 漂移、早期的 `fs/nfs` 和 `fs/lockd` SelectionDAG 崩溃以及后续的 `lib/random32.o` 崩溃，但仍然没有新的 BusyBox rootfs 判决，因为新的干净构建路径现在稍后在 `vmlinux` 链接之前停止在 `lib/hexdump.o` 处。- [ ] ID：LINUX-005 使用传播的 LLVM/QEMU 工作区状态构建固定的 `vmlinux`。
  命令：`bash tools/bringup/run_linux_vmlinux_build_clean.sh --linux-root $PWD/kernel/linux --out-dir $PWD/kernel/linux/build-linx-fixed --clang $PWD/compiler/llvm/build-linxisa-clang/bin/clang --gmake /opt/homebrew/bin/gmake --target vmlinux`
  完成意味着：固定内核树生成 `kernel/linux/build-linx-fixed/vmlinux`，没有源或链接故障。
  状态： ❌ 失败（本地 2026 年 5 月 19 日） - 最后的规范证明仍然是 4 月 18 日的运行，但当前的本地重新验证已经远远超出了旧的 `bug.h` 内联汇编故障、第一个 灵犀 vDSO 干净构建故障以及初始 灵犀 MM/核心 API 漂移。重建的内核现在通过了刷新的 VDSO 路径、第一个页表/uaccess/syscall 兼容性修复、早期的 `fs/nfs` 和 `fs/lockd` SelectionDAG 崩溃以及后续的 `lib/random32.o` 崩溃，然后在 `lib/hexdump.o` (`hex_to_bin`) 的同一后端崩溃系列上停止`-O2`。