# 灵犀核心模块目录

> 此发布的页面镜像了规范的 灵犀Core 源代码
> `rtl/ZXTERMEN45QXZCore/docs/architecture/module-catalog.md`。


本章定义了现场直播下 灵犀Core 的规范模块结构
`v0.56` 超级标量 合约。

它冻结了哪些模块系列拥有架构行为，哪些文件是
这些行为的规范所有者，以及这些模块如何组成
全核心。这里的模块所有权是规范的；辅助实用程序不会替换
舞台所有者。

## 结构规则

- 每个架构上可见的阶段、队列、块控制所有者和引擎
  边界必须有一个命名的模块所有者。
- 顶级包装器可以组成这些所有者、导出探针或适应
  测试平台集成，但他们不得重新定义架构所有权。
- 仅连接顶壳是 `src/linxcore_top.py` 的目标结构，
  `src/top/top.py`和`src/top/modules/export_core.py`；阶段本地状态和
  所有权逻辑属于专用子模块。
- `src/common/` 中的共享实用程序文件可以定义类型、解码器、元数据、
  或帮手；它们不能替代舞台模块。
- 跟踪可见性必须来自真实所有者模块或专用探针
  模块，而不是父级重建。

## 顶级组合模块

### `src/linxcore_top.py`

- 定义规范导出的顶级模块名称 `linxcore_top`。
- 附加提交、块和管道视图使用的顶级探针模块
  可观察性。
- 拥有顶级配置参数，例如内存大小和获取包
  宽度别名。

### `src/top/modules/export_core.py`- 定义 `ZXTERMEN45QXZCoreTopExport`，启动/导出集成 shell。
- 组成后端、内存、探针导出、块控制、LSU 和引擎
  适配器。
- 拥有由锁步和跟踪通道使用的主机馈送指令缓冲区路径。
- 当 IFU 源在启动时被旁路时，它仍然保留相同的内容
  解码和跟踪工具看到的下游阶段所有权模型。

### `src/top/top.py`

- 定义 `ZXTERMEN45QXZCoreTop`，具有显式 IFU 的完整顶级组合
  舞台链。
- 实例化 IFU 模块 `F0` 到 `F4`、后端、块控制
  路径、LSU、内存和引擎适配器。
- 用作级与级接线名称的参考组合。
- 必须收敛到仅连接的组合外壳作为阶段本地跟踪
  并且教养逻辑被强加给专心致志的孩子。

### `src/mem/mem2r1w.py` 和 `src/mem/byte_mem_2r1w.py`

- 拥有指令和数据路径使用的规范内存宏包装器。
- 保留启动和使用的分割指令/数据访问模型
  跟踪验证流程。

## 共享规范和元数据模块

### 配置和结构元数据

- `src/common/config.py`
- `src/common/params.py`
- `src/common/module_specs.py`
- `src/common/meta_specs.py`

这些文件定义结构参数、类型化接口元数据以及
规范的构建时配置规则。

### ISA 和解码所有权

- `src/common/isa.py`
- `src/common/decode.py`
- `src/common/decode16.py`
- `src/common/decode32.py`
- `src/common/decode48.py`
- `src/common/decode64.py`
- `src/common/decode_f4.py`

这些文件定义了操作码的身份和解码行为
前端/解码阶段。

### 架构元数据和跟踪元数据- `src/common/stage_tokens.py`
- `src/common/types.py`
- `src/common/interfaces.py`
- `src/common/exec_uop.py`
- `src/common/uid_allocator.py`

这些文件定义了阶段令牌目录、通用信号包、uop
阶段、区块和跟踪合约所需的元数据和 UID 分配。

## 前端和获取模块

### `src/bcc/ifu/f0.py`

- 拥有 `F0` 边界。
- 从引导、重定向或顺序候选中选择下一个获取 PC。
- 呈现已注册的 `F0 -> F1` 边界。

### `src/bcc/ifu/f1.py`

- 拥有 `F1` 边界。
- 保留 I-cache 查找/标签检查控制和前端未命中/背压
  一代。
- 保留面向体系结构的每线程获取控制模型，即使
  当前物理 I-cache 读取路径是单端口的。

### `src/bcc/ifu/icache.py`

- 拥有 IFU 路径使用的获取高速缓存访问模块。
- 为下游阶段生成捆绑、命中/未命中和面向重新填充的元数据。

### `src/bcc/ifu/f2.py`

- 拥有 `F2` 边界。
- 在可变长度组装之前暂存原始缓存读取数据和 ECC 状态。

### `src/bcc/ifu/ctrl.py`

- 拥有 IFU 控制元数据，例如检查点流和刷新交互。
- 协调前端控制决策，无需重新定义阶段
  所有权。

### `src/bcc/ifu/f3.py`

- 拥有 `F3` 边界和完整的 IFU 指令缓冲区入口行为。
- 执行可变长度拼接/组装、静态预测、块边界
  指令缓冲区传递之前的注释和模板流控制。

