# FMAX

## 说明

比较两个浮点数，将较大的值写入目的寄存器。

## 汇编语法

```asm
fmax.{T} SrcL, SrcR, ->{t, u, Rd}
```

## 数据类型

SrcType 为 0 时读取 FP64，为 1 时读取低 32 位 FP32（载体高位补零）。编码 2 和 3 保留，执行时在读取源寄存器之前触发非法指令异常。

## 编码格式

![FMAX](../../../figs/bitfield/svg/Instruction_32bit/FMAX.svg)

## 执行方式

若只有一个输入是 NaN，返回另一个数；若两个都是 NaN，返回规范的安静 NaN。遇到信号 NaN 时置 NV。

## 示例

一个输入为安静 NaN，另一个为 3，结果为 3。
