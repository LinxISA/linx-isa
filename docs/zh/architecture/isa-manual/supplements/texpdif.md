<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:SFU:0:29:TEXPDIF", "kind": "tile", "name": "TEXPDIF", "pto_instruction_sha256": "586521af63b10c3d28482206887647794e9c9224a8ded088f0473cf30503690e", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/elementwise-tile-tile/transcendental/TEXPDIF.asl", "pto_source_sha256": "1f5e9c00ce25b71ef34d8108a17b320765e23be55e25fecf6cafeb30ed1b1f75", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/elementwise-tile-tile/transcendental/TEXPDIF.md", "reader_source_sha256": "a1ec79e42bb7b9a9a91f543b04e008957dce14d5f05af8522c856f93894de8f7", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TEXPDIF

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TEXPDIF 在两个 Local 浮点 Tile 上逐元素计算 exp(source0 - source1)，并把结果写入一个新分配的 Local 目标 Tile。与 TADD 不同，目标类型可以比源类型更宽，且该操作在 SFU 引擎上执行。

其规范头部写作 BSTART.SFU TEXPDIF, SrcOperationType。头部类型给出源操作类型；目标类型来自 B.DATR。

## 输入与输出

- source0 是持久的被减数，按 SrcOperationType 解释。
- source1 是持久的减数，按 SrcOperationType 解释。
- destination0 是新分配的 Local Tile，其后备类型为目标类型 DstDataType。
- 一条终止 B.IOT 绑定全部三个 Tile，它们共享一个 PE_MASK。PE_MASK=0000 是严格无操作，发生在源描述符读取、目标分配、数值状态或载荷效果之前。
- DstDataType 由 B.DATR 解析。省略 B.DATR，或把 DataType 字段编码为 DTYPE_NONE（代码 31），会使目标继承 SrcOperationType。编码为零的 DataType 显式选择 FP64；它不表示缺省。
- 使用 DTYPE_NONE 使“未请求目标类型”与真实的类型请求保持区分。
- 每个源的后备类型都可以独立地不同于 SrcOperationType，前提是两种类型都非打包、元素位宽相同且载体兼容。源位按 SrcOperationType 校验和解释，源描述符不会被重新标记类型。

## 执行结果

- 目标描述符、有效区域内的结果、填充、每个元素的已定义性以及累积的数值状态同时发布。被拒绝的指令束不发布任何目标载荷、填充、描述符或状态，两个源也保持不变。
- ValidRow x ValidCol 之外的物理元素接收所选 PadValue。Zero 写入零；Max 与 Min 写入目标类型的最大与最小有限值；Null 使这些元素保持未定义。省略 B.DATR 选择 Null，而显式编码 00 选择 Zero。
- 由于两个源都在写入任何结果之前被快照，源与目标之间的合法别名会读取旧的源值。TEXPDIF 没有全局内存效果。存在 ExecutionMask 时，非活动坐标接收该掩码规定的零值或合并值，且不贡献状态。

## 示例

对混合类型对 (FP16,FP32)，被减数行 [1.0, 2.0] 与减数行 [1.0, 1.0] 被加宽到 FP32，得到差 [0.0, 1.0]。目标行为 FP32 的 [1.0, e]，其中 exp(0) 恰为 1.0，e 约为 2.71828。

对 RowMajor 中 8 x 64 的有效形状，每个 FP16 源占 8 x 64 x 2 = 1024 字节，而 FP32 目标需要 8 x 64 x 4 = 2048 字节。头部写作 BSTART.SFU TEXPDIF, FP16，B.DATR 选择目标 DataType FP32。同类型的 FP32 形式不需要 B.DATR，其宏形式写作 TEXPDIF <Row=8, Col=64, FP32>, T#1, T#2, ->T<2KB>。

## 合法性与异常

- 合法的 (SrcOperationType,DstDataType) 对为 (FP64,FP64)、(FP32,FP32)、(FP16,FP16)、(BF16,BF16)、(FP16,FP32) 与 (BF16,FP32)。其他任何类型对，包括变窄类型对或整数类型，都会被拒绝。CUBE FP64 形式要求 CUBE_M32。
- 布局为 RowMajor、CUBE_M16 或 CUBE_M32，三个操作数必须使用所选布局。CUBE_N8、Shared Tile 以及混合布局均非法。各操作数共享 ValidRow 与 ValidCol，但每个描述符的物理几何按其自身类型检查，因此 FP32 目标的物理大小可以不同于其 FP16 源。B.DATR 只接受 Layout、DataType 与 PadValue；非默认的 CMode、RMode、Sat 或 Canonicalize 均非法。
- 绑定格式错误或多余、出现 B.IOR 或 B.IOS、类型对非法、源载体为打包或位宽不同、源内容无效或未定义、布局或形状不匹配、维度错误时，会引发 Fault_TileLegality。目标形状无法表示或容量不足时，会引发 Fault_TileAllocation。两种故障都发生在任何目标效果之前。

## 0.59.1 来源

- 当前身份：tile:SFU:0:29:TEXPDIF
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x01D
- PTO 源：asl/tile/elementwise-tile-tile/transcendental/TEXPDIF.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
