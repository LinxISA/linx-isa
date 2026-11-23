# CSEL

## 说明

若 SrcP 非零，将 SrcL 写入目标；若 SrcP 为零，则写入 SrcR 或它的相反数。

## 汇编语法

```asm
csel SrcP, SrcL, SrcR<.neg>, ->{t, u, Rd}
```

## 编码格式

![CSEL](../../../figs/bitfield/svg/Instruction_32bit/CSEL.svg)

## 执行方式

在写回前读取全部三个源寄存器。只有右操作数带 .neg 时才对它取负，运算按 64 位回绕。SrcRType 的 00、01、10 均保留右源原值，11 表示取负。

## 示例

SrcP 为 0、SrcL 为 3、SrcR 为 5 时，右源带 .neg 的形式写入 −5；若 SrcP 为 2，则写入 3。

## 汇编索引模式

```asm
csel a1, a2, a3,          ->t
csel t#1, u#2, a3,        ->u
csel u#1, u#2, u#3,       ->a4
```
