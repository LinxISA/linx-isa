# 灵犀指令集 v0.3 — Sail 形式化审核日志

该日志记录了在实施 v0.3 Sail 模型时提出的“审查决策”和未解决的问题。

格式：

- 每个条目都有：日期、主题、问题、决定、理由和后续行动。
- 尽可能保留技术和参考规范来源。

---

## 2026 年 2 月 24 日 — 开球

主题：逐步 Sail 形式化约 670 个缺失的助记符（根据 `isa/sail/coverage.json`）。

决定：
- 以小的 PR 片段进行。
- 当遇到歧义时，针对每个切片提出一个集中的语义问题。

后续行动：
- 选择第一个切片并确认必须在约定中修复的任何极端情况语义。

---

## 2026-02-25 — SETC.*I 立即移位语义

主题：`SETC.*I` 形式编码隐式 `shamt` 字段，但汇编语法仅打印 `simm/uimm`。

问题：
- strict v0.3 应如何将编码的 `shamt` 解释为 `SETC.*I`？

决定（凯文）：
- **A)** 将其视为立即左移：`imm = (SignExtend(simm) << shamt)`（或 `ZeroExtend(uimm) << shamt`）。

理由：
- 编码明确地将位[11:7]（在32位SETC.*I中）专用于`shamt`，建议采用更广泛的立即编码方案。

后续行动：
- 在 `removed-pre-v056-profile/semantics_conventions.json` 中记录此约定。
- 更新 ISA 手动生成器中 SETC.*I 自动生成的伪代码。
- 实现相应的Sail语义。

---

## 2026-02-25 — CMP/SETC 的 SrcRType 处理受限

主题：`CMP.{EQ,NE,LT,GE,LTU,GEU}` 和 `SETC.{EQ,NE,LT,GE,LTU,GEU}` 汇编语法仅允许 `{.sw,.uw}`，但编码仍携带 2 位 `SrcRType`。

问题：
- 当这些限制形式出现`SrcRType=11`时，strict v0.3应该做什么？决定（凯文）：
- 将 `SrcRType=11` 视为**等同于 `00`（无修饰符）**。

理由：
- 保持严格的配置文件确定性，而不会为遗留流引入额外的非法编码。

后续行动：
- 记录在`srcrtype.restricted_forms`下的`removed-pre-v056-profile/semantics_conventions.json`中。
- 更新受限 CMP/SETC 表单的 Sail 语义以清理 11→00。

---

## 2026-02-25 — 标量 块中的 BRU 控制传输合法性

主题：
- BRU 控制传输指令（`B.*`、`J`、`JR` 和相关直接控制传输形式）在耦合的 标量 块中不是合法的有效负载指令。
- 它们仅在**vec引擎标量通道**上执行；如果在 标量 块中遇到，严格配置文件必须捕获。

决定（凯文）：
- 标量 块中的误用会引发 **ILLEGAL_INST**：`TRAPNUM=4`。

开放详情：
- 是否应填充 `TRAPARG0`（以及使用哪台 PC）仍待确定。

---

## 2026-02-25 — Vec 引擎 标量-lane BRU PC 域

主题：
- 当 BRU 控制传输指令在 vec 引擎 标量 通道上执行时，它们会更新哪个 PC 域？

决定（凯文）：
- 更新**TPC**（块体-本地PC），而不是架构全局PC。

后续行动：
- 定义 `B.*`/`J`/`JR` 相对于 TPC 的立即/标签目标计算（字节与半字缩放）。决定（凯文）：
- PC 相关目标的基础是 **当前指令 TPC**。
- 立即偏移量是**半字缩放**：`target = base + (SignExtend(simm) << 1)`。
- `JR SrcL, label` 从 **vec 引擎 标量 通道 GPR 文件** 读取 `SrcL`（不是 ClockHands `t/u` 队列）。
- `B.EQ/B.NE/B.LT/B.GE/B.LTU/B.GEU` 从**vec 引擎 标量-lane GPR 文件**读取 `SrcL/SrcR`。
- 有符号/无符号比较使用完整的 64 位宽度（LT/GE 有符号，LTU/GEU 无符号）。
- 相等比较 (EQ/NE) 是全 64 位宽度。
- `JR SrcL, label` 还使用半字缩放立即数：`target = SrcL + (SignExtend(simm12) << 1)`。
- `JR` **不**强制 2 字节对齐；奇数目标是允许的，并由正常的获取/对齐错误机制处理。
- 如果生成的 `TPC` 在获取/执行时未对齐，则会报告为 `E_BLOCK(EC_BFETCH)` (TRAPNUM=5)，其中 `TRAPARG0` = 故障 `TPC`。
- `JR` 编码包含 `SrcZero` 字段； strict v0.3 **忽略它**（视为 0）。如果计算出的目标最终为 VA=0，则后续提取将出现故障（块体 提取错误）。
- 如果 `JR` 的目标地址不是有效的 vec-块体 获取位置（块体 之外/未映射/否则不可获取），则报告为 `E_BLOCK(EC_BFETCH)`。
- 没有定义明确的架构 块体 范围边界； “可获取”是在操作上定义的（如果获取失败=> `EC_BFETCH`）。

---

## 2026-02-25 — B.Z / B.NZ 谓词来源

主题：
- `B.Z`/`B.NZ` 无源操作数；它们基于谓词值进行分支。决定（凯文）：
- 他们读取 **谓词寄存器 `p`** （vec 引擎谓词域）并测试它是否全零与非零：
  - `B.Z` 当且仅当 `p == 0`
  - `B.NZ` 当且仅当 `p != 0`

