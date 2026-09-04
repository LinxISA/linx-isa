# B.IOS

## 功能

`B.IOS` 为一个块操作绑定一个绝对索引的 Shared Tile 寄存器。每个 core
拥有一组私有的 `S0` 到 `S63`；同一 core 的四个 PE 都能访问该组中的
全部寄存器。另一个 core 中同名的 `Sx` 属于另一组寄存器。Shared
寄存器的架构编号由编译器分配，硬件可以对选中的架构寄存器进行重命名。

机器可读指令目录是编码的唯一权威来源。本页只解释该记录，不建立另一套编码定义。

## 汇编语法

源绑定：

```asm
B.IOS S<SharedTileID>, mask=<PE_MASK>
```

目的绑定：

```asm
B.IOS mask=<PE_MASK>, ->S<SharedTileID><SizeCode>
```

`SharedTileID` 是 0 到 63 的绝对整数。规范汇编名称因此是 `S0` 到
`S63`；不接受 `S#1` 这样的相对编号写法。

## 编码

![B.IOS 编码](../wavedrom/enc_b_ios.svg)

| 位 | 字段 | 含义 |
| --- | --- | --- |
| 31:26 | 固定 `000000` | 主编码 |
| 25:20 | `SharedTileID` | 0 到 63 的 Shared 寄存器绝对索引 |
| 19 | 固定 `0` | 固定保留位；其他值不属于 `B.IOS` |
| 18:15 | `SizeCode` | 源/目的角色与完整 Core-wide 目的对象容量 |
| 14:12 | 固定 `001` | 功能选择码 |
| 11:9 | `PEMode` | 固定四 PE 参与模式 |
| 8:0 | 固定 `000010011` | 次编码 |

32 位解码标识为 mask `0xfc0871ff`、match `0x00001013`。PTO 来源
form 是 `b_ios_32_4ba5ef98fdaa`，独立 Linx 目录中的 form 是
`b_ios_32_2f2d1ab83761`。

全部 64 个 `SharedTileID` 值和全部八个 `PEMode` 值均已分配。
`PEMode` 按下表译码：

| `PEMode` | 语义 mask |
| --- | --- |
| 0 | `0000`（无 PE） |
| 1 | `1000`（PE0） |
| 2 | `0100`（PE1） |
| 3 | `0010`（PE2） |
| 4 | `0001`（PE3） |
| 5 | `1100`（PE0+PE1） |
| 6 | `1110`（PE0+PE1+PE2） |
| 7 | `1111`（四个 PE） |

四位 `SizeCode` 按下表分配：

| `SizeCode` | 形式 | 完整 Core-wide 目的对象容量 |
| --- | --- | --- |
| 0 | 源绑定 | 不适用；不分配目的寄存器 |
| 1 | 目的绑定 | 128 B |
| 2 | 目的绑定 | 256 B |
| 3 | 目的绑定 | 512 B |
| 4 | 目的绑定 | 1 KiB |
| 5 | 目的绑定 | 2 KiB |
| 6 | 目的绑定 | 4 KiB |
| 7 | 目的绑定 | 8 KiB |
| 8 | 目的绑定 | 16 KiB |
| 9 | 目的绑定 | 32 KiB |
| 10 | 目的绑定 | 64 KiB |
| 11 | 目的绑定 | 128 KiB |
| 12 | 目的绑定 | 256 KiB |
| 13..15 | 保留 | 非法指令 |

固定字段不匹配的字不解码为 `B.IOS`。

## 操作

汇编操作数 `PE_MASK` 必须是上表八种语义 mask 之一；汇编器将其编码为
对应的 `PEMode`。`PEMode=000` 是所有 placement、
duplicate、schema、allocation、descriptor、memory 和 fault 检查之前的
严格无副作用路径。目的容量描述一个完整的 Core-wide Shared 对象；mask
不会扩大该容量，也不会隐式把对象划分为各 PE 的 quarter。

源绑定使用 `SizeCode=0`。参与的 PE 读取指定 Shared 寄存器，并且读取
不会修改描述符。读取未初始化的 Shared 寄存器会得到未定义值，其行为
与读取未定义的标量寄存器相同。

目的绑定使用 `SizeCode=1` 到 `SizeCode=12`。选中的 Shared 架构寄存器需要
获得新的分配，同时更新其描述符。Shared 写操作以一次原子的
read-modify-write 同时更新描述符和 payload 状态。除了该原子属性之外，
架构不规定 PE 之间的顺序；软件必须避免不同 PE 使用冲突的 offset。

表中的容量始终是完整 Core-wide 对象容量。描述符中的 rows 和 columns 都必须是 2
的次幂。rows 由 `SizeCode`、columns 和元素大小推导；valid rows 和 valid
columns 不能超过已分配 shape。矩阵操作也遵循同一 shape 约束。

## 示例

将 `S7` 作为 PE0 和 PE1 的源：

```asm
B.IOS S7, mask=1100
```

在 `S23` 中分配一个 128 B 的 Core-wide Shared 对象，并让四个 PE
全部参与：

```asm
B.IOS mask=1111, ->S23<128B>
```

完全禁止该绑定：

```asm
B.IOS S7, mask=0000
```

`B.IOT` 仍是独立的 Local Tile 绑定指令，不绑定 Shared `S0` 到
`S63` 寄存器组。
