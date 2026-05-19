# 集成/发布清单

- [x] ID：INT-001 在跨存储库运行时门之前验证规范的 AVS 合约。
  命令：`python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml`
  完成意味着：AVS 模式是规范的，所有活动条目都携带 `spec_refs` 和层元数据，并且不保留任何遗留合约代币。
  状态： ✅ 通过 (2026-03-08) - `check_avs_contract.py` 在合并子模块 repin 周期之前使用 `tests=54` 和 `active=54` 验证规范矩阵。

- [ ] ID：INT-016 要求在严格的运行时签核之前关闭 AVS 层。
  命令：`python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr`
  完成意味着：PR 关闭所需的每个主动 AVS 条目均已实施并通过机器可读的证据进行验证。
  状态： ✅ 通过 (2026-04-18) - 刷新的 PR 层矩阵/状态对现在报告 `required_tests=31` 和 `failure_count=0`（工件：`docs/bringup/gates/avs_tier_closure_pr.json`）。

- [x] ID：INT-002 验证所有必需的门行都已分配给已知的代理清单。
  完成意味着：多代理静态验证器报告没有未分配的所需门密钥。
  状态： ✅ 通过 (2026-03-20) - `check_multi_agent_gates.py --strict-always --mode static` 现在在刷新 3 月 15 日门集的清单/清单地图后返回 `ok: multi-agent static validation passed (agents=11, assignments=62)`。

- [ ] ID：INT-003 要求模型差分套件在严格的运行时闭包中传递。
  命令：`python3 tools/bringup/run_model_diff_suite.py ...`
  完成意味着：模型差异行是 `pass` 或通过分类帐明确放弃。
  状态： ✅ 通过 (2026-04-18) - 兼容性包装器再次接受旧门 CLI 和底层 `tools/model` 套件通过所有必需的装置（工件：`docs/bringup/gates/model_diff_summary.json`）。- [ ] ID: INT-004 要求 `strict_cross_repo.sh` 在严格封闭中通过。
  命令：`bash tools/regression/strict_cross_repo.sh`
  完成意味着：回归行是 `pass` 或通过分类帐明确放弃。
  状态：❌ 失败（本地 2026 年 5 月 19 日）- 最新的规范运行 `2026-04-18-r9-pin-linuxlibc-refresh` 仍将 `Regression::strict_cross_repo.sh` 记录为失败，因为所需的 BusyBox rootfs 门在同一运行中失败。当前的本地后续行动再次将区块链向前推进：rootfs 通道必须使用无固件 QEMU 启动 (`-bios none`)，旧的 `arch/linx/include/asm/bug.h` 指令故障在本地修复，立即的 SMP/VDSO 源冲突被清除，重建的内核现在超越了第一个 灵犀 MM/核心 API 漂移、早期的 `fs/nfs` 和`fs/lockd` SelectionDAG 崩溃，后续 `lib/random32.o` 崩溃。仍然没有更新的规范严格闭包证明，因为当前的第一站稍后位于 `lib/hexdump.o` (`hex_to_bin`) 的同一后端崩溃系列中。

- [ ] ID：INT-005 发出每次运行的多代理关闭摘要 JSON。
  神器：`docs/bringup/gates/logs/<run-id>/<lane>/multi_agent_summary.json`
  完成意味着：摘要存在，`ok=true`，并包括放弃决定。
  状态： ❌ 失败 (2026-05-17) - 存在最新的规范摘要，但它记录了 `ok=false`，因为 `Kernel::Linux busybox rootfs boot` 在没有豁免的情况下仍然失败（工件：`docs/bringup/gates/logs/2026-04-18-r9-pin-linuxlibc-refresh/pin/multi_agent_summary.json`）。后来的恢复探针没有发出替换的`multi_agent_summary.json`，因此仍然没有更新的绿色封闭包。 2026-05-17 本地烟雾迭代仅为 `rest_init()` 后任务创建通道提供非规范拦截器分类。- [x] ID：INT-006 保留从规范 JSON 报告生成的 `docs/bringup/GATE_STATUS.md`。
  命令：`python3 tools/bringup/gate_report.py render --report docs/bringup/gates/latest.json --out-md docs/bringup/GATE_STATUS.md`
  完成意味着：降价时间戳与报告时间戳匹配。
  状态： ✅ 通过 (2026-04-18) - 呈现的页面与 `2026-04-18-r9-pin-linuxlibc-refresh` 刷新后最新的规范报告时间戳 `2026-04-18 02:11:34Z` 匹配。

