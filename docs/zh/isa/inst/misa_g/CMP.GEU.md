# CMP.GEU

## 说明

大于等于无符号比较(*Compare if Greater than or Equal by Unsigned*)  
首先可以有选择的对右源操作数 **截取低32位有符号或无符号扩展**，然后无符号比较左源操作数和右源操作数。如果左源操作数大于等于右源操作数则结果为1，否则为0，将结果写入目的寄存器。

## 汇编语法

```
    cmp.geu SrcL, SrcR<{.sw, .uw}>, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，索引范围同SrcL。SrcR可以选择带后缀，分别表示：
    - **.sw**：截取操作数低32bit做符号扩展。
    - **.uw**：截取操作数低32bit做无符号扩展。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![CMP.GEU](../../../figs/bitfield/svg/Instruction_32bit/CMP.GEU.svg)

其中，SrcRType域编码如下：

|  SrcRType  |  汇编标识  |  解释                       |
|-----------|-----------|-----------------------------|
|  00  |   无   |  无格式转换   |
|  01  |  .sw   |  signed extended word，截取操作数的低32bit做有符号扩展  |
|  10  |  .uw   |  unsigned extended word，截取操作数的低32bit做无符号扩展  |
|  11  |  reserve  |  保留  |

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 64;

    bits(datawidth) operand1 = R[m, datawidth];
    bits(datawidth) operand2 = R[n, datawidth];

    case SrcRType of:
        when 2b00 then No operation;
        when 2b01 then operand2 = SignExtend(operand2[31:0]);
        when 2b10 then operand2 = ZeroExtend(operand2[31:0]);
        when 2b11 then undefined;

    bits(datawidth) result = (operand1 >=(u) operand2 ? 1 : 0);
    R[d, datawidth] = result;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
cmp.geu a1, a2,           ->t             /* 双寄存器绝对索引 */
cmp.geu a1, t#2,          ->t             /* 双寄存器混合索引 */
cmp.geu a1, u#2,          ->t             /* 双寄存器混合索引 */
cmp.geu t#1, a2,          ->t             /* 双寄存器混合索引 */
cmp.geu t#1, t#2,         ->t             /* 双寄存器相对索引 */
cmp.geu t#1, u#2,         ->t             /* 双寄存器相对索引 */
cmp.geu u#1, a2,          ->t             /* 双寄存器混合索引 */
cmp.geu u#1, t#2,         ->t             /* 双寄存器相对索引 */
cmp.geu u#1, u#2,         ->t             /* 双寄存器相对索引 */
cmp.geu a1, a2.sw,        ->t             /* SrcR寄存器格式转换，可使用sw,uw */
cmp.geu a1, t#2.sw,       ->t             /* SrcR寄存器格式转换，可使用sw,uw */
cmp.geu a1, u#2.sw,       ->t             /* SrcR寄存器格式转换，可使用sw,uw */
```

指令输出到块内u寄存器：
```asm
cmp.geu a1, a2,           ->u             /* 双寄存器绝对索引 */
cmp.geu a1, t#2,          ->u             /* 双寄存器混合索引 */
cmp.geu a1, u#2,          ->u             /* 双寄存器混合索引 */
cmp.geu t#1, a2,          ->u             /* 双寄存器混合索引 */
cmp.geu t#1, t#2,         ->u             /* 双寄存器相对索引 */
cmp.geu t#1, u#2,         ->u             /* 双寄存器相对索引 */
cmp.geu u#1, a2,          ->u             /* 双寄存器混合索引 */
cmp.geu u#1, t#2,         ->u             /* 双寄存器相对索引 */
cmp.geu u#1, u#2,         ->u             /* 双寄存器相对索引 */
cmp.geu a1, a2.sw,        ->u             /* SrcR寄存器格式转换，可使用sw,uw */
cmp.geu a1, t#2.sw,       ->u             /* SrcR寄存器格式转换，可使用sw,uw */
cmp.geu a1, u#2.sw,       ->u             /* SrcR寄存器格式转换，可使用sw,uw */
```

指令输出到全局寄存器R1-R23：
```asm
cmp.geu a1, a2,           ->a3             /* 双寄存器绝对索引 */
cmp.geu a1, t#2,          ->a3             /* 双寄存器混合索引 */
cmp.geu a1, u#2,          ->a3             /* 双寄存器混合索引 */
cmp.geu t#1, a2,          ->a3             /* 双寄存器混合索引 */
cmp.geu t#1, t#2,         ->a3             /* 双寄存器相对索引 */
cmp.geu t#1, u#2,         ->a3             /* 双寄存器相对索引 */
cmp.geu u#1, a2,          ->a3             /* 双寄存器混合索引 */
cmp.geu u#1, t#2,         ->a3             /* 双寄存器相对索引 */
cmp.geu u#1, u#2,         ->a3             /* 双寄存器相对索引 */
cmp.geu a1, a2.sw,        ->a3             /* SrcR寄存器格式转换，可使用sw,uw */
cmp.geu a1, t#2.sw,       ->a3             /* SrcR寄存器格式转换，可使用sw,uw */
cmp.geu a1, u#2.sw,       ->a3             /* SrcR寄存器格式转换，可使用sw,uw */
```

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
