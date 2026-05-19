# 存档的 v0.3 启动计划：架构清单

此页面仅保留作为退役 `v0.3` 的历史启动计划
切换。它不是规范 `v0.56` 的实时合约面。

## 实时规范来源

- `docs/architecture/v0.56-architecture-contract.md`
- `docs/architecture/v0.56-workload-engine-model.md`
- `docs/architecture/v0.56-rendering-command-contract.md`
- `docs/architecture/linxcore/overview.md`
- `docs/architecture/linxcore/microarchitecture.md`
- `isa/v0.56/`
- `tools/bringup/check_avs_contract.py`
- `tools/bringup/check_avs_profile_closure.py`

## 历史范围

已退役的 `v0.3` 检查表跟踪了以下内容的初始启动：

- 块结构执行和仅限边界控制流，
- GSTATE/BSTATE分割和块命令调度，
- 描述符验证和解耦的 块体 条目行为，
- TMA、CUBE、TEPL 和 SIMT/向量 块系列形状，
- 桥接 `.brg` 内存形式和 RI 命名空间规则，
- 早期编译器/QEMU/RTL 奇偶校验的陷阱信封和可重启性。

这些主题现在已被提升到规范的 `v0.56` 手册中，状态
目录和架构合同页面。任何剩余的 `v0.3` 措辞应为
被视为仅存档历史，而不是规范来源。

## 当前关闭政策

- AVS 是唯一实时公开的培育合同。
- 层闭合由`state + must_pass_in_tier`选择。
- 已退役的旧版 AVS 合约工件不属于当前 `v0.56` 的一部分
  关闭。

## 历史注释

该文件保留在 `docs/bringup/plan/` 中只是为了保留计划的可追溯性
旧的提出讨论。不应将其引用为当前的证据
释放严格的 `v0.56` 关闭。