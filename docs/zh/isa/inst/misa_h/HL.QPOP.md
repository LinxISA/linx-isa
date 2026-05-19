# HL.QPOP

## 说明

出队列(*Pop from Queue*)  
读出 SrcL 指定的GQM队列的数据输出到第一个目的寄存器并且将执行结果输出到第二个目的寄存器。

## 汇编语法

```asm
    hl.qpop{.b,.r,.br,} SrcL, ->Dst0, Dst1
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **{.b,.r,.br,}**：指令后面可以加上标记，具体含义如下:
    - 加上.r表示指令无 内存序 强制，否则本指令保证, 如果在qpush指令之前的程序中有写内存操作，那么在qpush指令之后的程序中进行的读操作将能够看到这些写操作的结果。
    - 加上.b表示指令同时向总线广播BWE(Block Wait for Event)通知，可唤醒所有处于等待状态的BWE指令。
- **->**：用于指示目的寄存器。
- **Dst0**：第一个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。
- **Dst1**：第二个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。

本指令为双输出指令，第一个目的寄存器为读出的数据，第二个目的寄存器为执行结果。

- 如果无输出返回，第一个目的寄存器中输出0。
- 第二个目的寄存器中内容存储格式如下：
    - [12:0]：表示数据读出后队列中的剩余单元数。
    - [63:62]：0表示读出成功，1表示队列空，2表示数据破坏，3保留。

## 编码格式

- 低16bit编码：

![HL.QPOP](../../../figs/bitfield/svg/Instruction_48bit_16/HL.QPOP.svg)

- 高32bit编码：

![HL.QPOP](../../../figs/bitfield/svg/Instruction_48bit_32/HL.QPOP.svg)


## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d0 = UInt(RegDst0);
    integer d1 = UInt(RegDst1);
    integer m = UInt(SrcL);
    integer remainNums, state;
    
    if b == 1 then
        GQM[address].notify();                         //同时向总线广播BWE通知，可唤醒所有处于等待状态的BWE事件
    
    bits(64) result;                              //执行的结果
    bits(64) data; 

    bits(64) address = R[m, 64];
    {remainNums, state, data} = GQM[address].pop();
    if state != 0 then
        data = 0;
    result[12:0] = remainNums;                           //表示写入后队列中的剩余单元数。
    result[63:62] = state;                                //0表示写入成功，1表示队列满，2表示数据破坏，3保留。

    R[d0, 64] = data;
    R[d1, 64] = result;
```

## 汇编索引模式

| 输入 | 输出<br>组合1 | 输出<br>组合2 | 输出<br>组合3 | 输出<br>组合4 | 输出<br>组合5 | 输出<br>组合6 | 输出<br>组合7 | 输出<br>组合8 | 输出<br>组合9 |
|------|---------------|--------------|--------------|--------------|---------------|--------------|--------------|---------------|--------------|
| a1  | t, t | t, u | t, a3 | u, t | u, u | u, a3 | a3, t | a3, u | a3, a4 |
| t#1  | t, t | t, u | t, a3 | u, t | u, u | u, a3 | a3, t | a3, u | a3, a4 |
| u#1  | t, t | t, u | t, a3 | u, t | u, u | u, a3 | a3, t | a3, u | a3, a4 |

## 备注

本指令属于[增强指令扩展](../../instset/haflLongInstrs.md)，并且只能用于系统块指令块体中。
