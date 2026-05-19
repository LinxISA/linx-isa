# SETC.GEUI

## 说明

立即数大于等于置位提交(*Set Commit Argument if Greater than or Equal, Unsigned Immediate*)  
无符号比较源操作数和立即数，如果源操作数大于等于立即数，在本块指令提交时，跳转到指定BPC。

## 汇编语法

```
    setc.geui SrcL, uimm
```

## 汇编符号

- **SrcL**：源寄存器，可以索引全局寄存器R0-R23和前序1-4条输出至T队列或U队列的指令结果。
- **uimm**：无符号立即数，可使用[0, 4095]左移0至31位范围内的数。该参数编码于uimm12和shamt字段。

## 编码格式

![SETC.GEUI](../../../figs/bitfield/svg/Instruction_32bit/SETC.GEUI.svg)

其中，uimm12和shamt共同编码立即数，shamt用于编码uimm12左移的位数。

| uimm12 | shamt |  立即数范围  |
|--------|-------|---------------|
| [0, 4095] | 0 | [0, 4095] |
| [0, 4095] | 1 | [0, 4095]<<1 |
| ... | ... | ... |
| [0, 4095] | n | [0, 4095]<<n |
| ... | ... | ... |
| [0, 4095] | 31 | [0, 4095]<<31 |

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
    uimm = uimm << shamt;
    BARG.TAKEN = (operand >=(u) uimm ? 1 : 0);
```

## 汇编索引模式

```asm
setc.geui a1, uimm   /* 单寄存器绝对索引 */
setc.geui t#1, uimm  /* 单寄存器相对索引 */
setc.geui u#1, uimm  /* 单寄存器相对索引 */
```

## 注意事项

1. 本指令不占块内私有寄存器槽位。
2. 本指令在一个块内只能执行一次。
3. 本指令仅在条件跳转COND块内有效。

## 备注

本指令属于[基础指令集](../../instset/baseInstrs.md)，可用于任意类型的块指令块体中。
