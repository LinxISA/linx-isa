# 灵犀指令集 新代理SOP

这是新特工在里面工作的最短安全操作程序
`linx-isa` 超级项目。

当您需要快速开始工作而无需重新加载完整文件时，请使用此文档
超级项目方法论。

## 使命

你的工作不是“让仓库看起来更环保”。你的工作是：

1. 留在规范的工作空间和允许的模块范围内；
2. 找到最小的失败合约、门或测试；
3.先修复所属叶子模块；
4. 仅在叶样呈绿色后重新固定并重新运行严格关闭；
5.留下机器可读的证据。

## 在接触任何东西之前

从存储库根目录运行这些命令：

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```

如果布局验证失败，请先停止并修复拓扑。

## 首先阅读这些文件

按以下顺序仅阅读您需要的内容：

1.`AGENTS.md`
2.`docs/project/navigation.md`
3.`docs/bringup/agent_runs/manifest.yaml`
4. `docs/bringup/agent_runs/checklists/`下您的拥有清单
5.`tools/bringup/`或`tools/regression/`下的相关gate脚本

如果任务是架构性的，还请阅读`docs/`中的相关合同或
`isa/`。

## 范围规则

严格遵守以下规则：

- 仅在声明的模块中工作。
- 不要创建新的顶级目录。
- 不要将工作路由到禁止的遗留路径中。
- 不要修复超级项目中的叶模块错误，除非问题是
  真正属于超级项目所有。
- 不要将生成的降价视为事实来源。

## 事实的规范来源

当不同的文件不一致时，请按以下顺序信任它们：1. 测试或门命令失败，
2. `isa/` 和 `docs/architecture/` 中的规范合约，
3. machine-readable reports such as `docs/bringup/gates/latest.json`,
4.生成Markdown视图，如`docs/bringup/GATE_STATUS.md`。

## 标准代理循环

几乎所有启动工作都使用此循环。

1. 使用失败的最小门重现问题。
2. 识别所属域和模块。
3.修复所属叶子模块中的问题。
4. 重新运行叶门直至其通过。
5. 如果叶存储库发生更改，请在超级项目中重新固定子模块 SHA。
6. 执行严格的跨仓库关闭。
7. 如果工作流程需要，刷新机器可读和生成的证据。

## 最小的有用命令

### 静态策略检查

在信任运行时关闭之前运行此命令：

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists
```

### AVS 合同检查

Run this when the question is "is the bring-up contract itself still valid?":

```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
python3 tools/bringup/check_avs_profile_closure.py \
  --matrix avs/linx_avs_v1_test_matrix.yaml \
  --status avs/linx_avs_v1_test_matrix_status.json \
  --tier pr
```

### 严格的跨仓库关闭

在叶子证明变为绿色后运行此命令：

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

### 双车道融合

当集成奇偶性很重要时运行此命令：

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id-pin>

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane external --run-id <run-id-external>
```

## 域路由备忘单

如果第一个失败门就在这里，请从此模块开始：

|失效面|从这里开始 |
| --- | --- |
|编译 AVS、覆盖率、LLVM binutils | `compiler/llvm` |
|运行时 AVS、严格系统、操作码同步 | `emulator/qemu` |
| Linux 烟雾/完全启动，`vmlinux` 构建 | `kernel/linux` |
| musl/glibc 运行时或构建闭包 | `lib/musl`、`lib/glibc` |
| cosim、舞台/连接、perf 地板 | `rtl/ZXTERMEN45QXZCore` |
|模型差异，接口契约| `tools/pyCircuit` |
|合同文档、架构 lint、AVS 合同 | `isa`、`docs` |
|通道奇偶性、门一致性、证据包装 |超级项目|

## 故障分类顺序

始终按以下顺序分类：

1. 拓扑故障，
2.静态策略失败，
3. 叶片模块闸门故障，
4.集成关闭失败，
5. 报告新鲜度或证据不匹配。

在叶子门变绿之前，请勿调试通道奇偶校验。

## 豁免规则

仅当满足以下条件时才允许豁免：

- 明确的，
- 相束缚，
- 有时间限制，
- 记录在`docs/bringup/agent_runs/waivers.yaml`中。

如果失败的所需门没有豁免条目，则将其视为阻塞。

## 证据规则

认真的跑步应该留下：

- 车道，
- 运行ID，
- 准确的命令，
- SHA 清单，
- 结果为 `docs/bringup/gates/latest.json`，
- `docs/bringup/gates/logs/<run-id>/<lane>/` 下的日志或工件。

如果无法指向证据路径，则运行未完成。

## 停止条件

在以下情况下停止并升级：

- 任务需要在声明的模块范围之外进行更改；
- 唯一可用的解决方法违反了架构合同；
- 两个规范来源不一致，您无法确定哪一个是过时的；
- 工作区包含与所需直接冲突的用户更改
  修复。## 清仓

在宣布成功之前：

1.确认最小相关叶门为绿色；
2. 如果集成发生变化，确认严格的交叉回购关闭是绿色的；
3. 确认证据路径存在；
4. 明确决定：重复、不重复或放弃阻止；
5. 仅根据规范报告更新生成的状态页面。

## 一屏摘要

- 首先修复叶模块。
- 列宾第二。
- 严格执行第三关。
- 在降价之前信任 JSON。
- 没有无证弃权。
- 无路径漂移。
- 没有“绿色叙事”。