- [x] ID：INT-007 强制执行显式代理模块所有权和规范技能名称。
  命令：`python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode static`
  完成意味着：每个代理声明 `modules[]` + `skill`，并且 `skill` 在规范列表中。
  状态： ✅ 通过 (2026-03-20) - `check_multi_agent_gates.py --strict-always --mode static` 在刷新当前门集的清单/清单映射后通过。

- [x] ID：INT-008 仅允许经批准的跨模块代理拥有多模块所有权。
  命令：`python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode static`
  完成意味着：具有多个模块的代理在 `cross_module_agents` 中明确列出。
  状态： ✅ 通过 (2026-03-20) - 静态验证仅确认批准的跨模块代理是多模块的（`libc`、`integration`）。

- [ ] ID：INT-009 从规范地图同步已安装的技能并删除已弃用的别名。
  命令：`bash skills/linx-skills/scripts/install_canonical_skills.sh`
  完成意味着：本地 `$CODEX_HOME/skills` 仅保留规范的 `linx-*` 技能（加上受保护的实用技能）。

- [x] ID：INT-010 在每个启动周期之前拉取最新的技能子模块。
  命令：`bash tools/bringup/sync_canonical_skills.sh --pull-latest`
  完成意味着：`skills/linx-skills` 位于最新的 `origin/main` 上并安装到 Codex 技能中。
  状态： ✅ PASS (2026-03-08) - `sync_canonical_skills.sh --pull-latest` 高级 `skills/linx-skills` 合并提交 `5b4799f` 并刷新 `/Users/zhoubot/.codex/skills`。- [ ] ID：INT-011 总结培养工作后进化的技能。
  命令：`bash tools/bringup/finalize_skill_updates.sh --base origin/main`
  完成意味着：`docs/bringup/agent_runs/skills_evolution/` 中存在摘要 Markdown，其中包含触及技巧 + SHA + 原理。

- [x] ID：INT-012 在技能提交之前防止破坏性技能流失。
  命令：`python3 skills/linx-skills/scripts/check_skill_change_scope.py --repo-root skills/linx-skills --base origin/main`
  完成意味着：更改范围守卫通行证并且仅更改预期的技能目录。
  状态： ✅ 通过 (2026-03-08) - 在合并的技能 PR 被拉回超级项目工作区后，范围警卫报告 `changed=0, removed=0`。
- [ ] ID：INT-013 在运行时关闭中强制执行阶段限制放弃策略。
  命令：`python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode runtime ...`
  完成意味着：豁免仅在清单活跃阶段内有效，并在阶段转换后自动过期。

- [ ] ID：INT-014 需要双通道所需门奇偶校验 (`pin` + `external`) 以实现严格关闭。
  命令：`python3 tools/bringup/check_gate_consistency.py --profile release-strict --lane-policy external+pin-required ...`
  完成意味着：两条车道均通过所需的相同门钥匙组和新证据。

