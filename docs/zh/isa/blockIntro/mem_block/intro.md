# 访存数据块

## 概述

访存数据块用于提供 **共享内存** 和 **Tile寄存器** 间的数据搬移能力。开发者以标量指令描述块体，硬件在执行期自动向量化并按Group/Lane层级展开，实现共享内存到向量寄存器（VT/VU/VM/VN）与Tile寄存器的高吞吐加载、存储、搬移和规约；标量Lane负责块内的控制流、掩码管理与状态迁移，使数据搬移与控制路径进行解耦。

## 执行模式 

访存数据块采用 **Lane-Group** 两级执行层次，实现细粒度并行与粗粒度调度的有机结合。

处理器会将一个访存数据块拆分为若干Group，每个Group包含多个向量Lane和一个标量Lane。块的并行度由块体的执行次数与每Group的Lane数共同决定；当数据依赖可消除或需要隐藏访存延迟时，常以并行Group执行（BSTART.MPAR）提高带宽利用与吞吐；当块体之间存在严格的顺序/依赖要求（如多步流水或跨Group的数据前后顺序约束），则采用串行Group执行（BSTART.MSEQ）确保一致性与可预测性。硬件自动向量化会将标量指令流广播到活跃Lane，并由P寄存器提供动态掩码，允许在块体内部对Lane进行条件屏蔽，实现不规则访问、边界处理与分段计算。

Group间并行执行或串行执行方式请见[执行模式](../../arch/executemode.md)。当Group间允许并行执行时，需要通过[BSTART.MPAR](./header.md)指令定义为**访存并行块**。当要求Group间串行时，需要通过[BSTART.MSEQ](./header.md)指令定义为**访存串行块**。

