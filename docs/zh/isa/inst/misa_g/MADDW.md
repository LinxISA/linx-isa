# MADDW

## 说明

乘加·字(*Multiply and Add Word*)  
有符号计算第一个源操作数乘以第二个源操作数，再加上第三个源操作数，将结果的`低32位`符号扩展后写到目的寄存器中。

## 汇编语法

```
    maddw SrcL, SrcR, SrcD, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：第一个源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：第二个源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcD**：第三个源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![MADDW](../../../figs/bitfield/svg/Instruction_32bit/MADDW.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer k = UInt(SrcD);

    bits(32) operand1 = R[m, 32];
    bits(32) operand2 = R[n, 32];
    bits(32) operand3 = R[k, 32];
    bits(64) result = operand3 +(s) operand1 *(s) operand2;

    R[d, 64] = SignExtend(result[31:0]);
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
maddw a1, a2, a3,           ->t             /* 三寄存器绝对索引 */
maddw a1, t#2, a3,          ->t             /* 三寄存器混合索引 */
maddw a1, a2, u#3,          ->t             /* 三寄存器混合索引 */
maddw a1, u#2, t#3,         ->t             /* 三寄存器混合索引 */
maddw t#1, a2, a3,          ->t             /* 三寄存器混合索引 */
maddw t#1, t#2, a3,         ->t             /* 三寄存器混合索引 */
maddw t#1, a2, u#3,         ->t             /* 三寄存器混合索引 */
maddw t#1, u#2, t#3,        ->t             /* 三寄存器相对索引 */
maddw u#1, a2, a3,          ->t             /* 三寄存器混合索引 */
maddw u#1, t#2, a3,         ->t             /* 三寄存器混合索引 */
maddw u#1, a2, u#3,         ->t             /* 三寄存器混合索引 */
maddw u#1, u#2, t#3,        ->t             /* 三寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
maddw a1, a2, a3,           ->u             /* 三寄存器绝对索引 */
maddw a1, t#2, a3,          ->u             /* 三寄存器混合索引 */
maddw a1, a2, u#3,          ->u             /* 三寄存器混合索引 */
maddw a1, u#2, t#3,         ->u             /* 三寄存器混合索引 */
maddw t#1, a2, a3,          ->u             /* 三寄存器混合索引 */
maddw t#1, t#2, a3,         ->u             /* 三寄存器混合索引 */
maddw t#1, a2, u#3,         ->u             /* 三寄存器混合索引 */
maddw t#1, u#2, t#3,        ->u             /* 三寄存器相对索引 */
maddw u#1, a2, a3,          ->u             /* 三寄存器混合索引 */
maddw u#1, t#2, a3,         ->u             /* 三寄存器混合索引 */
maddw u#1, a2, u#3,         ->u             /* 三寄存器混合索引 */
maddw u#1, u#2, t#3,        ->u             /* 三寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
maddw a1, a2, a3,           ->a3             /* 三寄存器绝对索引 */
maddw a1, t#2, a3,          ->a3             /* 三寄存器混合索引 */
maddw a1, a2, u#3,          ->a3             /* 三寄存器混合索引 */
maddw a1, u#2, t#3,         ->a3             /* 三寄存器混合索引 */
maddw t#1, a2, a3,          ->a3             /* 三寄存器混合索引 */
maddw t#1, t#2, a3,         ->a3             /* 三寄存器混合索引 */
maddw t#1, a2, u#3,         ->a3             /* 三寄存器混合索引 */
maddw t#1, u#2, t#3,        ->a3             /* 三寄存器相对索引 */
maddw u#1, a2, a3,          ->a3             /* 三寄存器混合索引 */
maddw u#1, t#2, a3,         ->a3             /* 三寄存器混合索引 */
maddw u#1, a2, u#3,         ->a3             /* 三寄存器混合索引 */
maddw u#1, u#2, t#3,        ->a3             /* 三寄存器相对索引 */
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
