# 灵犀Core v0.56 验证矩阵

> 此发布的页面镜像了规范的 灵犀Core 源代码
> `rtl/ZXTERMEN45QXZCore/docs/architecture/verification-matrix.md`。


该矩阵将 灵犀Core 架构意图与严格要求的门联系起来。

它是以下之间的规范映射：

- 灵犀Core 合约页面，
- 合同标识符，
- 所需的验证命令，
- 用于促销的接受场景。

## G1 合约行（规范）|合约编号 |面积 |规范性声明|
|---|---|---|
| `LC-ARCH-DOC-001` |架构文档 | Canonical 灵犀Core 文档位于 `rtl/ZXTERMEN45QXZCore/docs/architecture` 中，镜像到 `docs/architecture/linxcore` 中，并在 灵犀Arch 文档中保持导航连接 |
| `LC-MA-PIPE-001` |管道|保留舞台所有权和精确的 super标量 退休 |
| `LC-MA-HAZ-001` |危险/重赛 |重放、重定向、唤醒和发出行为不违反正确性 |
| `LC-MA-BLK-001` |块控制流| `BSTART`/`BSTOP`、BID 和恢复到边界的合法性被保留 |
| `LC-MA-PRV-001` |特权/陷阱|美国陷阱进入/返回和 CSR 可见的副作用是精确的 |
| `LC-MA-MMU-001` |管理单元|翻译和故障行为是精确的并且经过门验证 |
| `LC-MA-IRQ-001` |中断 |定时器 IRQ 传递和进入/返回行为在严格门控下是确定性的 |
| `LC-MA-MEM-001` |内存排序 |加载/存储转发、重播和提交可见排序保持合法 |
| `LC-MA-FWD-001` |前进的步伐 |分支、刷新、加载未命中和重放路径保留进度 |
| `LC-MA-STAGE-001` |舞台所有权|每个记录的管道阶段都映射到专用的所有者文件和 `@module` 边界 |
| `LC-IF-PYC-001` | pyCircuit 接口版本控制 | pyCircuit-灵犀Core 合约遵循 SemVer，具有门控强制兼容性 |
| `LC-IF-PYC-002` | pyCircuit 提交有效负载 |必需的提交字段和环境控件与跟踪工具保持兼容 |
| `LC-IF-TRACE-001` |跟踪模式| 灵犀Trace 模式在生产者和消费者工具之间保持同步 || `LC-IF-TRACE-002` |跟踪兼容性 |破坏跟踪更改需要主要版本碰撞和兼容性检查|
| `LC-IF-SYNC-001` |跨工具同步 |发射器、linter 和查看器合约保持同步并经过门验证 |

## 门到合约的可追溯性（需要 PR 门）

