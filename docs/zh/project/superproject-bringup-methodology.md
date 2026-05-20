# 灵犀指令集 超级项目启动方法论

本文档解释了`linx-isa`超级项目如何管理许多活跃的
子模块，而无需将启动转变为临时集成工作。它既是一个
方法说明以及针对人员和代理的操作手册。

简短的版本是：

- 超级项目是协调平面，而不是实施转储。
- 叶子模块首先发生变化；超级项目仅在模块拥有后重新启动
  大门是绿色的。
- 默认情况下，启动是严格的：没有隐式通行证，没有无证弃权，
  没有叙述的状态。
- 测试和门是合同。 Markdown 是机器可读的视图
  证据，但不能替代它。

## 超级项目拥有什么

超级项目拥有跨存储库协调，而不是叶子实现细节。
它的工作是使整个堆栈可重复、可归因和可测试。

规范职责：

- 保持根 `.gitmodules` 中子模块拓扑正确。
- 定义允许的路径和规范的工作位置。
- 维护`docs/`和`isa/`中的架构和启动合约。
- 从 `tools/regression/` 和 `tools/bringup/` 运行跨回购关闭门。
- 在`docs/bringup/gates/`下发布规范证据。
- 通过分配门所有权
  `docs/bringup/agent_runs/manifest.yaml` 和清单文件。
- 在 `docs/bringup/agent_runs/waivers.yaml` 中记录明确的弃权。

超级项目不应成为 `llvm`、`qemu`、`linux` 的卷影副本，
`glibc`、`musl`、`ZXTERMEN45QXZCore` 或 `pyCircuit`。如果 bug 存在于叶模块中，
首先在该模块中修复它，然后重新固定超级项目。

## 核心设计原则### 规范优先

架构意图存在于 `isa/` 和 `docs/architecture/` 中。每次提出
决策应追溯到稳定的合同，而不是本地解决方法。

### 子模块优先

生态系统存储库仍然是独立的存储库，具有独立的所有权和门户
表面。超级项目记录已知良好的 SHA 并验证它们是否有效
在一起。

### 单一规范工作区

使用一种基于超级项目的规范结账。避免并行临时
相同的引导车道上的树木。跨回购证据必须指向
相同的工作区布局。

### 测试驱动的启动

启动工作从失败的合同、测试或门开始。一个特点不是
“成长”是因为代码存在；当右门通过时就会出现
与捕获的证据。

### 默认严格

必须通过必需的、非豁免的大门。豁免是阶段性的、明确的、
有时间限制，并经过机器检查。不允许静音 异常。

### 证据胜于叙述

事实来源是机器可读的门报告及其附加日志，
工件和 SHA 清单。人类可读的状态页面是生成的视图。

## 四个控制平面

超级项目保持易于管理，因为它分离了四个关注点。

### 拓扑平面

这控制了工作的存放位置以及存储库的链接方式。

关键文件：

- `AGENTS.md`
- `docs/project/navigation.md`
- `docs/project/repository-flow.md`
- `.gitmodules`
- `tools/ci/check_repo_layout.sh`

规则：- 没有随机的顶级目录。
- 不再恢复已弃用的路径，例如 `tests/`、`examples/` 或
  `compiler/linx-llvm`。
- 灵犀 生态系统链接保留在根 `.gitmodules` 中，而不是在叶存储库中。

### 所有权飞机

这控制谁拥有每个门以及代理可以接触哪些模块。

关键文件：

- `docs/bringup/agent_runs/manifest.yaml`
- `docs/bringup/agent_runs/checklists/*.md`
- `docs/bringup/agent_runs/waivers.yaml`

规则：

- 每个必需的门钥匙都映射到清单所有者。
- 代理声明显式模块范围。
- 跨模块所有权保留给批准的集成角色。
- 规范技能是协调契约的一部分。

### 验证平面

这控制了在将更改视为集成之前必须通过的内容。

关键切入点：

- `tools/regression/strict_cross_repo.sh`
- `tools/bringup/check_multi_agent_gates.py`
- `tools/bringup/check_gate_consistency.py`
- `tools/bringup/check_avs_contract.py`
- `tools/bringup/check_avs_profile_closure.py`
- `tools/bringup/run_runtime_convergence.sh`

规则：

