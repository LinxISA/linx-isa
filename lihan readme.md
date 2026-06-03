# Linx QEMU User-Mode Bring-Up Notes

本文记录本次 `linx-linux-user` bring-up 的两类工作：

- QEMU user-mode 编译阶段的问题修复。
- LLVM 生成的 Linx C 程序在 `qemu-linx` 中运行时暴露的问题修复。

目标命令：

```bash
../configure --target-list=linx-linux-user --disable-werror --disable-bpf
make -j2
```

## 当前状态

QEMU user-mode 已编译通过：

```text
emulator/qemu/build-user/qemu-linx
```

版本验证：

```bash
emulator/qemu/build-user/qemu-linx --version
```

输出：

```text
qemu-linx version 7.0.0
```

最小 C 程序也已经通过 LLVM 编译，并在 `qemu-linx` 中运行成功：

```text
avs/qemu/tests/lihan_qemu_user_hello.c
```

编译命令：

```bash
compiler/llvm/build-linxisa-clang/bin/clang \
  --target=linx64-unknown-linux-gnu \
  -O2 -nostdlib -static -fuse-ld=lld -Wl,-e,_start \
  -o /tmp/linx-lihan-qemu-user/lihan_qemu_user_hello \
  avs/qemu/tests/lihan_qemu_user_hello.c
```

运行命令：

```bash
emulator/qemu/build-user/qemu-linx /tmp/linx-lihan-qemu-user/lihan_qemu_user_hello
```

运行输出：

```text
Hello from Linx LLVM + qemu-usermode
```

`-strace` 验证：

```text
write(1,0x7ffa32,37) = 37
exit_group(0)
```

## 一、QEMU 编译阶段修复

这些问题是在执行 `make -j2` 编译 `linx-linux-user` 时暴露的。目标是先让 `qemu-linx` 这个 user-mode binary 能完整链接出来。

### 1. target_sigaltstack 重复定义

失败现象：

```text
error: redefinition of 'struct target_sigaltstack'
error: conflicting types for 'target_stack_t'
```

原因：

`linux-user/linx/target_signal.h` 自己定义了一份 `target_sigaltstack`/`target_stack_t`，随后又包含 `../generic/signal.h`。generic signal 里也定义了同名结构。

修复：

- 删除 Linx 私有重复定义。
- 让 Linx 和 `riscv`、`openrisc` 一样复用 `../generic/signal.h`。

修改文件：

```text
emulator/qemu/linux-user/linx/target_signal.h
```

### 2. 缺少 target_resource.h

失败现象：

```text
fatal error: target_resource.h: No such file or directory
```

原因：

`linux-user/syscall_defs.h` 会包含架构目录下的 `target_resource.h`，但 Linx 目录没有这个文件。

修复：

新增 Linx wrapper，直接复用 generic RLIMIT 定义：

```c
#include "../generic/target_resource.h"
```

新增文件：

```text
emulator/qemu/linux-user/linx/target_resource.h
```

### 3. special errno 名称过旧

失败现象：

```text
error: 'TARGET_ERESTARTSYS' undeclared
error: 'TARGET_QEMU_ESIGRETURN' undeclared
```

原因：

当前 QEMU linux-user 公共层使用的是：

```text
QEMU_ERESTARTSYS
QEMU_ESIGRETURN
```

Linx 代码还在用旧名字。

修复：

- `TARGET_ERESTARTSYS` 改为 `QEMU_ERESTARTSYS`。
- `TARGET_QEMU_ESIGRETURN` 改为 `QEMU_ESIGRETURN`。

修改文件：

```text
emulator/qemu/linux-user/linx/cpu_loop.c
emulator/qemu/linux-user/linx/signal.c
```

### 4. 缺少 target_prctl.h

失败现象：

```text
fatal error: target_prctl.h: No such file or directory
```

原因：

`linux-user/syscall.c` 的 prctl 路径要求每个 linux-user 架构目录提供 `target_prctl.h`。Linx 当前没有特殊 prctl 行为。

修复：

新增空语义头文件：

```c
/* No special prctl support required. */
```

新增文件：

```text
emulator/qemu/linux-user/linx/target_prctl.h
```

## 二、LLVM + qemu-user 运行验证阶段修复

这些问题是在 `qemu-linx /tmp/linx-lihan-qemu-user/lihan_qemu_user_hello` 运行 LLVM 生成的 Linx ELF 时暴露的。

### 1. QEMU ELF machine ID 与 LLVM 不一致

失败现象：

```text
qemu-linx: Invalid ELF image for this architecture
```

LLVM 生成的 ELF header 是：

```text
Machine: EM_LINXISA (0xE9)
```

但 QEMU 中 `EM_LINX` 原先定义为 `261`，导致 loader 拒绝 LLVM 产物。

修复：

将 QEMU 的 `EM_LINX` 对齐到 LLVM 的 `EM_LINXISA = 233`。

修改文件：

```text
emulator/qemu/include/elf.h
```

### 2. qemu-user syscall number 应使用 a7

Linx Linux userspace syscall ABI：

```text
syscall number: a7
args:           a0..a5
trap:           acrc 1
return:         a0
```

问题：

Linx qemu-user `cpu_loop.c` 原先从 `x1` 读取 syscall number，和文档、LLVM inline asm、libc 侧 ABI 不一致。

修复：

- 在 `target/linx/cpu_user.h` 中增加 `xA7`。
- 在 `linux-user/linx/cpu_loop.c` 中用 `env->gpr[xA7]` 读取 syscall number。

修改文件：

```text
emulator/qemu/target/linx/cpu_user.h
emulator/qemu/linux-user/linx/cpu_loop.c
```

### 3. syscall 返回 PC 使用 next_bpc

背景：

Linx qemu-user 的 `acrc` translator 在 `CONFIG_USER_ONLY` 下会设置：

```text
next_bpc = ctx->pc_succ_insn
```

因此 syscall 返回后应恢复到 translator 给出的 `env->next_bpc`。

最终代码保留：

```c
env->pc = env->next_bpc;
```

修改文件：

```text
emulator/qemu/linux-user/linx/cpu_loop.c
```

### 4. acrc 必须位于 SYS block

失败现象：

程序运行时 guest 收到 `SIGILL`，QEMU log 中可见：

```text
blktype error
```

原因：

QEMU translator 对 `acrc` 有静态 block type 检查：

```text
static_blk_type_check(ctx, 1 << HEAD_TYPE_SYS)
```

普通 C/inline asm 外层由编译器生成 `C.BSTART.STD`，不能直接在这个 STD block 中执行 `acrc`。

修复：

在 C inline asm 的 syscall 模板中显式切换 block：

```asm
c.bstop
C.BSTART.SYS
c.movr  arg0, ->a0
c.movr  arg1, ->a1
c.movr  arg2, ->a2
c.movr  nr,   ->a7
acrc 1
c.bstop
C.BSTART.STD
c.movr  a0, ->ret
```

修改文件：

```text
avs/qemu/tests/lihan_qemu_user_hello.c
```

### 5. 避免当前 .rodata 寻址干扰 smoke

现象：

第一次使用字符串字面量：

```c
const char *msg = "Hello ...";
```

QEMU 确实执行到了 `write`，但输出是错误字节。反汇编显示 LLVM 通过 PC-relative 方式访问 `.rodata`，当前这条最小验证链路中该地址计算会偏移到错误位置。

修复：

为了让本次 smoke 聚焦在 qemu-user 加载、执行、syscall 闭环上，示例程序不使用 `.rodata` 字符串字面量，而是在 `_start` 中用 C 逐字节构造栈上字符串：

```c
char msg[38];
msg[0] = 'H';
...
```

这样绕开了 libc/CRT 和 `.rodata` 全局寻址依赖。

修改文件：

```text
avs/qemu/tests/lihan_qemu_user_hello.c
```

## Smoke 程序设计

示例程序的特点：

- 入口直接是 `_start`，不依赖 CRT 的 `_start`、`crt1.o`、`__libc_start_main`。
- 使用 `-nostdlib -static -Wl,-e,_start` 链接。
- 不使用 `printf`、`puts`、`strlen`、`exit` 等 libc API。
- 只使用两个 Linux syscall：`write` 和 `exit_group`。
- 输出字符串放在栈上，避免 `.rodata` 寻址问题影响 user-mode smoke。

核心路径：

```text
_start
  -> build stack message
  -> write(1, msg, 37)
  -> exit_group(0 or 1)
```

## 本次修改清单

```text
modified: emulator/qemu/linux-user/linx/target_signal.h
modified: emulator/qemu/linux-user/linx/cpu_loop.c
modified: emulator/qemu/linux-user/linx/signal.c
modified: emulator/qemu/target/linx/cpu_user.h
modified: emulator/qemu/include/elf.h
added:    emulator/qemu/linux-user/linx/target_resource.h
added:    emulator/qemu/linux-user/linx/target_prctl.h
added:    avs/qemu/tests/lihan_qemu_user_hello.c
```

## 后续优化建议

1. 把 `avs/qemu/tests/lihan_qemu_user_hello.c` 固化成 qemu-user smoke test，并给出脚本化编译/运行入口。
2. 继续检查 `.rodata`/PC-relative relocation 路径，目标是让普通字符串字面量也能稳定运行。
3. 后续接 libc 后，将当前裸 syscall smoke 升级到 `main + printf + exit` 的正常 C 程序路径。
4. 将 Linx qemu-user syscall ABI 与文档、LLVM、musl/glibc port 做一次交叉校验，避免 `a7`/`x1` 这类 drift 再出现。

---

# Glibc qemu-user Bring-Up Plan

## 任务约束

本阶段目标不再是裸 syscall smoke。新的通过标准是：

- C 程序以正常 glibc 路径构建。
- 程序入口经过 glibc/CRT 或动态加载器路径，而不是手写 `_start` 直接 syscall。
- 输出路径使用 glibc API，例如 `printf`、`puts`、`write` libc wrapper、`exit` 等。
- 运行环境使用 `emulator/qemu/build-user/qemu-linx`。
- 每次遇到失败点，先在本文档记录现象、命令、日志位置、假设，再改源码。

允许保留上一阶段裸 syscall smoke 作为底层 qemu-user 对照组，但不能把它当作本阶段完成证据。

## 分阶段计划

### Phase 0: 基线盘点

目标：

- 确认当前 `qemu-linx` 可执行。
- 确认 LLVM Linx 工具链可用。
- 盘点 glibc build/install/sysroot 产物是否存在。
- 记录当前 dirty files，避免混淆已有改动和新改动。

关键检查：

```bash
emulator/qemu/build-user/qemu-linx --version
compiler/llvm/build-linxisa-clang/bin/clang --target=linx64-unknown-linux-gnu --version
find out/libc/glibc -maxdepth 4 -type f
git status --short
```

### Phase 1: 构建 Linx glibc 产物

目标：

- 生成至少以下产物：

```text
crt1.o / Scrt1.o / crti.o / crtn.o
libc.so
ld.so.1
```

优先使用现有脚本：

```bash
lib/glibc/tools/linx/build_linx64_glibc.sh
lib/glibc/tools/linx/build_linx64_glibc_g1b.sh
```

注意：

- 当前脚本里有 macOS/Homebrew 默认路径，需要在本机用环境变量覆盖为 Linux 工具，例如 `make`、`sed`、`bison`、`readelf`。
- 如果 glibc build 失败，先记录日志和第一个失败点，再修源码或脚本。

### Phase 2: 构建最小 glibc hello

目标：

- 写一个普通 C 程序，优先使用：

```c
#include <stdio.h>

int main(void)
{
    puts("Hello from Linx glibc + qemu-usermode");
    return 0;
}
```

- 使用 LLVM 链接到 Linx glibc。
- 先让 ELF header、program headers、dynamic section 可被 `llvm-readobj` 正确识别。

预期产物：

```text
/tmp/linx-lihan-glibc-user/hello_glibc
```

### Phase 3: qemu-linx 运行 glibc 程序

目标：

- 使用 `qemu-linx` 直接运行 glibc 程序。
- 明确 dynamic loader 路径和 sysroot 布局。

候选运行方式：

```bash
emulator/qemu/build-user/qemu-linx -L <linx-sysroot> /tmp/linx-lihan-glibc-user/hello_glibc
```

或：

```bash
QEMU_LD_PREFIX=<linx-sysroot> emulator/qemu/build-user/qemu-linx /tmp/linx-lihan-glibc-user/hello_glibc
```

### Phase 4: 按失败点修复

预计可能出现的问题：

- QEMU linux-user ELF interpreter 查找失败。
- glibc dynamic loader 不认识 Linx relocation。
- TLS 初始化失败。
- `auxv` 缺关键项或值不符合 glibc 预期。
- signal/stack/clone/futex 等 syscall wrapper 缺实现。
- glibc startup `_start`、`__libc_start_main`、`exit` 路径有 ABI drift。
- `.rodata`/PC-relative relocation 问题影响普通字符串字面量。
- libc syscall inline asm 没有切入 `C.BSTART.SYS`。

处理规则：

1. 每个失败点先记录到 “实时日志”。
2. 一次只修一个最小问题。
3. 修完后立即重新运行相同命令。
4. 能通过后再推进下一层：loader -> libc init -> stdio -> exit。

### Phase 5: 固化 smoke

目标：

- 新增脚本化入口，自动完成：

```text
build glibc hello
run qemu-linx
check stdout marker
check exit code
emit summary
```

推荐位置：

```text
avs/qemu/
```

## 实时日志

### 2026-05-31: glibc qemu-user bring-up 启动

状态：

- 裸 syscall smoke 已通过，但不能作为本阶段完成证据。
- 已确认仓库中存在 Linx glibc port：`lib/glibc/sysdeps/linx/`。
- 已确认现有 `run_glibc_smoke.py` 更偏 Linux+system-QEMU 路径，本阶段需要补 qemu-user 路径。
- 下一步：盘点本机 glibc build 产物和工具依赖，然后进入 Phase 1。

### 2026-05-31: Phase 0 基线盘点

命令：

```bash
emulator/qemu/build-user/qemu-linx --version
compiler/llvm/build-linxisa-clang/bin/clang --target=linx64-unknown-linux-gnu --version
which make sed bison readelf gmake gsed || true
find out/libc/glibc -maxdepth 5 -type f
git status --short --branch
```

结果：

- `qemu-linx version 7.0.0` 可执行。
- Linx clang 可用，target 为 `linx64-unknown-linux-gnu`。
- 本机存在 `/usr/bin/make`、`/usr/bin/sed`、`/usr/bin/bison`、`/usr/bin/readelf`、`/usr/bin/gmake`。
- 未发现 `out/libc/glibc` 下已有 `crt1.o`、`Scrt1.o`、`crti.o`、`crtn.o`、`libc.so`、`ld.so.1`。
- 顶层已有改动：`emulator/qemu`、`avs/qemu/tests/lihan_qemu_user_hello.c`、`lihan readme.md`。

