# 灵犀指令集 维护者 Repin 清单

此清单适用于更新一个或多个子模块 SHA 的维护人员
`linx-isa` 超级项目。

用它来保持回复的纪律性、可追溯性和可复制性。

## 列宾先决条件

在满足以下条件之前，请勿开始重新固定：

- 叶模块更改已存在于所属存储库中；
- 叶子所有者已针对该更改运行了模块拥有的门；
- 驳回原因明确；
- 预计的门影响是已知的。

错误的重新固定模式：

- “这些模块在上游发生了变化，所以我把它们全部放在一起。”

良好的重新固定模式：

-“QEMU 严格系统修复已登陆上游；重新固定 `emulator/qemu`；重新运行 QEMU 并
  整合关闭。”

## 范围声明

在编辑 SHA 之前，写下：

- 正在重新固定哪些模块；
- 为什么每个模块都在变化；
- 哪些登机门预计会移动；
- 更改是仅叶更改还是跨模块更改。

如果你不能回答这四个问题，那么 repin 批次就太模糊了。

## 工作区准备

从仓库根目录：

```bash
git submodule sync --recursive
git submodule update --init --recursive
bash tools/ci/check_repo_layout.sh
```

在新的培养周期开始时刷新规范技能：

```bash
bash tools/bringup/sync_canonical_skills.sh --pull-latest
```

## 静态策略防护

在运行时关闭之前运行此命令：

```bash
python3 tools/bringup/check_multi_agent_gates.py \
  --strict-always \
  --mode static \
  --manifest docs/bringup/agent_runs/manifest.yaml \
  --waivers docs/bringup/agent_runs/waivers.yaml \
  --checklists-root docs/bringup/agent_runs/checklists
```

如果此操作失败，请不要信任稍后的运行时结果，直到策略得到修复。

## 列宾力学

仅更新预期的模块：

```bash
git submodule update --remote \
  compiler/llvm \
  emulator/qemu \
  kernel/linux \
  rtl/ZXTERMEN45QXZCore \
  tools/pyCircuit \
  lib/glibc \
  lib/musl \
  workloads/pto_kernels
```

在实践中，将该命令缩小到您要重新固定的特定模块。

更新 SHA 后：

```bash
git status
git diff --submodule
```

检查：- 仅移动预期的子模块；
- `.gitmodules` 仅当 URL 策略确实更改时才更改；
- 没有不相关的工作空间流失混合到 repin 中。

## 每个模块所需的问题

对于每个重新固定的模块，回答：

1. 什么叶子门证明新的 SHA 是健康的？
2. 由于 SHA 此举，哪些跨回购门可能会回归？
3. 此 repin 是否仅需要 `pin`，还是同时需要 `pin` 和 `external` 通道
   验证？
4. 是否需要添加、删除任何豁免或允许其过期？

## Repin 后的最小门矩阵

### 总是

运行：

```bash
python3 tools/bringup/check_avs_contract.py --matrix avs/linx_avs_v1_test_matrix.yaml
python3 tools/bringup/check_avs_profile_closure.py \
  --matrix avs/linx_avs_v1_test_matrix.yaml \
  --status avs/linx_avs_v1_test_matrix_status.json \
  --tier pr
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/regression/strict_cross_repo.sh
```

### 当严格的集成奇偶校验很重要时

运行两条车道：

```bash
LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane pin --run-id <run-id-pin>

LINX_GATE_TIER=pr RUN_EXTENDED_CROSS_GATES=1 \
bash tools/bringup/run_runtime_convergence.sh --lane external --run-id <run-id-external>
```

### 当结束严格的发布质量运行时

运行一致性门：

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

## 特定领域的期望

使用此表可以避免重新固定测试不足。

|模块|您应该期待的最低限度的证据 |
| --- | --- |
| `compiler/llvm` |如果 Linux/libc 关闭很重要，请编译 AVS、覆盖率、辅助 LLVM 工具 |
| `emulator/qemu` |严格系统、运行时 AVS、操作码同步、固定二进制构建 |
| `kernel/linux` | `vmlinux` 构建，initramfs 冒烟/完全启动 |
| `lib/glibc` |适用于当前配置文件的 G1a/G1b 阶段闸门 |
| `lib/musl` |构建闭包和运行时烟雾（如适用）
| `rtl/ZXTERMEN45QXZCore` |适合该阶段的 lint/cosim/perf 门 |
| `tools/pyCircuit` |界面契约和模型差异表面|
| `isa`、`docs` |合同检查和任何生成的工件刷新它们意味着 |

## 证据包装清单

在合并 repin 之前，请确保您可以指向：- 运行ID，
- 车道，
- 准确的命令，
- 日志路径，
- `docs/bringup/gates/latest.json` 中的 SHA 清单条目，
- 生成状态刷新（如果适用），
- 用于严格运行时关闭的多代理摘要 JSON。

如果其中任何一个缺失，则 repin 尚未准备好合并。

## Repin期间放弃纪律

不要通过编辑散文或依赖他人的文章来通过repin走私红色大门
隐含的理解。

如果需要豁免：

- 记录在`docs/bringup/agent_runs/waivers.yaml`中；
- 将其与活性相结合；
- 设置所有者和`expires_utc`；
- 确保运行时验证器可以看到它。

如果不再需要豁免，请在同一维护时段中将其删除。

## 合并决策

仅当满足以下条件时，重新固定才准备就绪：

- 预期模块是批次中唯一的 SHA 移动；
- 所需的非豁免登机通行证；
- 证据是新鲜的且机器可读的；
- `pin`和`external`车道政策满足目标封闭水平；
- 生成的 Markdown 与规范的 JSON 一致；
- 提交消息解释了模块范围和原因。

## 提交形状

更喜欢重新固定那些范围狭窄且可解释的提交。

好的例子：

- `chore(submodule): repin emulator/qemu for strict-system timer fix`
- `chore(submodules): repin compiler/llvm and kernel/linux for pinned build closure`

避免不透明的消息，例如：

- `update deps`
- `sync repos`
- `latest upstream`

## 反模式

不要：

- 仅仅因为多个不相关的模块可用而重新固定它们；
- 将 repin 与过时的 `latest.json` 证据合并；
- 手动编辑`GATE_STATUS.md`；
- 当严格关闭需要两条车道时，假设 `pin` 车道成功就足够了；
- 在严格释放闭包中接受阻塞模式快捷方式。

## 最终合并清单1. 仅限预期的子模块 SHA。
2. 为每个移动模块确定叶子证明。
3. PR 层或夜间层严格关闭运行。
4. 如果需要的话，进行双通道验证。
5. 通过一致性检查，严格发布关闭。
6. 审查豁免。
7.记录证据路径。
8. 提交消息命名重新固定的模块和原因。