- 静态结构必须在运行时闭包被信任之前进行验证。
- 运行时关闭必须是特定于通道的并且由运行 ID 支持。
- 严格的发布封闭需要 `pin` 和 `external` 通道。

### 证据平面

这控制如何记录运行以及如何拒绝陈旧或部分数据。

关键工件：

- `docs/bringup/gates/latest.json`
- `docs/bringup/GATE_STATUS.md`
- `docs/bringup/gates/logs/<run-id>/<lane>/...`
- `docs/bringup/agent_runs/skills_evolution/latest.json`

规则：

- 每次运行都会记录命令、通道、时间戳、结果和证据。
- SHA 清单必须标识测试中的确切版本。
- 生成的 markdown 必须与规范的 JSON 时间戳匹配。

## 规范模块模型

通过将每个主要存储库视为一片叶子，超级项目保持易于理解
自己的主要责任。

|域名 |规范模块 |主封闭面|
| --- | --- | --- |
| ISA / 文档 | `isa`、`docs` |合同检查、架构 lint、AVS 合同 |
|编译器| `compiler/llvm` |编译AVS、覆盖率、工具构建闭包|
|模拟器| `emulator/qemu` |运行时 AVS、严格系统、操作码同步 |
|内核| `kernel/linux` | initramfs 烟雾/完全启动，`vmlinux` 关闭 |
|图书馆 | `lib/glibc`、`lib/musl` | libc 阶段门，运行时烟雾 |
|左转 | `rtl/ZXTERMEN45QXZCore` |阶段/连接 lint、cosim、perf 地板 |
|型号| `tools/pyCircuit` |模型差异，接口契约|
|整合|超级项目|严格的跨回购封闭，双通道平价 |

这是主要的扩展技巧：每个模块首先证明局部正确性，然后
超级项目其次证明了跨模块兼容性。

## 为什么双通道很重要

灵犀指令集 使用两个启动通道：

- `pin`：完全运行超级项目记录的子模块 SHA。
- `external`：针对活动的外部工作树或构建运行。

这区分了两个不同的问题：

1. 固定的工作区是否可重现绿色？
2. 一旦当前的叶子变化完成，下一个 repin 仍然是绿色的吗？

严格封闭需要两个答案。只通过`external`的系统
尚未稳定下来。只传入`pin`的系统可能隐藏
即将到来的集成回归。

## “严格门”在实践中意味着什么

在这个存储库中，“严格”是可操作的，而不是修辞性的。

严格的意思是：- 必须通过必需的、非豁免的大门；
- 豁免必须记录在豁免分类账中；
- Lane、run-id和timestamp是强制上下文；
- 陈旧的工件被拒绝；
- 释放严格配置文件不允许阻塞模式快捷方式；
- Markdown 摘要不能与规范的 JSON 报告不一致；
- 所需的门组必须在 `pin` 和 `external` 通道上匹配。

`tools/regression/strict_cross_repo.sh` 通过以下方式对许多此类策略进行编码
配置文件默认值和硬故障。 `tools/bringup/check_gate_consistency.py`
添加了新鲜度、通道奇偶性、工件存在和摘要一致性检查。

## “严格检查”是什么意思

严格的检查分两层进行。

### 静态严格检查

这些在任何运行时测试被信任之前验证结构。

示例：

- 清单模式和执行模式，
- 检查表 ID 完整性，
- 门到业主的分配范围，
- 规范的技能名称，
- 允许的模块范围，
- 弃权格式和阶段约束。

主要命令：

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists
```

### 运行时严格检查

这些根据静态策略验证具体车道/运行。

示例：

- 每个必需的运行时行都有一个有效的所有者，
- 必需的非豁免行是 `pass`，
- 豁免决定仅在当前阶段有效，
- 运行时存在输出摘要 JSON，
- 严格的封闭由当前工件支持。

主要命令形式：

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode runtime \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists \
  --report docs/bringup/gates/latest.json \
  --lane pin \
  --run-id <run-id> \
  --out docs/bringup/gates/logs/<run-id>/pin/multi_agent_summary.json
```

## 测试驱动的启动方法

推荐的启动循环是：1. 从失败的合同、测试或审核开始。
2. 使用仍然公开的最小叶级命令来重现它
   失败。
