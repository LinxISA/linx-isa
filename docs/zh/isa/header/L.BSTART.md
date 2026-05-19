# L.BSTART

64位长度的L.BSTART指令在支持[超长指令扩展](../instset/longInstrs.md)的处理器中允许使用，相比标准版本的[BSTART](./BSTART.md)以及增强版本的[HL.BSTART](./HL.BSTART.md)提供更大范围的跳转距离，因此可用于更长距离的跳转场景。

## 汇编语法

```asm
    L.BSTART<.BlockType> BrType, label
```

其中：

- **BlockType**：该参数代表块类型，如果是标量块，则可缺省`.STD`标识。
- **BrType**：该参数代表块指令的跳转方式，可选类型包括3种偏移类跳转。
- **label**：该参数代表跳转目标位置的标签，其相对于本指令的偏移距离除以2后编码于simm[42:1]字段。

L.BSTART指令支持的块类型和跳转方式见下表：

| BlockType | 支持的BrType | 
|------------|-------------|
| STD  | fall, direct, call, cond |
| SYS  | fall, direct, call, cond |
| FP   | fall, direct, call, cond |

## 编码格式

**BlockType** 字段用于指示执行该块指令的引擎类型，具体编码如下：

| BlockType | 块类型              | 汇编标识  |
|-----------|---------------------|-----------|
| 0         | Standard Block       | .STD      |
| 1         | System Block         | .SYS      |
| 2         | Floating-point Block | .FP       |
| 3-15      | RESERVE              | RESERVE   |

**BrType** 字段描述了当前块的跳转方式，决定了如何从当前块跳转到下一个块。具体编码如下：

| BrType | 跳转类型          | 解释                          |
|--------|-------------------|-------------------------------|
| 0      | invalid            | 无效                         |
| 1      | **fall**           | 顺延(Fall through)，，用于支持[Fixup](../arch/fixup.md)处理的块    |
| 2      | **direct**         | 直接跳转(Direct Branch)      |
| 3      | **cond**           | 条件跳转(Conditional Branch) |
| 4      | **call**           | 直接调用(Direct Call)        |
| 5,6,7  | reserve            | 保留                         |

## 汇编示例

```asm
    L.BSTART.STD direct, 0x00ff
    L.BSTART.SYS call,   0x01ef
    L.BSTART.FP  cond,   0x1234
```
