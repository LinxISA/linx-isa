<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:SFU:3:23:TPACK", "kind": "tile", "name": "TPACK", "pto_instruction_sha256": "6efd3a843d49ad03e3e705f8d045de3bc7cb6eb97cd323555b4b9517d432b0b9", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/layout-and-rearrangement/layout/TPACK.asl", "pto_source_sha256": "18bf9d94463b1a6430af63e8805fcc2439306336c60e288c52ba0e66521dad5f", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/layout-and-rearrangement/layout/TPACK.md", "reader_source_sha256": "38692f0ae0744abebbd124288583287a6dc363c567e51b25448a80a5b984faf4", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TPACK

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TPACK 把两个 Local CUBE 源中对应 32 位字的低字节字段拼接成一个目标字。它重排原始字节，不执行任何数值转换。

BSTART 类型 U8、U16、U32 或 U64 是目标类型；它不必与源类型一致。

## 输入与输出

- source0 与 source1 是 Local 数值 CUBE Tile，元素为非打包 8、16、32 位或 M32 64 位。它们共用一个布局、相同有效行数与每行相同 raw 32 位 word 数；类型可以不同。
- scalar0 是来自一条 B.IOR 的打包控制字；RegSrc1、RegSrc2 与 RegDst 为零。
- destination0 是新的。U8/U16/U32 每个 raw word 分别生成 4/2/1 个元素。U64 要求 CUBE_M32、偶数 raw-word 数以及每个完整低/高 pair 一个逻辑列。
- 因此宏形式没有形状字段，静态反汇编器无法打印 Row 或 Col。

## 执行结果

- 控制与源验证都在发布之前完成。每对源字产生一个完整的目标字，每个有效目标元素都变为已定义，填充为 Null。
- 存在 ExecutionMask 时，raw word 分别受控。对 U64，低、高 word 掩码位可以不同；每个活动半部独立打包，两个半部再合成一个一致的 64 位发布，非活动半部由 ZERO 或 MERGE 提供。

## 示例

对于对应的源字 0x00001234 与 0x00ABCDEF，控制值 0x00000202 从每个源中选择两个低字节。目标字节为 0x34、0x12、0xEF、0xCD，即字 0xCDEF1234。

当 U32 CUBE_M16 源有 8 个有效行、8 个有效列时，每行有 32 字节，即 8 个字。因此 U32 目标有 8 个有效行、8 个有效列；U16 目标则有 16 个有效列。

TPACK <U32>, T#1, T#2, a0, ->T<2KB>

## 合法性与异常

- 每个字段宽度必须在 1 到 3 之间，两者之和不得超过 4，控制位 63:32 必须为零。不支持的存储、布局或源位宽、字数不相等、目标与源别名，或被选字节未定义，同样会在任何目标效果之前引发 Fault_TileLegality。

## 0.59.1 来源

- 当前身份：tile:SFU:3:23:TPACK
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x077
- PTO 源：asl/tile/layout-and-rearrangement/layout/TPACK.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
