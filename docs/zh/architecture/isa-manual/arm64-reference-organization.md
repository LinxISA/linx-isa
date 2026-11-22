# Arm A64 指令参考站的组织结构与 LinxISA 手册目录

## 从分类进入单条指令

参考站把基础指令、SIMD 与浮点、SVE、SME 分别做成独立的助记符索引。首页本身就是基础指令索引。读者进入一个分类后，按字母顺序查找助记符，每项旁边有一句用途说明。相同助记符可以按形式拆开，例如 ADD 的立即数、移位寄存器和扩展寄存器形式各有入口。别名条目指出对应的基础指令。[基础指令索引](https://www.scs.stanford.edu/~zyedidia/arm64/index.html) · [SIMD 与浮点索引](https://www.scs.stanford.edu/~zyedidia/arm64/fpsimdindex.html)

## 单条指令页的阅读顺序

以 ADD 的立即数形式为例，标题先说明是哪种 ADD，正文开头解释源操作数、加法和写回目标。接着给出位图，在同一编码下面列出 32 位和 64 位变体的选择条件与汇编写法。再往下是汇编符号、别名条件、执行伪代码和适用的操作说明。想写汇编的读者在前半页就能找到答案；写译码器的读者可以接着查字段和执行细节。[ADD 立即数形式](https://www.scs.stanford.edu/~zyedidia/arm64/add_addsub_imm.html)

## 从机器字反查指令

编码索引提供另一条路径。顶层位图标出分组字段，表格用字段取值把读者引到下一层编码组，直至具体形式；保留和未分配空间也在表中标出。共享伪代码另有入口，各分类页和指令页都保留同一排导航。[编码索引](https://www.scs.stanford.edu/~zyedidia/arm64/encodingindex.html) · [共享伪代码](https://www.scs.stanford.edu/~zyedidia/arm64/shared_pseudocode.html)

## LinxISA 0.59.1 的分类页

Linx 手册采用“指令分类 → 该类助记符索引 → 指令页”的阅读路径。分类依据是签名标签 `v0.59.1` 中每个编码形式的 `uop_big_kind`。下面的“目录助记符”按 `mnemonic` 去重；同名指令的不同编码形式分别计数。LSU 是浏览时使用的访存分类名，在本版目录中对应 `AGU`。原子访存 `AMO` 单列。Tile 操作另按实际操作目录查找，其中 `TLSU` 是 Tile 访存引擎。[0.59.1 指令目录](https://github.com/LinxISA/linx-isa/blob/v0.59.1/isa/v0.59/linxisa-v0.59.json)

| 浏览分类 | 目录字段 | 目录助记符 | 编码形式 |
| --- | --- | ---: | ---: |
| ALU · 整数运算 | ALU | 107 | 107 |
| BBD · 块边界 | BBD | 15 | 27 |
| BRU · 分支与比较 | BRU | 58 | 58 |
| LSU · 加载、存储与预取 | AGU | 183 | 714 |
| AMO · 原子访存 | AMO | 61 | 235 |
| CMD · 块命令 | CMD | 82 | 110 |
| FSU · 标量浮点 | FSU | 30 | 30 |
| SYS · 系统 | SYS | 36 | 36 |
| VEC · 向量指令 | VEC | 182 | 182 |
| 合计 | | **754** | **1,499** |

以 `C.MOVR` 为例，读者从 ALU 索引进入后，首先看到灵犀中文站原有的“说明、汇编语法、汇编符号、编码格式、执行方式、汇编索引模式、备注”。原页的 T 队列、U 队列和全局寄存器示例都应能在页内阅读。指令图与 0.59.1 位位置、字段及固定位一致时，直接使用原 SVG。版本存在差异时，在相关内容旁标出本版写法，当前编码以发布标签为准。ASL 和 Sail 放在核对资料中。没有对应中文站文章的形式应交代资料来源。[中文站 C.MOVR](https://linxisa.github.io/isa/inst/misa_c/C.MOVR/)

## 芯片开发时如何核对

| 查阅问题 | 其他手册的做法 | LinxISA 的入口 |
| --- | --- | --- |
| 实现一条指令前，要知道哪些状态可见？ | 龙芯基础架构手册先介绍通用寄存器、PC、特权级和异常，再列整数指令。 | 从架构状态查 BPC、TPC、队列与 Tile 寄存器，再到指令页核对字段。 |
| 编码图中的位置如何决定操作数？ | RISC-V 在 RV32I 基本指令格式中集中说明寄存器和立即数字段，并在具体指令处说明它们的用法。 | 每个形式保留分段位图；遇到跨段字段，可直接查指令位到字段值位的映射。 |
| 同名指令在哪些条件下可用？ | AMD64 通用指令卷把适用模式、标志位和异常列在指令条目中；例如 AAA 的条目单列 64 位模式的无效操作码异常。 | LinxISA 原页保留汇编、约束和异常。本版与原页有差异时，在原文之前标出相应条件。 |

这些比较用于选择阅读顺序。寄存器和异常的实际取值仍取自各自架构。[龙芯基础架构手册第 2 章](https://loongson.github.io/LoongArch-Documentation/LoongArch-Vol1-EN.html) · [RISC-V 非特权规范 RV32I](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html) · [AMD64 程序员手册第 3 卷](https://www.amd.com/content/dam/amd/en/documents/processor-tech-docs/programmer-references/24594.pdf)
