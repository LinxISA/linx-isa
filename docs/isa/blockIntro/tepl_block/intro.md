# Template data block

## Function Overview

TEPL (Template Tile Block) template data block is a dedicated, hardware-solidified parallel computing engine** in the tensor processor architecture. Its core positioning is to efficiently execute **vector-based calculation operations** for **Tile data blocks** (multi-dimensional data slices). Unlike general-purpose processors, TEPL does not rely on second-layer microinstruction decoding and execution, but directly implements its rich computing functions through highly optimized dedicated hardware circuits (hardened units). This design aims to provide **extremely low latency, high throughput hardware acceleration** for core modes of tensor operations such as element-wise computation, scalar fusion, along-axis reduction and broadcast.

## Core Competencies

| Function | Description |
|------|--------|
| **Hardware-accelerated vector-based computing** | The core value of TEPL lies in its **hardened implementation of parallel computing capabilities**. It supports directly through dedicated circuits:<br>1. **Parallel processing of Tile data blocks:** Perform the same arithmetic, logical, comparison, selection, or basic mathematical function operations on all elements within the Tile simultaneously. <br>2. **Efficient interaction between Tile and scalar:** Seamlessly integrate Tile data and scalar values ​​for calculation (such as scalar broadcast, Tile-scalar calculation). <br>3. **Smart operations of data dimension:** Perform reduction (sum, maximum, minimum, etc.) or broadcast operations along specified rows or columns. |
| **Computing mode hardware solidification** | The functions of TEPL are not implemented through software microinstruction sequences, but are **directly executed by specific functional units pre-designed and manufactured in hardware**:<br>1. **Zero microinstruction overhead:** The overhead of microinstruction fetching, decoding, and dispatch is eliminated, and calculations are triggered directly on the functional unit. <br>2. **Deterministic high performance:** Hardened circuitry ensures that specific calculation operations (such as vector addition, ReLU, row summation) can be completed in the **constant or predictable shortest period**. <br>3. **Maximizing parallelism:** The hardware structure naturally matches the parallelism of Tile data and can process a large number of data elements simultaneously. |
| **tensor Computing Primitive Provider** | TEPL is a key module for executing **basic and computational primitives** in tensor neural network and scientific computing. It provides underlying, efficient hardware execution support for complex upper-layer operators (such as dot product post-processing in the convolutional layer, activation functions, statistical calculations in normalization, and scaling/Softmax in the attention mechanism). |

## Architecture positioning

TEPL plays the role of **Core Execution Unit (EU)** in the computing pipeline, focusing on transforming and calculating the data loaded into the Tile register:
```
[数据供给] Tile寄存器阵列 → [核心计算] TEPL模版数据块 (硬化计算) → [结果暂存] Tile寄存器阵列
                              ↑
                      [控制] 核心调度器 (指令派发)
```
* **Input and output:** Its operand source and result destination are mainly **Tile register array**. It does not directly manage data movement (that is the responsibility of the TMA), but focuses on performing calculations on Tile data residing in registers.
* **Cooperation:** Relies on the Data Movement Block (TMA) to efficiently load data from memory into Tile registers; after calculations are completed, the results are typically written back to memory by the TMA or used by other blocks (including TEPL itself for subsequent instructions).
* **Control method:** The core control logic/scheduler starts its corresponding internal **hardened functional unit** to perform specific computing tasks by dispatching **TEPL instructions**.

## block type Features* **Core role**: **Dedicated, hardware-solidified parallel computing engine**.
* **Operation object**: Mainly perform operations on the data block stored in the **Tile register**.
* **execution mechanism**: **No microinstruction layer**. Instructions are mapped directly to internal predefined **hardened functional units** for execution, achieving ultra-low latency and high throughput.
* **Functional Scope**: Covers the key primitives of tensor calculations: vectorized arithmetic/logic/comparison, basic mathematical functions, scalar fusion calculations, along-axis reduction and broadcasting.
* **Data Movement**: **Does not access system memory directly**. Data input/output all work together with the data handling block (TMA) through the Tile register array and global register GGPR.
* **Performance Critical**: Provides **deterministic, high-performance acceleration** for common computing patterns on Tile data blocks by eliminating microinstruction overhead and leveraging dedicated hardware circuitry.
* **Jump method**: Only supports Fall extension.