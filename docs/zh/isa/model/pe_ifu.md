# PE IFU

PE IFU 使用统一的 LinxCore IFU 规范。

## I-SIDE

- I-F0 接受/选择 PC 并寄存请求身份；
- I-F1 并行启动 ITLB 和 L1I；
- I-F2 汇合结果，ITLB miss 产生 I-SIDE inner flush；
- I-F3 保存一个 cacheline 和跨 line 字节上下文；
- I-F4 判断 2/4/6/8-byte 长度，只识别 `BSTART`/`BSTOP`，把每条指令
  扩展为 64-bit 并写 Instruction Buffer；
- D1 每周期读取四条 64-bit 指令，每个 valid lane 携带完整 prediction
  record，并完成完整译码。

## B-SIDE

B-SIDE 是独立 B-F0..B-F4 流水：B-F0 L0/NLP+checkpoint，B-F1
uBTB/RAS，B-F2 PBTB/BTB+BIM，B-F3 short/medium TAGE+IBTB launch，
B-F4 static+long-TAGE/IBTB/loop/final arbitration。B-F4 是最后一个
prediction-driven inner flush 点；后续校验 mismatch 使用 BRU
flush/recover。它通过显式接口与 I-SIDE 交互，不与 I-F0..I-F4 锁步。
