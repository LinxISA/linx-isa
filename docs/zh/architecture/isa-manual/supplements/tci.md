<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:SFU:3:6:TCI", "kind": "tile", "name": "TCI", "pto_instruction_sha256": "e0eb18cef9f926710745f62726cb13713cb12675c8a65f56e5fffcb07c9991c4", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/irregular-and-complex/initialization/TCI.asl", "pto_source_sha256": "bd4548e4d2bb8905aa9e8ceeb4922512fcf6630889ec6eb5af985b960988dfea", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/irregular-and-complex/initialization/TCI.md", "reader_source_sha256": "f36dc6e98ffaed232157c3b64c7f563c9da78e837479dbb2d8ca4af6be86dc49", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TCI

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TCI 把一个整数索引序列写入新分配的 Local Tile。它不读取任何源 Tile；唯一的输入是从通用寄存器（GPR）取得的起始值以及方向或步长字。

它有两种形式。RowMajor 形式写一行。CUBE 形式把二维模式写入 CUBE_M16 或 CUBE_M32 Tile。

CUBE 形式只能由显式 B.DATR Layout 为 CUBE_M32（29）或 CUBE_M16（31）选中，因此不带该元组的指令束始终保持 RowMajor 形式。

## 输入与输出

- destination0 是新分配的 Local S64、S32、S16、U64、U32 或 U16 Tile。
- scalar0 是起始值，从 RegSrc0 指定的 GPR 读取。
- flag0 是 RowMajor 方向或 CUBE Step2D 字，从 RegSrc1 指定的 GPR 读取。
- RowMajor 形状：B.DIM LB0 是必需的，给出非零 ValidCol。LB1 默认为 1，显式 LB1 也必须等于 1。LB2 默认为 Col = ValidCol。省略 B.IOR 选择起始值 0 与递增方向；显式全零 B.IOR 给出相同的值。
- CUBE 形状：LB1 给出正的 ValidRow，CUBE_M16 时不超过 16。显式 LB2 是精确的物理 Col，必须按 cell 列粒度对齐；省略 LB2 时把 ValidCol 向上对齐到该粒度。存在的 B.DATR 必须使用 DataType=DTYPE_NONE，且 Pad、CMode、RMode、Sat 与 Canonicalize 全为 0；并且恰好一条 B.IOR 必须依次指定 StartGPR、Step2DGPR、zero 与 ->zero。
- 目标保持 BSTART 数据类型。只允许恰好一条终止的 B.IOT：除非由 PredicateCell 提供 ExecutionMask，否则它只绑定目标；此时同一条 B.IOT 还必须把该谓词 Tile 绑定为源。第二条 B.IOT、B.IOS 或任何其他源绑定均非法。

## 执行结果

- 序列载荷、目标描述符以及每个元素的已定义性作为一次操作发布。每个有效元素都变为已定义。
- 有效区域之外的物理元素接收 Null 填充：它们保存零载体但保持未定义。TCI 不携带 PadValue，因此之后的已定义性检查不会把填充视为生成的数据。
- TCI 没有全局内存效果，不写任何 GPR，也不记录数值状态。被拒绝的指令束不发布任何内容。

## 示例

U16 RowMajor 目标有 4 个有效列，起始寄存器保存 0x1fffe，方向为递增。起始值被截断为 65534，因此该行为 65534、65535、0、1；第三个值是 65536 截断到 16 位的结果。

U16 CUBE_M16 目标的 ValidRow 为 2、ValidCol 为 3，起始值为 5，Step2D 为 0xFFFFFFFF00000001，即 RowStep -1、ColStep +1。第 0 行为 5、6、7，第 1 行为 4、5、6。

以宏形式表示，使用默认起始值与方向的 64 元素 U32 序列写作下面的形式。256B 目标容纳 64 x 4 = 256 字节。

TCI <Row=1, Col=64, U32>, ->T<256B>

## 合法性与异常

- 可接受的数据类型为 S64、S32、S16、U64、U32 与 U16。64 位 CUBE 形式要求 CUBE_M32；这些类型在 CUBE_M16 中仍非法。
- RowMajor 形式：绑定格式错误、B.IOS、不支持的类型、维度缺失或无效、方向不是 0 或 1，或非零的不适用 B.DATR 字段，会引发 Fault_TileLegality。
- CUBE 形式：命令或 B.IOR 结构格式错误引发 Fault_BundleControl；无效的选择器、元组、维度、步长或对齐引发 Fault_TileLegality；几何合法但 TSize 过小或 Tile 容量耗尽时引发 Fault_TileAllocation。
- PE_MASK=0000 在 B.IOT 的 size code 编码检查之后是严格无操作：不再进行模式验证、GPR 读取、分配或操作故障，但非法的 B.IOT size code 仍会引发 Fault_IllegalInstruction。
- 所有拒绝都发生在分配或发布之前，因此故障不会留下部分序列。

## 0.59.1 来源

- 当前身份：tile:SFU:3:6:TCI
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x066
- PTO 源：asl/tile/irregular-and-complex/initialization/TCI.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
