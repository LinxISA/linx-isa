# D1 译码

D1 是第一次完整指令译码阶段。

D1 每周期从独立 Instruction Buffer 读取最多四条连续 entry。每项已包含
完整 64-bit `insn64`、原始 2/4/6/8-byte 长度、PC、
`BSTART`/`BSTOP` boundary、fault 和 request/checkpoint metadata。

D1 对四个 lane 完成完整 opcode、operand、immediate、异常和 split/fuse
译码。它不再获取独立块头，也不重新切分变长字节流。boundary metadata
用于形成 block group；D2/D3 再计算并原子接纳 BROB/ROB、rename、IQ 和
memory-order 资源。
