# v0.56 ISA 子模块对齐计划

该计划跟踪协调实施所需的子模块升级
与规范的 v0.56 ISA 手册和生成的编码目录堆栈。

## 范围

- 规范 ISA 源：`isa/v0.56/` 和
  `docs/architecture/isa-manual/src/`。
- 超级项目引脚通道：此存储库记录的已提交子模块 SHA。
- 外部通道：灵犀指令集 拥有的子模块中的活动上游分支。
- 关闭门：`LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 bash tools/regression/strict_cross_repo.sh`。

## 对齐矩阵

|子模块 |升级目标|需要 v0.56 工作 |门证据|
| --- | --- | --- | --- |
| `compiler/llvm` |导入 v0.56 操作码和寄存器目录后固定已提交的 LLVM 后端更新。 |刷新 TableGen/汇编器/反汇编器编码、块边界合法性、向量 内存格式以及针对生成的目录的调用/返回降低。 |在 `avs/compiler/linx-llvm/tests/` 加上严格的跨存储库编译通道下编译 AVS 测试。 |
| `emulator/qemu` |登陆并固定 QEMU v0.56 解码/运行时更新。 |重新生成操作码元数据，对齐 CPU 状态/寄存器定义，实施 v0.56 向量 和内存编码更改，并保留断点/半主机分割。 | `avs/qemu/` 下的运行时 AVS、QEMU 解码烟雾测试和严格的跨存储库运行时通道。 |
| `kernel/linux` |在 QEMU 可以启动新合约后，登陆并固定 Linux ABI/运行时更新。 |更新 灵犀指令集 ABI 注释、进程/线程上下文处理、调度程序/抢占诊断和 v0.56 运行时假设的 rootfs 脚本。 | Busybox/rootfs 启动烟雾、ctx-tu/ctx-tq 诊断和严格的跨存储库运行时通道。 |
| `rtl/LinxCore` |一旦本地 ISA 对齐编辑落地，就固定提交的 灵犀Core 操作码目录刷新。 |将操作码目录、解码元数据、块结构合约、ROB/簿记、跟踪模式和 cosim 锁步行为与 v0.56 对齐。 | 灵犀Core 单元测试，生成 RTL 安全门、cosim 锁步烟雾和 灵犀Trace lint。 |
| `tools/model` |本地 ISA 执行更新落地后固定已提交的模型固定分支。 |刷新 v0.56 目录的 `minst` 编解码器生成、执行状态、ELF/程序加载、主机系统调用行为和 JSON 跟踪格式。 |通过 `tests/checks/check_avs_runtime_smoke.py` 进行模型单元/系统测试以及 AVS 运行时烟雾。 |
| `tools/pyCircuit` |在上游活动分支后固定 pyCircuit PTO/手动源更新。 |保持 pyCircuit 流程和 PTO 手动生成与 v0.56 块、图块和编码术语一致。 | pyCircuit C++ 后端烟雾、QEMU-vs-pyC 比较流程以及 PTO 手动生成检查。 |
| `lib/glibc` |保持当前引脚，除非 ABI 更改需要 libc 刷新。 |验证编译器、QEMU 和内核收敛后的加载程序/共享库行为。 | glibc 加载器烟雾和严格的跨存储库 libc 通道。 |
| `lib/musl` |保持当前 pin 直到本地工具链脚本更改登陆 musl。 |根据 v0.56 ABI 更改确认仓库内工具链默认值和启动假设。 | musl 静态 hello/运行时烟雾和严格的跨存储库 libc 通道。 |
| `workloads/pto_kernels` |保留当前引脚，直到提交并审查内核目录清理。 |将旧类型示例重命名为 v0.56 中性内核、更新tile asm 合约并刷新状态站点清单。 | PTO 内核清单检查、tile asm 合同检查和基准状态站点构建。 |
| `skills/linx-skills` |固定 v0.56 手动导航的最新规范技能更新。 |将启动代理保留在 v0.56 手册、编码目录和子模块关闭工作流程中。 | `check_skill_change_scope.py` 在改变技能时加上安装/修剪试运行。 |

