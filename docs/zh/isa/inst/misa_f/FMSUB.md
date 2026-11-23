# FMSUB

## 说明

融合计算 SrcL × SrcR − SrcA，将结果写入目的寄存器。

## 汇编语法

```asm
fmsub.{T} SrcL, SrcR, SrcA, ->{t, u, Rd}
```

## 数据类型

SrcType 为 0 时读取 FP64，为 1 时读取低 32 位 FP32（载体高位补零）。编码 2 和 3 保留，执行时在读取源寄存器之前触发非法指令异常。

## 编码格式

![FMSUB](../../../figs/bitfield/svg/Instruction_32bit/FMSUB.svg)

## 执行方式

把本次数值运算产生的 NV、DZ、OF、UF、NX 标志按位并入已有状态。

## 示例

三个操作数依次为 2、3、1，结果为 5。
