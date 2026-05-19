# 浮点块块头

浮点块块头通过`BSTART.FP`作为起始指令，其他块头指令根据需要进行补充。例如，如果指定块热度等信息，可以增加[B.HINT](./B.HINT.md)指令等。

为了兼顾程序代码量大小和长跳转偏移的情况，BSTART.FP提供了不同编码长度的定义，具体如下：

## 汇编语法

- 16-bit：` C.BSTART.FP BrType`
- 32-bit：`   BSTART.FP BrType<, label>`
- 48-bit：`HL.BSTART.FP BrType, label`
- 64-bit：` L.BSTART.FP BrType, label`

其中：

- 浮点块指令在汇编中通过 “.FP” 进行标识。
- **BrType**表示跳转类型。如果块指令是顺延的，那么可以省略“FALL”标识。
- **label**表示跳转目标位置的程序标签。

不同版本的`BSTART.FP`指令提供的跳转方式种类范围有所不同，具体见下表：

| 指令长度 | 支持跳转方式 |
|----------|-----------------|
| **16-bit** | fall, ind, icall, ret |
| **32-bit** | fall, direct, call, cond, ind, icall, ret |
| **48-bit** | fall, direct, call, cond |
| **64-bit** | fall, direct, call, cond |

## **编码格式**

### 16-bit编码

![C.BSTART.FP](../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART.FP.svg)

其中，BrType字段用于编码跳转方式。由于编码空间限制的原因无法表达跳转距离信息。因此该编码仅支持非偏移类跳转，编码方式如下：

| BrType | 跳转类型          | 解释                           |
|--------|-------------------|-------------------------------|
| 0      | invalid            | 无效                         |
| 1      | **FALL**           | 顺延(Fall Through)           |
| 2-4    | reserve            | 保留编码                      |
| 5      | **IND**            | 间接跳转(Indirect)            |
| 6      | **INDCALL**        | 间接调用(Indirect Call)       |
| 7      | **RET**            | 返回(Return)                  |

### 32-bit编码

![BSTART.FP](../../figs/bitfield/svg/Introduction_32bit/BSTART.FP.svg)

该编码支持**全量的跳转方式**。

### 48-bit编码

低16bit编码：

![BSTART.FP](../../figs/bitfield/svg/Instruction_48bit_16/HL.BSTART.FP.svg)

高32bit编码：

![BSTART.FP](../../figs/bitfield/svg/Instruction_48bit_32/HL.BSTART.FP.svg)

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

![L.BSTART.FP](../../figs/bitfield/svg/BlockHeader_64bit/L.BSTART.FP.svg)

64bit编码也只支持偏移类跳转方式，BrType字段编码方式同上。

## 跳转地址

对于FALL, DIRECT, CALL和COND等跳转方式，下个块的地址计算方式为：
```c
    // 跳转偏移
    bits(64) BNextOffset = simm << 1;     // simm为解码不同长度指令获得立即数值
    // 下个块的地址
    bits(64) NextBPC = BPC + BNextOffset;
```
