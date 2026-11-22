<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/linxisa-v0.59.json", "identity": "b_assemble_32_20b4f7671811", "kind": "instruction", "name": "B.ASSEMBLE", "pto_instruction_sha256": "d6a4fc3ebbc15387d9457f9371f33fc89d01cab170227534ac8417acafa62dd9", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/block/operands/B.ASSEMBLE.asl", "pto_source_sha256": "803c3bf79faffc4d7edf2c4cb6111d117b6f6b9a8a83b54544b57f1765be1dca", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/block/operands/B.ASSEMBLE.md", "reader_source_sha256": "fa3d55dd70fc5549c08a9981a2b999ae424a6c0d38ecb6e476a67bc1d4426bbc", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# B.ASSEMBLE

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

B.ASSEMBLE 是一条 32 位头部命令，把紧邻其前的绑定命令的目标变为多块构建中的一个写入者。绑定命令是 B.IOT 或 B.IOS。这种构建称为世代：一个父 Tile 由多个块或多个 PE 按范围写入，并在 LAST 时发布一次。

它与 B.SUBVIEW 同属范围修饰符，附着于前一条绑定命令并记录字段；执行这条命令本身不分配 Tile。

## 输入与输出

- INIT（位 31）为 1 时选择 INIT 或 INIT_LAST，为 0 时选择 MIDDLE 或 LAST。
- uimm11（位 30:20）是无符号加数，零扩展。零是真实的零。
- RegSrc（位 19:15）指定绝对 GPR 0 至 23。编码零指零 GPR。
- LAST（位 11）标记最后一个写入者。
- WriterSizeCode（位 10:7）是本写入者范围的大小：Local 范围组为 1 至 10，Shared 范围组为 1 至 12，从 128 B 起。原始编码 13 至 15 保留。
- 写入者偏移为 GPR[RegSrc] + uimm11（模 2^XLEN），以父 Tile 的 128 字节 CELL 计数。处理程序把原始字段与该偏移存入目标的范围记录。
- 父容量来自 INIT 绑定命令的 SizeCode，因此一个父 Tile 可以由多个较小的写入者填充，它们的范围必须位于父 Tile 之内，并且在共享 PE 上不得重叠。

## 执行结果

- 被接受的 B.ASSEMBLE 只改变绑定命令的范围记录；对于 Local 续写阶段，它还把最后一个源移入父引用。它不读取 Tile 载荷。
- 对正常参与的绑定组，指令读取 GPR[RegSrc]，计算 GPR[RegSrc] + ZeroExtend(uimm11)（模 2^XLEN），并把派生偏移与 INIT、LAST、RegSrc、uimm11、WriterSizeCode 原始字段一起写入当前范围记录。
- 操作成功后，写入者的 CELL 被标记为已覆盖。在 LAST 时世代关闭。只有当每个参与 PE 都满足条件时，世代才被标记为已发布，这要求每个必需 CELL 对该 PE 既已覆盖也已就绪。
- 只有前置绑定的 PEMode=000、因而打开丢弃组时，原始字段合法且连续的 B.ASSEMBLE 才只检查范围组已打开，不读取 GPR，也不写入范围记录或其他状态。

## 示例

~~~asm
B.IOT T#2, mask=1111, <last>, ->T<4KB>
B.ASSEMBLE 1, 0, zero, 0, 5
~~~

该块开始一个 Local 世代。绑定命令的 SizeCode 6 产生 4 KiB 父 Tile，即 32 个 CELL。修饰符是 INIT 而非 LAST，偏移为 0 + 0 = 0，写入者大小编码为 5，即 2 KiB 或 16 个 CELL，编码为 0x800012d3。提交后，CELL 0 至 15 已覆盖，父 Tile 成为新的 T#1。之后的块 B.IOT T#2, T#1, mask=1111, <last> 接 B.ASSEMBLE 0, 1, zero, 16, 5（编码 0x01001ad3）以 T#1 作为父引用，从其源 T#2 写入 CELL 16 至 31，并关闭世代。若第二个块的偏移为 8，将与 CELL 8 至 15 重叠并引发故障。

## 合法性与异常

- RegSrc 编码为 24 至 31、原始 WriterSizeCode 为 13 至 15，或固定位非零时，在读取任何 GPR 之前引发 Fault_IllegalInstruction。
- 附着于参与的 Local 范围组的 WriterSizeCode 11 或 12 引发 Fault_TileLegality。
- 没有打开的范围组、INIT 所在绑定命令没有未使用的目标角色、续写阶段所在绑定命令带有目标，或参与范围组中写入者大小编码为 0 时，引发 Fault_BundleControl。
- 在阶段 2 准备期间，范围超出父 Tile、范围在共享 PE 上与较早写入者重叠、写入者掩码不是世代掩码的子集，或父引用未指向打开的世代时，在操作效果之前引发故障。
- 有多个参与 PE 且没有 B.ASSEMBLE 的 Shared 目标引发 Fault_TileLegality。

## 0.59.1 来源

- 当前身份：b_assemble_32_20b4f7671811
- 当前汇编或载体：B.ASSEMBLE INIT, LAST, RegSrc, uimm11, WriterSizeCode
- PTO 源：asl/block/operands/B.ASSEMBLE.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
