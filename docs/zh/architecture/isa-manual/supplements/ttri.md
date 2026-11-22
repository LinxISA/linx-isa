<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:SFU:3:7:TTRI", "kind": "tile", "name": "TTRI", "pto_instruction_sha256": "58712f2a998b833493fcb4993c03fd206a3e1e43000e4d3193ab646d2ddc286d", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/irregular-and-complex/initialization/TTRI.asl", "pto_source_sha256": "5082458f6e0b1f27af9852b27590628628ea6fe222e719e0ba8fff0c4390301c", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/irregular-and-complex/initialization/TTRI.md", "reader_source_sha256": "cec2bce17263034908b9f6052699dc22c125e12584b54ce7d451fe36e2aa01d2", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TTRI

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TTRI 把一个由类型化的一和零组成的三角掩码写入新分配的 Local RowMajor Tile。它不读取任何源 Tile；对角线与方向来自 GPR。

## 输入与输出

- destination0 是新分配的 Local RowMajor Tile，类型为 FP64、FP32、FP16、S64、S32、S16、U64、U32 或 U16。
- diagonal 是从 RegSrc0 读取的有符号位移；它必须位于 -65535 到 65535 之间。
- flag0 是从 RegSrc1 读取的方向：0 选择下三角，1 选择上三角。RegSrc2 与 RegDst 必须为零。
- 省略 B.DIM LB0 时取架构默认值一；显式编码的零非法，因为 ValidCol 必须非零。LB1 默认使 ValidRow 为 1，LB2 默认为 Col = ValidCol。省略 B.IOR 选择对角线 0 与下三角方向；显式全零 B.IOR 读取 GPR0，并给出相同的值。
- 存在的 B.DATR 必须所有字段为零。只允许恰好一条终止的仅目标 B.IOT。

## 执行结果

- 没有源 Tile，也没有源操作数快照。三角载荷、目标描述符以及每个元素的已定义性作为一次操作发布；每个有效元素都变为已定义。
- 有效区域之外的物理元素接收 Null 填充：一个保持未定义的零载体。TTRI 没有全局内存、GPR 或数值状态效果。

## 示例

下面的示例只帮助理解当前 ASL 绑定契约，并不是第二份指令定义。

一个 FP32 目标有 3 个有效行、4 个有效列，下三角方向，对角线为 0，保存下面各行，其中 1 表示 0x3f800000。若对角线改为 1，每行多一个一：1 1 0 0，然后 1 1 1 0，然后 1 1 1 1。

~~~asm
row 0: 1 0 0 0
row 1: 1 1 0 0
row 2: 1 1 1 0
~~~

同样的对角线 0 在上三角方向下，在 c >= r 处写入一：1 1 1 1，然后 0 1 1 1，然后 0 0 1 1。两种方向下主对角线都为一。

## 合法性与异常

- 绑定格式错误、B.IOS、不支持的类型、非 RowMajor 布局、维度缺失或无效、方向不是 0 或 1、对角线超出 -65535 到 65535，或非零 B.DATR 字段，会在分配之前引发 Fault_TileLegality。
- 形状无法表示、目标寄存器不可用、TSize 过小或 Tile 容量耗尽，会在分配之前引发 Fault_TileAllocation。
- PE_MASK=0000 在 B.IOT 的 size code 编码检查之后是严格无操作：不再进行 GPR 读取、描述符检查、分配或操作故障，但非法的 B.IOT size code 仍会引发 Fault_IllegalInstruction。

## 0.59.1 来源

- 当前身份：tile:SFU:3:7:TTRI
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x067
- PTO 源：asl/tile/irregular-and-complex/initialization/TTRI.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
