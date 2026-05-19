# B.DIM

## 说明

**块维度（Block Dimension）**

`B.DIM` 用于设置块指令块体执行的维度信息。其中包括：

- [访存数据块](../blockIntro/vec_block/header.md)或[向量数据块](../blockIntro/mem_block/intro.md)的块头中设置块体迭代的三层循环的上限值。
- 用于其他数据块块头中指定输入数据的行或列等维度信息。

## 汇编格式

```asm
    B.DIM RegSrc, imm, ->{LB0, LB1, LB2}
```

## 汇编符号

- **RegSrc**：表示一个[全局寄存器](../register/common/ggpr.md)输入。
- **imm**：无符号立即数。
- **LB0/1/2**：目的寄存器，具体介绍请见[LANE寄存器](../register/common/loop.md)介绍。

每层维度值通过 “寄存器加立即数” 计算得到，并且只有结果的低16位有效。例如：

```c
    bits(64) result = RegSrc + imm;
    LBx = result[15:0];   // x = 0 ,1 , 2
```

## 编码格式

![B.DIM](../../figs/bitfield/svg/BlockHeader_32bit/B.DIM.svg)

其中，LoopNest字段用于指示设置哪一层级的维度信息，编码方式如下：

| LoopNest | 目的寄存器 |
|----------|---------|
| 0 | 最内层循环上限LB0 |
| 1 | 中间层循环上限LB1 |
| 2 | 最外层循环上限LB2 |
| >2 | 无效 |
