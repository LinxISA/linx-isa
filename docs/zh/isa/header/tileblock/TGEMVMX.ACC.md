# TGEMVMX.ACC

## 说明

将 1×K 的行向量 A 与 K×N 的矩阵 B 相乘，按各输入的类型使用相应的缩放因子，再加上显式输入 Tile C 的对应元素。把结果写入新分配的目标 Tile D。

## 操作数

| 操作数 | 用途 |
| --- | --- |
| `destination0` | D |
| `source0` | C（累加源） |
| `source1` | A（行向量） |
| `source2` | A 的缩放 Tile（按输入类型绑定） |
| `source3` | B（矩阵） |
| `source4` | B 的缩放 Tile（按输入类型绑定） |

C 是本地累加源，D 是独立的本地输出。解码时，C 的相对编号必须与零扩展的 DstTile 不同。两侧独立选择缩放。某侧使用 FP16 或 BF16 时省略该侧的缩放 Tile，MX FP8 或 FP4 输入使用每 32 个元素一组的 E8M0 缩放，HiF4X2 输入使用每 64 个元素一组的 U32 缩放。该操作的发布摘要漏列了 HiF4X2 的例外，此处按同版模型的类型检查和分组函数说明。[矩阵缩放类型与组宽定义](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-functions.asl#L29)

## 执行方式

M 固定为 1，只能使用本地输入；TransA 和 TransB 均为零。块头使用 `BSTART.TGEMVMX.ACC AType`，并且必须有一条 B.FPATR 来指定后处理。数值运算先形成累加值，再按块头配置处理并发布 D。

## 示例

看输出中的一个位置。取两侧缩放因子为 1，若 A 的一行为 [2, 3]，B 的对应列为 [4, 5]，点积为 2×4 + 3×5 = 23。若 C 的对应元素为 7，后处理前的累加值为 30。
