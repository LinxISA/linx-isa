# C.SETC.TGT

## 说明

读取 SrcL 的完整 64 位值，用它替换当前块的待提交目标 BARG.BPCN。

## 汇编语法

```asm
c.setc.tgt srcL
```

## 编码格式

![C.SETC.TGT](../../../figs/bitfield/svg/Instruction_16bit/C.SETC.TGT.svg)

## 执行方式

这条指令记录的是源值的快照。之后即使覆盖源寄存器，目标也保持不变。目标对齐在块提交时检查。只有标准块或浮点块可使用本指令，且同一块内最多成功执行一次。

## 示例

在合法的标准块内，若 a0 为 0x2000，执行 `c.setc.tgt a0` 后把 a0 改成 0x3000，已记录的目标仍为 0x2000。
