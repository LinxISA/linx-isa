# MULUW

## 说明

将两个源寄存器的低 32 位相乘。取乘积的低 32 位，符号扩展至 64 位后写入目的寄存器。

## 汇编语法

```asm
muluw SrcL, SrcR, ->{t, u, Rd}
```

## 编码格式

![MULUW](../../../figs/bitfield/svg/Instruction_32bit/MULUW.svg)

## 执行方式

两个输入按无符号数解释。截断乘积后，用结果的第 31 位填满高 32 位。

## 示例

a0 为 `0x40000000`、a1 为 2 时，`muluw a0, a1, ->a2` 写入 `0xffffffff80000000`。

## 汇编索引模式

```asm
muluw a1, a2,           ->t
muluw t#1, t#2,         ->u
muluw u#1, u#2,         ->a3
```