结论：

- 需要进入 Phase 1，从 glibc build 开始。
- glibc 脚本默认 `gmake/gsed/readelf` 指向 macOS/Homebrew 路径，本机需要用环境变量覆盖。

### 2026-05-31: Phase 1 第一次 glibc G1a configure 失败

命令：

```bash
GMAKE_BIN=/usr/bin/gmake \
GSED_BIN=/usr/bin/sed \
BISON_BIN=/usr/bin/bison \
READELF_BIN=/usr/bin/readelf \
SYSROOT=/home/touzi/linx-isa/out/libc/glibc/sysroot \
JOBS=2 \
MAKE_TARGETS=csu/subdir_lib \
bash lib/glibc/tools/linx/build_linx64_glibc.sh
```

失败日志：

```text
out/libc/glibc/logs/02-configure.log
```

失败现象：

```text
Invalid configuration `x86_64-apple-darwin6.6.87.2-microsoft-standard-WSL2': more than four components
configure: error: ... config.sub x86_64-apple-darwin6.6.87.2-microsoft-standard-WSL2 failed
```

原因判断：

- `build_linx64_glibc.sh` 中 `--build` 写死为 macOS/Homebrew 风格。
- 在当前 Linux/WSL 环境中，`uname -r` 包含额外字段，拼出的 build triple 不合法。

修复计划：

- 给脚本增加 `BUILD_TRIPLE` 环境变量。
- 默认通过 glibc 自带 `scripts/config.guess` 自动探测 build triple。
- configure 时使用 `--build="$BUILD_TRIPLE"`。

### 2026-05-31: Phase 1 build triple 修复后推进到 make

已修改：

```text
lib/glibc/tools/linx/build_linx64_glibc.sh
```

修复内容：

- 新增 `BUILD_TRIPLE` 环境变量。
- 默认值来自 `lib/glibc/scripts/config.guess`。
- configure 使用 `--build="$BUILD_TRIPLE"`。

验证结果：

- configure 已通过。
- build triple 当前为 `x86_64-pc-linux-gnu`。
- 构建推进到 `csu/subdir_lib`。

### 2026-05-31: Phase 1 第二次失败，Linux UAPI sigcontext 缺 pt_regs 定义

命令同上一轮。

失败日志：

```text
out/libc/glibc/logs/03-make.log
```

失败现象：

```text
/home/touzi/linx-isa/out/libc/glibc/linux-headers/include/asm/sigcontext.h:18:17:
error: field has incomplete type 'struct pt_regs'
        struct pt_regs sc_regs;
                        ^
```

上下文：

- glibc 正在通过 `scripts/gen-as-const.py` 生成 `rtld-sizes.h`。
- include 链路进入 `sysdeps/unix/sysv/linux/bits/sigcontext.h`，最终包含 Linux headers 的 `asm/sigcontext.h`。
- Linx UAPI `asm/sigcontext.h` 使用 `struct pt_regs`，但没有包含完整定义。

修复计划：

- 检查 `kernel/linux/arch/linx/include/uapi/asm/sigcontext.h` 和 `ptrace.h`。
- 确认后发现完整 `struct pt_regs` 只存在于非 UAPI 的 `arch/linx/include/asm/ptrace.h`，不能暴露给用户态 glibc。
- UAPI `ptrace.h` 已经提供 `struct user_regs_struct`，注释说明它用于 `core dumps, ptrace, sigcontext`。
- 因此 `sigcontext.h` 应改为 `struct user_regs_struct sc_regs;`，避免 glibc 包含用户态 header 时依赖内核私有 `pt_regs`。
- 重新执行 `headers_install` 或 glibc build 脚本，让 `out/libc/glibc/linux-headers/include/asm/sigcontext.h` 更新。

修复与验证：

- 已修改 `kernel/linux/arch/linx/include/uapi/asm/sigcontext.h`。
- 已执行：

```bash
/usr/bin/gmake -C kernel/linux ARCH=linx \
  INSTALL_HDR_PATH=/home/touzi/linx-isa/out/libc/glibc/linux-headers \
  headers_install
```

- 重新运行 `MAKE_TARGETS=csu/subdir_lib` 后通过。
- 已生成：

```text
out/libc/glibc/build/csu/crt1.o
```

结论：

- glibc 构建已越过 UAPI `sigcontext` 编译失败点。
- 下一步进入 G1b，继续构建 libc / loader 相关产物。

### 2026-05-31: Phase 1 进入 G1b libc/loader 构建

目标：

- 在已生成 `crt1.o`、`Scrt1.o`、`crti.o`、`crtn.o` 的基础上继续构建 `lib`。
- 至少拿到 `libc.so` / `libc.so.6` 或新的明确失败点。

命令：

```bash
GMAKE_BIN=/usr/bin/gmake \
GSED_BIN=/usr/bin/sed \
BISON_BIN=/usr/bin/bison \
READELF_BIN=/usr/bin/readelf \
SYSROOT=/home/touzi/linx-isa/out/libc/glibc/sysroot \
JOBS=2 \
bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh
```

结果：

- G1b 推进到 `elf/ld.so` 链接阶段后失败。
- 失败日志：

```text
out/libc/glibc/logs/03-make.log
```

关键错误：

```text
ld.lld: error: ... librtld.os:(function __minimal_malloc: .text+0xa1e4):
R_LINX_LO12 relocation points to unsupported anchor section '.bss' for symbol '_end'

ld.lld: error: ... librtld.os:(function _dl_start: .text+0x15f0c):
R_LINX_LO12 relocation points to unsupported anchor section '' for symbol '__ehdr_start'
```

原因判断：

- 这些失败来自 LLD 的 Linx `R_LINX_PCREL_HI20` / `R_LINX_LO12` 配对恢复逻辑。
- `librtld.os` 里 `_end`、`__ehdr_start` 的 LO12 relocation 指向最终链接符号；这些符号由 linker 脚本/输出文件提供，不是普通 input section symbol。
- 当前 LLD 看到 `Defined` 符号不属于 `InputSection` / `MergeInputSection` / `EhInputSection` 时直接报错，来不及走“按同一符号向前查找配对 HI20 relocation”的兜底路径。
- 实际上同一个 input section 内存在相邻的 `R_LINX_PCREL_HI20 _end` / `R_LINX_LO12 _end` 和 `R_LINX_PCREL_HI20 __ehdr_start` / `R_LINX_LO12 __ehdr_start` 配对。

修复计划：

- 修改 `compiler/llvm/lld/ELF/InputSection.cpp` 的 Linx LO12 配对逻辑。
- 对非 input-section 的 linker-defined/output-section 符号，不立即报错。
- 先尝试 `findLinxPCRelHiBySymbol(loSec, loOffset, sym)` 回溯同一 section 中的 HI20。
- 只有既不能映射到 input section，又找不到同符号 HI20 时才报错。
- 重建 `ld.lld`，再重新运行 G1b。

修复与验证准备：

- 已修改：

```text
compiler/llvm/lld/ELF/InputSection.cpp
```

- 具体策略：遇到 linker-defined/output-section 符号时先延迟错误，允许后续 `findLinxPCRelHiBySymbol` 按同一符号向前找到配对的 `R_LINX_PCREL_HI20`。
- 已重建 LLD：

```bash
cmake --build compiler/llvm/build-linxisa-clang --target lld -- -j2
```

- `compiler/llvm/build-linxisa-clang/bin/ld.lld` 是指向 `lld` 的 symlink，已使用新构建产物。

重新运行 G1b：

```bash
GMAKE_BIN=/usr/bin/gmake \
GSED_BIN=/usr/bin/sed \
BISON_BIN=/usr/bin/bison \
READELF_BIN=/usr/bin/readelf \
SYSROOT=/home/touzi/linx-isa/out/libc/glibc/sysroot \
JOBS=2 \
bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh
```

结果：

```text
[G1b] status: pass
[G1b] classification: shared_libc_so_built
[G1b] artifact: /home/touzi/linx-isa/out/libc/glibc/build/linkobj/libc.so
```

当前 glibc 产物：

```text
out/libc/glibc/build/csu/crt1.o
out/libc/glibc/build/csu/Scrt1.o
out/libc/glibc/build/csu/crti.o
out/libc/glibc/build/csu/crtn.o
out/libc/glibc/build/libc.so
out/libc/glibc/build/linkobj/libc.so
out/libc/glibc/build/elf/ld.so
out/libc/glibc/build/libc_nonshared.a
```

结论：

- Phase 1 已经从 CRT 推进到 shared libc / dynamic loader build。
- 下一步不使用现有 `qemu-system` initramfs smoke 作为本阶段完成证据，而是补 `qemu-linx` user-mode 路径：构造最小 sysroot、链接带 `/lib/ld.so.1` interpreter 的 glibc 程序，并用 `qemu-linx -L <sysroot>` 运行。

### 2026-05-31: Phase 2 准备普通 glibc hello

目标程序形态：

```c
#include <stdio.h>

int main(void)
{
    puts("Hello from Linx glibc + qemu-user");
    return 0;
}
```

处理顺序：

1. 先尝试把 glibc headers 安装到本地 sysroot，使 hello 能使用正常 `<stdio.h>`。
2. 准备 qemu-user sysroot 中的 `/lib/ld.so.1` 和 `/lib/libc.so.6`。
3. 使用 `crt1.o` / `crti.o` / `crtn.o` 和 `libc.so` 链接动态 glibc 程序。
4. 使用 `emulator/qemu/build-user/qemu-linx -L <sysroot>` 运行。

headers 安装命令：

```bash
PATH=/home/touzi/linx-isa/out/libc/glibc/build/.host-tools:/usr/bin:$PATH \
/usr/bin/gmake -C out/libc/glibc/build \
  install_root=/home/touzi/linx-isa/out/libc/glibc/sysroot \
  install-headers
```

结果：

- `install-headers` 通过。
- `out/libc/glibc/sysroot/usr/include/stdio.h` 已生成。

下一步源码：

- 新增 `avs/qemu/tests/lihan_glibc_puts.c`。
- 程序使用 `#include <stdio.h>` 和 `puts`，入口是普通 `main`。
- 不手写 `_start`，不直接发 Linx Linux syscall ABI。

sysroot 准备：

```bash
mkdir -p out/libc/glibc/sysroot/lib out/libc/glibc/sysroot/usr/lib
cp -f out/libc/glibc/build/elf/ld.so out/libc/glibc/sysroot/lib/ld.so.1
cp -f out/libc/glibc/build/libc.so out/libc/glibc/sysroot/lib/libc.so.6
ln -sf libc.so.6 out/libc/glibc/sysroot/lib/libc.so
cp -f out/libc/glibc/build/csu/{crt1.o,Scrt1.o,crti.o,crtn.o} out/libc/glibc/sysroot/usr/lib/
cp -f out/libc/glibc/build/libc_nonshared.a out/libc/glibc/sysroot/usr/lib/
cp -f out/libc/glibc/fallback-libs/{libgcc.a,libgcc_eh.a,crtbeginS.o,crtendS.o} out/libc/glibc/sysroot/usr/lib/
```

第一次编译失败：

```text
out/libc/glibc/sysroot/usr/include/features.h:564:10:
fatal error: 'gnu/stubs.h' file not found
```

原因判断：

- `install-headers` 安装了公开头文件，但当前 bring-up 没有执行完整 `make install`。
- glibc 的 installed `<features.h>` 总会包含 `<gnu/stubs.h>`。
- 当前 Linx glibc build 已经可以构建 libc/ld.so，但还没有生成 installed `gnu/stubs.h`。

修复计划：

- 在 sysroot 中补一个最小 `usr/include/gnu/stubs.h`。
- 该文件只用于让外部 hello 程序通过公开 glibc headers 编译；不声明任何 `__stub_*`，表示本轮不额外标记 syscall stub。
- 后续完整 install 路径接好后，应由 glibc install 规则生成该文件。

修复与编译结果：

- 已补：

```text
out/libc/glibc/sysroot/usr/include/gnu/stubs.h
```

- 重新编译通过，产物：

```text
/tmp/linx-lihan-glibc-user/lihan_glibc_puts
```

- ELF 形态：

```text
Type: PIE / ET_DYN
Interpreter: /lib/ld.so.1
NEEDED: libc.so.6
RUNPATH: /lib
Entry: glibc crt1.o 提供的 _start
```

运行命令：

```bash
emulator/qemu/build-user/qemu-linx \
  -L /home/touzi/linx-isa/out/libc/glibc/sysroot \
  /tmp/linx-lihan-glibc-user/lihan_glibc_puts
```

第一次 qemu-user 运行失败：

```text
--- SIGSEGV {si_signo=SIGSEGV, si_code=1, si_addr=0x0000004002882fa2} ---
```

定位：

- `-singlestep -d cpu,in_asm,guest_errors` 显示崩溃发生在 dynamic loader `_dl_start` 的第一条 `hl.sd.pcr`。
- 反汇编中的目标地址：

```text
0x00000040028224f2: hl.sd.pcr t#1[0x400282e648]
```

- 实际 fault 地址：

```text
0x0000004002882fa2
```

原因判断：

- `hl.sd.pcr` 是 48-bit PC-relative store。
- QEMU `trans_block_48.c.inc` 的 `trans_blk_sd_pcr_48` 把 pcr store immediate 又按访问宽度左移。
- `sd` 将 `0xc156` 错误扩大为 `0xc156 << 3 = 0x60ab0`，因此访问到错误地址。
- pcr relocation/linker 已经给出字节偏移，load pcr 也使用 unscaled；store pcr 应同样 unscaled。

修复计划：

- 修改 `emulator/qemu/target/linx/insn_trans/trans_block_48.c.inc`。
- `blk_{sb,sh,sw,sd}_pcr_48` 全部使用 `UNSCALED`，避免按元素宽度再次缩放。
- 重建 `qemu-linx` 后重新运行同一个 glibc hello。

修复与重建：

- 已修改：

```text
emulator/qemu/target/linx/insn_trans/trans_block_48.c.inc
```

- 已执行：

```bash
make -C emulator/qemu/build-user -j2
```

- `qemu-linx` 已重新链接。

PCR 修复后的下一次运行结果：

```bash
timeout 20s emulator/qemu/build-user/qemu-linx \
  -L /home/touzi/linx-isa/out/libc/glibc/sysroot \
  /tmp/linx-lihan-glibc-user/lihan_glibc_puts
```

