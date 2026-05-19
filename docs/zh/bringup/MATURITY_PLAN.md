# 灵犀指令集 成熟度计划（Tier-1 轨道与 ARM/x86）

最后更新: 2026-05-17

## 基线

- 最新规范运行：`2026-04-18-r9-pin-linuxlibc-refresh`
- 最新规范报告生成：`2026-04-18 02:11:34Z`
- 规范报告：`docs/bringup/gates/latest.json`
- 最新的诊断严格重新运行：`2026-04-17-r7-pin-recovery`（非规范；BusyBox rootfs 跳过以暴露 `docs/bringup/gates/logs/2026-04-17-r7-pin-recovery/pin/reg_strict_cross_repo.log` 中的下游阻止程序）
- 签入的规范报告现在包括 4 月 18 日的针道恢复证据。它清除了 AVS PR 层关闭、模型差异、灵犀Core/Testbench/Trace/pyCircuit 叶 PR 门、glibc 运行时、musl 运行时、PTO 奇偶校验和 TSVC 仅编译 PR 覆盖范围的过时的 3 月错误拦截器。
- 主动治理阶段仍为`G0`； `docs/bringup/agent_runs/waivers.yaml` 不包含任何豁免。
- 最新的非规范 Linux 烟雾诊断：2026 年 5 月 17 日，本地启动迭代远远超过了 DT、percpu、日志缓冲区、proc/ns/pidfs 伪文件系统设置以及 `rest_init()` 之前的后期初始化通道。实时边界现在是 `rest_init()` 之后的第一次任务创建切换，特别是 灵犀 tiny-RCU 配置上的 `user_mode_thread()` / `kernel_clone()` / `copy_process()`。

## 差距快照- AVS PR 层关闭现已完成（`31/31` 要求的测试通过），而夜间宽度仍为 `32/54`。
- 当前的恢复工作现已缩小到 Linux/用户空间运行时关闭：
  - 即使使用干净的固定 QEMU 构建和干净的 rootfs 构建帮助程序，在 `/sbin/init` 后 Linux BusyBox rootfs 仍然失败，
  - `strict_cross_repo.sh` 保持红色仅是因为所需的 BusyBox rootfs 行在最新的规范运行中为红色，
  - 规范运行时证据通过 `2026-04-18-r9-pin-linuxlibc-refresh` 刷新，
  - 跳过 BusyBox 的最新诊断重新运行到达 TSVC，然后在 `tsvc.auto.elf` 上 240 秒后超时，因此 TSVC QEMU 运行时是 BusyBox 之后的下一个阻塞器，而不是已清除的通道。
- 单独的非规范内核烟雾启动工作不再在 DT 解析或伪文件系统引导程序中被阻止：
  - 只读 DT 导入、内存发现、percpu 设置和后期伪 fs 烟雾旁路现已完成，
  - 当前本地烟雾跟踪到达 `...abcdefghijklZ`，然后在用户空间启动之前停止，
  - 重建映像反汇编显示活动的下一个通道是从 `rest_init()` 到 `user_mode_thread()` / `kernel_clone()` 的任务创建，而不是早期的 RCU 微型帮助程序调用站点，也不是 DT/procfs/nsfs/pidfs 启动。
- 托管工作负载强化现在按层明确划分：
  - PR 通道：基准测试/polybench/投资组合/调整工件发布、PTO 奇偶校验和 TSVC 仅编译严格覆盖范围为绿色。- 运行时繁重的后续工作：活动的存储库 SPEC 通道是 CPU2017 Stage A，而不是签入的 SPEC CPU2006 语料库。新的 2026 年 5 月 17 日非规范重新运行显示，纯静态 `999.specrand_ir` 现在达到了与 initramfs 冒烟相同的后期内核任务创建停顿，而动态 `531.deepsjeng_r` 仍然较早被阻止，因为 `phase-c` 共享 musl 打包仍然缺少 `libc.so` (`m3_notext_probe_signature=ld.lld: error: relocation R_ZXTERMEN45QXZV5_64_BNEXT cannot be used against symbol 'malloc'; recompile with -fPIC`)。在最新的诊断重新运行中，TSVC QEMU 运行时仍然失败。
