<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:TLSU:-:13:GMOV", "kind": "tile", "name": "GMOV", "pto_instruction_sha256": "8d69d4c4fa07ef95ad1097072a78aab5deec743af1d069f03df468cb39856234", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/memory-and-data-movement/pe-movement/GMOV.asl", "pto_source_sha256": "d36ad1a78c748f462906baf60f915f4f7eec56734a6484f6671a309bfc781a14", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/memory-and-data-movement/pe-movement/GMOV.md", "reader_source_sha256": "5c18e149c9b7922802aec18a78fc17168c5400cd7bde33b55675356c6cd34118", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# GMOV

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

GMOV 把 Core4 PE 组内一个由对端选择的 Local 片段复制到新分配的 Local 目标中。它是 TLSU Function 13，写作 BSTART.GMOV DataType，并且没有独立 opcode。

每个 PE 提供自己的 peer_tid，即它想要的 Local 片段所属 PE 的编号，并接收该片段的字节。PE_MASK 决定哪些 PE 获得目标。本操作不记录内存效果：它从不转换地址、不做权限检查，也不发出 load、store、atomic 或 fence 事件。

## 输入与输出

- destination0 是选中的 Local 目标片段。指令束在其 B.IOT 下分配它，并采用源的有效行数、有效列数、物理列数与数据类型。
- source0 是 Core4 对端解析的 read-old Local 源操作数快照。目标 TSize 必须等于该源的每 PE 容量。
- scalar0 是每个 PE 的绝对 peer_tid。
- 恰好一条终止 B.IOT 同时携带源与目标，且 L=1。指令束不接受第二个 Tile 源，也不接受 B.IOS，Shared 绑定会被拒绝。
- 每个解析后的 B.DIM 值必须等于 1，目标描述符由源描述符得到，因此复制不能重塑数据。

## 执行结果

- 成功时，每个被选中 PE 新分配的目标保存已解析源片段的保字节副本，具有相同的已定义元素与相同的 contents_defined 标志。未被选中的目标以及所有 Shared 与 GM 状态保持不变。

## 示例

取 U8，源 T#1 的每 PE 容量为 1 KB 且其数据已完全定义，PE_MASK 指定 PE 0 与 PE 1，并且每个 PE 的 peer_tid 都为 1。

预检：T#1 必须在四个 PE 中都已分配且完全定义，并且 a2 中的 peer_tid 在每个 PE 中必须在 0..3 内。

每个解析后的 B.DIM 值必须为 1，并且目标 TSize 必须等于 T#1 的 1 KB 每 PE 容量。

规范宏写法是 GMOV <U8, PE0_1>, T#1, a2, ->T<1KB>。PE 0 与 PE 1 各获得一个新的目标，其字节与已定义性是已解析 PE 1 片段的副本；PE 2 与 PE 3 保持不变。

## 合法性与异常

- GMOVDataTypeLegal 恰好接受 TileCarrierOrPackedBaselineDataTypeSupported 允许的类型：所有最高 64 位的非打包载体，加上打包四位基线。64 位源在 RowMajor 中仍合法；在 CUBE 布局中则要求 CUBE_M32 double-CELL 存储。
- 源与目标必须在数据类型、布局、存储种类、行数、列数、有效行数与有效列数上一致（TileOperandsLegal_GMOV）。布局必须是 RowMajor、CUBE_M16 或 CUBE_M32；CUBE_N8 与 Shared 操作数非法。 64 位 CUBE 操作数要求 CUBE_M32 double-CELL 映射；CUBE_M16 会拒绝。
- 任一 PE 的 peer_tid 超出 0..3、Core4 源未就绪、B.DIM 值不为 1、TSize 不匹配、绑定多余或未终止，或出现 B.IOS，都会在复制之前引发 Fault_TileLegality；集体预检失败时不分配也不写入任何目标。
- PE_MASK 可以是任意非零值，部分掩码只选择这些 PE 的目标。零掩码不选择任何 PE。与 atom/red、gather 和 scatter 分派器不同，ExecuteBundleGMOVOperation 没有零掩码提前返回，因此就绪、peer_tid 范围、类型、布局与维度检查仍会执行，也仍可能引发故障。

## 0.59.1 来源

- 当前身份：tile:TLSU:-:13:GMOV
- 当前汇编或载体：BSTART.GMOV
- 当前选择子：Function=13
- PTO 源：asl/tile/memory-and-data-movement/pe-movement/GMOV.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
