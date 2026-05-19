# 代码密度和动态指令减少（Linux 内核驱动）

本文将 Linux 内核静态/动态指令统计数据转化为 灵犀指令集 的具体优化路线图。

## 数据源（可重现）

- 静态（vmlinux objdump、块感知模式）：
  - `workloads/generated/linux/build-linx-fixed/static_stats.md`
  - `workloads/generated/linux/build-linx-fixed/static_stats.json`
- 动态（QEMU 启动示例，30 秒直方图）：
  - `workloads/generated/linux/build-linx-fixed/dynamic_stats.md`
  - `workloads/generated/qemu/linux/build-linx-fixed/boot_30s.dyn_insn_hist.json`

## 当前内核快照的主要观察结果

- 指令长度混合已经以 16b/32b 为主，因此最大的胜利来自于删除整个指令（动态计数），而不仅仅是缩小编码。
- 灵犀 块结构 在反汇编中可见：`*.BSTART*` 很频繁，块大小很小（许多 2-5 个指令块）。
- 两个指令块很常见；最常见的形状包括：
  - `C.BSTART ; c.setc.eq`（大）和`C.BSTART ; c.setc.ne`
  - `C.BSTART ; <small op>`（例如 `c.movr`、`c.movi`、`sdi`，...）
- 热门“扩展/屏蔽搅动”显示为：
  - 显式 `sext.w` 模式（通常具体化为 `addw src, zero`，然后压缩为 `c.sext.w`）
  - 明确的 `zext.w` 模式（通常是 `andiw` 或移位对）
- 存在与 PC 相关的符号访问 (`*.PCR`)，但在许多情况下，代码生成会退回到地址实现序列，从而降低密度。

## 块感知模式计数（工具合约）

统计模式分析必须尊重块边界：

- `BSTART` 开始一个块（例如 `C.BSTART`、`HL.BSTART.STD`、`BSTART.*`）。
- `BSTOP`/`BSTACK`（如果存在）终止块。
- N-gram 模式不得跨块。实现：`tools/analysis/objdump_stats.py` 在块边界重置其 n 元语法窗口，并另外报告：

- 块长度直方图
- 顶部两个指令块形状

## 1) “BEQ/HL.BEQ”融合别名（不需要新的 CBR ISA）

约束：灵犀 块编码将 `BSTART(..., branch_offset)` 放置在 `SETC.*` 比较之前，因此经典的比较+分支融合指令 (CBR) 很尴尬。

相反，为常见的两指令条件块定义融合*别名*：

- `BEQ` = `C.BSTART COND,<target>` + `C.SETC.EQ <lhs>,<rhs>`
- `BNE` = `C.BSTART COND,<target>` + `C.SETC.NE <lhs>,<rhs>`
- `HL.BEQ`/`HL.BNE` 类似，当目标超出压缩范围（或强制更长的形式）时。

这有帮助的地方：

- 它使这种非常常见的形状变得明确，使编译器和汇编器能够将其视为单个语义单元。
- 它启用有针对性的窥视孔：仅当块恰好有两条指令时才发出融合别名。

所需的工具链工作：

- 汇编器：接受 `beq/bne` 作为伪，以正确的顺序扩展为 `bstart.cond + setc.*`。
- 反汇编器：可选择将两个指令块重新糖化回 `beq/bne` 以提高可读性。
- LLVM Blockify：当块的整个 块体 恰好是 `{BSTART.COND, SETC.EQ/NE}` 时，在 MIR 级别表示中发出融合别名，以便以后的传递可以对其进行推理。

## 2) 生产者使用 `SrcRType` 进行扩展 (`.sw` / `.uw`)

目标：通过标记消费者来删除显式的 `sext.w` / `zext.w` 指令。

许多 32b/48b 形式的 ISA 编码中已经存在的机制：- `SrcRType` 是一个 2 位字段：
  - `0`：`.sw`（符号扩展低32位）
  - `1`：`.uw`（零扩展低32位）
  - `2`：`.neg/.not`（现有使用）
  - `3`：无

