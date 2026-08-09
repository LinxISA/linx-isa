# AVS 兼容性合约（v0.57）

`avs/linx_avs_v1_test_matrix.yaml` 保留为公开的 `v0.57` 兼容性矩阵。
它是硬断裂升级的回归证据，不是 LLVM、QEMU、Linux 或其他消费者已实现
`v0.58` 的规范证据。每个下游消费者升级时都必须生成新的 `v0.58` AVS
证据；历史 `v0.57` PASS 结果不得转移。

## 规范文件

- 矩阵：`avs/linx_avs_v1_test_matrix.yaml`
- 状态：`avs/linx_avs_v1_test_matrix_status.json`
- 当前架构权威：`isa/v0.58/linxisa-v0.58.json`
- 当前架构说明：`docs/zh/architecture/v0.58-architecture-contract.md`

## 必需的条目元数据

规范矩阵中的每个 AVS 条目都包含：

- `state`：`active` 或 `archived`
- `profiles`：架构或子系统覆盖范围
- `must_pass_in_tier`：`pr` 和 `nightly` 等门层
- `spec_refs`：规范的 `v0.57` 规范、手册或状态参考
- `requirement` 和 `pass_fail`：规范闭包语句

只有 `state: active` 条目参与层级关闭。

## 合约门

验证矩阵架构和引用：

```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
```

生成并验证规范的派生状态工件：

```bash
python3 tools/bringup/gen_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --source-status avs/linx_avs_v1_test_matrix_status.json --out avs/linx_avs_v1_test_matrix_status.json
python3 tools/bringup/check_avs_matrix_status.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json
```

要求所有活动条目关闭层级：

```bash
python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr
```

## 当前范围

规范的 AVS 矩阵现在涵盖：

- 标量 和 向量 ISA 合法性
- 平铺和 TEPL 行为
- Linux 启动和运行时门
- musl 和 glibc 门
- 维护工作负载运行程序
- SPEC舞台大门

该矩阵是上一配置的公开兼容性合约。它不覆盖
`isa/v0.58/linxisa-v0.58.json`，也不能在缺少新证据时关闭任何 `v0.58`
消费者升级。
