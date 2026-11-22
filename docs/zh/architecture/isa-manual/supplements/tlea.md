<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:VEC:1:14:TLEA", "kind": "tile", "name": "TLEA", "pto_instruction_sha256": "db9e7224f517675ea6ebbf1cc4254fd4b0e2e41cebe331f46920540266dba13a", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/tile-scalar-and-immediate/arithmetic/TLEA.asl", "pto_source_sha256": "6356e31b2a42789e3355a6ba3af7af1e02fbd9fb8d82030aa8ea4e59996557fb", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/tile-scalar-and-immediate/arithmetic/TLEA.md", "reader_source_sha256": "f8ff1a8cf0eafbf2b1a093abc3321de609f1c039e09240d1d94dfb31f38ab07a", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TLEA

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TLEA 把 Local Tile 中的逻辑元素索引转换为一个新的 Local 字节偏移 Tile。它由 TEPL Mode 1 Function 14（选择器 0x02E）选中，规范头部为 BSTART.VEC TLEA, SrcDataType，没有独立 opcode。

TLEA 不读取基址寄存器，也不访问内存。后续的索引内存操作（如 MGATHER）使用自己的基址与字节位移组合地址。

## 输入与输出

- source0 是持久 Local 索引 Tile，后备类型必须恰为 S32、U32、S64 或 U64。
- scalar0 是来自 B.IOR.RegSrc0 的必需逐 PE 元素位宽。除既有 ExecutionMask 绑定扩展外，RegSrc1、RegSrc2 与 RegDst 保持为零。
- destination0 是新分配的 Local 字节偏移 Tile，元素类型为对应的 S64 或 U64。
- 一条终止 B.IOT 绑定源与重命名目标。源和目标具有相同的逻辑 ValidRow x ValidCol 形状及相同布局，但各自独立检查物理描述符。这在 32 位索引扩展为 64 位偏移时尤其重要；合法 CUBE 目标所需的容量或物理列几何可以与源不同。
- PE_MASK=0000 是严格无操作，在 GPR 读取、描述符读取、分配、源操作数快照或故障之前退出。其他情况下，所有合法性与分配检查均在源操作数快照前完成，因此 S64 或 U64 源与目标直接别名时读取旧载荷。

## 执行结果

- 预检与源操作数快照完成后，目标描述符、活动坐标结果、填充和已定义性一起变为可见。源保持不变，不更新数值状态；被拒绝的操作不产生目标效果。
- 对于 CUBE_M32，非活动 ExecutionMask 坐标遵循既有 ZERO 或 MERGE 规则，并且不读取对应源元素。一个掩码位控制完整 64 位逻辑结果，包括两个物理 CELL 平面。MERGE 通过既有目标掩码源取得值；ZERO 提供目标类型的零编码。
- 逻辑有效矩形之外的物理元素接收所选 PadValue。省略 B.DATR 选择 Null 与 RowMajor；唯一显式 CUBE 布局是 CUBE_M32。填充与有效矩形内部的 ExecutionMask 处理相互独立。

## 示例

对于 U32 源行 [0, 1, 2] 与 element_bits=32，零扩展得到相同的三个 64 位值，再乘以 4 得到 U64 行 [0, 4, 8]。若 MGATHER 随后使用基址 0x1000，其内存地址为 0x1000、0x1004 与 0x1008；该基址相加由 MGATHER 执行，不由 TLEA 执行。

对于相同元素位宽下的 S32 源行 [-1, 0, 1]，符号扩展后进行模 2^64 乘法，得到 S64 位模式 [0xFFFFFFFFFFFFFFFC, 0x0000000000000000, 0x0000000000000004]。第一个结果表示 -4 字节位移，不会触发宿主语言的有符号溢出。

## 合法性与异常

- 源操作类型与后备类型必须完全相同，并且只能是 S32、U32、S64 或 U64。打包四位类型、浮点类型、更窄整数、Shared Tile 与 CUBE_N8 均不支持。标量元素位宽必须恰为 8、16、32 或 64 位；对于活动指令块，零和其他所有 GPR 值都会被拒绝。
- RowMajor 与 CUBE_M32 使用相同逻辑形状，同时允许源与目标拥有独立合法物理描述符。每个 TLEA 目标都是 64 位，因此其 CUBE_M32 描述符对每个逻辑列使用两个完整 CELL；32 位 CUBE_M32 源可以只用一个。即使源索引类型为 32 位，CUBE_M16 也非法。
- 保留低 64 位的乘积不会引发溢出故障。TLEA 只生成字节偏移，因此也不会引入内存访问故障；后续的基址算术、地址校验或内存事件由消费该偏移的内存指令负责。

## 0.59.1 来源

- 当前身份：tile:VEC:1:14:TLEA
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x02E
- PTO 源：asl/tile/tile-scalar-and-immediate/arithmetic/TLEA.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
