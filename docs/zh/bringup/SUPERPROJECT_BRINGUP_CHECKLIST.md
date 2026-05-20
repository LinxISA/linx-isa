# 灵犀指令集 超级项目启动阻止清单

将此运行手册用于 `linx-isa` 中当前的**红门恢复通道**
超级项目。它反映了 2026 年 4 月 18 日签入的规范门报告，
不是旧的 3 月 15 日基线。

它故意比完整期限计划更窄：

- 重点关注执行顺序中最新的阻塞启动工作；
- 它假设每个域所有者清单对于模块细节仍然是规范的；
- 它命名夜间/运行时后续通道，而不试图在此处关闭它们。

详细的业主清单仍然存在于
`docs/bringup/agent_runs/checklists/`。
使用此页面决定**先做什么**，然后交给所有者
特定于模块的关闭标准的检查表。

## 基线

- 规范基线：[`docs/bringup/gates/latest.json`](gates/latest.json)，
  生成 `2026-04-18 02:11:34Z`，最新的 pin-lane 运行
  `2026-04-18-r9-pin-linuxlibc-refresh`。
- 4 月 18 日的报告取代了 Sail/model、PTO 的过时的 3 月行
  奇偶校验、AVS PR 层闭包、glibc/musl 运行时、灵犀Core/Testbench/Trace、
  pyCircuit 和 TSVC 仅编译 PR 报道。
- 此清单的范围：
  - `LINUX-004`
  - `INT-004`
  - `INT-016`
  - `INT-025`
  - `SPEC-003` / `SPEC-004` 作为夜间/运行时后续

## 当前拦截器地图

|面积 |登机口/身份证 |当前状态 |分诊注意事项|
| --- | --- | --- | --- |
|内核| `Kernel::Linux busybox rootfs boot` / `LINUX-004` |主动拦截器 | rootfs 通道仍然需要无固件启动 (`-bios none`)。本地后续行动现已清除了早期的 灵犀 解析器/VDSO/页表/API 阻止程序，解决了第一个 `fs/nfs` 和 `fs/lockd` SelectionDAG 崩溃以及后续的 `lib/random32.o` 崩溃，并且仍然没有新的 rootfs 判决，因为重建的内核稍后在 `lib/hexdump.o` 停止。 |
|内核| ``Kernel::Linux `vmlinux` build closure`` / `LINUX-005` |主动依赖| 4 月 18 日的规范运行仍然是最后的绿色证明。当前的本地重新验证远远超出了旧的汇编程序、VDSO 和 MM 胶水阻断程序；当前的确定性停止现在是 `lib/hexdump.o` (`hex_to_bin`) 中相同 灵犀 SelectionDAG 崩溃系列的后续重复，这是针对早期 `fs/nfs`、`fs/lockd` 和 `lib/random32.o` 故障的本地对象范围 向量izer 解决方法之后的重复。 |
| LLVM 灵犀 目标 | `Compiler::AVS compile suites` + 覆盖 |主动依赖 | AVS/覆盖通道保持绿色，并且针对 `.option push/pop/norelax` 和 `.word/.half/.dword` 解析修复了本地集成汇编器兼容性差距。当前 Linux 闭包的编译器端阻止程序不再是解析器接受；它是 `fs/nfs` 中较大 C 文件的后端代码生成稳定性。 |
|严格封闭| `Regression::strict_cross_repo.sh` / `INT-004` |主动拦截器 |该行失败是因为所需的 BusyBox rootfs 门在同一运行中失败。除非重现，否则不要恢复过时的 March Sail 解码诊断。 |
| 混合磁贴 + SIMT 工作负载 | `Regression::PTO kernel parity` / `INT-020` |没有被屏蔽| 4 月 18 日的规范运行记录 PTO 平价为通过。 |
| SIMT 自动化 | `Regression::TSVC strict coverage gate` / `INT-025` | PR 未被屏蔽 | PR 闭包在 `148/151` 处使用仅编译严格覆盖； QEMU 运行时仍然是单独的夜间/运行时后续。 |
| QEMU 基线 | `Emulator::QEMU all suites` + `QEMU strict system` |没有被屏蔽|基线运行时/系统门为绿色；该通道的剩余 QEMU 问题是 TSVC 运行时再现，而不是广泛的解码扩展。 |
|超级项目广度| `ISA::AVS tier closure` / `INT-016` | PR 未被屏蔽 | PR 层关闭在 `31/31` 处为绿色；夜间宽度仍然是`32/54`。 |
|规格运行时 | `Regression::SPEC stage A QEMU matrix` / `SPEC-003` |每晚/运行时拦截器 | PR 运行让该行选择加入。当前的 2026-05-17 非规范证据是分裂的：静态 `999.specrand_ir` 现在达到了与烟雾启动相同的后期内核任务创建停顿，而动态 `531.deepsjeng_r` 仍然更早被阻止，因为 `phase-c` 托管的 musl 包装没有 `libc.so`。 |

