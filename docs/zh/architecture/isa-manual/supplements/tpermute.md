<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:SFU:3:21:TPERMUTE", "kind": "tile", "name": "TPERMUTE", "pto_instruction_sha256": "91c298bbcadc8d95b6787fa459613bfab09fec45f80144d23731ac8f7246f66b", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/layout-and-rearrangement/layout/TPERMUTE.asl", "pto_source_sha256": "13dc19464e98b16c131bb056076f35c4d975bd6dc7c9e4834216b30c04fbec08", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/layout-and-rearrangement/layout/TPERMUTE.md", "reader_source_sha256": "1e267e3bb4d302dfa5b13386df8b79339ea39031ad27dfde7030364f557f31ce", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TPERMUTE

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TPERMUTE 根据一个 U8 索引 Tile，从两个数据源的某个字节构建每个目标字节。它作用于 Local CUBE_M16 或 CUBE_M32 Tile 的原始字节，不执行任何数值转换。

## 输入与输出

- source0 与 source1 是数据源。它们与目标共用同一类型、有效形状与布局，并且可以是同一个 Tile。
- source2 是索引 Tile：U8，布局与有效行相同，每个有效目标字节对应一个有效列，cell 数量相同。它必须不同于两个数据源。
- destination0 是新的，保持源类型、有效形状与布局。它必须不同于每个源。
- 数据类型可以是任何受支持 CUBE 载体；64 位载体要求 CUBE_M32 double-CELL 描述符。第一条 B.IOT 携带 source0 与 source1；第二条携带索引 Tile 与目标。

## 执行结果

- 所有索引检查与源读取都在发布之前完成。每个有效目标元素都变为已定义，有效区域之外的物理元素接收 Null 填充并保持未定义。
- 存在 ExecutionMask 时，非活动目标元素不读取任何索引或源字节，并接收该掩码规定的零值或合并值。源保持不变，该操作没有内存或数值状态效果。

## 示例

取一个 U8 CUBE_M32 行，有 4 个有效字节，因此行字节数为 4，合法索引为 0 到 7。source0 保存字节 0x01、0x02、0x03、0x04（字 0x04030201），source1 保存 0x05 到 0x08（字 0x08070605）。

索引字节 [0, 4, 1, 5] 依次选择 source0 字节 0、source1 字节 0、source0 字节 1 与 source1 字节 1。目标字节为 0x01、0x05、0x02、0x06，即字 0x06020501。索引 8 会拒绝该指令束。

以宏形式表示，T#1 与 T#2 是数据源，T#3 是索引 Tile：

TPERMUTE <U8>, T#1, T#2, T#3, ->T<128B>

## 合法性与异常

- 非 CUBE_M16/M32 布局、64 位 CUBE_M16 载体、类型、形状、布局或 CELL 数不匹配、索引 Tile 非法、目标别名或所选字节未定义，都会在任何目标效果前引发 Fault_TileLegality。
- 绑定结构格式错误会引发 Fault_BundleControl；cell 重排模式拥有该检查。

## 0.59.1 来源

- 当前身份：tile:SFU:3:21:TPERMUTE
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x075
- PTO 源：asl/tile/layout-and-rearrangement/layout/TPERMUTE.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
