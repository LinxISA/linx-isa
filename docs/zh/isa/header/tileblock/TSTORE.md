# TSTORE

## 说明

**数据块存储（Tile Store）**

`TSTORE`用于将一至多个Tile寄存器中的数据搬运到内存中，搬运过程中支持修改数据的存储布局（layout）。多输入时，所有输入Tile的大小必须相同，数据存储排布也必须相同。

## 汇编语法

```asm
TSTORE.Layout <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType>, SrcTile0<.reuse>,..., SrcTile7<.reuse>, 
              [RegSrc0, RegSrc1], DepSrc, -> DepDst
```

## 汇编符号

| 参数 | 定义位置 | 解释 | 是否可选 |
|------|---------|------|----------|
| **Layout** | B.DATR | 指示数据从Tile寄存器到内存过程中存储布局的变化，支持NORM、NZ2ND、ZN2ND这几种变换。 | 是，默认NORM |
| **ValidCol** | B.DIM ->LB0 | 表示本指令搬运的数据块有效的列数信息。 | 否 |
| **ValidRow** | B.DIM ->LB1 | 表示本指令搬运的数据块有效的行数信息。 | 是，默认值为1 |
| **DataType** | BSTART | 表示本指令搬运的数据块中元素的数据格式。 | 否 |
| **Col** | B.DIM ->LB2 | 表示本指令输入的Tile寄存器空间可容纳元素的总列数（该值必须大于等于ValidCol，等于ValidCol时可缺省）。 | 是，默认ValidCol |
| **Row** | 硬件推导 | 可通过输入Tile的TileSize，Col以及DataType计算得到：Row = TileSize / (Col * sizeof(DataType))。 | 是 |
| **SrcTile0-7** | B.IOT | 指示每个输入Tile Register的类型，可选`T/U/M/N`。（不允许是ACC寄存器） | 否 |
| **RegSrc0** | B.IOR | 表示搬移的数据块在内存中的目的地址（BaseAddress），即搬运的第一个元素的基地址。 | 否 |
| **RegSrc1** | B.IOR | 表示内存中两组数据的首地址间隔Stride（单位：字节）（如果两组数据之间地址是连续的则可缺省） | 是，默认连续 |
| **DepSrc** | B.IOD | 表示本块指令对前序输出至D的块指令的依赖。 | 是，默认无依赖 |
| **DepDst** | B.IOD | 表示本块指令对后序引用该标识的块指令的屏障。 | 是，默认无屏障 |

其中，DataType的可选类型见下表：

| DataType | 说明 | DataType | 说明 | DataType | 说明 |
|----------|-----------|----------|-----------|----------|-----------|
| FP64 | 64位双精度浮点数（E11M52）| S64  | 64位有符号整型数据  | U64  | 64位无符号整型数据  |
| FP32 | 32位单精度浮点数（E8M23） | S32  | 32位有符号整型数据  | U32  | 32位无符号整型数据  |
| FP16 | 16位半精度浮点数（E5M10） | S16  | 16位有符号整型数据  | U16  | 16位无符号整型数据  |
| E4M3 | 8位低精度浮点数（E4M3）   | S8   | 8位有符号整型数据   | U8   | 8位无符号整型数据   |

---

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TSTORE, DataType`
- [B.DATR](../../header/B.DATR.md) `Layout`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `SrcTile0<.reuse>, SrcTile1<.reuse>`
- [B.IOT](../../header/B.IOT.md) `SrcTile2<.reuse>, SrcTile3<.reuse>`
- [B.IOT](../../header/B.IOT.md) `SrcTile4<.reuse>, SrcTile5<.reuse>`
- [B.IOT](../../header/B.IOT.md) `SrcTile6<.reuse>, SrcTile7<.reuse>, last`
- [B.IOR](../../header/B.IOR.md) `RegSrc0, RegSrc1`
- [B.IOD](../../header/B.IOD.md) `DepSrc, ->DepDst`

## 实现方式

### 类型1：NORM模式

NORM模式下，`Layout=NORM`，数据存储布局无变化。

实现伪代码：
```py
src_addr_start = SrcTile;    # 源起始地址
dst_addr_start = RegSrc0;    # 目的起始地址
src_row_width = col * sizeof(DataType);    # 一行数据宽度
for (int i = 0; i < rowvalid; i++) do   
    src_addr_row = src_addr_start + i * src_row_width;   # 每行数据的源起始地址
    dst_addr_row = dst_addr_start + i * stride;  # 每行数据的目的起始地址
    for (int j = 0; j < colvalid; j++) do
        src_addr_elem = src_addr_row + j * sizeof(DataType);    # 当前元素的源地址
        dst_addr_elem = dst_addr_row + j * sizeof(DataType);    # 当前元素的目的地址
    end for
end for
```

图示如下：

![TSTORE_NORM](../../../figs/isa/tileop/TSTORE_NORM.png){ width="1000" }

### 类型2：NZ2ND模式（Layout=NZ2ND）：Tile（分型之间列优先，分型内行优先）-> 内存（行优先）

NZ2ND模式，`Layout=NZ2ND`，`Tile（分型之间列优先，分型内行优先）`-> `内存（行优先）`

实现伪代码：
```py
src_frac_size = 512B;     # 小z分型大小
src_frac_row = 16;        # z分型的行数（r0）
src_frac_col = src_frac_size / (src_frac_row * sizeof(DataType));     # z分型的列数（c0）
src_addr_start = SrcTile;    # 源起始地址
dst_addr_start = RegSrc0;    # 目的起始地址
for (int i = 0; i < rowvalid; i++) do
    dst_addr_row = dst_addr_start + i * stride;    # 每行数据的源起始地址
    for (int j = 0; j < colvalid; j++) do
        src_frac_j = j / src_frac_col;     # 分型所在的列（分型维度的列）
        src_addr_elem = src_addr_start + (src_frac_j * row * src_frac_col + i * src_frac_col + j % src_frac_col) * sizeof(DataType);   # 当前元素的源地址
        dst_addr_elem = dst_addr_row + j * sizeof(DataType);    # 当前元素的目的地址
    end for