失败信息：

```text
error SrcRType:3 in INSTR_TYPE_AU_LD_ST
ERROR:../target/linx/translate.c:782:conver_src_value: code should not be reached
```

定位：

- `-singlestep -d cpu,in_asm,guest_errors` 显示 dynamic loader 已经越过 `_dl_start` 开头的 PCR store。
- 后续进入普通 block load/store / compare / setc 路径时，QEMU 翻译器在 `conver_src_value()` 中遇到 `SrcRType == 3`。
- `emulator/qemu/target/linx/cpu_bits.h` 中 `AU_NEG == 3`，并且同文件对 `INSTR_TYPE_CMP_SETC_LD_ST` 的注释已经提示 load/store 类型要处理 `AU_NEG` 例外。
- 当前 `conver_src_value()` 只在 `INSTR_TYPE_AU` 分支处理 `AU_NEG`，没有在 `INSTR_TYPE_CMP_SETC_LD_ST` 分支处理，所以 glibc loader 触发了 QEMU 自身断言。

修复计划：

- 修改 `emulator/qemu/target/linx/translate.c`。
- 在 `INSTR_TYPE_CMP_SETC_LD_ST` 分支中补 `AU_NEG`，语义与 arithmetic 分支一致，生成 `tcg_gen_neg_tl(t, SrcReg)`。
- 重建 `qemu-linx` 后继续运行同一个 glibc hello。

修复与重建：

- 已修改：

```text
emulator/qemu/target/linx/translate.c
```

- 在 `INSTR_TYPE_CMP_SETC_LD_ST` 路径补充 `AU_NEG`，避免 dynamic loader 中 block load/store 地址计算触发 QEMU 断言。
- 已执行：

```bash
make -C emulator/qemu/build-user -j2
```

重新运行结果：

```text
timeout: the monitored command dumped core
```

现象变化：

- 不再出现 `error SrcRType:3 in INSTR_TYPE_AU_LD_ST`。
- 运行继续推进，但 host 侧 `qemu-linx` 自身发生 SIGSEGV。

下一步定位计划：

- 使用 gdb 运行 `qemu-linx -L <sysroot> lihan_glibc_puts` 并抓 host backtrace。
- 同时保留 QEMU `-d cpu,in_asm,guest_errors` 日志，确认崩溃前最后一个 guest basic block。
- 在确认 host crash 位置后，再记录具体修复方案并修改源码。

进一步定位：

- gdb 显示普通运行时 host SIGSEGV 发生在 TCG code buffer 内，guest PC 对应 `_dl_start + 0xac`，也就是 `0x400282258e` 附近的 store block。
- 非单步 QEMU 日志显示，在第二次执行：

```text
0x000000400282253a: BSTART COND, next:400282258e
0x000000400282253c: setc.ltu a6, a1.N/A
```

时，`a6` 已经是从字符串表读出的 64-bit 数据，不应该满足 `a6 < 38`。
- 由于上一轮把 `SrcRType=3` 在整个 `INSTR_TYPE_CMP_SETC_LD_ST` 路径中当作 `.neg`，`setc.ltu a6, a1` 被错误翻译成 `a6 < -a1`，条件恒偏真，导致 dynamic loader 走错分支。
- 走错分支后，后续 block 用巨大的 `a6` 计算 store 地址，最终 host 侧 JIT store 写到非法地址并 SIGSEGV。

更正依据：

- `isa/v0.56/semantics_conventions.json` 规定：`CMP.{EQ,NE,LT,GE,LTU,GEU}` 和 `SETC.{EQ,NE,LT,GE,LTU,GEU}` 这类语法只允许 `{.sw,.uw}` 的形式，`SrcRType=11` 在 strict v0.56 中按 `00` 处理。
- `isa/sail/model/execute/execute.sail` 的 `sanitize_srcrtype_swuw()` 也实现了同样规则。
- load/store 地址计算仍使用 arithmetic SrcRType，`11` 对应 `.neg`。

修复计划：

- 不再把 compare/setc 和 load/store 混在同一个转换语义里。
- 在 QEMU 中新增一个 compare/setc 专用源操作数类型。
- `CMP/SETC` 路径：`SrcRType=3` 先 sanitize 为 `AU_NONE`。
- load/store 路径：继续支持 `AU_NEG`，用于地址偏移的负值形式。
- 顺手把 QEMU disassembler 的 compare/setc `SrcRType=3` 显示从 `.N/A` 改为空后缀，避免后续日志误导。

修复与重建：

- 已修改：

```text
emulator/qemu/target/linx/cpu_bits.h
emulator/qemu/target/linx/translate.c
emulator/qemu/target/linx/insn_trans/trans_block_32.c.inc
emulator/qemu/target/linx/disas.c
```

- `CMP/SETC` 使用新的 `INSTR_TYPE_CMP_SETC_SWUW`。
- `SrcRType=3` 在 compare/setc 路径按 `AU_NONE` 处理。
- load/store 路径仍保留 `AU_NEG`。
- 已重建 `qemu-linx`，第二次重建已消除宏重定义 warning。

新的运行结果：

- `setc.ltu a6, a1` 的 QEMU 日志不再显示 `.N/A`。
- 第二次循环中 `a6` 很大时，`setc.ltu` 正确落到 fall-through 分支，说明 compare/setc 的 `SrcRType=3` 语义已经修正。
- 但程序仍在后续 `sdi a3, [t#1, 64]` 处 host SIGSEGV。

进一步定位：

- 这次不是分支条件错误，而是 `_dl_start` 扫描 dynamic section 的基址已经错了。
- `ld.so.1` 的 `.dynamic` 虚拟地址是：

```text
0x278d8
```

- 当前运行时 `addtpc 10; addi t#1, 0 -> a3` 得到的地址偏移是：

```text
0x27522
```

- `0x27522` 落在 `.data.rel.ro` 的 tunables 字符串附近，例如 `glibc.rtld.enable_secure`。
- 后续 `ldi [a3, 16]` 读到字符串字节 `0x646c74722e636269`，而不是 dynamic tag，因此 loader 后面仍然走到非法地址计算。

根因判断：

- Linx 的 `ADDTPC + ADDI` 地址材料化需要：

```text
ADDTPC: page-relative high part
ADDI:   low 12-bit correction for full PC-relative delta
```

- 当前 LLD 的 `RE_LINX_PC_INDIRECT` 给 `R_LINX_LO12` 返回的是 paired HI20 的 page delta。
- 对 `_DYNAMIC` 这类目标，page delta 为 `0xa000`，低 12 位是 `0`，所以 ADDI 被错误写成 `0`。
- 正确的 LO12 应来自完整 PC-relative delta：

```text
S - P = 0x278d8 - 0x1d522 = 0xa3b6
LO12 = 0x3b6
```

修复计划：

- 修改 `compiler/llvm/lld/ELF/InputSection.cpp` 的 `RE_LINX_PC_INDIRECT` 计算。
- 找到 paired `R_LINX_PCREL_HI20` 后，用 HI relocation 的 symbol/addend 和 HI place 计算完整 `S + A - P`。
- `R_LINX_LO12` 继续由 `encodeLo12()` 取低 12 位。
- 重建 LLD，重新运行 glibc G1b 以生成修正后的 `ld.so` / `libc.so`，再更新 sysroot 并重跑 qemu-user glibc hello。

修复与验证：

- 已修改：

```text
compiler/llvm/lld/ELF/InputSection.cpp
```

- 已重建 LLD：

```bash
cmake --build compiler/llvm/build-linxisa-clang --target lld -- -j2
```

- 已重新运行 G1b，状态通过。
- 重新链接后的 `_dl_start` 已从：

```text
addtpc 10, ->t
addi   t#1, 0, ->a3
```

变为：

```text
addtpc 10, ->t
addi   t#1, 950, ->a3
```

- 这使 `a3` 正确指向运行时 `.dynamic` 地址 `0x400282c8d8`。

更新 sysroot 后的新运行结果：

- dynamic loader 已经开始正确遍历 `.dynamic`。
- 普通 tag `0xe`、`0x7`、`0x8`、`0x9` 等都能进入 `0x1d58e` 的表项保存路径。
- 新崩溃出现在处理 OS/GNU 扩展 dynamic tag，例如 `0x6ffffef5` 时。

进一步定位：

- 日志显示 QEMU 把 `llvm-objdump` 反汇编为：

```text
subw a4, x0, ->t
```

的指令解释成：

```text
subw a4, x0.neg, ->t
```

- 当前 LLVM 后端/反汇编器的 SrcRType 编码实际是：

```text
0 = .sw
1 = .uw
2 = .neg / .not
3 = none
```

- QEMU 旧定义仍是：

```text
0 = none
1 = .sw
2 = .uw
3 = .neg / .not
```

- 这导致 arithmetic、logic、load/store、compare/setc 中所有 SrcRType 解释都有潜在错位；此前 `SETC SrcRType=3` 只是第一个暴露点。

修复计划：

- 本轮 bring-up 先让 QEMU 对齐当前本地 LLVM 生成的二进制编码。
- 修改 `emulator/qemu/target/linx/cpu_bits.h` 中 SrcRType 常量：

```text
AU_SW / REG_EXT_SW = 0
AU_UW / REG_EXT_UW = 1
AU_NEG / REG_EXT_NOT = 2
AU_NONE / REG_EXT_NONE = 3
```

- 同步更新 QEMU disassembler 的 suffix 表，避免日志继续误导。
- 保留 `CMP/SETC` 对 `.neg/.not` 编码的 sanitize：对这类只允许 `.sw/.uw` 的形式，raw `2` 和 raw `3` 都不做 negate。

#### 当前新卡点：GNU dynamic tag 索引计算仍异常

在 SrcRType 编码表修复后，`subw a4, x0, ->t` 已不再被 QEMU 错译成 `subw a4, x0.neg, ->t`，但 glibc loader 仍在 `_dl_start` 的 dynamic tag 表项保存阶段崩溃。

现象：

- 处理 GNU/OS 扩展 dynamic tag `DT_GNU_HASH = 0x6ffffef5` 时，guest 代码会进入 `0x1d55c..0x1d58a` 的 tag 分类/归一化路径。
- 运行日志显示该路径之后 `a6` 变成：

```text
0x0000000010000140
```

- 下一段代码执行：

```text
slli a6, 3, ->u
addtpc 49152, ->t
addi t#1, 164, ->t
c.add t#1, u#1, ->t
sdi a3, [t#1, 64]
```

- 因为 `a6 << 3` 极大，QEMU 最终在 host JIT 代码中尝试写入无效 guest 地址，触发 host SIGSEGV。

初步判断：

- glibc 这里期望把 `DT_GNU_HASH` 归一化成一个很小的 dynamic-vector 索引，而不是 `0x10000140`。
- 可疑点集中在 QEMU 对 Linx word shift/word arithmetic 的翻译语义：

```text
slliw
sraiw
sll
srl
32-bit 结果的 sign/zero extension
```

下一步计划：

- 对照 `isa/sail/model/execute/execute.sail` 中 `exec_slliw/exec_sraiw/exec_sll/exec_srl` 的语义。
- 检查 QEMU `emulator/qemu/target/linx/insn_trans/trans_block_32.c.inc` 里对应 translator 是否正确截断到 32 位、是否按规范做 sign/zero extend。
- 修复前继续把每个可复现 bug 和修复点记录在本文件中。

进一步定位结果：

- word shift 本身在当前输入上没有直接算错；`slliw a6, 1` 和 `sraiw t#1, 1` 产生的中间值符合 Sail 对低 32 位的处理。
- 真正让 extra-tag 检查失败的是 `HL.LUI` 常量材料化。
- glibc 为 `DT_EXTRATAGIDX` 检查生成了如下常量路径：

```text
hl.lui -3, ->t
sll    t#1, a2, ->t
srl    t#1, a2, ->u
```

- 这里 `a2 = 32`，期望 `hl.lui -3` 先得到 `0xfffffffffffffffd`，再通过 `sll/srl` 得到 32 位无符号上界 `0x00000000fffffffd`。
- QEMU 当前 `trans_blk_lui_48()` 实现为：

```text
imm32 << 32
```

- 因此 `hl.lui -3` 变成 `0xfffffffd00000000`，后续再左移 32 位被移成 `0`，导致 `u#1 = 0`。
- `setc.ltu t#1, u#1` 因此没有跳到下一类 tag，错误落入 `DT_EXTRATAGIDX` 的索引计算，得到 `0x10000140`。

规范依据：

- `isa/v0.56/semantics_conventions.json` 明确写明：

```text
HL.LUI: Write(RegDst, SignExtend(imm32))
No <<12 in HL.LUI.
```

- `isa/sail/model/execute/execute.sail` 中 `exec_hl_lui()` 同样是 `sext32_from32(imm32)`。

修复计划：

- 修改 `emulator/qemu/target/linx/insn_trans/trans_block_48.c.inc` 的 `trans_blk_lui_48()`。
- 将旧的 `((uint64_t)a->imm << 32)` 改成 32 位 sign-extend。
- 重建 QEMU 后重新运行 glibc hello，观察 `DT_GNU_HASH` 是否映射到 `ADDRIDX(DT_GNU_HASH) = 79` 附近，而不是 `0x10000140`。

修复与验证：

- 已修改 `trans_blk_lui_48()` 为 `SignExtend(imm32)`。
- 已重建 QEMU。
- 重新运行后，`DT_GNU_HASH = 0x6ffffef5` 已正确映射为：

```text
a6 = 0x4f
```

- `0x4f == 79 == ADDRIDX(DT_GNU_HASH)`，说明 dynamic tag 分类阶段已越过。

#### 当前新卡点：CSEL 选择方向与 LLVM 发码不一致

新的崩溃发生在 dynamic loader 自身 relocation 的 `DT_RELR` 处理阶段。

现象：

- RELR 表的正确运行时地址为：

```text
0x4002806a20
```

- 当前运行中，在进入 RELR 迭代前被算成：

```text
0x800500ca20
```

- 随后执行：

```text
ldi [a3, 0], ->a7
```

从这个非法地址读取，触发 host SIGSEGV。

定位：

- `D_PTR(map, l_info[DT_RELR])` 的逻辑是：

```text
d_ptr + (dl_relocate_ld(map) ? 0 : map->l_addr)
```

- 本轮 bootstrap 中前面已经执行过 `ADJUST_DYN_INFO(DT_RELR)`，`d_ptr` 已经是 `0x4002806a20`。
- 因此这里 `dl_relocate_ld(map)` 为真时应选择 `0` 作为附加值。
- LLVM 后端在 `compiler/llvm/llvm/lib/Target/LinxISA/LinxISAMCInstLower.cpp` 中明确按如下语义发码：

