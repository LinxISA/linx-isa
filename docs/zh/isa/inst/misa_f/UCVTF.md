# UCVTF

## 说明

将无符号整数转换为指定格式的浮点数。

## 汇编语法

```asm
ucvtf.{srcT2dstT} SrcL, ->{t, u, Rd}
```

## 数据类型

SrcType 的编码 0 至 3 依次选择64、32、16、8 位无符号整数。DstType 的编码 0 至 3 依次选择FP64、FP32、FP16、E4M3，4 至 31 保留。

## 编码格式

![UCVTF](../../../figs/bitfield/svg/Instruction_32bit/UCVTF.svg)

## 执行方式

把本次数值运算产生的 NV、DZ、OF、UF、NX 标志按位并入已有状态。标量转换关闭饱和；保留的类型编码在读取源寄存器前触发非法指令异常。

## 示例

源值为 3，目标格式为 FP32，结果为 3.0。
