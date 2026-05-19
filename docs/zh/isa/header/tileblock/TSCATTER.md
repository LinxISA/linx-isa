# TSCATTER

## 说明

数据块分散(*Scatter from Tile to Tile*)  
本指令执行如下操作：将第一个输入数据块内的数据存储到离散的数据块空间中。离散的索引存储在第二个输入Tile中。

## 汇编语法

```asm
    TSCATTER <Row:arg0, Col:arg1, Dep:arg2, DataType>, SrcTile0<.reuse>, SrcTile1<.reuse>, DepSrc, ->DstTile<TileSize>, DepDst
```

## 汇编符号

- **Row,Col,Dep**：分别表示本指令操作的数据块的`Row-行数`、`Col-列数`和`Dep-深度`等尺寸信息。这些参数可以通过三种方式设置，具体如下：
    - **reg**：通过全局寄存器R0至R23设置。
    - **imm**: 通过立即数设置，最大支持16bit值。
    - **reg+imm**：通过全局寄存器R0至R23加上立即数设置。
- **DataType**：表示本指令操作的数据块中元素数据格式，可选类型请见下表。
- **SrcTile0**：指示第一个输入的[Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile1**：指示第二个输入的[Tile 寄存器](../../register/common/tilereg.md)。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：指示输出的[Tile 寄存器](../../register/common/tilereg.md)。
- **TileSize**：指示输出的Tile寄存器的空间大小，可以通过`立即数`或者`全局寄存器`设置。
- **DepSrc**：表示本块指令对前序输出至D的块指令的依赖。
- **DepDst**：表示本块指令对后序引用该标识的块指令的屏障。

| DataType | 说明 |
|----------|-----------|
| FP64 | 64位双精度浮点数（E11M52）|
| FP32 | 32位单精度浮点数（E8M23） |
| FP16 | 16位半精度浮点数（E5M10） |
| E4M3 | 8位低精度浮点数（E4M3）   |
| S64  | 64位有符号整型数据        |
| S32  | 32位有符号整型数据        |
| S16  | 16位有符号整型数据        |
| S8   | 8位有符号整型数据         |
| U64  | 64位无符号整型数据        |
| U32  | 32位无符号整型数据        |
| U16  | 16位无符号整型数据        |
| U8   | 8位无符号整型数据         |

## 执行模型

本指令执行过程通过伪代码示意如下：

```c
// dst: 输出 Tile，形状为 [max_index, col]，必须至少支持 indices[i][j] 所指向的行号
// src: 源 Tile，形状为 [row, col]
// indices: 索引 Tile，形状为 [row, col]，每个元素是整型索引（如 0~N-1）
// 该函数直接按行列遍历，将 indices[i][j] 作为 dst 的行索引，复制 src[i][j] 到 dst[idx][j]
void TScatter(Tile __in__ dst, Tile __in__ src, Tile __in__ indices) {
  for (int i = 0; i < src.row; i++)
    for (int j = 0; j < src.col; j++) {
        int idx = indices[i][j];
        dst[idx][j] = src[i][j];
    }
}
```
