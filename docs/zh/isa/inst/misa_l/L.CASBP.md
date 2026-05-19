# L.CASBP

## 说明

原子比较交换·一对字节(*Compare and Swap Pair of Byte*)  
本指令执行如下的原子操作：从寄存器SrcL指定的内存位置连续加载两个`8位`数据，分别与寄存器SrcR0和SrcR1的`低8位`进行比较，如果相同的话，把寄存器SrcD0和SrcD1的`低8位`的值存入原内存中。不管前面比较的结果如何，都将从内存读取两个的`8位`数据无符号扩展后分别写入两个目的寄存器中。

## 汇编语法

```asm
    l.casbp<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR0, SrcR1, SrcD0, SrcD1, ->RegDst0, RegDst1
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR0**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR1**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcD0**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcD1**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **RegDst0**：第一个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。
- **RegDst1**：第二个目的寄存器，可以索引块内T队列和U队列寄存器或者全局寄存器R1-R23。
- **.aq,.rl**：内存访问限制，详见[原子指令](../../blockIntro/sys_block/atomic.md)
- **.f**：指令可选后缀，表示内存访问发生在远端Cache中。

## 编码格式

![L.CASBP](../../../figs/bitfield/svg/Instruction_64bit/L.CASBP.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 将数据无符号扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d0 = UInt(RegDst0);
    integer d1 = UInt(RegDst1);
    integer m = UInt(SrcL);
    integer n0 = UInt(SrcR0);
    integer n1 = UInt(SrcR1);
    integer p0 = UInt(SrcD0);
    integer p1 = UInt(SrcD1);

    Atomic {
        bits(64) address = R[m, 64];
        bits(8) cmpvalue0 = R[n0, 8];
        bits(8) cmpvalue1 = R[n1, 8];
        bits(8) newvalue0 = R[p, 8];
        bits(8) newvalue1 = R[p, 8];
        bits(16) oldvalue = Mem[address];
        bits(16) cmpvalue = (cmpvalue1 << 8) | cmpvalue0;
        bits(16) newvalue = (newvalue1 << 8) | newvalue0;

        if oldvalue == cmpvalue then
            Mem[address] = newvalue;
            
        R[d0, 64] = ZeroExtend(oldvalue[7:0]);
        R[d1, 64] = ZeroExtend(oldvalue[15:8]);
    }
```

## 备注

- 本指令要求**内存访问地址必须对齐**，否则触发地址不对齐异常。
- 本指令属于[超长指令扩展](../../instset/longInstrs.md)，且**仅允许在系统块内使用**。
