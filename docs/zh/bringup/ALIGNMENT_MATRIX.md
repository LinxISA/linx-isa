# 对齐矩阵

本矩阵将当前 v0.58 架构权威与历史 v0.57 兼容性证据分开。历史 PASS
不能转移为 v0.58 结论。

| 主题 | 规范 | 编译器 | 模拟器 | 内核 | 模型 | 证据 |
| --- | --- | --- | --- | --- | --- | --- |
| Linx Linux libc ABI 与重定位 | ✅ ABI 指南与清单 | ✅ 精确升级后的 LLVM gitlink | ✅ 精确升级后的 QEMU gitlink | ✅ 精确升级后的 Linux gitlink | ⚠ 模型升级单独跟踪 | 组件锁与各 leaf 仓检查 |
| Block/descriptor 合约 | ✅ 手册与生成参考 | ✅ 描述符发射测试 | ✅ 已升级实现 | ✅ 用户态 ABI 同步 | ⚠ 当前实现子集 | `bash tools/regression/run.sh` |
| ISA 目录一致性（v0.58） | ✅ golden 目录与 PTO 0.58 精确锁 | ✅ v0.58 leaf 已合入 | ✅ v0.58 leaf 已合入 | ✅ v0.58 leaf 已合入 | ⚠ 单独升级 | `python3 tools/isa/check_canonical_v058.py --root .` |
| ISA 广度（v0.58） | `728` 个合法 mnemonic、`766` 个合法 form | leaf 检查已合入 | L1 `728/728` mnemonic、`759/766` form；L2/L3 不可用 | 精确 gitlink | L1 不测量模型 | `docs/bringup/gates/qemu_isa_coverage_latest.json` |
| AVS QEMU translation（v0.58） | 当前目录 | 需要重新生成当前 pin 对象 | 开放；v0.57 对象报告已归档 | 不适用 | 不适用 | 生成新证据前不得声明通过 |
| Tile 工作负载（v0.58） | VEC/TLSU/CUBE/SFU；TEPL 仅为 VEC/SFU 编码载体 | Linx-TileOP-API | runtime AVS 由 issue 169 跟踪 | 不适用 | 流程只提升独立通过的 ELF | `make -C tools/Linx-TileOP-API check`；`python3 workloads/pto_kernels/scripts/check_supernpu_v058.py` |
