# DIVUW

## 说明

取两个源寄存器的低 32 位，按无符号整数相除。将商写入目的寄存器。

## 汇编语法

```asm
divuw SrcL, SrcR, ->{t, u, Rd}
```

## 编码格式

![DIVUW](../../../figs/bitfield/svg/Instruction_32bit/DIVUW.svg)

## 执行方式

余数等于被除数减去商与除数的乘积。除数为零时，商为零，余数为被除数。每个写回结果都从 32 位符号扩展到 64 位。

## 示例

若两个操作数分别为 17 和 5，商为 3，余数为 2。因此本指令写入 3。

## 汇编索引模式

```asm
divuw a1, a2,           ->t
divuw t#1, t#2,         ->u
divuw u#1, u#2,         ->a3
```
