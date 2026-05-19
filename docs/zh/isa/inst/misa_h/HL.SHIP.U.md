# HL.SHIP.U

## 说明

立即数偏移无缩放.存储一对半字(*Store Pair Halfword with Unscaled Immediate Offset*)  
将两个数据寄存器的低位 `两个字节` 依次存入目标地址指向的内存中，目标地址由 **基址寄存器** 加 **有符号立即数偏移** 计算得到。 

## 汇编语法

```asm
    hl.ship.u SrcD0, SrcD1, [SrcR, simm]
```

## 汇编符号

- **SrcD0**：第一个数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcD1**：第二个数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：基址寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数偏移，编码在simm17字段中。

## 编码格式

- 低16bit编码：

![HL.SHIP.U](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SHIP.U.svg)

- 高32bit编码：

![HL.SHIP.U](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SHIP.U.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer m1 = UInt(SrcD0);
    integer m2 = UInt(SrcD1);
    integer n = UInt(SrcR);

    bits(64) data1 = R[m1, 64];
    bits(64) data2 = R[m2, 64];
    bits(64) baseAddr = R[n, 64];
    bits(64) offset = SignExtend(simm17);

    bits(64) address = baseAddr + offset;
    Mem[address] = data1[15:0];
    Mem[address+2] = data2[15:0];
```

## 汇编索引模式

```asm
hl.ship.u a1, a2, [a3, simm]      /* 三寄存器绝对索引 */
hl.ship.u a1, a2, [t#3, simm]     /* 三寄存器混合索引 */
hl.ship.u a1, a2, [u#3, simm]     /* 三寄存器混合索引 */
hl.ship.u a1, t#2, [a3, simm]     /* 三寄存器混合索引 */
hl.ship.u a1, t#2, [t#3, simm]    /* 三寄存器混合索引 */
hl.ship.u a1, t#2, [u#3, simm]    /* 三寄存器混合索引 */
hl.ship.u a1, u#2, [a3, simm]     /* 三寄存器混合索引 */
hl.ship.u a1, u#2, [t#3, simm]    /* 三寄存器混合索引 */
hl.ship.u a1, u#2, [u#3, simm]    /* 三寄存器混合索引 */
hl.ship.u t#1, a2, [a3, simm]     /* 三寄存器混合索引 */
hl.ship.u t#1, a2, [t#3, simm]    /* 三寄存器混合索引 */
hl.ship.u t#1, a2, [u#3, simm]    /* 三寄存器混合索引 */
hl.ship.u t#1, t#2, [a3, simm]    /* 三寄存器混合索引 */
hl.ship.u t#1, t#2, [t#3, simm]   /* 三寄存器相对索引 */
hl.ship.u t#1, t#2, [u#3, simm]   /* 三寄存器相对索引 */
hl.ship.u t#1, u#2, [a3, simm]    /* 三寄存器混合索引 */
hl.ship.u t#1, u#2, [t#3, simm]   /* 三寄存器相对索引 */
hl.ship.u t#1, u#2, [u#3, simm]   /* 三寄存器相对索引 */
hl.ship.u u#1, a2, [a3, simm]     /* 三寄存器混合索引 */
hl.ship.u u#1, a2, [t#3, simm]    /* 三寄存器混合索引 */
hl.ship.u u#1, a2, [u#3, simm]    /* 三寄存器混合索引 */
hl.ship.u u#1, t#2, [a3, simm]    /* 三寄存器混合索引 */
hl.ship.u u#1, t#2, [t#3, simm]   /* 三寄存器相对索引 */
hl.ship.u u#1, t#2, [u#3, simm]   /* 三寄存器相对索引 */
hl.ship.u u#1, u#2, [a3, simm]    /* 三寄存器混合索引 */
hl.ship.u u#1, u#2, [t#3, simm]   /* 三寄存器相对索引 */
hl.ship.u u#1, u#2, [u#3, simm]   /* 三寄存器相对索引 */
```

## 注意事项

本指令不占块内私有寄存器槽位。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
