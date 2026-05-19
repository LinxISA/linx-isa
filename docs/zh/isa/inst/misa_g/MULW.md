# MULW

## 说明

乘·字(*Multiply Word*)  
有符号计算左源操作数的低32位乘以右源操作数的低32位，结果取`低32位`符号扩展后写到目的寄存器中。

## 汇编语法

```
    mulw SrcL, SrcR, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![MULW](../../../figs/bitfield/svg/Instruction_32bit/MULW.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 32;

    bits(32) operand1 = R[m, 32];
    bits(32) operand2 = R[n, 32];
    bits(64) result = operand1 *(s) operand2;

    R[d, 32] = SignExtend(result[31:0]);
```


## 汇编索引模式

指令输出到块内t寄存器:
```asm
mulw a1, a2,           ->t             /* 双寄存器绝对索引 */
mulw a1, t#2,          ->t             /* 双寄存器混合索引 */
mulw a1, u#2,          ->t             /* 双寄存器混合索引 */
mulw t#1, a2,          ->t             /* 双寄存器混合索引 */
mulw t#1, t#2,         ->t             /* 双寄存器相对索引 */
mulw t#1, u#2,         ->t             /* 双寄存器相对索引 */
mulw u#1, a2,          ->t             /* 双寄存器混合索引 */
mulw u#1, t#2,         ->t             /* 双寄存器相对索引 */
mulw u#1, u#2,         ->t             /* 双寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
mulw a1, a2,           ->u             /* 双寄存器绝对索引 */
mulw a1, t#2,          ->u             /* 双寄存器混合索引 */
mulw a1, u#2,          ->u             /* 双寄存器混合索引 */
mulw t#1, a2,          ->u             /* 双寄存器混合索引 */
mulw t#1, t#2,         ->u             /* 双寄存器相对索引 */
mulw t#1, u#2,         ->u             /* 双寄存器相对索引 */
mulw u#1, a2,          ->u             /* 双寄存器混合索引 */
mulw u#1, t#2,         ->u             /* 双寄存器相对索引 */
mulw u#1, u#2,         ->u             /* 双寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
mulw a1, a2,           ->a3             /* 双寄存器绝对索引 */
mulw a1, t#2,          ->a3             /* 双寄存器混合索引 */
mulw a1, u#2,          ->a3             /* 双寄存器混合索引 */
mulw t#1, a2,          ->a3             /* 双寄存器混合索引 */
mulw t#1, t#2,         ->a3             /* 双寄存器相对索引 */
mulw t#1, u#2,         ->a3             /* 双寄存器相对索引 */
mulw u#1, a2,          ->a3             /* 双寄存器混合索引 */
mulw u#1, t#2,         ->a3             /* 双寄存器相对索引 */
mulw u#1, u#2,         ->a3             /* 双寄存器相对索引 */
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