```text
CSEL: predicate != 0 ? SrcR : SrcL
```

- 因此 `csel t#1, u#1, a0, ->a4` 在 predicate 为真时应选择 `a0 == 0`。
- QEMU 当前 `trans_blk_csel_32()` 实现为：

```text
predicate != 0 ? SrcL : SrcR
```

- 这导致它错误选择 `u#1 == map->l_addr`，把已调整的 RELR 表地址再次加上 load base。

修复计划：

- 修改 QEMU scalar `CSEL` 为当前 LLVM 发码约定：

```text
predicate != 0 ? SrcR : SrcL
```

- 同步修正 SIMT `V.CSEL` 翻译，避免后续同类语义分叉。
- 重建 QEMU 后重新验证 RELR 表地址不再重复加 base。

修复与验证：

- 已修改：

```text
emulator/qemu/target/linx/insn_trans/trans_block_32.c.inc
emulator/qemu/target/linx/insn_trans/trans_block_32_private_fvec.c.inc
```

- scalar `CSEL` 和 SIMT `V.CSEL` 均改为：

```text
predicate != 0 ? SrcR : SrcL
```

- 已重建 QEMU。
- 重新运行后，`DT_RELR` 路径不再把已调整的 RELR 表地址二次加上 `map->l_addr`。
- RELR 表指针保持为：

```text
0x4002806a20
```

#### 当前新卡点：负向 PC-relative 地址材料化高一页

新的崩溃仍发生在 `_dl_start` 的 RELR relocation 处理阶段，但性质已经变化。

现象：

- `a3` 进入 RELR 迭代时是：

```text
0x4002806a20
```

- 这个地址按当前 loader 计算路径看起来像 `.relr.dyn`，但执行：

```text
ldi [a3, 0], ->a7
```

读出的首项却是：

```text
0x6620736920736968
```

- 该值是 `.rodata` 中的 ASCII-like 数据，而不是 `.relr.dyn` 的首项。
- 文件中 `.relr.dyn` 的首项实际为：

```text
0x0000000000027858
```

进一步定位：

- `ld.so.1` 中 `_DYNAMIC` 虚拟地址：

```text
0x278d8
```

- 运行时 `_DYNAMIC` 地址：

```text
0x400282c8d8
```

- 因此真实 load bias 应为：

```text
0x4002805000
```

- 但 `elf_machine_load_address()` 通过 `__ehdr_start` 的 `ADDTPC + ADDI` 材料化得到：

```text
0x4002806000
```

- 差值正好是 `+0x1000`。

可疑根因：

- 当前 LLD 对 Linx `R_LINX_PCREL_HI20` 使用 page delta，对 `R_LINX_LO12` 使用完整 delta 的低 12 位。
- 但 Linx `ADDI` 低 12 位是 `uimm12`，不是 signed imm12。
- 对负向 PC-relative delta，例如：

```text
addtpc -118784, ->t
addi   t#1, 2198, ->u
```

低 12 位 `0x896` 被 `ADDI` 当作 `+2198` 加上，因此 high part 必须扣掉额外一页。
- 当前 high part 没有针对 unsigned LO12 做补偿，导致 `__ehdr_start` 计算高一页。

修复计划：

- 修改 `compiler/llvm/lld/ELF/Arch/LinxISA.cpp`。
- `R_LINX_PCREL_HI20` / `R_LINX_GOT_HI20` 的 high part 不再直接使用 `page(S+A)-page(P)`。
- 改为根据完整 delta 计算：

```text
hi = floor((S + A - P) / 4096)
lo = (S + A - P) & 0xfff
ADDTPC(hi) + ADDI(lo) == S + A - P
```

- 这样负向 delta 且低 12 位非零时，high part 会自动比 trunc/page 算法少一页。
- 重建 LLD 后重新运行 G1b，更新 sysroot，再用同一个 glibc hello 复测。

修复与验证：

- 已修改：

```text
compiler/llvm/lld/ELF/Arch/LinxISA.cpp
```

- `R_LINX_PCREL_HI20` 改为 `R_PC`，`R_LINX_GOT_HI20` 改为 `R_GOT_PC`。
- `encodePcrelHi20()` 改为从完整 `S + A - P` 中扣掉 unsigned LO12 后再编码 high part：

```text
lo = delta & 0xfff
hi = (delta - lo) >> 12
```

- 已重建 LLD，重新运行 G1b，并更新 sysroot。
- 重新反汇编可见 RELR 写回路径的 high part 已从旧的 `0xffffe3` 类值变成少一页的形式，例如：

```text
addtpc 1048546, ->t
addi   t#1, 2142, ->u
```

- 新 QEMU 日志中 `UR1..UR4` 的 loader load bias 已稳定为：

```text
0x4002805000
```

结论：

- `__ehdr_start` 高一页的问题已修复。
- 程序继续推进到 `.rela.dyn` / audit 初始化附近。

#### 当前新卡点：QEMU 48-bit load-pair 译码仍按旧 LDI.PO 语义

新的失败现象：

- 程序不再在 RELR 首项读取处崩溃。
- 继续运行后，QEMU host 侧以 `SIGILL` 退出。
- 最后可见 guest 已进入 `_dl_start` 更后面的 relocation/audit 路径。

关键日志：

```text
0x400282293c: ...
0x4002822960: hl.ldi.po [s5, 0], ->s6, s8
...
s5 = 0x4002803970
s6 = 0x4002805a08
s8 = 0x4002803970
```

但 LLVM 反汇编同一位置实际是当前 ISA 的：

```text
0x1d960: hl.ldip [s5, 0], ->s6, s8
```

期望语义：

- `HL.LDIP [SrcL, simm]` 是 load pair。
- 对 64-bit `LDIP`：

```text
ea  = SrcL + (simm << 3)
Dst0 = *(uint64_t *)ea
Dst1 = *(uint64_t *)(ea + 8)
```

- 因此这里应得到：

```text
s6 = 0x4002805a08   # RELA start
s8 = 0x18           # RELASZ
```

实际 QEMU 行为：

- QEMU 旧 `block48.decode` 把当前编码 `bits[5:4] = 01` 的 `HL.LDIP` 落到了旧的 `HL.LDI.PO` 路径。
- `trans_blk_ldi_po_48()` 当前按 “load + post-index address result” 处理，第二个结果写成地址 `s5` 自身。
- 后续执行：

```text
add s8, s6, ->s6
```

把 `RELA start + stack address` 相加，得到类似：

```text
0x8005009378
```

导致 relocation loop 读越界，最终进入错误路径。

修复计划：

- 先按当前 glibc 暴露的最小问题修复 QEMU 48-bit immediate load-pair 路径。
- 修改 `emulator/qemu/target/linx/insn_trans/trans_block_48.c.inc`。
- 将当前会匹配 `HL.{LBIP,LHIP,LWIP,LDIP,...}` 的 `*_po_48` immediate load translator 改为 load-pair 语义：

```text
addr0 = SrcL + scaled(simm)
addr1 = addr0 + element_size
Dst0 = load(addr0)
Dst1 = load(addr1)
```

- 先覆盖 `LDIP` / `LWIP` / half/byte pair 的通用 helper，重建 QEMU 后复测。
- 后续还需要系统性整理 QEMU `block48.decode` 中 current v0.56 的 `LDI` / `LDIP` / `LDI.PR` / `LDI.PO` 命名和语义，避免靠旧名字承载新语义。

修复与验证：

- 已修改：

```text
emulator/qemu/target/linx/insn_trans/trans_block_48.c.inc
```

- 将当前匹配 `bits[5:4] = 01` 的 48-bit load helper 改成 load-pair：

```text
Dst0 = load(ea)
Dst1 = load(ea + element_size)
```

- 已重建 QEMU。
- 重新运行后，程序明显越过前一处 `.rela.dyn` end pointer 错误，继续进入：

```text
_dl_sysdep_start
memset
```

结论：

- `HL.LDIP` 被当成旧 `HL.LDI.PO` 的问题已修复到足以越过当前 relocation/audit 路径。
- 这也确认前一轮 `RELA start + stack address` 造成的巨大 end pointer 不再是当前阻塞点。

#### 当前新卡点：memset 中仍有一处 32/48-bit 译码分歧触发 SIGILL

新的失败现象：

```text
--- SIGILL {si_signo=SIGILL, si_code=1, si_addr=NULL} ---
```

关键推进点：

- 已经进入 `_dl_sysdep_start`。
- 已调用 loader 内部 `memset`：

```text
0x4002828fd4: memset
```

当前日志线索：

```text
Disassembler disagrees with translator over instruction decoding
```

发生区域：

```text
0x23fd4 <memset>
0x23fe4: hl.lui 1, ->t
0x23fea: sll t#1, a3, ->u
0x23fee: srl u#1, a3, ->t
0x23ff2: or u#1, t#1, ->a5
0x23ffa: hl.lui 16843009, ->t
0x24000: mulw u#1, t#1, ->t
...
```

判断：

- 现在不再是 loader dynamic section / RELR / RELA 指针错误。
- 当前问题更像 QEMU 的 disassembler/translator 对 current LLVM 生成的混合 16/32/48-bit 指令流仍存在长度或译码漂移。
- `memset` 暴露的是更普通的 libc 代码路径，说明 glibc bring-up 已推进到 libc 内部函数级别。

下一步计划：

- 以 `memset` 的 `0x23fd4..0x24030` 为最小复现窗口。
- 对照 `llvm-objdump` 和 QEMU `block32/block48.decode`，确认到底是哪一条指令触发 `gen_exception_illegal()`。
- 优先检查：

```text
HL.LUI 后续 PC 步进
32-bit SLL/SRL/OR/MULW 的译码
C.BSTART.STD 与 conditional block 交界
```

- 继续按“先记录，再改源码”的方式修复。

#### 当前修复目标：16-bit offset conditional header 在 TB 切分后丢失条件块状态

新的最小定位：

```text
0x4002828fde: C.BSTART COND, 0x400282903a
...
0x4002829000: mulw u#1, t#1, ->t
...
0x4002829012: c.setc.eq t#1, a4
```

TCG `op` 日志确认 `SIGILL` 不是 `c.setc.eq` 编码非法，而是 QEMU 在翻译这条指令时主动插入了异常：

```text
---- 0000004002829012
st_i32 $0x10,env,$0xd8
mov_i64 pc,$0x4002829012
call raise_exception,$0x8,$0,env,$0x3
```

根因判断：

- `0x8fde` 的 16-bit `BSTART COND` 使用 `trans_blk_offset_cond()`。
- 当前实现先建立 `BRANCH_CONDITIONAL` 状态，但随后又把运行时 `header_info` / `carg_tgt` 恢复成进入该 header 之前的旧状态。
- 这个块在 `hl.lui` 后发生 TB 切分，下一段从 `0x9000` 继续翻译时会重新从 `env->header_info` 初始化 `ctx->brh_type`。
- 因为运行时状态已被恢复成旧的 `FENTRY/FALL`，所以 `0x9012 c.setc.eq` 被误判为“不在 conditional block 中使用 setc”，触发 `gen_exception_illegal()`。

修复计划：

- 修改 `emulator/qemu/target/linx/insn_trans/trans_block_header.c.inc`。
- 让 16-bit offset conditional/call header 像普通 block header 一样，把当前 header 状态保留到运行时环境中，直到该 block commit。
- 先移除 `trans_blk_offset_cond()` / `trans_blk_offset_direct_call()` 中恢复旧 `header_info` / `carg_tgt` 的逻辑。
- 重建 QEMU 后复测 glibc `puts` 程序是否越过 `memset`。

修复与验证：

- 已修改：

```text
emulator/qemu/target/linx/insn_trans/trans_block_header.c.inc
```

- 移除 16-bit offset conditional/call header 中恢复旧 `header_info` / `carg_tgt` 的逻辑。
- 已重建 QEMU。
- 复测结果：程序已越过 `memset`，继续进入：

```text
__GI___tunables_init
_dl_sort_maps_init
__GI___tunable_get_val
__brk
```

结论：

- `memset` 中 `0x9012 c.setc.eq` 的误 SIGILL 已修复。
- 当前阻塞点已推进到 glibc syscall wrapper。

#### 当前修复目标：glibc Linx syscall 模板未切入 SYS block 就执行 acrc

新的失败位置：

```text
0000000000021ca4 <brk>:
   21ca4: FENTRY [ra ~ ra], sp!, 8
   21ca8: C.BSTART COND, 0x21cd2
   21caa: c.movr a0, ->t
   21cac: addi zero, 214, ->a7
   21cb0: acrc
   21cb4: C.BSTOP
```

QEMU 日志：

```text
acrc do not in the fall block.
```

根因判断：

- `lib/glibc/sysdeps/unix/sysv/linux/linx/sysdep.h` 的 C 侧 `__SYSCALL_INSN` 当前直接发：

```text
acrc 1
c.bstop
C.BSTART
```

- 因此 `acrc` 会落在编译器当前所在的普通 block 或 conditional block 中。
- QEMU/ISA 文档要求 `ACRC` 属于 system request 路径，之前可工作的裸 syscall 也显式使用：

```text
C.BSTART.SYS
acrc 1
c.bstop
C.BSTART.STD
```

修复计划：

- 修改 `lib/glibc/sysdeps/unix/sysv/linux/linx/sysdep.h`。
- C 侧 `__SYSCALL_INSN` 在 `acrc 1` 前先用 `c.bstop` 结束当前 block，再进入 `C.BSTART.SYS`。
- `acrc 1` 后保留显式 `c.bstop`，再回到 `C.BSTART.STD`。
- 同步调整 assembler 侧 `PSEUDO` / `PSEUDO_NOERRNO`，避免汇编 syscall wrapper 也把 `acrc` 放在 STD block。
- 重建 glibc G1b，刷新 sysroot 中的 `ld.so.1` / `libc.so.6` / CRT 文件后复测。

修复尝试与新发现：

- 已按上面计划修改 glibc syscall 模板并重建 G1b。
- 新 `brk` 片段确实变成：

```text
21ce6: C.BSTART.SYS
21ce8: acrc
21cec: C.BSTOP
21cee: C.BSTART.STD
21cf0: setc.geu a0, t#1
```

- QEMU 已经能执行 `acrc SCT_SYS`，并返回 `brk` syscall 结果。
- 但新的 SIGILL 出现在 syscall 返回后的：

```text
21cf0: setc.geu a0, t#1
```

进一步判断：