|大门钥匙|涵盖的合约 ID |
|---|---|
| `Architecture::ZXTERMEN45QXZCore architecture contract lint` | `LC-ARCH-DOC-001`、`LC-MA-PIPE-001`、`LC-MA-HAZ-001`、`LC-MA-BLK-001`、`LC-MA-PRV-001`、`LC-MA-MMU-001`、`LC-MA-IRQ-001`、`LC-MA-MEM-001`、`LC-MA-FWD-001`、`LC-MA-STAGE-001`、 `LC-IF-PYC-001`、`LC-IF-PYC-002`、`LC-IF-TRACE-001`、`LC-IF-TRACE-002`、`LC-IF-SYNC-001` |
| `Architecture::mkdocs architecture nav/docs` | `LC-ARCH-DOC-001` |
| `ZXTERMEN45QXZCore::stage/connectivity lint` | `LC-MA-PIPE-001`、`LC-MA-STAGE-001` |
| `ZXTERMEN45QXZCore::opcode parity` | `LC-MA-PIPE-001`、`LC-MA-BLK-001` |
| `ZXTERMEN45QXZCore::runner protocol` | `LC-MA-BLK-001`、`LC-MA-FWD-001`、`LC-MA-IRQ-001` |
| `ZXTERMEN45QXZCore::trace schema and memory smoke` | `LC-MA-HAZ-001`、`LC-MA-MEM-001`、`LC-IF-TRACE-001` |
| `ZXTERMEN45QXZCore::cosim smoke` | `LC-MA-PRV-001`、`LC-MA-MMU-001`、`LC-MA-IRQ-001`、`LC-MA-MEM-001` |
| `Testbench::ROB bookkeeping` | `LC-MA-PIPE-001`、`LC-MA-HAZ-001`、`LC-MA-FWD-001` |
| `Testbench::block struct pyc flow smoke` | `LC-MA-BLK-001`、`LC-MA-HAZ-001` |
| `pyCircuit::CPU C++ smoke` | `LC-IF-PYC-001`、`LC-IF-PYC-002` |
| `pyCircuit::QEMU vs pyCircuit trace diff` | `LC-MA-PRV-001`、`LC-MA-MMU-001`、`LC-MA-MEM-001`、`LC-IF-PYC-002`、`LC-IF-TRACE-001` |
| `pyCircuit::interface contract gate` | `LC-IF-PYC-001`、`LC-IF-PYC-002` |
| `ZXTERMEN45QXZTrace::contract sync lint` | `LC-IF-TRACE-001`、`LC-IF-SYNC-001` |
| `ZXTERMEN45QXZTrace::sample trace lint` | `LC-IF-TRACE-001`、`LC-IF-SYNC-001` |
| `ZXTERMEN45QXZTrace::semver compatibility gate` | `LC-IF-TRACE-002`、`LC-IF-TRACE-001` |

## PR 强制矩阵|域名 |门钥匙|命令 |合同意向 |
|---|---|---|---|
|建筑| `Architecture::ZXTERMEN45QXZCore architecture contract lint` | `python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict` |规范子模块文档、镜像和交叉链接均存在并同步 |
|建筑| `Architecture::mkdocs architecture nav/docs` | `python3 tools/bringup/check_linxcore_arch_contract.py --root . --strict --require-mkdocs` |已发布的文档包括镜像的 灵犀Core 合约页面 |
| 灵犀核心 | `ZXTERMEN45QXZCore::stage/connectivity lint` | `bash rtl/ZXTERMEN45QXZCore/tests/test_stage_connectivity.sh` |管道命名、阶段规范所有权和连接不变量 |
| 灵犀核心 | `ZXTERMEN45QXZCore::opcode parity` | `bash rtl/ZXTERMEN45QXZCore/tests/test_opcode_parity.sh` |解码和操作码奇偶校验与参考|
| 灵犀核心 | `ZXTERMEN45QXZCore::runner protocol` | `bash rtl/ZXTERMEN45QXZCore/tests/test_runner_protocol.sh` | co-sim 协议安全性和失配快速失败 |
| 灵犀核心 | `ZXTERMEN45QXZCore::trace schema and memory smoke` | `bash rtl/ZXTERMEN45QXZCore/tests/test_trace_schema_and_mem.sh` |提交和跟踪模式以及内存事件存在 |
| 灵犀核心 | `ZXTERMEN45QXZCore::cosim smoke` | `bash rtl/ZXTERMEN45QXZCore/tests/test_cosim_smoke.sh` |提交流与参考入口点对齐 |
|测试台| `Testbench::ROB bookkeeping` | `bash rtl/ZXTERMEN45QXZCore/tests/test_rob_bookkeeping.sh` | super标量 退休排序不变量 | super标量
|测试台| `Testbench::block struct pyc flow smoke` | `bash rtl/ZXTERMEN45QXZCore/tests/test_block_struct_pyc_flow.sh` |块结构 pyCircuit 管道集成 |
| py电路| `pyCircuit::CPU C++ smoke` | `bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh` | pyCircuit CPU 流功能 |
| py电路| `pyCircuit::QEMU vs pyCircuit trace diff` | `bash tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh` |建筑痕迹等价|
| py电路| `pyCircuit::interface contract gate` | `python3 tools/bringup/check_pycircuit_interface_contract.py --root . --strict` |版本化 pyCircuit↔灵犀Core 界面控制 |
| 灵犀跟踪 | `ZXTERMEN45QXZTrace::contract sync lint` | `python3 rtl/ZXTERMEN45QXZCore/tools/linxcoresight/lint_trace_contract_sync.py` |发射器、linter 和查看器管道合约同步 |
| 灵犀跟踪 | `ZXTERMEN45QXZTrace::sample trace lint` | `bash rtl/ZXTERMEN45QXZCore/tests/test_konata_sanity.sh` |追踪有效性和舞台存在感|| 灵犀跟踪 | `ZXTERMEN45QXZTrace::semver compatibility gate` | `python3 tools/bringup/check_trace_semver_compat.py --root . --strict` |架构版本兼容性策略实施 |

