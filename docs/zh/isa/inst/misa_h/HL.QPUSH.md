# HL.QPUSH

## 说明

入队列(*Push to Queue*)  
GQM提供了跨核的原子操作队列管理能力，QPUSH指令把SrcR的数据写到SrcL指定的GQM队列中，将执行结果写入到目的寄存器。

## 汇编语法

```asm
    hl.qpush{.h,.b,.r,.hb,.hr,.br,.hbr} SrcL, SrcR, ->{t, u}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **{.h,.b,.r,.hb,.hr,.br,.hbr}**：指令后面可以加上标记，具体含义如下:
    - 加上.h表示push到队首，否则默认push到队尾。
    - 加上.b表示指令同时向总线广播BWE(Block Wait for Event)通知，可唤醒所有处于等待状态的BWE事件。
    - 加上.r表示指令无 内存序 强制，否则本指令保证，qpop一方在读到本数据时，本指令在程序序前的内存写操作必然被qpop之后的内存读操作访问到。
- **->**：用于指示目的寄存器。
- **t,u**: 目的寄存器，代表块内的T,U寄存器队列。
- 指令的执行结果输出到t或者u寄存器，数据存储格式如下：
    - [9:0] 表示写入后队列中的剩余单元数。
    - [63:62] 0表示写入成功，1表示队列满，2表示数据破坏，3保留。

## 编码格式

- 低16bit编码：

![HL.QPUSH](../../../figs/bitfield/svg/Instruction_48bit_16/HL.QPUSH.svg)

- 高32bit编码：

![HL.QPUSH](../../../figs/bitfield/svg/Instruction_48bit_32/HL.QPUSH.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 64;
    integer remainNums, state;

    bits(datawidth) address = R[m, datawidth];
    bits(datawidth) operand = R[n, datawidth];
    
    if h == 1 then
        {remainNums, state} = GQM[address].push_front(operand);   //push到队首，否则默认push到队尾
    else
        {remainNums, state} = GQM[address].push_back(operand);

    if b == 1 then
        GQM[address].notify();                                     //同时向总线广播BWE通知，可唤醒所有处于等待状态的BWE事件
    
    bits(datawidth) result;                                          //执行的结果
    result[9:0] = remainNums;                                       //表示写入后队列中的剩余单元数。
    result[63:62] = state;                                          //0表示写入成功，1表示队列满，2表示数据破坏，3保留。

    R[d, datawidth] = result;

```

## 汇编索引模式

- 指令输出到块内t寄存器

```asm
hl.qpush.h  a1, a2,       ->t         /*双寄存器绝对索引*/
hl.qpush.h  a1, t#2,      ->t         /*双寄存器混合索引*/
hl.qpush.h  a1, u#2,      ->t         /*双寄存器混合索引*/
hl.qpush.h  t#1, a2,      ->t         /*双寄存器混合索引*/
hl.qpush.h  t#1, t#2,     ->t         /*双寄存器相对索引*/
hl.qpush.h  t#1, u#2,     ->t         /*双寄存器相对索引*/
hl.qpush.h  u#1, a2,      ->t         /*双寄存器混合索引*/
hl.qpush.h  u#1, t#2,     ->t         /*双寄存器相对索引*/
hl.qpush.h  u#1, u#2,     ->t         /*双寄存器相对索引*/
hl.qpush.b  a1, t#2,      ->t         /*可选择.h,.b,.r,.hb,.hr,.br,.hbr等标记*/
hl.qpush.hb  t#1, a2,     ->t         /*可选择.h,.b,.r,.hb,.hr,.br,.hbr等标记*/
hl.qpush.hbr  u#1, a2,    ->t         /*可选择.h,.b,.r,.hb,.hr,.br,.hbr等标记*/
```

- 指令输出到块内u寄存器

```asm
hl.qpush.h  a1, a2,       ->u         /*双寄存器绝对索引*/
hl.qpush.h  a1, t#2,      ->u         /*双寄存器混合索引*/
hl.qpush.h  a1, u#2,      ->u         /*双寄存器混合索引*/
hl.qpush.h  t#1, a2,      ->u         /*双寄存器混合索引*/
hl.qpush.h  t#1, t#2,     ->u         /*双寄存器相对索引*/
hl.qpush.h  t#1, u#2,     ->u         /*双寄存器相对索引*/
hl.qpush.h  u#1, a2,      ->u         /*双寄存器混合索引*/
hl.qpush.h  u#1, t#2,     ->u         /*双寄存器相对索引*/
hl.qpush.h  u#1, u#2,     ->u         /*双寄存器相对索引*/
hl.qpush.b  a1, t#2,      ->u         /*可选择.h,.b,.r,.hb,.hr,.br,.hbr等标记*/
hl.qpush.hb  t#1, a2,     ->u         /*可选择.h,.b,.r,.hb,.hr,.br,.hbr等标记*/
hl.qpush.hbr  u#1, a2,    ->u         /*可选择.h,.b,.r,.hb,.hr,.br,.hbr等标记*/
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，并且只能用于系统块指令块体中。
