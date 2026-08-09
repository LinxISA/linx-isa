# 灵犀Core 管道阶段目录

> 此发布的页面镜像了规范的 灵犀Core 源代码
> `rtl/LinxCore/docs/architecture/pipeline-stage-catalog.md`。


本章定义了架构上可见的 灵犀Core 舞台布景和
拥有每个阶段的模块。

IFU 的规范分解和接口字段见 [`ifu.md`](./ifu.md)。

本文档中的阶段名称与规范的阶段令牌目录一致
按照 `src/common/stage_tokens.py` 和 灵犀Trace 阶段顺序。如果是艺名
在跟踪、比较工具或阶段连接检查中可见，它必须
仍然由真正的所有者模块支持。

## 阶段所有权规则

- 每个架构上可见的阶段都是一个模块。
- 阶段可以实现为专用的顶级阶段模块或实现为
  后端系列内的专用所有者模块，但它必须保留
  明确的结构边界。
- 阶段包装器可以调整接口或导出探针，但它们不得合并
  多个架构阶段变成匿名胶水。
- 启动旁路路径可以取代阶段输入的生成器，但它们可能
  不删除下游逻辑和跟踪工具看到的阶段边界。

## IFU 组织

IFU 由 I-SIDE 与 B-SIDE 两个 decoupled engine 组成。I-SIDE 使用
I-F0..I-F4，B-SIDE 使用 B-F0..B-F4；两条流水独立反压、不锁步。

### I-F0

- 接受/选择 PC，分配 request/STID/epoch 身份；
- 寄存请求并向 B-SIDE 发送相关联的预测请求。

### I-F1

- 对同一 PC 和请求身份并行启动 ITLB 与 L1I。

### I-F2

- 汇合 ITLB 与 L1I 状态；
- ITLB miss 产生 I-SIDE inner flush 并清除对应 STID/epoch 的年轻
  I-SIDE 工作；
- L1I miss 保留请求身份并进入 refill。

### I-F3

- 保存一个 cacheline、ECC/refill、byte cursor 和跨 line carry；
- 向 I-F4 提供有序字节流。

### I-F4

- 是真实第 4 级，与 Instruction Buffer 独立；
- 判断 2/4/6/8-byte 长度，拼成完整指令；
- 只识别 `BSTART`/`BSTOP` boundary；
- 零扩展成固定 64-bit `insn64` 并写 Instruction Buffer。

### Instruction Buffer

- 位于 I-F4 与 D1 之间，按 STID 分区；
- 保存 PC、长度、`insn64`、boundary、fault、request/checkpoint 和
  prediction metadata；
- 每周期向 D1 提供最多四条连续 64-bit 指令。

### B-F0

- L0/NLP next-line prediction；
- 分配投机 prediction checkpoint 并保存 GHR/GHRQ 快照。

### B-F1

- uBTB 类型/目标查询；
- 投机 RAS push/pop/read。

### B-F2

- PBTB/BTB 类型/目标查询；
- BIM 基础方向预测。

### B-F3

- short/medium-history TAGE 查询；
- 启动 IBTB 间接目标查询。

### B-F4

- 基于匹配的 I-F4 boundary metadata 运行 static predictor，并汇合
  long-history TAGE、IBTB、loop predictor/buffer；
- 完成最终预测仲裁；
- provider rank 为
  `B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential`；
- B-F4 内 exact RAS return 或 high-confidence IBTB 赢得对应 target；
  direction rank 为 `loop > long-TAGE > short-TAGE > BIM > static`，
  direct target 由 BTB 提供。

backend restart 优先于所有 provider，但属于 typed recovery source，不是
prediction provider。B-SIDE 后级若纠正已经驱动取指的预测，
inner-flush I-SIDE 并重启 I-F0；B-F4 是最后一个 prediction-driven inner
flush 点。其 final record 随每个 valid D1 lane 传递；post-B-F4
Dispatch/BRU mismatch 进入 BRU flush/recover 并发布 frontend restart。
B-SIDE 不拥有 ITLB、L1I、refill、predecode 或 Instruction Buffer。

## 解码和预发行阶段

### D1

- 所有者模块：`src/bcc/ooo/dec1.py` (`JanusBccOooDec1`)
- 设计角色：读取四条 64-bit Instruction Buffer entry，首次完成完整
  opcode/operand/immediate/异常/split-fuse 译码并形成连续组。

### D2