- glibc 的 generic C 代码会在 `INTERNAL_SYSCALL_CALL()` 后继续生成当前 conditional block 的 `setc.*`。
- 在 inline asm syscall 模板里强行插入 `c.bstop` / `C.BSTART.SYS` / `C.BSTART.STD` 会破坏编译器原本的 block 状态。
- 对 qemu-user 来说，`acrc 1` 更接近 Linux syscall 指令：它应该陷入 QEMU 执行 host syscall，然后从下一条 guest 指令继续，同时保留当前 Linx block 上下文，让后续 `setc.*` 仍处在原来的 conditional block 中。

修正计划：

- 回调 glibc C 侧 syscall 模板：`__SYSCALL_INSN` 只发 `acrc 1`，不再内联 block header/terminator。
- 同步简化 assembler 侧 syscall PSEUDO，避免在 syscall wrapper 中硬切 block。
- 修改 QEMU user-mode syscall 处理：
  - `trans_blk_acrc_32()` 在 `CONFIG_USER_ONLY` 下不再要求 `HEAD_TYPE_SYS`。
  - `linux-user/linx/cpu_loop.c` 处理 `LINX_EXCP_SCALL` 后不调用 `linx_reset_bstate(env)`，保留当前 block 状态。
- 重建 QEMU 与 glibc 后复测。

#### 静态链接验证路线：绕开动态加载器 dl_main

目的：

- 当前动态链接执行已经越过 syscall/brk，推进到 `ld.so.1` 的 `dl_main`。
- 新阻塞点是动态加载器内部的 `hl.sdip` 48-bit store-pair immediate 译码。
- 为了区分“glibc 本体启动/stdio 路径”和“动态加载器路径”的问题，先尝试把测试程序改为 glibc 静态链接。

验证计划：

- 使用同一个测试程序：

```text
avs/qemu/tests/lihan_glibc_puts.c
```

- 使用 Linx LLVM/LLD 加 `-static` 链接。
- 如果 sysroot 缺少 `libc.a`，先确认链接报错，再把已构建出的 `out/libc/glibc/build/libc.a` 同步到 sysroot。
- 运行方式仍然使用 qemu-user：

```text
emulator/qemu/build-user/qemu-linx -L out/libc/glibc/sysroot <static-binary>
```

预期收益：

- 静态程序不经过 `/lib/ld.so.1`，可以暂时绕开 `dl_main` 中的 `hl.sdip`。
- 如果静态程序继续失败，说明问题已经进入 glibc 静态启动、syscall、TLS 或 stdio 初始化路径。

首次静态链接结果：

```text
ld.lld: error: cannot open crtbeginT.o: No such file or directory
ld.lld: error: cannot open crtend.o: No such file or directory
```

判断：

- `clang -static` 走普通静态 executable 链接路径，会查找 `crtbeginT.o` 和 `crtend.o`。
- 当前 Linx glibc sysroot 中只有之前动态链接验证所需的 `crtbeginS.o` / `crtendS.o`。
- `libc.a` 已构建在 `out/libc/glibc/build/libc.a`，但尚未安装到 sysroot。

临时修复计划：

- 将 `out/libc/glibc/build/libc.a` 同步到 `out/libc/glibc/sysroot/usr/lib/libc.a`。
- 在 sysroot 中临时让 `crtbeginT.o` 指向 `crtbeginS.o`，`crtend.o` 指向 `crtendS.o`。
- 重新执行 `-static` 链接，确认是否还有缺失符号或重定位问题。

静态路线阶段判断：

- 静态 ELF 已能链接生成，但 LLD 会输出大量 `R_LINX_LO12` addend 警告。
- 静态 ELF 在 `_start_c` 很早 SIGILL，尚未进入 `puts` 主路径。
- 动态 ELF 已能链接并进入 `ld.so.1` 的 `dl_main`，当前阻塞点更集中。

结论：

- 回归动态链接路线，优先修复 QEMU 对当前 v0.56 `HL.SDIP` 的译码和执行语义。

#### 当前修复目标：QEMU 缺少当前 v0.56 HL.SDIP 译码

失败位置：

```text
IN: dl_main
0x0000004002822eb4: sdi s2, [s7, 360]
0x0000004002822eb8: sdi s2, [s7, 352]
0x0000004002822ebc: sdi s2, [s7, 344]
0x0000004002822ec0: (unknown)
```

LLVM 反汇编对应：

```text
1dec0: hl.sdip s2, s2, [s7, 624]
1dec6: hl.sdip s2, s2, [s7, 640]
1decc: hl.sdip s2, s2, [s7, 656]
```

根因判断：

- 当前 LLVM/glibc 已经生成 v0.56 的 `HL.SDIP` store-pair immediate。
- ISA v0.56 中该类 pair-immediate 指令使用 `bits[5:4] = 01`。
- QEMU 的 `target/linx/block48.decode` 仍把 store-pair immediate 放在旧的 pre/post-index 编码：

```text
bits[5:4] = 10
bits[5:4] = 11
```

- 因此动态加载器里的 `hl.sdip` 被 QEMU 判为 unknown instruction。

修复计划：

- 修改 `emulator/qemu/target/linx/block48.decode`，为当前 `bits[5:4] = 01` 的 `HL.{SBIP,SHIP,SWIP,SDIP}` 增加译码。
- 修改 `emulator/qemu/target/linx/insn_trans/trans_block_48.c.inc` 中 store-pair immediate 的语义：
  - `ea = SrcR + imm`
  - `SrcD  -> [ea]`
  - `SrcD1 -> [ea + element_size]`
- 重建 QEMU 后复测动态 glibc `puts`。

修复结果：

- 已补充当前 v0.56 `HL.{SBIP,SHIP,SWIP,SDIP}` 的 `bits[5:4] = 01` 译码。
- 已为无后缀 pair-immediate store 增加语义：

```text
ea = SrcR + (imm << scale)
store SrcD  -> [ea]
store SrcD1 -> [ea + element_size]
```

- QEMU 已重建通过。
- 动态 glibc 程序已越过 `dl_main` 中的 `hl.sdip`，推进到 `__minimal_malloc` / `mmap64`。

补充修正：

- QEMU 日志中 `hl.sdip s2, s2, [s7, 624]` 一开始被打印为 `[s7, 1248]`。
- 原因是旧 `@arg_sdip` 使用了带 `ex_shift_1` 的立即数字段，当前 v0.56 `HL.SDIP` 不应在译码阶段额外左移 1。
- 需要为当前 pair-immediate 单独使用完整 `simm17` 字段：

```text
15..11 = simm17[16:12]
27..23 = simm17[11:7]
47..41 = simm17[6:0]
```

- 执行阶段再按指令宽度缩放，例如 `SDIP` 使用 `imm << 3` 得到字节偏移。

#### 当前修复目标：QEMU 缺少 48-bit arithmetic immediate 译码

新的失败位置：

```text
0000000000023184 <mmap64>:
   23184: FENTRY [ra ~ ra], sp!, 8
   23188: C.BSTART COND, 0x231a8
   2318a: hl.andi a5, 4095, ->t
   23190: setc.eqi t#1, 0
```

QEMU 日志：

```text
0x000000400282818a: (unknown)
```

根因判断：

- 当前 LLVM/glibc 会生成 v0.56 的 48-bit arithmetic immediate，例如 `HL.ANDI`。
- `emulator/qemu/target/linx/block48.decode` 目前没有 `HL.ADDI/SUBI/ANDI/ORI/XORI` 及 `*W` 变体的译码。
- 32-bit arithmetic immediate 已有执行语义，可以复用到 48-bit 立即数版本。

修复计划：

- 在 `block48.decode` 增加 24-bit split immediate 字段。
- 增加 `HL.ADDI/SUBI/ANDI/ORI/XORI` 和 `HL.ADDIW/SUBIW/ANDIW/ORIW/XORIW` 的 48-bit 译码。
- 在 `trans_block_48.c.inc` 增加对应执行函数。
- 在 `disas.c` 增加对应反汇编入口。
- 重建 QEMU 后继续运行动态 glibc 程序。

修复结果：

- 已增加 48-bit `HL.ADDI/SUBI/ANDI/ORI/XORI` 与 `*W` 译码。
- 已修正当前 `HL.SDIP` 的 simm17 立即数解码，避免偏移被额外放大 2 倍。
- QEMU 已重建通过。
- 动态执行已越过 `mmap64` 的 `hl.andi`，继续推进到 `dl_main -> strcmp`。

#### 当前修复目标：当前 HL.LDI.PO 被旧 pair-post 路径误译

新的 QEMU abort：

```text
Bail out! ERROR:../target/linx/translate.c:599:set_dst_regx: code should not be reached
```

触发位置：

```text
000000000002438a <strcmp+0x52>:
   2438a: C.BSTART COND, 0x24534
   2438c: hl.ldi.po [a3, 8], ->a2, a3
```

根因判断：

- 当前 v0.56 `HL.LDI.PO` 使用 `bits[5:4] = 11`。
- QEMU 旧 decode 中 `bits[5:4] = 11` 仍对应旧的 pair-post immediate 路径。
- 旧路径把 `bits[10:6]` 当作第三目的寄存器 `RegDst2`；而当前 `HL.LDI.PO` 中这些位是 immediate 高位。
- 本例 immediate 高位为 0，于是 QEMU 调用 `set_dst_regx(..., 0)` 并 abort。

修复计划：

- 将旧 pair-post load immediate helper 调整为当前 post-index 语义：
  - `addr = SrcL + (imm << scale)`
  - `Dst0 = load(SrcL)`
  - `Dst1 = addr`
- 同步调整 register post-index pair helper，避免当前 `HL.LD.PO` 类指令也把 `bits[10:6]=0` 当作目的寄存器。
- 重建 QEMU 后复测。

修复结果：

- 已调整 48-bit post-index load-pair helper，让当前 `HL.LDI.PO [a3, 8], ->a2, a3` 不再走旧 pair-post 三目的寄存器语义。
- 已越过 `strcmp` 中的 `set_dst_regx(..., 0)` abort。
- 动态执行继续推进到 `ld.so.1` 的 `_dl_map_new_object`，并已经能在 `-strace` 中看到 loader 打开并读取 `/lib/libc.so.6`、`/usr/lib/libc.so.6`。

#### 当前修复目标：48-bit HL.BSTART.STD CALL 跳转没有正确落到目标块

新的失败位置：

```text
IN: _dl_map_new_object
0x000000400281254c: fffee8cec001fffe BSTART.STD call 0x400280c886
0x0000004002812554: ffffd507 setret -6, ->ra
```

LLVM 反汇编对应：

```text
d54c: HL.BSTART.STD CALL, 0x7886, ra=0x20000d54c
d558: addtpc 1048565, ->a0
d55c: addi a0, 1461, ->a3
```

根因判断：

- 当前动态 ELF 已经链接成功，并进入 `ld.so.1` 的真实动态装载路径。
- 失败点不再是 libc/CRT 缺失，也不是简单的 unknown 普通指令。
- QEMU 日志显示 48-bit call header 已被反汇编出来，但执行后没有稳定跳到 `_dl_signal_error` 的目标地址 `0x400280c886`。
- `-singlestep` 下同一位置容易把 12 字节 `HL.BSTART.STD CALL + setret` 组合拆开，下一条从 `0x4002812552` 开始解码为 unknown，说明 48-bit call header 的指令长度/返回地址/块提交边界可能仍按旧模型处理。

修复计划：

- 检查 `block48.decode` 中 48-bit header 的长度、`bnext_offset` 和 call 目标计算。
- 检查 `translate.c` 中 `pc_succ_insn`、`insn_size`、`head_size` 对 48-bit header 的处理。
- 检查 `trans_block_header.c.inc` 中 `BRANCH_CALL` 的提交逻辑，确认是否必须消费整个 fused call bundle 或正确设置返回地址。
- 修复后重建 QEMU，并重新运行动态 glibc `puts`。

进一步定位：

- `block48.decode` 对 call 目标的解码是对的，目标地址已经能算到 `0x400280c886`。
- 真实问题出在 PC 推进：
  - 普通 48-bit body 指令仍然是 6 字节，例如 `hl.andi`、`hl.sdip`、`hl.ldi.po`。
  - 该处 48-bit call header 后面有两字节 `0xfffe` 填充，然后才是 32-bit `setret`。
  - `translate.c:get_inst_len()` 只按 6 字节推进，导致下一次从填充字节 `0x...2552` 开始译码。
- 修复方向：
  - 仅在“48-bit header + `0xfffe` 填充 + 后续 32-bit `setret`”这个组合下，把 `pc_succ_insn` 额外前移 2 字节。
  - 这样仍保留普通 6 字节 48-bit body 指令，不破坏此前已经修好的 `HL.ANDI/SDIP/LDI.PO`。

修复结果：

- 已在 QEMU 翻译器中补充该窄条件 PC 推进修正。
- QEMU 已重建通过。
- 动态执行已经越过该 call bundle，能够真正进入 `_dl_signal_error`，说明 `HL.BSTART.STD CALL` 不再停在填充字节上。

#### 当前修复目标：glibc Linx 缺少 setjmp/longjmp 实现

新的失败现象：

```text
IN: __GI__dl_signal_error
0x000000400280c8f4: ... BSTART.STD call 0x4002828488
...
IN: __longjmp
0x0000004002828488: FENTRY [ra], sp!, 8
IN: _itoa_word
0x000000400282848c: FENTRY [ra,s0], sp!, 18
```

根因判断：

- `readelf -sW ld.so.1` 显示 `__longjmp` 只有 4 字节。
- `out/libc/glibc/build/elf/librtld.map` 显示当前 rtld 使用的是 generic `setjmp/__longjmp.c`：

```text
rtld-__longjmp.os:(.text) __longjmp size 4
.gnu.glibc-stub.longjmp
```

- `lib/glibc/sysdeps/linx/` 已有 `bits/setjmp.h` 和 `jmpbuf-offsets.h`，但没有 `setjmp.S` / `__longjmp.S`。
- 因此动态 loader 错误路径调用 `__longjmp` 时不会恢复 `jmp_buf`，而是执行一个 ENOSYS stub 后继续落入相邻 `_itoa_word`，最终用错误参数触发 guest SIGSEGV。

修复计划：

- 在 `lib/glibc/sysdeps/linx/` 增加最小可用的 `setjmp.S`：
  - 保存 `s0..s8`、`sp`、`ra` 到 `__jmp_buf[11]`。
  - `_setjmp` / `setjmp` / `__sigsetjmp` 暂时都返回 0，先满足 rtld bring-up；普通信号 mask 保存后续再补。
