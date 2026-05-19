# Loop寄存器

Loop寄存器主要用于[向量数据块](../../blockIntro/vec_block/intro.md)和[访存数据块](../../blockIntro/mem_block/intro.md)中指示块体迭代展开的总数量以及记录每次迭代的ID。根据寄存器的作用，Loop寄存器分为以下两组：

## <span id="LB">**1.LB寄存器**</span>

LB（全称为**Lane Bound Register**）寄存器包含3个，分别命名为LB0、LB1和LB2。每个寄存器宽度都是 **16bit** 的。

- **LB0**：用于存储最内层循环迭代上限值。
- **LB1**：用于存储中间层循环迭代上限值。
- **LB2**：用于存储最外层循环迭代上限值。

在没有块体的数据块（例如[TMA块](../../blockIntro/tma_block/intro.md)或[CUBE块](../../blockIntro/cube_block/intro.md)）中，LB寄存器通常用作设置Tile中数据的行列数等维度信息。

## <span id="LC">**2.LC寄存器**</span>

LC（全称为**Lane Counter Register**）寄存器也包含3个，分别命名为LC0、LC1和LC2。寄存器宽度同样都是 **16bit** 的。

- **LC0**：用于记录最内层循环迭代的ID。
- **LC1**：用于记录中间层循环迭代的ID。
- **LC2**：用于记录最外层循环迭代的ID。

## 访问属性

- LB寄存器是可读写的（RW），并且只能通过[B.DIM](../../header/B.DIM.md)和[C.B.DIM](../../header/C.B.DIM.md)指令设置。
- LC寄存器是只读的（RO）。
