<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:VEC:0:28:TFMA", "kind": "tile", "name": "TFMA", "pto_instruction_sha256": "bb543db48a668462536c5fddbcd6ab79bf8f199aca447417607c22f698f530f4", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/elementwise-tile-tile/arithmetic/TFMA.asl", "pto_source_sha256": "ebee392fec0866e93b732e484c18607ad759d302b00207b1c6a1d10398dbe2e7", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/elementwise-tile-tile/arithmetic/TFMA.md", "reader_source_sha256": "900a2545886a614a7698a8e223344ae5424edea79566b43cd0294a9f36584b15", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TFMA

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TFMA 在三个 Local Tile 上逐元素计算 left * right + addend，并把结果写入一个新分配的 Local 目标 Tile。与 TADD 不同，它读取三个源。

一条 B.IOT 最多携带两个源，因此 TFMA 使用两条 B.IOT 绑定：第一条携带两个乘数，第二条携带加数和目标。

## 输入与输出

- source0 是左乘数，绑定为第一条 B.IOT 的第一个源。
- source1 是右乘数，绑定为第一条 B.IOT 的第二个源。
- source2 是加数，绑定为第二条即终止 B.IOT 的源。
- destination0 是新分配的 Local Tile，由第二条 B.IOT 绑定。
- 第一条 B.IOT 不得带目标或终止标记；第二条必须携带目标并终止序列。所有参与的 B.IOT 绑定必须使用同一个 PE_MASK，PE_MASK=0000 是严格无操作。
- 与 TADD 不同，TFMA 不接受以不同后备类型存储的同位宽源，因此不会对任何源做重解释。

## 执行结果

- 目标描述符、有效区域内的结果、填充、每个元素的已定义性以及累积的数值状态作为一次操作发布。被拒绝的指令束没有任何架构效果，三个源也保持不变。
- ValidRow x ValidCol 之外的物理元素接收所选 PadValue。Zero 写入零；Max 与 Min 写入该 DataType 的最大与最小有限值；Null 使这些元素保持未定义。省略 B.DATR 选择 Null，而显式编码 00 选择 Zero。
- 重复的源以及与目标别名的源都观察到完整的操作前值。TFMA 没有全局内存效果。存在 ExecutionMask 时，非活动坐标接收该掩码规定的零值或合并值，且不贡献状态。

## 示例

这是非规范契约模式草图；它用于组织字段和绑定关系，不声称可以直接汇编。

对 FP16，取 left = right = 1.0009765625，addend = -1.001953125。精确积为 1.001953125 + 2^-20，因此 TFMA 返回 2^-20，它在 FP16 中可精确表示。若单独使用 TMUL，积会被舍入为 1.001953125，随后的 TADD 将返回 0。

以宏形式表示，一个 8 x 64 的 FP16 融合乘加写作 TFMA <Row=8, Col=64, FP16>, T#1, T#2, T#3, ->T<1KB>，其中 T#1 与 T#2 是乘数，T#3 是加数。目标载荷为 8 x 64 x 2 = 1024 字节。

## 合法性与异常

- TFMA 恰好接受 FP64、S64、U64、FP16、FP32 与 BF16。融合浮点辅助函数为 FP64、FP32 与 FP16 提供有限执行；既有已接受 BF16 有限结果缺口保持不变。整数形式使用定宽融合规则。
- 默认布局为 RowMajor。显式 Layout 可以选择 CUBE_M16 或 CUBE_M32，所有操作数必须使用同一布局。CUBE_N8、Shared Tile 以及混合布局均非法。TFMA 拒绝非默认的 RMode、Sat、CMode 与 Canonicalize。 在 CUBE 布局中，64 位操作类型只在 CUBE_M32 中合法；CUBE_M16 会拒绝。
- 绑定格式错误或多余、出现 B.IOR 或 B.IOS、掩码不相等、维度错误、DataType 不受支持、布局不匹配、源未定义或浮点编码无效时，会引发 Fault_TileLegality。目标形状无法表示或容量不足时，会引发 Fault_TileAllocation。两种故障都发生在任何目标效果之前。

## 0.59.1 来源

- 当前身份：tile:VEC:0:28:TFMA
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x01C
- PTO 源：asl/tile/elementwise-tile-tile/arithmetic/TFMA.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
