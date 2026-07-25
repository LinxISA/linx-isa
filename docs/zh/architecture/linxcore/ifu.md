# LinxCore IFU 架构

## 1. 总体定义

LinxCore IFU 由两个互相解耦、独立反压的引擎组成：

- **I-SIDE（Instruction Side）**：负责指令地址转换、L1I 访问、
  cacheline 处理、边界预解码、64 位定长化以及写入 Instruction
  Buffer。
- **B-SIDE（Branch Side）**：负责控制流预测以及预测器的训练、检查点
  和恢复状态。

两个引擎不共享隐式流水寄存器或可变队列，只通过带 ready/valid 和请求
身份的显式接口交互。任一引擎都可以独立停顿。

两个引擎分别拥有五级流水：

- I-SIDE：`I-F0`、`I-F1`、`I-F2`、`I-F3`、`I-F4`；
- B-SIDE：`B-F0`、`B-F1`、`B-F2`、`B-F3`、`B-F4`。

前缀不可省略，因为两条流水相互解耦、不锁步。Instruction Buffer 位于
I-F4 之后、D1 之前。

## 2. I-SIDE 流水

```text
PC/redirect
    |
    v
 I-F0 -> I-F1 -> I-F2 -> I-F3 -> I-F4 -> Instruction Buffer -> D1
        |                                  |
   ITLB || L1I                        每周期 4 x 64-bit
```

### I-F0：PC 请求

- 接受 reset、顺序、预测或 redirect PC；
- 多线程时选择 STID；
- 分配 `fetch_id` 并记录当前 `epoch`；
- 向 B-SIDE 发送带身份的预测请求；
- 把 I-SIDE 请求寄存到 I-F1。

### I-F1：ITLB 与 L1I 并行访问

I-F1 对同一个虚拟 PC 和请求身份并行启动 ITLB 与 L1I 访问。不得实现为
先查 ITLB、再启动 L1I 的串行流程。

### I-F2：结果汇合和 inner flush

- 汇合 ITLB 结果与 L1I tag/data 查询状态；
- ITLB fault 形成精确取指异常；
- ITLB miss 启动页表遍历/回填，并产生 **I-SIDE inner flush**；
- L1I miss 启动或合并 cacheline refill。

inner flush 只清除对应 STID/epoch 的年轻 I-SIDE 工作和陈旧 L1I
响应，不清除 OOO、retire 或其他 STID 的状态。需要取消 B-SIDE 请求时，
必须走显式 cancel/redirect 接口。

### I-F3：cacheline 与字节流状态

I-F3 保存：

- cacheline 数据和基地址；
- ECC/完整性结果；
- refill 响应身份；
- 从请求 PC 开始的 byte cursor；
- 跨 cacheline 的未完成指令 carry。

I-F3 只向 I-F4 提供有序字节流和 carry，不做完整指令译码，也不做跳转预测。

### I-F4：边界预解码和 64 位定长化

I-F4 是 I-SIDE 的真实第 4 级，不是 Instruction Buffer。

I-F4：

- 判断 2/4/6/8-byte 指令长度；
- 结合 I-F3 carry 拼成完整指令；
- 只识别 `BSTART`/`BSTOP` 类 block boundary；
- 把编码字节零扩展成固定 64-bit `insn64`；
- 按程序顺序写入 Instruction Buffer。

I-F4 不做通用 opcode、operand、immediate、branch kind/target 或 template
语义译码。原始长度仍作为 PC 推进、合法性和 trace 元数据保留。

## 3. Instruction Buffer 与 D1

Instruction Buffer 是按 STID 分区的队列。每项至少包含：

```text
valid, stid, fetch_id, epoch, pc
encoded_length, insn64
is_bstart, is_bstop
fetch_fault
prediction_id / prediction metadata
```

D1 每周期从一个 STID 读取最多四条连续的 64-bit 指令，完成完整
opcode、operand、immediate、异常和 split/fuse 译码。D1 之后所有携带
指令的接口都使用 64-bit 定长容器，下游不再切分变长原始字节流。

## 4. B-SIDE 预测引擎

B-SIDE 参考 LinxCoreModel 的预测算法，并拥有独立五级流水：

| Stage | 职责 |
|---|---|
| B-F0 | L0/NLP next-line prediction，分配投机 prediction checkpoint，保存 GHR/GHRQ/RAS 快照 |
| B-F1 | uBTB 类型/目标查询、fast RAS 查询并启动较大预测表访问 |
| B-F2 | PBTB/BTB 类型/目标查询以及 BIM 基础方向预测 |
| B-F3 | short/medium-history TAGE 查询并启动 IBTB 间接目标查询 |
| B-F4 | long-history TAGE、final IBTB、loop predictor/buffer、RAS final check 和统一方向/类型/目标仲裁 |

