<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/linxisa-v0.59.json", "identity": "b_subview_32_48f114b5d12b", "kind": "instruction", "name": "B.SUBVIEW", "pto_instruction_sha256": "03206d774b689fc211220df1ca767b65d20d072169b7fdee3ecb8ec54a66bcf0", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/block/operands/B.SUBVIEW.asl", "pto_source_sha256": "80a371f5288c878380f7124f959bf2f552a3e835a5940770ce8227cc236d14a6", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/block/operands/B.SUBVIEW.md", "reader_source_sha256": "9934788c191679964245a27d5aa0acacba6b7b2bde3d7fc504a345057fab19e5", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# B.SUBVIEW

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

B.SUBVIEW 是一条 32 位头部命令，把紧邻其前的 B.IOT 或 B.IOS 绑定源缩小为一段连续范围。该命令只记录范围，不分配 Tile，也不查询当前操作模式。

## 输入与输出

- SrcSelect（位 31）为 0 时选择源 0，为 1 时选择源 1。Shared 范围组没有源 1。
- uimm11（位 30:20）是无符号加数，零扩展。零是真实的零加数。
- RegSrc（位 19:15）指定绝对 GPR 0 至 23。编码零指零 GPR，读出 0。
- SubviewSizeCode（位 10:7）是请求的范围大小，1 至 12，对应 128 B 至 256 KiB。编码 0 保留。
- 位 14:11 固定；该形式在掩码 0x0000787f 下低位匹配 0x53。
- 之后写 RegSrc 的主体指令不会改变已记录的偏移。对于 Local CUBE 源，派生偏移以父 Tile 的 128 字节 CELL 计数。

## 执行结果

- 被接受的 B.SUBVIEW 只改变绑定上该源的范围记录。它不读取 Tile 载荷。
- 在阶段 2 准备期间，Local 子视图成为 CUBE 布局父 Tile 上从偏移开始、覆盖 min(requested, remaining) 个 CELL 的描述符。所选 CELL 被复制到一个临时 Tile 中，该 Tile 使用父 Tile 的布局、数据类型与 PE 掩码，操作读取这份副本。无论成功还是失败，临时副本都在操作结束后释放。
- 子视图选择同一对象的一个范围；它不是重新布局，也不能使未定义的数据变得可读。

## 示例

~~~asm
B.IOT T#1, mask=1111, <last>, ->T<2KB>
B.SUBVIEW 0, a0, 2, 2
~~~

假设 T#1 是有效形状为 16 x 32 的 CUBE_M16 FP16 Tile，即 8 个 16 行 x 4 列的 CELL，且 a0 保存 0。派生偏移为 0 + 2 = 2 个 CELL，大小编码 2 请求 256 B，即 2 个 CELL。剩余 4 个 CELL，因此视图覆盖所请求的 2 个 CELL：父 Tile 的第 8 至 15 列，即 16 x 8 的视图。该修饰符编码为 0x00210153。其后再出现 B.SUBVIEW 0 会引发 Fault_BundleControl，因为源 0 已被修饰。

## 合法性与异常

- RegSrc 编码为 24 至 31、SubviewSizeCode 为 0 或 13 至 15，或固定位非零时，在读取任何 GPR 之前引发 Fault_IllegalInstruction。
- 附着于参与的 Local 范围组的 SubviewSizeCode 11 或 12 引发 Fault_TileLegality，因为 Local 大小编码止于 10，即每 PE 64 KiB。Shared 范围组接受 1 至 12。
- 没有打开的范围组、绑定命令没有所选源角色、角色重复或角色顺序错误时，引发 Fault_BundleControl。
- 在阶段 2 准备期间，若 Local 子视图的父 Tile 不是已分配的 CUBE Tile，或偏移不小于父 Tile 的 CELL 数，则在操作之前引发 Fault_TileLegality。

## 0.59.1 来源

- 当前身份：b_subview_32_48f114b5d12b
- 当前汇编或载体：B.SUBVIEW SrcSelect, RegSrc, uimm11, SubviewSizeCode
- PTO 源：asl/block/operands/B.SUBVIEW.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