## PR 选择加入扩展

|域名 |门钥匙|命令 |合同意向 |
|---|---|---|---|
|规格/灵犀Core | `SPEC::Stage-A dual-transport + 1K xcheck` | `bash rtl/ZXTERMEN45QXZCore/tests/test_specint_stage_a_xcheck.sh` |跨 QEMU 传输通道的 A 阶段关闭和针对 灵犀Core C++ TB 的 1K 提交奇偶校验 |

## 每晚强制扩展

|域名 |门钥匙|命令 |合同意向 |
|---|---|---|---|
| 灵犀核心 | `ZXTERMEN45QXZCore::CoreMark crosscheck 1000` | `bash rtl/ZXTERMEN45QXZCore/tests/test_coremark_crosscheck_1000.sh` |长期架构融合|
| 灵犀核心 | `ZXTERMEN45QXZCore::CoreMark crosscheck full` | `bash rtl/ZXTERMEN45QXZCore/tests/test_coremark_crosscheck_full.sh` |具有严格源/数据关联的全面运行架构融合|
| 灵犀核心 | `ZXTERMEN45QXZCore::CBSTOP inflation guard` | `bash rtl/ZXTERMEN45QXZCore/tests/test_cbstop_inflation_guard.sh` |块边界行为回归守卫 |
| 灵犀跟踪 | `ZXTERMEN45QXZTrace::DFX trace smoke` | `bash rtl/ZXTERMEN45QXZCore/tests/test_konata_dfx_pipeview.sh` | DFX 跟踪路径有效性 |
| 灵犀跟踪 | `ZXTERMEN45QXZTrace::template trace smoke` | `bash rtl/ZXTERMEN45QXZCore/tests/test_konata_template_pipeview.sh` |模板流跟踪可见性 |
| py电路| `pyCircuit::examples regression` | `bash tools/pyCircuit/flows/scripts/run_examples.sh` |烟流宽度|
| py电路| `pyCircuit::simulation regression` | `bash tools/pyCircuit/flows/scripts/run_sims.sh` |回归模拟车道|
| py电路| `pyCircuit::nightly simulation regression` | `bash tools/pyCircuit/flows/scripts/run_sims_nightly.sh` |深夜流闭|
|整合| `Integration::ZXTERMEN45QXZCore performance floor` | `python3 tools/bringup/check_linxcore_perf_floor.py --root . --max-regression 10.0` | <=10% 回归上限执行 |

## 验收场景

强制场景系列：- 权限转换和 `SRET` 行为
- MMU 转换和页面或权限故障路径
- 定时器中断传递和边界交互
- 分支、块和恢复合法性
- 加载/存储转发和重播排序
- super标量 多发出、多提交和刷新排序
- 跟踪架构、合约 ID 同步和 SemVer 策略

## 矩阵维护规则

- `overview.md`、`microarchitecture.md` 和 `microarchitecture.md` 中的每个合约可见行为
  `interfaces.md` 必须映射到此处至少一个门行。
- 用于晋升的每个必需的门都必须出现在该矩阵中。
- 没有相应矩阵更新的合同变更是不完整的。
- 门重命名必须更新此矩阵以及任何检查器或发布工具
  解析门密钥。