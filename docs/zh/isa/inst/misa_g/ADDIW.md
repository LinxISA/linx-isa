# ADDIW

## 说明

加立即数·字(*Add Word Immediate*)  
将寄存器值和无符号立即数相加，结果的`低32位`有符号扩展后写到目的寄存器中。

## 汇编语法

```
    addiw SrcL, uimm, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **uimm**：12位无符号立即数，编码于uimm12域。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![ADDIW](../../../figs/bitfield/svg/Instruction_32bit/ADDIW.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) operand = R[s, datawidth];
    bits(datawidth) uimm = ZeroExtend(uimm12);
    bits(datawidth) result = SignExtend((operand + uimm)[31:0]);

    R[d, datawidth] = result;
```


## 汇编索引模式

指令输出到块内t寄存器:
```asm
addiw a1, uimm,           ->t             /* 单寄存器绝对索引 */
addiw t#1, uimm,          ->t             /* 单寄存器相对索引 */
addiw u#1, uimm,          ->t             /* 单寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
addiw a1, uimm,           ->u             /* 单寄存器绝对索引 */
addiw t#1, uimm,          ->u             /* 单寄存器相对索引 */
addiw u#1, uimm,          ->u             /* 单寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
addiw a1, uimm,           ->a3            /* 单寄存器绝对索引 */
addiw t#1, uimm,          ->a3            /* 单寄存器相对索引 */
addiw u#1, uimm,          ->a3            /* 单寄存器相对索引 */
```

## 注意事项

1. 如果结果溢出，则舍弃额外的位。
2. 带进位的场景可使用[ADDI](./ADDI.md)指令。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
