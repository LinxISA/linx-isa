# V.FDOT

## 说明

浮点向量点积（*Vector Floating-point Dot Product*）<br>
对SrcL和SrcR中同一个lane的浮点值相乘后，将连续 lane 的乘积累加起来，加上SrcD中最小lane的累加初值，结果广播（broadcast）到组内所有lane中。与 V.DOT 逻辑相同，但操作数为浮点类型。

向量长度字段 `vlen` 控制几个 lane 执行一次点积运算：

| vlen | 合并粒度 | 说明 |
|------|---------|------|
| 00 | 4-lane 合并 | 每 4 个连续 lane 乘加后广播 |
| 01 | 2-lane 合并 | 每 2 个连续 lane 乘加后广播 |
| 10 | 1-lane | 单个 lane 内独立执行点积 |
| 11 | — | 预留 |

## 汇编语法

```asm
    v.fdot SrcL<.reuse>.{T}, SrcR<.reuse>.{T}, SrcD<.reuse>.{T}, ->RegDst.{W}
```

## 汇编符号

- **SrcL**：左源乘数向量，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcR**：右源乘数向量，可以索引的寄存器类型请见[向量指令介绍](../../blockIntro/vecinstrs/instIntro.md)。
- **SrcD**：累加初值寄存器，提供各组归约前的初始值。取值来自每组中最小lane号对应的寄存器值。
- **reuse**：当源寄存器为向量寄存器时可增加本后缀，用于指示当前指令提交后本寄存器不允许被释放。如无此标识，则表示允许硬件释放本寄存器。
- **T**：指定操作数的数据类型，可选类型包括fb,fh,fs,fd等浮点型。
- **->**：用于指示目的寄存器。
- **RegDst**：目的寄存器。
- **W**：目的寄存器位宽，至少是源操作数的两倍，以容纳扩展精度的累加结果。

## 编码格式

（待补充）

## 执行方式

- 解码源寄存器域：[DecodeFP](../LibPseudoCode.md#locationM)
- 解码输出参数：[DecodeDst](../LibPseudoCode.md#locationN)
- 通用寄存器读写：[V\[\]](../LibPseudoCode.md#locationB)

```c
integer {m, srcwidth} = DecodeINT(SrcL);
integer {n, srcwidth} = DecodeINT(SrcR);
integer {acc, accwidth} = DecodeINT(SrcD);
integer {d, dstwidth} = DecodeDst(RegDst);

// vlen 控制合并粒度
integer groupsize;
if (vlen == 0)
    groupsize = 4;
elsif (vlen == 1)
    groupsize = 2;
else  // vlen == 2
    groupsize = 1;

bits(64) pmask = P;
integer num_groups = lanenum / groupsize;

for (gid = 0; gid < num_groups; gid++) {
    integer base_lane = gid * groupsize;
    bits(64) sum = V[acc, accwidth, base_lane];

    for (j = 0; j < groupsize; j++) {
        integer laneid = base_lane + j;
        if (pmask[laneid] == 1) {
            bits(64) opL = V[m, srcwidth, laneid];
            bits(64) opR = V[n, srcwidth, laneid];
            sum += fp_mul(opL, opR, srctype, dsttype);
        }
    }

    // 广播到组内所有 lane
    for (j = 0; j < groupsize; j++) {
        integer laneid = base_lane + j;
        if (pmask[laneid] == 1)
            V[d, dstwidth, laneid] = sum;
        else
            V[d, dstwidth, laneid] = 0;
    }
}
```

## 备注

本指令属于[超长指令扩展](../../instset/longInstrs.md)，可用于向量数据块或访存数据块中。

点积运算中，中间乘法结果应扩展到更高精度后再累加，以避免溢出。

vlen=00（4-lane 合并）适用于 4×4×4 小矩阵乘法。对于更大规模的矩阵运算（≥16×16×16），请使用CUBE运算指令。

本指令为 0.57 版本新增。
