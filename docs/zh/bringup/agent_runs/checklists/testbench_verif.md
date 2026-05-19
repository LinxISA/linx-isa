# 测试平台验证清单

- [ ] ID：TB-001 通过ROB记账门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_rob_bookkeeping.sh`
  完成意味着：多次提交 ROB 排序和簿记检查通过。
  状态：❌失败 (2026-03-15) - 最新的 pin-lane 运行在重新生成 灵犀Core 抵押品时中止，因为 `rtl/ZXTERMEN45QXZCore/tools/lib/workspace_paths.sh` 丢失（日志：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/testbench_rob_bookkeeping.log`）。

- [ ] ID：TB-002 通块结构pyCircuit流烟门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_block_struct_pyc_flow.sh`
  完成意味着：块结构流集成完成，没有合约漂移。
  状态：❌失败 (2026-03-15) - 在 pyCircuit 流程可以编译示例之前，最新的引脚通道运行因 `missing pycc` 中止（日志：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/testbench_block_struct_pyc.log`）。

- [ ] ID：TB-003 在夜间套房中保持重播/重定向/刷新边缘场景覆盖处于活动状态。
  完成意味着：执行扩展压力套件并在门证据中链接。

- [ ] ID：TB-004 在 super标量 危险场景中保持前进进度保证。
  完成意味着：在所需的验证运行中没有挂起/死锁回归。