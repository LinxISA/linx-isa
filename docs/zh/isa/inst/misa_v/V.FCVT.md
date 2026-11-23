# V.FCVT

## 说明

逐活动通道把 `SrcL` 中由 `SrcType` 指定的浮点值转换为 `DstType` 指定的浮点格式，并写入目的寄存器。本指令只有一个源寄存器，不读取第二个源寄存器，也没有编码 `rm` 或 `sat` 操作数；转换使用当前浮点舍入模式，并累计浮点异常标志。

源类型或目的类型不是发布模型支持的浮点类型编码时，指令触发非法指令异常。P 掩码为 0 的通道保持目的寄存器中的原值。

## 汇编语法

```asm
v.fcvt.{st2dt} SrcL, ->Dst
```

## 编码格式

![V.FCVT](../../../figs/bitfield/svg/Instruction_64bit/V.FCVT.svg)

## 例子

`v.fcvt.fp162e5m2 vt#1.fh, ->vt.b` 把 `vt#1` 中的 FP16 元素转换为 E5M2 元素。
