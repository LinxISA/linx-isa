# B.IOS

## 功能

`B.IOS` 为块操作绑定一个 core 私有的 Shared Tile 寄存器。每个 core
拥有 `S0` 到 `S63`，该 core 的四个 PE 共享这组寄存器；另一个 core 中
同名的寄存器属于另一组 bank。

生成页 [`B.IOS`](/isa/instructions/b_ios/) 与机器可读目录是编码和
合法性的权威来源。本页只解释 Shared 寄存器模型，不建立第二套指令合约。

## 汇编

```asm
B.IOS S<SharedTileID>, mask=<PE_MASK>
B.IOS mask=<PE_MASK>, ->S<SharedTileID><SizeCode>
```

`SharedTileID` 是 6 bit 绝对索引，规范名称为 `S0` 到 `S63`；不接受
`S#1` 这样的相对编号。

## 编码身份

![B.IOS 编码](../wavedrom/enc_b_ios.svg)

| 位 | 字段 | 含义 |
| --- | --- | --- |
| 31:26 | 固定零 | 保留位 |
| 25:20 | `SharedTileID` | `S0` 到 `S63` 的绝对索引 |
| 19 | 固定零 | 保留位 |
| 18:15 | `SizeCode` | 源角色或完整 Shared 对象容量 |
| 14:12 | 固定 `001` | 功能选择码 |
| 11:9 | `PEMode` | 固定四 PE 参与模式 |
| 8:0 | 固定 `000010011` | 次编码 |

解码 mask 为 `0xfc0871ff`，match 为 `0x00001013`。PTO 来源 form 是
`b_ios_32_4ba5ef98fdaa`，编译后的 Linx form 是
`b_ios_32_2f2d1ab83761`。

`PEMode` 的 0 到 7 依次映射为 `0000`、`1000`、`0100`、`0010`、
`0001`、`1100`、`1110`、`1111`。`PEMode=000` 在 placement、重复、
schema、allocation、描述符（descriptor）、memory 与 fault 检查之前就是严格无副作用
路径。

`SizeCode=0` 表示源。目的代码 `SizeCode=1` 到 `SizeCode=12` 分别表示完整 core-wide Shared
对象的 128 B、256 B、512 B、1 KiB、2 KiB、4 KiB、8 KiB、16 KiB、
32 KiB、64 KiB、128 KiB 与 256 KiB；`13..15` 非法。该容量不会乘以
参与 PE 数量。

## 状态行为

源绑定只读，不改变 Shared descriptor、allocation mask、initialized mask
或 payload；读取未初始化寄存器得到 undefined-register value。

单 PE 目的原子发布完整 Shared parent。多 PE 目的通过 `B.ASSEMBLE`
给出互不重叠的显式范围，并只在 `LAST` 时发布。schema、容量、范围、
readiness 和 allocation 检查必须先于任何可见 descriptor 或 payload
效果完成。

除原子发布规则外，架构不规定冲突 PE 访问之间的顺序；软件必须避免冲突
或建立独立同步。

## 示例

```asm
B.IOS S7, mask=1100
B.IOS mask=1111, ->S23<0001>
B.IOS S7, mask=0000
```

`B.IOT` 仍绑定 Local Tile，不命名 Shared `S0` 到 `S63` bank。
