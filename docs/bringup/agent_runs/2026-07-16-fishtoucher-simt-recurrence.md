# 乱序摸鱼：SIMT recurrence 闭环报告

日期：2026-07-16
状态：当前子循环通过；软件总循环未完成

## 管家结论

LLVM generic loop-carried recurrence 不能被拆成互相独立的 grouped lanes。本轮将其固定为 lane-1 scalar replay，并强制使用 `MSEQ`；显式 grouped 请求以稳定 reason 拒绝。TSVC `s317` 的四模式 checksum 已恢复一致，全量 AUTO 运行不再在 batch 5 崩溃。

本轮没有宣称 TSVC 语义全部闭环。全量 OFF/AUTO 比对仍有 18/151 个 checksum 不一致，已进入下一轮诊断清单。

## 版本锁定

- superproject 起点：`c858ba6872a6767b3b11a4b5a1808ee5f264262d`
- LLVM：`ff6e0421e482a591072e2ad1fdd87901e3d4229a`
- QEMU：`2856230890045899f074c18bcb2c2e37bbd09a0c`
- QEMU binary SHA256：`eabe8770ddbd798f286a1a25d346a1b9e48302e5cb566c8aff75e7a06ffdd78e`
- Linux：`1d79efccf6b41bc675342e1b283b5ffd55f474a4`
- LinxCore：`09d4292c49f9c0e022dfb06fd9e2874cbfd6d89f`
- linx-skills：`c8147f9455de3937e7f48263fec85e56c009fa6a`

## Agent 上报

| name-role | req | resp |
| --- | --- | --- |
| Hennessy-LLVM_DESIGN | 定位 `s317` AUTO 崩溃根因，只读提出最小安全契约 | generic recurrence 的 grouped lowering 破坏依赖顺序；建议 scalar replay |
| Hejlsberg-LLVM_SENIOR_CODER | 仅修改 SIMT auto-vectorizer 与定向测试 | 实现 lane-1/MSEQ、grouped 稳定拒绝与 token def-use 测试 |
| Dijkstra-LLVM_VERIFIER | 独立审查实现、模式选择、既有 reduction 回归 | PASS；补充发现并推动修复 parallel hint 仍选 MPAR 的问题 |
| Steward-INTEGRATION | 复核、重建、运行 runtime/coverage gate、提交与 repin | 当前子循环 PASS；18 项语义差异转下一轮 |

## 验证证据

### LLVM 定向门禁

- AUTO recurrence：`lane_count=1`、`group_count=160`、`selected_mode=mseq`、`header_kind=mseq`。
- explicit grouped：拒绝 reason 为 `grouped_layout_unsupported_recurrence`。
- MPAR-safe 加 parallel hint：仍强制 `MSEQ`。
- 既有 supported reduction：保留 32x2 grouped lowering。
- 三条 `llc | FileCheck` 路径与 `git diff --check` 通过。
- 构建配置为 `LLVM_INCLUDE_TESTS=OFF`，因此未运行完整 LLVM lit suite；使用测试文件三条 RUN 等价命令执行。

### TSVC/QEMU

- `s317` OFF/MSEQ/MPAR/AUTO：均为 `0x3e4d1580`，四条 stderr 均为空。
- AUTO batched：8/8 batches，151/151 QEMU 执行，151/151 strict vectorized，aggregate stderr 为空。
- OFF batched：8/8 batches，151/151 QEMU 执行，aggregate stderr 为空。
- 产物：`workloads/generated/fishtoucher-tsvc-ff6e042-20260716-r2/`（本地生成，不作为源码提交）。

### Compile coverage

- linx64：711/711 ISA mnemonics，747/747 instruction definitions audited，743 assembled、4 skipped。
- linx32：711/711 ISA mnemonics，747/747 instruction definitions audited，743 assembled、4 skipped。
- call/ret templates 与负向编码检查通过。

## 下一轮语义清单

OFF/AUTO checksum 不一致共 18 项：

`s1161`, `s123`, `s124`, `s126`, `s1279`, `s278`, `s279`, `s3113`, `s318`, `s341`, `s343`, `s4115`, `s4116`, `s442`, `s443`, `s451`, `vdotr`, `vsumr`。

下一轮先按共同 lowering 模式分类，再一次修复一个根因族；每个补丁必须同时具备单 kernel 四模式 parity、相关族回归和全量 OFF/AUTO 对比。

## 外部阻塞

- Linux issue #24 仍为 OPEN：缺少 source-complete、可复现的 kernel 基线，Linux/SPEC train 暂不能作为可信绿灯。
- ISA/QEMU issue #141 仍为 OPEN：vector-memory C/L 与 halfword alignment 语义尚待统一。

`skill-evolve: update linx-compiler (新增 generic recurrence 的可复用 lowering 与验证契约)`
