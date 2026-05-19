# HL.QMT

## 说明

队列维护指令(*Queue Management Transfer*)  
对SrcL指定的GQM队列进行管理和维护，使得通讯过程更加规范和高效，QMT指令通常用于在多处理器或多核之间传递数据或指令，确保消息的有序传递和处理。

GQM队列的最大空间是 2^10 字节。

## 汇编语法

```asm
    hl.qmt{.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr} SrcL, SrcR, ->{t, u}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：SrcR仅对带.i后缀的指令有效，在这种情况下，它的格式定义如下：
    - SrcR[9:0] 表示队列中可容纳的64位单元最大数量。
- **{.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr}**：指令后面可以加上标记，具体含义如下:
    - 没有.i后缀，指令输出队列中剩余的单元数量。
    - 加.i表示重新初始化队列，并返回占用的内存空间大小。
    - 加上.b表示指令同时向总线广播BWE(Block Wait for Event)通知，可唤醒所有处于等待状态的BWE事件。
    - 加上.s表示挂起队列，队列只能读出，不能写入。本后缀不可以和.r后缀同时使用。
    - 加上.r表示恢复队列，队列可以读出和写入。本后缀不可以和.r后缀同时使用。
- **->**：用于指示目的寄存器。
- **t,u**: 目的寄存器，代表块内的T,U寄存器队列。数据存储格式如下：
    - [9:0] 表示根据要求输出的单元数量。
    - [63:62] 0表示执行成功，1表示数据损坏，2, 3保留。

## 编码格式

- 低16bit编码：

![HL.QMT](../../../figs/bitfield/svg/Instruction_48bit_16/HL.QMT.svg)

- 高32bit编码：

![HL.QMT](../../../figs/bitfield/svg/Instruction_48bit_32/HL.QMT.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 64;
    integer remainNums, capacity, memorysize;

    bits(64) address = R[m, datawidth];
    bits(64) operand = R[n, datawidth];
    
    if i == 0 then 
        remainNums = GQM[address].size();             //输出队列中剩余的单元数量
        R[d, datawidth] = remainNums;
    else
        capacity = operand[9:0];                      //队列中可容纳的64位单元最大数量
        GQM[address].init(capacity);
        memorysize = GQM[address].size() * 8(Byte);   //占用的内存空间大小
        R[d, datawidth] = memorysize;

    if b == 1 then
        GQM[address].notify();                         //同时向总线广播BWE通知，可唤醒所有处于等待状态的BWE事件

    if s == 1 then
        GQM[address].pending();                           //挂起队列，队列只能读出，不能写入

    if r == 1 then
        GQM[address].restore();                            //恢复队列，队列可以读出和写入。
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
hl.qmt.i  a1, a2,       ->t         /*双寄存器绝对索引*/
hl.qmt.i  a1, t#2,      ->t         /*双寄存器混合索引*/
hl.qmt.i  a1, u#2,      ->t         /*双寄存器混合索引*/
hl.qmt.i  t#1, a2,      ->t         /*双寄存器混合索引*/
hl.qmt.i  t#1, t#2,     ->t         /*双寄存器相对索引*/
hl.qmt.i  t#1, u#2,     ->t         /*双寄存器相对索引*/
hl.qmt.i  u#1, a2,      ->t         /*双寄存器混合索引*/
hl.qmt.i  u#1, t#2,     ->t         /*双寄存器相对索引*/
hl.qmt.i  u#1, u#2,     ->t         /*双寄存器相对索引*/
hl.qmt.b  a1, t#2,      ->t         /*可选择.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr等标记*/
hl.qmt.ib  t#1, a2,     ->t         /*可选择.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr等标记*/
hl.qmt.ir  u#1, a2,     ->t         /*可选择.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr等标记*/
```

指令输出到块内u寄存器:
```asm
hl.qmt.i  a1, a2,       ->u         /*双寄存器绝对索引*/
hl.qmt.i  a1, t#2,      ->u         /*双寄存器混合索引*/
hl.qmt.i  a1, u#2,      ->u         /*双寄存器混合索引*/
hl.qmt.i  t#1, a2,      ->u         /*双寄存器混合索引*/
hl.qmt.i  t#1, t#2,     ->u         /*双寄存器相对索引*/
hl.qmt.i  t#1, u#2,     ->u         /*双寄存器相对索引*/
hl.qmt.i  u#1, a2,      ->u         /*双寄存器混合索引*/
hl.qmt.i  u#1, t#2,     ->u         /*双寄存器相对索引*/
hl.qmt.i  u#1, u#2,     ->u         /*双寄存器相对索引*/
hl.qmt.b  a1, t#2,      ->u         /*可选择.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr等标记*/
hl.qmt.ib  t#1, a2,     ->u         /*可选择.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr等标记*/
hl.qmt.ir  u#1, a2,     ->u         /*可选择.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr等标记*/
```

指令输出到全局R1-R23寄存器:
```asm
hl.qmt.i  a1, a2,       ->a3         /*双寄存器绝对索引*/
hl.qmt.i  a1, t#2,      ->a3         /*双寄存器混合索引*/
hl.qmt.i  a1, u#2,      ->a3         /*双寄存器混合索引*/
hl.qmt.i  t#1, a2,      ->a3         /*双寄存器混合索引*/
hl.qmt.i  t#1, t#2,     ->a3         /*双寄存器相对索引*/
hl.qmt.i  t#1, u#2,     ->a3         /*双寄存器相对索引*/
hl.qmt.i  u#1, a2,      ->a3         /*双寄存器混合索引*/
hl.qmt.i  u#1, t#2,     ->a3         /*双寄存器相对索引*/
hl.qmt.i  u#1, u#2,     ->a3         /*双寄存器相对索引*/
hl.qmt.b  a1, t#2,      ->a3         /*可选择.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr等标记*/
hl.qmt.ib  t#1, a2,     ->a3         /*可选择.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr等标记*/
hl.qmt.ir  u#1, a2,     ->a3         /*可选择.i,.b,.s,.r,.ib,.is,.ir,.bs,.br,.ibs,.ibr等标记*/
```

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，并且只能用于系统块指令块体中。
