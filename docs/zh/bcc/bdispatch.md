# Decode Group Dispatch

Dispatch 接收 D1 四 lane 译码组，并位于 D2 资源需求计算和 D3 原子接纳
之后。

它根据已译码 execution class 和容量，把 uop 路由到 scalar、memory、
vector、tile 或 engine issue structure。B-SIDE 只负责预测控制流；
D1/D2/D3 负责建立指令语义、block ownership 和资源身份。

整组必须全有或全无地接纳。任一 lane 或所需资源阻塞时，任何 lane 都
不能推进 RID/BID/rename/IQ/memory-order 状态。
