# 第 7 阶段：工具链/glibc 启动

规范源存储库：

- `lib/glibc` (`git@github.com:ZXTERMEN40QXZ/glibc.git`)

## 目标

在派生的 glibc 存储库中跟踪并验证 `linx64-unknown-linux-gnu` 的 灵犀 glibc 启动。

## 启动序列中的角色

- 此阶段在编译器/模拟器/内核基础知识之后关闭 Linux 用户空间工具链拦截器。
- 它是第 4-6 阶段的支持工作，不会取代 RTL/Linux 验证门。

## 工作流程

从 `lib/glibc` 子模块：

```bash
cd lib/glibc
bash tools/linx/build_linx64_glibc.sh
bash tools/linx/build_linx64_glibc_g1b.sh
```

工件和日志：

- 默认日志：`out/libc/glibc/logs/02-configure.log`、`out/libc/glibc/logs/03-make.log`、`out/libc/glibc/logs/summary.txt`。
- `G1b` 摘要：`out/libc/glibc/logs/g1b-summary.txt`（显式 `status` + `classification`）。
- `G1a` 门证明 `configure` + `csu/subdir_lib` 并生成启动对象（`crt*.o`）。
- `G1b` 跟踪共享的 `libc.so` 构建状态和阻止者签名（如果被阻止）。

## 当前的门

- `G1a`：配置+`csu/subdir_lib`+启动对象制作（`crt1.o`）。
- `G1b`：完全共享的 `libc.so` 构建证明。

## 退出标准

- `G1a` 传递参考启动主机/工具链。
- `G1b` 由 `build_linx64_glibc_g1b.sh` 测量，状态在 `docs/bringup/libc_status.md` 中跟踪。
- 工具链/libc 不再阻塞 Linux shell/用户空间门。
- 剩余问题在 `docs/bringup/libc_status.md` 中明确跟踪。