3. 在其自己的存储库中修复叶子模块。
4. 重新运行叶子所属的门，直到它们通过。
5. 在超级项目中重新固定子模块 SHA。
6. 重新运行严格的跨仓库关闭。
7. 仅在严格运行变为绿色后才发布更新的证据。

这可以防止大型启动项目中的常见故障模式：使用
超级项目作为“掩盖”未解决的叶模块缺陷的地方。

## 代理友好的运营模式

代理人友好的超级项目是代理人可以回答四个问题的项目
没有人类民间传说：

1. 我可以接触哪些模块？
2. 哪些门证明我的范围是健康的？
3. 哪些工件是规范的？
4. 当门出现故障时，下一步具体是什么？

当前的 灵犀指令集 布局已经很好地支持了这一点：

- 允许的模块在`manifest.yaml`中列出；
- 门所有权分配给清单 ID；
- 规范技能有明确的命名；
- 所需证据位于 `docs/bringup/gates/` 下的稳定路径中；
- 导航规则防止路径漂移；
- repin 规则使跨存储库更改流程保持可预测。

代理人应遵守以下纪律：

- 仅接触已声明的模块，除非作为经批准的跨模块代理；
- 将清单 ID 视为机器可读的承诺，而不是非正式的注释；
- 更喜欢能够证明或反驳假设的最小门；
- 在运行级别记录证据，而不仅仅是散文；
- 以明确的重新固定/不重新固定决定结束。## 每日超级项目工作流程

### 引导程序和拓扑验证

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```

这确认了在任何门结果出现之前工作空间布局是规范的
解释了。

### 刷新规范技能

```bash
bash tools/bringup/sync_canonical_skills.sh --pull-latest
```

这使代理工作流程与当前模块合同保持一致，
分类模式。

### 运行静态启动策略检查

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists
```

在更深入的运行时工作之前执行此操作。如果静态策略被破坏，运行时结果
不够值得信赖，无法关闭。

### 运行合同检查

```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
python3 tools/bringup/check_avs_profile_closure.py \
  --matrix avs/linx_avs_v1_test_matrix.yaml \
  --status avs/linx_avs_v1_test_matrix_status.json \
  --tier pr
```

这证实了面向架构的测试矩阵仍然是规范的。

## Repin 工作流程

重新固定是许多多回购项目变得混乱的地方。 灵犀指令集
纪律应该是：

1. 首先将修复程序放入叶模块中。
2. 验证叶模块自己的门。
3. 更新超级项目中的子模块 SHA。
4. 执行严格的跨仓库关闭。
5. 仅当所需的门和证据完整时才合并 repin。

推荐的同步和重新固定流程：

```bash
git submodule sync --recursive
git submodule update --init --recursive
git submodule update --remote \
  compiler/llvm \
  emulator/qemu \
  kernel/linux \
  rtl/ZXTERMEN45QXZCore \
  tools/pyCircuit \
  lib/glibc \
  lib/musl \
  workloads/pto_kernels
bash tools/ci/check_repo_layout.sh
```

重要规则：不要仅仅推测性地重新固定几个不相关的模块
因为它们都在上游发生了变化。仅重新固定具有已知原因和
已知的门影响。

## 严格的关闭工作流程

### PR 层关闭

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

在重点重装或文档/合同之后，使用此功能进行正常集成关闭
更新。

### 每晚关闭

```bash
LINX_GATE_TIER=nightly RUN_EXTENDED_CROSS_GATES=1 RUN_PERF_FLOOR_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

当您需要更广阔的夜间场地（包括表演场地）时，请使用此功能
检查。

### 双通道运行时收敛

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id-pin>

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane external --run-id <run-id-external>
```当问题是“两条车道是否收敛并且同样严格？”时使用此选项。
而不是“现在是否恰好通过了一个命令？”

### 发布-严格一致性检查

```bash
python3 tools/bringup/check_gate_consistency.py \
  --report docs/bringup/gates/latest.json \
  --progress docs/bringup/PROGRESS.md \
  --gate-status docs/bringup/GATE_STATUS.md \
  --libc-status docs/bringup/libc_status.md \
  --profile release-strict \
  --lane-policy external+pin-required \
  --trace-schema-version 1.0 \
  --max-age-hours 24
```

这就是最后的“文物是否一致？”护栏。

