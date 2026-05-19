# 灵犀指令集 Navigation Guide (v0.5)

这是贡献者和代理的规范导航合约。

## 顶级地图

- `README.md` — workspace overview
- `AGENTS.md` — 面向代理的路由和护栏
- `avs/` — 架构验证套件
- `compiler/` — 编译器端子模块（`compiler/llvm`、`compiler/ptoas`）
- `emulator/` — 上游 QEMU 子模块 (`emulator/qemu`)
- `kernel/` — 上游 Linux 子模块 (`kernel/linux`)
- `rtl/` — 灵犀Core 子模块 (`rtl/ZXTERMEN45QXZCore`) + rtl 注释
- `tools/` — 生成器、回归、pyCircuit 子模块
- `workloads/` — 基准运行程序 + 生成的工件 + PTO 内核子模块
- `isa/` — ISA 事实来源和生成的目录
- `docs/` — 架构、启动、迁移、项目参考
- `lib/` — glibc/musl fork submodules

## Canonical test locations

- Runtime AVS suites: `avs/qemu/`
- Compile AVS suites: `avs/compiler/linx-llvm/tests/`
- AVS matrix/docs: `avs/`

## Canonical 工具链支持位置

- AVS/测试使用的独立 libc 支持：`avs/runtime/freestanding/`
- Linux libc 源代码分支：`lib/glibc/`、`lib/musl/`
- PTO装配叉：`compiler/ptoas/`
- PTO 内核/工具/块头（子模块）：`workloads/pto_kernels/`
- PTO 块头 包括根：`workloads/pto_kernels/include/`
- LLVM opcode sync helper: `tools/isa/sync_generated_opcodes.sh`

## 基准位置

- CoreMark upstream: `workloads/coremark/upstream/`
- Dhrystone上游：`workloads/dhrystone/upstream/`
- PolyBench source cache: `workloads/third_party/PolyBenchC/`
- 调整转轮：`workloads/ctuning/`

## 删除/禁止的路径

不要添加或恢复这些路径：- `compiler/linx-llvm`
- `emulator/linx-qemu`
- `examples/`
- `models/`
- `toolchain/`
- `tests/`
- `docs/validation/avs/`
- `tools/ctuning/`
- `tools/libc/`
- `tools/glibc/`
- `workloads/benchmarks/`
- `workloads/examples/`
- `spec/`

CI防护装置：`tools/ci/check_repo_layout.sh`

## 子模块策略

当实施存储库发生变化时：

1. 首先合并到上游生态系统仓库中。
2. 更新此工作区中的子模块 SHA。
3. 保持 `.gitmodules` URL 与 灵犀指令集 org forks/repos 保持一致。
4. 验证：

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```