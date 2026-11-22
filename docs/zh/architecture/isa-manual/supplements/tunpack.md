<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:SFU:3:24:TUNPACK", "kind": "tile", "name": "TUNPACK", "pto_instruction_sha256": "869b76b9b0a28dbb13d4cfc6a4fae176c100a1e7d3a4fa24ceec8995999f3dae", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/layout-and-rearrangement/layout/TUNPACK.asl", "pto_source_sha256": "19e81729034e9db24ca7c2f3c9f1ddf87e58d913a381f2b17566b29fffbe53c7", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/layout-and-rearrangement/layout/TUNPACK.md", "reader_source_sha256": "5104aea96bb91da161a88e667035dd81d901385bec240b39fb24e058a795cce6", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TUNPACK

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TUNPACK 从 Local CUBE 源的每个参与的 32 位字中提取一个连续的字节字段，并把它放入目标字的低字节。它重排原始字节，不执行任何数值转换。

BSTART 类型 U8、U16、U32 或 U64 是目标类型；源后备类型不必与之相同。

## 输入与输出

- source0 是 Local 数值 CUBE Tile，元素为非打包 8、16、32 位或 M32 64 位。
- scalar0 是来自一条 B.IOR 的解包控制字；RegSrc1、RegSrc2 与 RegDst 为零。
- destination0 是新的。U8/U16/U32 每个 raw word 分别生成 4/2/1 个元素。U64 要求 CUBE_M32、偶数 raw-word 数以及每个完整低/高 pair 一个逻辑列。
- 与 TPACK 相同，目标形状由源描述符推导，而不是来自 B.DIM。

## 执行结果

- 控制与源验证都在发布之前完成。每个参与的源字产生一个完整的目标字，每个有效目标元素都变为已定义，填充为 Null。
- 存在 ExecutionMask 时，位于 (row, word index) 的一个掩码位控制整个目标字组；非活动组不读取任何源字节，并接收该掩码规定的零值或合并值。源保持不变，该操作没有内存或数值状态效果。

## 示例

源字 0x44332211 与控制值 0x00000201 选择从字节偏移 1 开始的两个字节，即 0x22 与 0x33。目标字为 0x00003322。

一个有 6 个有效列的 U8 CUBE_M16 源每行有 6 个有效字节：字 0 有 4 个，字 1 有 2 个。控制值 0x00000200（偏移 0，字节数 2）合法，U16 目标得到 2 x 2 = 4 个有效列。控制值 0x00000201 会被拒绝，因为偏移 1 加字节数 2 超过了字 1 的 2 个有效字节。

TUNPACK <U16>, T#1, a0, ->T<128B>

## 合法性与异常

- 偏移必须为 0 到 3，字节数为 1 到 4，且 offset + count 不超过 4；控制位 63:32 必须为零。不支持的存储、布局或源位宽、字段超出某个字的有效字节、目标与源别名，或被选字节未定义，都会在任何效果之前引发 Fault_TileLegality。

## 0.59.1 来源

- 当前身份：tile:SFU:3:24:TUNPACK
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x078
- PTO 源：asl/tile/layout-and-rearrangement/layout/TUNPACK.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
