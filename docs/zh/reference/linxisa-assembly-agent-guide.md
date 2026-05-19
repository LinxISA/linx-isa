# 灵犀指令集 组装代理指南

本指南是面向代理的规范参考，用于在 libc/runtime 启动工作中编写 灵犀指令集 程序集。

## 1) 标量 ABI（linx64 Linux 用户空间）

事实来源：

- `${LINUX_ROOT}/Documentation/linxisa/abi.md`

当前编译器分支注释：

- 规范编译器实现是 in-repo Bisheng LLVM 分支
  `compiler/llvm`;
- 活动注册的编译器架构名称为 `linx64` 和 `linx64be`；
- 使用 `linx64-linx-none-elf` 进行裸机/编译器 AVS 工作和
  `linx64-unknown-linux-*` 用于托管 Linux 通道。

注册合同：

- `R0` = `zero`（常量 0）
- `R1` = `sp`
- `R2..R9` = `a0..a7`（参数/返回+系统调用参数）
- `R10` = `ra`
- `R11..R19` = `s0..s8`（被调用者保存）
- `R20..R23` = `x0..x3`（来电刮擦）

调用约定：

- 整数/指针返回：`a0`
- 整数/指针参数：`a0..a7`，然后堆栈
- 被叫方保存：`s0..s8` 和 `sp`
- 来电已保存：`a*`、`ra`、`x0..x3`
- 堆栈对齐：16 字节

线程指针：

- TLS 基础在 SSR `0x0000` (`TP`) 中建模并通过 `ssrget/ssrset` 访问。

## 2) 块结构控制流规则

灵犀为块结构；控制流必须针对合法的块边界。

所需图案：- 在控制流区域周围使用 `BSTART ...` / `BSTOP` 或 `C.BSTART ...` / `C.BSTOP`。
- 对静态标签使用直接块分支：`C.BSTART DIRECT, <label>`。
- 在同一块中使用带有 `SETC` 谓词的条件块分支：
  - `C.BSTART COND, <label>`
  - `setc.<cond> ...`
  - `C.BSTOP`
- 通过目标寄存器使用间接块传输：
  - `C.BSTART IND`
  - `setc.tgt <reg>`
  - `C.BSTOP`

实用规则：

- 不要发出绕过块进入/退出标记的临时直通/跳跃混合。

## 3) 精确的 Call/Ret 合约（强制）

正常函数形式：

- 在函数入口处使用 `FENTRY`。
- 使用 `FRET.STK` 进行正常退货。
- 规范对是 `FENTRY + FRET.STK`。

尾调用形式：

- 尾部调用函数仍以 `FENTRY` 进入。
- 使用 `FEXIT` 进行尾部转移退出。
- 规范尾部对是 `FENTRY + FEXIT`，然后块合法传输到被调用者。

`RET/IND/ICALL` 目标设置：

- `BSTART.RET` 需要 `setc.tgt` 来定义目标源。
- 规范返回块是：
  - `C.BSTART.RET`
  - `c.setc.tgt ra`
  - `C.BSTOP`
- `IND` 和 `ICALL` 块还需要在同一块中显式 `setc.tgt`。

融合呼叫 块头（回拨）：- 直接 `CALL` 源应使用融合的 `BSTART.STD CALL, <callee>, ra=<label>`。
- 物体拆卸可能仍会显示降低的相邻 `SETRET/C.SETRET`。
- `BSTART.CALL` 和 `SETRET/C.SETRET` 之间不能出现任何指令。
- `SETRET` 定义显式返回块标签（`ra` 目标）；不要假设 return 是词汇上的失败。
- 在当前编译器分支上，手写`ICALL`仍然需要显式
  相邻的`SETRET/C.SETRET`；融合的 `ra=` 源语法尚不可移植
  那里。

非失败返回示例：

```asm
BSTART.STD CALL, callee, ra=.Lresume
... call block ZXTERMEN46QXZ ...
C.BSTOP

... other blocks ...

.Lresume:
C.BSTART.STD
```

固定宽度指导：

- 对于直接源代码级调用，更喜欢融合 `ra=` 语法并让 MC 选择
  降低了宽度。
- 当前编译器 AVS 通道验证融合的 `ra=` 源语法和
  成对的对象级返回地址重定位。
