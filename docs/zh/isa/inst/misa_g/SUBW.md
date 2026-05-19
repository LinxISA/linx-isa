# SUBW

## 说明

减字(*Substract Word*)  
首先可以有选择的对右源操作数 **截取低32位有符号或无符号扩展** 或 **按位取反加一**，接着左移 **shamt** 位。然后用左源操作数减去右源操作数，结果的`低32位`有符号扩展后写到目的寄存器中。

## 汇编语法

```
    subw SrcL, SrcR<{.sw,.uw,.neg}><<<shamt>, ->{t, u, Rd}
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，索引范围同SrcL。SrcR可以选择带后缀，分别表示：
    - **.sw**：截取右源操作数低32bit做符号扩展。
    - **.uw**：截取右源操作数低32bit做无符号扩展。
    - **.neg**：将右源操作数按位取反加一。
    - **shamt**：表示右源操作数逻辑左移位数，范围[0, 31]。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![SUBW](../../../figs/bitfield/svg/Instruction_32bit/SUBW.svg)

其中，SrcRType域编码如下：

|  SrcRType  |  汇编标识  |  解释                       |
|-----------|-----------|-----------------------------|
|  00  |   无   |  无格式转换                        |
|  01  |  .sw   |  signed extended word，截取操作数的低32bit做有符号扩展  |
|  10  |  .uw   |  unsigned extended word，截取操作数的低32bit做无符号扩展  |
|  11  |  .neg  |  negative，将操作数位取反加一  |

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)
- 对数据零扩展：[ZeroExtend()](../LibPseudoCode.md)
- 对操作数位取反加一：[Negative()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer datawidth = 64;

    bits(datawidth) operand1 = R[m, datawidth];
    bits(datawidth) operand2 = R[n, datawidth];

    case SrcRType of
        when 2b00 then No operation;
        when 2b01 then operand2 = SignExtend(operand2[31:0]);
        when 2b10 then operand2 = ZeroExtend(operand2[31:0]);
        when 2b11 then operand2 = Negative(operand2);

    bits(datawidth) result = operand1 - (operand2 << shamt);
    bits(datawidth) result = SignExtend(result[31:0]);
    
    R[d, datawidth] = result;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
subw a1, a2,           ->t             /* 双寄存器绝对索引 */
subw a1, t#2,          ->t             /* 双寄存器混合索引 */
subw a1, u#2,          ->t             /* 双寄存器混合索引 */
subw t#1, a2,          ->t             /* 双寄存器混合索引 */
subw t#1, t#2,         ->t             /* 双寄存器相对索引 */
subw t#1, u#2,         ->t             /* 双寄存器相对索引 */
subw u#1, a2,          ->t             /* 双寄存器混合索引 */
subw u#1, t#2,         ->t             /* 双寄存器相对索引 */
subw u#1, u#2,         ->t             /* 双寄存器相对索引 */
subw a1, a2.sw,        ->t             /* SrcR寄存器格式转换，可使用sw,uw,neg */
subw a1, t#2<<2,       ->t             /* SrcR寄存器左移，支持左移0-31位 */
subw a1, u#2.sw<<3,    ->t             /* SrcR寄存器格式转换并左移 */
```

指令输出到块内u寄存器：
```asm
subw a1, a2,           ->u             /* 双寄存器绝对索引 */
subw a1, t#2,          ->u             /* 双寄存器混合索引 */
subw a1, u#2,          ->u             /* 双寄存器混合索引 */
subw t#1, a2,          ->u             /* 双寄存器混合索引 */
subw t#1, t#2,         ->u             /* 双寄存器相对索引 */
subw t#1, u#2,         ->u             /* 双寄存器相对索引 */
subw u#1, a2,          ->u             /* 双寄存器混合索引 */
subw u#1, t#2,         ->u             /* 双寄存器相对索引 */
subw u#1, u#2,         ->u             /* 双寄存器相对索引 */
subw a1, a2.sw,        ->u             /* SrcR寄存器格式转换，可使用sw,uw,neg */
subw a1, t#2<<2,       ->u             /* SrcR寄存器左移，支持左移0-31位 */
subw a1, u#2.sw<<3,    ->u             /* SrcR寄存器格式转换并左移 */
```

指令输出到全局寄存器R1-R23：
```asm
subw a1, a2,           ->a3             /* 双寄存器绝对索引 */
subw a1, t#2,          ->a3             /* 双寄存器混合索引 */
subw a1, u#2,          ->a3             /* 双寄存器混合索引 */
subw t#1, a2,          ->a3             /* 双寄存器混合索引 */
subw t#1, t#2,         ->a3             /* 双寄存器相对索引 */
subw t#1, u#2,         ->a3             /* 双寄存器相对索引 */
subw u#1, a2,          ->a3             /* 双寄存器混合索引 */
subw u#1, t#2,         ->a3             /* 双寄存器相对索引 */
subw u#1, u#2,         ->a3             /* 双寄存器相对索引 */
subw a1, a2.sw,        ->a3             /* SrcR寄存器格式转换，可使用sw,uw,neg */
subw a1, t#2<<2,       ->a3             /* SrcR寄存器左移，支持左移0-31位 */
subw a1, u#2.sw<<3,    ->a3             /* SrcR寄存器格式转换并左移 */
```

## 注意事项

1. 结果忽略算数溢出。
2. 如果需要保留算数溢出，则可以使用[SUB](./SUB.md)指令代替。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
