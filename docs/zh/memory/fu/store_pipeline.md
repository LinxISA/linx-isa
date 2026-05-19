# Store 指令流水线

![STORE_PIPE_HW](../../figs/uArch/store_pipe_hw.png){ width="800" }

## 工作流程

LSU 的 Store 指令主要工作流程：

1. PE 下发 Store 指令，从 STQ 中挑选出一个空闲的表项存放地址、数据等信息，同时查找 TLB 进行虚拟地址 (Virtual Address, VA) 和 物理地址(Physical Address, PA) 的转换，如果 TLB 缺失，发送 TLB 请求到 MMU

2. MMU 返回 TLB 后从 STQ 中重新挑选出 Store 指令查找 TLB

3. TLB 查找完成后发送 Store 完成标记 (Resolve) 到 PE ROB，以通知 PE ROB 当前 Store 指令执行完成

4. 传递 (Forward) STQ 中数据到 VA 匹配且更新的 Load 指令

5. Store 指令完成后和 LDQ 中已经完成的 Load 指令对比，如有 PA 一致且更新的 Load 指令在当前 Store 指令前完成，需要发送nuke flush到ROB

6. 当 STQ 中多个表项和 Load 物理地址一致时，需要把 Load 置于睡眠状态，等待最新表项的 STQ retire 到 SCB 后，再把前面睡眠的 Load 重新激活并执行

7. 根据 PE ROB 给出的当前将提交的 ID (Commit ID) 将 STQ 中的指令转移到 SCB。当有物理地址一致的 Load 指令时，需要转发 SCB 中数据到 Load 指令

8. SCB 在写入 L1 DCache 前需要查找 DCache Tag，如 Tag 缺失需要发送请求到 L2 Cache，L2 返回数据再重新查找 L1 DCache 并把数据写入 L1 DCache 

流程图如下：

![STORE_PIPE](../../figs/uArch/store_pipe.png){ width="800" }
