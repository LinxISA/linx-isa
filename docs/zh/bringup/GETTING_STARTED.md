# 灵犀指令集 启动入门

本指南是贡献者加入 灵犀指令集 启动工作区的入口点。

## 1.先决条件

### 平台说明

- **Linux**：支持（推荐）。
- **macOS**：支持大多数编译器/模拟器/工具工作。
- **Windows**：
  - **通过 WSL2** 支持（推荐），
  - 本机 Windows 可用于编辑 + 一些工具，但大多数门都需要 POSIX shell。

### 必填

- `git`
- `python3`
- 用于运行 `*.sh` 门的 POSIX shell（Linux/macOS 或 Windows+WSL2）
- `clang` + `ld.lld` 用于 灵犀 交叉构建（来自固定的 LLVM 子模块构建或外部工具链）

### 推荐

- `gh`（GitHub CLI）

## 2. 克隆子模块

```bash
git clone --recurse-submodules git@github.com:ZXTERMEN40QXZ/linx-isa.git
cd linx-isa
git submodule sync --recursive
git submodule update --init --recursive
```

子模块图：

- `compiler/llvm` -> `ZXTERMEN40QXZ/llvm-project`
- `emulator/qemu` -> `ZXTERMEN40QXZ/qemu`
- `kernel/linux` -> `ZXTERMEN40QXZ/linux`
- `rtl/ZXTERMEN45QXZCore` -> `ZXTERMEN40QXZ/ZXTERMEN45QXZCore`
- `tools/pyCircuit` -> `ZXTERMEN40QXZ/pyCircuit`
- `lib/glibc` -> `ZXTERMEN40QXZ/glibc`
- `lib/musl` -> `ZXTERMEN40QXZ/musl`
- `workloads/pto_kernels` -> `ZXTERMEN40QXZ/PTO-Kernel`

## 3. 验证基线

从仓库根目录：

```bash
bash tools/regression/run.sh
```

可选覆盖：

```bash
# Tool paths can come from:
# - pinned submodules (recommended for reproducibility)
# - external installs (recommended for day-to-day dev if you already have them)
#
# If you built the pinned submodules:
export CLANG=$PWD/compiler/llvm/build-linxisa-clang/bin/clang
export LLD=$PWD/compiler/llvm/build-linxisa-clang/bin/ld.lld
export QEMU=$PWD/emulator/qemu/build/qemu-system-linx64

# Or point to external toolchains:
# export CLANG=/path/to/clang
# export LLD=/path/to/ld.lld
# export QEMU=/path/to/qemu-system-linx64

bash tools/regression/run.sh
```

运行合约门：

```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
python3 tools/bringup/check_avs_profile_closure.py --matrix avs/linx_avs_v1_test_matrix.yaml --status avs/linx_avs_v1_test_matrix_status.json --tier pr
```

## 4.日常工作流程

1. 在 `docs/bringup/phases/` 下选择示波器。
2. 首先在相关子模块/repo 中实现。
3. 在本地运行 AVS + 回归门。
4. 合并生态系统存储库中的上游。
5. 修改 `linx-isa` 中的子模块 SHA。

子模块凹凸命令：

```bash
git submodule update --remote compiler/llvm emulator/qemu kernel/linux rtl/ZXTERMEN45QXZCore tools/pyCircuit lib/glibc lib/musl workloads/pto_kernels
git add .gitmodules compiler/llvm emulator/qemu kernel/linux rtl/ZXTERMEN45QXZCore tools/pyCircuit lib/glibc lib/musl workloads/pto_kernels
git commit -m "chore(submodules): bump ecosystem revisions"
```

## 5. 规范路径- AVS 运行时测试：`avs/qemu/`
- AVS编译测试：`avs/compiler/linx-llvm/tests/`
- AVS 使用的独立 libc 支持：`avs/runtime/freestanding/`
- Linux libc 源代码分支：`lib/glibc/`、`lib/musl/`
- PTO内核块头s：`workloads/pto_kernels/include/`
- 组装样品包：`docs/reference/examples/v0.56/`

## 6. 协调参考

- 调出进度：`docs/bringup/PROGRESS.md`
- 合约检查点：`docs/bringup/AVS_CONTRACT.md`
- 渲染用户空间启动：`docs/bringup/rendering_vulkan_bringup.md`
- 规范门注册表：`docs/bringup/gate_registry.json`
- 导航指南：`docs/project/navigation.md`