# 灵犀指令集 v0.3 — Sail 形式化计划（逐步）

本文档跟踪在 `isa/sail/` 下逐步启动 Sail 模型。

范围/限制：

- Sail 模型是语义的**参考**。
- 缺失的语义必须**明确**（无需猜测）。如果规则不清楚，我们可以：
  - 添加澄清/约定条目，或者
  - 保留未执行的指令并将问题记录在审核日志中。
- 覆盖范围通过以下方式机械跟踪：
  - `isa/sail/implemented_mnemonics.txt`
  - `isa/sail/coverage.json`（生成）

每个助记符的完成定义：

- 解码/调度到达助记符的实现点（即使解码最初是部分/功能门控的）。
- 实现执行语义（或使用链接的审阅日志条目显式 `unimplemented("MNEMONIC")`）。
- 处理手动文档影响：
  - 自动生成的 ISA 手册部分已经涵盖，或者
  - 需要明确的规范/非规范注释，捕获为 `docs/architecture/isa-manual/src/...` 中的提交。

建议的迭代循环（每个小切片一个 PR）：

1) 选择一小部分（例如，一组连贯的助记词中有 5-20 个）。
2）对于每个助记词：
   - 确认语义极端情况（陷阱原因/参数、符号/零扩展规则、对齐/原子性等）
   - 实现 Sail 执行语义
   - 添加/扩展解码/调度支持
3）更新`isa/sail/implemented_mnemonics.txt`。
4）重新生成并检查：
   - `python3 tools/isa/sail_coverage.py ... --check`
   - `python3 tools/isa/validate_spec.py --profile v0.3`
   - `python3 tools/isa/build_golden.py --profile v0.3 --check`
5) 将任何审稿人的决定记录在：`docs/bringup/plan/sail_review_log_v0.3.md`

初始优先级（可以调整）：- P0：建立可维护的解码/调度路径（最好从 `removed-pre-v056-profile/removed-pre-v056-catalog.json` 生成）。
- P1：工具链/QEMU 对齐所需的整数核心缺失语义（比较 + setc + 分支）。
- P2：加载/存储+缓存维护（以及相关的故障/部分效应规则）。
- P3：原子。
- P4：浮点数和 向量（整数/内存基数稳定后）。

当前覆盖范围快照：

- 权威缺失列表见`isa/sail/coverage.json`。