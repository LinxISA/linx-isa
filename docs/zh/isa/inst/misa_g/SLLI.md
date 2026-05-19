# SLLI

## 说明

立即数逻辑左移(*Shift Left Logical by Immediate*)  
左源操作数逻辑左移（低位补零，高位舍弃）**shamt** 位，结果写到目的寄存器中。

## 汇编语法

```
    slli SrcL, shamt, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **shamt**：对操作数左移位数，范围[0, 63]。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![SLLI](../../../figs/bitfield/svg/Instruction_32bit/SLLI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) operand = R[s, datawidth];
    bits(datawidth) result = operand << shamt;

    R[d, datawidth] = result;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
slli a1, uimm,           ->t             /* 单寄存器绝对索引 */
slli t#1, uimm,          ->t             /* 单寄存器相对索引 */
slli u#1, uimm,          ->t             /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
slli a1, uimm,           ->u             /* 单寄存器绝对索引 */
slli t#1, uimm,          ->u             /* 单寄存器相对索引 */
slli u#1, uimm,          ->u             /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
slli a1, uimm,           ->a3            /* 单寄存器绝对索引 */
slli t#1, uimm,          ->a3            /* 单寄存器相对索引 */
slli u#1, uimm,          ->a3            /* 单寄存器相对索引 */
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
