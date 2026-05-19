# HL.SD.PCR

## 说明

PC相对寻址.存储双字(*Store Doubleword with PC-Relative*)  
将源数据寄存器中完整的 `八个字节` 存入目标地址指向的内存，目标地址由 **当前TPC** 加 **有符号立即数偏移** 计算得到。 

## 汇编语法

```asm
    hl.sd.pcr SrcL, [symbol]
```

## 汇编符号

- **SrcL**：数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **symbol**：表示存储数据的程序标签，它相对于本指令TPC的距离编码于simm字段。

## 编码格式

- 低16bit编码：

![HL.SD.PCR](../../../figs/bitfield/svg/Instruction_48bit_16/HL.SD.PCR.svg)

- 高32bit编码：

![HL.SD.PCR](../../../figs/bitfield/svg/Instruction_48bit_32/HL.SD.PCR.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);

    bits(64) data = R[m, 64];
    bits(64) offset = SignExtend(simm);

    bits(64) address = current_tpc + offset;
    Mem[address] = data[63:0];
```

## 汇编索引模式

```asm
hl.sd.pcr a1, [symbol]     /* 寄存器绝对索引 */
hl.sd.pcr t#1, [symbol]    /* 寄存器相对索引 */
hl.sd.pcr u#1, [symbol]    /* 寄存器相对索引 */
```

## 注意事项

本指令不占块内私有寄存器槽位。

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，可用于任意类型的块指令块体中。
