# SD.PCR

## 说明

PC相对寻址·存储双字(*Store Doubleword with PC-Relative*)  
将源数据寄存器的 `八个字节` 存入目标地址指向的内存，目标地址由 **当前TPC** 加 **有符号立即数偏移** 计算得到。 

## 汇编语法

```c
    sd.pcr SrcL, [symbol]
```

## 汇编符号

- **SrcL**：数据寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **symbol**：表示存储数据的程序标签，它相对于本指令TPC的距离编码于simm17字段。

## 编码格式

![SD.PCR](../../../figs/bitfield/svg/Instruction_32bit/SD.PCR.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);

    bits(64) data = R[m, 64];
    bits(64) offset = SignExtend(simm17);

    bits(64) address = current_tpc + offset;
    Mem[address] = data[63:0];
```

## 汇编索引模式

```asm
sd.pcr a1, [symbol]     /* 寄存器绝对索引 */
sd.pcr t#1, [symbol]    /* 寄存器相对索引 */
sd.pcr u#1, [symbol]    /* 寄存器相对索引 */
```

## 注意事项

本指令不占块内私有寄存器槽位。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
