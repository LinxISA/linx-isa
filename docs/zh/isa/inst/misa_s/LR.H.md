# LR.H

## 说明

加载保留半字(*Load-Reserved Halfword*)  
本指令执行如下的原子操作：从源寄存器的值为地址的内存中加载`2个字节`的数据，符号位扩展后写入目的寄存器中，并对这个内存字注册保留。

## 汇编语法

```c
    lr.h<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **.aq,.rl**：内存访问限制，详见[原子指令](../../blockIntro/sys_block/atomic.md)介绍。
- **.f**：指令可选后缀，表示内存访问发生在远端Cache中。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![LR.H](../../../figs/bitfield/svg/Instruction_32bit/LR.H.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)
- 内存加载保留：LoadReserved()-告诉独占监视器Exclusive monitor记录从虚拟地址范围[address, address+1]中读取的一个或多个原子内存的序列。只有当所有的读操作都来自相同的2字节对齐的物理地址时，才会设置独占监视器，以允许在读操作之间转换发生变化时原子性中断的可能性。

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) address = R[s, datawidth];
    bits(16) data = LoadReserved(Mem[address][15:0]);

    R[d, datawidth] = SignExtend(data[15:0]);
```

## 汇编索引模式

- 指令输出到块内t寄存器

```asm
lr.h [a1]          ->t      /* 单寄存器绝对索引 */
lr.h [t#1]         ->t      /* 单寄存器相对索引 */
lr.h [u#1]         ->t      /* 单寄存器相对索引 */
lr.h.aq [a1]       ->t      /* 后序访存指令限制 */
lr.h.rl [t#1]      ->t      /* 前序访存指令限制 */
lr.h.aqrl [u#1]    ->t      /* 前序和后序访存指令限制 */
```

- 指令输出到块内u寄存器

```asm
lr.h [a1]          ->u      /* 单寄存器绝对索引 */
lr.h [t#1]         ->u      /* 单寄存器相对索引 */
lr.h [u#1]         ->u      /* 单寄存器相对索引 */
lr.h.aq [a1]       ->u      /* 后序访存指令限制 */
lr.h.rl [t#1]      ->u      /* 前序访存指令限制 */
lr.h.aqrl [u#1]    ->u      /* 前序和后序访存指令限制 */
```

- 指令输出到全局寄存器R1-R23

```asm
lr.h [a1]          ->a3      /* 单寄存器绝对索引 */
lr.h [t#1]         ->a3      /* 单寄存器相对索引 */
lr.h [u#1]         ->a3      /* 单寄存器相对索引 */
lr.h.aq [a1]       ->a3      /* 后序访存指令限制 */
lr.h.rl [t#1]      ->a3      /* 前序访存指令限制 */
lr.h.aqrl [u#1]    ->a3      /* 前序和后序访存指令限制 */
```

## 约束

- 本指令属于系统块指令集，仅允许在系统块内使用。
- 本指令要求**内存访问地址必须2字节对齐**，否则触发地址不对齐异常。
- 除SC类指令外，普通Store指令也会清除其保留标记。
- LR.H与SC.H指令成对出现性能会比较好，单独出现会导致监视器阻塞。