### `src/top/modules/ib.py`- 拥有 `ZXTERMEN45QXZCoreTopIb`，这是由主机提供的指令缓冲区模块
  导出外壳。
- 保留相同的下游指令缓冲区所有权模型
  QEMU/主机注入取代了启动通道中的本机 IFU 源。

### `src/top/modules/xchk.py`

- 拥有明确的 `XCHK` 验证/导出边界。
- 将交叉检查相关性保留为命名模块边界而不是
  用匿名顶级胶水合成它。

### `src/top/modules/export_store_drain.py`

- 拥有导出 shell 使用的 SCB/D-cache-stub store-drain 助手。
- 将本地存储耗尽状态和辅助实例拉出
  `export_core.py` 因此顶壳仍然更接近纯粹的成分。

### `src/bcc/ifu/f4.py`

- 拥有 `F4` 边界。
- 呈现架构解码合约使用的 4 时隙解码窗口。

### `src/bcc/frontend/`

- 包含辅助前端支持模块，例如`frontend.py`、`bpu.py`、
  `ftq.py`、`ibuffer.py` 和 `ifetch.py`。
- 这些文件可能支持替代分解或实验，但是
  他们不会取代上面的规范舞台所有者。

## 解码、重命名和重命名后调度模块

### `src/bcc/ooo/dec1.py`

- 拥有`D1`。
- 将 `F4` 时隙窗口解码为 uop 候选并分配 `RID`、`BID`、
  和`LSID`。

### `src/bcc/ooo/dec2.py`

- 拥有`D2`。
- 执行重命名请求/翻译准备并解析 ROB 可见
  `BSTART` 和 `BSTOP` 的边界元数据。

### `src/bcc/ooo/ren.py`- 拥有 `D3`。
- 将架构操作数映射为重命名/标记的操作数形式并用作
  重命名的 uop 锁存器边界。

### `src/bcc/ooo/s1.py`

- 拥有 `S1`。
- 执行重命名后调度准备、执行类路由和准备
  针对非规范就绪表进行查询。

### `src/bcc/ooo/s2.py`

- 拥有 `S2`。
- 将实际 IQ 条目写入选定的物理 IQ。

### `src/bcc/ooo/renu.py`

- 拥有重命名的调度路径使用的重命名状态支持结构。
- 供应重命名簿记必须与`D3`保持一致
  合同。

### `src/bcc/ooo/pc_buffer.py`

- 拥有分支恢复和合法-BSTART使用的PC缓冲区元数据存储
  检查。

### `src/bcc/ooo/flush_ctrl.py`

- 拥有显式刷新和重定向控制边界。
- 提供架构刷新所有者而不是隐藏重定向策略
  在不相关的模块内。

### `src/bcc/ooo/rob.py`

- 拥有面向阶段映射路径的 Janus/BCC ROB 阶段边界。
- 在阶段分解中提供 ROB 可见状态，无需替换
  规范后端 ROB 所有者。

## 后端编排模块

### `src/bcc/backend/backend.py`

- 定义 `ZXTERMEN45QXZCoreBackend`，规范的后端包装器。
- 将实时后端组合委托给跟踪导出支持的核心构建。

### `src/bcc/backend/decode.py`

- 定义 `ZXTERMEN45QXZCoreDecodeStage`。
- 拥有功能管道的后端本地解码打包。

### `src/bcc/backend/rename.py`

- 定义 `ZXTERMEN45QXZCoreRenameStage` 和 `ZXTERMEN45QXZCoreCommitRenameStage`。
- 拥有重命名分配和提交端重命名发布。

### `src/bcc/backend/dispatch.py`- 定义`ZXTERMEN45QXZCoreDispatchStage`。
- 拥有从解码/重命名到后端的 ROB、IQ 和 LSU 分配切换
  执行机。

### `src/bcc/backend/issue.py`

- 定义 `ZXTERMEN45QXZCoreIssuePicker`、`ZXTERMEN45QXZCoreIssueStage` 和
  `ZXTERMEN45QXZCoreIqUpdateStage`。
- 拥有 IQ 就绪、最早优先选择、`inflight` 保留和发布
  合法性。

### `src/bcc/backend/prf.py`

- 定义`ZXTERMEN45QXZCorePrf`。
- 拥有物理寄存器文件状态和问题使用的读/写可见性
  写回。

### `src/bcc/backend/lsu.py`

- 定义`ZXTERMEN45QXZCoreLsuStage`。
- 拥有后端 LSU 阶段行为及其与问题/提交的集成。

### `src/bcc/backend/rob.py`

- 定义ROB阶段模块，例如`ZXTERMEN45QXZCoreRobCommitReadStage`，
  `ZXTERMEN45QXZCoreRobCtrlStage` 和 `ZXTERMEN45QXZCoreRobEntryUpdateStage`。
- 拥有精确的退休簿记和ROB端查询/更新边界。

### `src/bcc/backend/commit.py`

- 定义 `ZXTERMEN45QXZCoreCommitHeadStage` 和 `ZXTERMEN45QXZCoreCommitCtrlStage`。
- 拥有架构提交选择和有序退出端控制。

