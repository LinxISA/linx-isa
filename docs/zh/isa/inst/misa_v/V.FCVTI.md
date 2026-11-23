# V.FCVTI

## 说明

逐活动通道把 `SrcL` 中由 `SrcType` 指定的浮点值转换为 `DstType` 指定的整数格式，并把结果装入目的寄存器的 32 位通道。本指令只有一个源寄存器，不读取第二个源寄存器，也没有编码 `rm` 或 `sat` 操作数；转换使用当前浮点舍入模式，并累计浮点异常标志。

源浮点类型或目的整数类型不受发布模型支持时，指令触发非法指令异常。P 掩码为 0 的通道保持目的寄存器中的原值。

## 汇编语法

```asm
v.fcvti.{st2dt} SrcL, ->Dst
```

## 编码格式

![V.FCVTI](../../../figs/bitfield/svg/Instruction_64bit/V.FCVTI.svg)

## 例子

`v.fcvti.fp162u16 vt#1.fh, ->vt.h` 把 `vt#1` 中的 FP16 元素转换为无符号 16 位整数。
