# C.BSTART

16位长度的C.BSTART指令在支持压缩扩展的处理器中允许使用，可以有效降低块指令间近距离跳转以及非偏移类跳转场景下的代码字长。

有三种C.BSTART指令提供给用户选择：

- 第一种可以用于不同类型的块，但是只支持非偏移类跳转。
- 第二种仅用于标量块且跳转方式只能是DIRECT或CALL类型的。
- 第三种仅用于标量块且跳转方式只能是COND类型的。

## 汇编语法

```asm
    C.BSTART<.BlockType> BrType           
    C.BSTART<.STD> {direct, call}, label
    C.BSTART<.STD> cond, label
```

其中：

- **BlockType**：该参数代表块类型，如果是标量块，则可缺省`.STD`标识。
- **BrType**：该参数代表块指令的跳转方式，根据块类型不同可选类型也不同，具体见下表。
- **label**：该参数代表跳转目标位置的标签，其相对于本指令的偏移距离除以2后编码于simm12字段。

| BlockType | 支持的BrType | 
|------------|-------------|
| 标量块（.STD）  | fall, ind, icall, ret |
| 系统块（.SYS）  | fall, ind, icall, ret |
| 浮点块（.FP）   | fall, ind, icall, ret |
| 并行块（.PAR）  | fall  |

## 编码格式

第一种C.BSTART编码:

![C.BSTART.COM](../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART.svg)

- **BlockType 域**

BlockType 用于指示执行该块指令的引擎类型，具体编码如下：

| BlockType | 块类型              | 汇编标识  |
|-----------|---------------------|-----------|
| 0         | Standard Block       | .STD      |
| 1         | System Block         | .SYS      |
| 2         | Floating-point Block | .FP       |
| 3         | Parallel Block       | .PAR     |
| 4-15      | RESERVE              | RESERVE   |

- **BrType 域**

BrType 描述了当前块的跳转方式，决定了如何从当前块跳转到下一个块。具体编码如下：

| BrType | 跳转类型          | 解释                          |
|--------|-------------------|-------------------------------|
| 0      | invalid            | 无效                         |
| 1      | **fall**           | 顺延(Fall Through)           |
| 2,3,4  | invalid            | 无效                         |
| 5      | **ind**            | 间接跳转(Indirect)           |
| 6      | **icall**          | 间接调用(Indirect Call)      |
| 7      | **ret**            | 返回(Return)                 |

第二种C.BSTART编码:

![C.BSTART.DIRECT](../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART_1.svg)

第三种C.BSTART编码:

![C.BSTART.COND](../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART_2.svg)

## 汇编示例

```asm
    C.BSTART.STD direct, 0x00ff
    C.BSTART.STD call, 0x01ef
    C.BSTART.SYS ind
    C.BSTART.SYS icall
    C.BSTART.FP  ret
```
