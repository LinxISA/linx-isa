# SETC.NE

## 说明

不等时置位提交(*Set Commit Argument if Not Equal*)  
如果左源操作数不等于右源操作数，在本块指令提交时，跳转到指定BPC。

## 汇编语法

```
    setc.ne SrcL, SrcR<{.sw, .uw}>
```

## 汇编符号

- **SrcL**：左源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **SrcR**：右源寄存器，索引范围同SrcL。SrcR可以选择带后缀，分别表示：
    - **.sw**：截取操作数低32bit做符号扩展。
    - **.uw**：截取操作数低32bit做无符号扩展。

## 编码格式

![SETC.NE](../../../figs/bitfield/svg/Instruction_32bit/SETC.NE.svg)

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
    integer m = UInt(SrcL);
    integer n = UInt(SrcR);
    integer DataWidth = 64;

    bits(DataWidth) operand1 = R[m, DataWidth];
    bits(DataWidth) operand2 = R[n, DataWidth];

    case SrcRType of:
        when 2b00 then No operation;
        when 2b01 then operand2 = SignExtend(operand2[31:0]);
        when 2b10 then operand2 = ZeroExtend(operand2[31:0]);
        when 2b11 then undefined;
    
    BARG.TAKEN = (operand1 != operand2 ? 1 : 0);
```

## 汇编索引模式

```asm
setc.ne a1, a2,       /* 双寄存器绝对索引 */
setc.ne a1, t#2,      /* 双寄存器混合索引 */
setc.ne a1, u#2,      /* 双寄存器混合索引 */
setc.ne t#1, a2,      /* 双寄存器混合索引 */
setc.ne t#1, t#2,     /* 双寄存器相对索引 */
setc.ne t#1, u#2,     /* 双寄存器相对索引 */
setc.ne u#1, a2,      /* 双寄存器混合索引 */
setc.ne u#1, t#2,     /* 双寄存器相对索引 */
setc.ne u#1, u#2,     /* 双寄存器相对索引 */
setc.ne a1, a2.sw,    /* SrcR寄存器格式转换，可使用sw,uw */
setc.ne a1, t#2.sw,   /* SrcR寄存器格式转换，可使用sw,uw */
setc.ne a1, u#2.sw,   /* SrcR寄存器格式转换，可使用sw,uw */
```

## 注意事项

1. 本指令不占块内私有寄存器槽位。
2. 本指令在一个块内只能执行一次。
3. 本指令仅在条件跳转COND块内有效。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
