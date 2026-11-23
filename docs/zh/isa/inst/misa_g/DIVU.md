# DIVU

## 说明

取两个源寄存器的低 64 位，按无符号整数相除。将商写入目的寄存器。

## 汇编语法

```asm
divu SrcL, SrcR, ->{t, u, Rd}
```

## 编码格式

![DIVU](../../../figs/bitfield/svg/Instruction_32bit/DIVU.svg)

## 执行方式

余数等于被除数减去商与除数的乘积。除数为零时，商为零，余数为被除数。

## 示例

若两个操作数分别为 17 和 5，商为 3，余数为 2。因此本指令写入 3。

## 汇编索引模式

```asm
divu a1, a2,           ->t
divu t#1, t#2,         ->u
divu u#1, u#2,         ->a3
```
