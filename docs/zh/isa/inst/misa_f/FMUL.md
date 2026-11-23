# FMUL

## 说明

将两个输入相乘，将结果写入目的寄存器。

## 汇编语法

```asm
fmul.{T} SrcL, SrcR, ->{t, u, Rd}
```

## 数据类型

SrcType 为 0 时读取 FP64，为 1 时读取低 32 位 FP32（载体高位补零）。编码 2 和 3 保留，执行时在读取源寄存器之前触发非法指令异常。

## 编码格式

![FMUL](../../../figs/bitfield/svg/Instruction_32bit/FMUL.svg)

## 执行方式

把本次数值运算产生的 NV、DZ、OF、UF、NX 标志按位并入已有状态。

## 示例

2 乘以 3，结果为 6。