## 1. 保持 Gate Truth 最新

- [x] 将陈旧的 3 月 15 日 Sail 解码和 PTO 奇偶校验失败视为已替换
      根据 4 月 18 日的规范报告。
- [x] 从刷新的 JSON 报告重新渲染门状态降价：

  ```bash
  python3 tools/bringup/gate_report.py render \
    --report docs/bringup/gates/latest.json \
    --out-md docs/bringup/GATE_STATUS.md
  ```

- [ ] 如果您需要发布刷新的规范报告，请运行新的收敛
      通过而不是仅编辑 Markdown：

  ```bash
  LINX_GATE_TIER=pr \
  bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id>
  ```

- [ ] 不要将“Sail 解码生成器损坏”或 `INT-020` 作为主动拦截器
      除非它们在当前工作空间状态下再次再现，否则以散文形式呈现。

退出标准：- 在当前规范报告中，帆/模型状态和 PTO 奇偶校验为绿色。
- 门状态降价由 `docs/bringup/gates/latest.json` 生成。

## 2. 恢复 BusyBox Rootfs 运行时 (`LINUX-004`)

- [x] 通过干净的 `vmlinux` 帮助器保持 `LINUX-005` 关闭：

  ```bash
  bash tools/bringup/run_linux_vmlinux_build_clean.sh \
    --linux-root "$PWD/kernel/linux" \
    --out-dir "$PWD/kernel/linux/build-linx-fixed" \
    --clang "$PWD/compiler/llvm/build-linxisa-clang/bin/clang" \
    --gmake /opt/homebrew/bin/gmake \
    --target vmlinux
  ```

- [ ] 使用干净的辅助路径和无固件 QEMU 启动重现当前 BusyBox rootfs 故障：

  ```bash
  QEMU="$(bash tools/bringup/run_qemu_build_clean.sh \
    --qemu-root "$PWD/emulator/qemu" \
    --out-dir /tmp/linx-qemu-clean-build \
    --target qemu-system-linx64)" \
  ROOTFS_IMG="$(bash tools/bringup/run_linux_busybox_rootfs_build_clean.sh \
    --linux-root "$PWD/kernel/linux" \
    --out-dir /tmp/linx-linux-rootfs-clean-out \
    --llvm-build "$PWD/compiler/llvm/build-linxisa-clang")" \
  SKIP_BUILD=1 QEMU="$QEMU" QEMU_EXTRA_ARGS='-bios none' \
    python3 kernel/linux/tools/linxisa/busybox_rootfs/boot.py
  ```

- [ ] 在迭代时保持 initramfs Smoke/full boot 为绿色，并将它们视为阻止程序特定于 virtio-blk/ext2 用户空间通道而不是最小 BusyBox 二进制文件的证据。

  ```bash
  python3 kernel/linux/tools/linxisa/initramfs/smoke.py
  python3 kernel/linux/tools/linxisa/initramfs/full_boot.py
  ```

退出标准：

- `LINUX-004` 到达 BusyBox 用户空间并干净地关闭电源。
- `LINUX-005`，冒烟，完全启动后保持绿色。

## 3. 对第一次真正失败重新运行严格关闭 (`INT-004`)

- [ ] 步骤2完成后，重新运行严格关闭。
- [ ] 刷新签入门时首选规范收敛包装器
      真相：

  ```bash
  LINX_GATE_TIER=pr \
  bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id>
  ```