编码建议（具体、不冲突）：

1. 保持压缩的 `C.SETC.*` 原样（没有可用的 `SrcRType` 位）。
2. 当删除指令时，优先从 `{c.sext.w + C.SETC.*}` (2x16b) 到 `{SETC.* with SrcRType}` (1x32b) 的**提升**：
   - 大小保持不变，动态指令数下降。
3. 当 `SrcRType` 可用时，将相同的策略扩展到 `CMP.*`：
   - 将本地 `sext.w`/`zext.w` 生产者折叠到 `cmp.* <lhs>, <rhs.{sw|uw}>`
4. 对于额外的 ALU 操作（未来的工作），不要尝试将 `.sw/.uw` 改造为 16b 压缩编码；更喜欢：
   - 未使用编码空间中的 32b“typed-srcR”变体，或者
   - 当 32b 空间紧张时，带有 `SrcRType` 的 HL.* 长格式。

所需的编译工作：

- 为 `.sw` 添加不同的 MI 操作数标志（除了 `.uw` 之外）。
- 窥视孔：
  - 折叠本地 `sext.w` 生产者将 `SETC/CMP` 喂入 `SrcRType=.sw`
  - 折叠本地 `zext.w` 生产者将 `SETC/CMP` 喂入 `SrcRType=.uw`
- 启发式：
  - 当替换（删除）一条或多条指令时，允许使用 `SrcRType` 选择 32b SETC/CMP。

## 3) PC 相关代码生成必须首选 `*.PCR`（完全加载/存储 PC 相关）

政策：

- 全局/常量池加载/存储应优先选择 `LB/LH/LW/LD.PCR` 和 `SB/SH/SW/SD.PCR`。
- 超出范围应通过放宽到 `HL.*.PCR` 来处理（而不是通过回退到通用地址实现）。LLVM降低策略：

- 保持 `GlobalAddress` 降低为 PC 相关（页面+低）仅作为*内部*表示。
- 在 DAG-to-DAG isel 中，积极折叠：
  - `addr = ADDI(ADDTPC(sym), sym) [+ const]`
  - `load/store [addr]`
  - 转换为 `*.PCR` 形式。
- 使折叠对于等效（但不是指针相同）符号节点具有鲁棒性。

## 4) 积极使用现有的 Bit-Manip + CONCAT

已在 ISA 中：

- `BXU` / `BXS`：位域提取无符号/有符号
- `BCNT`：popcount
- `CONCAT`：通过连接 `(srcL,srcR)` 然后移位来启用桶移位样式模式。

所需的 LLVM 工作：

- TableGen / DAG 结合：
  - `sll; srl/sra` -> `BXU/BXS`（已在 Blockify 中作为窥视孔出现；确保它在更多形状上触发）
  - `popcount` -> `BCNT`
  - `rotl/rotr` -> `CONCAT + shift` 序列（或专用模式，如果存在）

## 5) 模板块：`MCOPY` / `MSET`（库+加速器路径）

已在 ISA 中：

- `MCOPY` 模板块 适用于 `memcpy/memmove`
- `MSET` 模板块 适用于 `memset`

路线图：

1. libc 实现了映射到这些模板的手写入口点以实现常见的大小/对齐范围。
2. LLVM 识别内置模式并根据大小阈值选择模板（或调用 libc 存根）。
3. 稍后：确定其他内核热点区域并定义更多 模板块，以便 CPU 可以卸载到 ASIC 组件。

## 建议的下一步测量- 每次编译器更改后重新运行内核静态+动态统计信息（相同的构建目录，相同的 QEMU 窗口）：
  - 跟踪 `C.SETC.*`、`C.SEXT.W`、`ANDIW`、`HL.LUI`、`*.PCR` 频率。
- 将动态“顶级 PC”添加到 QEMU 插件（PC->计数）以将热点本地化为函数/符号。
- 添加“双指令块候选报告”，具体计数：
  - `C.BSTART ; c.setc.eq/ne` 和分支目标可达性类别。