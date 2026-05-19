# LCFR

灵犀核特征寄存器（Linx Core Features Register）<br>
用于描述当前处理器核支持的功能特征，如向量扩展、浮点运算等。

![LCFR](../../../figs/bitfield/svg/Sysregs/LCFR.svg)

各字段说明如下：

## **C标志位**

`C`位在[压缩指令扩展](../../instset/compressInstrs.md)被支持的时候为1，否则为0；

## **G标志位**

`G`位在GQM指令扩展被支持的时候为1，否则为0；

## **F标志位**

`F`位在浮点指令被支持的时候为1，否则为0；

## **V标志位**

`v`位在向量指令扩展被支持的时候为1，否则为0；

## **GroupNum字段**

`GroupNum`表示在支持向量扩展的核内有多少个并行Group，计算方式：

```c
    GroupNumber = 2 ^ GroupNum;
```
GroupNum的有效范围为[0, 8]，因此GroupNumber有效取值为：

| GroupNum | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 
|----------|---|---|---|---|---|---|---|---|---|
| 并行Group数量 | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 256 |

## **LaneNum字段**

`LaneNum`表示在支持向量扩展的核内每个Group内并行lane的数量**LaneNumber**，计算方式：

```c
    LaneNumber = 2 ^ LaneNum;
```

LaneNum的有效范围为[0, 6]，因此LaneNumber有效取值为：

| LaneNum | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 
|----------|---|---|---|---|---|---|---|
| 并行Lane数量 | 1 | 2 | 4 | 8 | 16 | 32 | 64 |

## **TMaxSize字段**

`TMaxSize`表示架构允许申请使用的[Tile Register](../common/tilereg.md)的最大范围**TileMaxSize**，计算方式：

```c
    TileMaxSize = 512 * (TMaxSize + 1) byte;
```

当前版本，Tile寄存器范围允许设置的最大值是32KB。

## **TMinSize字段**

`TMinSize`表示架构允许申请使用的[Tile Register](../common/tilereg.md)的最小范围**TileMinSize**，计算方式：

```c
    TileMinSize = 512 * (TMinSize + 1) byte;
```

当前版本，Tile寄存器范围允许设置的最小值是512Byte。

## 备注

该寄存器是**只读的(RO)**，其SSRID为**0x0024**。