end for
```

图示如下：

![TSTORE_NZ2ND](../../../figs/isa/tileop/TSTORE_NZ2ND.png){ width="1000" }

Tile寄存器内有padding填充的场景（只拷贝有效数据）：

![TSTORE_NZ2ND1](../../../figs/isa/tileop/TSTORE_NZ2ND1.png){ width="1000" }

### 类型3：ZN2ND模式

ZN2ND模式下，`Layout=ZN2ND`：`Tile（分型之间行优先，分型内列优先）`-> `内存（行优先）`

实现伪代码：
```py
src_frac_size = 512B;     # 小n分型大小
src_frac_col = 16;     # n分型的列数（c0）
src_frac_row = src_frac_size / (src_frac_col * sizeof(DataType));     # n分型的行数（r0）
dst_addr_start = RegSrc0;    # 目的起始地址
src_addr_start = SrcTile;    # 源起始地址
for (int i = 0; i < rowvalid; i++) do
    dst_addr_row = dst_addr_start + i * stride;    # 每行数据的源起始地址
    src_frac_i = i / src_frac_row;     # 分型所在的行（分型维度的行）
    for (int j = 0; j < colvalid; j++) do
        src_addr_elem = src_addr_start + (src_frac_i * col * src_frac_row + j * src_frac_row + i % src_frac_row) * sizeof(DataType);   # 当前元素的源地址
        dst_addr_elem = dst_addr_row + j * sizeof(DataType);   # 当前元素的目的地址
    end for
end for
```
图示如下：

![TSTORE_ZN2ND](../../../figs/isa/tileop/TSTORE_ZN2ND.png){ width="1000" }

Tile寄存器内有padding填充的场景（只拷贝有效数据）：

![TSTORE_ZN2ND1](../../../figs/isa/tileop/TSTORE_ZN2ND1.png){ width="1000" }

## 多输入场景

多输入的场景下，TSTORE可以将多个小输入Tile组合成为一个大Tile，然后将数据一起搬运至内存中，从而提升数据搬运能力。

当前版本中，TSTORE**最多允许有8个输入**，并且所有输入Tile的大小必须相同，数据排布Layout必须相同，否则不保证执行结果的正确性。

多输入时参数含义如下：

* `ValidCol`和`ValidRow`表示一至多个输入Tile合并为一个总Tile后，有效数据的行/列数。同时也表征着向内存中存储的数据块的行/列数。
* `Col`和`Row`表示一个输入Tile块或多个输入Tile合并为总Tile块的行列数。其中**Col必须大于等于ValidCol**，**Row必须大于等于ValidRow**。
* `Row`参数通过多个输入Tile的总空间大小以及Col，DataType计算得到。假设有n个输入Tile，每个Tile的大小为size，总空间大小为TotalTileSize，那么：

```cpp
TotalTileSize = n * size;
Row = TotalTileSize / (Col * sizeof(DataType));
```

多输入时合并规则如下：

* TSTORE应根据输入GM中数据的存储布局决定按照行维度或列维度切分：
    * 按照操作数的定义顺序，依次合并所有输入Tile 成为一个总Tile块。
    * 如果内存GM中数据是ND（行优先）存储的，那么需要沿着列维度进行合并。
    * 如果内存GM中数据是DN（列优先）存储的，那么需要沿着行维度进行合并。
    * 然后将总的Tile块中 `ValidRow * ValidCol` 指示的区域，写到指定内存中。
* 尺寸参数要求：
    * 如果内存数据是ND（行优先）存储的，那么要求**整个Tile的列数Col是输入Tile寄存器数量的整数倍**。否则不保证计算结果的正确性。
    * 如果内存数据是DN（列优先）存储的，那么要求**整个Tile的行数Row是输入Tile寄存器数量的整数倍**。否则不保证计算结果的正确性。

示例1：TSTORE.NZ2ND，合并3个输入Tile寄存器，并且沿着列维度合并。

![TSTORE](../../../figs/isa/tileop/TSTORE.MERGEC.png){ width="900" }

示例2：TSTORE.NZ2DN，合并2个输入Tile寄存器，并且沿着行维度合并。

![TSTORE](../../../figs/isa/tileop/TSTORE.MERGER.png){ width="900" }

## 汇编示例

```asm
    TSTORE.NORM <LB0:100, LB1:a0, LB2:a1+10, FP32>, T#1, [a2]
    TSTORE.NZ2ND <LB0:100, LB1:a0, LB2:a1+10, FP32>, U#1, [a2, a1]
```

## 注意事项

- 当前版本，TSTORE最多只支持二维的数据存储。
- 后序为性能需要，可通过增加维度参数支持多维存储。B.IOR定义的GGPR个数不受限制。
- `ValidCol(LB0)`的值必须小于等于`Col(LB2)`，否则报非法参数异常。
- `ValidRow(LB1)`的值必须小于等于`Row`（硬件推导的值），否则报非法参数异常。
- 当Tile寄存器中为Nz格式时，Col必须为 `32/sizeof(DataType)` 的整数倍，Row为 `16` 的整数倍；
- 当Tile寄存器中为Zn分型，Row必须为 `32/sizeof(DataType)` 的整数倍，Col为 `16` 的整数倍；

## 备注

此指令是一种模版块，软件只定义块头。
