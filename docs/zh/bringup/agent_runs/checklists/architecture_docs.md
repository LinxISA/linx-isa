# 架构 / 灵犀Arch 清单

- [x] ID：ARCH-001 在 mkdocs 导航中保留 灵犀Arch 灵犀Core 合约页面并链接。
  命令：`python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict --require-mkdocs`
  完成意味着：灵犀Core 架构页面存在，mkdocs nav 包含它们，并且链接目标解析。
  状态： ✅ 通过 (2026-03-15) - `arch_mkdocs_report.json` 运行 `2026-03-15-r2-pin` 报告 `ok=true` ，其中复制的 灵犀Core 架构页面和 mkdocs 导航同步（工件：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/arch_mkdocs_report.json`）。

- [x] ID：ARCH-002 保持架构验证矩阵与所需的门名称同步。
  命令：`python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict`
  完成意味着：验证矩阵包含每个必需的 Architecture/灵犀Core/Testbench/pyCircuit/灵犀Trace 门密钥。
  状态： ✅ 通过 (2026-03-15) - `arch_contract_report.json` 运行 `2026-03-15-r2-pin` 报告 `ok=true`，没有契约矩阵漂移（工件：`docs/bringup/gates/logs/2026-03-15-r2-pin/pin/arch_contract_report.json`）。

- [ ] ID：ARCH-003 保持实时 v0.56 架构合约和 灵犀Core 合约页面交叉链接。
  完成意味着：`v0.56-architecture-contract.md` 引用 灵犀Core 页面，灵犀Core 概述引用 v0.56 范围。

- [ ] ID：ARCH-004 确保影响架构的更改在实施签核之前更新 灵犀Arch。
  完成意味着：架构门行是绿色的，并且不存在未解决的合同漂移。