- 增加 `__longjmp.S`：
  - 从 `__jmp_buf` 恢复 `s0..s8`、`sp`、`ra`。
  - 返回值按 C 语义处理：`val == 0` 时让 setjmp 返回 1。
  - 显式 `C.BSTART.STD RET + c.setc.tgt ra`，避免 bare `ret` 在当前 QEMU 下只落到下一块。
- 更新 `jmpbuf-unwind.h` 中 SP 槽位说明，使其与 `bits/setjmp.h` 的布局一致。
- 重建 glibc/rtld 后复测动态 glibc 程序。

构建中追加发现：

- 新增 `setjmp.S` / `__longjmp.S` 后，glibc 已经开始选择 Linx 汇编实现。
- 但链接 `libc_pic.os` 时出现重复符号：

```text
duplicate symbol: _setjmp
duplicate symbol: setjmp
```

- 原因是 generic `setjmp/bsd-setjmp.c` 和 `setjmp/bsd-_setjmp.c` 仍被纳入构建。
- 修复方式参考 RISC-V：在 `sysdeps/linx/` 放置空的 `bsd-setjmp.c` / `bsd-_setjmp.c`，声明这些入口已由 `setjmp.S` 实现。

复测追加发现：

- 新的 `__longjmp` 已经进入 `ld.so.1`，符号大小从 4 字节变为 64 字节。
- 但 `__longjmp` 从 jmp_buf 恢复出的 `sp/ra/s0..s8` 全为 0，说明保存端仍不是新汇编。
- `ld.so.1` 中的 `__sigsetjmp` 仍只有 12 字节：

```text
__sigsetjmp:
  FENTRY [ra ~ ra], sp!, 8
  c.movr zero, ->a0
  FRET.STK [ra ~ ra], sp!, 8
```

- 根因是 `lib/glibc/sysdeps/linx/linx-rtld-stubs.c` 里仍有早期 bring-up 的 C 版 `__sigsetjmp` stub。
- C stub 带函数序言，不能可靠保存调用者的 `sp/ra`，并且会覆盖真正的 rtld setjmp 实现。

修复计划：

- 从 `linx-rtld-stubs.c` 移除 C 版 `__sigsetjmp`。
- 增加 `linx-rtld-setjmp.S`，只为 rtld 提供无序言的 `__sigsetjmp`。
- 在 `sysdeps/linx/Makefile` 的 `elf` 段加入 `linx-rtld-setjmp`。
- 重建并确认 `ld.so.1` 中 `__sigsetjmp` 变为完整保存版本，再复测动态 glibc 程序。

修复结果：

- `ld.so.1` 中 `__longjmp` 已从 generic ENOSYS stub 变为 Linx 汇编实现。
- `ld.so.1` 中 `__sigsetjmp` 已从 12 字节 C stub 变为完整保存 `s0..s8/sp/ra` 的无序言版本。
- 动态执行不再因为 jmp_buf 全 0 而落入 `_itoa_word` 或触发早期 SIGSEGV。

#### 当前新卡点：动态 loader 读取 libc 头后在 __sync_synchronize 返回处超时

运行命令：

```bash
timeout 20s emulator/qemu/build-user/qemu-linx \
  -L /home/touzi/linx-isa/out/libc/glibc/sysroot \
  /tmp/linx-lihan-glibc-user/lihan_glibc_puts
```

现象：

- 程序不再 SIGILL / SIGSEGV。
- 当前表现为超时，无 stdout/stderr。
- `-strace` 显示 dynamic loader 已经实际访问 sysroot 中的 libc：

```text
openat(AT_FDCWD,"/lib/libc.so.6",O_RDONLY|O_CLOEXEC) = 3
read(3,0x28029d0,832) = 832
close(3) = 0
openat(AT_FDCWD,"/usr/lib/libc.so.6",O_RDONLY|O_CLOEXEC) = 3
read(3,0x28029d0,832) = 832
close(3) = 0
```

但 loader 只读取 ELF 头后关闭文件，没有继续 mmap libc 段。说明当前已经推进到真实的 libc 查找/校验路径，新的问题集中在 loader 错误处理或返回控制流。

QEMU 详细日志尾部反复停在：

```text
pc       00000040028275f6
CARG_TGT 00000040028275f6
ra       000000400280ea94
```

按当前 `ld.so.1` load bias `0x4002805000` 折算，`0x40028275f6` 对应 `ld.so.1` 文件内 `0x225f6`：

```text
00000000000225f4 <__sync_synchronize>:
   225f4: 00 38        C.BSTART.STD RET
   225f6: 00 00        C.BSTOP
```

初步判断：

- 当前 hang 不是 libc/CRT 链接失败。
- loader 能打开并读取 `libc.so.6`，但没有接受该 libc 继续 mmap。
- 控制流在 `__sync_synchronize` 的 `RET/BSTOP` 附近无法回到 `ra=0x400280ea94`，可疑点是 QEMU 对 `C.BSTART.STD RET` / `C.BSTOP` 的提交语义，或进入该函数前的 block/call 状态没有正确建立。

下一步计划：

- 反汇编 `ra=0x400280ea94` 附近，确认 `__sync_synchronize` 的调用点属于哪个 loader 分支。
- 检查 QEMU `RET` block header 与 `C.BSTOP` 的提交逻辑，确认 `CARG_TGT` 是否应在 header 处设为 `ra`，而不是落到 `BSTOP` 自身。
- 同时检查为什么 `libc.so.6` 只被读头后关闭：判断是 ELF 校验失败后进入 `_dl_signal_error`，还是返回控制流错误导致 loader 走错清理路径。

进一步定位：

- `ra=0x400280ea94` 对应 `_dl_map_object_deps` 中对 `__sync_synchronize` 的正常调用点。
- `__sync_synchronize` 来自 Linx glibc rtld 本地 stub：

```text
lib/glibc/sysdeps/linx/linx-rtld-sync.S
```

当前源码为：

```asm
ENTRY (__sync_synchronize)
  ret
END (__sync_synchronize)
```

汇编结果为：

```text
00000000000225f4 <__sync_synchronize>:
   225f4: 00 38        C.BSTART.STD RET
   225f6: 00 00        C.BSTOP
```

根因判断：

- Linx 文档要求 `RET/IND/ICALL` 类 block 必须在同一 block 中通过 `setc.tgt` 显式设置动态目标。
- 当前 stub 使用 `ret` 伪指令后只生成裸 `C.BSTART.STD RET`，没有 `c.setc.tgt ra`。
- QEMU 为避免 split RET helper 自循环，曾把裸 RET 的默认目标设为下一条；这个裸 stub 因此在 `BSTOP` 自身形成循环。

修复计划：

- 修改 `linx-rtld-sync.S`，不用 `ret` 伪指令。
- 显式写成：

```asm
C.BSTART.STD RET
c.setc.tgt ra
C.BSTOP
```

- 重建 `ld.so.1`，确认 `__sync_synchronize` 由 2 字节变为 6 字节左右，并且 QEMU 能从该函数返回到 `ra=0x400280ea94`。

修复结果：

- 已修改 `lib/glibc/sysdeps/linx/linx-rtld-sync.S`。
- 已重建 G1b 并刷新 sysroot 中的 `ld.so.1` / `libc.so.6`。
- 新 `__sync_synchronize` 反汇编为：

```text
00000000000225f4 <__sync_synchronize>:
   225f4: 00 38        C.BSTART.STD RET
   225f6: 9c 02        c.setc.tgt ra
   225f8: 00 00        C.BSTOP
```

- QEMU 日志确认已经能从 `__sync_synchronize` 返回到 `_dl_map_object_deps` 的 `ra=0x400280ea94`，原先在 `0x40028275f6` 自循环的问题已消失。

#### 当前新卡点：32-bit CALL header 后的 0xfffe padding 未跳过

新的失败位置：

```text
IN: __GI__dl_signal_exception
0x000000400280c746: BSTART.STD call 0x400280c790
0x000000400280c74a: (unknown)
```

LLVM 反汇编同一位置：

```text
7746: 01 c0 12 00 fe ff 07 e5 ff ff  BSTART.STD CALL, 0x7790, ra=0x200007746
7750: 99 b2 11 00                    ldi [a1, 8], ->a3
```

根因判断：

- 这是 32-bit `BSTART.STD CALL`，后面同样存在两字节 `0xfffe` padding，然后才是 32-bit `setret`。
- 之前 QEMU 只修了 48-bit call header 的 padding 跳过逻辑。
- 因此 32-bit call header 的 `pc_succ_insn` 仍停在 `0xfffe`，下一次把 padding 当成 48-bit 指令头译码，触发 unknown/SIGILL。

修复计划：

- 扩展 `translate.c` 中 call header padding 检测。
- 对 32-bit 和 48-bit header 都识别：

```text
header + 0xfffe + 32-bit setret
```

- 命中时统一让 `pc_succ_insn += 2`。

#### 动态 glibc 当前卡点：先查官方 QEMU/LLVM/Sail 后再改

当前 loader 已经能打开 `/lib/libc.so.6`，但报：

```text
libc.so.6: wrong ELF class: ELFCLASS32
```

`llvm-readobj` 确认该文件实际是 `ELF64 / EM_LINXISA`，所以这是 QEMU 执行 loader 时把 ELF header 读偏了，不是 libc 文件本身错误。

按用户要求，先检查官方仓库而不是盲目改 QEMU：

- 官方 remote：`https://github.com/LinxISA/qemu.git`
- 当前本地 submodule：`origin/qemu-my-patch-v7.0.0`
- 官方较新相关分支：`origin/codex/qemu-refresh-boot-fixes-20260531`

官方新分支的结论：

- 新 QEMU decoder 使用原始 `simm17_6_s5_23_5_41_7` 字段解码 `HL.SDI.PO`。
- 新 QEMU translator 仍然对 `HL.SDI.PO` 使用 scaled store writeback，即 `simm17 << 3`。
- 因此不能把 `HL.SDI.PO` 改成 unscaled；那会偏离 Sail。

Sail 语义：

```sail
function exec_hl_sdi_po(...) -> unit = {
  let base = read_reg5(SrcR);
  let v : bits(64) = read_reg5(SrcD);
  mem_store64_le(base, v);
  let ea = hl_ea_imm17_scaled(base, simm17, 3);
  write_regdst(RegDst, ea)
}
```

LLVM 语义：

- `LinxISAMemOpsCombine.cpp` 对 `SDI` post-index 合并时，如果 byte delta 能被 8 整除，会生成 `HL_SDI_PO`，并把 immediate 写成 `DeltaBytes / 8`。
- 所以 `+8 bytes` 应编码为 `simm17 = 1`，再由执行端按 `<<3` 得到 `+8`。

旧 QEMU 根因：

- `emulator/qemu/target/linx/block48.decode` 的 `@arg_sdi` 仍使用旧字段：

```text
%s_imm_12_1 ... !function=ex_shift_1
@arg_sdi imm=%s_imm_12_1
```

- `ex_shift_1` 会在 decodetree 阶段先把 immediate 左移 1。
- translator 随后又在 `gen_blk_store_po_48_imm(... OFFSET_LD_SD)` 中按 64-bit store 再左移 3。
- 对 LLVM 期望的 `simm17 = 1`，旧 QEMU 实际得到 `1 << 1 << 3 = 16`，这和 trace 中 `s4=...29c0`、writeback 到 `s6=...29d0` 的 `+16` 完全吻合。

下一步修复方向：

- 不改 `HL.SDI.PO` 的 scaled 执行语义。
- 回填官方新 decoder 的做法：让 `HL.SBI/SHI/SWI/SDI.{PR,PO,UPR,UPO}` 使用原始 v0.56 `simm17_6_s5_23_5_41_7`。
- 同时放开当前旧 pattern 中固定为 `00000` 的高 5 位 immediate 字段，避免只支持低 12 位 immediate。

修复结果：

- 已修改 QEMU `target/linx/block48.decode`。
- 已重建 `emulator/qemu/build-user/qemu-linx`。
- 动态 loader 已越过 `wrong ELF class`：
  - 能 mmap `/lib/libc.so.6`。
  - 能解析 libc dynamic section。
  - 能继续推进到 TLS/NPTL 初始化。

#### 新卡点：Linx glibc 缺少 `thread_pointer.h`，rseq 使用了错误 TP

新的崩溃：

```text
set_robust_list(...) = -1 errno=38
--- SIGSEGV {si_addr=0x0000000000000004} ---
```

定位：

- 崩溃发生在 `__tls_init_tp` 的 rseq 初始化路径。
- `RSEQ_SETMEM (cpu_id, RSEQ_CPU_ID_REGISTRATION_FAILED)` 被编译成了直接写 `__rseq_offset + 4`。
- 当时 `__rseq_offset = 0`，所以写地址变成 `0x4`。

进一步确认：

- `sysdeps/linx/nptl/tls.h` 已经定义了正确的 TP 读法：

```c
ssrget TP
```

- 但 `rseq-internal.h` 走的是 `<thread_pointer.h>` 的 `__thread_pointer()`。
- Linx sysdeps 目前没有自己的 `thread_pointer.h`，所以落到了 generic 版本：

```c
return __builtin_thread_pointer ();
```

- 当前 Linx LLVM/glibc 组合下，这没有生成 SSR TP 读取，导致 rseq 代码没有把 TP 加到 `__rseq_offset` 上。

官方检查：

- `https://github.com/LinxISA/glibc.git` 当前 `origin/master` 也没有 Linx 专用 `thread_pointer.h`。
- 因此这是 Linx glibc sysdeps 缺口，不应继续改 QEMU。

修复计划：

- 新增 `lib/glibc/sysdeps/linx/thread_pointer.h`。
- 让 `__thread_pointer()` 使用和 `tls.h` 一致的 `ssrget TP`。
- 重建 G1b 并刷新 sysroot。
- 再验证 rseq 初始化是否越过 `si_addr=0x4`。

执行前确认：

- `lib/glibc/sysdeps/linx/nptl/tls.h` 已定义 `LINX_SSR_TP = 0x0000`。
- `docs/architecture/isa-manual/src/chapters/03_programming_model.adoc` 说明 Linx 使用 SSR 保存 TP/GP 等运行时状态。
- `isa/v0.56/state/system_registers.json` 中 `TP` 的 id 是 `0x0000`，描述为 `Thread pointer (TLS base).`
- 因此本次修复应该补 glibc sysdeps 的 TP 读取入口，不继续在 QEMU 侧绕过该问题。

增量构建注意：