- [ ] ID：INT-015 强制实施 灵犀Core 夜间性能下限（<=10% 回归）。
  命令：`python3 tools/bringup/check_linxcore_perf_floor.py --root . --max-regression 10.0 ...`
  完成意味着：测量的吞吐量回归在配置的阈值内或运行被拒绝。- [ ] ID：INT-017 在 v0.56 传播后需要编译器、QEMU、Linux 和 libc 的固定构建闭包。
  命令：`cd avs/compiler/linx-llvm/tests && CLANG=compiler/llvm/build-linxisa-clang/bin/clang TARGET=linx64-linx-none-elf OUT_DIR=out-linx64 ./run.sh`； `ninja -C emulator/qemu/build qemu-system-linx64`; `bash lib/glibc/tools/linx/build_linx64_glibc.sh`; `bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh`; `MODE=phase-b lib/musl/tools/linx/build_linx64_musl.sh`; `env PATH=$PWD/compiler/llvm/build-linxisa-clang/bin:$PATH /opt/homebrew/bin/gmake -C kernel/linux ARCH=linx LLVM=$PWD/compiler/llvm/build-linxisa-clang/bin/ 'CC=$PWD/compiler/llvm/build-linxisa-clang/bin/clang --target=linx64-unknown-linux-gnu -fintegrated-as' HOSTCC=/usr/bin/clang HOSTCXX=/usr/bin/clang++ O=$PWD/kernel/linux/build-linx-fixed vmlinux -j$(sysctl -n hw.ncpu 2>/dev/null || nproc)`
  完成意味着：固定工作区编译传播的工具链/模拟器堆栈并生成 Linux + libc 工件，而不会出现构建失败，编译器 AVS 闭包在仍由活动编译器分支注册的裸机目标上进行评估。
  状态： ✅ 通过 (2026-04-18) - 最新的 pin-lane 运行记录编译器、QEMU、musl、glibc 和 clean-helper Linux `vmlinux` 构建关闭为通过。

- [x] ID：INT-018 在关闭检查之前规范化规范 AVS 矩阵状态文件。
  命令：`python3 tools/bringup/gen_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --source-status avs/linx_avs_v1_test_matrix_status.json --out avs/linx_avs_v1_test_matrix_status.json`
  完成意味着：签入的 AVS 状态文件在下游关闭/审核门使用它之前已就地标准化。
  状态： ✅ 通过 (2026-04-18) - 最新的 pin-lane 报告将 `ISA::AVS status normalize` 在运行 `2026-04-18-r9-pin-linuxlibc-refresh` 中记录为 `pass`。

- [x] ID：INT-019 审核 AVS 矩阵状态与规范矩阵的一致性。
  命令：`python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --report-out docs/bringup/gates/avs_matrix_status_audit.json`
  完成意味着：每个矩阵条目在状态文件中仅表示一次，并且机器报告已实施/通过的计数。
  状态： ✅ 通过 (2026-04-18) - 最新审计报告 `ok=true`，没有丢失/额外的状态条目（工件：`docs/bringup/gates/logs/2026-04-18-r9-pin-linuxlibc-refresh/pin/avs_matrix_status_audit.json`）。- [x] ID：INT-020 在固定工作负载通道中使 PTO 内核奇偶校验保持绿色。
  命令：`python3 workloads/pto_kernels/tools/run_pto_kernel_parity.py --out-dir workloads/generated`
  完成意味着：奇偶校验运行器报告 `ok=true` 并且生成的最新 markdown/json 工件与当前固定通道一致。
  状态： ✅ PASS (2026-04-18) - 最新的规范运行记录 `Regression::PTO kernel parity` 为 pass。

- [x] ID：INT-021 针对固定的 B 阶段 sysroot，保持基准工作负载回归绿色。
  命令：`LINX_CLANG=compiler/llvm/build-linxisa-clang/bin/clang LINX_SYSROOT=out/libc/musl/install/phase-b python3 workloads/run_benchmarks.py --cc tools/spec2017/linx_cc.sh --target linx64-unknown-linux-musl --sysroot out/libc/musl/install/phase-b --json-out workloads/generated/benchmarks_result.json`
  完成意味着：基准回归成功完成并写入规范的 JSON 工件。
  状态： ✅ PASS (2026-04-18) - 最新的pin-lane运行记录`Regression::Workload benchmarks`为`pass`。

