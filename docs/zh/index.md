---
title: LinxISA
---

!!! warning "非规范翻译"
    本站是英文规范文档的辅助中文翻译。发生差异时，以英文文档和
    `isa/v0.56/linxisa-v0.56.json` 为准。指令助记符、字段名、路径和代码标识符保持原文。

<section class="linx-home-hero" markdown="1">
<div class="linx-home-hero__copy" markdown="1">

<p class="linx-home-eyebrow">灵犀指令集架构</p>

# 一套面向块执行的指令集架构

LinxISA 把程序组织成一组组块指令。每个块同时说明控制流、执行属性和数据并行关系，让软件能清楚表达意图，也让硬件更容易调度前端、寄存器队列、向量/Tile 计算和异常恢复。

<div class="linx-home-actions" markdown="1">
[开始阅读](background/index.md){ .md-button .md-button--primary }
[查看指令编码](isa/instset/baseInstrs.md){ .md-button }
</div>

</div>

<div class="linx-home-hero__visual" markdown="1">
<img class="linx-home-logo" src="assets/linxisa-logo.svg" alt="LinxISA logo">
<div class="linx-home-wordmark">LinxISA</div>
<div class="linx-home-submark">Block-structured Instruction Set Architecture</div>
</div>
</section>

<section class="linx-home-strip" markdown="1">
<div markdown="1">
**v0.56.5**
: 当前公开规范版本
</div>
<div markdown="1">
**747**
: 指令形式
</div>
<div markdown="1">
**16/32/48/64-bit**
: 压缩、基础、半长与超长编码
</div>
<div markdown="1">
**Block ISA**
: 控制流与执行状态以块为单位建模
</div>
</section>

## 先读哪一部分

<div class="linx-home-grid" markdown="1">

<div class="linx-home-card" markdown="1">
### 架构背景
[设计背景](background/index.md) 解释 LinxISA 为什么选择块结构，以及它如何把控制流、数据流和执行属性放进同一套 ISA 合同。
</div>

<div class="linx-home-card" markdown="1">
### 指令语义
[指令集总览](isa/instset/baseInstrs.md) 按基础、压缩、标准、增强、超长、向量和模板指令族组织，每个指令页都展示对应编码。
</div>

<div class="linx-home-card" markdown="1">
### 架构状态
[寄存器与状态](isa/register/common/intro.md) 汇总 GGPR、SGPR、VGPR、BARG、BPC、TPC 与系统寄存器，帮助读者理解两层执行状态。
</div>

<div class="linx-home-card" markdown="1">
### 工具链与编程
[编程手册](compiler/manuals.md) 覆盖汇编语法、调用约定、内联汇编、kernel offload 和工具链使用。
</div>

</div>

## 编码一眼可查

<section class="linx-home-encoding" markdown="1">
<div markdown="1">

每个指令页的“编码格式”区域都使用从 WaveDrom/bit-field JSON 生成的 SVG。图中高位在左、低位在右，字段名和常量位直接对应手册定义。

[浏览基础指令](isa/instset/baseInstrs.md){ .md-button }
[浏览向量指令](isa/blockIntro/vecinstrs/instIntro.md){ .md-button }

</div>
<figure markdown="1">
![ADD instruction encoding](figs/bitfield/svg/Instruction_32bit/ADD.svg)
<figcaption>ADD 的 32-bit 编码示例。</figcaption>
</figure>
</section>

## 规范性入口

| 文档面 | 用途 |
|---|---|
| [总体架构](isa/arch/bisa.md) | 块指令、跳转、执行模型、程序序和异常处理 |
| [v0.56 架构合同](architecture/v0.56-architecture-contract.md) | 架构可见行为的规范性合同 |
| [ISA 附录参考](isa/index.md) | 机器生成的精确索引和附录页面 |
| [Call/Ret 合同](reference/linxisa-call-ret-contract.md) | 跨栈调用、返回和保存恢复规则 |
| [Bring-up 指南](bringup/GETTING_STARTED.md) | QEMU、LLVM、AVS 和运行环境入口 |
