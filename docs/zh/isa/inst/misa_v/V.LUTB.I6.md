# V.LUTB.I6

## 说明

6-bit 索引查表返回 Byte（*6-bit Index Look-Up Table to Byte*）<br>
将源寄存器中的 6-bit 索引值作为表项地址，从 Uniform 查找表寄存器中读取对应位置的 byte 数据。每个 byte 索引寄存器包含 1 个 6-bit 索引（高 2-bit 为 padding），查表得到 1 个 byte 结果，写入 8-bit 目的寄存器。

## 汇编语法

```asm
    v.lutb.i6 SrcL<.reuse>.ub, SrcR<.reuse>, ->RegDst.b
```

## 汇编符号

- **SrcL**：表项索引寄存器，仅支持 `vt.ub`（8-bit 无符号整数向量）格式。每个 byte 元素的低 6-bit（bit[5:0]）为有效索引，高 2-bit（bit[7:6]）为 padding。
- **SrcR**：查找表寄存器。若为向量寄存器则隐式支持跨 lane 访问（无需显式 `.uniform` 标记）。表中每项为 8-bit 数据。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **.ub**：指定 SrcL 操作数的数据类型为无符号 8-bit 整数。
- **->**：用于指示目的寄存器。
- **RegDst**：目的寄存器。
- **.b**：目的寄存器为 8-bit 字节宽，包含 1 个 8-bit 查表结果。

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

for (laneid = 0; laneid < lanenum; laneid++) {
    if (pmask[laneid] == 1) {
        bits(8)  src_byte  = V[m, 8, laneid];
        bits(6)  idx       = src_byte[5:0];           // 低 6-bit 为有效索引

        bits(8)  result    = V_LUT[idx];

        V[d, 8, laneid]    = result;
    } else {
        V[d, dstwidth, laneid] = 0;
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
