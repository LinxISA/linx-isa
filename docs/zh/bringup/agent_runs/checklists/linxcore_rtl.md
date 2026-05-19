# 灵犀Core RTL 清单

- [ ] ID：LC-001 通过阶段/连接棉绒门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_stage_connectivity.sh`
  完成意味着：阶段命名、无存根 lint 和连接检查通过。
  状态：❌失败 (2026-03-15) - 最新的引脚通道运行报告减少的测试平台阶段列表与预期的完整管道目录之间存在 `tb kTraceStageNames` 不匹配（日志：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxcore_stage_connectivity.log`）。

- [x] ID：LC-002 通过操作码奇偶校验门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_opcode_parity.sh`
  完成意味着：解码/操作码元数据奇偶校验通过。
  状态： ✅ PASS (2026-03-15) - `ZXTERMEN45QXZCore::opcode parity` 在最新的 pin-lane 报告 `2026-03-15-r2-pin` 中为绿色。

- [ ] ID：LC-003 通过跑步者礼宾门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_runner_protocol.sh`
  完成意味着：协议握手和不匹配失败路径通过。
  状态：❌失败 (2026-03-15) - 最新的 pin-lane 运行立即失败，并显示 `error: fallback benchmark memh not found`（日志：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxcore_runner_protocol.log`）。

- [ ] ID：LC-004 传递跟踪模式和内存烟门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_trace_schema_and_mem.sh`
  完成意味着：提交跟踪模式检查通过并且观察到内存事件覆盖率。
  状态：❌失败 (2026-03-15) - 最新的 pin-lane 运行立即失败，并显示 `error: fallback benchmark memh not found`（日志：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxcore_trace_mem_smoke.log`）。

- [ ] ID：LC-005 通过 cosim 防烟门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_cosim_smoke.sh`
  完成意味着：QEMU↔灵犀Core 烟雾 co-sim 通过且快速失败行为完好无损。
  状态：❌失败 (2026-03-15) - 生成的 灵犀Core 更新脚本中止，因为固定树中缺少 `rtl/ZXTERMEN45QXZCore/tools/lib/workspace_paths.sh`（日志：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxcore_cosim_smoke.log`）。- [ ] ID：LC-006 通过 CoreMark 交叉检查夜间门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_coremark_crosscheck_1000.sh`
  完成意味着：1000 次提交交叉检查零不匹配。
  状态：⚪ 未运行 (2026-03-15) - 最新的严格 pin 运行使夜间 灵犀Core 门禁用 (`RUN_LINXCORE_NIGHTLY_GATES=0`)。

- [ ] ID：LC-007 通过 CBSTOP 通货膨胀守卫夜间门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_cbstop_inflation_guard.sh`
  完成意味着：第一个窗口直方图防护报告没有通货膨胀回归。
  状态：⚪ 未运行 (2026-03-15) - 最新的严格 pin 运行使夜间 灵犀Core 门禁用 (`RUN_LINXCORE_NIGHTLY_GATES=0`)。

- [ ] ID：LC-008 保持 super标量 退出顺序和 ROB 不变量稳定。
  完成意味着：ROB/测试平台门在两条通道中均保持绿色。

- [ ] ID：LC-009 在重播/重定向路径下保持块/刷新/核弹语义精确。
  完成意味着：所需的分支/块/内存门通过，没有豁免。