## 执行顺序

1. 将超级项目 ISA/手动刷新和计划更新作为活动项目
   合约面。
2. 对于每个实现子模块，提交并 PR 本地 v0.56 工作
   在重新固定超级项目之前拥有存储库。
3. 仅重新固定推送到其规范上游远程的子模块 SHA。
4. 在瓶道上运行 PR 级严格封闭门。
5. 在标记 repin 准备就绪之前，在外部车道上运行相同的门
   合并。
6. 仅在经过必要的检查和门控证据后才压缩合并超级项目 PR
   是绿色的。

## 立即执行的 v0.56.4 更新车道

### LLVM repin 车道（`ea930273ec2acffa98491bf7057894dbd3f54c90`）

目标：把编译器车道从目录版本对齐推进到可 repin 的候选提交，同时保持现有
编译闭包不回退，并清掉当前剩余的编译侧阻塞项。

1. 先把 `compiler/llvm` 规范化到正确的上游分支，再处理本地 cherry-pick
   或重生成产物。
2. 将刷新后的 `isa/v0.56/linxisa-v0.56.json` 目录重新导入 LLVM 后端里
   消费操作码/寄存器元数据的表面。
3. 重新运行当前 pin 已通过的编译证明集：
   `avs/compiler/linx-llvm/tests/run.sh`（`linx32`、`linx64`），
   `analyze_coverage.py` 100%，以及辅助工具构建
   （`llvm-ar`、`llvm-nm`、`llvm-readelf`、`llvm-strip`）。
4. 排查当前严格 PR 车道的剩余编译侧阻塞项：
   `python3 workloads/tsvc/run_tsvc.py ... --no-run-qemu`。
5. 只有在 LLVM 自有仓库先落上游提交，并且保持上述证明集与 TSVC gate
   通过后，才回 pin 超级项目。

退出条件：

- `linx32` / `linx64` 编译 AVS 通过；
- 编译覆盖率保持 100%；
- LLVM 辅助工具构建通过；
- TSVC 严格 gate 在候选提交上通过。

### QEMU repin 车道（`12b28e847e2e94bed322da122b147f00a9633727`）

目标：落地运行时侧的 `v0.56.4` 目录更新，并清掉当前阻止 repin 的严格 PR
车道运行时阻塞项。

1. 先从刷新后的 `isa/v0.56/linxisa-v0.56.json` 目录重生成 QEMU 侧的
   opcode/decode 元数据，再改运行时行为。
2. 使用
   `tools/bringup/run_qemu_build_clean.sh --qemu-root emulator/qemu`
   重新构建候选 QEMU。
3. 重新运行运行时证明集：
   `avs/qemu/run_tests.sh --all --timeout 10` 和
   `avs/qemu/check_system_strict.sh`。
4. 把当前 all-suites timeout 作为第一优先级的运行时 repin 阻塞项。严格
   车道在当前 pin 已经能稳定走到这个失败点。
5. BusyBox / 全系统启动回归仍然保留在范围内，但在 PR stop path 的超时
   问题解决后再继续推进。当前仓库注记把该回归定位在
   `finish_task_switch` / `FRET.STK` 附近。
6. 只有在 QEMU 自有仓库先落上游提交，并且运行时 AVS 与 strict-system
   gate 清绿后，才回 pin 超级项目。

退出条件：

- 候选提交可干净重建 QEMU；
- `avs/qemu/run_tests.sh --all --timeout 10` 通过；
- `avs/qemu/check_system_strict.sh` 通过；
- Linux 启动后续检查没有新增回归。

## 当前风险

- 多个实现子模块当前包含未提交的本地编辑；
  这些编辑在落地之前不能由超级项目 SHA 表示
  在他们拥有的存储库中。
- `compiler/llvm` 在此结帐中报告未初始化的本地分支状态，
  因此 LLVM 必须先进行标准化，然后才能参与闭包门。
- 完全严格的关闭可能会失败，直到 QEMU、模型、灵犀Core 和工作负载全部完成
  使用重新生成的 v0.56 编码目录。
