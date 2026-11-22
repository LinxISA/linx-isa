<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/linxisa-v0.59.json", "identity": "bstart_timg2col_32_557b5cf18709", "kind": "instruction", "name": "BSTART.TIMG2COL", "pto_instruction_sha256": "fb0684e45f2629d4c12638c22b0bd14fde509c39b8a657a7d6eb083838db6c91", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/block/execution/BSTART.TIMG2COL.asl", "pto_source_sha256": "8b372d487c0f9998f41f4defd546335331c537f89af209fdec9b6a49270ff188", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/block/execution/BSTART.TIMG2COL.md", "reader_source_sha256": "26012ff9b9ea93b56f48f5a1e442b61467bc9cbd7e9f48b51fbe2a634f7b0857", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# BSTART.TIMG2COL

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

BSTART.TIMG2COL 打开一个 Tile 内存指令束，其操作为 IMG2COL：从全局内存（GM）读取卷积输入图像，并把它写成矩阵。矩阵的每一行是一个输出像素，每一列是一个卷积核位置与输入通道，按 32 字节的 C0 通道组分组。该命令是一个 32 位字（匹配值 0x01c11181，掩码 0x07ffffff），DataType 位于位 31 到 27。它是命令形式 94，携带固定的 TLSU 选择器 28。

结果写到两处之一：普通行主序（ND）的 Shared Tile，或 CUBE_M16、CUBE_M32 布局的 Local Tile，可直接供 CUBE 引擎使用。

只有当描述符恰为 TIMG2COL 描述符且 DataType 受支持时才合法。因此不受支持的编码在 BSTART 处引发 Fault_IllegalInstruction，发生在指令束启动分派提交任何前驱之前。

## 输入与输出

- DataType 是元素类型：FP32、TF32、HF32、FP16、BF16、HiF8、E4M3、E5M2、E8M0、S32、S16、S8、U32、U16 或 U8。
- 显式的 B.DATR 必须使用 DTYPE_NONE、Zero 填充（编码 0），且比较、舍入、饱和与规范化控制均为零；只有它的布局起作用。
- B.DIM 的 LB0、LB1 和 LB2 给出 ValidCol、ValidRow（1 到 128，Local M16 最多 64）和 TotalCol。
- 两条相邻的仅源 B.IOR 记录：第一条为 GMBase, zero, zero，第二条为 ParamGPR0, ParamGPR1, ParamGPR2。TIMG2COL 参数定义了打包方式。
- Shared ND 输出恰好使用一条 B.IOS，没有 B.IOT。Local 输出恰好使用一条 PE_MASK 为 1111 的目标 B.IOT，没有 B.IOS。
- 每个 PE 根据同一几何计算不同的行份额，因此该检查使所有份额属于同一个矩阵；不一致时在任何 GM 访问之前拒绝。

## 执行结果

- ValidRow 分给四个 PE，先填满 PE 0。Local M16 每个 PE 16 行，Local M32 每个 PE 32 行；Shared ND 在 ValidRow 不超过 64 时每个 PE 16 行，否则 32 行。行数为零的 Local PE 不分配也不读取，但仍是参与者。
- Shared ND 的掩码必须是单个 PE 或 1111，并且必须包含当前 PE。单个 PE 不得使用 B.ASSEMBLE，并直接发布 Tile。使用 1111 时 B.ASSEMBLE 是必需的：PE 0 携带 INIT，PE 3 携带 LAST，PE 1 与 PE 2 两者都不携带。其寄存器与立即数必须为零，因为处理程序根据行起点以 32 字节为单位推导每个写者的偏移。父对象只在无空隙的 LAST 写者到达时发布。
- 只写入逻辑矩形及其已定义性；物理存储尾部既不写入，也不标记为已定义。Local CUBE 结果等于 Shared ND 结果再经过普通的 ND 到 CUBE 转换。

## 示例

以下示例勾勒一个协作式 Shared 结果；符号值代表事先准备好的 GPR 或维度。

~~~asm
BSTART.TIMG2COL FP16
B.DIM zero, 64, ->LB0
B.DIM zero, 64, ->LB1
B.DIM zero, 64, ->LB2
B.IOR a0, zero, zero
B.IOR a1, a2, a3
B.IOS mask=1111, ->S0<7>
B.ASSEMBLE 1, 0, zero, 0, 5
BSTOP
~~~

这是 PE 0 的指令束。PE 1 与 PE 2 绑定 B.IOS S0, mask=1111 并使用 B.ASSEMBLE 0, 0, zero, 0, 5，PE 3 使用 B.ASSEMBLE 0, 1, zero, 0, 5。对 FP16，C0 为 16。ValidRow 64 使每个 PE 得到 16 行，每个写者覆盖 16 * 64 / 16 = 64 个 32 字节单位，偏移分别为 0、64、128 和 192。SizeCode 7 为 8192 字节，即 256 个单位，因此 PE 3 的 LAST 范围恰好结束于 256，父对象随之发布。

## 合法性与异常

- 裁剪必须按 C0 对齐：ValidCol、TotalCol 与 ColStart 是 C0 的倍数，ValidCol 不超过 TotalCol，RowStart + ValidRow 不超过 Hout * Wout，ColStart + ValidCol 不超过 KValid。非零的参数扩展位、零尺寸以及错误的绑定数量同样会被拒绝。
- 没有记录故障的失败检查变为 Fault_TileLegality；内存故障保持其自身类型。任何失败时，BundleTIMG2COLAbortFailedAttempt 中止 Shared 代或回滚 Local 目标，因此之前的 Shared 代保持不变。
- 操作的每个输入都在指令束自己的命令与 GPR 中可见。

## 0.59.1 来源

- 当前身份：bstart_timg2col_32_557b5cf18709
- 当前汇编或载体：BSTART.TIMG2COL DataType
- PTO 源：asl/block/execution/BSTART.TIMG2COL.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
