# 跟踪模式合约

版本：`1.0`（发布严格基线）

所有差异验证路径必须发出通用的架构跟踪模式。

## 版本兼容性政策

- 架构版本格式为 `MAJOR.MINOR`。
- `MAJOR` 不匹配是不允许的并且必须快速失败。
- 破坏性架构更改必须增加 `MAJOR` 并运行迁移兼容性检查。
- `MINOR` 在同一 `MAJOR` 内向前兼容：
  - 当 `Z >= Y` 时，消费者 `X.Y` 接受生产者 `X.Z`；
  - 生产者 `X.Z` 和 `Z < Y` 必须被拒绝。
- 生产者可以发出显式的每行 `schema_version`；如果省略，则为浇口工具
  必须使用活动配置文件默认值（当前 v0.56 严格基线中的 `1.0`）。

## 每个提交/事件的必填字段

标量/基数必填字段：

- `cycle`
- `pc`
- `insn`
- `len`
- `wb_valid`
- `wb_rd`
- `wb_data`
- `mem_valid`
- `mem_addr`
- `mem_wdata`
- `mem_rdata`
- `mem_size`
- `trap_valid`
- `trap_cause`
- `next_pc`

扩展 向量/tile 字段（当 向量/tile 子集正在测试时）：

- `block_kind` (`ZXTERMEN44QXZ|vpar|vseq|tma|cube|tepl|call|ret|sys`)
- `lane_id`（用于通道范围的 向量 提交）
- `tile_meta`（磁贴问题/提交的描述符摘要）
- `tile_ref_src` / `tile_ref_dst`（相对参考令牌）

验证政策：

- `block_kind in {vpar,vseq}` 需要 向量 字段 (`lane_id`)。
- `block_kind in {tma,cube,tepl}` 需要图块字段（`tile_meta`，图块参考）。
- 在一个跟踪流中，`cycle` 中的提交顺序必须是非递减的。

## 生产者必须遵守- QEMU参考执行
- pyCircuit C++ 循环模型
- RTL模拟（Icarus/Verilator/VCS）
- FPGA 减少跟踪记录器

## 比较规则

- 使用相同的程序映像和启动 PC 按提交顺序比较跟踪。
- 第一个不匹配是分类锚；不要向前跳过。
- 如果路径中不支持某个字段，请明确标记它并将其视为超出该门的范围。
- 跟踪验证器必须在语义差异之前运行，以尽早捕获模式违规。

## 门要求

如果未解决的模式级分歧仍然存在于声明的指令子集中，则不能将门标记为 `Passed`。