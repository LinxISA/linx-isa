# 对齐矩阵

本矩阵将当前 v0.58.1 架构权威与历史 v0.57 兼容性证据分开。历史 PASS
不能转移为 v0.58.1 结论。

| 主题 | 规范 | 编译器 | 模拟器 | 内核 | 模型 | 证据 |
| --- | --- | --- | --- | --- | --- | --- |
| Linx Linux libc ABI 与重定位 | ✅ PTO ISA 0.58.1 精确 ELF 身份 | ✅ Linx32/Linx64 调用返回与重定位门 | ✅ 精确身份加载矩阵与严格 AVS | ✅ 全新 `vmlinux`；glibc 五变体烟雾通过 | ✅ release-strict 结果内存消费者共用同一精确 manifest | component lock、Linux 来源、glibc 摘要与模型发布报告 |
| Block/descriptor 合约 | ✅ 手册与生成参考 | ✅ 描述符发射测试 | ✅ 已升级实现 | ✅ 用户态 ABI 同步 | ⚠ 当前实现子集 | `bash tools/regression/run.sh` |
| ISA 目录一致性（v0.58.1） | ✅ golden 目录与 PTO 0.58.1 精确锁 | ✅ 精确 LLVM gitlink | ✅ 精确 QEMU gitlink | ✅ 精确 Linux gitlink | ✅ 规范模型 codec 与来源门 | `python3 tools/isa/check_canonical_v058.py --root .` |
| ISA 广度（v0.58.1） | `731` 个合法 mnemonic、`765` 个合法 form | v0.58.1 leaf 检查已合入 | L1 `731/731` mnemonic、`765/765` form；L2/L3 需要独立运行时证据 | 精确 gitlink | L1 不测量模型 | `docs/bringup/gates/qemu_isa_coverage_latest.json` |
| AVS QEMU translation（v0.58.1） | 当前目录 | ✅ 当前汇编与 767/767 decode audit | ✅ 完整严格/运行时 AVS；逐源 translation aggregate 单独跟踪 | 不适用 | 不适用 | 不得重用归档的 v0.57 报告 |
| Tile 工作负载（v0.58） | VEC/TLSU/CUBE/SFU；TEPL 仅为 VEC/SFU 编码载体 | Linx-TileOP-API | runtime AVS 由 issue 169 跟踪 | 不适用 | 流程只提升独立通过的 ELF | `make -C tools/Linx-TileOP-API check`；`python3 workloads/pto_kernels/scripts/check_supernpu_v058.py` |
