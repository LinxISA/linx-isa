# C.ZEXT.W

## 说明

无符号扩展字(*Zero-extend Word*)  
将源寄存器的 **低32位** 进行无符号扩展，结果写入T寄存器队列。

## 汇编格式

```
    c.zext.w SrcL, ->t
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **t**：目的寄存器，代表块内的T寄存器队列。

## 编码格式

![ZEXT.W](../../../figs/bitfield/svg/Instruction_16bit/C.ZEXT.W.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 将数据无符号扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer s = UInt(SrcL);
    integer DataWidth = 64;

    bits(DataWidth) data = R[s, DataWidth];
    bits(DataWidth) result = ZeroExtend(data[31:0]);
    T[id] = result;
```

## 汇编索引模式

指令输出到块内T寄存器
```asm
    c.zext.w  a1,  ->t
    c.zext.w  t#1, ->t
    c.zext.w  u#1, ->t
```

## 备注

本指令属于[压缩指令扩展](../../instset/compressInstrs.md)，仅在使能了压缩扩展的处理器中支持使用。
