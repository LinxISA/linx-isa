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

- 编码和解码假设必须匹配 `isa/v0.58/linxisa-v0.58.json`。
- 块 ISA 控制流不变量必须保持。
- PTO 公共直接调用必须使用原子融合形式
  `BSTART.CALL <br_label>, <rt_label>, ->ra`。
- PTO 公共间接调用必须使用 `BSTART.ICALL <rt_label>, ->ra`；目标来自
  正在退役的 STD/FP block 的 `BARG.BPCN`，且不消费 `SETC.TGT` 或 `SETRET`。
- Linx 独有的长格式 bare call 保持 `ra` 不变；可选的 `SETRET` 或
  `C.SETRET` 配对必须紧邻并位于 bare call 之前。

## 执行

```bash
# Using pinned submodule build
CLANG=$PWD/compiler/llvm/build-linxisa-clang/bin/clang ./avs/compiler/linx-llvm/tests/run.sh

# Or using an external toolchain
# CLANG=/path/to/clang ./avs/compiler/linx-llvm/tests/run.sh
```
