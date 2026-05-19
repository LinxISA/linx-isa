# 灵犀 C++ 启动合约（C++17、LLVM 堆栈、musl-first）

本文档冻结了 灵犀指令集 的托管 C++ 启动合约，因此 gateway
脚本和报告使用一种确定性策略。

## 范围

- 主要运行时堆栈：`compiler-rt` + `libunwind` + `libc++abi` + `libc++`。
- 语言基线：`-std=c++17`。
- 调出配置文件 `CXX17_NOEH`：
  - `-fno-ZXTERMEN38QXZs`
  - `-fno-rtti`
- libc 顺序：musl 通道第一，glibc 通道第二。
- 优惠政策：`pin`和`external`车道均须通过。

## 三重和车道合同

- 裸机编译通道：`linx64-linx-none-elf`。
- 当前分支注释：固定的 Bisheng 编译器通道未注册 `linx32-linx-none-elf`；旧的 `linx32` 参考文献仅保留历史证据。
- 托管 Linux musl 通道：`linx64-unknown-linux-musl`。
- 托管 Linux glibc 通道（后续）：`linx64-unknown-linux-gnu`。

车道角色：

- `pin` 通道：来自超级项目子模块 SHA 的可重现基线。
- `external` 通道：针对主动外部磁头的集成运行状况。

促销规则：

- 切勿仅从一条通道将运行时/C++ 状态提升为绿色。
- 要求两条车道上的通行证分类和证据相匹配。

## Clang 驱动程序合约

- 灵犀 交叉链接不得通过主机 C++ 驱动程序进行路由。
- 灵犀 Linux 和 灵犀 裸机流的默认链接器是 `ld.lld`。
- Linux 灵犀 此阶段默认 C++ 运行时策略：
  - `stdlib=libc++`
  - `rtlib=compiler-rt`
  - `unwindlib=libunwind`（托管 C++ 门的策略目标）

## Sysroot 合约 (musl)

Musl 系统根目录：

- `out/libc/musl/install/<mode>/`

LLVM C++ 运行时覆盖安装根目录：- `out/cpp-runtime/musl-cxx17-noeh/install/`

clang 消耗的预期托管 C++ 布局：

- 标题：
  - `<overlay>/include/c++/v1`
- 运行时库：
  - `<overlay>/lib/libc++.a`
  - `<overlay>/lib/libc++abi.a`
  - `<overlay>/lib/libunwind.a`
  - `<overlay>/lib/clang/<ver>/lib/linx64/libclang_rt.builtins-*.a`（或同等拱形）

合并/安装策略：

- 覆盖工件被复制到 AVS/QEMU 门的活动 musl sysroot 中。
- 门命令中不允许隐藏主机 include/lib 回退。

## Gate ID 和证据政策

新的 AVS ID 保留用于 C++ 启动并记录在：

- `avs/linx_avs_v1_test_matrix.yaml`
- `avs/linx_avs_v1_test_matrix_status.json`

门证据必须包括：

- 准确的命令
- 车道（`pin` 或 `external`）
- SHA 清单（llvm/qemu/linux/musl/glibc/...）
- 通过/失败分类
- 工件路径（日志+摘要）

## 规范命令

构建/安装 musl C++ 运行时覆盖：

```bash
bash tools/build_linx_llvm_cpp_runtimes.sh --mode phase-b
```

C++编译门：

```bash
(cd avs/compiler/linx-llvm/tests && ./run_cpp.sh)
```

Musl C++ 运行时烟门：

```bash
python3 avs/qemu/run_musl_smoke.py --mode phase-b --link both --sample cpp17_smoke
```