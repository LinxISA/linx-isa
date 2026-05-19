# L.FCLASS

## 说明

浮点数类别判断(*Floating-point Category Classification*)<br>
对源寄存器的浮点数进行类别判断，所得判断结果由10比特信息组成，每比特的含义如下表所示，当被判断的数据符合某个比特对应的条件时，结果信息向量的对应比特就会被置为1，最后将结果写入目的寄存器。

<table border="2" align="center">
<caption>信息向量</caption>
    <tr>
        <th>Bit0</th>
        <th>Bit1</th>
        <th>Bit2</th>
        <th>Bit3</th>
        <th>Bit4</th>
        <th>Bit5</th>
        <th>Bit6</th>
        <th>Bit7</th>
        <th>Bit8</th>
        <th>Bit9</th>
    </tr>
    <tr>
        <td rowspan="2">SNaN</td>
        <td rowspan="2">QNaN</td>
        <td colspan="4">negative value</td>
        <td colspan="4">positive value</td>
    </tr>
    <tr>
        <td>inf</td>
        <td>normal</td>
        <td>subnormal</td>
        <td>0</td>
        <td>inf</td>
        <td>normal</td>
        <td>subnormal</td>
        <td>0</td>
    </tr>
</table>

## 汇编语法

```asm
    l.fclass SrcL.<T>, ->RegDst.d
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引的寄存器类型请见[长指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **T**：指定操作数的数据类型，可选类型包括fb, fh, fs, fd等。
- **->**：用于指示目的寄存器。
- **RegDst**: 目的寄存器，可以索引T/U或P类型标量寄存器。目的寄存器固定为16bit。
- **.d**：目的寄存器的位宽标识（d表示64-bit）。

## 编码格式

![L.FCLASS](../../../figs/bitfield/svg/Instruction_64bit/L.FCLASS.svg)

## 执行方式

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 标量寄存器读写：[SREG\[\]](../LibPseudoCode.md#locationB)
- 判断浮点类型：[FP_Class()](../LibPseudoCode.md#locationO)

```c

    integer {m, srcWidth} = DecodeFP(SrcL);
    integer {d, dstWidth} = DecodeDst(RegDst); 

    bits(srcWidth) operand = SREG[m, srcWidth];
    
    bits(64) result;
    (fptype, sign) = FP_Class(operand);

    when fptype == FP_SNaN                   : result[0] = 1;
    when fptype == FP_QNaN                   : result[1] = 1;
    when fptype == FP_INF       && sign == 0 : result[2] = 1;
    when fptype == FP_Normal    && sign == 0 : result[3] = 1;
    when fptype == FP_Subnormal && sign == 0 : result[4] = 1;
    when fptype == FP_Zero      && sign == 0 : result[5] = 1;
    when fptype == FP_INF       && sign == 1 : result[6] = 1;
    when fptype == FP_Normal    && sign == 1 : result[7] = 1;
    when fptype == FP_Subnormal && sign == 1 : result[8] = 1;
    when fptype == FP_Zero      && sign == 1 : result[9] = 1;

    SREG[d, dstWidth] = result;
```

## 备注

1. 本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块的块体内。
2. 本指令的向量版本请见[V.FCLASS](../misa_v/V.FCLASS.md)。
