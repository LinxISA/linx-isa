<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:SFU:2:29:TCOLARGMIN", "kind": "tile", "name": "TCOLARGMIN", "pto_instruction_sha256": "ee3744c87495bda972e81e53f92ccb1d4c422b327c218a3b3d062059c8b92ef3", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/reduce-and-expand/column-reduction/TCOLARGMIN.asl", "pto_source_sha256": "6fba606b8fc5d3fad2fff5db951392e90f641b4862e1af79d0a43951539d2587", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/reduce-and-expand/column-reduction/TCOLARGMIN.md", "reader_source_sha256": "9ee9535c2de9cc6825df280dab51e2ca4d4f1ee1540d735de8b55bb938856657", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TCOLARGMIN

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TCOLARGMIN 是由 SFU 引擎执行的 Tile 归约与扩展操作。它扫描单个 Local 源 Tile 的每个有效列，把获胜元素的行下标写为 U32。它由 TEPL Mode 2 Function 29（选择器 0x05D）选中，没有独立 opcode。

## 输入与输出

- source0 是持久 Local 源 Tile。其有效区域的每个坐标都参与，其存储后备类型只有在等位宽、非打包载体视图下才允许与操作类型不同。
- destination0 是新分配的 Local U32 Tile，逻辑形状为 `1 × ValidCol`，每个有效列产生一个行下标；其余物理坐标是填充坐标。
- 目标使用源的布局，只有 RowMajor、CUBE_M16 与 CUBE_M32 是允许的布局。 64 位 CUBE 操作数要求 CUBE_M32 double-CELL 映射；CUBE_M16 会拒绝。
- 各操作数共享同一个 PE_MASK。PE_MASK=0000 是严格无操作，发生在描述符读取、分配、故障、状态或载荷效果之前。
- 只要存在有效的掩码状态——无论是指令束中编码的还是注入模型的——操作数检查就会失败，指令束因此故障，而不是只归约一个子集；每个有效源坐标都必须已定义、编码有效并参与归约。

## 执行结果

- 目标作为一个整体变为可见：描述符、结果、已定义性、有效结果矩形之外的填充与累积的数值状态同时发布，被拒绝的执行不会发布其中任何一项。源保持不变，该操作没有 GM 内存效果。
- `1 × ValidCol` 有效区域之外的物理目标坐标接收所选 PadValue。Zero、Max 与 Min 会定义这些坐标；Null 使它们保持未定义。
- 省略与编码零并不相同，因此要读取整个物理目标的程序必须请求 Zero、Max 或 Min。

## 示例

以一个小型 TCOLARGMIN 示例说明：列数据 [[1, 4], [3, 2]] 产生最小的获胜行下标 [0, 1]：左列在第 0 行获胜，右列在第 1 行获胜。

对于有效区域为 7 x 60 且使用 Zero 填充的 8 x 64 FP32 源，遍历访问 60 个有效列，每个执行 6 个比较步骤，因此目标得到 60 个结果，作为 U32 下标占用 240 字节，位于由 2KB TSize 推导出的 8 x 64 形状内的 1 x 60 有效区域中，其中 512 个坐标里有 452 个是 Zero 定义的填充坐标。

同样的操作在宏形式下写作 TCOLARGMIN <Row=8, Col=64, ValidRow=7, ValidCol=60, FP32, Zero>, T#1, ->T<2KB>。

## 合法性与异常

- 可接受的操作类型为 FP64、S64、U64、S32、U32、FP32、S16、U16、FP16、BF16、S8 与 U8。无论源类型是什么，目标 DataType 都是 U32。源可以使用位宽相同、非打包的其他后备类型，但 RCPE6M2 绝不能作为归约后备；活动的指令束必须从 BSTART 解析出操作 DataType，否则拒绝。
- 恰好一条终止的 Local B.IOT 提供源与新目标，因此 B.IOR、B.IOS、第二条 B.IOT、非终止绑定，以及把目标命名为源的写法都非法。
- 绑定流格式错误、维度缺失或为零、DataType 不受支持、源布局不合法/混合/不匹配、源元素未定义或源编码无效，会在效果之前引发 Fault_TileLegality；结果形状、TSize、重命名或容量失败会在发布之前引发 Fault_TileAllocation。
- 因此这里接受的每个浮点类型都能得到已定义的元素结果，合法性与可执行定义一致。

## 0.59.1 来源

- 当前身份：tile:SFU:2:29:TCOLARGMIN
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x05D
- PTO 源：asl/tile/reduce-and-expand/column-reduction/TCOLARGMIN.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
