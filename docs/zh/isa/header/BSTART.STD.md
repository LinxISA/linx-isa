# 标量块块头

标量块块头通过BSTART.STD作为起始指令，其他块头指令根据需要进行补充。为了兼顾程序代码量大小和长跳转偏移的情况，BSTART.STD提供了不同编码长度的定义，具体如下：

## 汇编语法

- 16-bit：` C.BSTART.STD BrType<, label>`
- 32-bit：`   BSTART.STD BrType<, label>`
- 48-bit：`HL.BSTART.STD BrType, label`
- 64-bit：` L.BSTART.STD BrType, label`

其中：

- 标量块指令的 “.STD” 标识可以省略。
- **BrType**表示跳转类型。如果块指令是顺延的，那么可以省略“FALL”标识。
- **label**表示跳转目标位置的程序标签。

不同版本的`BSATRT.STD`指令提供的跳转方式种类范围有所不同，具体见下表：

| 指令长度 | 支持跳转方式 |
|----------|-----------------|
| **16-bit** | fall, direct, call, cond, ind, icall, ret |
| **32-bit** | fall, direct, call, cond, ind, icall, ret |
| **48-bit** | fall, direct, call, cond |
| **64-bit** | fall, direct, call, cond |

## **编码格式**

### 16-bit编码

为了满足不同跳转方式的需要，16-bit的C.BSTART.STD指令有如下3种编码。

第一种编码如下：

![C.BSTART.STD](../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART.STD.svg)

其中，BrType字段用于编码跳转方式。由于编码空间限制的原因无法表达跳转距离信息。因此该编码仅支持非偏移类跳转，编码方式如下：

| BrType | 跳转类型          | 解释                           |
|--------|-------------------|-------------------------------|
| 0      | invalid            | 无效                         |
| 1      | **FALL**           | 顺延(Fall Through)           |
| 2-4    | reserve            | 保留编码                      |
| 5      | **IND**            | 间接跳转(Indirect)            |
| 6      | **INDCALL**        | 间接调用(Indirect Call)       |
| 7      | **RET**            | 返回(Return)                  |

另外，由于标量块在程序中出现热度较高，因此我们为标量块指令专门定义了两种编码，应用于需要分配较大编码空间的偏移类跳转的场景。这些编码通过缺省`块类型`和`跳转类型`的空间来表达跳转偏移，可以有效降低代码量并提升取指效率。

第二种编码如下：

![C.BSTART_1](../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART_1.svg)

该编码用于 **跳转类型为DIRECT或CALL** 的跳转方式。

第三种编码如下：

![C.BSTART_2](../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART_2.svg)

该编码用于 **跳转类型为COND** 的跳转方式。

### 32-bit编码

与16bit版本的设计逻辑相同，32-bit的BSTART.STD指令同样拥有3种编码。

第一种编码如下：

![BSTART.STD](../../figs/bitfield/svg/Introduction_32bit/BSTART.STD.svg)

该编码支持**全量的跳转方式**。

第二种编码如下：

![BSTART.STD](../../figs/bitfield/svg/BlockHeader_32bit/BSTART_1.svg)

该编码用于 **跳转类型为DIRECT或CALL** 的跳转方式。

第三种编码如下：

![BSTART.STD](../../figs/bitfield/svg/BlockHeader_32bit/BSTART_2.svg)

该编码用于 **跳转类型为COND** 的跳转方式。

### 48-bit编码

低16bit编码：

![HL.BSTART](../../figs/bitfield/svg/Instruction_48bit_16/HL.BSTART.STD.svg)

高32bit编码：

![HL.BSTART](../../figs/bitfield/svg/Instruction_48bit_32/HL.BSTART.STD.svg)

48bit编码只支持偏移类跳转方式，其中fall类型的跳转用于fixup处理。BrType字段编码方式如下：

| BrType | 跳转类型          | 解释                          |
|--------|-------------------|-------------------------------|
| 0      | invalid            | 无效                         |
| 1      | **FALL**           | 顺延(Fall through)，，用于支持[Fixup](../arch/fixup.md)处理的块    |
| 2      | **DIRECT**         | 直接跳转(Direct Branch)      |
| 3      | **COND**           | 条件跳转(Conditional Branch) |
| 4      | **CALL**           | 直接调用(Direct Call)        |
| 5,6,7  | reserve            | 保留                         |

### 64-bit编码

![L.BSTART.STD](../../figs/bitfield/svg/BlockHeader_64bit/L.BSTART.STD.svg)

64bit编码也只支持偏移类跳转方式，BrType字段编码方式同上。

## 跳转地址

对于FALL, DIRECT, CALL和COND等跳转方式，下个块的地址计算方式为：
```c
    // 跳转偏移
    bits(64) BNextOffset = simm << 1;     // simm为解码不同长度指令获得立即数值
    // 下个块的地址
    bits(64) NextBPC = BPC + BNextOffset;
```
