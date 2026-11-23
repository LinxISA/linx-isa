# HL.SETC.ORI

## 说明

立即数或置位提交（*Set Commit Argument by Or Immediate*）。读取 `SrcL`，把 24 位有符号立即数符号扩展为 64 位，再左移 `shamt` 位；随后对两者按位或。按位或结果非零时向当前条件指令束提交 1，结果为零时提交 0。

本指令不写通用寄存器、向量寄存器或内存。立即数为零时，它等价于对 `SrcL` 做非零判定。

## 汇编语法

```asm
hl.setc.ori SrcL, simm
```

## 操作数

- `SrcL` 是标量源寄存器。
- `simm24` 是 24 位有符号立即数字段。
- `shamt` 是 5 位移位量，作用于符号扩展后的立即数。

## 编码格式

低 16 位：

![HL.SETC.ORI](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SETC.ORI.svg)

高 32 位：

![HL.SETC.ORI](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SETC.ORI.svg)

## 例子

`SrcL = 0`、`simm24 = 0`、`shamt = 0` 时提交 0；把 `simm24` 改为 1 后提交 1。

## 使用约束

本指令只在活动的条件指令束尚未设置条件时适用。它不占用块内私有寄存器槽位。
