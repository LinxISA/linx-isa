# TLOAD

## 说明

**数据块加载(Tile Load)**

`TLOAD`用于将内存中的数据搬运到一至多个Tile寄存器中，搬运过程中支持修改数据的存储布局（layout）。多输出时，所有输出Tile的大小必须相同，数据存储排布也必须相同。

## 汇编语法

```asm
TLOAD.Layout <LB0:ValidCol, LB1:ValidRow, LB2:Col, DataType, PadValue>, [RegSrc0, RegSrc1], DepSrc, 
             ->DstTile0<Size>, ..., DstTile7<Size>, DepDst
```

## 汇编符号

| 参数 | 定义位置 | 解释 | 是否可选 |
|------|---------|-------|----------|
| **Layout** | B.DATR | 指示数据从内存到Tile寄存器的过程中存储布局的变化，支持NORM、ND2NZ、ND2ZN、DN2NZ、DN2ZN这几种变换。 | 是，默认NORM |
| **ValidCol** | B.DIM ->LB0 | 表示本指令搬运的数据块有效的列数信息。 | 否 |
| **ValidRow** | B.DIM ->LB1 | 表示本指令搬运的数据块有效的行数信息。 | 是，默认值为1 |
| **Col** | B.DIM ->LB2 | 表示本指令申请的输出Tile寄存器空间可容纳元素的总列数（该值必须大于等于ValidCol，等于ValidCol时可缺省）。 | 是，默认ValidCol |
| **Row** | 硬件推导 | 可通过Size，Col以及DataType计算得到：Row = Size / (Col * sizeof(DataType))。 | 是 |
| **DataType** | BSTART | 表示本指令搬运的数据块中元素的数据格式。 | 否 |
| **PadValue** | B.DATR | Tile寄存器中的padding value。可选类型包括: Null（不填充或保留随机值）, Zero（填充零值）, Max（填充当前数据格式下最大值）, Min（填充当前数据格式下最小值）。 | 是，默认Null |
| **DstTile0-7** | B.IOT | 指示每个输出Tile Register的类型，可选T/U/M/N。（不允许输出到ACC） | 否 |
| **Size** | B.IOT | 输出Tile寄存器的空间大小（有效范围参见：[Tile寄存器](../../register/common/tilereg.md)）。 | 否 |
| **RegSrc0** | B.IOR  | 表示搬移的数据块的基地址（BaseAddress），即搬运的第一个元素的地址。 | 否 |
| **RegSrc1** | B.IOR  | 表示内存中两组数据的首地址间隔Stride（单位：字节）（如果两组数据之间地址是连续的则可缺省） | 是，默认连续 |
| **DepSrc** | B.IOD | 表示本块指令对前序输出至D的块指令的依赖。 | 是，默认无依赖 |
| **DepDst** | B.IOD | 表示本块指令对后序引用该标识的块指令的屏障。 | 是，默认无屏障 |

其中DataType的可选类型如下表：

| 数据位宽 | 类型列表 |
|----------|------------|
| b64 | S64, U64, FP64 |
| b32 | S32, U32, FP32, TF32, HF32 |
| b16 | S16, U16, FP16, BF16 |
| b8  | S8,  U8,  FP8(E4M3, E5M2), E8M0, HiF8, HiF4x2, E1M2x2, E2M1x2, S4x2, U4x2 |

## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.TMA](../../blockIntro/tma_block/header.md) `TLOAD, DataType`
- [B.DATR](../../header/B.DATR.md) `Layout, PadValue`
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB0`    （注：*ValidCol*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB1`    （注：*ValidRow*）
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->LB2`    （注：*Col*）
- [B.IOT](../../header/B.IOT.md) `, ->DstTile0<Size>`
- [B.IOT](../../header/B.IOT.md) `, ->DstTile1<Size>`
- ...
- [B.IOT](../../header/B.IOT.md) `last, ->DstTile7<Size>`
- [B.IOR](../../header/B.IOR.md) `RegSrc0, RegSrc1`
- [B.IOD](../../header/B.IOD.md) `DepSrc, ->DepDst`

## 实现方式

### 类型1：NORM模式

NORM模式下，`Layout = NORM`，且存储布局无变化。

实现伪代码：
```py
src_addr_start = RegSrc0;    # 源起始地址
dst_addr_start = DstTile;    # 目的起始地址
dst_row_width = col * sizeof(DataType);    # 一行数据宽度
for (int i = 0; i < row; i++) do   
    src_addr_row = src_addr_start + i * stride;   # 每行数据的源起始地址
    dst_addr_row = dst_addr_start + i * dst_row_width;  # 每行数据的目的起始地址
    for (int j = 0; j < col; j++) do
        if (i < rowvalid and j < colvalid)
            src_addr_elem = src_addr_row + j * sizeof(DataType);    # 当前元素的源地址
        else
            dst_data_elem = PadValue;      # 填充元素
        dst_addr_elem = dst_addr_row + j * sizeof(DataType);    # 当前元素的目的地址
        end for
