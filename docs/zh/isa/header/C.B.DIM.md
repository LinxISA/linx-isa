# C.B.DIM

## 说明

块维度信息(*Block Dimension*)<br>
本指令用于并行块块头中设置三层循环的上限值或者用于数据块块头中指定输入数据的维度信息。

## 汇编格式

```asm
    C.B.DIM RegSrc, ->{LB0, LB1, LB2}
    C.B.DIM imm,    ->{LB0, LB1, LB2}
```

- **RegSrc**：表示一个[全局寄存器](../register/common/ggpr.md)输入。
- **imm**：无符号立即数。
- **LB0/1/2**：目的寄存器，具体介绍请见[LANE寄存器](../register/common/loop.md)介绍。

每层维度可通过寄存器或立即数指定，通过寄存器指定时只有RegSrc的低16位有效。例如：

```c
    bits(64) result = RegSrc;
    LBx = result[15:0];   // x = 0 ,1 , 2
```

## 编码格式

- 立即数传参版本：

![C.B.DIMI](../../figs/bitfield/svg/BlockHeader_16bit/C.B.DIMI.svg)

- 寄存器传参版本：

![C.B.DIM](../../figs/bitfield/svg/BlockHeader_16bit/C.B.DIM.svg)

其中，LoopNest字段用于指示设置哪一层级的维度信息，编码方式如下：

| LoopNest | 循环层级/维度 |
|----------|---------|
| 0 | 最内层循环上限LB0 |
| 1 | 中间层循环上限LB1 |
| 2 | 最外层循环上限LB2 |

## 备注

本指令仅用于并行块块头中。
