# REMUW

## 说明

无符号余数·字(*Remainder Word, Unsigned*)  
无符号计算左源操作数`低32位`除以右源操作数`低32位`，向 0 舍入，余数符号位扩展后写入目的寄存器中。

## 汇编语法

```
    remuw SrcL, SrcR, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![REMUW](../../../figs/bitfield/svg/Instruction_32bit/REMUW.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 32;

    bits(datawidth) operand1 = R[m, datawidth];
    bits(datawidth) operand2 = R[n, datawidth];
    bits(datawidth) result;

    if operand2 != 0 then
        result = operand1 %(u) operand2;
    else
        result = operand1;

    R[d, datawidth] = SignExtend(result[31:0]);
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
remuw a1, a2,           ->t             /* 双寄存器绝对索引 */
remuw a1, t#2,          ->t             /* 双寄存器混合索引 */
remuw a1, u#2,          ->t             /* 双寄存器混合索引 */
remuw t#1, a2,          ->t             /* 双寄存器混合索引 */
remuw t#1, t#2,         ->t             /* 双寄存器相对索引 */
remuw t#1, u#2,         ->t             /* 双寄存器相对索引 */
remuw u#1, a2,          ->t             /* 双寄存器混合索引 */
remuw u#1, t#2,         ->t             /* 双寄存器相对索引 */
remuw u#1, u#2,         ->t             /* 双寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
remuw a1, a2,           ->u             /* 双寄存器绝对索引 */
remuw a1, t#2,          ->u             /* 双寄存器混合索引 */
remuw a1, u#2,          ->u             /* 双寄存器混合索引 */
remuw t#1, a2,          ->u             /* 双寄存器混合索引 */
remuw t#1, t#2,         ->u             /* 双寄存器相对索引 */
remuw t#1, u#2,         ->u             /* 双寄存器相对索引 */
remuw u#1, a2,          ->u             /* 双寄存器混合索引 */
remuw u#1, t#2,         ->u             /* 双寄存器相对索引 */
remuw u#1, u#2,         ->u             /* 双寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
remuw a1, a2,           ->a3             /* 双寄存器绝对索引 */
remuw a1, t#2,          ->a3             /* 双寄存器混合索引 */
remuw a1, u#2,          ->a3             /* 双寄存器混合索引 */
remuw t#1, a2,          ->a3             /* 双寄存器混合索引 */
remuw t#1, t#2,         ->a3             /* 双寄存器相对索引 */
remuw t#1, u#2,         ->a3             /* 双寄存器相对索引 */
remuw u#1, a2,          ->a3             /* 双寄存器混合索引 */
remuw u#1, t#2,         ->a3             /* 双寄存器相对索引 */
remuw u#1, u#2,         ->a3             /* 双寄存器相对索引 */
```

!!! note "注意"

    如果出现除以零的情况，余数等于被除数，且不会触发异常。

## 备注

本指令属于[基础指令扩展](../../instset/baseExtInstrs.md)，可用于任意类型的块指令块体中。
