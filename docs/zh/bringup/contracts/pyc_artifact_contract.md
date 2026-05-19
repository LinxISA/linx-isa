# pyCircuit 神器合约

## 权威和来源根源

- pyCircuit 的事实来源可以是：
  - 固定子模块：`tools/pyCircuit`（推荐用于再现性），或者
  - 外部结帐（设置 `PYCIRCUIT_ROOT=/path/to/pyCircuit`）。
- 灵犀 CPU源码根：
  - `tools/pyCircuit/examples/linx_cpu_pyc`
- Janus 源根：
  - `tools/pyCircuit/janus/pyc/janus`

`linxisa` 不会手动创作这些 RTL/模型源。

## 所需的生成输出

对于每个跟踪的核心目标：

- Verilog RTL：`*.v`
- C++循环模型块头s：`*_gen.hpp`
- 测试平台执行日志（C++ 和 RTL 模拟路径）

pyCircuit 中推荐的生成位置：

- 灵犀 生成的工件：`tools/pyCircuit/examples/generated/linx_cpu_pyc/`
- Janus 生成的工件：`tools/pyCircuit/janus/generated/`

## 规范生成入口点

- `bash tools/pyCircuit/scripts/pyc build`
- `bash tools/pyCircuit/scripts/pyc regen`
- `bash tools/pyCircuit/janus/update_generated.sh`

如果使用外部结帐，请在这些路径前加上 `$PYCIRCUIT_ROOT/` 前缀。

## 再现性规则

- 复制/暂存到 `linxisa` 中的生成工件必须来自脚本，而不是手动编辑。
- 每个启动门都必须记录所使用的命令和神器来源。
- 如果生成器版本发生变化，请在门注释中记下版本/提交。
- 与 灵犀Core 的接口兼容性必须通过 `docs/bringup/contracts/pyc_linxcore_interface_contract.json` 进行版本控制。