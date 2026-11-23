# HL.SETC.LTI

## 说明

立即数小于置位提交（*Set Commit Argument if Less Than with Immediate*）。读取 `SrcL`，把 24 位有符号立即数符号扩展为 64 位，再左移 `shamt` 位。将两者视为二进制补码有符号数，满足 `SrcL < (simm24 << shamt)` 时向当前条件指令束提交 1，否则提交 0。

本指令不写通用寄存器、向量寄存器或内存。一个条件指令束只接受一次条件设置。

## 汇编语法

```asm
hl.setc.lti SrcL, simm
```

## 操作数

- `SrcL` 是标量源寄存器。
- `simm24` 是 24 位有符号立即数字段。
- `shamt` 是 5 位移位量，作用于符号扩展后的立即数。

## 编码格式

低 16 位：

![HL.SETC.LTI](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SETC.LTI.svg)

高 32 位：

![HL.SETC.LTI](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SETC.LTI.svg)

## 例子

`SrcL = 0xffffffffffffffff`（有符号数 -1）、`simm24 = 0`、`shamt = 0` 时，比较成立，提交值为 1。

## 使用约束

本指令只在活动的条件指令束尚未设置条件时适用。它不占用块内私有寄存器槽位。
