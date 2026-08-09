# TEPL 编码载体

## 架构角色

TEPL 是 PTO Tile 操作保持不变的 Mode/Function 编码载体，不是执行单元。
每个合法 TEPL selector 都由 v0.58 机器可读目录分类，并且只派发到一个执行单元：

| 执行单元 | 职责 | 操作数量 |
|---|---|---:|
| **VEC** | Tile/Tile 与 Tile/标量的逐元素计算 | 35 |
| **SFU** | 复杂函数、归约/展开、重排和不规则计算 | 52 |

TLSU 与 CUBE 保留各自的编码族和执行单元。因此完整的 Tile 执行单元集合为
`VEC`、`SFU`、`TLSU`、`CUBE`。

## 编码与汇编

TEPL 的 Mode/Function 编码不变。`BSTART.TEPL` 是唯一编译后的译码身份。
汇编器还接受：

- 当所选操作在目录中属于 VEC 时使用 `BSTART.VEC`；
- 当所选操作在目录中属于 SFU 时使用 `BSTART.SFU`。

规范反汇编根据所选操作的执行单元输出 `BSTART.VEC` 或 `BSTART.SFU`。
这些别名不占用新编码空间，也不产生额外译码身份。

## 分类

七个规范语义类别如下：

| 类别 | 执行单元归属 | 数量 |
|---|---|---:|
| elementwise-tile-tile | 由目录指定为 VEC 或 SFU | 25 |
| tile-scalar-and-immediate | VEC | 15 |
| reduce-and-expand | SFU | 28 |
| memory-and-data-movement | TLSU | 9 |
| matrix-and-matrix-vector | CUBE | 12 |
| layout-and-rearrangement | 由目录指定为 SFU 或 TLSU | 7 |
| irregular-and-complex | SFU | 13 |

VEC 只执行逐元素计算。需要复杂硬件的操作，包括超越函数、归约、展开和
不规则处理，均由 SFU 执行。每条操作的精确归属以
`isa/v0.58/state/pto_ops.json` 为规范来源，说明文档不得重新定义第二套分类。

## 块行为

TEPL 承载的操作是头部驱动的 Tile 操作，不包含 SIMT 块体，`B.TEXT` 非法。
操作数与描述符要求由所选操作和生成的 v0.58 目录定义。

除非具体指令页面规定更严格的规则，TEPL 承载的块只支持顺序落下。
它们操作 Tile 状态，不能替代 TLSU 的内存搬运或 CUBE 的矩阵执行。
