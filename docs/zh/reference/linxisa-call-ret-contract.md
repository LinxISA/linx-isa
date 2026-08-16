# 灵犀指令集 精确 Call/Ret 合约 (linx64)

本文档是编译器、模拟器、运行时和 Linux 交叉检查工作的规范。

## 1) 函数进入/退出形式

正常函数路径：

- 参赛作品必须使用`FENTRY`。
- 退货必须使用`FRET.STK`。
- 规范形式为 `FENTRY ... FRET.STK`。

尾部转移路径：

- 参赛作品仍使用`FENTRY`。
- 尾部出口使用`FEXIT`。
- `FEXIT` 之后的控制传输必须是块合法的（直接或间接块传输）。
- 规范形式为 `FENTRY ... FEXIT`。

当按设计从预恢复 `ra` 消耗返回目标时，`FRET.RA` 有效，但标准 C ABI 返回使用 `FRET.STK`。

## 2) 返回目标语义

- `FRET.STK`：返回目标来自从帧加载的恢复的 `ra` 状态。
- `FRET.RA`：返回目标来自堆栈恢复返回解析之前的 `ra`。
- `BSTART.RET` 块必须包含显式目标设置：
  - `setc.tgt <src>`，其中 `<src>` 解析为 `ra` 以获得正常返回。

所需的 `RET` 块形式：

```asm
C.BSTART.RET
c.setc.tgt ra
C.BSTOP
```

## 3) 调用标头合约

PTO 公共返回调用是一条融合的架构指令：

- `BSTART.CALL <br_label>, <rt_label>, ->ra` 同时编码分支目标和返回目标，并原子写入 `ra`。
- 它不消费相邻的 `SETRET/C.SETRET`，反汇编也不得输出已删除的 `BSTART.STD CALL` 或 `BSTART.FP CALL`。
- `br_label` 与 `rt_label` 是两个独立的 PC-relative 操作数；返回目标不能由词法 fall-through 推导。

正式形式：

```asm
BSTART.CALL callee, .Lret, ->ra
```

非失败退货表格是有效且常见的：

```asm
BSTART.CALL callee, .Ljoin, ->ra

... unrelated blocks ...

.Ljoin:
C.BSTART.STD FALL
```

Linx 额外保留 `L.BSTART.STD CALL, <label>`、`HL.BSTART.FP CALL, <label>` 等长格式 bare call；它们保持 `ra` 不变。若软件显式搭配 `SETRET/C.SETRET`，该指令必须紧邻并位于 bare call 之前；这不是 `BSTART.CALL` 的别名。

## 4) 间接目标设置规则

`RET` 和 `IND` block transfer 必须在同一 block 中用 `setc.tgt` 定义动态目标。

`BSTART.ICALL <rt_label>, ->ra` 不同：它退役活动的 STD/FP block，将该 block 的 `BARG.BPCN` 快照为间接目标，并把显式返回标签写入 `ra`。它不读取 `SETC.TGT`，也不消费独立的 `SETRET`。

目标状态缺失、目标未对齐或长格式 bare-call 组合错误，都必须在产生架构效果前触发异常。

## 5) 动态目标安全规则

来自 `RET`/`IND`/`ICALL` 的动态控制流目标必须解析为合法的块起始标记（`BSTART*`、`C.BSTART*`、模板块 与 `FENTRY/FEXIT/FRET.*` 类似）。非块目标一定会出错。

## 6) 跨堆栈验证锚点

对照 Linux 灵犀 实现模式进行交叉检查：

- `${LINUX_ROOT}/arch/linx/kernel/switch_to.S`
- `${LINUX_ROOT}/arch/linx/kernel/entry.S`

这些文件被视为返回目标设置和调用/返回块排序的权威参考行为。
