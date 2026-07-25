# IFU：解耦的 I-SIDE 与 B-SIDE

LinxCore IFU 由两个独立反压的引擎组成：

- **I-SIDE**：根据 PC 做地址转换，读取一个 L1I cacheline，只做边界
  预解码，把指令定长化为 64-bit 并写入 Instruction Buffer。
- **B-SIDE**：预测下一控制流 PC，并维护预测器训练、检查点和恢复状态。

两个引擎只通过带 request ID、STID、PC、epoch 的显式 request、
prediction、training 和 redirect 接口交互。

## I-SIDE 流水

I-SIDE 使用 I-F0..I-F4：

| Stage | 职责 |
|---|---|
| I-F0 | 接受/选择 PC，分配 fetch ID 与 epoch，寄存请求 |
| I-F1 | 并行启动 ITLB 与 L1I 访问 |
| I-F2 | 汇合 ITLB/L1I 状态；ITLB miss 产生 I-SIDE inner flush；L1I miss 保留 refill 身份 |
| I-F3 | 保存一个 cacheline、ECC/refill、byte cursor 和跨 line carry |
| I-F4 | 判断 2/4/6/8-byte 长度，只识别 `BSTART`/`BSTOP`，零扩展为 64-bit，写 Instruction Buffer |

Instruction Buffer 位于 I-F4 之后。每个 entry 保存完整 effective prediction
record。D1 每周期读取四条连续 64-bit 指令，每个 valid lane 携带该完整记录，
并完成完整 opcode、operand、immediate、异常和 split/fuse 译码。D1 之后统一
使用 64-bit 指令容器。

## B-SIDE

B-SIDE 使用 B-F0..B-F4：B-F0 L0/NLP+checkpoint，B-F1 uBTB/RAS，
B-F2 PBTB/BTB+BIM，B-F3 short/medium TAGE+IBTB launch，B-F4
static+long-TAGE/IBTB/loop/final arbitration。provider rank 为
`B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential`；B-F4 内使用 exact
RAS/high-confidence IBTB target、
`loop > long-TAGE > short-TAGE > BIM > static`
direction 和 BTB direct target。

I/B 两条流水解耦、不锁步。后级 B-stage 纠正已使用预测时 inner-flush
I-SIDE 并重启 I-F0；B-F4 是最后一个 prediction-driven inner flush 点。
此后 Dispatch/BRU 的校验错误使用 BRU flush/recover 加 frontend restart。

ITLB、L1I、cacheline refill、predecode 和 Instruction Buffer 只属于
I-SIDE。

规范见 [LinxCore IFU 架构](../architecture/linxcore/ifu.md)。
