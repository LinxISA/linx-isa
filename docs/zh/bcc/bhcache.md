# I-SIDE L1 指令 Cache

取指 cache 属于 I-SIDE，是 I-F0..I-F4 流水的 L1I 服务，不是 B-SIDE
预测结构，也不兼任 BTB。

- I-F1 对同一虚拟 PC 和请求身份并行访问 ITLB 与 L1I。
- I-F2 用翻译后的物理 tag 校验 L1I 查询。
- ITLB miss 产生 I-SIDE inner flush，阻止投机 L1I 结果形成指令。
- L1I miss 在 refill 全程保留 request ID、STID、PC 和 epoch。
- I-F3 保存完整 cacheline、ECC/refill 状态和字节流上下文。

容量、组相联度、bank、替换和 ECC 是实现参数，但必须保证响应身份、
精确取指异常、陈旧响应丢弃和前向进展。

L1I 只提供字节。I-F4 负责长度判断、`BSTART`/`BSTOP` 边界识别、64-bit
定长化和 Instruction Buffer 写入。
