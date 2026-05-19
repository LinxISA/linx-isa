# v0.56 ISA 子模块对齐计划

该计划跟踪协调实施所需的子模块升级
与规范的 v0.56 ISA 手册和生成的编码目录堆栈。

## 范围

- 规范 ISA 源：`isa/v0.56/` 和
  `docs/architecture/isa-manual/src/`。
- 超级项目引脚通道：此存储库记录的已提交子模块 SHA。
- 外部通道：灵犀指令集 拥有的子模块中的活动上游分支。
- 关闭门：`LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 bash tools/regression/strict_cross_repo.sh`。

## 对齐矩阵|子模块 |升级目标|需要 v0.56 工作 |门证据|
| --- | --- | --- | --- |
| `compiler/llvm` |导入 v0.56 操作码和寄存器目录后固定已提交的 LLVM 后端更新。 |刷新 TableGen/汇编器/反汇编器编码、块边界合法性、向量 内存格式以及针对生成的目录的调用/返回降低。 |在 `avs/compiler/linx-llvm/tests/` 加上严格的跨存储库编译通道下编译 AVS 测试。 |
| `emulator/qemu` |登陆并固定 QEMU v0.56 解码/运行时更新。 |重新生成操作码元数据，对齐 CPU 状态/寄存器定义，实施 v0.56 向量 和内存编码更改，并保留断点/半主机分割。 | `avs/qemu/` 下的运行时 AVS、QEMU 解码烟雾测试和严格的跨存储库运行时通道。 |
| `kernel/linux` |在 QEMU 可以启动新合约后，登陆并固定 Linux ABI/运行时更新。 |更新 灵犀指令集 ABI 注释、进程/线程上下文处理、调度程序/抢占诊断和 v0.56 运行时假设的 rootfs 脚本。 | Busybox/rootfs 启动烟雾、ctx-tu/ctx-tq 诊断和严格的跨存储库运行时通道。 |
| `rtl/ZXTERMEN45QXZCore` |一旦本地 ISA 对齐编辑落地，就固定提交的 灵犀Core 操作码目录刷新。 |将操作码目录、解码元数据、块结构合约、ROB/簿记、跟踪模式和 cosim 锁步行为与 v0.56 对齐。 | 灵犀Core 单元测试，生成 RTL 安全门、cosim 锁步烟雾和 灵犀Trace lint。 || `tools/model` |本地 ISA 执行更新落地后固定已提交的模型固定分支。 |刷新 v0.56 目录的 `minst` 编解码器生成、执行状态、ELF/程序加载、主机系统调用行为和 JSON 跟踪格式。 |通过 `tests/checks/check_avs_runtime_smoke.py` 进行模型单元/系统测试以及 AVS 运行时烟雾。 |
| `tools/pyCircuit` |在上游活动分支后固定 pyCircuit PTO/手动源更新。 |保持 pyCircuit 流程和 PTO 手动生成与 v0.56 块、图块和编码术语一致。 | pyCircuit C++ 后端烟雾、QEMU-vs-pyC 比较流程以及 PTO 手动生成检查。 |
| `lib/glibc` |保持当前引脚，除非 ABI 更改需要 libc 刷新。 |验证编译器、QEMU 和内核收敛后的加载程序/共享库行为。 | glibc 加载器烟雾和严格的跨存储库 libc 通道。 |
| `lib/musl` |保持当前 pin 直到本地工具链脚本更改登陆 musl。 |根据 v0.56 ABI 更改确认仓库内工具链默认值和启动假设。 | musl 静态 hello/运行时烟雾和严格的跨存储库 libc 通道。 |
| `workloads/pto_kernels` |保留当前引脚，直到提交并审查内核目录清理。 |将旧类型示例重命名为 v0.56 中性内核、更新tile asm 合约并刷新状态站点清单。 | PTO 内核清单检查、tile asm 合同检查和基准状态站点构建。 || `skills/linx-skills` |固定 v0.56 手动导航的最新规范技能更新。 |将启动代理保留在 v0.56 手册、编码目录和子模块关闭工作流程中。 | `check_skill_change_scope.py` 在改变技能时加上安装/修剪试运行。 |

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

## 当前风险

- 多个实现子模块当前包含未提交的本地编辑；
  这些编辑在落地之前不能由超级项目 SHA 表示
  在他们拥有的存储库中。
- `compiler/llvm` 在此结帐中报告未初始化的本地分支状态，
  因此 LLVM 必须先进行标准化，然后才能参与闭包门。
- 完全严格的关闭可能会失败，直到 QEMU、模型、灵犀Core 和工作负载全部完成
  使用重新生成的 v0.56 编码目录。