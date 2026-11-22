<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/state/pto_tile_operations.json", "identity": "tile:SFU:3:30:TGPR2T", "kind": "tile", "name": "TGPR2T", "pto_instruction_sha256": "f529ef1cd427645ea8eb295ad9431d895970ec6c79d34f4c54cc36f610e6bfb4", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/tile/layout-and-rearrangement/layout/TGPR2T.asl", "pto_source_sha256": "85472071d45e13f3d924320f2b1017f06ef5fb347ff250c5e7e5eac701851b9e", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/tile/layout-and-rearrangement/layout/TGPR2T.md", "reader_source_sha256": "9048b347e4bdff052ae5903b93aa1e1b234cc0d624839a4f3d7610ff504c47f8", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# TGPR2T

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

TGPR2T 把保存在四个通用寄存器（GPR）中的谓词位转置到一个新分配的 U8 CUBE Tile 中。每个 GPR 保存完整的谓词平面；每个 Tile 行接收所有平面在该行上的位，并打包为字节。

结果是普通数值 U8 Tile，而不是 PredicateCell，因此其字节可以是 0x00 到 0xFF 之间的任意值。

## 输入与输出

- source0 到 source3 是四个 GPR，即规范位映射中的 GPR0 到 GPR3，由 0 到 23 的绝对选择器指定。
- destination0 是新分配的数值 U8 Tile，布局为 CUBE_M32 或 CUBE_M16。
- 形状是固定的：B.DIM LB1 = 32 且 LB0 = 4 选择 CUBE_M32，LB1 = 16 且 LB0 = 8 选择 CUBE_M16。两个维度都是必需的，LB2 必须为 1（其默认值），编码的 TSize 必须覆盖整个描述符。
- 四个 GPR 来自恰好两条紧邻的仅源 B.IOR 记录，按 3+1 划分，随后是一条目标 B.IOT。TGPR2T 模式检查该流。
- B.DATR 是可选的。省略它时选择 Zero 填充与字节偏移 0。

## 执行结果

- 四个 GPR 与 PE 掩码都在发布之前被快照，不读取任何旧目标载荷。目标载荷、描述符与已定义性作为一次操作发布；每个元素都变为已定义。
- TGPR2T 不写任何 GPR，不记录数值状态，也没有全局内存效果。

## 示例

头部 BSTART.SFU TGPR2T, U8 配合 B.DIM LB1 = 32 与 LB0 = 4 选择一个 32 x 4 = 128 字节的 CUBE_M32 目标。B.DATR 选择 Zero 与字节偏移 0。第一个 GPR 为 0x0000000100000001，其余三个为零。

第一个 GPR 的位 0 是平面 0 在第 0 行的位，位 32 是平面 1 在第 0 行的位。因此第 0 列的第 0 行接收 0x03，其他每个字节都为 0x00。若改为 Max，第 1 到 3 列保存 0xFF，而第 0 列仍在第 0 行保存 0x03、在第 1 到 31 行保存 0x00。

## 合法性与异常

- RMode[17] 必须为零，RMode[16:15] 是字节偏移 0 到 3；对该操作而言，RMode 不是舍入方式。
- 有效 PadValue 必须为 Zero 或 Max；Min 与 Null 会在任何效果之前被拒绝。
- 维度缺失、形状不是 32 x 4 或 16 x 8、中间插入其他命令、B.IOR 记录的顺序或划分错误、GPR 目标或多余记录，都会在任何效果之前被拒绝。
- PE_MASK=0000 在 B.IOT 的 size code 编码检查之后是严格无操作：不再进行模式检查、GPR 读取、分配或效果，但非法的 B.IOT size code 仍会引发 Fault_IllegalInstruction。

## 0.59.1 来源

- 当前身份：tile:SFU:3:30:TGPR2T
- 当前汇编或载体：BSTART.TEPL
- 当前选择子：0x07E
- PTO 源：asl/tile/layout-and-rearrangement/layout/TGPR2T.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
