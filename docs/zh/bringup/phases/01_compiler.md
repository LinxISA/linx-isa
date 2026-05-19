# 第 1 阶段：编译器启动

编译器实现的真实来源是 LLVM 子模块：

- `compiler/llvm/`

仓库内编译验证资产集中在 AVS 下：

- `avs/compiler/linx-llvm/tests/`

## 当前检查点

- 常用的主机编译器二进制文件：
  - 固定子模块构建：`compiler/llvm/build-linxisa-clang/bin/clang`
  - 或外部工具链（设置 `CLANG=/path/to/clang`）
- 当前币升分支支持的启动目标：`linx64-linx-none-elf`
- 签入的编译器当前注册了 `linx64` / `linx64be`；旧的 `linx32` 参考是存档的启动历史记录，而不是活动的必需门。
- 编译测试套件入口点：`avs/compiler/linx-llvm/tests/run.sh`

## 必需的不变量

- 编码和解码假设必须匹配 `isa/v0.56/linxisa-v0.56.json`。
- 块 ISA 控制流不变量必须保持。
- 调用 块头 邻接规则 (`BSTART CALL` + `SETRET`) 必须成立。

## 执行

```bash
# Using pinned submodule build
CLANG=$PWD/compiler/llvm/build-linxisa-clang/bin/clang ./avs/compiler/linx-llvm/tests/run.sh

# Or using an external toolchain
# CLANG=/path/to/clang ./avs/compiler/linx-llvm/tests/run.sh
```