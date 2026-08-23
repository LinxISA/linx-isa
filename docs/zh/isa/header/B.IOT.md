# B.IOT

## 功能

`B.IOT` 按编码顺序绑定 Local Tile 源和目的寄存器。它只使用
`T#1..T#16`、`U#1..U#16`、`M#1..M#16` 与 `N#1..N#16` 的相对
Local 队列空间，不绑定 Shared `S0..S255`。

机器可读目录 `isa/v0.58/linxisa-v0.58.json` 是编码唯一权威来源。

## 五种规范形式

```asm
B.IOT SrcTile0, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>
B.IOT SrcTile0, SrcTile1, mask=PE_MASK, <last>, ->DstTile<SizeCode>
B.IOT SrcTile0, mask=PE_MASK, <last>
B.IOT mask=PE_MASK, <last>, ->DstTile<SizeCode>
```

不存在 `.reuse` 后缀。`L`/`last` 只终止当前有效 B.IOT 绑定序列，绝不
释放源寄存器。

## 编码字段

| 位 | 字段 | 含义 |
| --- | --- | --- |
| 31:26 | `SrcTile1` 或固定零 | 第二个 Local 源 |
| 25:20 | `SrcTile0` 或固定零 | 第一个 Local 源 |
| 19 | `L` | 当前有效绑定之后终止序列 |
| 18:15 | `SizeCode` | 0 为纯源；目的形式使用 1..10 |
| 14:12 | `Func` | `100` 两源、`101` 一源、`110` 无源 |
| 11:9 | `PEMode` | 三位参与模式 |
| 8:7 | `DstTile` | 0 T、1 U、2 M、3 N |
| 6:0 | 固定 `0010011` | 次编码 |

`PEMode` 使用 PTO ISA 0.58.3 的公共固定译码表：

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

`PEMode=000` 在 placement、duplicate、schema、allocation、descriptor、
memory 和 downstream fault 检查之前形成严格无副作用路径。

## SizeCode

纯源形式固定 `SizeCode=0`，不分配目的。目的形式仅允许 1..10：

| `SizeCode` | 每个参与 PE 的目的容量 |
| --- | --- |
| 1 | 128 B |
| 2 | 256 B |
| 3 | 512 B |
| 4 | 1 KiB |
| 5 | 2 KiB |
| 6 | 4 KiB |
| 7 | 8 KiB |
| 8 | 16 KiB |
| 9 | 32 KiB |
| 10 | 64 KiB |
| 11..15 | 保留，非法指令 |

目的容量按参与 PE 计算，core 总分配量为
`popcount(decoded_mask) * per-PE capacity`，且不得超过 256 KiB。

## 顺序与异常

- 有效 B.IOT 只能出现在 BSTART 之后、第一条块体指令之前。
- 一个块最多接受四个有效 Local 绑定，并按编码顺序匹配操作 schema。
- 所有有效绑定必须具有相同的译码后 PE mask。
- `L=1` 关闭序列；关闭后出现另一条有效 B.IOT，在产生状态变化之前报
  Illegal Block Exception。
- 保留位、保留 SizeCode 或畸形组合在产生架构副作用之前报非法指令。
- 描述符不兼容、mask 扩展或 schema 角色不匹配在 Tile 状态变化之前
  报 Fault_TileLegality。

## 示例

两个 Local 源、一个 16 KiB/PE 的 T-hand 目的，四个 PE 参与：

```asm
B.IOT T#1, U#1, mask=1111, last, ->T<8>
```

纯源绑定，PE0 与 PE1 参与：

```asm
B.IOT M#1, mask=1100, last
```

零参与严格无副作用：

```asm
B.IOT T#1, mask=0000, last
```
