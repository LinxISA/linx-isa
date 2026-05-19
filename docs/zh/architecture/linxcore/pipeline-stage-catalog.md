# 灵犀Core 管道阶段目录

> 此发布的页面镜像了规范的 灵犀Core 源代码
> `rtl/ZXTERMEN45QXZCore/docs/architecture/pipeline-stage-catalog.md`。


本章定义了架构上可见的 灵犀Core 舞台布景和
拥有每个阶段的模块。

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

## 前端阶段

### F0

- 所有者模块：`src/bcc/ifu/f0.py` (`JanusBccIfuF0`)
- 设计角色：PC选择阶段，从多个PC中选择下一个获取PC
  候选 PC 并呈现已注册的 `F0 -> F1` 边界。

### F1

- 所有者模块：`src/bcc/ifu/f1.py` (`JanusBccIfuF1`)
- 设计角色：I-cache查找阶段，拥有标签/数据查找控制和
  缺失/背压产生。
- 架构说明：控制是每个线程的，而当前的物理
  实现跨线程仲裁单个 I-cache 读取端口。

### F2- 所有者模块：`src/bcc/ifu/f2.py` (`JanusBccIfuF2`)
- 设计角色：I-cache数据阶段和ECC检查阶段。
- 仅将 ECC 干净的原始缓存数据和线程/PC 上下文转发到 `F3`。

### F3

- 所有者模块：`src/bcc/ifu/f3.py` (`JanusBccIfuF3`)
- 设计角色：可变长度缝合/组装、静态预测、
  块边界注释和模板识别/扩展控制。

### 国际文凭

- 所有者模块：
  - 完整 IFU 路径：`src/bcc/ifu/f3.py`
  - 导出/调出路径：`src/top/modules/ib.py` (`ZXTERMEN45QXZCoreTopIb`)
- 设计角色：每线程指令缓冲区组提供对齐解码
  组。

### F4

- 所有者模块：`src/bcc/ifu/f4.py` (`JanusBccIfuF4`)
- 设计角色：4 时隙解码窗口生成，每时隙连续 64 位
  从插槽PC查看。

## 解码和预发行阶段

### D1

- 所有者模块：`src/bcc/ooo/dec1.py` (`JanusBccOooDec1`)
- 设计角色：解码、连续组形成和 `RID/BID/LSID`
  分配。

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
  - `src/bcc/backend/dispatch.py` (`ZXTERMEN45QXZCoreDispatchStage`)
  - `src/bcc/backend/issue.py` (`ZXTERMEN45QXZCoreIssueStage`,
    `ZXTERMEN45QXZCoreIqUpdateStage`、`ZXTERMEN45QXZCoreIssuePicker`）
- 设计角色：队列分配、就绪跟踪、最早优先选择以及
  `inflight` 居住地。

## 发出、执行和唤醒阶段

### P1

- 所有者模块：
  - `src/bcc/backend/issue.py`（`ZXTERMEN45QXZCoreIssuePicker`、`ZXTERMEN45QXZCoreIssueStage`）
- 设计角色：IQ挑选阶段选择准备好的、非`inflight`的条目和
  断言 `inflight`。

### I1

- 所有者模块：
  - `src/bcc/backend/issue.py` (`ZXTERMEN45QXZCoreIssueStage`)
  - `src/bcc/backend/prf.py` (`ZXTERMEN45QXZCorePrf`)
- 设计作用：操作数读取规划和射频读取端口仲裁。

### I2

- 所有者模块：
  - `src/bcc/backend/issue.py` (`ZXTERMEN45QXZCoreIssueStage`)
  - `src/bcc/backend/modules/exec_pipe_cluster.py` (`ZXTERMEN45QXZCoreBackendExecPipe`)
- 设计角色：问题确认边界和IQ解除分配点。

### E1

- 所有者模块：
  - `src/bcc/backend/modules/exec_pipe_cluster.py`
  - `src/bcc/iex/iex.py`及系列模块
  - `src/bcc/backend/lsu.py` 用于负载规格唤醒条目
- 设计角色：提升的基线切片中的第一个执行阶段。

### W1

- 所有者模块：
  - `src/bcc/backend/wakeup.py` (`ZXTERMEN45QXZCoreHeadWaitStage`)
  - `src/bcc/backend/commit.py` (`ZXTERMEN45QXZCoreCommitHeadStage`)
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
  - `src/bcc/backend/lsu.py` (`ZXTERMEN45QXZCoreLsuStage`)
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
  - `src/bcc/backend/engine.py` (`ZXTERMEN45QXZCoreCommitSelectStage`)
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

### TMA

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

- 所有者模块：`src/vec/vec.py` (`ZXTERMEN45QXZCoreVec`)
- 设计角色：向量-引擎命令/响应边界。

### 牛

- 所有者模块：`src/tau/tau.py` (`JanusTau`)
- 设计角色：张量/辅助发动机命令/响应边界。

### 布罗布

- 所有者模块：`src/bcc/bctrl/brob.py` (`JanusBccBctrlBrob`)
- 设计角色：BID分配、块完成、块异常捕获，以及
  最旧的区块退休门控。

### XCHK

- 所有者模块：`src/top/modules/xchk.py` (`ZXTERMEN45QXZCoreXchkStage`)
- 设计角色：提交时使用的严格交叉检查/导出相关边界
  验证和 灵犀Trace 注释。

## 发动机阶段

### TMU- 所有者模块：
  - `src/tmu/noc/node.py`
  - `src/tmu/noc/pipe.py`
  - `src/tmu/sram/tilereg.py`
- 设计角色：瓷砖运动和瓷砖状态运输所有权。

### TMA

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

- 所有者模块：`src/vec/vec.py` (`ZXTERMEN45QXZCoreVec`)
- 设计角色：块控制下的可编程SIMT引擎边界。

### 牛

- 所有者模块：`src/tau/tau.py` (`JanusTau`)
- 设计角色：块控制下面向瓦片的引擎边界。