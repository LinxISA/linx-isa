# 对齐矩阵

本矩阵跟踪活动 v0.58.3 权威；历史 v0.57 和 v0.58.1 结果不能转移到本发布。

| 主题 | 规范 | 编译器/API | 模拟器 | 内核/libc | Model/workload | 当前证据 |
| --- | --- | --- | --- | --- | --- | --- |
| 精确 PTO 身份 | ✅ v0.58.3 lock 与 ELF descriptor | ✅ LLVM/LLD/TileOP；PTOAS 合入待定 | ✅ loader 拒绝矩阵；QEMU `2ba240fd` | ✅ Linux/glibc/musl 精确身份 | ✅ model/kernels 叶仓；root pin 待定 | PTO lock、叶仓审查、repin 后 component lock |
| ISA catalog 一致性 | ✅ 723 mnemonic、757 form | ✅ LLVM 723/723 linx64 compile AVS | ✅ 当前候选 723/757 decode mapping | 不适用 | ✅ model 权威叶仓 | 规范 ISA 与叶仓报告 |
| HL.LUI/HL.LIU/CSEL 语义 | ✅ catalog、convention、Sail 定向测试 | ✅ LLVM 编码与常量生成 | ✅ 已审查 QEMU 修复合入 | ✅ 最终 LLVM 的干净 vmlinux 已到用户态 | 不适用 | Sail 门禁、QEMU PR 70/72、Linux r6/r7 |
| TLSU 虚拟内存访问 | ✅ IOTCR 未使能时用 CPU 翻译 | ✅ TileOP pointer 接口 | ✅ QEMU PR 74 已合入 | ✅ ACR2 mapped/fault 集成 | 不适用 | issue 73、PR 74、定向差分测试 |
| CUBE DATR/accumulator 路径 | ✅ 每操作 DATR 契约 | ✅ TileOP `bd1ecca9` 输出 compute Zero | ✅ accumulator/compute/publish 与 TLSU | ✅ PID1/fork/exec/exit | ✅ 六个精确 kernel 冷启动通过 | cold matrix SHA `3328caf9…` |
| VECTOR/CUBE 首次使用 | ✅ 执行前、可重试 E_INST/EC_PERM | 不适用 | ✅ QEMU 定向行为 | ⚠ 跨 ACR EXTCTX ABI 完成前 V/C 默认关闭 | 不适用 | root issue 182、Linux issue 32 |
| 完整 release-strict 闭包 | ✅ 策略已定义 | ⏳ 最终 PTOAS 合入/pin | ✅ QEMU 与六用例冷启动矩阵 | ✅ 精确 boot summary | ⏳ 最终 lock 的新鲜 model 报告 | 所有等待项关闭前不得晋级 |
