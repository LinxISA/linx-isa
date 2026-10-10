# SD.SUB

## 说明

存储双字·减(*Store Doubleword, Subtract*)
本指令执行如下的原子操作：从左源寄存器的值为地址的内存加载`64bit`的数据，与右源寄存器低`64bit`的值相减，将结果写回到原内存中。

## 汇编语法

```c
    sd.sub<.{rl}> [SrcL], SrcR
```

## 编码格式

![SD.SUB](../../../figs/bitfield/svg/Instruction_32bit/SD.SUB.svg)

!!! note "编码说明（v0.58 store-op op5 编码）"

    本指令的 op5（`31..27`）为 `0_1000`：b31=0（保持字/双字宽度），b30..27=`1000`（SUB）。原 `.f` 远端访问后缀已从本类指令中移除，详见[原子指令](../../blockIntro/sys_block/atomic.md)。

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **.rl**：内存访问限制，详见[原子指令](../../blockIntro/sys_block/atomic.md)介绍。

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 64;

    bits(64) address = R[m, 64];
    bits(datawidth) operand = R[n, datawidth];

    Atomic {
        bits(datawidth) data = Mem[address];
        bits(datawidth) result = data - operand;
        Mem[address] = result;
    }
```

## 汇编索引模式

```asm
sd.sub [a1], a2        /* 双寄存器绝对索引 */
sd.sub [a1], t#2       /* 双寄存器混合索引 */
sd.sub [a1], u#2       /* 双寄存器混合索引 */
sd.sub [t#1], a2       /* 双寄存器混合索引 */
sd.sub [t#1], t#2      /* 双寄存器相对索引 */
sd.sub [t#1], u#2      /* 双寄存器相对索引 */
sd.sub [u#1], a2       /* 双寄存器混合索引 */
sd.sub [u#1], t#2      /* 双寄存器相对索引 */
sd.sub [u#1], u#2      /* 双寄存器相对索引 */
sd.sub.rl [a1], a2     /* 前序访存指令限制 */
```

!!! note "注意"

    该指令不占用块内私有寄存器。

## 约束

- 本指令属于系统块指令集，仅允许在系统块内使用。
- 本指令要求**内存访问地址必须8字节对齐**，否则触发地址不对齐异常。
