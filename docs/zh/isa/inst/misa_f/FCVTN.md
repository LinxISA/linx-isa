# FCVTN

## 说明

将浮点数转换为指定宽度的整数，舍入到最近整数，中点取偶数。

## 汇编语法

```asm
fcvtn.{srcT2dstT} SrcL, ->{t, u, Rd}
```

## 数据类型

SrcType 的编码 0 至 3 依次选择FP64、FP32、FP16、E4M3。DstType 的 0 至 3 依次选择 U64、U32、U16、U8，4 至 7 依次选择 S64、S32、S16、S8，8 至 31 保留。

## 编码格式

![FCVTN](../../../figs/bitfield/svg/Instruction_32bit/FCVTN.svg)

## 执行方式

把本次数值运算产生的 NV、DZ、OF、UF、NX 标志按位并入已有状态。标量转换关闭饱和；保留的类型编码在读取源寄存器前触发非法指令异常。

## 示例

−2.5 转为 −2（有符号目标）。