end for
```

图示如下：

![TLOAD_NORM](../../../figs/isa/tileop/TLOAD_NORM.png){ width="1000" }

Tile寄存器中填充PadValue的图示：

![TLOAD_NORM1](../../../figs/isa/tileop/TLOAD_NORM1.png){ width="1000" }

### 类型2：ND2NZ模式

ND2NZ模式：`内存（行优先）`-> `Tile（大分形列优先，小分形行优先）`

实现伪代码：
```py
dst_frac_size = 512B;     # 小z分型大小
dst_frac_row = 16;     # z分型的行数（r0）
dst_frac_col = dst_frac_size / (dst_frac_row * sizeof(DataType));     # z分型的列数（c0）
src_addr_start = RegSrc0;    # 源起始地址
dst_addr_start = DstTile;    # 目的起始地址
for (int i = 0; i < row; i++) do
    src_addr_row = src_addr_start + i * stride;    # 每行数据的源起始地址
    for (int j = 0; j < col; j++) do
        if (i < rowvalid and j < colvalid)
            src_addr_elem = src_addr_row + j * sizeof(DataType);     # 当前元素的源地址
        else
            dst_data_elem = PadValue;      # 填充元素
        dst_frac_j = j / dst_frac_col;     # 分型所在的列（分型维度的列）
        dst_addr_elem = dst_addr_start + (dst_frac_j * row * dst_frac_col + i * dst_frac_col + j % dst_frac_col) * sizeof(DataType);  # 当前元素的目的地址
    end for
end for
```

图示如下：

![TLOAD_ND2NZ](../../../figs/isa/tileop/TLOAD_ND2NZ.png){ width="1000" }

Tile寄存器中填充PadValue的图示：

![TLOAD_ND2NZ1](../../../figs/isa/tileop/TLOAD_ND2NZ1.png){ width="1000" }

### 类型3：ND2ZN模式

ND2ZN模式：`内存（行优先）`-> `Tile（大分形行优先，小分形列优先）`

伪代码实现：
```py
dst_frac_size = 512B;     # 小n分型大小
dst_frac_col = 16;     # n分型的列数（c0）
dst_frac_row = dst_frac_size / (dst_frac_col * sizeof(DataType));     # n分型的行数（r0）
src_addr_start = RegSrc0;    # 源起始地址
dst_addr_start = DstTile;    # 目的起始地址
for (int i = 0; i < row; i++) do
    src_addr_row = src_addr_start + i * stride;    # 每行数据的源起始地址
    dst_frac_i = i / dst_frac_row;     # 分型所在的行（分型维度的行）
    for (int j = 0; j < col; j++) do
        if (i < rowvalid and j < colvalid)
            src_addr_elem = src_addr_row + j * sizeof(DataType);     # 当前元素的源地址
        else
            dst_data_elem = PadValue;     # 填充元素
        dst_addr_elem = dst_addr_start + (dst_frac_i * col * dst_frac_row + j * dst_frac_row + i % dst_frac_row) * sizeof(DataType);   # 当前元素的目的地址
    end for
end for
```

图示如下：

![TLOAD_ND2ZN](../../../figs/isa/tileop/TLOAD_ND2ZN.png){ width="1000" }

Tile寄存器中填充PadValue的图示：

![TLOAD_ND2ZN1](../../../figs/isa/tileop/TLOAD_ND2ZN1.png){ width="1000" }

### 类型4：DN2NZ模式

DN2NZ模式：`内存（列优先）`-> `Tile（大分形列优先，小分形行优先）`

伪代码实现：
```py
dst_frac_size = 512B;     # 小z分型大小
dst_frac_row = 16;       # z分型的行数（r0）
dst_frac_col = dst_frac_size / (dst_frac_row * sizeof(DataType));     # z分型的列数（c0）
src_addr_start = RegSrc0;    # 源起始地址
dst_addr_start = DstTile;    # 目的起始地址
for (int i = 0; i < row; i++) do
    for (int j = 0; j < col; j++) do
        if (i < rowvalid and j < colvalid)
            src_addr_row = src_addr_start + j * stride;    # 每列数据的源起始地址
            src_addr_elem = src_addr_row + i * sizeof(DataType);  # 当前元素的源地址
        else
            dst_data_elem = PadValue;      # 填充元素
        dst_frac_j = j / dst_frac_col;                 # 分型所在的列（分型维度的列）
        dst_addr_elem = dst_addr_start + (dst_frac_j * row * dst_frac_col + i * dst_frac_col + j % dst_frac_col) * sizeof(DataType);   # 当前元素的目的地址
    end for
