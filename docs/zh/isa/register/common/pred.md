# PRED

## 说明

**P（Predicate Mask）**寄存器是并行块Group内的lane掩码寄存器，用于控制所属Group内每个lane的执行状态是否有效。该寄存器64bit宽，因此基于本指令集的实现中要求每个Group最多包含64个lane。

该寄存器的每一位掩码与Lane一一对应，控制着对应Lane计算结果的有效性。当掩码为1时，该lane的计算结果有效；为0时则无效。

![lanemask](../../../figs/isa/arch/pred.png){ width="800" }

如上图所示，假设P寄存器的 `0~9 bit` 全为1且高位都为0，则表示当前Group内 `lane0 ~ lane9` 是有效lane，其余lane是无效的并且计算结果将被掩掉。

## 访问属性

该寄存器是可读可写的（RW）。
