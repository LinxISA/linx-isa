# FCVT

## 说明

将浮点源值转换为指定的目标浮点格式。

## 汇编语法

```asm
fcvt.{srcT2dstT} SrcL, ->{t, u, Rd}
```

## 数据类型

SrcType 的编码 0 至 3 依次选择FP64、FP32、FP16、E4M3。DstType 的编码 0 至 3 依次选择FP64、FP32、FP16、E4M3，4 至 31 保留。

## 编码格式

![FCVT](../../../figs/bitfield/svg/Instruction_32bit/FCVT.svg)

## 执行方式

把本次数值运算产生的 NV、DZ、OF、UF、NX 标志按位并入已有状态。标量转换关闭饱和；保留的类型编码在读取源寄存器前触发非法指令异常。

## 示例

源值为 3，目标格式为 FP32，结果为 3.0。
