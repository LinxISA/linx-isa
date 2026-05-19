# 灵犀Core 外部接口合约

## pyCircuit-灵犀Core 接口合约 (LC-IF-PYC-001)

pyCircuit/灵犀Core 集成合约已进行版本控制并由网关强制执行。

合约工件：

- `docs/bringup/contracts/pyc_linxcore_interface_contract.json`
- `docs/bringup/contracts/pyc_linxcore_interface_contract.md`

规则：

- 合约版本遵循`MAJOR.MINOR`。
- 向后兼容的添加增量 `MINOR`。
- 破坏字段删除/重命名或语义重新定义增量 `MAJOR`。
- Gate 工具拒绝未版本控制的接口中断。

## 所需的提交有效负载合同 (LC-IF-PYC-002)

`pyc_linxcore_interface_contract.json` 所需的提交字段：

- `cycle`、`pc`、`insn`
- `wb_valid`、`wb_rd`、`wb_data`
- `mem_valid`、`mem_addr`、`mem_wdata`、`mem_rdata`、`mem_size`
- `trap_valid`、`trap_cause`、`next_pc`

所需的环境控制：

- `PYC_COMMIT_TRACE`
- `PYC_BOOT_PC`
- `PYC_MEM_BYTES`
- `PYC_MAX_CYCLES`

## 灵犀Trace 模式合约 (LC-IF-TRACE-001)

跟踪模式治理：

- 规范合约：`docs/bringup/contracts/trace_schema.md`
- 生产者端模式验证：`tools/bringup/validate_trace_schema.py`
- SemVer 兼容性门：`tools/bringup/check_trace_semver_compat.py`

规则：

- `MAJOR` 不匹配是硬故障。
- `MINOR` 必须是生产者 >= 消费者期望。
- 破坏跟踪更改需要进行重大碰撞和迁移检查。

## 跟踪兼容性合同 (LC-IF-TRACE-002)

- `linxtrace.v1` 对于添加剂变化保持稳定。
- 对于不兼容的字段/语义更改，主要版本更新是强制性的。
- 兼容性检查必须在重大不匹配时快速失败。

## 跨工具同步合约（LC-IF-SYNC-001）当跟踪/管道合同发生变化时，以下内容必须保持同步：

- `rtl/ZXTERMEN45QXZCore/src/common/stage_tokens.py`
- `rtl/ZXTERMEN45QXZCore/tb/tb_linxcore_top.cpp`
- `rtl/ZXTERMEN45QXZCore/tools/trace/build_linxtrace_view.py`
- `rtl/ZXTERMEN45QXZCore/tools/linxcoresight/lint_linxtrace.py`
- `rtl/ZXTERMEN45QXZCore/tools/linxcoresight/lint_trace_contract_sync.py`

查看器端合约同步通过 灵犀Trace 门进行验证。

## 范围边界

本文档仅涵盖**外部** 灵犀Core 接口治理：

- pyCircuit合约
- 追踪模式合约
- 跨工具同步规则

灵犀Core **微架构**接口合约详解（两层区块机、面向BROB的解析、
原始引擎结构、引擎/块类型映射）属于：

- `rtl/ZXTERMEN45QXZCore/docs/architecture/`
- `docs/architecture/linxcore/microarchitecture.md`

对于当前的架构编写阶段，升级阶段合同来自
`F0` 通过基线发出/唤醒片（`S1/S2/P1/I1/I2/E1/W1`）
在 `docs/architecture/linxcore/microarchitecture.md` 中规范捕获，
虽然本文档仍然仅限于外部/面向工具的接口
治理。

## 接口变更控制

- 界面可见的更改必须首先更新合约工件。
- `docs/architecture/linxcore/verification-matrix.md` 中的门行是接口升级的释放阻塞器。
- 任何合同重大变更都必须包括迁移说明和双通道证据。