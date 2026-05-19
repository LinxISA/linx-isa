# SD.UMIN

## 说明

存储双字·无符号最小值(*Store Doubleword, Unsigned Minimum*)  
本指令执行如下的原子操作：从左源寄存器的值为地址的内存加载`64bit`的数据，与右源寄存器的值进行无符号比较，将较小值写回到原内存中。

## 汇编语法

```c
    sd.umin<.{rl, f, rlf}> [SrcL], SrcR
```

## 编码格式

![SD.UMIN](../../../figs/bitfield/svg/Instruction_32bit/SD.UMIN.svg)

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **.rl**：内存访问限制，详见[原子指令](../../blockIntro/sys_block/atomic.md)介绍。介绍。
- **.f**：指令可选后缀，表示内存访问发生在远端Cache中。

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 64;

    bits(datawidth) address = R[m, datawidth];
    bits(datawidth) operand = R[n, datawidth];

    Atomic {
        bits(datawidth) data = Mem[address];
        bits(datawidth) result = (operand <(u) data ? operand : data);
        Mem[address] = result;
    }
```

## 汇编索引模式

```asm
sd.umin [a1], a2        /* 双寄存器绝对索引 */
sd.umin [a1], t#2       /* 双寄存器混合索引 */
sd.umin [a1], u#2       /* 双寄存器混合索引 */
sd.umin [t#1], a2       /* 双寄存器混合索引 */
sd.umin [t#1], t#2      /* 双寄存器相对索引 */
sd.umin [t#1], u#2      /* 双寄存器相对索引 */
sd.umin [u#1], a2       /* 双寄存器混合索引 */
sd.umin [u#1], t#2      /* 双寄存器相对索引 */
sd.umin [u#1], u#2      /* 双寄存器相对索引 */
sd.umin.rl [a1], a2     /* 前序访存指令限制 */
```

!!! note "注意"

    该指令不占用块内私有寄存器。

## 约束

- 本指令属于系统块指令集，仅允许在系统块内使用。
- 本指令要求**内存访问地址必须8字节对齐**，否则触发地址不对齐异常。