- 所有者模块：`src/bcc/ooo/dec2.py` (`JanusBccOooDec2`)
- 设计角色：重命名请求/翻译阶段和ROB可见边界
  分辨率。
- `BSTART` 和 `BSTOP` 在此变得结构可见。

### D3

- 所有者模块：`src/bcc/ooo/ren.py` (`JanusBccOooRen`)
- 设计作用：重命名-uop锁存点，携带已解析的后端标签形式。

### S1

- 所有者模块：`src/bcc/ooo/s1.py` (`JanusBccOooS1`)
- 设计角色：重命名后调度准备、执行类路由以及
  就绪状态查询。

### S2

- 所有者模块：`src/bcc/ooo/s2.py` (`JanusBccOooS2`)
- 设计作用：将实际IQ条目写入选定的物理队列。

### 智商- 所有者模块：
  - `src/bcc/backend/dispatch.py` (`LinxCoreDispatchStage`)
  - `src/bcc/backend/issue.py` (`LinxCoreIssueStage`,
    `LinxCoreIqUpdateStage`、`LinxCoreIssuePicker`）
- 设计角色：队列分配、就绪跟踪、最早优先选择以及
  `inflight` 居住地。

## 发出、执行和唤醒阶段

### P1

- 所有者模块：
  - `src/bcc/backend/issue.py`（`LinxCoreIssuePicker`、`LinxCoreIssueStage`）
- 设计角色：IQ挑选阶段选择准备好的、非`inflight`的条目和
  断言 `inflight`。

### I1

- 所有者模块：
  - `src/bcc/backend/issue.py` (`LinxCoreIssueStage`)
  - `src/bcc/backend/prf.py` (`LinxCorePrf`)
- 设计作用：操作数读取规划和射频读取端口仲裁。

### I2

- 所有者模块：
  - `src/bcc/backend/issue.py` (`LinxCoreIssueStage`)
  - `src/bcc/backend/modules/exec_pipe_cluster.py` (`LinxCoreBackendExecPipe`)
- 设计角色：问题确认边界和IQ解除分配点。

### E1

- 所有者模块：
  - `src/bcc/backend/modules/exec_pipe_cluster.py`
  - `src/bcc/iex/iex.py`及系列模块
  - `src/bcc/backend/lsu.py` 用于负载规格唤醒条目
- 设计角色：提升的基线切片中的第一个执行阶段。

### W1

- 所有者模块：
  - `src/bcc/backend/wakeup.py` (`LinxCoreHeadWaitStage`)
  - `src/bcc/backend/commit.py` (`LinxCoreCommitHeadStage`)
- 设计角色：基线后期唤醒和解析阶段。

## 稍后的执行和内存阶段

### E2

- 所有者模块：
  - `src/bcc/backend/modules/exec_pipe_cluster.py`
  - `src/bcc/iex/iex_alu.py`、`iex_bru.py`、`iex_agu.py`、`iex_fsu.py`、
    `iex_std.py`
- 设计作用：后来的标量执行阶段被多周期管道使用。

### E3

- 所有者模块：
  - `src/bcc/backend/modules/exec_pipe_cluster.py`
  - `src/bcc/backend/lsu.py`
- 设计角色：多周期标量工作和LSU使用的后期执行阶段
  进展。

### E4- 所有者模块：
  - `src/bcc/backend/lsu.py` (`LinxCoreLsuStage`)
  - `src/bcc/lsu/l1d.py`、`src/bcc/lsu/mdb.py`
- 设计角色：加载数据返回可见性、漏检和转发
  `E4 -> consumer-I2`使用的点。

### W2

- 所有者模块：
  - `src/bcc/backend/modules/commit_trace_stage.py`
  - `src/bcc/backend/modules/macro_trace_prep_stage.py`
- 设计角色：后期写回/跟踪准备阶段。一定不能是
  由仅提交簿记合成。

## ROB、提交和重定向阶段

### 抢

- 所有者模块：
  - `src/bcc/ooo/rob.py` (`JanusBccOooRob`)
  - `src/bcc/backend/rob.py`
  - `src/bcc/backend/modules/rob_bank.py`
- 设计角色：精准报废排序、完成情况跟踪、ROB端
  元数据所有权。

### CMT

- 所有者模块：
  - `src/bcc/backend/commit.py`
  - `src/bcc/backend/engine.py` (`LinxCoreCommitSelectStage`)
  - `src/bcc/backend/modules/commit_slot_step.py`
- 设计角色：有序的架构提交、块可见的退休以及
  提交有效负载生成。

### FLS

- 所有者模块：
  - `src/bcc/ooo/flush_ctrl.py`
  - `src/bcc/backend/modules/recovery_checks.py`
- 设计角色：架构重定向、重播和刷新所有权。

## 路易斯安那州立大学舞台家族

### LIQ

- 所有者模块：`src/bcc/lsu/liq.py` (`JanusBccLsuLiq`)
- 设计角色：负载发出队列排序和合格负载选择。

### 总部

- 所有者模块：`src/bcc/lsu/lhq.py` (`JanusBccLsuLhq`)
- 设计角色：飞行中负载的命中/返回跟踪。

### STQ

- 所有者模块：`src/bcc/lsu/stq.py` (`JanusBccLsuStq`)
- 设计角色：推测存储排序、转发可见性和可刷新
  存储状态。

### SCB

- 所有者模块：`src/bcc/lsu/scb.py` (`JanusBccLsuScb`)
- 设计角色：承诺存储合并和下游排水管理。

### MDB

- 所有者模块：`src/bcc/lsu/mdb.py` (`JanusBccLsuMdb`)
- 设计角色：用于加载未命中处理的未命中/数据缓冲区所有权。

### L1D- 所有者模块：`src/bcc/lsu/l1d.py` (`JanusBccLsuL1D`)
- 设计作用：数据缓存端接口边界。

## 块控制阶段

### BISQ

- 所有者模块：`src/bcc/bctrl/bisq.py` (`JanusBccBctrlBisq`)
- 设计作用：块发布队列所有权和携带BID的入队状态。

### BCTRL

- 所有者模块：`src/bcc/bctrl/bctrl.py` (`JanusBccBctrl`)
- 设计角色：块命令路由、引擎命令启动和响应路径
  协调。

### TMU

- 所有者模块：`src/tmu/noc/node.py` (`JanusTmuNocNode`)
- 设计角色：块控制使用的平铺网络问题/响应边界
  命令运输。

### TLSU

- 所有者模块：
  - `src/csu/subsystem.py` (`JanusCsuSubsystem`)
  - `src/csu/tma_cmd_frontend.py` (`JanusCsuTmaCmdFrontend`)
  - `src/csu/tma_ctx_tracker.py` (`JanusCsuTmaCtxTracker`)
  - `src/csu/tma_l2_client.py` (`JanusCsuTmaL2Client`)
- 设计角色：平铺矩阵命令/响应边界仍然是块可见的，但是
  南向传输属于 CSU 子系统内部。

### 立方体

- 所有者模块：`src/cube/cube.py` (`JanusCube`)
- 设计角色：立方体引擎命令/响应边界。

### 血管内皮细胞

- 所有者模块：`src/vec/vec.py` (`LinxCoreVec`)
- 设计角色：向量-引擎命令/响应边界。

### 牛

- 所有者模块：`src/tau/tau.py` (`JanusTau`)
- 设计角色：张量/辅助发动机命令/响应边界。

### 布罗布

- 所有者模块：`src/bcc/bctrl/brob.py` (`JanusBccBctrlBrob`)
- 设计角色：BID分配、块完成、块异常捕获，以及
  最旧的区块退休门控。

### XCHK

- 所有者模块：`src/top/modules/xchk.py` (`LinxCoreXchkStage`)
- 设计角色：提交时使用的严格交叉检查/导出相关边界
  验证和 灵犀Trace 注释。

## 发动机阶段

### TMU- 所有者模块：
  - `src/tmu/noc/node.py`
  - `src/tmu/noc/pipe.py`
  - `src/tmu/sram/tilereg.py`
- 设计角色：瓷砖运动和瓷砖状态运输所有权。

### TLSU

- 所有者模块：
  - `src/csu/subsystem.py`
  - `src/csu/tma_cmd_frontend.py`
  - `src/csu/tma_ctx_tracker.py`
  - `src/csu/tma_l2_client.py`
- 设计角色：块控制下的矩阵/瓦片加速器执行边界
  与 CSU 拥有的 L2 传输和完成聚合。

### 立方体

- 所有者模块：`src/cube/cube.py` (`JanusCube`)
- 设计角色：块控制下的立方体引擎执行边界。

### 血管内皮细胞

- 所有者模块：`src/vec/vec.py` (`LinxCoreVec`)
- 设计角色：块控制下的可编程SIMT引擎边界。

### 牛

- 所有者模块：`src/tau/tau.py` (`JanusTau`)
- 设计角色：块控制下面向瓦片的引擎边界。
