# THISTOGRAM

## 说明

`THISTOGRAM` 指令用于对 src tile 中每一行的元素 **按字节进行直方图统计**，并将统计结果转换为前缀累计计数写入 dst tile。每个输出行对应一个输入有效行，输出列表示一个字节的 256 种可能取值 0..255，第 k 列保存取值 0..k 的累计计数。

该指令常用于基于字节的分桶、radix sort 分阶段统计等场景。对于多字节元素，THistogram 可选择统计其中某一个字节；在统计低位字节时，可使用 idx tile 提供高位字节前缀过滤条件，使指令只统计满足指定前缀的元素。

## 汇编格式

```asm
THISTOGRAM <LB0:validCol, LB1:validRow, LB2:Col, SrcType, DstType, ByteId, PadValue>, SrcTile<.reuse>, IdxTile<.reuse>, ->DstTile<Size>
```

## 汇编符号


- **LB0: validCol**：指定源 SrcTile 的有效列数，即每个有效行中参与统计的元素个数。
- **LB1: validRow**：指定源 SrcTile 的有效行数，即独立生成累计计数的行数。
- **LB2: Col**：指定源 SrcTile 的总列数或 tile 列跨度。源 SrcTile 的总行数Row可通过源tile大小和Col计算得到。
- **SrcType**：指定源元素类型，当前版本仅支持 u16 或 u32。
- **DstType**：指定输出累计计数元素类型，用于描述 DstTile 中累计计数的存储类型，支持u8/u16/u32/u64。
- **ByteId**：指定要统计的目标字节，可取 Byte0、Byte1、Byte2、Byte3（u16输入时仅Byte0和Byte1有效）。
- **SrcTile**：为输入源 tile，`.reuse` 表示该 tile 可按复用语义保留供后续指令继续使用。
- **IdxTile**：为索引/过滤 tile，其元素表示过滤用的字节值。
    - 对 uint16 + Byte0，idx[row,0] 保存该行高字节过滤值。
    - 对 uint32，idx 按行保存高位前缀过滤值：
        - idx[0, 0]：用于过滤 Byte3。
        - idx[1, 0]：用于过滤 Byte2。
        - idx[2, 0]：用于过滤 Byte1。
        - 当统计 Byte3 时不需要过滤，IdxTile 可作为占位操作数。
- **DstTile**：为输出 tile，Size 表示输出 tile 的目标大小配置。

## 编码格式

本TileOp编码为以下指令：

- [BSTART.TEPL](../../blockIntro/tepl_block/header.md) `THISTOGRAM, SrcType`
- [B.DATR](../B.DATR.md) `DstType, ByteId, PadValue`
- [B.DIM](../B.DIM.md) `reg, imm, ->LB0`     *（注：ValidCol）*
- [B.DIM](../B.DIM.md) `reg, imm, ->LB1`     *（注：ValidRow）*
- [B.DIM](../B.DIM.md) `reg, imm, ->LB2`     *（注：Col）*
- [B.IOT](../B.IOT.md) `SrcTile<.reuse>, idxTile<.reuse>, last, ->DstTile<Size>`

对于 uint16输入：

| 字节参数 | 含义 | 过滤规则 |
|---------|-------|----------|
| Byte1 | 高字节，MSB | 无过滤 |
| Byte0 | 低字节，LSB | 仅统计高字节等于 idx[row, 0] 的元素 |

对于 uint32输入：

| 字节参数 | 含义 | 过滤规则 |
|----------|-------|---------|
| Byte3 | 最高字节，MSB | 无过滤 |
| Byte2 | 次高字节 | `byte3 == idx[0, 0]` |
| Byte1 | 次低字节 | `byte3 == idx[0, 0] && byte2 == idx[1, 0]` |
| Byte0 | 最低字节，LSB | `byte3 == idx[0, 0] && byte2 == idx[1, 0] && byte1 == idx[2, 0]` |

## 执行方式

实现方式概述：

1. 对 src 的每个有效行独立统计。
2. 每行遍历 src 的有效列元素。
3. 从元素中提取指定的 Byte 字段。
4. 根据 Byte 模式和 idx 提供的过滤值决定元素是否参与计数。
5. 对 256 个字节取值的计数结果做前缀和。
6. 将累计计数写入 dst[row, 0..255]。

