# CMP.GEUI

## 说明

立即数大于等于无符号比较(*Compare with Immediate if Greater than or Equal by Unsigned*)  
无符号比较源操作数和立即数，如果源操作数大于等于立即数则结果为1，否则为0，结果写到目的寄存器中。

## 汇编语法

```
    cmp.geui SrcL, uimm, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **uimm**：12位无符号立即数，编码于uimm12字段。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![CMP.GEUI](../../../figs/bitfield/svg/Instruction_32bit/CMP.GEUI.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) operand = R[s, datawidth];
    bits(datawidth) uimm = ZeroExtend(uimm12);

    bits(datawidth) result = (operand >=(u) uimm ? 1 : 0);
    R[d, datawidth] = result;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
cmp.geui a1, uimm,           ->t             /* 单寄存器绝对索引 */
cmp.geui t#1, uimm,          ->t             /* 单寄存器相对索引 */
cmp.geui u#1, uimm,          ->t             /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
cmp.geui a1, uimm,           ->u             /* 单寄存器绝对索引 */
cmp.geui t#1, uimm,          ->u             /* 单寄存器相对索引 */
cmp.geui u#1, uimm,          ->u             /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
cmp.geui a1, uimm,           ->a3            /* 单寄存器绝对索引 */
cmp.geui t#1, uimm,          ->a3            /* 单寄存器相对索引 */
cmp.geui u#1, uimm,          ->a3            /* 单寄存器相对索引 */
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
