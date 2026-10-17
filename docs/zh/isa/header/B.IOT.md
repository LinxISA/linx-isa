# B.IOT

唯一规范来源: [PTO-SPEC golden](https://github.com/PTO-ISA/pto-spec/blob/f0a876e449a95d26841c5ee7affb4c905ebc5f5b/asl/block/operands/B.IOT.asl).

## 汇编形式

```asm
B.IOT SrcTile0.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0.reuse, SrcTile1.reuse, mask=PE_MASK, <last>
B.IOT SrcTile0.reuse, SrcTile1.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0.reuse, mask=PE_MASK, <last>
B.IOT mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>
B.IOT SrcTile0.reuse, SrcTile1, mask=PE_MASK, <last>
B.IOT SrcTile0, SrcTile1.reuse, mask=PE_MASK, <last>
B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0.reuse, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0, SrcTile1.reuse, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0, mask=PE_MASK, <last>
B.IOT SrcTile0, mask=PE_MASK, <last>, ->DstTile<SizeCode>
```

## 编码

| PTO form | mask | match | fields |
| --- | --- | --- | --- |
| `b_iot_32_10db6db84f5d` | `0xfc00707f` | `0x00005013` | SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_2c07e7177fad` | `0x0007f1ff` | `0x00004013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_8b8bce6bffe8` | `0x0000707f` | `0x00004013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_c11eb189dd83` | `0xfc07f1ff` | `0x00005013` | SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_efa0fe3fe49a` | `0xfff0707f` | `0x00006013` | L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_ll_src` | `0x0007f1ff` | `0x00002013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_rl_src` | `0x0007f1ff` | `0x00003013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_lr_src` | `0x0007f1ff` | `0x00007013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_ll_dst` | `0x0000707f` | `0x00002013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_rl_dst` | `0x0000707f` | `0x00003013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_lr_dst` | `0x0000707f` | `0x00007013` | SrcTile1=31:26; SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |
| `b_iot_32_last_src` | `0xfc07f1ff` | `0x04005013` | SrcTile0=25:20; L=19:19; PEMode=11:9 |
| `b_iot_32_last_dst` | `0xfc00707f` | `0x04005013` | SrcTile0=25:20; L=19:19; SizeCode=18:15; PEMode=11:9; DstTile=8:7 |

## 语义边界

显式 `.reuse` 保留所选源的数据；省略 `.reuse` 表示最后一次使用，在成功且未被取消的块完成时消耗对应的数据容量。旧编码的规范打印形式包含 `.reuse`。
Local 源按参与 PE 消耗数据容量；Shared 源消耗完整 Core 范围的数据容量。寄存器代次身份和描述符保留。
`PEMode=000` 在位置、重复、分配、描述符及内存检查前为严格无副作用路径。其他 PEMode 的四 PE mask 由 golden 公共译码器定义。
B.IOT 的终止位 L 与源最后使用标记是不同维度。每个源的 `.reuse` 独立编码。B.IOS 使用绝对 Shared 名称 S0..S63。
纯源 `SizeCode=0` 不分配目的。Local 目的使用 1..10，每 PE 为 128 B..64 KiB；Shared 目的使用 1..12，完整 Core 对象为 128 B..256 KiB。其余大小码保留。
完整合法性、异常和状态转换以以上 PTO owning ASL 为准；本页编码表直接生成自同一 golden。

## 模型支持

新增 LAST/LL/LR/RL 形式尚未在 Linx Sail 子集中实现；模型在产生效果前拒绝。编码存在不等于执行支持。
