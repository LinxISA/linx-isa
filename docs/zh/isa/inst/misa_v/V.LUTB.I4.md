# V.LUTB.I4

## 说明

4-bit 索引查表返回 Byte（*4-bit Index Look-Up Table to Byte*）<br>
将源寄存器中的 4-bit 索引值作为表项地址，从 Uniform 查找表寄存器中读取对应位置的 byte 数据。每个 byte 索引寄存器包含 2 个 4-bit 索引，查表得到 2 个 byte 结果，打包写入 16-bit 目的寄存器。

## 汇编语法

```asm
    v.lutb.i4 SrcL<.reuse>.ub, SrcR<.reuse>, ->RegDst.h
```

## 汇编符号

- **SrcL**：表项索引寄存器，仅支持 `vt.ub`（8-bit 无符号整数向量）格式。每个 byte 元素包含 2 个 4-bit 索引（位于 bit[3:0], bit[7:4]）。
- **SrcR**：查找表寄存器。若为向量寄存器则隐式支持跨 lane 访问（无需显式 `.uniform` 标记）。表中每项为 8-bit 数据。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **.ub**：指定 SrcL 操作数的数据类型为无符号 8-bit 整数。
- **->**：用于指示目的寄存器。
- **RegDst**：目的寄存器。
- **.h**：目的寄存器为 16-bit 半字宽，其中打包 2 个 8-bit 查表结果。

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
        bits(4)  idx0      = src_byte[3:0];           // 第 0 个 4-bit 索引
        bits(4)  idx1      = src_byte[7:4];           // 第 1 个 4-bit 索引

        bits(8)  result0   = V_LUT[idx0];
        bits(8)  result1   = V_LUT[idx1];

        bits(16) packed    = {result1, result0};
        V[d, 16, laneid]   = packed;
    } else {
        V[d, dstwidth, laneid] = 0;
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。
