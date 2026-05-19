# 模拟器/QEMU 清单

## 关闭类别

### 标量

- 状态：主动关闭车道
- 范围：
  - 严格系统/运行时 AVS 基线
  - 标量区块合法性和call/ret合约行为
  - generic-C 标量 调用/ret 闭包与融合直接 `CALL ..., ra=...` 对齐
- 当前证据：
  - `QEMU-001`、`QEMU-002`、`QEMU-004`、`QEMU-006`、`QEMU-007`
- 剩余的 标量 特定间隙：
  - 融合的手写 `ICALL ra=` 源语法尚未在
    当前编译器分支，因此 QEMU 合约覆盖率仍然需要显式
    `setret/c.setret` 用于间接调用源测试

### SIMT

- 状态：部分/仅子集
- 范围：
  - 对当前记录的 SIMT 编译器子集的运行时支持
  - 没有声称完全分组发散闭合
- 当前证据：
  - 基线运行时/系统门是绿色的
  - 更广泛的 SIMT 运行时成熟度仍单独跟踪
    `docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`
- 剩余间隙：
  - 适用于分组不同内核和许多 `V.*` 解码的 QEMU 运行时广度
    表格仍然不完整

### 瓷砖

- 状态：部分
- 范围：
  - 平铺/模板解码表面和严格的合法性/陷阱行为
- 当前证据：
  - 操作码/元同步为绿色 (`QEMU-003`)
- 剩余间隙：
  - 平铺/模板解码频谱和语义覆盖仍然很重要
    规格目录后面- [x] ID：QEMU-001 通过严格系统门以及严格运行所需的定时器 IRQ 策略。
  命令：`cd avs/qemu && LINX_DISABLE_TIMER_IRQ=0 ./check_system_strict.sh`
  完成意味着：严格的系统套件通过，没有陷阱噪声回归。
  状态：✅ 通过（2026-02-25）-在运行 `2026-02-25-r2-pin-lanefix` 和 `*** REGRESSION PASSED ***` 中重新验证了严格的系统（日志：`docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/emu_strict_system.log`）。

- [x] ID：QEMU-002 通过带有超时预算的运行时 AVS 套件 (`--all`)。
  命令：`cd avs/qemu && ./run_tests.sh --all --timeout 10`
  完成意味着：所有运行时套件都通过并且日志附加到门证据。
  状态：✅ 通过 (2026-02-25) - `run_tests.sh --all --timeout 10` 在运行 `2026-02-25-r2-pin-lanefix` 中重新验证（日志：`docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/emu_all_suites.log`）。

- [x] ID：QEMU-003 保持重新生成的操作码元/ID 表与解码源同步。
  命令：`python3 tools/bringup/check_qemu_opcode_meta_sync.py --allowlist docs/bringup/qemu_opcode_sync_allowlist.json --report-out docs/bringup/gates/qemu_opcode_sync_latest.json --out-md docs/bringup/gates/qemu_opcode_sync_latest.md`
  文件：`emulator/qemu/target/linx/linx_opcode_ids_gen.h`、`emulator/qemu/target/linx/linx_opcode_meta_gen.h`
  完成意味着：操作码审计报告没有意外的解码/元漂移，也没有枚举/元操作 ID 不匹配。
  状态： ✅ 通过 (2026-03-07) - 从标准化 `insn48.decode` 目录重新生成 灵犀Core/QEMU 操作码表后，操作码同步审核返回 `qemu_opcode_meta_sync_ok` 以及 `decode_only_unexpected=0`、`meta_only_unexpected=0` 和 `id_mismatch_count=0`（工件： `docs/bringup/gates/qemu_opcode_sync_latest.json`、`docs/bringup/gates/qemu_opcode_sync_latest.md`）。

