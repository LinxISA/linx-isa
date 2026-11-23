# FSUB

## 说明

从左源中减去右源，将结果写入目的寄存器。

## 汇编语法

```asm
fsub.{T} SrcL, SrcR, ->{t, u, Rd}
```

## 数据类型

SrcType 为 0 时读取 FP64，为 1 时读取低 32 位 FP32（载体高位补零）。编码 2 和 3 保留，执行时在读取源寄存器之前触发非法指令异常。

## 编码格式

![FSUB](../../../figs/bitfield/svg/Instruction_32bit/FSUB.svg)

## 执行方式

把本次数值运算产生的 NV、DZ、OF、UF、NX 标志按位并入已有状态。

## 示例

从 2 减去 3，结果为 −1。