- 剩余的超级项目工作：BusyBox rootfs Linux 运行时、SPEC Stage A over 9p/initramfs、TSVC 运行时、AVS 每夜宽度、QEMU 解码覆盖率、ABI/unwind/TLS 强化、特权/MMU/调试范围以及 SIMT/编译器成熟度。

## 关闭车道

### 标量

状态：第一封闭车道有效

- 优先级：
  - 没有显式SIMT autovec或tile内在源的通用C
  - 标量 ABI/运行时/工具链关闭
  - 直接返回调用 块头s 写为融合 `BSTART ... , ra=...`
- 所需的跨堆栈证据：
  - 编译器AVS编译套件+100%主动助记词覆盖率
  - 标量 运行时启动 asm 融合直接调用 块头s
  - QEMU 标量 调用/ret 合约运行时门
- 该车道明确的非目标：
  - 证明当前之前融合的手写 `ICALL ra=` 源语法
    解析器/MC 差距已弥合
  - 证明分组 SIMT 或瓦片降低成熟度

### SIMT

状态：部分/在标量之后上演- 优先级：
  - 保持记录的 SIMT 子集明确并经过验证
  - 仅在冻结子集边界内扩展分组通道/运行时闭包
- 规范计划：
  - `docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`
  - `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`

### 瓷砖

状态：部分/在标量之后上演

- 优先级：
  - 保持tile/TEPL编码和asm/手动同步绿色
  - 扩展解码/运行时语义，而不将其与 标量 混为一谈
    关闭

## 立即恢复通道（2026 年 3 月至 4 月）

状态：活跃1. 保留 2026 年 4 月 18 日签入的规范报告作为当前 PR 通道基线。
2. 关闭剩余的内核/用户空间运行时阻止程序：
   - 修复 BusyBox rootfs 运行时回归（当前信号：`/sbin/init` 之后的内核 `E_BLOCK`；针对干净固定的 QEMU 构建会重现相同的故障，并且当前使用 `ra=0` 落在 `FRET.STK` 上的 `__submit_bio` 中，而干净工作树 `switch_to` EBARG 回滚仅稳定详细信息启动），
   - BusyBox rootfs 通过后刷新规范收敛报告，以便 `Regression::strict_cross_repo.sh` 可以在无需豁免的情况下变绿。
   - 保持本地 initramfs 烟雾诊断与规范的 BusyBox 关闭不同：当前的烟雾拦截器是 `rest_init()` 之后的第一个任务创建切换，tiny-RCU 状态翻转已经内联在 灵犀 上，下一个实时调查目标缩小到 `kernel_clone()` / `copy_process()`。
3. 重新运行仍然阻止夜间关闭的运行时繁重的工作负载通道：
   - 一旦为动态工作台恢复了共享 musl 托管通道并且为静态工作台清除了内核任务创建停顿，则重新运行 CPU2017 Stage A QEMU 矩阵，
   - 重新运行 TSVC 严格 QEMU 门（仅当跳过 BusyBox 并在 `tsvc.auto.elf` 上 240 秒后超时时，最新的诊断重新运行才会到达此通道），
   - 每次修复后重新分类下一个 Linux/用户空间运行时故障。
4. 恢复夜间 AVS 对解码/块边缘情况、原子、FP、向量 运行时和 Linux 工作负载启动语义的广泛工作。

## 里程碑### M1（1-2周）：恢复被破坏的严格门先决条件

状态：进行中

- 本次刷新完成：
  - 检查表/清单所有权现在包括 AVS 规范化/审核以及 3 月 15 日规范报告中记录的工作负载回归行。
  - 执行顺序 Runbook 现在位于 `docs/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md` 中。
  - 4 月 18 日的规范报告捕获了 PR 层 AVS 关闭、模型差异恢复、PTO 奇偶校验、TSVC 仅编译覆盖率、glibc/musl 运行时恢复和 灵犀Core/Testbench/Trace/pyCircuit 叶恢复。
