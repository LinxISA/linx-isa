# 灵犀 ISA 页面结构

<div class="isa-hero">

## 主手册层级 + 附录参考

当前 ISA 页面分成两层：

- **主手册层级**：当前公开手册结构
- **机器生成附录**：保留现有 v0.56 生成型参考页

前者承担主要公开叙事结构，后者承担精确的助记符、分组、编码与逐条指令检索。

</div>

---

## 主手册层级

<div class="quick-links">

[:fontawesome-solid-sitemap: **架构叙事**](arch/bisa.md) {.quick-link-card}
: 块定义、执行模型、跳转方式、程序序、访问控制环与指令集约束。

[:fontawesome-solid-server: **架构状态**](register/common/intro.md) {.quick-link-card}
: GGPR、SSR、BPC、Tile 状态以及两层执行状态模型。

[:fontawesome-solid-cubes: **数据类型**](datatype/intro.md) {.quick-link-card}
: 浮点、整数、微缩放与低精度格式族。

[:fontawesome-solid-layer-group: **指令家族**](instset/baseInstrs.md) {.quick-link-card}
: 基础、压缩、标准、半长、超长、向量、张量与模板指令集。

[:fontawesome-solid-shapes: **块类型介绍**](blockIntro/std_block/intro.md) {.quick-link-card}
: 标量、向量、矩阵、访存、系统、模板与系统调用块。

[:fontawesome-solid-code: **编程手册**](../../compiler/manuals.md) {.quick-link-card}
: host/device 工作流、kernel offload 模式与工具链/运行方式。

</div>

---

## 附录参考

以下页面仍然保留为精确机器生成参考：

- [编码格式](encoding.md)
- [分组索引](groups/index.md)
- [指令 A-Z](instructions/index.md)

它们仍是精确的编码图、按助记符检索、按分组检索与生成型附录入口，只是不再承担 ISA 首页角色。

---

## 建议阅读顺序

1. 从 [../background/index.md](../background/index.md) 阅读背景与定位。
2. 阅读 [arch/bisa.md](arch/bisa.md)、[arch/execute.md](arch/execute.md) 与
   [arch/constraints.md](arch/constraints.md) 理解导入后的主架构模型。
3. 阅读 [register/common/intro.md](register/common/intro.md) 与
   [datatype/intro.md](datatype/intro.md) 理解状态与类型基础。
4. 阅读 [instset/baseInstrs.md](instset/baseInstrs.md) 与各类块介绍页理解指令家族组织方式。
5. 最后使用 [instructions/index.md](instructions/index.md) 做精确逐条查询。

---

## 附录快速入口

本页适合作为中文 ISA 总索引页；若需要逐条查阅，请直接进入
[完整字母顺序附录](instructions/index.md)。
