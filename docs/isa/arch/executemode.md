# body execution method

LinxISA adopts a converged computing architecture and can simultaneously support the operations of data type such as scalar, vector and tensor. Based on this architectural feature, we have designed various types of block instruction to meet different computing needs. Different types of block instruction and body also have their own characteristics in their execution methods.

In the current version, block instruction with body supports the following three execution methods:

| Execution method | Description |
|---------|----------|
| **scalar mode (Scalar mode)** | body is only executed once, suitable for scalar operation or system configuration operation. |
| **Sequel mode** | body repeats multiple executions. Iterations within the same group are allowed to be executed in parallel, but different groups must be executed in sequence. |
| **Parallel mode**| body repeats multiple executions, and parallel execution is allowed between all iterations. |

![](../../figs/intro/execmode.png){ width="900" }

## Detailed explanation of core concepts

## Execution group (Group) and execution channel (Lane)

In both serial mode and parallel mode, the processor will sequentially number all body iterations after expansion starting from 0. The hardware scheduling unit takes out several of these iterations in batches according to the scheduling policy and assigns them to an **Execution Group (Group)** for execution.

**Execution group (Group) is the basic unit of hardware scheduling, which represents a group of body iterations that can be executed in parallel at the same time. **

Each Group contains several execution channels (Lane):

- Each Lane corresponds to an independent hardware execution path, which can completely execute a body iteration;
- Lane is numbered sequentially from 0 to `LaneNum - 1` within the Group to which it belongs. This number can be regarded as the local ID of Lane within the Group;
- The number of Lanes in a single Group is fixed by the hardware implementation. Software can query the number of Lanes supported by the current hardware through the `LaneNum` field of system register [LCFR](../register/ssr/LCFR.md).

All Lanes in the same Group are executed in Lock Step mode:

- At the same time, all Lanes execute the same instruction stream (the same PC);
- Each Lane only differs in the data processed (corresponding iteration number).

The scheduling and mapping relationship is as follows:

- A Group contains at least 1 Lane, and usually the number of Lanes is equal to the maximum number of parallel Lanes supported by the hardware;
- Each time it is scheduled, the hardware will assign a set of **consecutive number** body iterations to each Lane within the same Group:
    - Normally, Lane `i` corresponds to iteration `base_iter + i` (`base_iter` is the starting iteration number of the current Group);
- When the total number of iterations is not an integer multiple of the Group size (number of Lanes), only some Lanes in the last Group may perform effective iterations, and the remaining Lanes remain idle or blocked within the Group.

![](../../figs/intro/group.png){ width="900" }

---

## Execution method description

### scalar MODE

scalar mode is suitable for block instruction that performs scalar operations or performs system configuration. In this mode:- body is only executed once and does not perform iterative expansion.
- In block engines that support out-of-order execution, the body instructions can be executed out-of-order. However, all body instructions are required to be submitted in order to ensure the correctness of the execution results.
- Suitable for one-time operations such as scalar calculation, configuration register, and parameter setting.

### Serial mode

Serial mode is suitable for scenarios where there are dependencies in the data processed between different iterations of body expansion. In this mode:

Execution characteristics:

1. Parallel within a group, serial between groups: All iterations within the same group can be executed in parallel, but different groups must be executed strictly in sequence.
2. Data dependency processing: When the calculation result of iteration i is used by iteration j (j>i), the two iterations must be allocated to different Groups
3. Sequence guarantee: All iterations of Group N must be completed before any iteration of Group N+1 starts.

Scheduling mechanism:
```mermaid
迭代编号：0  1  2  3  4  5  6  7  8  9  ...
Group分配： 
          ┌──Group 0───┐┌──Group 1───┐┌──Group 2──┐
          │ 0  1  2  3 ││ 4  5  6  7 ││ 8  9 ...  │
          └────────────┘└────────────┘└───────────┘
执行顺序：Group 0 → Group 1 → Group 2 → ...
```

Nested loop expansion:

Both serial mode and parallel mode use the LB and LC registers to control the number of executions of body:
```c
lane_id = 0;
// 三层嵌套循环展开
Parallel_for(LC2 = 0; LC2 < LB2; LC2++)
  Parallel_for(LC1 = 0; LC1 < LB1; LC1++)
    Parallel_for(LC0 = 0; LC0 < LB0; LC0++) {
        kernel(lane_id);  // ZXTERMZH40QXZ执行，lane_id标识当前迭代
        lane_id++;
    }
```

Calculation of total number of iterations: `CNT = (LB0-LC0) × (LB1-LC1) × (LB2-LC2)`

Iteration numbering rule: `ID = LC0 + LC1×(LB0-LC0) + LC2×(LB0-LC0)×(LB1-LC1)`

### Parallel mode

Parallel mode is suitable for scenarios where the data processed between all iterations of body expansion has no dependencies. In this mode:

Execution characteristics:

1. Full parallelism: parallel execution is allowed between all iterations, with no execution order constraints
2. Independent execution: Each iteration is independent and does not depend on the results of other iterations.
3. Maximum parallelism: The hardware will try its best to schedule all iterations to be executed on available Lanes at the same time.

Scheduling mechanism:
```mermaid
迭代编号：0  1  2  3  4  5  6  7  8  9  ...
并行调度：所有迭代尽可能同时分配到可用Lane
          ┌─group 0─┐ ┌─Group 1─┐ ┌──Group 2──┐ ┌───Group 3───┐
          │ 0 1 2 3 │ │ 4 5 6 7 │ │ 8 9 10 11 │ │ 12 13 14 15 │
          └─────────┘ └─────────┘ └───────────┘ └─────────────┘
          ┌───Group 4───┐ ┌───Group 5───┐ ┌───Group 6───┐ ┌───Group 7───┐
          │ 16 17 18 19 │ │ 20 21 22 23 │ │ 24 25 26 27 │ │ 28 29 30 31 │
          └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
          ...（继续直到所有迭代完成）
```

Applicable scenarios:

- vector element-level independent operations such as addition and multiplication
- Calculation of elements in a matrix that are independent of each other
- Pixel-level independent operations in image processing

## Summary

Mode selection guide:

| Features | scalar Mode | Serial Mode | Parallel Mode |
|------|----------|-----------|----------|
| Number of iterations | 1 time | Multiple times (LB register control) | Multiple times (LB register control) |
| Inter-iteration dependencies | Not applicable | Possible dependencies | No dependencies |
| Parallel Granularity | None | Intra-Group Parallelism | Fully Parallel |
| Execution order | Sequential submission | Inter-group order | No order requirement |
| Applicable scenarios | scalar operation and configuration | Data-dependent loops | Data-independent loops |

Hardware implementation considerations:

1. Group scheduler: Responsible for grouping and assigning iterations to execution units
2. Lane allocator: manages Lane resource allocation within each Group
3. Dependency detection: Detect cross-Group data dependencies in serial mode
4. Resource arbitration: Arbitrate multiple iterations’ access to shared resources in parallel mode

Through the flexible combination of these three execution modes, LinxISA can efficiently handle various application scenarios from scalar operations to large-scale parallel computing, giving full play to the advantages of the converged computing architecture.