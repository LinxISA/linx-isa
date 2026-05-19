# 灵犀Trace 检查表

- [ ] ID：TRACE-001 通过 灵犀Trace 合约同步 lint 门。
  命令：`python3 rtl/ZXTERMEN45QXZCore/tools/linxcoresight/lint_trace_contract_sync.py`
  完成意味着：阶段代币/发射器/linter/查看器合约同步传递。
  状态：❌失败 (2026-03-15) - 最新的引脚通道运行报告了在 灵犀Core 阶段/连接门中看到的相同 `tb kTraceStageNames` 不匹配（日志：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxtrace_contract_sync.log`）。

- [ ] ID：TRACE-002 通过 灵犀Trace 样本棉绒门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_konata_sanity.sh`
  完成意味着：示例跟踪验证架构/阶段要求。
  状态：❌ 失败 (2026-03-15) - 最新的 pin-lane 样本 lint 因 `error: fallback benchmark memh not found` 中止（日志：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/linxtrace_sample_lint.log`）。

- [x] ID：TRACE-003 通过跟踪 SemVer 兼容性门。
  命令：`python3 tools/bringup/check_trace_semver_compat.py --root . --strict`
  完成意味着：跟踪模式契约 + 工具默认值保持 SemVer 兼容。
  状态： ✅ 通过 (2026-03-15) - 最新的 pin-lane 报告记录了 `ok=true`，没有 SemVer/默认版本漂移（工件：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/trace_semver_report.json`）。

- [ ] ID：TRACE-004 通过 DFX 追踪夜间门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_konata_dfx_pipeview.sh`
  完成意味着：DFX 跟踪通道验证成功。
  状态：⚪ 未运行 (2026-03-15) - 最新的严格引脚运行使夜间跟踪门禁用 (`RUN_TRACE_NIGHTLY_GATES=0`)。

- [ ] ID：TRACE-005 通过模板追踪夜间门。
  命令：`bash rtl/ZXTERMEN45QXZCore/tests/test_konata_template_pipeview.sh`
  完成意味着：模板跟踪通道验证成功。
  状态：⚪ 未运行 (2026-03-15) - 最新的严格引脚运行使夜间跟踪门禁用 (`RUN_TRACE_NIGHTLY_GATES=0`)。

- [ ] ID：TRACE-006 通过迁移检查不断破坏跟踪更改的主要版本。
  完成意味着：在没有重大碰撞和验证证据的情况下，不会合并不兼容的跟踪更改。