# libc / 运行时清单

- [x] ID：LIBC-001 为所需模式构建 musl sysroots（当需要时，阶段 b 和阶段 c）。
  命令：`MODE=phase-b lib/musl/tools/linx/build_linx64_musl.sh`
  完成意味着：所需的 musl 安装树存在于 `out/libc/musl/install/<mode>` 下，并且摘要报告 `M1/M2/M3` 通过。
  状态： ✅ 通过 (2026-03-08) - `MODE=phase-b` musl 构建以 `m1=pass`、`m2=pass` 和 `m3=pass` 完成（摘要：`out/libc/musl/logs/phase-b-summary.txt`）。

- [x] ID：LIBC-005 在固定工作区中构建 glibc 基线 G1a 工件。
  命令：`bash lib/glibc/tools/linx/build_linx64_glibc.sh`
  完成意味着：标准 灵犀 glibc 构建路径完成并在 `out/libc/glibc/build` 下生成预期的构建树。
  状态： ✅ 通过 (2026-03-08) - 固定的 glibc 基线构建在 G1b 验证之前成功完成，工件位于 `out/libc/glibc/build` 下。

- [x] ID：LIBC-002 构建 glibc G1b 共享 libc 门工件。
  命令：`bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh`
  完成意味着：`out/libc/glibc/logs/g1b-summary.txt` 报告通过或显式放弃块。
  状态： ✅ 通过 (2026-03-08) - `g1b-summary.txt` 报告 `status: pass` 和 `classification: shared_libc_so_built`，其中存在 `out/libc/glibc/build/linkobj/libc.so`。

- [x] ID：LIBC-003 为静态和共享模式传递 musl 运行时烟雾。
  命令：`python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both`
  完成意味着：静态/共享报告 `ok=true` 的摘要 json。
  状态： ✅ 通过 (2026-03-15) - musl 静态/共享运行时烟雾在最新的 pin-lane 报告 `2026-03-15-r2-pin` 中保持绿色。- [x] ID：LIBC-004 在启动门工件中保持运行时状态证据的更新。
  完成意味着：门报告行包含 musl/glibc 运行时检查的证据链接。
  状态：✅ 通过 (2026-03-15) - `docs/bringup/gates/latest.json` 包含最新 pin-lane 运行的刷新的 musl/glibc 运行时证据，包括回归的 `Library::glibc runtime dynamic hello` 行及其日志路径。

- [x] ID：LIBC-006 使用完整的 hello 矩阵关闭 Linux/QEMU 上的 glibc 动态运行时。
  命令：`python3 avs/qemu/run_glibc_smoke.py --qemu /tmp/linx-qemu-clean-build/qemu-system-linx64 --timeout 30`
  完成意味着：当前 hello 矩阵中每个跟踪的 glibc 运行时变体都在 Linux/QEMU 通道下到达 `main`，没有包装器端条目绕过，也没有加载器致命错误。
  状态： ✅ 通过 (2026-04-18) - 包装器不再重新打开 `/dev/console`，通过虚拟 UART 发出标记，完整的 `entry_main`/`shared`/`startup`/`startup_norpath` hello 矩阵现在可以通过干净固定的 QEMU 工件（`avs/qemu/out/glibc-smoke/summary.json`）。