- [ ] 当单独迭代 `strict_cross_repo.sh` 时，重复使用精确的
      `Regression::strict_cross_repo.sh`命令记录在
      [`docs/bringup/gates/latest.json`](gates/latest.json) 用于主动运行
      形状，因此环境与失败的行匹配。
- [x] 将陈旧的 March Sail 首次故障诊断替换为当前的诊断
      BusyBox-rootfs驱动的严格关闭失败。
- [ ] 不要将“Sail解码生成器损坏”保留为活动的`INT-004`
      除非它在当前工作空间下再次再现。

退出标准：- `INT-004` 指出当前第一个真正的失败，而不是陈旧的三月航行
  失败。
- 重新运行具有新的运行 ID、更新的日志路径和刷新的多代理
  总结。

## 4. 将 TSVC PR 覆盖范围与运行时跟进分开 (`INT-025`)

- [x] 保持 PR 通道仅编译严格覆盖，直到自动运行时
      挂起已关闭。专用运行时分类仍应对
      第一个挂内核
      [`docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`](SIMT_COMPILER_SUPPORTED_SUBSET.md)
      恰好是以下之一：
  - 在记录的支持子集中；
  - 故意 标量 后备；
  - 因缺少分组 EXEC 掩码保存/恢复支持而被阻止。
- [ ] 在运行时分类期间保持当前架构边界明确：
  - 分组的单块 if-convert 和 active-replay 形状是有效的工作；
  - 原始分组多块分歧仍然故意未关闭，因为
    标准表面缺少一流的 `p` 保存/恢复载体。
- [ ] 仅在记录的子集中促进支持。如果形状超时
      不属于该子集，请将问题视为工作负载策略或覆盖范围
      范围，而不是作为已经需要分组发散闭包的证据。

退出标准：

- PR 通道在记录的 `148/151` 中使用仅编译严格覆盖
  地板而不是陈旧的 `151/151` QEMU 门。
- 专用运行时后续仍然有记录的第一个挂起内核和
  记录的分类。

## 5. 重新运行关闭审计- [ ] 将以下命令视为 **repo-root 命令**。如果您需要`cd`
      进入子目录，首先捕获根目录：

  ```bash
  ROOT=$PWD
  ```

- [ ] 相关更改后重新运行当前工作负载 PR 检查：

  ```bash
  python3 workloads/pto_kernels/tools/run_pto_kernel_parity.py --timeout 120
  python3 workloads/tsvc/run_tsvc.py --clang compiler/llvm/build-linxisa-clang/bin/clang --lld compiler/llvm/build-linxisa-clang/bin/ld.lld --ZXTERMEN42QXZ-mode auto --strict-fail-under 148 --source-policy linx-v03-parity --no-run-qemu --out-dir workloads/generated
  ```

- [ ] 重新运行集成广度检查：

  ```bash
  python3 tools/bringup/check_avs_profile_closure.py \
    --matrix avs/linx_avs_v1_test_matrix.yaml \
    --status avs/linx_avs_v1_test_matrix_status.json \
    --tier pr
  ```

- [ ] 在 BusyBox 修复后重新运行严格关闭：
  - 规范报告刷新：`tools/bringup/run_runtime_convergence.sh`
  - 集中迭代：当前的精确 `strict_cross_repo.sh` 命令
    门报告行
- [ ] 仅根据新的重新运行证据更新集成检查表状态。

退出标准：

- 陈旧的拦截器已被当前证据取代；
- `LINUX-005`已解决，`LINUX-004`携带当前失败日志；
- `INT-025` 仍然是 PR 编译覆盖门，运行时单独跟踪；
- `INT-016` 和 `INT-004` 反映了当前的重播证据，而不是 3 月份的结转证据。

## 假设和默认值

- 此页面仅限于当前内核的超级项目阻止程序切片，
  LLVM/SIMT autovec、混合切片/SIMT 工作负载、QEMU 基线和严格
  关闭。
- 2026 年 4 月 18 日的规范报告是签入的基线，直到更新
  规范运行取代了它。
- glibc 运行时、灵犀Core、Testbench、Trace 和中特定于所有者的 PR 门
  pyCircuit 在当前基线中为绿色；他们夜间的宽度仍然存在
  单独的后续工作。
