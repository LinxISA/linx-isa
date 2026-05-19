# CSEL

## 说明

条件选择(*Conditional Select*)  
如果条件寄存器的值不等于0，选择将左源寄存器值写入到目的寄存器中；否则选择右源寄存器值写入。

## 汇编语法

```
    csel SrcP, SrcL, SrcR, ->{t, u, Rd}
```

## 汇编符号

- **SrcP**：条件寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **->**：用于指示目的寄存器。
- **{t,u,Rd}**：表示三种可选的目的寄存器，编码于RegDst域。其中：
    - **t,u**：分别表示块内的T和U寄存器队列。
    - **Rd**：可以索引全局寄存器R1-R23。

## 编码格式

![CSEL](../../../figs/bitfield/svg/Instruction_32bit/CSEL.svg)

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer p = UInt(SrcP);
    integer datawidth = 64;

    bits(datawidth) operand1 = R[m, datawidth];
    bits(datawidth) operand2 = R[n, datawidth];
    bits(datawidth) operand3 = R[p, datawidth];

    bits(datawidth) result = (operand3 != 0 ? operand1 : operand2);

    R[d, datawidth] = result;
```

## 汇编索引模式

指令输出到块内t寄存器:
```asm
csel a1, a2, a3,          ->t                 /* 三寄存器绝对索引 */
csel a1, t#2, u#3,        ->t                 /* 三寄存器混合索引 */
csel a1, u#2, t#3,        ->t                 /* 三寄存器混合索引 */
csel t#1, a2, u#3,        ->t                 /* 三寄存器混合索引 */
csel t#1, u#2, a3,        ->t                 /* 三寄存器混合索引 */
csel t#1, t#2, t#3,       ->t                 /* 三寄存器相对索引 */
csel u#1, a2, t#3,        ->t                 /* 三寄存器混合索引 */
csel u#1, t#2, a3,        ->t                 /* 三寄存器混合索引 */
csel u#1, u#2, u#3,       ->t                 /* 三寄存器相对索引 */
```

指令输出到块内u寄存器：
```asm
csel a1, a2, a3,          ->u                 /* 三寄存器绝对索引 */
csel a1, t#2, u#3,        ->u                 /* 三寄存器混合索引 */
csel a1, u#2, t#3,        ->u                 /* 三寄存器混合索引 */
csel t#1, a2, u#3,        ->u                 /* 三寄存器混合索引 */
csel t#1, u#2, a3,        ->u                 /* 三寄存器混合索引 */
csel t#1, t#2, t#3,       ->u                 /* 三寄存器相对索引 */
csel u#1, a2, t#3,        ->u                 /* 三寄存器混合索引 */
csel u#1, t#2, a3,        ->u                 /* 三寄存器混合索引 */
csel u#1, u#2, u#3,       ->u                 /* 三寄存器相对索引 */
```

指令输出到全局寄存器R1-R23：
```asm
csel a1, a2, a3,          ->a4                 /* 三寄存器绝对索引 */
csel a1, t#2, u#3,        ->a4                 /* 三寄存器混合索引 */
csel a1, u#2, t#3,        ->a4                 /* 三寄存器混合索引 */
csel t#1, a2, u#3,        ->a4                 /* 三寄存器混合索引 */
csel t#1, u#2, a3,        ->a4                 /* 三寄存器混合索引 */
csel t#1, t#2, t#3,       ->a4                 /* 三寄存器相对索引 */
csel u#1, a2, t#3,        ->a4                 /* 三寄存器混合索引 */
csel u#1, t#2, a3,        ->a4                 /* 三寄存器混合索引 */
csel u#1, u#2, u#3,       ->a4                 /* 三寄存器相对索引 */
```

## 汇编示例

该指令提供了一种较好的方法来避免使用分支或有条件执行的指令。编译器或汇编程序员可以为`if-then-else`语句的两个分支执行操作，然后在最后选择正确的结果。

以下面的C代码为例：
```c
    if (i == 0)
        r = r + 2;
    else
        r = r - 1;
```
这可以生成类似于以下代码：
```
    cmp.eqi a0, 0, ->t      /* if (i == 0) */
    addi a1, 2, ->t         /* r = r + 2 */
    subi a1, 1, ->t         /* r = r - 1 */
    csel t#3, t#2, t#1      /* 根据比较情况在两种结果之间选择 */
```

## 硬件实现建议

对于任何一条csel指令建议如下:

```asm
    csel SrcP, SrcL, SrcR, ->RegDst
```
将其拆成3条指令：
```asm
    cmask SrcP, SrcL, 0, ->m    # SrcP非零，选择SrcL写入m；否则写入0。
    cmask ~SrcP, SrcR, 0, ->m   # SrcP为零，选择SrcR写入m；否则写入0。
    or m#1, m#2, ->RegDst
```
注：m为微架构内部的hand，软件不可见。

## 备注

本指令属于[基础指令扩展](../../instset/baseExtInstrs.md)，可用于任意类型的块指令块体中。
