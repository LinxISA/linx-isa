# 灵犀 ASM ABI/展开/上下文检查表

在 musl/glibc/runtime 代码中登陆 灵犀64 asm 更改时使用此清单。

## A) ABI 注册合同

- [ ] 使用 `${LINUX_ROOT}/Documentation/linxisa/abi.md` 中的 linx64 ABI 寄存器映射。
- [ ] 在可调用函数中保留被调用者保存的集合（`s0..s8`、`sp`）。
- [ ] 跨调用/返回保留 `ra` 语义。
- [ ] 使堆栈在调用边界处保持 16 字节对齐。

## B) 阻止 ISA 合法性

- [ ] 控制流用有效的块标记（`BSTART/C.BSTART` + `BSTOP/C.BSTOP`）表示。
- [ ] 条件分支消耗同一条件块内的 `SETC`。
- [ ] 间接传输在 `IND` 块中使用 `setc.tgt`。
- [ ] `RET` 块使用显式目标设置 (`BSTART.RET` + `setc.tgt ra`)。
- [ ] 没有直接非法分支到块 块体 的中间。
- [ ] 动态 `RET/IND/ICALL` 目标是合法的块启动。

## C) 调用标头融合/邻接

- [ ] 返回直接 `CALL` 源使用融合形式：`BSTART.CALL ..., ra=...`。
- [ ] 降低的对象仍然保持直接相邻的 `SETRET/C.SETRET`
      选择的编码需要它。
- [ ] 在调用 块头 和 setret 实现之间不发出任何指令。
- [ ] 不带 `SETRET` 的非返回 `CALL` 块头 是明确/有意的，并保持 `ra` 不变。

## D) 系统调用路径正确性

- [ ] 系统调用号位于 `a7` 中。
- [ ] 参数位于 `a0..a5` 中。
- [ ] 陷阱指令是 `acrc 1`（不是传统回退陷阱）。
- [ ] 返回值路径保留 `a0` 中的负 errno 约定。## E) setjmp/sigsetjmp/longjmp

- [ ] `__jmp_buf` 与 灵犀 ABI 存储集大小（11 个字）匹配。
- [ ] `setjmp` 仅保存 ABI 保留状态（`s0..s8`、`sp`、`ra`）。
- [ ] `longjmp` 恢复相同状态并强制执行 `val==0 -> 1`。
- [ ] `sigsetjmp` 在 `savemask!=0` 时通过 `__sigsetjmp_tail` 进行掩码保存/恢复。

## F) 信号/恢复器 ABI

- [ ] 用户空间 `SA_RESTORER` 定义为 `0x04000000`。
- [ ] `__restore_rt` 发布 `rt_sigreturn`（`a7=139`、`acrc 1`）。
- [ ] 对于 灵犀，无操作通用恢复器回退未激活。
- [ ] `mcontext/sigcontext/ucontext` 布局与 Linux 灵犀 UAPI 兼容。

## G) 展开/上下文切换一致性

- [ ] 保存/恢复顺序与 Linux 灵犀 内核模式一致：
  - `${LINUX_ROOT}/arch/linx/kernel/switch_to.S`
  - `${LINUX_ROOT}/arch/linx/kernel/entry.S`
  - `${LINUX_ROOT}/arch/linx/kernel/signal.c`
- [ ] Linux 跨堆栈检查确认 call/ret 目标设置与内核模式匹配。
- [ ] Noreturn 终端存根（`sigreturn`、`exit`、unmap-self 路径）不会暴露虚假的展开路径。
- [ ] 导出到用户空间的任何上下文结构都符合 ptrace/signal 期望。

## H) 搬迁/TLS 合同

- [ ] 灵犀 拱形重定位 块头 使用规范的 `R_LINX_*` 常量。
- [ ] `CRTJMP` 是真正的控制传输（不是无操作）。
- [ ] `dlsym` 将调用者返回地址元数据传递给 `__dlsym`。
- [ ] `tlsdesc` 存根是拱形实现（无零返回回退）。

## I) 运行时门期望- [ ] 静态链接和共享链接都会经过烟门。
- [ ] 共享运行时包括 `/lib/libc.so` 和 `/lib/ld-musl-linx64.so.1`。
- [ ] QEMU 测试涵盖：
  - 信号传输/恢复器
  - setjmp/sigsetjmp/longjmp
  - 线程创建/加入+TLS
  - dlopen/dlsym + TLS 描述符路径