- [x] ID：INT-022 针对固定的 B 阶段系统根，保持 PolyBench 工作负载回归绿色。
  命令：`LINX_CLANG=compiler/llvm/build-linxisa-clang/bin/clang LINX_SYSROOT=out/libc/musl/install/phase-b python3 workloads/run_polybench.py --cc tools/spec2017/linx_cc.sh --target linx64-unknown-linux-musl --sysroot out/libc/musl/install/phase-b --json-out workloads/generated/polybench_result.json`
  完成意味着：PolyBench 回归成功完成并写入规范的 JSON 工件。
  状态： ✅ PASS (2026-04-18) - 最新的pin-lane运行记录`Regression::Workload polybench`为`pass`。

- [x] ID：INT-023 针对固定的 b 阶段 sysroot，保持投资组合工作负载回归绿色。
  命令：`LINX_CLANG=compiler/llvm/build-linxisa-clang/bin/clang LINX_SYSROOT=out/libc/musl/install/phase-b python3 workloads/run_portfolio.py --cc tools/spec2017/linx_cc.sh --target linx64-unknown-linux-musl --sysroot out/libc/musl/install/phase-b --polybench --ctuning-limit 5 --json-out workloads/generated/portfolio_report.json`
  完成意味着：投资组合回归成功完成并写入规范的 JSON 工件。
  状态： ✅ PASS (2026-04-18) - 最新的pin-lane运行记录`Regression::Workload portfolio`为`pass`。

- [x] ID：INT-024 将固定工作负载通道中的策划调整子集保持为绿色。
  命令：`python3 workloads/ctuning/run_milepost_codelets.py --ctuning-root workloads/ctuning --target linx64-unknown-linux-musl --clang compiler/llvm/build-linxisa-clang/bin/clang --lld compiler/llvm/build-linxisa-clang/bin/ld.lld --qemu emulator/qemu/build/qemu-system-linx64 --limit 5 --run --summary-json workloads/generated/ctuning_result.json`
  完成意味着：策划的 ctuning 子集在 QEMU 下完成并写入规范的摘要 JSON。
  状态： ✅ PASS (2026-04-18) - 最新的pin-lane运行记录`Regression::ctuning curated subset`为`pass`。- [x] ID：INT-025 在所需的通行楼层保持 TSVC 严格编译覆盖率绿色。
  命令：`python3 workloads/tsvc/run_tsvc.py --clang compiler/llvm/build-linxisa-clang/bin/clang --lld compiler/llvm/build-linxisa-clang/bin/ld.lld --ZXTERMEN42QXZ-mode auto --strict-fail-under 148 --source-policy linx-v03-parity --no-run-qemu --out-dir workloads/generated`
  完成意味着：仅编译 TSVC 通道完成并满足严格的通行楼层，无需 QEMU 运行时。
  状态： ✅ PASS (2026-04-18) - 最新的 pin-lane 运行记录 `Regression::TSVC strict coverage gate` 在 `148/151` 为 `pass`。

- [ ] ID：INT-026 在运行时传递层保持 TSVC 严格 QEMU 回归绿色。
  命令：`python3 workloads/tsvc/run_tsvc.py --clang compiler/llvm/build-linxisa-clang/bin/clang --lld compiler/llvm/build-linxisa-clang/bin/ld.lld --qemu emulator/qemu/build/qemu-system-linx64 --ZXTERMEN42QXZ-mode auto --strict-fail-under 148 --source-policy linx-v03-parity --out-dir workloads/generated`
  Done 表示：TSVC 通道在 QEMU 下完成并满足配置的严格通行楼层。
  状态： ❌ 失败 (2026-05-15) - 不存在规范的运行时通行证。最新的诊断严格重新运行（`docs/bringup/gates/logs/2026-04-17-r7-pin-recovery/pin/reg_strict_cross_repo.log`）仅在跳过 BusyBox rootfs 时才达到 TSVC，然后在 `tsvc.auto.elf` 上 240 秒后超时； 4 月 18 日的规范报告仍然证明仅编译严格报道。