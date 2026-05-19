# 派遣单元 (PE Dispatch)
派遣单元会将已经解码好的指令同时发往 ISQ 和 ROB。每拍最多下发四条微指令，派遣单元会根据指令类型的不同分配到不同的 ISQ 中。同时对于同样类型的指令，微架构会根据每个 ISQ 的剩余空位来派遣微指令。

微架构中需要被分配的 ISQ 如下：

| ISQ 类型 |  个数 |深度| 计算类别|
| --| --- | ---|--|
|ALU 0| 1 | 8|通用计算类|
|ALU 1| 1 | 8|通用计算类|
|GSU | 2 | 8|PC计算及块间通信类|
|LSU |2| 8|访存类|




以 ALU 指令举例 : (注：GSU指令、LSU指令适用于同样的分发规则）

ALU 的发射队列有 ALU0，ALU1 两个 Bank。在同一时钟周期，最多会有四条指令写入这两个 Bank。假设 Free0 Free1 为 ALU0/1 两个 Bank 的空位数量，Instr0 Instr1 Instr2 Instr3 为同一拍同类型、程序顺序从老到新的四条指令。其中 Instr0 有效的概率高于 Instr1，依此类推 Instr0 >= Instr1 >= Instr2 >= Instr3。基于前述条件，优先将有效概率大的指令发往空位多的 Bank。具体如下：

|规则	|ALU 0 入队	|ALU1 1 入队|
|--|--|--|
|Free0 >= Free1 (ALU0 的空位大于等于 ALU1)	|Instr0 Instr1	|Instr2 Instr3|
|Free0 <   Free1 (ALU0 的空位小于 ALU1)	|Instr2 Instr3|	Instr0 Instr1|
