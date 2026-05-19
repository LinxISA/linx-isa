# 灵犀指令集文档站点

<div class="isa-hero">

## 发布形态

本站现在采用 当前统一维护的手册层级作为**主要公开文档结构**：

- 英文主站位于 `/`
- 中文镜像位于 `/zh/`
- 两个语言版本共享同一套 Material 主题、导航层级与语言映射

### 当前定位

| | |
|---|---|
| **主要公开结构** | patch 导入后的手册层级 |
| **规范性英文来源** | [v0.56 合同页与 AsciiDoc 手册](../architecture/README.md) |
| **机器生成附录** | [ISA 附录参考](isa/index.md) |
| **中英文切换** | 页眉语言切换器 + 路径对齐镜像 |

</div>

---

## 入口导航

<div class="quick-links">

[:fontawesome-solid-circle-info: **设计背景**](background/index.md) {.quick-link-card}
: 为什么需要灵犀指令集、什么是块指令，以及这套架构与传统 CPU/GPU ISA 的差异。

[:fontawesome-solid-diagram-project: **总体架构**](isa/arch/bisa.md) {.quick-link-card}
: 块结构、执行模型、程序序、跳转方式、访问控制环与异常处理。

[:fontawesome-solid-server: **架构状态**](isa/register/common/intro.md) {.quick-link-card}
: GGPR、SSR、BPC、Tile 状态以及两层执行状态模型。

[:fontawesome-solid-table-cells-large: **数据类型**](isa/datatype/intro.md) {.quick-link-card}
: 浮点、整数、微缩放与低精度格式体系。

[:fontawesome-solid-microchip: **指令集总览**](isa/instset/baseInstrs.md) {.quick-link-card}
: 基础、压缩、标准、半长、超长、向量、张量与模板指令族。

[:fontawesome-solid-book-open: **编程手册**](compiler/manuals.md) {.quick-link-card}
: 异构 host/device 工作流、kernel offload 模式与工具链使用方式。

[:fontawesome-solid-book: **规范性合同页**](architecture/v0.56-architecture-contract.md) {.quick-link-card}
: v0.56 合同页与英文 AsciiDoc 手册仍是架构可见行为的规范性来源。

[:fontawesome-solid-list: **ISA 附录参考**](isa/index.md) {.quick-link-card}
: 现有机器生成附录仍然保留，用于按字母、分组、编码形式做精确查询。

</div>

---

## 阅读方式

1. 首先阅读 `background/`、`compiler/` 与扩展后的 `isa/` 手册层级，理解最新公开结构。
2. 对于规范性英文合同，请回到 [architecture/README.md](architecture/README.md) 与
   [AsciiDoc ISA 手册](architecture/isa-manual/README.md)。
3. 对于精确的按指令/分组查阅，请使用 [ISA 附录参考](isa/index.md)。

---

## 关键文档面

| 文档面 | 用途 |
|---|---|
| [background/index.md](background/index.md) | 高层背景与定位 |
| [isa/arch/bisa.md](isa/arch/bisa.md) | 导入后的主要架构叙事 |
| [isa/register/common/intro.md](isa/register/common/intro.md) | 寄存器与状态总览 |
| [isa/datatype/intro.md](isa/datatype/intro.md) | 数据格式总览 |
| [compiler/manuals.md](compiler/manuals.md) | 编程/工具链指导 |
| [architecture/v0.56-architecture-contract.md](architecture/v0.56-architecture-contract.md) | 规范性 v0.56 合同 |
| [architecture/isa-manual/README.md](architecture/isa-manual/README.md) | 规范性英文手册源 |
| [isa/index.md](isa/index.md) | 机器生成附录参考 |

> 中文首页把“公开手册层级”和“机器生成附录”明确分开。附录并未移除，而是从默认首页角色调整为精确检索角色。
