# 系统块块头

系统块块头通过`BSTART.SYS`作为起始指令，其他块头指令根据需要进行补充。例如，如果定义为原子块，那么块头中需要增加[B.CATR](./B.CATR.md)指令。如果指定块热度等信息，可以增加[B.HINT](./B.HINT.md)指令等。

为了兼顾程序代码量大小和长跳转偏移的情况，BSTART.SYS提供了不同编码长度的定义，具体如下：

## 汇编语法

- 16-bit：` C.BSTART.SYS FALL`
- 32-bit：`   BSTART.SYS FALL`
- 48-bit：`HL.BSTART.SYS FALL`
- 64-bit：` L.BSTART.SYS FALL`

其中：

- 系统块指令在汇编中通过 “.SYS” 进行标识。
- 系统块仅支持 **顺延-FALL** 类型，并且“FALL” 标识可以省略。

## **编码格式**

### 16-bit编码

![C.BSTART.SYS](../../figs/bitfield/svg/BlockHeader_16bit/C.BSTART.SYS.svg)

### 32-bit编码

![BSTART.SYS](../../figs/bitfield/svg/BlockHeader_32bit/BSTART.SYS.svg)

### 48-bit编码

低16bit编码：

![BSTART.SYS](../../figs/bitfield/svg/Instruction_48bit_16/HL.BSTART.SYS.svg)

高32bit编码：

![BSTART.SYS](../../figs/bitfield/svg/Instruction_48bit_32/HL.BSTART.SYS.svg)

### 64-bit编码

![L.BSTART.SYS](../../figs/bitfield/svg/BlockHeader_64bit/L.BSTART.SYS.svg)

## Fixup地址

系统块指令可支持Fixup跳转，跳转目标地址为：
```c
    // 跳转偏移
    bits(64) BNextOffset = simm << 1;     // simm为解码不同长度指令获得立即数值
    // 下个块的地址
    bits(64) NextBPC = BPC + BNextOffset;
```