- 新增 `sysdeps/linx/thread_pointer.h` 后，第一次 `MAKE_TARGETS=lib` 通过但没有重编 `elf/dl-tls_init_tp.os`。
- 原因是旧 `.d` 依赖仍指向 `../sysdeps/generic/thread_pointer.h`，make 不知道 sysdeps include 优先级发生了变化。
- 已确认以下对象仍依赖 generic thread pointer：
  - `csu/libc-tls.o`
  - `elf/dl-support.o`
  - `elf/dl-sysdep.o/os`
  - `elf/dl-tls.o/os`
  - `elf/dl-tls_init_tp.o/os`
  - `nptl/pthread_create.o/os`
  - `posix/sched_getcpu.o/os`
- 下一步先清掉这些对象和 `.d`，再重建，确保 rseq 路径真正使用 Linx 的 `ssrget TP`。

修复结果：

- 清理旧 `.d/.o/.os` 后重建 G1b 通过。
- `elf/dl-tls_init_tp.os` 依赖已变成 `../sysdeps/linx/thread_pointer.h`。
- 反汇编确认 rseq 路径已从：

```text
hl.ld.pcr [__rseq_offset], ->t
add zero, t#1, ->u
c.swi t#1, [u#1, 4]
```

变成：

```text
ssrget TP, ->a0
hl.ld.pcr [__rseq_offset], ->t
add a0, t#1, ->u
c.swi t#1, [u#1, 4]
```

- `si_addr=0x4` 的 rseq 空地址写入问题已消失。

#### 新卡点：rtld `security_init` 写 `__stack_chk_guard` 时走到未稳定 GOT 地址

现象：

```text
--- SIGSEGV {si_addr=NULL} ---
```

定位：

- `LD_SHOW_AUXV=1` 显示 QEMU 已提供 `AT_RANDOM=0x4002803cf0`，所以不是 QEMU 缺少 `AT_RANDOM`。
- trace 显示 `_dl_sysdep_start` 已执行：

```text
hl.sd.pcr a5[0x400282c6f8]   # _dl_random = 0x4002803cf0
```

- 崩溃发生在 `security_init` 写 stack guard：

```text
addtpc ...          # materialize GOT slot address
addi ...
c.ldi [t#1, 0], ->t # load GOT slot
sdi u#1, [t#1, 0]   # t#1 为 0 时写 NULL
```

官方/本地对照：

- 官方较新的 QEMU 对 `ADDTPC` 已转向 page-base 语义。
- 本地 LLVM/lld 注释也说明 `ADDTPC` 用于 page-scaled 全局地址物化。
- 但当前这个 rtld GOT_HI20/LO12 序列在本地产物里仍会把 stack guard 的目标地址走成不稳定的间接写。

下一步修复方向：

- 不先盲改 QEMU。
- 先补 Linx glibc TLS guard sysdeps：
  - 在 `tcbhead_t` 中加入 `stack_guard` 和 `pointer_guard`。
  - 定义 `THREAD_SET_STACK_GUARD` / `THREAD_SET_POINTER_GUARD`。
  - 新增 `sysdeps/linx/stackguard-macros.h`，让后续 `STACK_CHK_GUARD` / `POINTER_CHK_GUARD` 从 TCB 读取。
- 这样 `security_init` 会写 TP-relative TCB 字段，不再在 rtld bootstrap 早期写 `__stack_chk_guard` 的 GOT 间接地址。

执行记录：

- 已修改 `lib/glibc/sysdeps/linx/nptl/tls.h`：
  - `tcbhead_t` 增加 `stack_guard` / `pointer_guard`。
  - 增加 `THREAD_SET_STACK_GUARD` / `THREAD_COPY_STACK_GUARD`。
  - 增加 `THREAD_GET_POINTER_GUARD` / `THREAD_SET_POINTER_GUARD` / `THREAD_COPY_POINTER_GUARD`。
- 已新增 `lib/glibc/sysdeps/linx/stackguard-macros.h`：
  - `STACK_CHK_GUARD` 从当前 TP 对应 TCB 读取。
  - `POINTER_CHK_GUARD` 从当前 TP 对应 TCB 读取。
- 下一步先不继续改 QEMU；清理 glibc 中可能缓存旧 guard/TLS 头文件依赖的对象，重建 G1b，刷新 sysroot 后重跑动态 glibc `puts`。

修复结果：

- 重新运行 G1b 通过。
- 已刷新 sysroot 中的 `ld.so.1` / `libc.so.6` / CRT 文件。
- 已重新链接 `/tmp/linx-lihan-glibc-user/lihan_glibc_puts`。
- `security_init` 写 `__stack_chk_guard` 时的 `SIGSEGV si_addr=NULL` 已越过。

#### 新卡点：glibc 汇编 syscall wrapper 成功返回后落入错误路径

现象：

```text
/tmp/linx-lihan-glibc-user/lihan_glibc_puts: error while loading shared libraries: /lib/libc.so.6: cannot apply additional memory protection after relocation
```

`-strace` 关键线索：

```text
mprotect(0x0000004002986000,16384,PROT_READ) = 0
...
error while loading shared libraries: /lib/libc.so.6: cannot apply additional memory protection after relocation
```

结论：

- host/QEMU 侧 `mprotect` syscall 已成功返回 `0`。
- rtld 仍然进入 `_dl_protect_relro()` 的错误分支，说明问题在 guest 侧 syscall wrapper 返回控制流或返回值判断。
- 反汇编 `ld.so.1` 中的 `mprotect` wrapper：

```text
000000000002315c <mprotect>:
  C.BSTART.STD
  addiw zero, 226, ->a7
  acrc
  addiw zero, 0, ->a7
  C.BSTART COND, error
  setc.ltu a7, a0
  C.BSTART.STD RET
error:
  j __syscall_error
```

- 成功路径使用裸 `C.BSTART.STD RET`，没有 `c.setc.tgt ra`。
- 这和前面 `linx-rtld-sync.S` 的裸 RET 自循环/落入问题同类：Linx 的 RET/IND/ICALL 类 block 需要显式设置动态目标。
- 这不是继续改 QEMU 的首选点；应修 glibc Linx `sysdep.h` 的汇编侧 `ret` / `ret_NOERRNO` / `ret_ERRVAL` 和 PSEUDO 返回模板，让 syscall wrapper 成功路径显式 `c.setc.tgt ra`。

修复结果：

- 已修改 `lib/glibc/sysdeps/unix/sysv/linux/linx/sysdep.h`。
- 汇编 syscall wrapper 的成功返回现在生成：

```text
C.BSTART.STD RET
c.setc.tgt ra
C.BSTOP
```

- 错误判断阈值从无法正确编码的 `addiw zero, -4096` 改为和 C 侧 inline syscall 一致的：

```text
subi zero, 4095, ->a7
setc.geu a0, a7
```

- 重建 G1b 通过。
- 反汇编确认 `mprotect` / `munmap` wrapper 已带 `c.setc.tgt ra`。
- 复测后，rtld 的 RELRO `mprotect` 已全部成功，不再报 `cannot apply additional memory protection after relocation`。

#### 新卡点：libc early init 中 ADDTPC 地址材料化高/低基准不一致

新现象：

```text
mprotect(0x0000004002986000,16384,PROT_READ) = 0
mprotect(0x0000004000002000,4096,PROT_READ) = 0
mprotect(0x000000400282b000,8192,PROT_READ) = 0
--- SIGSEGV {si_signo=SIGSEGV, si_code=1, si_addr=NULL} ---
```

定位：

- 程序已越过 rtld RELRO 保护，进入 `_dl_call_libc_early_init`。
- `ld.so.1` 调用 libc 的 `__libc_early_init`。
- 在 `__libc_early_init` 中，LLVM 反汇编显示：

```text
14b286: addtpc 12, ->a0
14b28a: addi a0, 2632, ->a0
14b28e: ldi [a0, 0], ->a0
14b292: sbi s0, [a0, 0]
```

- QEMU 日志对同一条 `addtpc` 打印为：

```text
addtpc 49152, ->a0
```

交叉检查：

- 当前旧 QEMU `block32.decode` 对 `%s_imm_20` 使用 `ex_shift_12`，所以 decode/disas 阶段已经把 `12` 变成 `49152`。
- 旧 QEMU translator 再用 `ctx->base.pc_next + imm`，因此结果依赖当前 PC 的低 12 位。
- 官方较新 QEMU 分支 `origin/codex/qemu-refresh-boot-fixes-20260531`：
  - decode 中 `imm20` 是原始字段，没有在 decodetree 阶段左移。
  - `trans_addtpc` 使用 `(PC & ~0xfff) + (sext(imm20) << 12)`。
- 本地 LLVM/lld 明确按 page-scaled ADDTPC 发码：
  - `compiler/llvm/lld/ELF/Arch/LinxISA.cpp`：`ADDTPC adds a 4KiB-scaled signed immediate`。
  - `compiler/llvm/llvm/lib/Target/LinxISA/...` 多处说明 `ADDTPC (page base) + ADDI/ADDIW (low 12 bits)`。
- 当前 superproject 的 Sail/`semantics_conventions.json` 仍写 `ADDTPC` 为 `imm << 1`，这和 LLVM/lld 以及官方新 QEMU 分支冲突；本轮为了跑当前 LLVM/glibc 产物，先让 QEMU 对齐 LLVM 和官方 QEMU，并记录后续需要同步 Sail/spec。

修复方向：

- QEMU `ADDTPC` decode 保留 raw `imm20`，不要在 decodetree 阶段左移。
- QEMU `ADDTPC` translator 改为 page-base：

```text
rd = (current_pc & ~0xfff) + (sext(imm20) << 12)
```

- `LUI` 不能被这个改动破坏；如果复用 `%s_imm_20`，需要单独在 translator 中执行 `imm << 12`，或保留单独的 shifted decode 字段。

#### 官方仓库对照与 ADDTPC 实测回退

检查对象：

```text
superproject: https://github.com/LinxISA/linx-isa
qemu submodule: https://github.com/LinxISA/qemu
```

结论：

- `linx-isa` 的 `origin/main` 目前仍然固定到本地同一个 QEMU submodule commit：

```text
emulator/qemu -> 12b28e847e2e94bed322da122b147f00a9633727
compiler/llvm -> ea930273ec2acffa98491bf7057894dbd3f54c90
lib/glibc     -> 085874633efdb9125b6a843ab180962f9eb3a9af
```

- `LinxISA/qemu` 仓库本身已经有较新的 Linx target 改动，主要在：

```text
origin/master
origin/codex/qemu-refresh-boot-fixes-20260531
origin/codex/runtime-bstart-closure
```

- 官方较新 QEMU 已从旧的 `block32.decode` / `block48.decode` / `trans_block_*.c.inc` 大幅重构到 `insn32.decode` / `insn48.decode` / `translate.c`，不是可以直接整块 cherry-pick 到当前 submodule 的小补丁。
- 官方新 QEMU 中 `ADDTPC` 采用 page-base 语义：

```text
rd = (PC & ~0xfff) + (sext(imm20) << 12)
```

- 但是在当前本地 LLVM/lld + glibc 产物上，临时把 QEMU 改成官方 page-base ADDTPC 后，动态程序从“越过 rtld RELRO、进入 `__libc_early_init` 后 NULL SIGSEGV”退化为很早的 `SIGSEGV si_addr=0x8`，没有进入正常 syscall/rtld 路径。
- 因此本轮已回退该 ADDTPC 实验，恢复旧 QEMU 对当前产物可运行到更深位置的语义：

```text
decode: imm20 在 decodetree 阶段左移 12
translate: rd = current PC + shifted imm
```

后续判断：

- 官方仓库确实有相关改变，但当前 superproject 没有采用这些改变。
- `ADDTPC` 不能单独按官方新 QEMU 回灌；它还牵涉当前 LLVM/lld 输出、Sail/spec 文档和 QEMU 新旧 decoder 架构三者同步。
- 当前继续推进 glibc user-mode 时，优先检查官方已经修过的 PCR/HL48、SrcRType、call/ret closure 等局部语义，逐项小步回灌和验证，不做 QEMU 大重构。

#### 当前更正：ADDTPC 不是 QEMU 单点问题，而是 lld hi/lo 配对语义混用

工作树当前实际状态：

- QEMU `ADDTPC` 已处于官方新分支一致的 page-base 实验状态：

```text
rd = (PC & ~0xfff) + (sext(imm20) << 12)
```

- 该状态下动态程序很早在 `ld.so.1` `_dl_start` 附近崩溃：

```text
SIGSEGV si_addr=0x8
```

最新对照结果：

- 旧 exact-PC 语义：

```text
rd = PC + (sext(imm20) << 12)
```

可以让 rtld 继续推进到 `__libc_early_init`，但 libc 中访问 `__libc_single_threaded` 的 GOT slot 会算错地址，最终从 0 地址附近写入而崩溃。

- page-base 语义可以正确解释 libc GOT 访问：

```text
__libc_single_threaded GOT slot = page(PC) + 12 * 4096 + 0xa48
```

但会让 rtld `_dl_start` 中 `_dl_rtld_map` / `l_info` 的本地 PC-relative 材料化偏到错误页，导致 `_dl_rtld_map+0x70` 没被正确填充，后续从 `0x8` 读取。

关键结论：

- 当前生成出的 `ld.so.1` 和 `libc.so.6` 里同时存在两种地址材料化假设：
  - `R_LINX_PCREL_HI20 + R_LINX_LO12` 目前更像 exact-PC：低 12 位来自完整 `S - P`。
  - `R_LINX_GOT_HI20 + R_LINX_GOT_LO12` 更像 page-base：低 12 位来自 GOT slot 绝对页内偏移。
- 因此不能在 QEMU 里继续做“按场景猜测”的混合 ADDTPC。
- 结合本地 LLVM 后端注释、LLD 原始表达式、官方较新 QEMU 分支，下一步应让 lld 的 Linx hi/lo relocation 统一回 page-base ABI：

```text
ADDTPC: page(S + A) - page(P)
LO12:   (S + A) & 0xfff
```

后续动作：

1. 修复 `compiler/llvm/lld/ELF/Arch/LinxISA.cpp`，恢复 `R_LINX_PCREL_HI20` / `R_LINX_GOT_HI20` 的 page-based relocation 表达。
2. 修复 `compiler/llvm/lld/ELF/InputSection.cpp` 中 `RE_LINX_PC_INDIRECT`，让 `R_LINX_LO12` 从配对 HI relocation 的目标绝对地址取低 12 位，而不是取 `S - P` 的低 12 位。
3. 重建 LLD、重建 glibc G1b、刷新 sysroot，再用 page-base QEMU 复测动态 glibc `puts`。

#### 阶段性成功：动态 glibc `puts` 已在 qemu-user 中正常运行

本轮涉及：

