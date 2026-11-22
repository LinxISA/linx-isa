<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/linxisa-v0.59.json", "identity": "b_fpatr_32_12243b200432", "kind": "instruction", "name": "B.FPATR", "pto_instruction_sha256": "c5a97dba63405083e52e7a5de20b71df9ddfe55514f82bcae42816344a92836c", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/block/attributes/B.FPATR.asl", "pto_source_sha256": "680a0a51e996368ffd8e57cb5dbb137b047ea951be23d7de952ababd5ae50515", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/block/attributes/B.FPATR.md", "reader_source_sha256": "8855d11092dc142cfda335caeb33e96c3aad012b7beca9398b05342aee7aac73", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# B.FPATR

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

B.FPATR（定点后处理属性）是用于 CUBE 矩阵指令块（例如 TMATMUL 和 TGEMV）的 32 位块头命令。它锁存一个描述符，控制累加器结果在发布之前的处理：预量化、激活、行最大值与分组最大值、Shared 输入的逻辑转置，以及显式 FP32 累加器 C 的缩放。

每个 CUBE 矩阵指令块必须恰好包含一条 B.FPATR。其他指令块不得包含它。该描述符由 SetBundleFixedPointAttributeState 写入；见属性模式模型。

## 输入与输出

- 固定位为 W=1（第 0 位）、Opcode=1（第 1 至 3 位）、Opc1=2（第 4 至 6 位）、Reserved=0（第 10 位）、ElementWiseEn=0（第 11 位）和 Func=2（第 12 至 14 位）。其余可变字段包括：
- TransA（第 7 位）与 TransB（第 8 位）：对 Shared A 或 B 主操作数做逻辑转置。
- CScaleEn，第 9 位：对显式 FP32 累加器 C 做逐行缩放。
- MaxAbsEn，第 15 位：按最大绝对值而不是有符号最大值归约。
- RowMaxInit，第 16 位；GroupMaxEn，第 17 位；RowMaxEn，第 18 位。
- GroupNCode，第 19 至 22 位：编码 0 至 9 选择 0、8、16、32、48、64、80、96、112 或 128 列的分组宽度。
- ReluMode，第 23 至 25 位：编码 0 至 3 依次选择无、ReLU、标量 LReLU/PReLU 和向量 PReLU。
- PreQuantMode，第 26 至 31 位：编码 0 至 5、12、13、16 至 20、23 至 28 以及 32 至 39。
- 不在这些编码集合中的值或固定位不匹配都无法译码，并引发 Fault_IllegalInstruction。
- ASL 注释指出 U8 不是 S8 的同义词。每个非零编码同时固定所需的累加器类别（S32 或 FP32）和输出类型；编码 0 接受 FP32、S32 或 U32 并保持该类型。

## 执行结果

- 全零字段表示：无预量化、无激活、无分组最大值、无行最大值、无转置、无 CScale。此时有效输出类型 EffectiveDType 即累加器类型。
- 缺少它的矩阵指令块会在完整预检时以 Fault_BundleControl 失败，因为矩阵操作数模式要求该描述符。全零命令才是请求普通输出的方式。
- 指令块提交时，D、RowMaxOut 与 GroupMaxOut 作为一个输出组一起发布。被拒绝的指令块一个都不发布。RowMax 与 GroupMax 在 EffectiveDType 中对最终编码的 D 值做归约。
- 该描述符在指令块提交时被清除，并在陷阱保存与恢复中随待处理指令块一起保留。

## 示例

~~~asm
B.FPATR None, None, 0, 0, 0, 0, 0, 0, 0, 0
~~~

该命令请求普通输出：累加器为 FP32 时，D 以 FP32 发布。同一块头中的第二条 B.FPATR 引发 Fault_BundleControl。

再看 PreQuantMode 编码 16、ReluMode 1、GroupNCode 2、RowMaxEn=1 与 GroupMaxEn=1。编码 16 需要 FP32 累加器并输出 BF16，因此 EffectiveDType 为 BF16，两种归约都被允许；每个分组最大值覆盖 16 列。编码 16 使用固定舍入，因此矩阵 B.DATR 必须保持 RMode 为零。若改用 PreQuantMode 编码 2，输出类型为 S8，同样的归约使能会在预检时以 Fault_TileLegality 失败。

## 合法性与异常

- 由命令检查，失败时引发 Fault_TileLegality：
- RowMaxInit 要求 RowMaxEn。
- GroupMaxEn 与非零 GroupNCode 互为前提。
- MaxAbsEn 要求 RowMaxEn 或 GroupMaxEn。
- 由完整预检在任何效果之前检查，失败时引发 Fault_TileLegality：
- 累加器类型必须与 PreQuantMode 类别匹配。启用 RowMaxEn 或 GroupMaxEn 时，EffectiveDType 必须是 FP32、FP16 或 BF16。
- TransA 或 TransB 要求对应主操作数为 Shared。CScaleEn 只被 FP32 TMATMUL.ACC 与 TMATMULMX.ACC 接受。
- 矩阵 B.DATR 只提供转换控制：PreQuantMode 为 0 或移位模式（12、13）时，RMode 与 Sat 必须为零；固定舍入模式时，RMode 必须为零。
- 若 B.DATR 设置 CCTRL[0]=1（原始部分和输出），所有后处理与归约字段都必须为零；只保留合法的 CScale。

## 0.59.1 来源

- 当前身份：b_fpatr_32_12243b200432
- 当前汇编或载体：B.FPATR PreQuantMode, ReluMode, GroupNCode, RowMaxEn, GroupMaxEn, RowMaxInit, MaxAbsEn, TransA, TransB, CScaleEn
- PTO 源：asl/block/attributes/B.FPATR.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
