# Decode 与 Dispatch Model 映射

目标后端输入是 D1 从 Instruction Buffer 读取的最多四条固定 64-bit
指令组成的 group。

1. D1 完成 opcode、operand、immediate、异常和 split/fuse 完整译码；
2. D2 计算 BROB/ROB、rename、IQ、memory-order 完整资源需求并解析
   block boundary ownership；
3. D3 原子接纳整个 group，否则不改变任何分配状态；
4. Dispatch 把已接纳 uop 路由到对应 execution-class issue structure。

`bfu_be_q`、`MachineHeader`、`decodeBlockHeader()` 等名称只描述当前
可执行 Model 的代码组织，可用于行为对照，但不是目标 IFU-to-OOO
接口，也不定义独立块头译码路径。
