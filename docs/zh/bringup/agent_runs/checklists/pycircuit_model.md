# pyCircuit 模型清单

- [ ] ID: PYC-001 通过 pyCircuit CPU C++ 烟门。
  命令：`bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh`
  完成意味着：pyCircuit C++ CPU 流程通过烟雾执行。
  状态： ❌ 失败 (2026-03-15) - 在烟雾流开始之前，最新的 pin-lane 运行失败并显示 `missing pycc`（日志：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/pyc_cpu_cpp_smoke.log`）。

- [ ] ID：PYC-002 通过 QEMU 与 pyCircuit 跟踪差异门。
  命令：`bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh`
  完成意味着：模式检查通过并且跟踪差异与门控样本没有不匹配。
  状态：❌失败 (2026-03-15) - 最新的引脚通道运行达到跟踪生成，但在 pyCircuit 端编译示例之前以 `missing pycc` 中止（日志：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/pyc_trace_diff.log`）。

- [x] ID：PYC-003 通过 pyCircuit 接口合约门。
  命令：`python3 tools/bringup/check_pycircuit_interface_contract.py --root . --strict`
  完成意味着：合同文件、必填字段和流程脚本兼容性检查通过。
  状态： ✅ PASS (2026-03-15) - 最新的 pin-lane 合约报告记录 `ok=true` 没有错误（工件：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/pyc_interface_contract_report.json`）。

- [ ] ID：PYC-004 通过 pyCircuit 示例 nightly gateway。
  命令：`bash tools/pyCircuit/flows/scripts/run_examples.sh`
  完成意味着：示例编译/运行套件成功完成。
  状态：⚪ 未运行 (2026-03-15) - 最新的严格引脚运行使 pyCircuit 夜间门禁用 (`RUN_PYC_NIGHTLY_GATES=0`)。

- [ ] ID: PYC-005 通过 pyCircuit 模拟夜间门。
  命令：`bash tools/pyCircuit/flows/scripts/run_sims.sh`
  完成意味着：模拟套件通过且没有回归。
  状态：⚪ 未运行 (2026-03-15) - 最新的严格引脚运行使 pyCircuit 夜间门禁用 (`RUN_PYC_NIGHTLY_GATES=0`)。- [ ] ID: PYC-006 通过 pyCircuit 深夜模拟门。
  命令：`bash tools/pyCircuit/flows/scripts/run_sims_nightly.sh`
  完成意味着：夜间模拟车道关闭。
  状态：⚪ 未运行 (2026-03-15) - 最新的严格引脚运行使 pyCircuit 夜间门禁用 (`RUN_PYC_NIGHTLY_GATES=0`)。

- [ ] ID：PYC-007 保持 API 进化版本化并向后兼容，除非声明重大改进。
  完成意味着：没有未版本化的破坏性 API 更改绕过接口合约门。