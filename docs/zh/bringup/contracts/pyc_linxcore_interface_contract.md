# pyCircuit ↔ 灵犀Core 接口合约

版本：`2.0`

## 范围

该合约控制 灵犀Core 启动门消耗的 pyCircuit 集成行为。

规范的机器可读文件：

- `docs/bringup/contracts/pyc_linxcore_interface_contract.json`

## 兼容性政策

- 合约版本格式：`MAJOR.MINOR`
- 突破性的界面变化需要 `MAJOR` 碰撞。
- 附加的向后兼容更改需要 `MINOR` 碰撞。
- 未版本控制的接口中断被门工具拒绝。

## 所需的生产者路径

- `tools/pyCircuit/contrib/linx/flows/tools/run_linx_cpu_pyc_cpp.sh`
- `tools/pyCircuit/contrib/linx/flows/tools/run_linx_qemu_vs_pyc.sh`
- `tools/pyCircuit/contrib/linx/flows/tools/linx_trace_diff.py`

## 必需的提交字段

所需的提交跟踪字段必须与以下内容保持兼容：

- `tools/bringup/validate_trace_schema.py`
- `tools/pyCircuit/contrib/linx/flows/tools/linx_trace_diff.py`

当前标量/底座所需设置：

- `cycle`
- `pc`
- `insn`
- `len`
- `next_pc`
- `src0_valid`
- `src0_reg`
- `src0_data`
- `src1_valid`
- `src1_reg`
- `src1_data`
- `dst_valid`
- `dst_reg`
- `dst_data`
- `wb_valid`
- `wb_rd`
- `wb_data`
- `mem_valid`
- `mem_is_store`
- `mem_addr`
- `mem_wdata`
- `mem_rdata`
- `mem_size`
- `trap_valid`
- `trap_cause`
- `traparg0`

版本 `2.0` 强制提交源/目标关联。制片人
消费者路径必须处理丢失的源、目的地、内存方向或
trap-argument 字段作为合约失败而不是可选的调试元数据。

生产者方的任何更改都必须更新合同版本和迁移说明。