end for
```

图示如下：

![TLOAD_DN2NZ](../../../figs/isa/tileop/TLOAD_DN2NZ.png){ width="1000" }

### 类型5：DN2ZN模式

DN2ZN模式：`内存（列优先）`-> `Tile（大分形行优先，小分形列优先）`

伪代码实现：
```py
dst_frac_size = 512B;     # 小n分型大小
dst_frac_col = 16;       # n分型的列数（c0）
dst_frac_row = dst_frac_size / (dst_frac_col * sizeof(DataType));     # n分型的行数（r0）
src_addr_start = RegSrc0;    # 源起始地址
dst_addr_start = DstTile;    # 目的起始地址
for (int i = 0; i < row; i++) do
    dst_frac_i = i / dst_frac_row;                 # 分型所在的列（分型维度的列）
    for (int j = 0; j < col; j++) do
        if (i < rowvalid and j < colvalid)
            src_addr_row = src_addr_start + j * stride;    # 每列数据的源起始地址
            src_addr_elem = src_addr_row + i * sizeof(DataType);  # 当前元素的源地址
        else
            dst_data_elem = PadValue;      # 填充元素
        dst_addr_elem = dst_addr_start + (dst_frac_i * col * dst_frac_row + j * dst_frac_row + i % dst_frac_row) * sizeof(DataType);   # 当前元素的目的地址
    end for
end for
```

图示如下：

![TLOAD_DN2ZN](../../../figs/isa/tileop/TLOAD_DN2ZN.png){ width="1000" }

## 多输出场景

多输出的场景下，TLOAD实际是将内存GM中多个小Tile捆绑在一起进行数据搬运，然后再将加载的整个大Tile切分为多个小Tile输出到不同的目的寄存器中。这样既可以提升TLOAD的数据搬运能力，又能满足后序块指令对小Tile块的输入需要。

当前版本中，**TLOAD 最多允许输出到8个不同 Tile 寄存器中**。软件应保证所有输出Tile 的大小和数据排布Layout相同，否则不保证执行结果的正确性。

多输出时参数含义如下：

- `ValidCol`和`ValidRow`表示多个输出Tile合并状态下，有效数据的行/列数。同时也表征着从内存加载的数据块的行/列数。
- `Col`和`Row`表示对加载的数据进行填充（padding）后，总Tile块的行列数。其中**Col必须大于等于ValidCol，Row必须大于等于ValidRow**。
- `Row`参数通过多个输出Tile的总空间大小以及Col，DataType计算得到。假设有n个输出Tile，每个Tile的大小为size，总空间大小TotalSize，那么：

```c++
TotalSize = n * size;
Row = TotalSize / (Col * sizeof(DataType));
```

多输出时切分规则如下：

* TLOAD应根据输入GM中数据的存储布局决定按照行维度或列维度切分：
    * 如果输入是ND（行优先）的，那么需要沿着列维度进行切分。假设整个Tile是`Row*Col`的，那么切分N份后每个输出Tile中是`Row * Col/N` 的。
    * 如果输入是DN（列优先）的，那么需要沿着行维度进行切分。假设整个Tile是`Row*Col`的，那么切分N份后每个输出Tile中是`Row/N * Col` 的。
* 尺寸参数要求：
    * 如果输入是ND（行优先）的，那么要求**整个Tile的列数Col是输出Tile寄存器数量的整数倍**。否则不保证计算结果的正确性。
    * 如果输入是DN（列优先）的，那么要求**整个Tile的行数Row是输出Tile寄存器数量的整数倍**。否则不保证计算结果的正确性。

实现示意图如下：

示例1：TLOAD.ND2NZ输出至3个Tile寄存器，并且沿着列维度切分。

![TLOAD](../../../figs/isa/tileop/TLOAD.SPLITC.png){ width="900" }

示例2：TLOAD.DN2NZ，输出至2个Tile寄存器，并且沿着行维度切分。

![TLOAD](../../../figs/isa/tileop/TLOAD.SPLITR.png){ width="900" }

## 汇编示例

```asm
    TLOAD.NORM <LB0:100, LB1:a0, LB2:a1+10, FP16>, [a2], ->T<2KB>         # 通过立即数设置输出Tile的大小
    TLOAD.ND2NZ <LB0:100, LB1:a0, LB2:a1+10, FP16>, [a2, a0], ->T<a1>     # 通过寄存器设置输出Tile的大小
```

## 注意事项

- 当前版本，TLoad只支持一维或二维的数据加载，多维数据的加载通过多个TLoad完成。
- 后序为性能需要，可通过增加维度参数支持多维加载。B.IOR定义的GGPR个数不受限制。
- **ValidCol(LB0)的值必须小于等于Col(LB2)**，否则报非法参数异常。
- **ValidRow(LB1)的值必须小于等于Row（硬件推导的值）**，否则报非法参数异常。
- 当Tile寄存器中数据为 Nz 格式时，Row必须为 `16` 的整数倍，Col为 `32/sizeof(DataType)` 的整数倍；
- 当Tile寄存器中数据为 Zn 格式时，Row必须为 `32/sizeof(DataType)` 的整数倍，Col为 `16` 的整数倍；
- 本指令不允许直接写到ACC寄存器，否则报非法指令异常。

## 备注

该指令是一种模版块，软件只定义块头。
