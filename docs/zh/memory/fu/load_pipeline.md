# Load 指令流水线

![LOAD_PIPE](../../figs/uArch/load_pipe_hw.png){ width="800" }


## 工作流程

LSU 在收到 Load 指令时主要有以下工作流程：
```
1. 当接收到来自上游的 Load 指令时，硬件将从 Load Queue (LDQ) 中挑选一个空位放置，同时查找 TLB 进行虚拟地址 (Virtual Address, VA) 和物理地址 (Physical Address, PA) 转换，如果 TLB 未命中，则发送 TLB 请求到 MMU；

2. 当接收到来自上游的 Load 指令时，硬件将同时查找 DCache TAG，如果 DCache 未命中，发送数据请求到 L2 Cache；

3. L2 Cache 返回数据或 MMU 返回 TLB 后，从 LDQ 中重新挑选出 Load 指令查找 DCache TAG 或 TLB；

4. DCache 命中后从 DCache 读取数据，同时检查 STQ 和 SCB，查看是否有和 Load 指令虚拟地址 VA 匹配的 Store 数据存在。注意：Store 数据应该比 Load 指令更老并有相同的域段才能真正匹配；

5. 把从 STQ、SCB 和 DCache 中的数据按照 Byte Mask 域段进行合并操作，STQ 优先级最高，SCB 次之，L1DCache 优先级最低；

6. 由于数据有不同的格式，因此需要对 Load 数据进行符号位扩展 (Sign Extend) 或无符号位扩展 (Zero_Extend)；

7. 返回 Load 数据到 PE，同时发送 Load 完成信号 (Resolve) 到 PE ROB，以通知 PE ROB 当前此 Load 指令完成，同时，将 Load 相关信息写入 LDQ，后面 Store 指令会查找 LDQ 以确认是否有更新的 Load 指令在更老 Store 之前完成，如有则需要刷掉 (Nuke Flush) 这个 Load 指令并发送 Nuke Flush 到 PE ROB；

8. PE ROB 按序提交后通知 LSU，LSU 把对应提交完成的 Load 指令从 LDQ 中解除分配
```
流程图如下：

![LOAD_PIPE1](../../figs/uArch/load_pipe.png){ width="800" }

