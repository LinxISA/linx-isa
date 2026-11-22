<!-- LINXISA-SUPPLEMENT: {"catalog": "isa/v0.59/linxisa-v0.59.json", "identity": "sync_core_32_d6367bd93586", "kind": "instruction", "name": "SYNC.CORE", "pto_instruction_sha256": "514131a8b3025c7edc11320016d0d07fd9643fc72d88a431c743e1f08a03f1a9", "pto_source_commit": "a89a53d48f5708328be609fe2e6296ac8bdb4bc2", "pto_source_path": "asl/scalar/sys/SYNC.CORE.asl", "pto_source_sha256": "6441631266888d23b1ff871fca9eb1549e0113c2b5a2b17446d3b426cec3c522", "reader_source_path": "docs/site/i18n/zh-CN/docusaurus-plugin-content-docs-reference/current/scalar/sys/SYNC.CORE.md", "reader_source_sha256": "0efecc624e0e9deee8a08b90c672978db8f1ab06d4cc6e4ab46888166deaf7d5", "schema": "linxisa.manual-supplement.v1", "version": "0.59.1"} -->
# SYNC.CORE

> **0.59.1 增补**

本页按 0.59.1 发布来源说明当前行为、合法性和异常边界。

## 用途

SYNC.CORE 为一次内核调用中同一 Core 的四个 PE 建立局部阶段边界。它确保后续工作不会越过一个尚未完成的早期阶段；该阶段要求所有参与 PE 及其 GM 义务都已完成。

## 输入与输出

- 该指令没有编码操作数，并且始终指代当前 Core 的 PE0、PE1、PE2 和 PE3。它不产生寄存器值或内存值。其可观察结果是：会合和所需 GM 推进完成后，每个参与者都可以越过同一个阶段边界继续执行。

## 执行结果

- 被阻塞的 PE 将 TPC 保持在 SYNC.CORE。完成后，每个参与者较早的合格 GM 操作都排在每个参与者较晚的合格 GM 操作之前；同时使各参与者当前的本地保留失效，并允许每个 PE 恰好前进一次。释放信号会一直保留到被消费，从而避免较快的 PE 丢失完成通知。

## 示例

~~~asm
BSTART.SYS FALL
sync.core
BSTOP
~~~

若 PE0、PE1 和 PE2 先到达该序列，它们都会停驻并把 TPC 保持在 sync.core。当 PE3 不可撤销地到达且先前 GM 义务已经完成后，PE3 继续执行，保留的释放则让另外三个 PE 各继续一次。

## 合法性与异常

- 唯一合法的主体是 BSTART.SYS FALL、一个精确的 sync.core 指令字 0x0330a02b 和 BSTOP。该指令要求存在活动内核调用，且不能从处理程序来源的执行进入。错误的块类型或转移、额外主体操作、畸形或不可取指的结束指令，以及处理程序进入，都会在记录任何屏障到达之前拒绝；既有的包、指令或取指故障指出失败检查。

## 0.59.1 来源

- 当前身份：sync_core_32_d6367bd93586
- 当前汇编或载体：sync.core
- PTO 源：asl/scalar/sys/SYNC.CORE.asl
- PTO 提交：a89a53d48f5708328be609fe2e6296ac8bdb4bc2