实现伪代码如下：
```py
for row in 0 .. src.Rv - 1:
counts[0..255] = 0
    for col in 0 .. src.Cv - 1:
        value = src[row, col]
        if src is uint16:
            byte1 = high_byte(value)
            byte0 = low_byte(value)

            if Byte == BYTE_1:
                counts[byte1] += 1
            if Byte == BYTE_0:
                if byte1 == idx[row, 0]:
                    counts[byte0] += 1
        if src is uint32:
            byte3 = highest_byte(value)
            byte2 = second_high_byte(value)
            byte1 = second_low_byte(value)
            byte0 = lowest_byte(value)

            if Byte == BYTE_3:
                counts[byte3] += 1
            if Byte == BYTE_2:
                if byte3 == idx[0, 0]:
                    counts[byte2] += 1
            if Byte == BYTE_1:
                if byte3 == idx[0, 0] and byte2 == idx[1, 0]:
                    counts[byte1] += 1
            if Byte == BYTE_0:
                if byte3 == idx[0, 0] and byte2 == idx[1, 0] and byte1 == idx[2, 0]:
                    counts[byte0] += 1
    prefix = 0
    for k in 0 .. 255:
        prefix += counts[k]
        dst[row, k] = prefix
```

输入元素为 u16（uint16_t）格式 时，元素拆分为 `BYTE_1` 和 `BYTE_0`。`BYTE_1` 模式直接统计高字节；`BYTE_0` 模式在高字节等于 idx[row,0] 时统计低字节。

![THISTOGRAM_u16](../../../figs/isa/tileop/THISTOGRAM_u16.svg)

输入元素为u32（uint32_t）格式时，元素拆分为 `BYTE_3`、`BYTE_2`、`BYTE_1`、`BYTE_0`。`BYTE_3` 无过滤；统计更低字节时，使用 idx 中保存的高位前缀值进行级联过滤。

![THISTOGRAM_u32](../../../figs/isa/tileop/THISTOGRAM_u32.svg)

下面以 Byte1为例展示统计结果，左侧源数据提取目标字节后得到原始频次 counts，再经过前缀累积写入dst。因此dst 中保存的是累积计数，而不是单个取值的原始频次。

![THISTOGRAM_result](../../../figs/isa/tileop/THISTOGRAM_result.svg)

## 指令约束

- SrcType 支持 u16(uint16) 或 u32(uint32)。
- IdxTile 用于保存过滤字节值，按字节粒度解释。
- DstTile.ValidCol 必须大于等于 256。
- DstTile 的有效行应覆盖 validRow 对应的输出行。
- u16 源元素只支持 Byte1 和 Byte0 两种统计模式。
- u32 源元素支持 Byte3、Byte2、Byte1、Byte0 四种统计模式。
- 统计 u32.Byte3 或 u16.Byte1 时无过滤；统计更低字节时必须保证 IdxTile 中的过滤值已经正确设置。
- 输出为累计计数，而不是单独频次计数；即 dst[row, k] 保存的是取值 0..k 的累计结果。
- 指令只处理 validRow × validCol 描述的有效区域，其他元素不参与统计。
- DstTile 的 Size 配置应能容纳每个有效行 256 个累计计数结果。

## 汇编示例

示例1：统计 uint32 源数据中满足高位前缀的 Byte1
```asm
THISTOGRAM <LB0:64, LB1:4, LB2:64, u32, u32, Byte1>, T#3.reuse, U#1, ->T<4KB>
```

该示例表示：对 SrcTile 中 4 个有效行、每行 64 个有效元素进行统计，源元素类型为 uint32，目标统计字节为 Byte1。由于统计的是 Byte1，指令仅统计满足以下前缀条件的元素：
```c
byte3 == idx[0, 0] && byte2 == idx[1, 0]
```

参数说明：

- validCol = 64：每个有效行统计 64 个源元素。
- validRow = 4：共统计 4 个有效行，并产生 4 行累计计数输出。
- Col = 64：源 tile 的总列数或行内列跨度为 64。
- SrcType = u32：源元素为 32 位无符号整数，可拆分为 Byte3/Byte2/Byte1/Byte0。
- DstType = u32：输出累计计数以 32 位无符号整数保存。
- Byte1：表示目标统计字节为 uint32 元素中的次低字节。
- T#3.reuse：输入源 tile，并带复用标记。
- U#1.reuse：过滤 tile，并带复用标记；调用前需要写入高位前缀过滤值：
    - idx[0, 0] 保存目标 Byte3 值。
    - idx[1, 0] 保存目标 Byte2 值。
- T<4KB>：输出 tile，示例中 `Size=4KB`，用于容纳 4 × 256 个u32类型累计计数结果。

执行后，dst[row,k] 保存第 row 行中满足上述高位前缀条件，且 Byte1 取值小于等于 k 的元素数量。

示例2：统计 uint16 源数据的低字节
```asm
THISTOGRAM <LB0:128, LB1:2, LB2:128, u16, u32, Byte0>, M#1, N#2.reuse, ->T<2KB>
```

该示例表示：对 uint16 源元素统计低字节 Byte0，但仅统计高字节 Byte1 等于 idx[row,0] 的元素。validCol=128 表示每行统计 128 个元素，validRow=2 表示输出 2 行累计计数，T<2KB> 用于容纳 2 × 256 个累计计数结果。执行后，dst[row,k] 表示该行中满足高字节过滤条件，且低字节取值小于等于 k 的累计计数。