### `src/bcc/backend/wakeup.py`

- 定义 `ZXTERMEN45QXZCoreHeadWaitStage`。
- 拥有唤醒、头部等待和重放端可见性约束。

### `src/bcc/backend/engine.py`

- 定义`ZXTERMEN45QXZCoreCommitSelectStage`和规范的后端组成
  帮手。
- 拥有提交端选择、块状态更新和执行系列
  组成胶水。

### `src/bcc/backend/code_template_unit.py`

- 定义 `CodeTemplateUnit`。
- 拥有模板微指令生成和模板端跟踪标识。

### `src/bcc/backend/modules/`- 包含重点后端模块系列，例如块结构桥接、
  提交跟踪导出、ROB 银行、PC 缓冲区阶段、恢复验证、
  内存读取仲裁、执行管道集群和存储缓冲区阶段。
- 这些是后端行为的规范子模块所有者，而不是可选的调试
  包装纸。

## 整数和 标量 执行模块

### `src/bcc/iex/iex.py`

- 拥有顶级整数执行组合边界。

### `src/bcc/iex/iex_alu.py`

- 拥有 ALU 执行行为。

### `src/bcc/iex/iex_bru.py`

- 拥有分支条件和分支恢复执行行为。

### `src/bcc/iex/iex_agu.py`

- 拥有 LSU 绑定操作的地址生成执行行为。

### `src/bcc/iex/iex_std.py`

- 拥有存储数据准备行为。

### `src/bcc/iex/iex_fsu.py`

- 拥有其他未涵盖的 标量 功能/系统执行行为
  整数执行单元。

## LSU 和内存排序模块

### `src/bcc/lsu/lsu.py`

- 拥有 LSU 组成边界。
- 集成队列、缓存端、存储消耗和内存数据流所有者。

### `src/bcc/lsu/liq.py`

- 拥有 `LIQ`，加载发出队列。

### `src/bcc/lsu/lhq.py`

- 拥有 `LHQ`，加载命中/加载返回队列状态。

### `src/bcc/lsu/stq.py`

- 拥有 `STQ`，推测存储队列。

### `src/bcc/lsu/scb.py`

- 拥有 `SCB`，提交存储合并缓冲区。

### `src/bcc/lsu/mdb.py`

- 拥有 `MDB`，未命中/数据缓冲区跟踪边界。

### `src/bcc/lsu/l1d.py`

- 拥有 `L1D`，数据缓存端接口边界。

### `src/bcc/lsu/store_pack.py`

- 拥有用于承诺存储路径的存储有效负载行打包。

### `src/bcc/lsu/lsu_store_drain.py`- 拥有为 D 缓存端路径提供数据的提交存储排出管道。

### `src/bcc/lsu/dcache_stub.py`

- 拥有当前启动流使用的功能 D 缓存存根。

## 块控制模块

### `src/bcc/bctrl/bisq.py`

- 拥有`BISQ`，块发布队列。

### `src/bcc/bctrl/bctrl.py`

- 拥有 `BCTRL`，块命令/控制路由边界。

### `src/bcc/bctrl/brenu.py`

- 拥有块端重命名和资源元数据处理。

### `src/bcc/bctrl/brob.py`

- 拥有`BROB`，包括`BID`分配、区块完成、区块异常
  捕获和最旧的块退休门控。

### `src/bcc/block_struct/`

- 包含针对 ROB/BROB 行为的重点块结构模型和测试。
- 该包支持块结构验证并且必须保持一致
  与实时区块控制合约。

## 发动机和加速器模块

### `src/csu/subsystem.py`

- 拥有统一的CSU父子系统，吸收IFU充值流量并
  CSU-内部 TMA 传输所有权。

### `src/csu/{tma_cmd_frontend,tma_ctx_tracker,tma_l2_client,client_arb}.py`

- 拥有 CSU 内部 TMA 命令入口、上下文跟踪、L2 客户端
  转换和再填充与 TMA 仲裁边界。

### `src/vec/vec.py`

- 拥有 `VEC` 发动机边界。

### `src/tma/tma.py`

- 保留独立 TMA 单元测试的独立兼容性外观。
- Janus顶层整合不再将其视为规范的南向
  运输业主。

### `src/cube/cube.py`

- 拥有 `CUBE` 发动机边界。

### `src/tau/tau.py`

- 拥有 `TAU` 发动机边界。

### `src/tmu/noc/node.py` 和 `src/tmu/noc/pipe.py`

- 拥有 TMU NoC 传输边界。

### `src/tmu/sram/tilereg.py`- 拥有面向瓦片的引擎使用的瓦片寄存器 SRAM 状态。

## 可观察性和导出模块

### `src/probes/pipeview_probe.py`

- 拥有管道阶段可观测性导出。

### `src/probes/block_probe.py`

- 拥有区块生命周期可观察性导出。

### `src/probes/commit_probe.py`

- 拥有提交流可观察性导出。

可观察性模块必须消耗真实所有者状态。他们绝不能发明一种
并行架构管道。