- 将显式 `hl.setret` 视为更广泛的可选形式，需要专用
  在可移植启动代码中依赖后端/MC 证明之前。

不回电形式：

- 没有 `SETRET` 的 `BSTART.CALL` 仅对非返回传输路径有效。
- 在这种形式下，`ra`被保留；任何最终的返回仍必须满足动态目标安全性。

## 4) Linux 系统调用模板

灵犀 Linux 用户空间系统调用 ABI：

- `a7` 中的系统调用号
- `a0..a5` 中的参数
- `acrc 1` 陷阱
- 以`a0`返回（`<0`表示`-errno`）

参考模板：

```asm
C.BSTART.STD
c.movr  <arg0>, ->a0
c.movr  <arg1>, ->a1
c.movr  <arg2>, ->a2
c.movr  <arg3>, ->a3
c.movr  <arg4>, ->a4
c.movr  <arg5>, ->a5
c.movr  <nr>,   ->a7
acrc 1
C.BSTART.STD RET
```

注意事项：

- 保留 `"memory"` 破坏内联 asm 系统调用帮助程序。
- 当 libc API 需要 errno 规范化时使用 `__syscall_ret`。

## 5) setjmp / sigsetjmp / longjmp 不变量灵犀64 jmp ABI 存储集：

- `s0..s8`、`sp`、`ra`（共11个插槽）

规则：

- `setjmp` 准确存储上面的呼叫保留集。
- `longjmp` 准确恢复该设置并返回：
  - `ret = val` 如果 `val != 0`
  - `ret = 1` 如果 `val == 0`（C 标准）
- `sigsetjmp(env, savemask)`：
  - `savemask == 0` 的行为类似于普通 `setjmp`
  - `savemask != 0` 必须通过 `__sigsetjmp_tail` 进行路由，因此掩码保存/恢复在 `siglongjmp` 上是对称的。

## 6) 信号恢复协议(`rt_sigreturn`)

Linux合约：

- 用户空间恢复程序符号 (`__restore_rt`) 必须发出 `rt_sigreturn` 系统调用（`a7=139`、`acrc 1`）。
- `SA_RESTORER` (`0x04000000`) 必须在用户空间信号 ABI 中可用。

内核端参考：

- `${LINUX_ROOT}/arch/linx/kernel/signal.c`

用户空间要求：

- `__restore` / `__restore_rt` 必须是 arch 实现（无操作回退对于完整的 Linux 信号 ABI 无效）。

## 7) 放松和 CFI 政策

抚养平等政策：

- 在手写汇编中保留 ABI 稳定的框架行为：
  - 在调用边界保持 `sp` 16 字节对齐
  - 准确保留/恢复被调用者保存的集合
- 对于故意不通过正常返回路径（`__restore_rt`、`__unmapself`、`exit` 路径）展开的存根，将它们视为无返回终端存根。
- 避免与 ABI 文档不同的合成寄存器保存布局； `setjmp`/上下文保存结构必须与导出的 块头 匹配。

## 8) Linux 上下文切换/陷阱模式进行镜像

主要参考资料：

- `${LINUX_ROOT}/arch/linx/kernel/switch_to.S`
- `${LINUX_ROOT}/arch/linx/kernel/entry.S`
- `${LINUX_ROOT}/arch/linx/kernel/signal.c`

在用户空间 arch asm 中重用的模式：- 被调用者保存状态的保存/恢复顺序（`s0..s8`、`sp`、`ra`）稳定且明确。
- 陷阱/返回流使用 SSR 快照并恢复准确的 中断ed 上下文。
- 信号帧设置/恢复需要用户空间恢复器+对齐的帧。

提交 asm 之前的代理清单：

1. 区块标记合法且平衡吗？
2. 是否返回直接融合的 `CALL` 块头（`..., ra=`），以及是否有任何显式 `SETRET/C.SETRET` 序列仅限于当前的 `ICALL` 或特定于宽度的合约案例？
3. 所有`RET/IND/ICALL`模块是否都通过`setc.tgt`设置目标？
4. ABI 保存/恢复设置是否最小且正确？
5.系统调用路径是否使用`a7 + acrc 1`？
6. 信号恢复器和`SA_RESTORER`是否接线？
7. `longjmp`是否归一化`0 -> 1`？
8. 上下文结构与 Linux UAPI 块头 一致吗？