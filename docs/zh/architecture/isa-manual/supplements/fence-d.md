<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/linxisa-v0.59.json", "identity": "fence_d_32_995ba6ba6bb7", "kind": "instruction", "name": "FENCE.D", "pto_instruction_sha256": "8381ce2cd126dcf972e657bf42c4cad3888d3a0e853628032732ad18f0ef0ffa", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/scalar/sys/FENCE.D.asl", "pto_source_sha256": "e76e608967534abdb78c76b8436bf4af29c4b397375e7e2822761ba3037e7db8", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/scalar/sys/FENCE.D.md", "reader_source_sha256": "62213bc711d3c75a02cf660ef0911687834566b8755c39f75758a5b6b928308a", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# FENCE.D

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

FENCE.D 是带显式前驱与后继访问类别掩码的数据排序屏障。两个掩码都是编码中的 4 位立即数而不是寄存器，因此该屏障描述哪些类别的访问必须被排序，而不从标量寄存器堆读取任何操作数。

## 输入与输出

- PRED_IMM 是 4 位前驱访问类别掩码，SUCC_IMM 是 4 位后继掩码。每个字段的全部十六个值都已分配，因此没有掩码值被保留，也没有字段是可选的。
- FENCE.D 没有目的地操作数。它不读取任何寄存器，因此不从寄存器堆快照任何内容；编码零是已分配的掩码值，而不是省略的操作数。

## 执行结果

- 该屏障清除本地保留，并把两个掩码记录为一个数据屏障事件。如果任一掩码的第 3 位被置位，指令缓存纪元也会递增一。随后 TPC 按指令长度前进，因为该处理程序不写自己的 TPC。
- 因此任一位置掩码为 8 的屏障具有指令可见性副作用，而掩码为 1 与 1 的屏障没有；同一条编码指令的行为始终一致。
- 该指令没有内存效果：不产生普通内存读写事件，且 FenceData 不触碰内存。它也不写任何寄存器或临时队列。

## 示例

在 SYS 块体内运行 fence.d 8, 1。保留被清除，前驱掩码 8 与后继掩码 1 被记录为一个屏障事件；由于前驱掩码的第 3 位被置位，指令缓存纪元递增一。运行 fence.d 1, 1 会清除保留并记录掩码，且不改变纪元。

## 合法性与异常

- FENCE.D 在活动 SYS 块体中执行。在其他位置的尝试会在掩码被读取之前引发 Fault_BundleControl，因此保留、已记录的掩码以及指令缓存纪元都保持先前值。
- 由于每个 4 位掩码值都已分配，这些字段不存在保留编码的拒绝。该 32 位形式的固定位仍在处理程序运行之前完成校验，且该操作不受访问环限制。

## 0.59.1 来源

- 当前身份：fence_d_32_995ba6ba6bb7
- 当前汇编或载体：fence.d pred_imm, succ_imm
- PTO 源：asl/scalar/sys/FENCE.D.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