B-F0 可以产生首个可用 next-PC。B-F1 至 B-F4 可以确认或纠正同一
`{fetch_id, stid, epoch, pc, checkpoint}` 的预测。由于 B-SIDE 与 I-SIDE
不锁步，每个候选和纠正都必须按身份匹配。

统一 provider 优先级为：

```text
backend restart
  > B-F4 > B-F3 > B-F2 > B-F1 > B-F0 > sequential
```

backend restart 是 recovery source，不是 prediction provider。B-F4 内，
exact RAS return target 或 high-confidence IBTB indirect target 赢得对应
target 选择；方向 override 顺序为
`loop > long-TAGE > short-TAGE > BIM`；direct target 由 BTB family 提供。

后级 B-SIDE 结果若与已接受的早期结果在
`{taken, branch_pc, target, kind}` 任一字段不同，则纠正该精确预测身份。若
早期结果已经驱动 I-SIDE，纠正必须产生 identity-qualified I-SIDE inner
flush，恢复匹配的 GHR/GHRQ/RAS checkpoint，切换 fetch epoch，取消匹配项及
更年轻的 I-SIDE/B-SIDE 工作，并从纠正 PC 重启 I-F0；这本身不清除 backend
架构状态。

backend 已解析的 misprediction 必须进入 typed recovery，按 recovery
class 恢复 predictor/rename/block 状态，同时发布 frontend restart 到
I-F0。

B-SIDE 包含：

- BTB、uBTB、PBTB；
- GHR、GHRQ；
- TAGE 和 BIM；
- RAS；
- IBTB；
- loop predictor 和 loop buffer；
- prediction arbiter、BRQ/checkpoint、训练和更新逻辑。

B-SIDE 不拥有 ITLB、L1I、cacheline refill、predecode 或 Instruction
Buffer。

## 5. 解耦接口

- **prediction request**：
  `{fetch_id, stid, epoch, pc, history_checkpoint}`。
- **prediction response**：
  `{fetch_id, stid, epoch, taken, branch_pc, target, kind, checkpoint_id, source}`。
- **resolve/training**：实际方向、实际目标、分支类型和检查点身份。
- **redirect/cancel**：STID、新 PC、新 epoch 和恢复身份。

cache 响应与 prediction 响应都必须按身份匹配，不能依赖同周期位置。

## 6. superscalarNPU 对比

`superscalarNPU` `origin/main@1fae7d0` 只作为参考设计，不是规范依赖。
可复用证据包括 FTQ 解耦的 B/I path、per-thread PC/GHR/RAS、
MBTB/TAGE/IBTB 和 Instruction Buffer。

| 项目 | superscalarNPU 参考 | LinxCore 目标 |
|---|---|---|
| stage | B0–B4 加 I-F1–I-F3 | I-F0..I-F4 加 B-F0..B-F4 |
| translation/cache | 无 TLB，PIPT 假设 | I-F1 并行 ITLB/L1I，miss/refill 保留身份 |
| early prediction | 移除 uBTB 与 intra-flush | B-F1 保留 uBTB；后级纠正 inner-flush I-SIDE 并重启 I-F0 |
| predictor grouping | B2/B3 聚合多种 predictor | 从 L0/NLP 到 long TAGE/IBTB/loop 的分级质量 |
| fetch completion | SN I-F3 static/context，加 variable-width IB | I-F4 只做 boundary predecode 和 64-bit entry，D1 完整译码 |

借鉴点只是按身份关联的解耦 prediction/fetch ownership。LinxCore stage
命名、translation policy、纠正规则、predecode 边界和 4x64-bit D1 合同
完全由本文定义。

## 7. 强制不变量

1. I-SIDE 使用 I-F0..I-F4，B-SIDE 使用 B-F0..B-F4。
2. 两个引擎相互解耦、不依赖锁步 stage 对齐。
3. I-F1 并行启动 ITLB 与 L1I。
4. ITLB miss 产生 I-SIDE inner flush，而不是 OOO/global flush。
5. B-SIDE 后级纠正已使用预测时 inner-flush I-SIDE 并重启 I-F0；
   backend misprediction 走 typed recovery。
6. BHC/fetch-cache 行为属于 I-SIDE L1I，不属于 B-SIDE。
7. 预解码只判断长度和 `BSTART`/`BSTOP` 边界。
8. 每个 Instruction Buffer entry 保存一条完整 `insn64`。
9. D1 每周期读取四条 64-bit 指令并完成完整译码。
10. I-SIDE 与 B-SIDE 只通过显式解耦接口交互。
