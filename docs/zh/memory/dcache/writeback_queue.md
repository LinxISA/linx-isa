## Load Result Pipe 组件功能描述

本模块负责将 L1 Data Cache 返回数据、STQ 和 SCB bypass 的三路数据的汇聚，汇聚完成后进行符号位扩展或零扩展操作并返回数据给 PE。

## Load Result Pipe 组件处理说明

写回过程中需要注意以下几点：

1. 数据选择的优先级为： STQ bypass > SCB bypass > L1 DC返回数据

2. 当存在 Load 请求和多个 STQ 中的请求有相同的物理地址，并且最新的 STQ 请求无法完全覆盖当前 Load 请求所需数据时, 需要等待这个 STQ 请求出队后才能重新选取 (Repick) 这条 Load 指令

3. 上述第二条的覆盖条件，可通过字节掩码 (bytemask) 确定 STQ, SCB 覆盖 L1 DCache 的数据域段

4. 汇聚完成后进行符号位扩展或零扩展和对齐操作

5. 返回数据后发送完成信号 (Resolve) 给 PE ROB
