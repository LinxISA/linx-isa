# IFU Model 映射

目标 IFU 由两个解耦引擎组成：

- I-SIDE：`I-F0 -> I-F1 -> I-F2 -> I-F3 -> I-F4 -> Instruction Buffer -> D1`；
- B-SIDE：`B-F0 -> B-F1 -> B-F2 -> B-F3 -> B-F4`。

LinxCoreModel BFU 只作为 BTB 类结构、GHR/GHRQ、TAGE、BIM、RAS、
IBTB、loop prediction、预测仲裁、BRQ/checkpoint 和恢复算法的参考。
Model BFU 的内部 stage 标签不覆盖目标 I/B 前缀。映射为 B-F0
L0/NLP+checkpoint、B-F1 uBTB/RAS、B-F2 PBTB/BTB+BIM、B-F3
short/medium TAGE+IBTB launch、B-F4 static+long-TAGE/IBTB/loop/final
arbitration。

provider rank 为
`B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential`。I/B 两侧解耦、不锁步；
B-F4 是最后一个 prediction-driven inner flush 点。final record 随每条指令
进入 D1；post-B-F4 Dispatch/BRU mismatch 使用 BRU flush/recover 加
frontend restart。

I-SIDE 在 I-F1 并行访问 ITLB/L1I，并独立拥有 ITLB-miss inner flush、cacheline
处理、边界预解码、64-bit 定长化和 Instruction Buffer 写入。D1 每周期
读取四条 `insn64`，每个 valid lane 携带完整 prediction record，并完成完整
译码。

规范见 [LinxCore IFU 架构](../../architecture/linxcore/ifu.md)。
