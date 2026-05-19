# 灵犀指令集 差距分析（v0.2 -> Tier-1）

最后更新: 2026-05-15

本文档总结了 灵犀指令集（规范、
工具链、模拟器、验证），标记已知的不一致，并映射每个
与此存储库中的具体工件和启动门之间的差距。

主要路线图：`docs/bringup/MATURITY_PLAN.md`。

## 这里的“Tier-1”是什么意思

与 Arm/x86/RISC-V 成熟度相当意味着：

- 明确且可机器检查的规范（编码+语义+陷阱）。
- 正确、经过充分测试且可调试的编译器/工具链。
- 一个正确的、确定性的、可观察的并且可用作参考模型的模拟器。
- 具有明确的通过/失败标准和覆盖范围的验证套件 (AVS)。

## 当前的优势（回购协议中的证据）

- 黄金操作码数据库和生成的 JSON 目录：
  - `isa/v0.56/` -> `isa/v0.56/linxisa-v0.56.json`
- 编码冲突检查和漏洞报告：
  - `python3 tools/isa/report_encoding_space.py --check`
  - 报告：`docs/reference/encoding_space_report.md`
- 使用每个目标输出时，LLVM 后端具有完整的助记符反汇编覆盖率：
  - `python3 avs/compiler/linx-llvm/tests/analyze_coverage.py --out-dir avs/compiler/linx-llvm/tests/out-linx64 --fail-under 100`
- 基准测试工具具有静态和动态指令统计信息：
  - `python3 workloads/run_benchmarks.py --dynamic-hist`

## 关闭类别

### 标量- 指令集：
  - 标量 块/调用/ret 语义是当前的第一个关闭通道
  - 直接调用源示例应使用融合的 `BSTART CALL, <target>, ra=<label>`
- 编译器：
  - 通用独立 C 覆盖范围较强，活动 LLVM AVS 通道为绿色
  - 直接调用源关闭现在预计将保持在 asm 级别融合，
    而目标代码可能仍低于相邻的 `setret`
-QEMU：
  - 标量 运行时/系统基线大大领先于 SIMT/tile 宽度
  - call/ret 正确性是 标量 关闭通道的一部分
- 剩余 标量 间隙：
  - 间接调用融合 `ra=` 源语法在当前版本上尚不可移植
    编译器分支，所以手写的`ICALL`仍然依赖显式相邻
    `setret/c.setret`

### SIMT

- 指令集：
  - 记录了规范的 `v0.56` 分组背离合约，包括
    显式 EXEC 掩码 (`p`) 控制
- 编译器：
  - 仅关闭记录的启动子集
  - 需要真正执行掩码保存/恢复的分组不同区域保持打开状态
-QEMU：
  - 存在一小部分运行时证据，但解码/运行时宽度是
    仍然不完整
- 剩余 SIMT 间隙：
  - 编译器、模拟器和 AVS 闭包都保持基于子集而不是
    全品类齐全

### 瓷砖- 指令集：
  - 瓦片/模板操作码目录和 TEPL 表面存在，但语义信封
    合法性验证仍需继续加强
- 编译器：
  - 存在 MC/asm 覆盖和 TEPL 编码检查，但通用 C 平铺闭包
    未被认领
-QEMU：
  - 平铺/模板解码覆盖范围和语义仍然不完整
- 剩余瓷砖间隙：
  - 磁贴关闭仍然主要是 ISA/MC/解码启动通道，而不是
    通用编译器/运行时关闭通道还没有

## 差距：ISA 规范

- 特权架构完整性：
  - 缺失或未明确：陷阱原因、陷阱优先级、精确状态捕获、
    CSR 重置值，以及哪些字段是 WARL 与固定字段。
  - 所需文物：
    - 扩展手册：`docs/architecture/isa-manual/src/chapters/10_system_and_privilege.adoc`
    - AVS覆盖范围：`avs/matrix_v1.md`（SYS区域）

- MMU和内存属性：
  - 没有完整的、可测试的转换定义、页表、TLB 失效、
    访问错误和可缓存性属性。
  - 培养策略：
    - 首先定义“无 MMU”配置文件门（当前），然后定义最小 MMU 配置文件。

