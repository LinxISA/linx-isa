# TGATHER

## 说明

内存聚集(*Gather from Tile to Tile*)  
本指令执行如下操作：聚集输入数据块中离散位置的数据，结果写入输出数据块中。 

## 汇编语法

```asm
    TGATHER <Row:arg0, Col:arg1, Dep:arg2, DataType>, SrcTile0<.reuse>, SrcTile1<.reuse>, DepSrc, ->DstTile, DepDst
```

## 汇编符号


- **Row,Col,Dep**：分别表示本指令操作的数据块的`Row-行数`、`Col-列数`和`Dep-深度`等尺寸信息。这些参数可以通过三种方式设置，具体如下：
    - **reg**：通过全局寄存器[GGPR](../../register/common/ggpr.md)设置。
    - **imm**: 通过立即数设置，最大支持16bit值。
    - **reg+imm**：通过全局寄存器[GGPR](../../register/common/ggpr.md)加上立即数设置。
- **DataType**：表示本指令操作的数据块中元素数据格式，可选类型请见下表。
- **SrcTile0**：指示第一个输入的[Tile 寄存器](../../register/common/tilereg.md)。
- **SrcTile1**：指示第二个输入的[Tile 寄存器](../../register/common/tilereg.md)。
- **reuse**（后缀）：指示当前指令提交后保留寄存器（若无此标识，允许硬件自动释放）。
- **DstTile**：指示输出的[Tile 寄存器](../../register/common/tilereg.md)。
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

本指令拆分成以下指令进行编码：

- [BSTART.PAR](../../header/BSTART.PAR.md) `TGATHER, DataType`。
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->Row`。
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->Col`。
- [B.DIM](../../header/B.DIM.md) `reg, imm, ->Dep`。
- [B.IOT](../../header/B.IOT.md) `SrcTile<.reuse>, group=0, ->DstTile<TileSize>`。
- [B.IOD](../../header/B.IOD.md) `DepSrc, ->DepDst`。
 -->

## 执行模型

本指令执行过程通过伪代码示意如下：

```c
// dst: 输出 Tile，形状为 [row, col]
// src: 源 Tile，形状为 [max_index, col]，必须至少支持 indices[i][j] 所指向的行号
// indices: 索引 Tile，形状为 [row, col]，每个元素是整型索引（如 0~N-1）
// 该函数直接按行列遍历，将 indices[i][j] 作为 src 的行索引，复制对应元素到 dst[i][j]
void TGather(Tile __out__ dst, Tile __in__ src, Tile __in__ indices) {
    for (int i = 0; i < dst.row; i++) {
        for (int j = 0; j < dst.col; j++) {
            int idx = indices[i][j];  // 索引值
            dst[i][j] = src[idx][j];  // 从 S 的第 idx 行取值
        }
    }
}
```
