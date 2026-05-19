# TTRANS

## 说明

数据块转置(*Tile Transpose*)  
本指令执行如下操作：对输入数据块中的矩阵进行转置，结果写入输出数据块中。

如果输入数据块中的矩阵是`M行N列`的，那么转置后的矩阵应是`N行M列`的。

## 汇编语法

```asm
    TTRANS <Row:arg0, Col:arg1, DataType>, SrcTile<.reuse>, DepSrc, ->DstTile<TileSize>, DepDst
```

## 汇编符号

- **Row,Colp**：分别表示本指令操作的数据块的`Row-行数`、`Col-列数`等尺寸信息。这些参数可以通过三种方式设置，具体如下：
    - **reg**：通过全局寄存器R0至R23设置。
    - **imm**: 通过立即数设置，最大支持16bit值。
    - **reg+imm**：通过全局寄存器R0至R23加上立即数设置。
- **DataType**：表示本指令操作的数据块中元素数据格式，可选类型请见下表。
- **SrcTile**：指示一个[Tile 寄存器](../../register/common/tilereg.md)输入。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：指示输出的[Tile 寄存器](../../register/common/tilereg.md)类型：T, U, M, N。
- **TileSize**：指示输出[Tile 寄存器](../../register/common/tilereg.md)的空间大小，可以通过立即数或者全局寄存器传参。
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
<!-- 
## 编码格式

该TileOp模版块编码为以下指令：

- [BSTART.PAR](../../header/BSTART.PAR.md) `TTRANS, DataType`。
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->Row`。
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->Col`。
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, group=0, ->DstTile<TileSize>`。
- [B.IOD](../../header/B.IOD.md) `DepSrc, ->DepDst`。
 -->

## 执行模型

本指令执行过程通过伪代码示意如下：
```cpp
// C = B^T
void TTranspose(Tile __out__ C, Tile __in__ B) {
  for (int i = 0; i < C.row; i++)
    for (int j = 0; j < C.col; j++)
      C[i][j] = B[j][i];
}
```
将数据块 `B` 转置并存储在 `C` 中。

## 备注

此指令是一种模版块，软件只定义块头。
