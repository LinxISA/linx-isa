# 灵犀Core v0.56 Super标量 启动概述

> 此发布的页面镜像了规范的 灵犀Core 源代码
> `rtl/ZXTERMEN45QXZCore/docs/architecture/overview.md`。


## 范围

本文档是 灵犀Core 下的顶级规范概述
实时 灵犀指令集 `v0.56` 合约。

灵犀Core 此处指定为：

- 灵犀指令集 的规范 super标量 乱序核心，
- 标量、向量、瓷砖和
  加速器支持的块工作，
- 精确退休、恢复、中断、MMU、痕迹可见的拥有者
  执行行为，
- 下游编译器、模拟器、pyCircuit 和测试平台的机器
  工作必须以规范的 `v0.56` 行为为目标。

该规范不是性能愿望清单，也不是历史记录
日志。它定义了实施必须保留的实时合同。

该合同中的每个架构上可见的阶段都必须依附于
命名模块边界。集成 shell 可以组成阶段模块，但它们
不得删除舞台所有权或将现场舞台隐藏在未区分的顶部内
胶水。

## 规范链接

- 基础 ISA 架构合约：`docs/architecture/v0.56-architecture-contract.md`
- 工作负载到引擎模型：`docs/architecture/v0.56-workload-engine-model.md`
- 渲染命令型号：`docs/architecture/v0.56-rendering-command-contract.md`
- 灵犀核心微架构合约：`rtl/ZXTERMEN45QXZCore/docs/architecture/microarchitecture.md`
- 灵犀核心接口合约：`rtl/ZXTERMEN45QXZCore/docs/architecture/interfaces.md`
- 灵犀核心验证矩阵：`rtl/ZXTERMEN45QXZCore/docs/architecture/verification-matrix.md`当措辞出现分歧时，灵犀指令集 架构页面和 灵犀Core
上面列出的合同页是规范的。深入实施说明是
下属。

## 核心定义

灵犀Core 是块有序的异构 super标量 内核。

其定义属性是：

- super标量 前端、调度、问题和提交行为，
- 具有精确架构退役的无序执行，
- 以 `BSTART` 和 `BSTOP` 为架构的块结构控制流
  界碑、
- 通过 `BROB` 和块引擎路径进行 BID 排序的块跟踪，
- 标量、内存、模板和的一种架构恢复模型
  引擎支持的工作，
- 一种用于提交和管道可见性的架构跟踪模型。

灵犀Core 没有为引擎定义第二个隐藏数据包机器。全部
加速器支持的工作必须保持从属于同一架构块
标量 工作时的流、完成模型、刷新规则和可观察性规则。

## 灵犀指令集 中的架构角色

在`v0.56`下，灵犀Core是多工作负载的执行基板
灵犀指令集 型号。- BCC和块结构提供架构控制和提交
  路径。
- `VEC` 是用于并行循环工作的通用可编程 SIMT 引擎。
- `TMA` 仍然通过相同的块模型进行选择，但其内存传输
  由 CSU 子系统拥有，而不是由对等顶级引擎 shell 拥有。
- `CUBE`和`TAU`仍然是通过同一块选择的集成发动机
  模型。
- 引擎支持的工作必须通过 灵犀Core 退出、取消、重定向和跟踪
  规则而不是通过单独的架构域。

该组合规则需要与以下内容保持一致：

- `docs/architecture/v0.56-architecture-contract.md`
- `docs/architecture/v0.56-workload-engine-model.md`
- `docs/architecture/v0.56-rendering-command-contract.md`

## 当前架构闭包切片

当前的架构编写阶段涵盖了升级的前端/解码，
重命名后调度，以及来自 `IFU/F0` 的基线问题/唤醒切片
`W1`。

本次舞台阵容：- `F0`：PC选择阶段；从多个候选 PC 中选择下一个获取 PC
  并呈现已注册的 `F0 -> F1` 边界。
- `F1`：指令缓存查找阶段；面向架构的控制仍然是每个线程的，
  而当前的物理实现仲裁单个 I-cache 读取
  跨线程的端口。
- `F2`：I-cache数据分级和ECC检查；仅转发 ECC 干净的原始缓存
  数据和线程/PC 上下文。
- `F3`：可变长度缝合/组装、静态预测、块边界
  注释和模板识别/扩展控制。
- `IB`：每线程指令缓冲区组提供对齐的解码组。
- `F4`：4 时隙解码窗口生成，具有连续的每时隙 64 位视图。
- `D1`：解码、连续组形成和 `RID/BID/LSID` 分配。
- `D2`：重命名请求/转换阶段和 ROB 可见边界解析。
- `D3`：重命名-uop 锁存点。
- `S1`：重命名后调度准备（路由和就绪查询）。
- `S2`：实际 IQ 条目写入。
- `P1`：IQ 选择阶段。
- `I1`：操作数读取规划和RF读取端口仲裁。
- `I2`：发出确认和 IQ 释放边界。
- `E1`：第一个执行阶段。
- `W1`：基线后期唤醒和解析阶段。这张通行证有意关注建筑舞台所有权和
界面形状。更详细的单元内部执行/旁路拓扑和完整的
提交机制仍然受规范中更广泛的合同管辖
微架构页面，直到后面的切片以相同的样式提升。

## 规格集

灵犀Core 规范分为四个合同页面：

- `overview.md`：范围、角色、文档边界和权限规则。
- `microarchitecture.md`：执行模型，详细的管道规则，恢复，
  内存、BID、`BROB` 和引擎组合语义。
- `interfaces.md`：pyCircuit、提交跟踪、灵犀Trace、块结构和
  跨工具同步合约。
- `verification-matrix.md`：合约 ID、门映射和所需证据。

两个结构章节扩展了这些合同页面，并且是实时的一部分
super标量-核心规格：

- `module-catalog.md`：规范模块系列和顶级组成。
- `pipeline-stage-catalog.md`：每级设计、所有权以及级到模块
  映射。

该目录中的其余文件是实现深入研究。他们可能
扩大机制，但不得削弱或重新定义现行合同。

## 真实来源模型

- Canonical 灵犀Core 合约编写位于 `rtl/ZXTERMEN45QXZCore/docs/architecture/` 中。
- 已发布的超级项目镜像在 `docs/architecture/linxcore/` 中运行。
- `tools/bringup/check_linxcore_arch_contract.py` 验证了规范
  页面和生成的镜像。
- 独立树如`/Users/zhoubot/ZXTERMEN45QXZCore`是开发镜像，
  不是合同权力。

## 所需的关闭目标本规范的实时关闭目标是：

- 灵犀指令集 `v0.56` 架构行为，
- U+S特权行为，
- MMU 和 中断 正确性，
- 双通道重现性（`pin` 和 `external`），
- 严格要求关闭带有证据的物品。

阶段标签仍然可以在操作中使用，但规范本身是
门驱动，而不是日期驱动。

## 非目标

此概述不会冻结：

- 最终频率、面积或功率目标，
- 超出当前实时合约的未来宽度缩放，
- 灵犀指令集 `v0.56` 尚未涵盖的未来发动机添加
  建筑合同，
- 历史性的引导策略不再是实时行为的一部分。