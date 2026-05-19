# Janus Core架构状态

LinxISA架构通过其独特的层次化设计实现了多任务块的并行执行。Janus Core是基于灵犀指令集实现的融合计算架构处理器，**以BCC(Block Control Core)为核心控制单元**，构建了完整的计算体系。

## **BCC**

作为系统顶层的控制中枢，BCC主要承担以下两个关键功能：

1. 指令获取与Tile调度：通过取指模块获取程序Tile（指令块），将Unified Buffer当作寄存器管理，以输入输出TileReg表达各Tile间的依赖关系，完成Tile的解依赖、调度和分发；
2. 混合计算能力：BCC内置完整的标量计算单元，使得BCC既可以作为控制核心管理控制流和分支逻辑，又可以独立执行传统CPU的负载任务，其计算能力覆盖从标量运算到复杂控制流处理的完整需求。

其内部包含如下的架构状态：

| 名称  |位宽| 简介  | 描述
| ----  | ----| ----  | ----  |
| PC | 64bit | 程序指针Program Counter  | 块指令级别的指针 |
| BARG | 256bit | Commit Argument  |  块提交参数寄存器 |
| R1-R23 | 64bit | Global GPR  | 全局寄存器，被全部单元访问的寄存器 |
| T#1-T#4 | 64bit | Temporal Hand  | 私有T寄存器相对索引1-4 |
| U#1-U#4 | 64bit | Uniform Hand  | 私有U寄存器相对索引1-4 |

## **VEC**

Vector Core是专为AI向量计算设计的高效处理单元，采用group加SIMD执行模式，兼具标量运算与向量的计算能力。作为一个乱序处理器，其通过简洁的块指令接口与上下游模块协同，为AI负载提供高性能并行计算支持。

其内部包含如下的架构状态：

| 名称  |位宽| 简介  | 描述
| ----  | ----| ----  | ----  |
| TPC | 64bit | 程序指针Program Counter  | 微指令级别的指针 |
| T#1-T#4 | 64bit | Scalar Temporal Hand  | 私有标量T寄存器相对索引1-4 |
| U#1-U#4 | 64bit | Scalar Uniform Hand  | 私有标量U寄存器相对索引1-4 |
| VT#1-VT#4 | 32bit | Vector Temporal Hand  | 私有向量T寄存器相对索引1-4 |
| VU#1-VU#4 | 32bit | Vector Uniform Hand  | 私有向量U寄存器相对索引1-4 |
| VM#1-VN#4 | 32bit | Vector Michealous Hand  | 私有向量M寄存器相对索引1-4 |
| VN#1-VN#4 | 32bit | Vector Normalized Hand  | 私有向量N寄存器相对索引1-4 |

## **TMU**

**TMU（Tile Manager Unit）**是用户管理Tile Register和交通总线的硬件单元。

其内部包含如下的架构状态：

| 名称  |位宽| 简介  | 描述
| ----  | ----| ----  | ----  |
| TT#1-TT#8 | 512B-32KB | Tile Temporal Hand  | 全局Tile T寄存器相对索引1-8 |
| TU#1-TU#8 | 512B-32KB | Tile Uniform Hand  | 全局Tile U寄存器相对索引1-8 |
| TM#1-TN#8 | 512B-32KB | Tile Michealous Hand  | 全局Tile M寄存器相对索引1-8 |
| TN#1-TN#8 | 512B-32KB | Tile Normalized Hand  | 全局Tile N寄存器相对索引1-8 |
| SCR | 512B-32KB | Scratch Tile  | 私有Scratch Tile |

## **CUBE**

Cube 是负责矩阵乘法的计算单元，相较于其他PE复杂的指令流，Cube需要处理的指令只有三条：TMATMUL、TMATMUL.BIAS与TMATMUL.ACC（即矩阵乘与矩阵乘累加）。所以，Cube Core内并无取指，乱序，控制流等复杂控制电路。

其内部包含如下的架构状态：

| 名称  |位宽| 简介  | 描述
| ----  | ----| ----  | ----  |
| ACC | 512B-32KB | Tile Normalized Hand  | 私有累加Tile |

## 架构状态

这些模版根据功能需要分别有单独的一套寄存器状态，具体如下：

| 模块    | 名称  |位宽| 简介  | 描述
|  ----  | ----  | ----| ----  | ----  |
| BCC  | PC | 64bit | 程序指针Program Counter  | 块指令级别的指针 |
| BCC  | BARG | 256bit | Commit Argument  |  块提交参数寄存器 |
| BCC  | R1-R23 | 64bit | Global GPR  | 全局寄存器，被全部单元访问的寄存器 |
| BCC  | T#1-T#4 | 64bit | Temporal Hand  | 私有T寄存器相对索引1-4 |
| BCC  | U#1-U#4 | 64bit | Uniform Hand  | 私有U寄存器相对索引1-4 |
| VEC  | TPC | 64bit | 程序指针Program Counter  | 微指令级别的指针 |
| VEC  | T#1-T#4 | 64bit | Scalar Temporal Hand  | 私有标量T寄存器相对索引1-4 |
| VEC  | U#1-U#4 | 64bit | Scalar Uniform Hand  | 私有标量U寄存器相对索引1-4 |
| VEC  | VT#1-VT#4 | 32bit | Vector Temporal Hand  | 私有向量T寄存器相对索引1-4 |
| VEC  | VU#1-VU#4 | 32bit | Vector Uniform Hand  | 私有向量U寄存器相对索引1-4 |
| VEC  | VM#1-VN#4 | 32bit | Vector Michealous Hand  | 私有向量M寄存器相对索引1-4 |
| VEC  | VN#1-VN#4 | 32bit | Vector Normalized Hand  | 私有向量N寄存器相对索引1-4 |
| TMU  | TT#1-TT#8 | 512B-32KB | Tile Temporal Hand  | 全局Tile T寄存器相对索引1-8 |
| TMU  | TU#1-TU#8 | 512B-32KB | Tile Uniform Hand  | 全局Tile U寄存器相对索引1-8 |
| TMU  | TM#1-TN#8 | 512B-32KB | Tile Michealous Hand  | 全局Tile M寄存器相对索引1-8 |
| TMU  | TN#1-TN#8 | 512B-32KB | Tile Normalized Hand  | 全局Tile N寄存器相对索引1-8 |
| TMU  | SCR | 512B-32KB | Scratch Tile  | 私有Scratch Tile |
| CUBE  | ACC | 512B-32KB | Tile Normalized Hand  | 私有累加Tile |

其中MTC和VEC的定义相同，只是MTC拥有对DDR访存的标记，VEC的标记不能访问DDR。
