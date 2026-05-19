# SETC.ANDI

## 说明

立即数与置位提交(*Set Commit Argument by And Immediate*)  
如果源操作数和有符号立即数执行按位与的结果为非0，在本块指令提交时，跳转到指定BPC。

## 汇编语法

```
    setc.andi SrcL, simm
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **simm**：有符号立即数，可使用[-2048, 2047]左移0至31位范围内的数。该参数编码于simm12和shamt字段。

## 编码格式

![SETC.ANDI](../../../figs/bitfield/svg/Instruction_32bit/SETC.ANDI.svg)

其中，simm12和shamt共同编码立即数，shamt用于编码simm12左移的位数。

| simm12 | shamt |  立即数范围  |
|--------|-------|-----------------------------|
| [-2048, 2047] | 0 | [-2048, 2047] |
| [-2048, 2047] | 1 | [-2048, 2047]<<1 |
| ... | ... | ... |
| [-2048, 2047] | n | [-2048, 2047]<<n |
| ... | ... | ... |
| [-2048, 2047] | 31 | [-2048, 2047]<<31 |

## 执行方式

- 转换为十进制数：[UInt()](../LibPseudoCode.md)
- 通用寄存器读写：[R\[\]](../LibPseudoCode.md)
- 对数据符号扩展：[SignExtend()](../LibPseudoCode.md)

```c
    integer d = UInt(RegDst);
    integer s = UInt(SrcL);
    integer datawidth = 64;

    bits(datawidth) operand = R[s, datawidth];
    bits(datawidth) simm = SignExtend(simm12);
    bits(datawidth) result = operand & (simm << shamt);

    BARG.TAKEN = (result != 0 ? 1 : 0);
```


## 汇编索引模式

```asm
setc.andi a1, simm     /* 单寄存器绝对索引 */
setc.andi t#1, simm    /* 单寄存器相对索引 */
setc.andi u#1, simm    /* 单寄存器相对索引 */
```

## 注意事项

1. 本指令不占块内私有寄存器槽位。
2. 本指令在一个块内只能执行一次。
3. 本指令仅在条件跳转COND块内有效。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
