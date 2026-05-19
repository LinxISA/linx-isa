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

返回调用 块头 在架构上是融合的：

- `BSTART.CALL + C.SETRET` 用于压缩/直接调用 块头。
- `BSTART.CALL + SETRET` 用于非压缩形式。
- 源代码级直接调用程序集应使用融合的 `..., ra=<label>` 语法。
- 降低的目标代码可能仍然将该对拼写为显式相邻
  `setret/c.setret`。
- 对象反汇编仍可能显示降低的 `CALL` 加 `setret/c.setret`
  MC 降低或放松后配对。

返回呼叫的邻接规则：- `SETRET/C.SETRET` 必须紧邻相应的 `BSTART.CALL`。
- 在 call-块头 和 setret 实现之间不能安排任何指令。
- 返回目标是由 `setret` 编码的显式标签，而不是词法失败。

不回电 块头s：

- 不带 `SETRET` 的 `BSTART.CALL` 仅对非返回控制传输路径有效。
- 在这种形式中，`ra` 被保留（没有隐式返回目标重写）。
- 如果控制最终返回并且动态目标不是合法的块启动，则动态目标安全检查必定出错。

所需融合形式：

```asm
BSTART.STD CALL, callee, ra=.Lret
```

非失败退货表格是有效且常见的：

```asm
BSTART.STD CALL, callee, ra=.Ljoin
... call block ZXTERMEN46QXZ ...
C.BSTOP

... unrelated blocks ...

.Ljoin:
C.BSTART.STD
```

设置宽度选择：

- `c.setret`：仅限短距离前进。
- `setret`：仅更大的前进范围。
- `hl.setret`：宽符号范围（向前/向后），但它不属于
  当前编译器 AVS 封闭面。

当前编译器分支注释：

- Bisheng `compiler/llvm` 分支在文本中发出融合的 `ra=` 调用 块头
  汇编并保留对象中成对的返回地址重定位；
- 手写的 `ICALL` 仍然不接受融合的 `ra=` 源语法
  分支，因此显式相邻的 `setret/c.setret` 仍然是可移植源
  在那里形成；
- 不要假设 `hl.setret` 在可移植编译器/运行时流程中可用
  除非该分支的专用 MC/后端测试证明了这一点。

## 4) 间接目标设置规则在任何 `RET`、`IND` 或 `ICALL` 块传输之前，`setc.tgt` 必须在同一块中定义动态目标寄存器源。

不合格序列（`setc.tgt` 缺失，或者返回调用 块头 中 `SETRET` 不相邻）属于违反合约的行为，必须在严格模式下捕获。

## 5) 动态目标安全规则

来自 `RET`/`IND`/`ICALL` 的动态控制流目标必须解析为合法的块起始标记（`BSTART*`、`C.BSTART*`、模板块 与 `FENTRY/FEXIT/FRET.*` 类似）。非块目标一定会出错。

## 6) 跨堆栈验证锚点

对照 Linux 灵犀 实现模式进行交叉检查：

- `${LINUX_ROOT}/arch/linx/kernel/switch_to.S`
- `${LINUX_ROOT}/arch/linx/kernel/entry.S`

这些文件被视为返回目标设置和调用/返回块排序的权威参考行为。