## 故障处理和分类顺序

当大型启动堆栈失败时，请按此顺序修复失败。

### 拓扑首先失败

如果`check_repo_layout.sh`或导航策略失败，则停止。路径漂移和
错误的回购编辑使后来的证据无效。

### 静态策略失败第二次

如果 `check_multi_agent_gates.py --mode static` 失败，请修复清单、清单、
或在信任运行时结果之前放弃结构。

### 叶门故障第三次

如果域门失败，请返回到所属的叶模块并首先修复那里。
示例：

- 编译覆盖失败-> `compiler/llvm`
- 严格的系统/运行时故障 -> `emulator/qemu`
- Linux启动失败-> `kernel/linux`
- cosim 或 perf-floor 故障 -> `rtl/ZXTERMEN45QXZCore`

### 最后集成失败

只有在叶门变绿后，您才可以调试以下方面的故障：

- `strict_cross_repo.sh`，
- 双通道奇偶校验，
- 报告新鲜度，
- 摘要不一致，
- 证据包装缺失。

这个顺序很重要。许多集成失败只是一个症状
不固定的叶子回归。

## 豁免纪律

豁免不是“临时评论”。它们是一流的政策机制。

所需属性：

- 明确的所有者，
- 参考问题，
- 相关相，
- `expires_utc`，
- 通过验证器的运行时可见性。豁免应该清楚地回答一个问题：为什么失败的必填门不是
目前正在阻止活动阶段？如果答案不准确，则放弃
可能太弱而无法保留。

## 证据包装标准

每一次认真的启动运行都应该留下：

- 运行 ID；
- 车道名称；
- 使用的确切命令；
- 车道的 SHA 清单；
- `docs/bringup/gates/latest.json` 中的通过/失败行；
- `docs/bringup/gates/logs/<run-id>/<lane>/` 下的日志或工件路径；
- 用于严格运行时关闭的多代理摘要 JSON。

这使得运行可重播且可审核。没有这个包裹，“它就传递了
我的机器”不是可接受的证据。

## 推荐的决策规则

使用这些规则可以使系统在增长时保持稳定。

- 当故障模式重复出现或架构可见时添加新的门。
- 当所有权必须变得持久且可审查时添加清单项目。
- 仅当活动阶段确实允许差距时才添加豁免。
- 仅在更改的模块具有自己的健康证明后才重新固定。
- 仅在叶子之后从叶子测试升级到严格的交叉回购关闭
  信号干净。
- 将生成的降价视为一次性的；从规范 JSON 重新生成它
  而不是手动编辑它。

## 最小操作手册

对于大多数超级项目启动工作来说，这个顺序就足够了。1. 同步子模块并验证布局。
2. 如果这是一个新的培养周期，请刷新规范技能。
3. 运行静态严格检查。
4. 运行最小的故障域门。
5. 在其自己的存储库中修复叶模块。
6. 重新固定受影响的子模块 SHA。
7. 运行 PR 层 `strict_cross_repo.sh`。
8. 如果更改对集成敏感，则运行双通道收敛。
9. 在调用工作区绿色之前运行 `check_gate_consistency.py`。
10. 从规范 JSON 报告重新生成任何 Markdown 视图。

## 要避免的反模式

避免这些模式；它们使得大量的启动堆栈变得难以管理。

- 编辑状态降价而不更新规范的 JSON 证据。
- 将叶错误隐藏在仅限超级项目的解决方法后面。
- 让路径漂移创建并行的“几乎规范”文件夹。
- 将不相关的 repin 混合到一批推测性集成中。
- 将豁免视为永久政策。
- 当严格封闭需要两条车道时，从一条车道宣告成功。
- 使用没有明确模块范围或清单所有权的代理。

## 总结

灵犀指令集 通过严格限制真相来扩展跨多个模块的启动
生活：

- `isa/` 和 `docs/` 中的合约，
- 根策略文件和 `.gitmodules` 中的拓扑，
- `manifest.yaml` 和清单 ID 的所有权，
- 严格门内的集成证明，
- 在规范的 JSON 证据中发布真相。

这是代理友好的部分。代理人不需要部落知识，如果
回购协议已经声明：

- 它可能发挥作用的地方，
- 它必须证明什么，
- 如何分配失败，
- 以及哪个工件是权威的。