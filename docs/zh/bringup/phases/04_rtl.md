# 第 4 阶段：RTL 启动和验证 (Agile pyCircuit)

主要 RTL 注释：`rtl/README.md`

## 范围和事实来源

- 架构/规范权威：`linxisa`（`isa/v0.56/`、`isa/v0.56/linxisa-v0.56.json`、`isa/generated/codecs/`）。
- RTL/模型生成权限：
  - 固定子模块：`tools/pyCircuit`（推荐用于再现性）
  - 或外部结帐（设置 `PYCIRCUIT_ROOT=/path/to/pyCircuit`）。
- 核心目标：
  - 首先是 **灵犀 CPU**
  - **Janus 核心** 第二

Linux 最终目标在后续阶段（`05_fpga_zybo_z7.md`、`06_linux_on_janus.md`）中处理，但此阶段必须
生成稳定且可区分的模型/RTL 作为先决条件。

## 合同（强制链接）

- 神器合约：`docs/bringup/contracts/pyc_artifact_contract.md`
- 追踪合约：`docs/bringup/contracts/trace_schema.md`
- FPGA 平台默认值（用于下游兼容性）：`docs/bringup/contracts/fpga_platform_contract.md`

## 所需的架构调整

- 控制流目标必须落在块开始标记上。
- 块边界必须在 `BSTOP` 或下一个块开始时提交。
- `SETC.*` 必须在块内执行并提供提交时控制流。
- 模板块（`FENTRY`/`FEXIT`/`FRET.*`）是独立块。

## 工作流 A：灵犀 CPU 敏捷循环

### 参赛标准

- `linxisa` 中的编译器和 QEMU 回归为绿色。
- `pyCircuit` 工具链构建（`scripts/pyc build`）并可以重新生成输出（`scripts/pyc regen`）。

### 实现循环

一次冲刺 = 一个功能切片（指令/CSR/异常/管道规则）：1. 实现/更新 pyCircuit 源代码：
   - `tools/pyCircuit/examples/linx_cpu_pyc/`（或`$PYCIRCUIT_ROOT/examples/linx_cpu_pyc/`）
2. 通过规范脚本重新生成 C++ 和 Verilog 工件。
3. 在相同的程序 向量 上运行 C++ 和 RTL 仿真。
4. 使用跟踪合约与 QEMU 进行比较。

### 规范跑步者

- `bash tools/pyCircuit/tools/run_linx_cpu_pyc_cpp.sh`
- `python3 tools/pyCircuit/tools/pyc_flow.py verilog-sim linx_cpu_pyc --tool verilator`

（如果使用外部结账，请在这些路径前加上 `$PYCIRCUIT_ROOT/` 前缀。）

### 退出标准

- Smoke 套件通过了 C++ 和 RTL 模拟。
- 在支持的指令子集中与 QEMU 没有确定性分歧。
- 工件是可复制的并且由脚本生成（无需手动编辑）。

## 工作流 B：Janus 核心稳定

### 参赛标准

- 工作流 A 退出标准已完成。
- Janus 生成的工件可以从 `tools/pyCircuit/janus`（或 `$PYCIRCUIT_ROOT/janus`）中的源刷新。

### 规范跑步者

- `bash tools/pyCircuit/janus/tools/run_janus_bcc_ooo_pyc_cpp.sh`
- `bash tools/pyCircuit/janus/tools/run_janus_bcc_ooo_pyc_sv.sh`
- `bash tools/pyCircuit/janus/tools/run_janus_bcc_ooo_pyc_verilator.sh`
- `bash tools/pyCircuit/janus/tools/run_janus_benchmarks.sh`

（如果使用外部结帐，请在这些路径前加上 `$PYCIRCUIT_ROOT/` 前缀。）

### 验证

- 重复使用相同的 向量，其中 灵犀 和 Janus ISA 行为重叠。
- 针对支持的子集添加针对 QEMU 的 Janus 特定 difftest 门。
- 将不支持的功能明确标记为当前门范围之外。

### 退出标准

- Janus C++ 和 Verilog 模拟通过定义的烟雾程序。
- 基准脚本运行并产生一致的架构结果。
- 剩余的增量由所有者和阻止者记录。

## 将工件摄入 `linxisa`

`linxisa` 存储计划、合同和验证结果。需要时，阶段生成的集成材料为：- `rtl/` 用于集成包装器或快照
- `tools/pyCircuit/` 用于模型源和包装器
- `tools/` 用于可重现的导入/检查脚本

直接创作保留在 pyCircuit 中（固定 `tools/pyCircuit` 或外部 `$PYCIRCUIT_ROOT`）； `linxisa` 中复制的工件必须是脚本派生的。