注意事项：
- `B.Z`/`B.NZ` 仅限 vec 引擎（标量 阻止使用 `TRAPNUM=4` 执行陷阱）。
- `p` 到架构 BARG/EBARG 的任何镜像都是 vec-engine/profile 定义的；仅 标量 组件不得采用它。

---

## 2026-02-25 — 浮点最小/最大 NaN 行为

主题：
- `FMAX/FMIN` NaN 处理语义。

决定（凯文）：
- IEEE/ARM 风格的 `maxNum/minNum` 行为：
  - 如果恰好有一个操作数为 NaN：返回非 NaN 操作数
  - 如果两个操作数均为 NaN：返回规范 qNaN
  - 有符号零：当两者都为零时，FMAX 返回 +0；当且仅当任一操作数为 -0 时，FMIN 返回 -0。

---

## 2026-02-25 — CSEL SrcRType 处理

主题：
- `CSEL` 汇编语法允许 `SrcR<.neg>`，但编码包括 2 位 `SrcRType`。

决定（凯文）：
——将`SrcRType=11`视为`.neg`；将所有其他值视为 `00`（无修饰符）。

注意事项：
- 这反映了其他地方使用的“受限 SrcRType”哲学：更喜欢确定性清理而不是新陷阱。

---

## 2026-02-25 — 立即实现（LUI / HL.LUI / HL.LIS / HL.LIU）

主题：
- 为 LUI 和 HL 立即加载表单定义常量物化语义。决定：
- 遵循 RTL 解码约定：
  - `LUI imm20` 实现了 `SignExtend(imm20) << 12`。
  - `HL.LUI imm32` 实现了 `SignExtend(imm32)`（无 `<< 12`）。
  - `HL.LIS simm32` 实现了 `SignExtend(imm32)`。
  - `HL.LIU uimm32` 实现了 `ZeroExtend(imm32)`。

---

## 2026-02-25 — 修复块（非托管修复）

主题：
- 定义非托管修复块的行为以及如何将 异常 路由到 `fixup_label`。

决定（凯文）：
- 非托管修复块**仅**具有显式 `fixup_label` 的 `.SYS` 块：
  - `BSTART.SYS FALL<, fixup_label`
- 如果同步 异常 发生在非托管修复块中：
  - 写入陷阱包络寄存器：`TRAPNO/TRAPARG0/ECSTATE`（EBARG 可选）
    - `TRAPNO.E = 0`（同步）和`TRAPNO.ARGV = 1`
  - 将控制流路由到修复处理程序**而不是 EVBASE**，将其作为 **新块** 输入（try/catch）：
    - `fixup_target = BPC + (SignExtend(fixup_label) << 1)`
    - 下一个块目标PC设置为`fixup_target`
  - 没有发生特权/ACR 切换（保留在当前执行上下文中）
- 当 `ASSERT` 故障发生在非托管修复块内时，它们会参与相同的修复路由。
- `ASSERT_FAIL` 保留 `TRAPNUM=52`。
- `ASSERT`仅在`.SYS`区块中合法；在其他地方它被捕获为 `TRAPNUM=4 ILLEGAL_INST`。
- 全局 异常 启用为 `ECONFIG[3]`（当 0 时：ASSERT 为 NOP）。
- 适用于 `ASSERT_FAIL`、`TRAPNO.CAUSE = 0`。

开放式问题：
- `CAUSE` 是否在 `TRAPNUM` 之外的修复上下文中使用/需要。

决定（凯文）：
- 修复上下文中的 `TRAPARG0` 映射：
  - 对于 `ASSERT_FAIL`：`TRAPARG0 = faulting PC/TPC`
  - 对于其他同步 异常：`TRAPARG0 = faulting VA`（例如，数据/页面错误地址）

---## 2026-02-25 — 预取 (PRF/PRFI)

主题：
- 定义预取/提示指令的架构语义以及它们是否可能出错。

决定（凯文）：
- 预取是一个**无故障提示**：地址转换、权限和对齐错误被抑制（无陷阱）。
- `HL.PRF.A` / `HL.PRFI.UA` 还返回计算出的有效地址：
  - `Rd = EA`

---

## 2026-02-25 — DIV/REM 边缘情况（类似 ARM 的语义）

主题：
- 定义 DIV/REM 系列的除零和有符号溢出的非捕获行为。

决定（凯文）：
- 遵循 ARM 风格的行为（非陷阱，定义的结果）：
  - 如果除数 == 0：
    * DIV/DIVU/DIVW/DIVUW => 商 = 0
    * REM/REMU/REMW/REMUW => 余数 = 股息
  - 如果有符号溢出 (MIN_INT / -1)：
    * DIV/DIVW => 商 = MIN_INT
    * REM/REMW => 余数 = 0
  - 除法向零舍入；余数计算为 `a - q*b`。
- 对于 *W 变体，对于所有 DIVW/DIVUW/REMW/REMUW，写回是从位 31** 符号扩展至 64 位。
- 对于HL DIV/REM 两个目的地表格：`Dst0 = quotient`、`Dst1 = remainder`。
- 对于HL MUL/MULU 两个目的地表格：`Dst0 = low64(full_product)`、`Dst1 = high64(full_product)`。
- 对于 HL MADD/MADDW 两目的地形式：视为 128 位累加器 `acc = (SrcL*SrcR + SrcD)`（有符号乘法/加法），然后是 `Dst0 = low64(acc)`、`Dst1 = high64(acc)`。