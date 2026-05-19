# AVS 合约 (v0.56)

`avs/linx_avs_v1_test_matrix.yaml` 是 灵犀指令集 `v0.56` 唯一的实时公开启动合约。

## 规范文件

- 矩阵：`avs/linx_avs_v1_test_matrix.yaml`
- 状态：`avs/linx_avs_v1_test_matrix_status.json`
- 架构合约：`docs/architecture/v0.56-architecture-contract.md`

## 必需的条目元数据

规范矩阵中的每个 AVS 条目都包含：

- `state`：`active` 或 `archived`
- `profiles`：架构或子系统覆盖范围
- `must_pass_in_tier`：`pr` 和 `nightly` 等门层
- `spec_refs`：规范的 `v0.56` 规范、手册或状态参考
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

矩阵就是公共契约。历史数字合同材料已从活动导航中删除，并且不参与关闭。