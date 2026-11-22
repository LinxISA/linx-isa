<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:SFU:3:22:TSHUF", "kind": "tile", "name": "TSHUF", "pto_instruction_sha256": "4db6d666fb59bbb43dcbd9a5260d832ea984bc61a1c83be63d32538e1cb3dd3d", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/layout-and-rearrangement/layout/TSHUF.asl", "pto_source_sha256": "1d0bb0fd911fec2a909ef1f48bc5608c94dc7d5cf14a1d902bb7010f67d8ae64", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/layout-and-rearrangement/layout/TSHUF.md", "reader_source_sha256": "863ff1bce4c7e6199f0f20c7daf1deab6d5a315b55854903d3dcda22b783eeec", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TSHUF

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TSHUF 在 Local CUBE_M16 或 CUBE_M32 Tile 的行之间移动元素。每一行是 CUBE cell 的一个通道，通道被分成相互独立的 2 的幂大小的段。列从不改变。

## 输入与输出

- source0 是数据源：数值 CUBE_M16 或 CUBE_M32 Tile；64 位载体要求 CUBE_M32。 64 位 CUBE 操作数要求 CUBE_M32 double-CELL 映射；CUBE_M16 会拒绝。
- source1 是控制 Tile：U32，布局与有效行相同，源行的每个 32 位字对应一个有效列，cell 数量相同。
- scalar0 是来自一条 B.IOR 的控制字；RegSrc1、RegSrc2 与 RegDst 为零。
- destination0 是新的，保持源类型、有效形状与布局。它必须不同于源与控制 Tile。
- B.DATR 只能携带 Layout。控制字的位 63 到 32 必须为零。

## 执行结果

- 源与控制快照都在发布之前完成。每个有效目标元素都变为已定义，有效区域之外的物理元素接收 Null 填充并保持未定义。
- 存在 ExecutionMask 时，非活动元素不读取任何控制字或源元素，并接收该掩码规定的零值或合并值。源保持不变，该操作没有内存或数值状态效果。

## 示例

一个 U32 CUBE_M16 源有 4 个有效行、1 个有效列，保存 1、2、3、4。每个控制 Tile 字的 b = 1。控制字 0x00000302 选择模式 2、宽度 16 与边界 0。

模式 2 按与 1 异或来配对通道，因此目标列为 2、1、4、3。模式 1 且边界为 1（0x00010301）时，每行读取下一行：第 3 行将读取第 4 行，而它超出了 4 个有效行，因此结果为 2、3、4、0。边界为 0（0x00000301）时，第 3 行保留自身的值，结果为 2、3、4、4。

以宏形式表示，T#1 是数据源，T#2 是控制 Tile，a0 保存控制字：

TSHUF <U32>, T#1, T#2, a0, ->T<128B>

## 合法性与异常

- 模式大于 3、边界大于 1、段代码大于 4、CUBE_M16 下的段代码 4、控制字位 63 到 32 非零、描述符不匹配、目标别名、控制字未定义，或将被读取的源元素未定义，都会在任何效果之前引发 Fault_TileLegality。
- 边界为 1 时，越出段的元素写入零且不读取任何内容，因此没有任何通道选中的未定义元素不会使该指令束非法。

## 0.59.1 来源

- 当前身份：tile:SFU:3:22:TSHUF
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x076
- PTO 源：asl/tile/layout-and-rearrangement/layout/TSHUF.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
