# 灵犀 跨栈技巧总结

本笔记总结了跨 Linux、LLVM、QEMU 和 libc 堆栈的 灵犀 调用/ret 和 libc 启动的实用技能和复习重点。

## Linux

- 验证内核对象中发出的调用/ret 模式（`entry.o`、`switch_to.o`、`panic.o`）。
- 保持返回/间接路径明确（`BSTART.RET/IND` + `setc.tgt`）。
- 交叉检查：
  - `${LINUX_ROOT}/arch/linx/kernel/entry.S`
  - `${LINUX_ROOT}/arch/linx/kernel/switch_to.S`
- 带 `tools/ci/check_linx_callret_crossstack.sh` 的门。

## LLVM

- 强制执行融合直接调用源 块头 (`BSTART.CALL ..., ra=...`) 和
  降低了对象中的 call-块头 邻接性。
- 在 `FEXIT` 尾部转移路径上保持必须尾部降低； `FRET.STK` 上的非尾部。
- 保留稳定的 MC/disasm 融合视图 (`CALL ..., ra=...`) 和迁移合法性。
- 添加照明覆盖范围：
  - 正常调用/返回形状
  - 须尾尾部转移形状
  - call-块头 邻接约束

## QEMU

- 将严格的合同违规行为视为确定性陷阱：
  - 缺少setret
  - 无效的 setret 序列
  - `RET/IND/ICALL` 缺少 `setc.tgt`
- 在传输之前验证动态目标作为合法区块的启动。
- 跨 TB 边界保留 call-块头 合约（翻译器状态不得丢失）。
- 支持所有 setret 宽度（`c.setret`、`setret`、`hl.setret` 别名路径）。

## 穆斯林

- 保持 linx64 arch ABI 具体（没有 riscv 派生的占位符布局）。
- 将 `clone`、`sigsetjmp`、恢复器、`__unmapself`、ldso 路径的存根替换为 arch asm。
- 保持搬迁合同与规范的 `R_LINX_*` 保持一致。
- 使用 `avs/qemu/run_musl_smoke.py` 控制静态/共享运行时行为。

## glibc- 保持系统调用/陷阱机制与 灵犀 合约（`acrc 1` 路径）保持一致。
- 保持重定位编号和 setjmp/signal/ucontext 契约与 Linux UAPI 和 musl 保持一致。
- 避免与 musl/QEMU 期望不同的后备重定位/填充行为。

## 共同审查清单

1. 调用块头s：返回直接调用源使用融合的`..., ra=...`，并且
   降低的物体在存在时保持相邻的固定形状。
2.返回/间接：每个`RET/IND/ICALL`路径都有显式的`setc.tgt`。
3. 目标：动态目标是块开始。
4.尾部调用：`FENTRY + FEXIT`仅在musttail/tail-transfer路径上。
5.运行时门：仅编译器+独立QEMU+Linux+musl全部通过。