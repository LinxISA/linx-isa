# LinxCore 块控制前端

LinxCore 前端取普通指令流，并保留由 `BSTART`/`BSTOP` 表达的架构块边界。

IFU 分为：

- [I-SIDE 与 IFU 总体](./bifu.md)：拥有 I-F0..I-F4 取指流水和
  Instruction Buffer 写入；
- [B-SIDE](./bp.md)：拥有解耦 B-F0..B-F4 跳转预测流水。

两条流水独立反压、不锁步。D1 从 Instruction Buffer 每周期读取四条
固定 64-bit 指令，再把完整
译码组交给 OOO 资源准备。
