# SPEC CPU + 灵犀Core XCheck 流程

## 范围

本文档定义了用于 灵犀指令集/灵犀Core 验证的双通道 SPEC CPU2017 工作流程：

- A 阶段阻塞子集：`999.specrand_ir`、`505.mcf_r`、`531.deepsjeng_r`
- 每晚完整 SPECint 扩展：`spec_policy.stage_b_required`（不包括保单除外）
- 功能性交通政策：
  - A阶段：`9p` + `initramfs`
  - 每晚全套：仅限 `9p`
- XCheck 目标：前 1,000 个提交 QEMU 跟踪和 灵犀Core C++ TB 之间的奇偶校验

该流程有意分开：

- C 阶段构建通道（功能清单）
- b阶段静态图像通道（灵犀Core图像/xcheck）

## 配置文件 A：A 阶段阻塞

运行：

```bash
bash rtl/ZXTERMEN45QXZCore/tests/test_specint_stage_a_xcheck.sh
```

管道：

1. A 阶段工作台的 C 阶段构建
2.QEMU矩阵（`9p` + `initramfs`、`--input-set test`，严格）
3.b阶段静态镜像准备（`LINX_SPEC_FORCE_STATIC=1`，自动恢复原始exe）
4.套件生成（`linxcore-xcheck-suite-v1`）
5. xcheck执行（`failfast`，1K提交）

## 配置文件 B：每晚完整 SPECint（报告通道）

运行（仅报告默认值）：

```bash
SPEC_NIGHTLY_REPORT_ONLY=1 bash rtl/ZXTERMEN45QXZCore/tests/test_specint_full_xcheck_nightly.sh
```

管道：

1. B阶段政策基准的C阶段建设
2.QEMU矩阵（`9p`、`--input-set test`）
3.b阶段静态图像准备
4. 套件生成（b 阶段策略集）
5. xcheck执行（`diagnostic`、`--continue-on-fail`，仅报告）

退出行为：

- 仅报告模式：奇偶校验不匹配不会使作业失败（报告 `summary.ok=false`）
- 基础设施/工具故障仍然返回非零

## 神器合约

A 阶段和夜间包装器会发出：- QEMU 矩阵：
  - `.../qemu_matrix/qemu_matrix_summary.json`
  - `.../qemu_matrix/qemu_matrix_summary.md`
  - 使用 `stage_<stage>_summary.json` 传输子目录
- B阶段图像导出：
  - `.../phaseb_static_images/phaseb_image_manifest.json`
- xcheck 套件：
  - `.../linxcore_suite_stage_<a|b>.json`
- xcheck聚合：
  - `.../xcheck/summary.json`
  - `.../xcheck/summary.md`
- 每箱捆绑：
  - `.../xcheck/<case>/qemu_trace.jsonl`
  - `.../xcheck/<case>/dut_trace.jsonl`
  - `.../xcheck/<case>/report/crosscheck_report.json`
  - `.../xcheck/<case>/report/crosscheck_report.md`
  - `.../xcheck/<case>/report/crosscheck_mismatches.json`

## 严格回归积分

`tools/regression/strict_cross_repo.sh` 公开选择加入切换：

- `RUN_SPEC_PR_GATES=1` -> A 阶段阻塞包装器
- `RUN_SPEC_NIGHTLY_GATES=1` -> 完整的夜间包装
- `SPEC_NIGHTLY_REPORT_ONLY`（默认`1`）
- `SPEC_INPUT_SET`（默认`test`）

## 晋升标准（报告 -> 每晚阻止）

每晚升级到阻止应要求满足以下所有条件：

1. 连续 7 次夜间运行，基础设施零故障。
2. 在 7 次运行窗口中，基准平价通过率至少为 95%。
3. A 阶段工作台中没有未解决的确定性回归。