# SRLIW

## 说明

立即数逻辑右移字 (*Shift Right Logical by Immediate, Word*)  
左源操作数低 32 位逻辑右移（低位舍弃，高位补零）**shamt** 位，结果有符号扩展后写到目的寄存器中。

## 汇编语法

```
    srliw SrcL, shamt, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **shamt**：对操作数右移位数，范围[0, 31]。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![SRLIW](../../../figs/bitfield/svg/Instruction_32bit/SRLIW.svg)

## 执行方式

- 转换为十进制值：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) operand = R[s, datawidth];
    bits(datawidth) result = SignExtend(operand[31:0] >>(u) shamt);

    R[d, datawidth] = result;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
srliw a1, shamt,           ->t             /* 单寄存器绝对索引 */
srliw t#1, shamt,          ->t             /* 单寄存器相对索引 */
srliw u#1, shamt,          ->t             /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
srliw a1, shamt,           ->u             /* 单寄存器绝对索引 */
srliw t#1, shamt,          ->u             /* 单寄存器相对索引 */
srliw u#1, shamt,          ->u             /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
srliw a1, shamt,           ->a3            /* 单寄存器绝对索引 */
srliw t#1, shamt,          ->a3            /* 单寄存器相对索引 */
srliw u#1, shamt,          ->a3            /* 单寄存器相对索引 */
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
