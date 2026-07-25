# BCC / LinxCoreModel 映射

LinxCoreModel 是可执行行为参考，不拥有目标架构 stage 命名。

IFU 映射规则：

- cacheline 取指机制映射到 I-SIDE；
- 预测算法映射到解耦 B-SIDE；
- I-SIDE 映射 I-F0..I-F4，B-SIDE 映射 B-F0..B-F4；
- 两条流水独立反压、不锁步；
- Model BFU 内部顺序映射为 B-stage 职责和 provider rank；
- D1 从 Instruction Buffer 读取四条固定 64-bit 指令。

- [查看 IFU Model 映射](./BIFU.md)
- [查看 Decode](./BCTRL.md)
- [查看 BROB](./BROB.md)
