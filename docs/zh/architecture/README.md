# 架构文档

面向架构的文档位于 `docs/architecture/` 下。

## 规范合约页面

- v0.57 规范页面：
  - `docs/architecture/v0.57-architecture-contract.md`
  - `docs/architecture/v0.57-encoding-decisions.md`
  - `docs/architecture/v0.57-hardening-policy.md`
  - `docs/architecture/v0.57-simt-compiler-contract.md`
  - `docs/architecture/v0.57-simt-compiler-contract-plan.md`（规划页面；本身不是规范的）
  - `docs/architecture/v0.57-workload-engine-model.md`
  - `docs/architecture/v0.57-rendering-kernel-authoring.md`
  - `docs/architecture/v0.57-rendering-pto-contract.md`
  - `docs/architecture/v0.57-rendering-command-contract.md`
- 发布的灵犀Core镜像：
  - `docs/architecture/linxcore/overview.md`
  - `docs/architecture/linxcore/microarchitecture.md`
  - `docs/architecture/linxcore/interfaces.md`
  - `docs/architecture/linxcore/verification-matrix.md`
  - `docs/architecture/linxcore/module-catalog.md`
  - `docs/architecture/linxcore/pipeline-stage-catalog.md`
  - `docs/architecture/linxcore/ifu.md`
- 规范的 灵犀Core 创作源：
  - `rtl/LinxCore/docs/architecture/overview.md`
  - `rtl/LinxCore/docs/architecture/microarchitecture.md`
  - `rtl/LinxCore/docs/architecture/interfaces.md`
  - `rtl/LinxCore/docs/architecture/verification-matrix.md`
  - `rtl/LinxCore/docs/architecture/module-catalog.md`
  - `rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md`
  - `rtl/LinxCore/docs/architecture/ifu.md`

## ISA 手册

- `docs/architecture/isa-manual/`
  - AsciiDoc ISA 手册源和生成的 PDF。

## 出版双语手册面

已发布的文档站点现在具有比 AsciiDoc 更广泛的手册层次结构
仅手册：

- 在 `docs/background/`、`docs/compiler/` 下导入 ISA/出版物页面，
  和扩展的 `docs/isa/` 树，
- `docs/zh/`下的中文镜像，具有路径奇偶校验，
- 现有生成的`docs/isa/groups/`和`docs/isa/instructions/`
  保留为附录/参考而不是主要手册主页。

规范规则没有改变：影响架构的行为仍然存在
由英语 v0.57 合同页面和英语 AsciiDoc 手册拥有。
导入/手动层次结构页面是主要发布的叙述表面，
但它们必须与这些规范来源保持同步。

## 治理说明- 灵犀Arch 页面是启动和门的规范架构合约。
- 灵犀核心合约编​​写位于`rtl/LinxCore/docs/architecture/`；的
  超级项目`docs/architecture/linxcore/`页面生成发布
  镜子。
- 子模块中特定于实现的深入研究必须链接回这些
  合同页。
- v0.57 是唯一活动配置；其源文件不得恢复已退休兼容拼写或归档原始片段。
- 任何影响架构的更改都必须首先更新 灵犀Arch，然后再实施。
- 规范之前的草稿笔记和研究笔记仅保留用于历史记录，不得用作实时合约。
- 当规划页面定义下一次合同冻结的分阶段路径时，它们可以与规范页面并存；它们必须明确说明它们是否规范。
