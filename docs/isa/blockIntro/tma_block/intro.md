# Data transfer block

## Function Overview

The TLSU (Tile Load/Store Unit) data movement block is the v0.58 interface between the memory subsystem and Tile registers. It executes the named TLOAD/TSTORE/TMOV/TPREFETCH, gather/scatter, masked, CAS, and GMOV operations assigned by the PTO 0.58 catalog.

## Core Competencies

| Function | Description |
|------|--------|
| **Multi-dimensional data movement** | TLSU supports strided, gather/scatter, masked, atomic CAS, collective GMOV, and Tile-register movement operations defined by the v0.58 catalog. |
| **Asynchronous Parallel Execution** | TLSU uses an independent hardware execution engine and participates in the architectural ordering rules recorded by the v0.58 memory model. |
| **Zero-overhead data management** | Optimized management of data transmission through dedicated hardware:<br>1. Automatic address generation: eliminates the additional overhead of software address calculation<br>2. Burst transmission optimization: maximizes memory bandwidth utilization<br>3. Data format conversion: supports transparent conversion of computing formats and storage formats |

## Architecture positioning

TLSU is located between the memory controller and the computing unit:
```
Memory subsystem → TLSU → Tile register array → Compute unit
```
This design achieves the decoupling of storage access and computing execution, allowing the computing unit to focus on arithmetic and logical operations, while the data supply is guaranteed by dedicated hardware.

Interface with computing unit

- Data supply interface: Provides input data loading services to computing units
- Result recovery interface: receives the output data of the computing unit and writes it back to the memory
- Inter-register transfer: supports data reorganization and copying within the Tile register array

## block type Features

- Data transfer block** only supports Fall jump mode**
- The data transfer block allows access to the global register GGPR, Tile register, and memory.
- The data transfer block allows up to 8 Tile registers to be read and 4 tile registers to be written in one block.
- There is no body in the data transfer block, **B.TEXT instruction is not allowed**
