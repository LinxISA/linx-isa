# LW.AND

## 说明

内存加载字相与(*Load Word, And*)  
本指令执行如下的原子操作：以左源寄存器的值为地址的内存中加载`32bit`的数据与右源操作数低`32bit`按位与，将结果写回到原内存，并把加载的数据符号扩展后写到目的寄存器中。

## 汇编语法

```c
    lw.and<.{aq, rl, f, aqrl, aqf, rlf, aqrlf}> [SrcL], SrcR, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **.aq,.rl**：内存访问限制，详见[原子指令](../../blockIntro/sys_block/atomic.md)介绍。
- **.f**：指令可选后缀，表示内存访问发生在远端Cache中。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![LW.AND](../../../figs/bitfield/svg/Instruction_32bit/LW.AND.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 32;

    bits(64) address = R[m, datawidth];
    bits(datawidth) operand = R[n, datawidth];

    Atomic {
        bits(datawidth) oldValue = Mem[address];
        bits(datawidth) newValue = oldValue & operand;

        Mem[address] = newValue;
        R[d, datawidth] = SignExtend(oldValue);
    }
```


## 汇编索引模式

- 指令输出至块内t寄存器

```asm
lw.and [a1], a2          ->t         /* 双寄存器绝对索引 */
lw.and [a1], t#2         ->t         /* 双寄存器绝对索引 */
lw.and [a1], u#2         ->t         /* 双寄存器绝对索引 */
lw.and [t#1], a2         ->t         /* 双寄存器混合索引 */
lw.and [t#1], t#2        ->t         /* 双寄存器相对索引 */
lw.and [t#1], u#2        ->t         /* 双寄存器相对索引 */
lw.and [u#1], a2         ->t         /* 双寄存器混合索引 */
lw.and [u#1], t#2        ->t         /* 双寄存器相对索引 */
lw.and [u#1], u#2        ->t         /* 双寄存器相对索引 */
lw.and.aq [a1], a2       ->t         /*可选择.aq, .rl或.aqrl的内存访问限制*/
lw.and.rl [t#1], a2      ->t         /*可选择.aq, .rl或.aqrl的内存访问限制*/
lw.and.aqrl [u#1], a2    ->t         /*可选择.aq, .rl或.aqrl的内存访问限制*/
```

- 指令输出至块内u寄存器

```asm
lw.and [a1], a2          ->u         /* 双寄存器绝对索引 */
lw.and [a1], t#2         ->u         /* 双寄存器绝对索引 */
lw.and [a1], u#2         ->u         /* 双寄存器绝对索引 */
lw.and [t#1], a2         ->u         /* 双寄存器混合索引 */
lw.and [t#1], t#2        ->u         /* 双寄存器相对索引 */
lw.and [t#1], u#2        ->u         /* 双寄存器相对索引 */
lw.and [u#1], a2         ->u         /* 双寄存器混合索引 */
lw.and [u#1], t#2        ->u         /* 双寄存器相对索引 */
lw.and [u#1], u#2        ->u         /* 双寄存器相对索引 */
lw.and.aq [a1], a2       ->u         /*可选择.aq, .rl或.aqrl的内存访问限制*/
lw.and.rl [t#1], a2      ->u         /*可选择.aq, .rl或.aqrl的内存访问限制*/
lw.and.aqrl [u#1], a2    ->u         /*可选择.aq, .rl或.aqrl的内存访问限制*/
```

- 指令输出至全局R1-R23寄存器

```asm
lw.and [a1], a2          ->a3         /* 双寄存器绝对索引 */
lw.and [a1], t#2         ->a3         /* 双寄存器绝对索引 */
lw.and [a1], u#2         ->a3         /* 双寄存器绝对索引 */
lw.and [t#1], a2         ->a3         /* 双寄存器混合索引 */
lw.and [t#1], t#2        ->a3         /* 双寄存器相对索引 */
lw.and [t#1], u#2        ->a3         /* 双寄存器相对索引 */
lw.and [u#1], a2         ->a3         /* 双寄存器混合索引 */
lw.and [u#1], t#2        ->a3         /* 双寄存器相对索引 */
lw.and [u#1], u#2        ->a3         /* 双寄存器相对索引 */
lw.and.aq [a1], a2       ->a3         /*可选择.aq, .rl或.aqrl的内存访问限制*/
lw.and.rl [t#1], a2      ->a3         /*可选择.aq, .rl或.aqrl的内存访问限制*/
lw.and.aqrl [u#1], a2    ->a3         /*可选择.aq, .rl或.aqrl的内存访问限制*/
```

## 约束

- 本指令属于系统块指令集，仅允许在系统块内使用。
- 本指令要求**内存访问地址必须4字节对齐**，否则触发地址不对齐异常。
