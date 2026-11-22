<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/linxisa-v0.59.json", "identity": "fence_i_32_85d88bc9693d", "kind": "instruction", "name": "FENCE.I", "pto_instruction_sha256": "19f6efb778878b1b4705f2f3d723719779277094856e38e70172477428c48953", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/scalar/sys/FENCE.I.asl", "pto_source_sha256": "166bf895c86b85ee8085f090166b3ed6a653603b9c793dd2f8921f7f93b733b4", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/scalar/sys/FENCE.I.md", "reader_source_sha256": "78159abf9b563136af6608583e7bb40222d4174298bf303e20372a59cc764508", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# FENCE.I

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

FENCE.I 是指令可见性屏障。它没有操作数、没有掩码、也没有目的地：整个 32 位形式都是固定的，该指令的全部职责就是让指令缓存纪元前进并清除本地保留。

## 输入与输出

- 完全没有编码操作数。该形式的每一位都是固定的，因此无法改变任何选择器、掩码或立即数，该指令也无法用来指名比整个指令流更窄的作用域。
- FENCE.I 不写目的地寄存器、临时队列项或系统寄存器。它唯一的输出是保留状态与指令缓存纪元。

## 执行结果

- 该指令清除本地保留，即后续 StoreConditional 成功所需的 _ReservationValid 状态，并恰好把指令缓存纪元递增一。随后它为该 32 位形式把 TPC 推进 4 字节。
- 不存在让指令缓存纪元保持不变的 fence.i 编码，也不存在总是推进它的 fence.d 编码。
- 该指令不发出数据内存事件，也不执行普通标量内存访问，因此不改变任何内存位置。针对数据访问的排序由 FENCE.D 负责。

## 示例

在 SYS 块体内执行 fence.i。保留被清除，指令缓存纪元递增一，TPC 继续前进 4 字节。在标准块体中的尝试则会引发 Fault_BundleControl。

## 合法性与异常

- 唯一可用的拒绝是位置。在活动 SYS 块体之外的尝试会引发 Fault_BundleControl 并在处理程序之前返回，因此保留仍然有效、纪元保持原值。没有保留编码可拒绝，因为所有位都是固定的，也没有操作数需要校验。
- 不需要任何访问环。维护路径中的环限制属于四个 TLB 操作，而 FENCE.I 根本不使用那条路径。

## 0.59.1 来源

- 当前身份：fence_i_32_85d88bc9693d
- 当前汇编或载体：fence.i
- PTO 源：asl/scalar/sys/FENCE.I.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
