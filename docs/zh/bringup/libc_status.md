# 灵犀 libc 启动状态

规范的 libc 来源：

- `lib/glibc`
- `lib/musl`

## 存储库和引脚

- `lib/glibc` @ `69493c1b395a23546cab196947d6424003a9f5ed`
- `lib/musl` @ `5b90c23dde11df89f37cf004256dff738510b469`

## 当前政策

- 调出增量存在于分叉历史记录中（`ZXTERMEN40QXZ/glibc`、`ZXTERMEN40QXZ/musl`）。
- 该存储库提供编排、运行时烟雾和状态跟踪。
- 发布严格门控使用来自 `docs/bringup/gates/latest.json` 的规范工件。

## 现状 (2026-04-18)

- glibc `G1a`：通过（`configure` + `csu/subdir_lib` + 启动对象）
- glibc `G1b`：通过（`out/libc/glibc/logs/g1b-summary.txt`）
- Linux/QEMU 上的 glibc 动态运行时：通过 (`avs/qemu/out/glibc-smoke/summary.json`)
- musl运行时`R1`：通过
- musl运行时`R2`：通过

## 证据指针

- 规范门神器：`docs/bringup/gates/latest.json`
- 渲染门表：`docs/bringup/GATE_STATUS.md`
- glibc 构建日志：`out/libc/glibc/logs/summary.txt`、`out/libc/glibc/logs/g1b-summary.txt`
- musl日志：`avs/qemu/out/musl-smoke/summary.json`
- glibc 运行时门：`avs/qemu/run_glibc_smoke.py`、`avs/qemu/out/glibc-smoke/summary.json`

## 注释- 发布严格签核不允许对所需的 libc 门进行阻止豁免。
- 运行时数字/基准奇偶校验仍然超出 libc 启动范围。
- `avs/qemu/run_glibc_smoke.py` 现在充当完整的树内 glibc hello 矩阵门，而不是单个二进制烟雾。它为每个变体重建一个包装器 initramfs 并运行 `entry_main`、`shared`、`startup` 和 `startup_norpath`。
- 当前矩阵结果为 `4/4` 通过。修复后的 `shared` 变体现在被重建为有效的基于 `crt1` 的可执行文件，而不是重用具有 `e_entry=0` 而没有 `_start` 的过时的畸形工件。
- 运行时通道的决定性加载器端更改仍然是 glibc 中与 灵犀 NOMMU 兼容的连续映像 PT_LOAD 路径，这避免了当前 Linux NOMMU 通道无法执行的精确地址文件重新映射。