```text
compiler/llvm/lld/ELF/Arch/LinxISA.cpp      # 恢复/确认 page-base 语义，当前无最终净 diff
compiler/llvm/lld/ELF/InputSection.cpp
```

修复内容：

- `R_LINX_PCREL_HI20` 确认使用 page delta 表达：

```text
page(S + A) - page(P)
```

- `R_LINX_GOT_HI20` 同样使用 GOT page delta。
- `R_LINX_LO12` 通过配对 HI relocation 找到真实目标，然后返回目标绝对地址，让 `encodeLo12()` 取：

```text
(S + A) & 0xfff
```

这使普通 `PCREL_HI20/LO12` 和 `GOT_HI20/GOT_LO12` 都符合 page-base `ADDTPC` ABI。

构建与验证：

```bash
cmake --build compiler/llvm/build-linxisa-clang --target lld -- -j2

GMAKE_BIN=/usr/bin/gmake \
GSED_BIN=/usr/bin/sed \
BISON_BIN=/usr/bin/bison \
READELF_BIN=/usr/bin/readelf \
SYSROOT=/home/touzi/linx-isa/out/libc/glibc/sysroot \
JOBS=2 \
bash lib/glibc/tools/linx/build_linx64_glibc_g1b.sh
```

结果：

```text
[G1b] status: pass
[G1b] classification: shared_libc_so_built
```

关键反汇编确认：

```text
ld.so.1 _dl_start:
  addtpc 12, ->t
  addi   t#1, 1312, ->t    # 0x520, _dl_rtld_map 页内偏移

libc.so __libc_early_init:
  addtpc 12, ->a0
  addi   a0, 2632, ->a0    # 0xa48, __libc_single_threaded GOT slot 页内偏移
```

动态测试程序：

```text
avs/qemu/tests/lihan_glibc_puts.c
/tmp/linx-lihan-glibc-user/lihan_glibc_puts
```

运行命令：

```bash
emulator/qemu/build-user/qemu-linx \
  -L /home/touzi/linx-isa/out/libc/glibc/sysroot \
  /tmp/linx-lihan-glibc-user/lihan_glibc_puts
```

运行结果：

```text
exit code: 0
stderr: empty
stdout contains: Hello from Linx glibc + qemu-user
```

`-strace` 关键路径：

```text
openat(AT_FDCWD,"/lib/libc.so.6",O_RDONLY|O_CLOEXEC) = 3
mmap(NULL,1448537,PROT_EXEC|PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0) = 0x0000004002832000
set_tid_address(...) = <tid>
set_robust_list(...) = -1 errno=38
mprotect(...,PROT_READ) = 0
getrandom(...,8,1,...) = 8
write(1,0x2996010,34) = 34
exit_group(0)
```

结论：

- 动态 ELF 可以链接成功。
- `/lib/ld.so.1` 可以被 qemu-user 加载并执行。
- rtld 可以找到、读取、mmap、解析并重定位 `/lib/libc.so.6`。
- glibc 初始化可以越过 TLS、rseq、RELRO、random guard、libc early init。
- 用户程序已经通过正常 `main -> puts -> exit` 路径运行成功，没有再使用裸 Linx Linux syscall ABI。

已清理的尾巴：

- 已移除 glibc `elf/dl-load.c` / `elf/dl-version.c` 中早期 bring-up 阶段留下的无条件 `_dl_printf` 诊断。
- 残留检查 `rg "linx_trace|linx-rtld-(id|map|ver|dyn|need|lose)" lib/glibc/elf/dl-load.c lib/glibc/elf/dl-version.c` 无输出。
- 动态程序 stdout 已恢复为用户程序自己的输出，不再混入 `linx-rtld-*`。

#### 补充验证：`printf` 格式化输出已成功

新增测试：

```text
avs/qemu/tests/lihan_glibc_printf.c
```

测试程序：

```c
#include <stdio.h>

int
main(void)
{
    printf("Hello from Linx glibc printf: value=%d status=%s\n", 42, "ok");
    return 0;
}
```

动态链接产物：

```text
/tmp/linx-lihan-glibc-user/lihan_glibc_printf
```

ELF 形态：

```text
ELF64 / EM_LINXISA
PIE / ET_DYN
interpreter: /lib/ld.so.1
NEEDED: libc.so.6
RUNPATH: /lib
```

运行命令：

```bash
emulator/qemu/build-user/qemu-linx \
  -L /home/touzi/linx-isa/out/libc/glibc/sysroot \
  /tmp/linx-lihan-glibc-user/lihan_glibc_printf
```

运行结果：

```text
exit code: 0
stderr: empty
link stdout: empty
link stderr: empty
stdout exactly: Hello from Linx glibc printf: value=42 status=ok
```

结论：

- 当前已经不是只跑通 `puts`。
- `main -> printf -> glibc stdio/vfprintf -> write -> exit` 的最小格式化输出闭环已经成功。
- `linx-rtld-*` stdout 噪声已清理。
- `R_LINX_LO12` non-zero addend 链接 warning 已清理。

#### 清理补充：`R_LINX_LO12` warning 收敛

现象：

```text
ld.lld: warning: non-zero addend in R_LINX_LO12 relocation ...
```

根因：

- Linx glibc/rtld 中有一类 `R_LINX_LO12` 直接指向最终符号加 addend，例如 `.rodata.str1.1+0x1589`。
- 原先 LLD 的 Linx HI/LO 恢复逻辑只按符号向前回溯，容易把不同 addend 的 HI20 错配在一起，于是把合法 addend 当作“被忽略的 LO12 addend”报警。
- 进一步收紧为 exact addend 后，又暴露出 Linx block layout 的真实形态：部分 LO12 的对应 HI20 可能位于后面的 predecessor block，而不是 LO12 前方。

修复：

- 修改 `compiler/llvm/lld/ELF/InputSection.cpp`。
- `findLinxPCRelHiBySymbol` 改为精确匹配 `(symbol, addend)`。
- 在同一个 input section 内同时查找 LO12 前后最近的 `R_LINX_PCREL_HI20`，覆盖 HI20 在后继位置的 block layout。
- `RE_LINX_PC_INDIRECT` 继续返回 HI20 目标绝对地址，让 LO12 编码取目标低 12 位。

重新验证：

```text
cmake --build compiler/llvm/build-linxisa-clang --target lld -- -j2
G1b status: pass
link exit: 0
link stdout bytes: 0
link stderr bytes: 0
run exit: 0
run stderr bytes: 0
run stdout: Hello from Linx glibc printf: value=42 status=ok
```

#### 清理补充：QEMU `kenny` TB 统计输出

现象：

```text
kenny: TB exec = 7881, trans = 6219
```

根因：

- 这行不是用户程序输出，也不是 glibc/rtld 输出。
- 来源是 QEMU user-mode 中早期性能统计调试代码：
  - `accel/tcg/cpu-exec.c` 维护 `kenny_tb_exec`。
  - `accel/tcg/translate-all.c` 维护 `kenny_tb_trans`。
  - `linux-user/syscall.c` 在 `exit` / `exit_group` 时直接 `printf` 到 stdout。
- 因为打印发生在宿主 QEMU 进程里，它会混入用户程序 stdout，污染 `printf` 验证结果。

修复：

- 移除 `kenny_tb_exec` / `kenny_tb_trans` 全局计数器。
- 移除 TCG 执行/翻译路径上的计数自增。
- 移除 `linux-user/syscall.c` 中 exit/exit_group 时的 `printf("kenny: TB exec ...")`。
- 移除 Linx cpu loop 中不再使用的 `extern` 声明。

重新验证：

```text
make -C emulator/qemu/build-user -j2
strings emulator/qemu/build-user/qemu-linx | rg "kenny: TB exec|kenny_tb_exec|kenny_tb_trans"
result: empty

run exit: 0
run stderr bytes: 0
run stdout: Hello from Linx glibc printf: value=42 status=ok
```

#### 两个 stdout 小尾巴的清理过程

本阶段真正污染用户 stdout 的有两类输出，清理时分开处理：

```text
linx-rtld-*
kenny: TB exec = ..., trans = ...
```

第一类：glibc rtld bring-up 诊断。

定位方式：

```bash
rg "linx_trace|linx-rtld-(id|map|ver|dyn|need|lose)" \
  lib/glibc/elf/dl-load.c \
  lib/glibc/elf/dl-version.c
```

定位结果：

- `lib/glibc/elf/dl-load.c` 中有加载 `libc.so.6` 时的 `linx-rtld-id*`、`linx-rtld-map*`、`linx-rtld-lose`。
- `lib/glibc/elf/dl-version.c` 中有版本检查阶段的 `linx-rtld-ver`、`linx-rtld-dyn`、`linx-rtld-need*`。
- 这些 `_dl_printf` 是早期 bring-up 为观察 rtld 加载、映射、版本解析状态而加入的临时输出。

修复方式：

- 移除 `linx_trace_libc_load_p` 和相关无条件 `_dl_printf`。
- 移除 `linx_trace_version_map` 和相关调用。
- 不改 glibc 正常错误路径和 `LD_DEBUG` 路径，只清理 Linx bring-up 私有诊断。

验证方式：

```bash
rg "linx_trace|linx-rtld-(id|map|ver|dyn|need|lose)" \
  lib/glibc/elf/dl-load.c \
  lib/glibc/elf/dl-version.c
```

结果应为空。

第二类：QEMU TCG TB 统计输出。

定位方式：

```bash
strings emulator/qemu/build-user/qemu-linx | \
  rg "kenny: TB exec|kenny_tb_exec|kenny_tb_trans"

rg "kenny: TB exec|kenny_tb_exec|kenny_tb_trans" emulator/qemu
```

定位结果：

- `accel/tcg/cpu-exec.c` 维护 `kenny_tb_exec`。
- `accel/tcg/translate-all.c` 维护 `kenny_tb_trans`。
- `linux-user/syscall.c` 在 `exit` / `exit_group` 时直接 `printf` 到宿主 stdout。
- `linux-user/linx/cpu_loop.c` 留有不再需要的 `extern` 声明。

修复方式：

- 删除 `kenny_tb_exec` / `kenny_tb_trans` 全局变量。
- 删除 TCG 执行和翻译路径里的计数自增。
- 删除 `do_syscall` 中 exit/exit_group 时的 `printf("kenny: TB exec ...")`。
- 删除 Linx cpu loop 里对应的 `extern`。

重建和验证：

```bash
make -C emulator/qemu/build-user -j2

strings emulator/qemu/build-user/qemu-linx | \
  rg "kenny: TB exec|kenny_tb_exec|kenny_tb_trans"
```

结果应为空。

最终 stdout 验证：

```bash
emulator/qemu/build-user/qemu-linx \
  -L /home/touzi/linx-isa/out/libc/glibc/sysroot \
  /tmp/linx-lihan-glibc-user/lihan_glibc_printf \
  > /tmp/linx-lihan-glibc-user/logs/run.stdout \
  2> /tmp/linx-lihan-glibc-user/logs/run.stderr
```

期望结果：

```text
run exit: 0
run stderr: empty
run stdout exactly: Hello from Linx glibc printf: value=42 status=ok
```

#### 便捷验证：`cat` 生成 C 文件并自动动态链接

新增脚本：

```text
avs/qemu/tests/lihan_cat_glibc_autolink.sh
```

验证方式：

```bash
./avs/qemu/tests/lihan_cat_glibc_autolink.sh
```

脚本行为：

- 用 `cat > /tmp/linx-lihan-cat-glibc/lihan_cat_glibc_hello.c` 生成一个简单 C 程序。
- 使用 Linx LLVM clang driver 直接编译并动态链接 glibc，不再手写完整 `ld.lld` 命令。
- 关键链接参数是 `--sysroot=out/libc/glibc/sysroot`、`-B out/libc/glibc/sysroot/usr/lib`、`-rtlib=libgcc`、`-unwindlib=none`、`-pie`、`--dynamic-linker=/lib/ld.so.1`。
- 最后通过 `emulator/qemu/build-user/qemu-linx -L out/libc/glibc/sysroot` 运行生成的 Linx ELF。

验证结果：

```text
built: /tmp/linx-lihan-cat-glibc/lihan_cat_glibc_hello
Hello from cat-built Linx glibc: value=2026 status=ok
```

生成 ELF 确认：

```text
interpreter: /lib/ld.so.1
NEEDED: libc.so.6
RUNPATH: /lib
```

说明：

- 当前 x86 主机不能直接 `./tmp/.../lihan_cat_glibc_hello` 执行 Linx ELF，除非额外注册 `binfmt_misc`。
- 因此这里提供的是 `./avs/qemu/tests/lihan_cat_glibc_autolink.sh` 这种验证入口：用户侧仍是 `./`，脚本内部负责调用 qemu-user。

#### PR review cleanup：raw syscall smoke test inline asm 约束修复

审查问题：

- `avs/qemu/tests/lihan_qemu_user_hello.c` 原先在 inline asm 内部手动把输入操作数依次移动到 `a0`、`a1`、`a2`、`a7`。
- 这些寄存器同时又出现在 clobber list 中，编译器可能把某个输入操作数分配到同一批目标寄存器，导致前面的 `c.movr` 覆盖后面的输入值。
- GCC/Clang inline asm 也不应该把输入/输出寄存器同时作为 clobber 处理。

修复方式：

- 使用 local register variables 显式绑定 syscall ABI 寄存器：
  `a0` 保存第一个参数和返回值，`a1`、`a2` 保存后续参数，`a7` 保存 syscall number。
- asm 模板只保留 Linx syscall block 切换和 `acrc 1`，不再手写 `c.movr`。
- clobber list 只保留 `memory`，避免与输入/输出约束冲突。

验证方式：

```bash
compiler/llvm/build-linxisa-clang/bin/clang \
  --target=linx64-unknown-linux-gnu \
  -O2 -nostdlib -static -fuse-ld=lld -Wl,-e,_start \
  -o /tmp/linx-lihan-qemu-user/lihan_qemu_user_hello \
  avs/qemu/tests/lihan_qemu_user_hello.c

emulator/qemu/build-user/qemu-linx \
  /tmp/linx-lihan-qemu-user/lihan_qemu_user_hello
```

验证结果：

```text
Hello from Linx LLVM + qemu-usermode
```

同时复跑动态 glibc `printf` 主验证：

```bash
emulator/qemu/build-user/qemu-linx \
  -L /home/touzi/linx-isa/out/libc/glibc/sysroot \
  /tmp/linx-lihan-glibc-user/lihan_glibc_printf
```

结果：

```text
Hello from Linx glibc printf: value=42 status=ok
```

补充检查：

```bash
git diff --check
bash tools/ci/check_repo_layout.sh
```

结果均通过。
