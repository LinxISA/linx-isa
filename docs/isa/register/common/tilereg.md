# Tile register

## Description

In order to optimize the block instruction data operation performance, reduce memory bandwidth requirements and improve cache utilization, this architecture introduces a set of Tile registers (referred to as Tile) in the first layer state to store one-dimensional or two-dimensional tensor data. The Tile register group contains 32 general-purpose register and 2 special register.

General Tile registers are divided into four types: **T, U, M, and N**, each type contains 16 registers. These registers are mainly used to support data transfer between block instruction and vector operation operations within the block. Special Tile registers include **ACC** and **S**:

- The ACC register is used to temporarily store the intermediate results of matrix operations in the CUBE operation unit, and can be used as the input data source for the next matrix multiply-accumulate operation.
- The S register is used to apply for stack space for block instruction (such as vector data block) that cannot access memory.

| Register type | Description |
|-----------|------|
| **T#1-T#16** | 16 Tile registers of T queue. |
| **U#1-U#16** | 16 Tile registers of U queue. |
| **M#1-M#16** | 16 Tile registers of M queue. |
| **N#1-N#16** | 16 Tile registers of N queue. |
| **ACC** | Matrix multiply-accumulate Tile register. |
| **S** | Stack space Tile register.    |

## Register characteristics

The characteristics of the Tile register are as follows:

- The size of the Tile register is not fixed and is specified by the block instruction application.
- The capacity Size of the Tile register ranges from **256Byte ~ 256KB** (and must be a power of 2 times 256Byte).
- In different hardware implementations, the maximum and minimum Tile register capacity allowed to be applied for by block instruction may be different. The software can query system register[LCFR](../ssr/LCFR.md) to obtain it.
- Tile registers are allocated and used using **relative index**. For usage methods, please see [relative index](../common/sgpr.md#relativeindex).

The Tile register is applied for and referenced through the [B.IOT](../../header/B.IOT.md) instruction.

## <span id="layout">Storage layout</span>

The storage layout determines the organization and arrangement rules of data in the Tile register. In order to improve the efficiency of matrix operations, the system divides the input complete matrix into several small fractal matrices (referred to as small fractals). The data inside each small fractal needs to be stored according to a specific layout. At the same time, the small fractals are also arranged according to corresponding rules, which together form an efficient storage structure. The overall arrangement between different small fractals is called **large fractal layout**.

Storage layout formats include the following:

| Storage Layout | Description |
|---------|----------------|
| **ND** | The entire matrix is stored in **row-major** order |
| **DN** | The entire matrix is stored in **column-major** order |
| **ZZ** | Big Z and small z, large fractals are stored in **row priority**, small fractals are stored in **row priority** |
| **ZN** | Large Z and small n, large fractals are stored in **row priority**, small fractals are stored in **column priority** |
| **NZ** | Large N and small z, large fractals are stored in **column priority**, small fractals are stored in **row priority** |
| **NN** | Large N and small n, large fractals are stored in **column priority**, small fractals are stored in **column priority** |

![d-layout](../../../figs/isa/arch/d-layout.png){ width="700" }

![z-layout](../../../figs/isa/arch/z-layout.png){ width="700" }

![n-layout](../../../figs/isa/arch/n-layout.png){ width="700" }For example, there is a `4行4列` matrix that needs to be stored in the Tile register, and the entire matrix is divided into multiple fractal matrices with 2 rows and 2 columns for storage. Then, under different layouts, the data storage method is as follows:
```c
    Matrix A = {{1, 2, 3, 4}, {5, 6, 7, 8}, {9, 10, 11, 12}, {13, 14, 15, 16}};
```

![layout](../../../figs/isa/arch/layout.png){ width="900" }

## Register attributes

Tile is a register, not memory. The properties of the register are:

- **Atomicity**: During the calculation process, block instruction's writing to Tile Register is atomic. There are no multiple block instructions writing the same Tile Register at the same time.
- **Exclusivity**: During the calculation process, block instruction has exclusive rights to its own Destination Tile Register. Subsequent block instruction cannot be read until the current block instruction is submitted.
- **Impotence**: A Tile register can only be assigned once and cannot be overwritten repeatedly. Only the current register is released and can be overwritten after re-application.
- **Directness**: The Tile register cannot obtain a pointer, nor can it be directly accessed through a pointer.

## Reuse feature

When the Tile register is used as the input of an instruction, it is allowed to have the **reuse** flag. Its semantics are:

- When the source register is marked as reuse: the register must remain available after the current instruction is executed and committed, and the hardware must not release the register at this commit point.
- When the source register is not marked as reuse: When the current instruction is submitted, the occupation of this register can be reclaimed by hardware (kill/release), and subsequent instructions should no longer use this register.

Visibility and lifecycle:

- Marking it as reuse only affects the register retention behavior when the current instruction is submitted, ensuring that its value can still be read in subsequent instructions.
- Source registers not marked for reuse are no longer guaranteed to be readable after the current instruction is committed; any subsequent read from them is illegal.

On subsequent reads of registers that have been freed, the hardware must generate exception.

Example description
```asm
TLOAD [xx], ->T  ; 加载数据到T-Tile寄存器
TLOAD [xx], ->T  ; 加载数据到T-Tile寄存器
TLOAD [xx], ->T  ; 加载数据到T-Tile寄存器
TADD T#2.reuse, T#3, ->U  ; 对T#2和T#3中数据做逐元素加法，保留T#2
TSUB T#2, T#1,       ->U  ; 再次使用T#2
```

In TADD, using the `.reuse` mark for the T#2 source operand means that after the TADD is committed, the T#2 register must not be released by hardware, allowing subsequent instructions to continue reading the register; if `.reuse` is not marked (such as T#3), the register can be recycled after the TADD is committed, and subsequent reads should trigger exception.

The Reuse mark only applies to source registers and does not affect the allocation and release strategy of destination registers.

## Access properties

This set of registers are both readable and writable (RW).