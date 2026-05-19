# 存档的 v0.3 启动计划：澄清

此页面仅保留为退役 `v0.3` 启动的存档索引
决定。对于当前规范的 `v0.56` ISA 合约来说，它并不规范。

## 实时规范来源

- `docs/architecture/v0.56-architecture-contract.md`
- `docs/architecture/isa-manual/src/linxisa-isa-manual.adoc`
- `docs/architecture/v0.56-workload-engine-model.md`
- `docs/architecture/v0.56-rendering-command-contract.md`
- `isa/v0.56/state/engine_ops.json`
- `tools/bringup/check_avs_contract.py`
- `tools/bringup/check_sail_model.py`

## 澄清升级到 Canonical v0.56

实时 `v0.56` 合约现在采用旧版本的规范形式
最初住在这里的决定：

- 块边界合法性和仅限边界的控制流目标，
- 块格式验证和 块体-fetch 故障报告，
- `TPC` 和 块体 入门术语，
- 模板重放元数据和 `BSTART.TEPL` 选择器处理，
- SIMT/向量 块体 终止、`.brg` 合法性和 RI 命名空间使用，
- 当前的 `BSTART.TEPL` 与 `BSTART.FIXP` 分离。

## 历史状况

- 已退役的旧 AVS 前一致性文件不是当前关闭的一部分。
- `v0.3` 架构合约页面不是 `v0.56` 的实时源。
- 存档的迁移笔记本仍然是唯一保留的草稿历史记录
  此切换的表面。

## 使用规则

如果本存档说明中的任何措辞与规范的 `v0.56` 文档不一致，请说明
目录或验证器，规范的 `v0.56` 表面获胜。