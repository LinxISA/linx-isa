# V.SD.BRG

## 说明

按照 v0.59.1 发布 Sail，本指令用 `SrcL + (LC0 × 8) + (SrcR[0] << shamt)` 形成一个有效地址，再把 `SrcD` 的 lane 1、lane 0 拼成一个 64 位值写入该地址。这里的 `SrcR[0]` 表示索引向量 lane 0 的 32 位值。

发布 Sail 只使用索引 lane 0 和第一项 64 位源数据，不读取 P 掩码。它没有读取桥接表，也没有按桥接表索引选择另一项源数据。`.local` 编码位会被译码，但当前处理程序不使用它，也没有据此切换地址空间。

## 汇编语法

```asm
v.sd.brg<.local> SrcD.<T1>, [SrcL, <lc0<<3>, SrcR.<T2><<(3+shamt)]
```

## 编码格式

![V.SD.BRG](../../../figs/bitfield/svg/Instruction_64bit/V.SD.BRG.svg)

## 0.59.1 内部不一致

目录汇编把索引位移写成 `SrcR << (3 + shamt)`，发布 Sail 只执行 `SrcR << shamt`。两者在同一 `shamt` 下会形成不同地址。0.59.1 没有在这两份发布资料之间给出裁决，因此这一位移差异不能当作已经确定的硬件要求。