- M1 剩余：
  - `LINUX-004`，
  - `INT-004`通过BusyBox依赖的严格闭排，
  - CPU2017 Stage A 工作负载通道、TSVC 运行时和 AVS 夜间宽度的夜间/运行时跟进。

### M2（3-6周）：AVS核心覆盖范围扩展

状态：PR 级别部分完成；夜间宽度仍然开放

- 将 2026 年 4 月 18 日 PR 子集固定在已证实的 `31` 所需 ID 上。
- 接下来实现剩余的夜间 AVS ID：`DEC/BLK edge cases`、`BR exact scaling`、`MEM endianness/misalignment`、`ATOM`、`FP`、`VEC`、运行时直方图语义和 SPEC/工作负载启动语义。
- 添加专用 SIMT 内核编译矩阵，用于分组通道启动、内部
  控制流程，以及 `.local` 一旦上面的合约页面被临时使用
  冻结了。
- 将 AVS 矩阵状态验证提升为严格的成熟度工件：
  - 检查器：`tools/bringup/check_avs_matrix_status.py`
  -神器：`docs/bringup/gates/avs_matrix_status_audit.json`

### M3（4-8 周）：模拟器/模型完整性门

状态：已启动（覆盖率报告已落地；PR 通道兼容性包装已恢复）- 保持机器生成的规范 ISA-vs-QEMU 覆盖率报告：
  - `tools/bringup/report_qemu_isa_coverage.py`
- 将 `run_model_diff_suite.py` 所需的覆盖范围从 标量/basic 扩展到 向量/tile + 重启/故障场景。
- 添加 SIMT 块体 执行/运行时覆盖范围：
  - 分组启动映射，
  - 分支重的内核，
  - 部分车道进度，
  - 编译器生成的 `.local` 状态。
- 通过明确的非法陷阱保持不支持的指令的确定性，直到实施为止。

### M4（4-10 周）：托管工具链/运行时工作负载成熟度

状态：已计划（PR 编译/工件通道绿色；运行时执行通道仍然打开）

- 在`docs/bringup/agent_runs/checklists/specint_qemu.md`中关闭`SPEC-001..SPEC-007`；将未签入 SPEC CPU2006 语料库视为单独的资产/先决条件问题，而不是作为当前 CPU2017 Stage A 运行时通道已关闭的证据。
- 保持规范的工作负载报告最新； PTO 奇偶校验在 `2026-04-18-r9-pin-linuxlibc-refresh` 中反映为绿色。
- 保持 9p/virtfs 兼容性 (`LINUX-003`) 作为 SPEC 通道的硬性先决条件。
- 一旦双通道证据稳定，就将 C++ 运行时策略发展到超出当前的 no-EH/no-RTTI 基线。
- 将 ABI/unwind/TLS 检查表转换为可执行的运行时门。

### M5（6-12 周）：特权/MMU/调试奇偶校验

状态： 计划中

- 关闭 `docs/bringup/ISA_GAP_ANALYSIS.md` 中的特权/MMU/调试间隙。
- 添加针对可重新启动磁贴故障和桥接内存排序的 Linux 自测试。
- 定义最小调试架构契约（单步、断点/观察点、权限交互）。

### M6（正在进行）：性能和发布级平价

状态： 计划中- 将基准测试方法和工件规则保留在 `workloads/generated/` 之下。
- 跟踪静态/动态指令趋势和优化路线图闭合。
- 扩展类似 CI 的编排，以实现全堆栈、跨存储库的可重复性。

## SIMT 特定规划页面

- 建筑详细规划：
  `docs/architecture/v0.56-simt-compiler-contract-plan.md`
- 编译器成熟计划：
  `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`

这些页面完善了更广泛的成熟度工作的 `VEC`/SIMT 通道。他们确实
不取代主要到期计划；他们提供了缺失的深度
当前的 LLVM/QEMU/AVS SIMT 子集。

## 所需的策略默认值

- 默认情况下，对于所需的严格门禁没有新的豁免。
- 仍然需要双通道促销（`pin` + `external`）。
- 现有严格的绿色门槛仍然是强制性的，而成熟度门槛则逐步增加。