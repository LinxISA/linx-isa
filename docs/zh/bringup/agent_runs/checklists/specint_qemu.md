# SPECint / QEMU 清单

- [ ] ID：SPEC-001 为 灵犀 (`phase-c`) 构建 SPEC CPU2017 内部二进制文件，无需修补 SPEC 源。
  命令：`MODE=phase-c bash tools/spec2017/build_int_rate_linx.sh --build-runtimes`
  完成意味着：在每个工作台 `exe/` 目录下生成预期的 灵犀 可执行文件。
  状态： ❌ NIGHTLY/RUNTIME BLOCKER (2026-05-17) - `MODE=phase-c` 现在重现具体的托管通道拦截器：`out/libc/musl/logs/phase-c-summary.txt` 记录 `m3=blocked`，因为共享 musl 打包因 `ld.lld: error: relocation R_ZXTERMEN45QXZV5_64_BNEXT cannot be used against symbol 'malloc'; recompile with -fPIC` 失败，因此 `phase-c/lib/libc.so` 仍然不存在于动态工作台中。

- [ ] ID：SPEC-002 验证生成的可执行文件是否为 灵犀 机器类型。
  命令：`llvm-readelf -h benchspec/CPU/<bench>/exe/<binary>`
  完成意味着：块头 报告 `Machine: ZXTERMEN45QXZ`。
  状态：⚠️ 未测试 (2026-02-23)- [ ] ID：SPEC-003 Stage A 在 QEMU 矩阵（9p + initramfs）下运行的快速子集。
  长凳：`999.specrand_ir`、`505.mcf_r`、`531.deepsjeng_r`
  命令：`python3 tools/spec2017/run_stage_qemu_matrix.py --spec-dir workloads/spec2017/cpu2017v118_x64_gcc12_avx2 --stage a --input-set test --transports 9p,initramfs --strict --out-dir workloads/generated/spec2017/stage_a_xcheck/qemu_matrix`
  完成意味着：两种传输均通过 Stage-A 子集和聚合摘要报告 `ok=true`。
  状态：❌夜间/运行时拦截器 (2026-05-17) - 非规范本地重播现在可以精确分割拦截器：
  - `999.specrand_ir` 通过 `9p` 到达带有 `guest_shared_runtime=false` 的 QEMU 工作负载路径，然后在 initramfs 烟雾中看到的同一后期内核任务创建边界处停止（`workloads/spec2017/tmp/linx-qemu-results-smoke/999_specrand_ir/run_001/qemu.log` 中的 `...abcdefghijklZ`）。
  - `531.deepsjeng_r` 较早被阻止，因为它需要 `/lib/ld-musl-linx64.so.1` + `libc.so`，而当前的 `phase-c` sysroot 仍然缺少 `libc.so`。
  - 合并的 灵犀64 QEMU 恢复通道还需要无固件启动 (`-bios none`) 来直接内核运行；较旧的本地 `...biosnone...` 工件已经反映了该通道，当前的重运行应保留该策略。
  - 因此，在托管的共享 musl 打包和相同的后期 Linux 用户空间/rootfs 运行时路径上，完整的 Stage-A 关闭仍然被阻止。- [ ] ID：SPEC-004 A 阶段矩阵摘要工件已写入。
  文物：
    - `.../qemu_matrix/qemu_matrix_summary.json`
    - `.../qemu_matrix/qemu_matrix_summary.md`
    - `.../qemu_matrix/9p/stage_a_summary.json`
    - `.../qemu_matrix/initramfs/stage_a_summary.json`
  完成意味着：每个基准记录聚合和每个传输的 qemu/specdiff 判决。
  状态： ❌ NIGHTLY/RUNTIME BLOCKER (2026-05-17) - 使用 `SPEC-003` 保持打开状态；现在存在针对目标重新运行的本地诊断工件（例如 `workloads/spec2017/tmp/linx-qemu-results-smoke/stage_a_summary.json`），但它们尚未构成 `9p` 和 `initramfs` 的传递全矩阵聚合。

- [ ] ID：SPEC-005 B 阶段全速率在 QEMU 下运行（不包括 Fortran 策略排除）。
  完成意味着：所有必需的 B 阶段内部基准测试运行并发出验证输出。
  状态：⚠️ 未测试 (2026-02-23)

- [ ] ID：SPEC-006 B 阶段主机端规范验证通过所需的比较。
  完成意味着：每个必需的比较命令都返回通过。
  状态：⚠️ 未测试 (2026-02-23)

- [ ] ID：SPEC-007 从所需的 灵犀 内部闭合中明确排除 `548.exchange2_r`。
  完成意味着：排除记录在清单政策中并通过门禁审查强制执行。
  状态：⚠️ 未测试 (2026-02-23)