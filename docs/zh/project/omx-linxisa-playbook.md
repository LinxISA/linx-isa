# 灵犀指令集 OMX 手册

该剧本将 灵犀指令集 超级项目规则转变为可重复的 OMX
操作员流程。

当工作涉及以下任意组合时使用它：

- 门分诊，
- 所有者和模块路由，
- 叶子修复然后重新固定纪律，
- 严格的交叉回购关闭，
- 双车道汇聚，
- 技能同步和可重复使用的跑步知识。

## 运营假设

- 超级项目是协调平面，而不是隐藏叶子修复的地方。
- `docs/bringup/gates/latest.json` 是规范门真理。
- `docs/bringup/GATE_STATUS.md` 是生成的视图。
- 必需的非豁免门会阻碍进度。
- 工作从最小的失败合同或门开始。
- 只有在叶样变为绿色后才会进行重新固定。
- `avs/qemu` 套件不得并行共享相同的输出目录。

## 会话引导

从仓库根目录开始：

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
omx --high
```

仅当您有意需要较少约束的路径时才使用 `--madmax`。

## 路由矩阵

|情况| OMX表面|目标|
| --- | --- | --- |
|闸门故障、主人不明、停车条件不明 | `$deep-interview` |锁定最小的复制器、所有者模块、车道影响和证据目标 |
|范围已知，但计划、门令或调整政策仍然模糊 | `$ralplan` |批准任务订单、证明要求和收尾标准 |
|一位所有者，一个模块，可逆步骤 |直接执行|保持低延迟并留在所属模块内 |
|几个只读的小问题 |本地子代理或 `omx explore` |无需启动 tmux 运行时即可并行化查找 |
|长期运行的多所有者关闭与持久协调| `omx team` |在具有 tmux/worktree 状态的清单对齐通道中运行工作 |
|批准的单一所有者完成循环| `$ralph` 或 `omx ralph` |保持任务进展，直至有证据支持完成 |

## 场景 1：登机口分类

当门是红色且主人不明显时使用此选项。

1. 预检：

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```

2.快速查找：

```bash
omx explore --prompt "Map gate <gate-key> to its owner, checklist ids, module scope, and primary scripts in /Users/zhoubot/linx-isa."
```

3. OMX 会话内部：

```text
$deep-interview "Investigate failing gate <gate-key>. Identify owner module, smallest reproducer, lane impact, and required evidence outputs."
$ralplan "Approve module scope, gate order, repin policy, and closeout evidence for <gate-key>."
```

预期结果：

- `docs/bringup/agent_runs/manifest.yaml` 的一位业主，
- 一个最小的叶子或超级项目门，
- 明确的车道策略（`pin`、`external` 或两者），
- `docs/bringup/gates/` 下的明确证据路径。

## 场景 2：Leaf Fix 然后 Repin

当问题属于`compiler/llvm`、`emulator/qemu`时使用此，
`kernel/linux`、`lib/*`、`rtl/ZXTERMEN45QXZCore` 或 `tools/pyCircuit`。1. 首先确认叶子所有者和叶子门。
2.修复所属叶子模块中的问题。
3. 重新运行叶子校样，直至其变成绿色。
4. 仅重新固定预期的子模块 SHA。
5. repin 后运行超级项目关闭。

提示形状：

```text
$ralplan "For <module> and <gate>, approve the exact leaf proof, repin boundary, cross-repo gates to rerun, and whether dual-lane validation is required."
```

列宾健全性检查：

```bash
git status
git diff --submodule
```

总是回答：

- 什么叶子证明使 SHA 安全？
- 什么跨回购门可能会回归？
- 封闭是否需要仅 `pin` 还是两条车道？
- 是否需要更改任何豁免？

## 场景 3：PR 级严格关闭

在叶修复或超级项目拥有的集成更改后使用此功能。

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists

python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml

python3 tools/bringup/check_avs_profile_closure.py \
  --matrix avs/linx_avs_v1_test_matrix.yaml \
  --status avs/linx_avs_v1_test_matrix_status.json \
  --tier pr

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

如果您想要使用 OMX 进行 shell 本机有界验证，请使用 `omx sparkshell`
表面一致性：

```bash
omx sparkshell bash tools/ci/check_repo_layout.sh
```

## 场景 4：双通道运行时融合

仅在拥有叶子证明和 PR 层关闭可信后才使用此功能。

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id-pin>

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane external --run-id <run-id-external>
```

当需要持久的多所有者与单独的工作时，请使用 `omx team`
检查表和证据流。保持车道与舱单所有者保持一致，例如
`arch`、`llvm`、`qemu`、`linux`、`libc`、`linxcore`、`pycircuit` 和
`integration`。

## 场景 5：技能同步和可重用知识

通过刷新规范技能来开始新的培养周期：

```bash
bash tools/bringup/sync_canonical_skills.sh --pull-latest
```

使用本地 wiki 获取不应该被困在终端中的运行知识
历史：

```bash
omx wiki wiki_ingest --input '{"source":"docs/bringup/gates/latest.json","title":"gate-truth-notes"}' --json
omx wiki wiki_query --input '{"query":"strict_cross_repo stale artifact failure"}' --json
```

好的维基目标：

- 反复出现的闸门故障，
- 车道专用脚枪，
- 证据路径约定，
- 值得重复使用的技能发展决策。

## 场景 6：长时间运行的 OMX 会话

有用的操作界面：

```bash
omx status
omx hud --watch
omx resume
```仅当 tmux/worktree 持久性值得开销时才使用 `omx team`。
对于小型会话内扇出，首选本机子代理。

## 反模式

不要：

- 在所属叶门变绿之前调试通道奇偶校验，
- 将降价状态视为事实来源，
- 将不相关的模块重新固定在一起，
- 并行化 `avs/qemu` 针对相同的输出目录运行，
- 仅修复超级项目中的叶错误，
- 留下不带命令、通道、运行 ID、SHA 清单和工件路径的运行。

## 收尾清单

在宣布成功之前：

1. 确认最小的相关叶子或超级项目门为绿色。
2. 如果集成发生变化，请确认 PR 层严格关闭。
3. 如果任务需要，确认双车道关闭。
4. 确认`docs/bringup/gates/`下存在证据。
5. 明确决定：重新固定、不重新固定或放弃阻止。
6. 仅更新从规范报告生成的降价。

## 主要参考文献

- `AGENTS.md`
- `docs/project/navigation.md`
- `docs/project/omx-linxisa-prompt-templates.md`
- `docs/project/new-agent-sop.md`
- `docs/project/maintainer-repin-checklist.md`
- `docs/project/superproject-bringup-methodology.md`
- `docs/bringup/agent_runs/manifest.yaml`
- `docs/bringup/agent_runs/waivers.yaml`
- `docs/bringup/gates/latest.json`