- [x] ID：QEMU-004 验证陷阱语义与 CFI/BLOCKFMT/BFETCH 的实时 v0.56 说明相匹配。
  完成意味着：在严格系统和模型差异门中没有观察到冲突的陷阱行为。
  状态：✅ PASS (2026-02-25) -严格系统和模型差异在运行 `2026-02-25-r2-pin-lanefix` 时都是绿色的（日志：`docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/emu_strict_system.log`、`docs/bringup/gates/logs/2026-02-25-r2-pin-lanefix/pin/model_diff_suite.log`）。- [x] ID：QEMU-005 ISA 规范与 QEMU 实现差距分析。
  命令：`python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md`
  完成意味着：刷新规范机器生成的覆盖率报告并捕获丢失的规范助记符和表格。
  状态： ✅ 通过 (2026-05-08) - 使用 `mnemonics=616/710`、`forms=612/740`、`missing_mnemonics=94` 和显式缺失/未映射列表生成的覆盖率报告（工件：`docs/bringup/gates/qemu_isa_coverage_latest.json`、`docs/bringup/gates/qemu_isa_coverage_latest.md`）。

- [x] ID：QEMU-006 QEMU 可以使用完整的运行时 API 启动完整的 Linux。
  完成意味着：Linux 内核启动，计时器 中断 工作，完整的系统调用可用。
  状态： ✅ 通过 (2026-02-25) - 在运行 `2026-02-25-r2-pin-lanefix` 时，完整操作系统关闭门为绿色（`strict_cross_repo.sh` 通行证和 BusyBox rootfs 引导通行证在 `kernel_busybox_rootfs.log` 中）。当前恢复工作的注意事项：合并的 灵犀64 恢复通道现在期望直接内核/rootfs 引导运行无固件 (`-bios none`)，因此本地 rootfs/SPEC 重新运行应保留 QEMU 调用策略。

- [x] ID：QEMU-007 在 v0.56 解码/翻译传播后构建固定的 `qemu-system-linx64`。
  命令：`ninja -C emulator/qemu/build qemu-system-linx64`
  完成意味着：固定的 QEMU 工作区使用当前解码/转换器状态编译 灵犀 系统模拟器二进制文件。
  状态： ✅ 通过 (2026-03-08) - 在 v0.56 传播修复和操作码同步刷新后，固定 QEMU `043390f788da` 成功构建 `emulator/qemu/build/qemu-system-linx64`。- [ ] ID：QEMU-008 保持 标量 调用/ret 合约覆盖范围与融合直接调用源语法一致。
  命令：`python3 avs/qemu/run_callret_contract.py`
  完成意味着：标量 直接呼叫源案例使用融合的 `CALL ..., ra=...`，畸形或缺失的 setret 降低仍然是故障，并且积极的 标量 直接呼叫案例仍然是无故障。
  状态： ✅ 通过 (2026-05-15) - 将 标量 直接调用源案例转换为融合的 `BSTART.STD CALL, ..., ra=...` 后，`run_callret_contract.py` 通过。阴性畸形/缺失固定病例仍被困住，阳性融合直接呼叫病例仍无过错。

---

## ISA 与 QEMU 实施差距分析

### 总结
- ISA规范：710个独特的助记符
- QEMU 映射规范覆盖范围：616 个独特的助记符
- QEMU 映射规范形式：612 种法律形式
- 差距：94 个助记符和 128 个表格目前在映射的 QEMU 解码覆盖范围之外

### 缺失指令的类别
1. **矢量指令（`V.*`）**：仍然是最大的未覆盖集，特别是在执行粒度上
2. **块/图块系列**：额外的 `BSTART.*`，图块/模板表单保持未覆盖状态
3. **压缩/HL 和会计漂移**：一些剩余的报告差距仍然是解码映射/报告问题，而不是经过证实的翻译人员缺席
4. **MMU/调试/系统广度**：当前启动子集之外的特权/系统系列仍然未被覆盖### 主要发现
- 实现了类似 RISC 的基本 ALU 操作（ADD、SUB 等）
- 实施块控制流程（BSTART/BSTOP）
- 实施原子操作（AMO）
- 实现系统指令（ACRC、ACRE、SSRGET/SRRSET）
- 矢量和瓦片操作仍然是主要的解码频谱差距