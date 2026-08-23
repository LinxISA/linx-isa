# 对齐矩阵

本矩阵跟踪活动 v0.58.3 权威；历史 v0.57 和 v0.58.1 结果不能转移到本发布。

| 主题 | 规范 | 编译器/API | 模拟器 | 内核/libc | Model/workload | 当前证据 |
| --- | --- | --- | --- | --- | --- | --- |
| 精确 PTO 身份 | ✅ v0.58.3 lock 与 ELF descriptor | ✅ LLVM/LLD；TileOP/PTOAS 最终 pin 待定 | ✅ loader 拒绝矩阵；最终 QEMU pin 待定 | ✅ Linux/glibc/musl 精确身份 | ✅ model/kernels 叶仓；root pin 待定 | PTO lock、叶仓审查、repin 后 component lock |
| ISA catalog 一致性 | ✅ 723 mnemonic、757 form | ✅ LLVM 723/723 linx64 compile AVS | ✅ 当前候选 723/757 decode mapping | 不适用 | ✅ model 权威叶仓 | 规范 ISA 与叶仓报告 |
| HL.LUI/HL.LIU/CSEL 语义 | ✅ catalog、convention、Sail 定向测试 | ✅ LLVM 编码与常量生成 | ✅ 已审查 QEMU 修复合入 | ✅ 最终 LLVM 的干净 vmlinux 已到用户态 | 不适用 | Sail 门禁、QEMU PR 70/72、Linux r6/r7 |
| TLSU 虚拟内存访问 | ✅ IOTCR 未使能时用 CPU 翻译 | ✅ TileOP pointer 接口 | ⏳ QEMU PR 74 | ✅ ACR2 Linux 集成已越过 TLOAD | 不适用 | issue 73、PR 74、r7 |
| CUBE DATR/accumulator 路径 | ✅ 每操作 DATR 契约 | ⏳ TileOP PR 27 输出 compute Zero | ⏳ 合法 r8 preflight 后由 QEMU issue 75 跟踪 | ✅ PID1/fork/exec | ✅ 六个精确 kernel 编译/链接 | r8 summary 与关联 issue |
| VECTOR/CUBE 首次使用 | ✅ 执行前、可重试 E_INST/EC_PERM | 不适用 | ✅ QEMU 定向行为 | ⚠ 跨 ACR EXTCTX ABI 完成前 V/C 默认关闭 | 不适用 | root issue 182、Linux issue 32 |
| 完整 release-strict 闭包 | ✅ 策略已定义 | ⏳ 最终 PTOAS/TileOP pin | ⏳ 最终 QEMU 与六用例 system PASS | ⏳ 最终精确 boot summary | ⏳ 最终 lock 的新鲜 model 报告 | 所有等待项关闭前不得晋级 |
