# 启动进度（v0.58.1）

最后更新：2026-08-17

## 当前架构基线

- `isa/v0.58/linxisa-v0.58.json` 是规范 ISA catalog。
- `isa/v0.58/pto-spec.lock.json` 固定已发布的 PTO 公共子集。
- 语义执行单元只有 `VEC`、`TLSU`、`CUBE`、`SFU`；TEPL 只保留为不变的编码载体，不是执行单元。
- LLVM、QEMU、Linux gitlink 已更新到合入后的 v0.58.1 兼容提交。
- `tools/Linx-TileOP-API` 是当前 Tile API 组件。
- SuperNPU 源码位于 `workloads/pto_kernels/benchmarks/supernpu`；独立 SuperNPUBench gitlink 已删除。

## 证据策略

只有绑定同一精确提交的 v0.58.1 结果可以作为当前证据。历史 v0.57 报告和旧 AVS Tile/PTO parity 套件已归档，不能把通过状态转移到 v0.58.1。等待中、跳过、缺少工具或提交不一致都不算通过。

## 当前签入状态

| 表面 | 状态 | 证据 |
| --- | --- | --- |
| ISA catalog 与 PTO lock | 已发布 | v0.58.1 catalog 投影、manifest、PTO lock |
| 组件拓扑 | 必须检查 | `python3 tools/ci/check_component_lock.py --root .` |
| Linx-TileOP-API | 必须检查 | `make -C tools/Linx-TileOP-API check` |
| 嵌套 SuperNPU 源码契约 | 必须检查 | `python3 workloads/pto_kernels/scripts/check_supernpu_v058.py` |
| QEMU 解码清单 | L1 完成 | 731/731 mnemonic、765/765 form；L2/L3 仍属于独立运行时证据层级 |
| AVS Tile/PTO 运行时 | 已验证 | 精确合入的 QEMU 已通过原生 Tile 测试、严格 system AVS 和完整 AVS 套件 |
| 跨模型发布闭包 | 已验证 | 七个有序 release-strict 用例在同一精确 compiler/QEMU/model manifest 上通过；见 `docs/bringup/gates/model_diff_release-strict.json` |
| 更广的 nightly 与 benchmark 闭包 | 未关闭 | Nightly workload 广度与 release-strict 结果内存证明分开跟踪 |

## 规范命令

```bash
bash tools/ci/check_repo_layout.sh
python3 tools/ci/check_component_lock.py --root .
python3 tools/isa/build_golden.py --profile v0.58 --check
python3 tools/isa/validate_spec.py --profile v0.58
python3 tools/isa/check_pto_v058_manifest.py --root .
python3 tools/isa/check_canonical_v058.py --root .
python3 tools/isa/check_agent_navigation.py --root .
make -C tools/Linx-TileOP-API check
python3 workloads/pto_kernels/scripts/check_supernpu_v058.py
python3 tools/bringup/run_model_diff_suite.py --root . --suite avs/model/linx_model_diff_suite.yaml --profile release-strict --trace-schema-version 1.0 --report-out docs/bringup/gates/model_diff_summary.json
python3 docs/check_documentation.py --root .
```

生成的 gate 页面只是视图；组件锁、v0.58 catalog、AVS matrix/status 和精确运行 manifest 才是机器可读的权威来源。
