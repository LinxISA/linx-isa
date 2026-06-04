# V.LUTB.I2

## 说明

2-bit 索引查表返回 Byte（*2-bit Index Look-Up Table to Byte*）<br>
将源寄存器中的 2-bit 索引值作为表项地址，从 Uniform 查找表寄存器中读取对应位置的 byte 数据。每个 byte 索引寄存器包含 4 个 2-bit 索引，查表得到 4 个 byte 结果，打包写入 32-bit 目的寄存器。

## 汇编语法

```asm
    v.lutb.i2 SrcL<.reuse>.ub, SrcR<.reuse>, ->RegDst.w
```

## 汇编符号

- **SrcL**：表项索引寄存器，仅支持 `vt.ub`（8-bit 无符号整数向量）格式。每个 byte 元素包含 4 个 2-bit 索引（位于 bit[1:0], bit[3:2], bit[5:4], bit[7:6]）。
- **SrcR**：查找表寄存器。若为向量寄存器则隐式支持跨 lane 访问（无需显式 `.uniform` 标记）。表中每项为 8-bit 数据。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **.ub**：指定 SrcL 操作数的数据类型为无符号 8-bit 整数。
- **->**：用于指示目的寄存器。
- **RegDst**：目的寄存器。
- **.w**：目的寄存器为 32-bit 字宽，其中打包 4 个 8-bit 查表结果。

## 编码格式

（待补充）

## 执行方式

- 解码源寄存器域：[DecodeINT](../LibPseudoCode.md#locationL)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
bits(64) pmask = P;
integer {m, srcwidth} = DecodeINT(SrcL);
integer {d, dstwidth} = DecodeDst(RegDst);
// SrcR 为 Uniform 寄存器，所有 lane 可读取其全部 lane 数据
// 查找表存储在 SrcR 指向的寄存器空间中

for (laneid = 0; laneid < lanenum; laneid++) {
    if (pmask[laneid] == 1) {
        bits(8)  src_byte  = V[m, 8, laneid];
        bits(2)  idx0      = src_byte[1:0];           // 第 0 个 2-bit 索引
        bits(2)  idx1      = src_byte[3:2];           // 第 1 个 2-bit 索引
        bits(2)  idx2      = src_byte[5:4];           // 第 2 个 2-bit 索引
        bits(2)  idx3      = src_byte[7:6];           // 第 3 个 2-bit 索引

        bits(8)  result0   = V_LUT[idx0];             // 查表
        bits(8)  result1   = V_LUT[idx1];
        bits(8)  result2   = V_LUT[idx2];
        bits(8)  result3   = V_LUT[idx3];

        bits(32) packed    = {result3, result2, result1, result0};  // 打包
        V[d, 32, laneid]   = packed;
    } else {
        V[d, dstwidth, laneid] = 0;
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