| 层级 | 状态   |
|------|--------|
| **块级别** | 1.[LB寄存器](../../register/common/loop.md#LB)负责控制块内展开的块体的总数量 | 
|           | 2.RI和RO寄存器分别作为进入块之前输入和输出全局寄存器的备份。 |
| **Group级别** | 1.包含多个向量Lane和1个标量Lane；|
|               | 2.标量Lane负责Group的跳转、mask管理和状态迁移。  |
|               | 3.[P寄存器](../../register/common/pred.md)动态控制Lane的有效性，支持指令级并行优化。 |
| **Lane级别** | 1.标量Lane：使用T/U寄存器存储标量数据。 |
|              | 2.向量Lane：独立拥有VT/VU/VM/VN向量寄存器，支持Shuffle指令进行Lane间通信。 |
|              | 3.[LC寄存器](../../register/common/loop.md#LC)负责记录每个向量lane的ID。 |

每个Group内向量lane的数量可以通过[SSR:LCFR](../../register/ssr/LCFR.md)寄存器的LaneNum字段查询。

![memoryblock](../../../figs/intro/memoryblock.png){ width="800" }

## 块内状态BSTATE

访存数据块的BSTATE中包含以下三部分内容：

- **[BARG](../../register/common/barg.md)寄存器**：块内的控制参数寄存器，用于条件跳转或执行参数的保存和处理。
- **[TPC](../../register/common/tpc.md)寄存器**：每个Group内拥有独立的TPC，记录当前Group正在执行的指令。
- **LPR-私有寄存器组** 包含以下内容：
    - **[SGPR](../../register/common/sgpr.md)寄存器**：通用标量寄存器，用于保证块内标量数据流传递。
    - **[RI/RO](../../register/common/lgpr.md)寄存器**：通用形参寄存器，存储块内读写的全局寄存器的备份。
    - **[PRED](../../register/common/pred.md)寄存器**：用于并行lane的掩码控制。
    - **[LB/LC](../../register/common/loop.md)寄存器**：用于块体展开控制。
    - **[VGPR](../../register/common/vgpr.md)寄存器**：通用向量寄存器，用于作为块内大量并行的向量运算的载体。
    - **[LTAR](../../register/common/ltar.md)寄存器**：Tile形参寄存器。
    - **Output Tile**：输出Tile寄存器，块内已部分更新但未提交到一层状态中。

总体上，以BARG管理块级访存控制（基址、步长、事务属性、序），以每个Group独立TPC推进访存微指令执行，并以8个SGPR承载指针与模式参数；结合PRED与LB/LC进行并行事务筛选与批次展开，以事务队列与Tile缓冲完成聚散与一致性提交，构成面向内存的数据调度与执行闭环。

## 块类型特征

访存数据块有如下特点：

| 层面 | 特征 | 说明 |
|------|-------|-------|
| **执行控制** | 硬件自动向量化 | 将开发者编写的标量指令流，在硬件层面自动展开、广播至所有活跃的向量Lane执行，极大简化编程模型。 |
|             | 线程级分支支持 | 通过**标量Lane执行条件跳转**，允许不同的Group根据条件独立进入不同的执行路径，支持灵活的流控制。 |
|             | 动态执行掩码 | 通过64位的P寄存器（1有效/0无效），可动态屏蔽Group内任意向量Lane，实现条件执行和灵活的数据处理。 |
| **数据通路** | 内存与寄存器 | **允许访问内存空间**，数据操作可在Tile寄存器、向量寄存器（VGPR）和标量寄存器（SGPR）以及内存间完成，保证数据通路完善。 |
|             | 分层寄存器架构 | 标量Lane使用T/U（SGPR）寄存器；向量Lane使用VT/VU/VM/VN（VGPR）寄存器；通过shuffle指令实现Lane间高效数据交换。 |
|             | 受限的GGPR写入 | **仅Reduce类指令被允许写回全局寄存器（GGPR），且输出的GGPR不可作为本块输入**，强制数据规约模式的清晰性，避免读写依赖冲突。 |
| **编程约束** | 分离块结构 | 必须**采用块头与块体分离的格式**，仅支持Fall-through跳转方式，简化控制流，利于硬件调度与优化。 |
|             | 资源访问隔离 | 允许读写全局寄存器、系统寄存器和Tile寄存器，但完全隔离外部内存系统，形成自包含的计算单元。 |

由于访存数据块采用分离块的结构，因此需要遵守[分离块](../../arch/executemachine.md#DecoupledBlock)的定义规则。

## 指令约束

**1.寄存器与全局状态访问及读写限制**

- 访存数据块允许访问全局寄存器GGPR，系统寄存器SSR和内存，以及Tile寄存器等全局状态。
- 访存数据块最多允许读8个Tile寄存器，写4个Tile寄存器。
- 访存数据块最多允许读12个GGPR，写4个GGPR。这是分离块形式带来的约束。
- 访存数据块内只有Reduce指令允许写全局寄存器GGPR。
- 访存数据块内的Reduce指令输出的全局寄存器不允许作为本并行块指令的输入，否则报非法指令异常。

**2.Tile寄存器访问 约束与保序**

- 访存数据块内的load local指令的地址不能超过本块输入输出tile寄存器的范围，否则报非法越界异常。
- 访存数据块内的store local指令不能访问输入Tile寄存器的地址范围，只能访问输出Tile寄存器的地址范围，否则报非法越界异常。
- **访存并行块约束**：
    - 访存并行块内的不同group间的load/store local 不允许地址重合，如出现重合硬件不保证执行的正确性。
    - 访存并行块内的同一个group内的load/store local 基于地址保序，不同group的地址不保序。
- **访存串行块约束**：
    - 访存串行块内的不同group间的load/store local 允许地址重合，但需要按照group id的顺序按序修改。 
    - 访存串行块内的同一个group内的load/store local 基于地址保序，不同group的load/store local按照地址顺序进行全局保序。

**3.内存 访问与原子、保序、重合**

- 访存数据块内的不同group间的load/store global 不允许和标量块的load/store地址重合，如出现重合硬件不保证执行的正确性。
- **访存并行块约束**：
    - 访存并行块内的不同group间的load/store global 不允许地址重合，如出现重合硬件不保证执行的正确性。
    - 访存并行块内的同一个group内的load/store global 基于地址保序，不同group的地址不保序。
    - 访存并行块的load/store global指令可以访问non-cacheable和device IO等地址空间，并且不保证group间的访问顺序。
    - 访存并行块的load/store global原子指令允许对内存进行原子访问，不保证group间原子访问的顺序。
- **访存串行块约束**：
    - 访存串行块内的不同group间的load/store global 允许地址重合，但需要按照group id的顺序按序修改。
    - 访存串行块内的同一个group内的load/store global 基于地址保序，不同group的load/store global 按照地址顺序进行全局保序。
    - 访存串行块的load/store global指令可以访问non-cacheable和device IO等地址空间，不同group间的访问基于地址保序。
    - 访存串行块的load/store global原子指令允许对内存进行原子访问，不同group间的原子访问基于地址保序。

**4.同步与提交**

- 访存数据块内无DMB/DSB等同步操作，如若做同步需要强行切块，通过系统块进行同步。
- 访存并行块内的提交需要等所有group提交，每个group的提交定义为本group内最后一条指令的提交。
- 访存串行块内只允许多个group按照程序序以group id由小到大顺序提交，最后一个group提交后则块指令整体提交。

## 总结

访存数据块是灵犀指令集架构中用于实现共享内存与Tile寄存器间高效数据搬移的硬件机制。其设计遵循分离块结构，通过将块指令分解为多个可并行或串行执行的Group，并在Group内进行向量化数据搬运，以优化内存带宽利用与数据局部性。
