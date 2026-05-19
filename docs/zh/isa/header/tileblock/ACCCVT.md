# ACCCVT

## 说明

**结果矩阵类型转换（AccTile Convert）**

`ACCCVT` 将 **ACC** 寄存器中的数据搬移到通用的 **T/U/M/N** 类型的Tile寄存器中。搬运期间支持如下的随路运算操作：

1. **存储布局重排**，例如：NZ2ND转换。
2. **分形大小拆分**（Canonicalize操作），以满足后序指令需要。
3. **数据类型转换**，例如：fp32 -> fp16。
4. **逐元素缩放**，每个元素乘以一个相同的scale值。
5. **行最大值归约**，输出每行数据的最大值。

## 汇编语法

```asm
ACCCVT Layout.{canon, normal}, <LB0:Row, LB1:Col, SrcType, DstType>, ACC, [RegSrc], DepSrc,
                               ->DstTile0<TileSize0>, DstTile1<TileSize1>, DepDst
```

## 汇编符号

- **Layout**：数据存储格式转换标识，支持NORM, NZ2ND，NZ2DN等。
    - **canon**: 将输入ACC矩阵的分形转换成标准左矩阵格式，基于不同的数据格式将ACC的原分形进行合并或者拆分。
    - **normal**：不对输入ACC矩阵的原分形做变换，可缺省。
- **SrcType**：指示数据ACC寄存器中元素的数据类型，可选类型见下表。
- **Row、Col**：表示输入矩阵的尺寸，可分别通过`全局寄存器`、`立即数`或`全局寄存器加立即数`的形式设置。
    - **Row**：表示输入矩阵的行数。
    - **Col**：表示输入矩阵的列数。
- **ACC**：指示输入ACC类型[Tile 寄存器](../../register/common/tilereg.md)。
- **RegSrc**：指示输入的[全局寄存器](../../register/common/ggpr.md)，用于存储scale值。该参数数据类型必须与ACC Tile的数据类型保持一致，否则指令不保证计算结果的正确性。如果不执行scale操作则可缺省。
- **DstTile0**：指示第一个输出的[Tile 寄存器](../../register/common/tilereg.md)类型，可选T, U, M, N。用于存储随路运算主结果。
- **DstTile1**：指示第二个输出的[Tile 寄存器](../../register/common/tilereg.md)类型，可选T, U, M, N。用于存储RowMax结果，如果不执行RowMax则缺省。
- **TileSize0**：指示第一个输出[Tile 寄存器](../../register/common/tilereg.md)的空间大小，可以通过立即数或者全局寄存器传参。
- **TileSize1**：指示第二个输出[Tile 寄存器](../../register/common/tilereg.md)的空间大小，可以通过立即数或者全局寄存器传参。跟随DstTile1缺省。
- **DepSrc**：表示本块指令对前序输出至D的块指令的依赖。
- **DepDst**：表示本块指令对后序引用该标识的块指令的屏障。

输入ACC寄存器中元素的数据格式（SrcType）可以是以下几种：

| DataType | 说明 |
|----------|-----------|
| FP32 | 32位单精度浮点数（E8M23） |
| S32  | 32位有符号整型数据  |
| U32  | 32位无符号整型数据  |

转换后元素的数据格式（DstType）可选类型如下表：

| DstType | 说明 | DstType | 说明 |
|----------|-----------|----------|-----------|
| FP64 | 64位双精度浮点数（E11M52）| S64  | 64位有符号整型数据   |
| FP32 | 32位单精度浮点数（E8M23） | S32  | 32位有符号整型数据   |
| TF32 | 32位单精度浮点数（E8M10） | S16  | 16位有符号整型数据   |
| HF32 | 32位单精度浮点数（E8M11） | S8   | 8位有符号整型数据    |
| FP16 | 16位半精度浮点数（E5M10） | U64  | 64位无符号整型数据   |
| BF16 | 16位半精度浮点数（E8M7）  | U32  | 32位无符号整型数据   |
| E4M3 | 8位低精度浮点数（E4M3）   | U16  | 16位无符号整型数据   |
| E5M2 | 8位低精度浮点数（E5M2）   | U8   | 8位无符号整型数据    |
| E2M3 | 6位低精度浮点数（E2M3）   | E3M2 | 6位低精度浮点数（E3M2） |
| E2M1 | 4位低精度浮点数（E2M1）   | E1M2 | 4位低精度浮点数（E1M2） |
| E8M0 | 8位低精度浮点数（E8M0）   | HiF4 | 4位低精度浮点数（E1M2） |

## 编码格式

`ACCCVT` 块需要拆分成以下指令进行编码：

- [BSTART.CUBE](../../blockIntro/cube_block/header.md) ACCCVT, SrcType
- [B.DATR](../../header/B.DATR.md) Layout.{canon, normal}, DstType
- [B.DIM](../../header/B.DIM.md) reg, imm, ->LB0
- [B.DIM](../../header/B.DIM.md) reg, imm, ->LB1
- [B.IOT](../../header/B.IOT.md) , ->DstTile0< TileSize0>
- [B.IOT](../../header/B.IOT.md) last, ->DstTile1< TileSize1>
- [B.IOR](../../header/B.IOR.md) RegSrc
- [B.IOD](../../header/B.IOD.md) DepSrc, ->DepDst

## 布局与数据类型

需要注意的是，根据[矩阵数据块](../../blockIntro/cube_block/intro.md)对矩阵运算输入输出的要求，ACC寄存器内的结果矩阵总是以**NZ（大N小z）**的布局进行存储的，并且每个小分形的大小为 **1024字节**。同时为了简化矩阵运算，数据精度统一对齐为32bit，因此ACC输入的数据都是以32位的精度进行存储的。

ACC输入的格式：

| 格式 | 说明 | 
|---------|-------|
| 存储布局（Layout） | NZ（大N小z）格式 |
| 小分形大小 | 1024Byte |
| 元素数据格式 | 32bit精度（FP32, INT32, UINT32） |

## 执行模型

执行过程通过伪代码示意如下：
```cpp
// 例如：dst = Convert(src)
// 实际实现中，硬件按 Src/Dst 的 Layout 完成地址换算和分型重排。
void ACCCVT(Tile __out__ dst, Tile __in__ src) {
  for (int i = 0; i < row; i++)
    for (int j = 0; j < col; j++) {
      SrcType temp = src[i][j] * scale;  // 执行scale运算
      C[i][j] = Convert(temp, SrcType, DstType);
    }
}
```

指令实现示意图如下：

![acccvt](../../../figs/isa/tileop/acccvt.png){ width="800" }

由于输入ACC中矩阵的小分形大小为1024byte，如果程序中期望将该矩阵作为矩阵乘运算的左矩阵输入时，那么就需要把1024byte大小的分形拆分为两个512Byte大小的分形，以满足输入要求。此时，可通过ACCCVT指令完成这种**标准化（canon）操作**。

canon操作的示意图如下：

![canonicalize](../../../figs/isa/arch/canon.png){ width="600" }

## 注意事项

- 仅当分形变化为 NZ2ND 或 NZ2DN 时，支持ROWMAX操作。
- 其他分形变换时执行ROWMAX为未定义行为，此时不保证第二个输出Tile（DstTile1）中结果的正确性。
- ACCCVT指令执行结束后，ACC寄存器将被释放，后序指令直接读取ACC寄存器会触发异常。

## 备注

此指令是一种模版块，软件只定义块头。
