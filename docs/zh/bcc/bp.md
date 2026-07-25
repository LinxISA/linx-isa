# B-SIDE 跳转预测引擎

B-SIDE 是 IFU 中与 I-SIDE 解耦的跳转预测引擎，不拥有 ITLB、L1I、
cacheline、predecode 或 Instruction Buffer。

## 预测流水

- B-F0：L0/NLP、checkpoint、GHR/GHRQ/RAS 快照；
- B-F1：uBTB、fast RAS，并启动较大预测表访问；
- B-F2：PBTB/BTB 和 BIM；
- B-F3：short/medium TAGE 并启动 IBTB；
- B-F4：long TAGE、final IBTB、loop、RAS final check 和统一仲裁；
- training/update：独立于 I-SIDE 反压接受已解析结果。

provider rank 为
`B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential`。B-F4 内使用 exact
RAS/high-confidence IBTB target、`loop > long-TAGE > short-TAGE > BIM`
direction 和 BTB direct target。backend restart 优先级更高，但属于
typed-recovery source。

I-SIDE 请求携带 `{fetch_id, stid, epoch, pc}`，B-SIDE 响应携带相同
身份以及 `{taken, branch_pc, target, kind, checkpoint_id, source}`。resolve 和
redirect 接口负责恢复 GHR/RAS/checkpoint，并禁止陈旧响应被消费。

B-F0..B-F4 与 I-F0..I-F4 解耦、不锁步。后级预测纠正已使用结果时，
inner-flush I-SIDE 并重启 I-F0；backend misprediction 使用 typed
recovery 加 frontend restart。
