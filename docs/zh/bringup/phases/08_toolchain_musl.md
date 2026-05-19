# 第 8 阶段：工具链/musl 启动

规范源存储库：

- `lib/musl` (`git@github.com:ZXTERMEN40QXZ/musl.git`)

## 目标

调出可重现的 灵犀 musl 路径：

- `linx64-unknown-linux-musl` (`M1/M2/M3`)
- Linux initramfs 运行时烟雾与使用 `malloc/free/printf` (`R1/R2`) 的真实 C 程序

## 入口点

- musl 构建入口点：
  - `lib/musl/tools/linx/build_linx64_musl.sh`
- 运行时安全带：
  - `avs/qemu/run_musl_smoke.py`
- 运行时示例程序：
  - `avs/qemu/tests/linux_musl_malloc_printf.c`

## 默认工件布局

- musl 构建/安装/日志：
  - `out/libc/musl/build`
  - `out/libc/musl/install`
  - `out/libc/musl/logs`
- 烟雾输出：
  - `avs/qemu/out/musl-smoke/initramfs.cpio`
  - `avs/qemu/out/musl-smoke/musl_smoke`
  - `avs/qemu/out/musl-smoke/qemu.log`
  - `avs/qemu/out/musl-smoke/summary.json`

## 模式

- `phase-b`：
  - 严格模式（`LINX_MUSL_MODE=phase-b`）
  - 不允许临时排除
- `phase-a`：
  - 通过 `LINX_MUSL_EXTRA_EXCLUDES` 进行临时排除的可选兼容模式
  - 在 `out/libc/musl/logs/phase-a-exclusions.md` 中记录活动排除和崩溃签名

## 命令

构建musl（`M1/M2/M3`）：

```bash
cd lib/musl
MODE=phase-b ./tools/linx/build_linx64_musl.sh
```

运行端到端烟雾（`R1/R2`）：

```bash
cd .
python3 avs/qemu/run_musl_smoke.py --mode phase-b
```

## 现状 (2026-02-16)- `M1`：通过。
- `M2`：传入`phase-b`（严格，暂时不排除）。
- `M3`：传入`phase-b`（共享`lib/libc.so`产生）。
- `arch/linx64` 原子：`a_cas`/`a_cas_p` 现在使用 `swapw` 支持的进程全局锁（已删除非原子加载/存储 CAS）。
- `R1`：通过（示例使用 musl sysroot 静态编译/链接，没有额外的线束后备对象）。
- `R2`：通过（在 `avs/qemu/out/musl-smoke/qemu.log` 中观察到 `MUSL_SMOKE_START` 和 `MUSL_SMOKE_PASS`）。
- Linux no-libc initramfs 基线 (`smoke.py` / `full_boot.py`)：通过默认 QEMU 路径选择。
  - 信号小程序当前在强化信号返回路径时发出回退 `sigill: ok` / `sigsegv: ok` 标记。

## 基线重现指针

- 基线冻结：
  - `out/libc/musl/logs/baseline.md`
- 最新的 Linux 用户空间启动结果：
  - `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/smoke.py`
  - `python3 ${LINUX_ROOT}/tools/linxisa/initramfs/full_boot.py`

## 退出标准

- `M1/M2` 在严格模式 (`phase-b`) 下通过，没有临时排除。
- `M3`传入`phase-b`（`out/libc/musl/logs/phase-b-summary.txt`显示`m3=pass`）。
- 在 QEMU 下观察运行时哨兵：
  - `MUSL_SMOKE_START`
  - `MUSL_SMOKE_PASS`