- 调试架构：
  - 没有单步、断点/观察点、调试寄存器访问规则的规范，
    和特权交互。
  - 培养策略：
    - 从 QEMU 中的 GDB 远程支持 + 最小调试 CSR 合同开始。

- 矢量/图块语义信封：
  - 块合法性规则需要明确并经过测试（VPAR 与 VSEQ 中什么是合法的，
    以及什么会导致滥用）。
  - AVS 向量 测试：`avs/matrix_v1.md` 和 `avs/linx_avs_v1_test_matrix.yaml` 中的 `AVS-VEC-*`。

## 差距：内存模型和栅栏- 存储库现在记录了一个弱模型，但许多“尖锐边缘”仍然需要关闭：
  - 设备与正常排序、累积围栏意图和确切的 `.aq/.rl` 范围。
  - 参考章节：`docs/architecture/isa-manual/src/chapters/09_memory_operations.adoc`
  - 所需验证：
    - Litmus 测试消息传递和栅栏排序 (AVS-ATOM-010/011)。

## 差距：工具链（LLVM/Asm/Obj）

- ABI合约稳定性：
  - 注册角色、堆栈对齐、可变参数、TLS 和展开/调试信息必须是
    正式记录并测试。
  - 所需文物：
    - `docs/architecture/` 下的 ABI 文档（未来）
    - AVS ABI 测试 (AVS-ABI-001/002)

- 对象/重定位模型：
  - ET_DYN/动态链接还不是启动门；搬迁保险必须是
    在托管工作负载（LLVM 测试套件）运行之前进行扩展。
  - 证据：`avs/compiler/linx-llvm/tests/run.sh` 具有 PIC 重定位检查、共享库门控。

Disasm覆盖门人体工程学：
  - 如果使用过时的 `avs/compiler/linx-llvm/tests/out/` 目录，可能会导致错误故障。
  - 缓解措施：`avs/compiler/linx-llvm/tests/analyze_coverage.py` 自动检测 `out-linx*`。

## 差距：模拟器 (QEMU)

- 执行完整性：
  - 任何未在 QEMU 中实现的规范定义的指令必须确定性地捕获
    视为非法，不会静默执行或解码为不同的指令。
  - AVS 门：AVS-DEC-001、AVS-EMU-001。

- 可观察性和差异测试：
  - 稳定的提交跟踪模式必须由 QEMU 发出并由 RTL difftest 使用。
  - 合约：`docs/bringup/contracts/trace_schema.md`

## 差距：验证 (灵犀-AVS)- 矩阵存在，但许多测试尚未实施：
  - 矩阵：`avs/matrix_v1.md`
  - 机器可读：`avs/linx_avs_v1_test_matrix.yaml`
  - 所需工作：
    - 在`avs/qemu/`下实现运行时测试
    - 在`avs/compiler/linx-llvm/tests/`下实现仅编译/MC测试

## 差距：基准投资组合

- 存在第三方来源，但预计只有一个独立友好的子集
  早点跑：
  - 获取脚本：`workloads/fetch_third_party.sh`
  - 方法：`workloads/BENCHMARKING_METHOD.md`
  - 现实：
    - 托管工作负载（完整的 LLVM 测试套件、Google Benchmark）需要更多 libc
      和操作系统服务比当前最小环境提供的要多。

## 具体“填补缺失部分”清单

- 规格：
  - 关闭 标量 核心语义和陷阱的所有规范 TODO。
  - 使用重置值和非法/WARL 规则定义特权陷阱/CSR 行为。
  - 精确定义内存模型试金石期望和栅栏语义。

- 工具链：
  - 锁定 ABI 并添加 ABI 测试（调用、可变参数、堆栈对齐）。
  - 扩展重定位/对象模型并在准备好时启用 ET_DYN。
  - 将 disasm/asm 往返测试和覆盖率保持在 100%。

- 模拟器：
  - 确定性地实施缺失的指令或陷阱。
  - 发出 difftest 的提交跟踪并保持直方图工具稳定。

- 验证：
  - 实施 AVS 测试并将其视为主要的启动门。