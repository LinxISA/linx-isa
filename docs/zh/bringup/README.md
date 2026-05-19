# 灵犀指令集 启动（公共 v0.56）

该目录跟踪 `v0.56` 架构和实现一致性，AVS 是唯一实时公开启动合约。

## 从这里开始

- 入门和工作区设置：`docs/bringup/GETTING_STARTED.md`
- 执行顺序阻止程序操作手册：`docs/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md`

## 规范合同

- 架构合约：`docs/architecture/v0.56-architecture-contract.md`
- AVS合约页面：`docs/bringup/AVS_CONTRACT.md`
- 规范 AVS 矩阵：`avs/linx_avs_v1_test_matrix.yaml`
- 合约门：`python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml`
- 关闭门：`python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier ${LINX_GATE_TIER:-pr}`

## 关键参考文献

- `docs/bringup/AVS_CONTRACT.md`
- `docs/bringup/SUPERPROJECT_BRINGUP_CHECKLIST.md`
- `docs/bringup/MATURITY_PLAN.md`
- `docs/bringup/SIMT_COMPILER_MATURITY_PLAN.md`
- `docs/bringup/SIMT_COMPILER_SUPPORTED_SUBSET.md`
- `docs/bringup/rendering_vulkan_bringup.md`
- `docs/bringup/CPP_BRINGUP_CONTRACT.md`
- `docs/bringup/PROGRESS.md`
- `docs/bringup/gates/latest.json`（规范的机器可读门报告）
- `docs/bringup/gate_registry.json`（规范配置文件/层门注册表）
- `docs/bringup/GATE_STATUS.md`（从门报告 JSON 生成）
- `docs/bringup/LINX_ASM_ABI_UNWIND_CONTEXT_CHECKLIST.md`
- `docs/bringup/CROSSSTACK_SKILLS_SUMMARY.md`
- `docs/bringup/agent_runs/manifest.yaml`（机器可读的多代理门所有权地图）
- `docs/bringup/agent_runs/waivers.yaml`（跟踪显式放弃分类账）
- `docs/bringup/agent_runs/checklists/`（具有稳定 ID 的每个域执行检查表）
- `docs/reference/linxisa-call-ret-contract.md`
- `docs/bringup/phases/`
- `docs/bringup/contracts/`

## Gate 报告中的路径变量（便携式）

`docs/bringup/gates/` 下的签入门报告使用 `${...}` 变量
而不是特定于机器的绝对路径。

树内（固定）结账的推荐默认值：

- `LINXISA_ROOT` = 仓库根
- `LLVM_ROOT` = `${LINXISA_ROOT}/compiler/llvm`
- `QEMU_ROOT` = `${LINXISA_ROOT}/emulator/qemu`
- `LINUX_ROOT` = `${LINXISA_ROOT}/kernel/linux`
- `PYCIRCUIT_ROOT` = `${LINXISA_ROOT}/tools/pyCircuit`
- `LINXCORE_ROOT` = `${LINXISA_ROOT}/rtl/ZXTERMEN45QXZCore`
- `GLIBC_ROOT` = `${LINXISA_ROOT}/lib/glibc`
- `MUSL_ROOT` = `${LINXISA_ROOT}/lib/musl`对于“外部”通道，将这些变量设置为指向您的外部克隆/构建
如果您故意将工具链保留在超级项目之外。

门状态markdown刷新命令：

`python3 tools/bringup/gate_report.py render --report docs/bringup/gates/latest.json --out-md docs/bringup/GATE_STATUS.md`

规范配置文件/层运行器：

`python3 tools/bringup/run_gates.py --profile release-strict --tier pr`

兼容性入口点：

- `bash tools/regression/run.sh`
- `bash tools/regression/strict_cross_repo.sh`

使用 `LINX_GATE_DRY_RUN=1` 与任一包装器来检查选定的门
无需运行工具链、模拟器或 Linux 引导工作的命令。

多代理严格静态检查表门：

`python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode static --manifest docs/bringup/agent_runs/manifest.yaml --waivers docs/bringup/agent_runs/waivers.yaml --checklists-root docs/bringup/agent_runs/checklists`

多智能体严格运行时关闭门（每通道/运行）：

`python3 tools/bringup/check_multi_agent_gates.py --strict-always --mode runtime --manifest docs/bringup/agent_runs/manifest.yaml --waivers docs/bringup/agent_runs/waivers.yaml --checklists-root docs/bringup/agent_runs/checklists --report docs/bringup/gates/latest.json --lane pin --run-id <run-id> --out docs/bringup/gates/logs/<run-id>/pin/multi_agent_summary.json`

发布严格的启动一致性检查：

- `python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml`
- `python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/model_diff_summary.json`
- `python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --report-out docs/bringup/gates/avs_matrix_status_audit.json`
- `python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier ${LINX_GATE_TIER:-pr}`
- `python3 tools/bringup/check_sail_model.py`
- `python3 tools/bringup/check_qemu_opcode_meta_sync.py --allowlist docs/bringup/qemu_opcode_sync_allowlist.json --report-out docs/bringup/gates/qemu_opcode_sync_latest.json --out-md docs/bringup/gates/qemu_opcode_sync_latest.md`
- `python3 tools/bringup/report_qemu_isa_coverage.py --report-out docs/bringup/gates/qemu_isa_coverage_latest.json --out-md docs/bringup/gates/qemu_isa_coverage_latest.md --require-full`（助记符+执行形式关闭）
- `python3 tools/bringup/check_linx_virt_defconfig_spec.py --report-out docs/bringup/gates/linxisa_virt_defconfig_audit.json`
- `python3 tools/bringup/check_gate_consistency.py --report docs/bringup/gates/latest.json --progress docs/bringup/PROGRESS.md --gate-status docs/bringup/GATE_STATUS.md --libc-status docs/bringup/libc_status.md --avs-matrix-audit docs/bringup/gates/avs_matrix_status_audit.json --qemu-opcode-sync docs/bringup/gates/qemu_opcode_sync_latest.json --qemu-isa-coverage docs/bringup/gates/qemu_isa_coverage_latest.json --linux-defconfig-audit docs/bringup/gates/linxisa_virt_defconfig_audit.json --require-maturity-artifacts --profile release-strict --lane-policy external+pin-required --trace-schema-version 1.0 --multi-agent-summary docs/bringup/gates/logs/<run-id>/<lane>/multi_agent_summary.json --max-age-hours 24`