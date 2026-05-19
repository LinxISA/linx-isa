# SWAPB

## 说明

原子交换·字节(*Swap Byte*)  
本指令执行如下的原子操作：从寄存器SrcL指定的内存位置加载`8位`数据无符号扩展后写到目的寄存器中，并将寄存器SrcR`低8位`写到原内存。

## 汇编语法

```c
    swapb<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->{t, u, Rd}
```

## 编码格式

![SWAPB](../../../figs/bitfield/svg/Instruction_32bit/SWAPB.svg)

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **.aq,.rl**：内存访问限制，详见[原子指令介绍](../../blockIntro/sys_block/atomic.md)介绍。
- **.f**：指令可选后缀，表示内存访问发生在远端Cache中。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 将数据无符号扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);

    Atomic {
        bits(64) address = R[m, 64];
        bits(8) newvalue = R[n, 8];
        bits(8) oldvalue = Mem[address];

        Mem[address] = newvalue;
        R[d, 64] = ZeroExtend(oldvalue);
    }
```

## 汇编索引模式

- 指令输出到块内t寄存器

```asm
swapb [a1], a2,            ->t      /* 双寄存器绝对索引 */
swapb [a1], t#2,           ->t      /* 双寄存器混合索引 */
swapb [a1], u#2,           ->t      /* 双寄存器混合索引 */
swapb [t#1], a2,           ->t      /* 双寄存器混合索引 */
swapb [t#1], t#2,          ->t      /* 双寄存器相对索引 */
swapb [t#1], u#2,          ->t      /* 双寄存器相对索引 */
swapb [u#1], a2,           ->t      /* 双寄存器混合索引 */
swapb [u#1], t#2,          ->t      /* 双寄存器相对索引 */
swapb [u#1], u#2,          ->t      /* 双寄存器相对索引 */
swapb.aq [a1], a2,         ->t      /*可选择.aq, .rl, .aqrl的内存访问限制*/
swapb.rl [t#1], a2,        ->t      /*可选择.aq, .rl, .aqrl的内存访问限制*/
swapb.aqrl [u#1], a2,      ->t      /*可选择.aq, .rl, .aqrl的内存访问限制*/
```

- 指令输出到块内u寄存器

```asm
swapb [a1], a2,            ->u      /* 双寄存器绝对索引 */
swapb [a1], t#2,           ->u      /* 双寄存器混合索引 */
swapb [a1], u#2,           ->u      /* 双寄存器混合索引 */
swapb [t#1], a2,           ->u      /* 双寄存器混合索引 */
swapb [t#1], t#2,          ->u      /* 双寄存器相对索引 */
swapb [t#1], u#2,          ->u      /* 双寄存器相对索引 */
swapb [u#1], a2,           ->u      /* 双寄存器混合索引 */
swapb [u#1], t#2,          ->u      /* 双寄存器相对索引 */
swapb [u#1], u#2,          ->u      /* 双寄存器相对索引 */
swapb.aq [a1], a2,         ->u      /*可选择.aq, .rl, .aqrl的内存访问限制*/
swapb.rl [t#1], a2,        ->u      /*可选择.aq, .rl, .aqrl的内存访问限制*/
swapb.aqrl [u#1], a2,      ->u      /*可选择.aq, .rl, .aqrl的内存访问限制*/
```

- 指令输出到块内u寄存器

```asm
swapb [a1], a2,            ->a3      /* 双寄存器绝对索引 */
swapb [a1], t#2,           ->a3      /* 双寄存器混合索引 */
swapb [a1], u#2,           ->a3      /* 双寄存器混合索引 */
swapb [t#1], a2,           ->a3      /* 双寄存器混合索引 */
swapb [t#1], t#2,          ->a3      /* 双寄存器相对索引 */
swapb [t#1], u#2,          ->a3      /* 双寄存器相对索引 */
swapb [u#1], a2,           ->a3      /* 双寄存器混合索引 */
swapb [u#1], t#2,          ->a3      /* 双寄存器相对索引 */
swapb [u#1], u#2,          ->a3      /* 双寄存器相对索引 */
swapb.aq [a1], a2,         ->a3      /*可选择.aq, .rl, .aqrl的内存访问限制*/
swapb.rl [t#1], a2,        ->a3      /*可选择.aq, .rl, .aqrl的内存访问限制*/
swapb.aqrl [u#1], a2,      ->a3      /*可选择.aq, .rl, .aqrl的内存访问限制*/
```

## 约束

- 本指令属于系统块指令集，仅允许在系统块内使用。
- 本指令要求**内存访问地址必须对齐**，否则触发地址不对齐异常。
